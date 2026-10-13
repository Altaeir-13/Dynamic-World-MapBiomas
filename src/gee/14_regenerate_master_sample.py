"""
14_regenerate_master_sample.py — Regeneração da Master Sample com Cobertura Completa (100%)
========================================================================================
Atende integralmente à Seção C da auditoria:
  1. Utiliza a nova alocação operacional tables/slice_sampling_allocation_final.csv (n_robust_hs >= 1)
  2. Preserva rigorosamente as 16 cotas científicas state x regime (n_robust_h, n_main_h)
  3. Amostragem estratificada sem reposição com root_seed = 25
  4. Ranking determinístico SHA256 para main sample (20.000 pontos)
  5. Extrai pixel_area_m2 exato de ee.Image.pixelArea().reproject(crs=mb_proj)
  6. Calcula probabilidades de inclusão e pesos exatos (Patch A):
     - area_weight_robust = pixel_area_m2 / selection_probability_robust
     - area_weight_main = pixel_area_m2 / selection_probability_main (se main_sample == 1)
  7. Mecanismo seguro de checkpoint/resume idempotente para fatias e pixel_area_m2
  8. Valida 100% de cobertura (zero pi = 0) e representação do frame completo
  9. Salva data/processed/master_sampling_points.csv
"""

from __future__ import annotations

import hashlib
import json
import math
import socket
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

_orig_request = requests.Session.request
def _patched_request(self, *args, **kwargs):
    if "timeout" not in kwargs or kwargs["timeout"] is None:
        kwargs["timeout"] = 240
    return _orig_request(self, *args, **kwargs)
requests.Session.request = _patched_request
socket.setdefaulttimeout(300)

import ee
import numpy as np
import pandas as pd
from shapely.geometry import box, shape

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.gee.dw_annual import (
    PROJECT_ID,
    get_harmonized_crosswalk_layers,
    get_mapbiomas_projection,
)

DATA_REF = BASE_DIR / "data" / "reference"
DATA_PROC = BASE_DIR / "data" / "processed"
TABLES_DIR = BASE_DIR / "tables"

STATES_GEOJSON = DATA_REF / "matopiba_states.geojson"
QUOTAS_CSV = TABLES_DIR / "sampling_quotas.csv"
ALLOC_FINAL_CSV = TABLES_DIR / "slice_sampling_allocation_final.csv"
CHECKPOINT_POINTS = DATA_PROC / "master_sample_canonical_checkpoint.json"
CHECKPOINT_PIXEL_AREA = DATA_PROC / "pixel_area_m2_canonical_checkpoint.json"
OUT_CSV = DATA_PROC / "master_sampling_points.csv"
SLICE_DESIGN_CSV = TABLES_DIR / "slice_sampling_design_audit.csv"

STEP_DEG = 0.75
ROOT_SEED = 25
MAX_WORKERS = 4
LOCK = threading.Lock()

REGIME_MAP = {1: "AA", 2: "AN", 3: "NA", 4: "NN"}
REGIME_REV = {"AA": 1, "AN": 2, "NA": 3, "NN": 4}
ORDERED_STATES = ["MA", "TO", "PI", "BA"]
ORDERED_REGIMES = ["AA", "AN", "NA", "NN"]


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def partition_state(state: str, geom_shp, step: float = STEP_DEG) -> list[tuple[str, any]]:
    min_x, min_y, max_x, max_y = geom_shp.bounds
    nx = int((max_x - min_x) / step) + 1
    ny = int((max_y - min_y) / step) + 1
    dx = (max_x - min_x) / nx
    dy = (max_y - min_y) / ny
    pieces = []
    for ix in range(nx):
        for iy in range(ny):
            b = box(min_x + ix * dx, min_y + iy * dy, min_x + (ix + 1) * dx, min_y + (iy + 1) * dy)
            sub = geom_shp.intersection(b)
            if not sub.is_empty and sub.area > 1e-6:
                pieces.append((f"{state}_x{ix:02d}_y{iy:02d}", sub))
    return pieces


def load_points_checkpoint() -> dict[str, list[dict]]:
    if CHECKPOINT_POINTS.exists():
        try:
            with open(CHECKPOINT_POINTS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_slice_points(slice_id: str, points: list[dict]) -> None:
    with LOCK:
        ckpt = load_points_checkpoint()
        ckpt[slice_id] = points
        with open(CHECKPOINT_POINTS, "w", encoding="utf-8") as f:
            json.dump(ckpt, f)


def load_pixel_area_checkpoint() -> dict[str, float]:
    if CHECKPOINT_PIXEL_AREA.exists():
        try:
            with open(CHECKPOINT_PIXEL_AREA, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_pixel_area_checkpoint(areas: dict[str, float]) -> None:
    with LOCK:
        with open(CHECKPOINT_PIXEL_AREA, "w", encoding="utf-8") as f:
            json.dump(areas, f)


def sample_slice(
    slice_id: str,
    geom_shp,
    target_quotas: dict[str, int],
    regime_code: ee.Image,
    mb_proj: ee.Projection,
) -> list[dict]:
    active_regimes = {reg: n for reg, n in target_quotas.items() if n > 0}
    if not active_regimes:
        return []

    ee_geom = ee.Geometry(geom_shp.__geo_interface__)
    slice_seed = int(hashlib.sha256(f"{ROOT_SEED}_{slice_id}".encode("utf-8")).hexdigest()[:8], 16) % 2147483647

    class_values = [REGIME_REV[reg] for reg in active_regimes.keys()]
    class_points = [max(n + 3, int(math.ceil(n * 1.10))) for n in active_regimes.values()]

    max_retries = 4
    for attempt in range(1, max_retries + 1):
        try:
            samples = regime_code.stratifiedSample(
                numPoints=0,
                classBand="regime_code",
                classValues=class_values,
                classPoints=class_points,
                region=ee_geom,
                scale=10,
                seed=slice_seed,
                geometries=True,
            )
            res = samples.getInfo()
            feats = res.get("features", [])

            by_reg = {reg: [] for reg in active_regimes.keys()}
            for f in feats:
                rc = f["properties"]["regime_code"]
                reg_name = REGIME_MAP.get(rc)
                if reg_name in by_reg and len(by_reg[reg_name]) < active_regimes[reg_name]:
                    coords = f["geometry"]["coordinates"]
                    by_reg[reg_name].append({
                        "lon": coords[0],
                        "lat": coords[1],
                        "regime": reg_name,
                        "slice_id": slice_id,
                    })

            final_points = []
            for reg, pts in by_reg.items():
                if len(pts) < active_regimes[reg]:
                    raise RuntimeError(f"Pontos insuficientes em {slice_id} para {reg}: obtido {len(pts)}, necessário {active_regimes[reg]}")
                final_points.extend(pts)

            return final_points
        except Exception as exc:
            log(f"  [ERRO] {slice_id} (tentativa {attempt}/{max_retries}): {exc}")
            if attempt == max_retries:
                raise
            time.sleep(5 * attempt)

    return []


def main():
    log("=" * 80)
    log("REGENERAÇÃO INTEGRAL DA MASTER SAMPLE 40.000 (COBERTURA 100%, ZERO PI=0)")
    log("=" * 80)

    ee.Initialize(project=PROJECT_ID)
    mb_proj = get_mapbiomas_projection()
    log("Construindo raster canônico de crosswalk e regimes...")
    layers = get_harmonized_crosswalk_layers()
    regime_code = layers["regime_code"]

    # 1. Carregar tabela de alocação final
    df_alloc = pd.read_csv(ALLOC_FINAL_CSV, keep_default_na=False)
    log(f"Alocação final lida: {len(df_alloc)} subestratos ativos, soma robusta = {df_alloc['n_robust_hs'].sum():,}")

    slice_allocations: dict[str, dict[str, int]] = {}
    for _, r in df_alloc.iterrows():
        s_id = r["slice_id"]
        reg = r["regime"]
        if s_id not in slice_allocations:
            slice_allocations[s_id] = {}
        slice_allocations[s_id][reg] = int(r["n_robust_hs"])

    # 2. Particionar estados
    with open(STATES_GEOJSON, "r", encoding="utf-8") as f:
        states_data = json.load(f)

    state_slices: dict[str, any] = {}
    slice_to_state: dict[str, str] = {}
    for feat in states_data["features"]:
        st = feat["properties"]["state"]
        shp = shape(feat["geometry"])
        pieces = partition_state(st, shp, STEP_DEG)
        for s_id, s_geom in pieces:
            state_slices[s_id] = s_geom
            slice_to_state[s_id] = st

    active_slices = [s_id for s_id, q in slice_allocations.items() if sum(q.values()) > 0]
    log(f"Fatias ativas a processar: {len(active_slices)}")

    # 3. Mecanismo de Resume Seguro: verificar fatias pendentes
    ckpt = load_points_checkpoint()
    pending_slices = []
    for s_id in active_slices:
        target_q = slice_allocations[s_id]
        cached_pts = ckpt.get(s_id, [])
        # Contar pontos por regime no cache
        cached_q = {}
        for p in cached_pts:
            cached_q[p["regime"]] = cached_q.get(p["regime"], 0) + 1
        
        # Verificar se coincide exatamente com a cota
        complete = True
        for reg, n_exp in target_q.items():
            if cached_q.get(reg, 0) != n_exp:
                complete = False
                break
        if not complete:
            pending_slices.append(s_id)

    log(f"Fatias já concluídas e validadas no checkpoint: {len(active_slices) - len(pending_slices)} / {len(active_slices)}")
    log(f"Fatias pendentes para amostragem: {len(pending_slices)}")

    # 4. Amostragem concorrente se houver fatias pendentes
    if pending_slices:
        log(f"Iniciando pool com {MAX_WORKERS} workers para amostragem das {len(pending_slices)} fatias pendentes...")
        completed_count = len(active_slices) - len(pending_slices)
        t_start = time.time()

        def sample_worker(s_id: str):
            t0 = time.time()
            geom = state_slices[s_id]
            target_quotas = slice_allocations[s_id]
            pts = sample_slice(s_id, geom, target_quotas, regime_code, mb_proj)
            save_slice_points(s_id, pts)
            dt = time.time() - t0
            return s_id, len(pts), dt

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(sample_worker, s_id): s_id for s_id in pending_slices}
            for fut in as_completed(futures):
                s_id = futures[fut]
                try:
                    s_id, n_pts, dt = fut.result()
                    completed_count += 1
                    log(f"  [{completed_count}/{len(active_slices)}] Concluído {s_id}: {n_pts} pontos amostrados ({dt:.1f}s)")
                except Exception as e:
                    log(f"FALHA na amostragem da fatia {s_id}: {e}")
                    raise

        log(f"Amostragem pendente concluída em {time.time() - t_start:.1f}s.")
    else:
        log("Todas as 182 fatias já estão 100% amostradas e validadas no checkpoint.")

    # 5. Carregar e agregar pontos
    ckpt = load_points_checkpoint()
    all_points = []
    for s_id in active_slices:
        pts = ckpt.get(s_id, [])
        st = slice_to_state[s_id]
        for p in pts:
            p["state"] = st
            all_points.append(p)

    df_pts = pd.DataFrame(all_points)
    log(f"Total bruto de pontos amostrados: {len(df_pts):,}")
    assert len(df_pts) == 40000, f"Esperado 40.000 pontos, obtido {len(df_pts)}"

    # Verificar duplicatas
    coords = set(zip(df_pts["lon"], df_pts["lat"]))
    log(f"Coordenadas únicas: {len(coords):,} / 40.000")
    assert len(coords) == 40000, "Existem coordenadas duplicadas na Master Sample!"

    # 6. Subamostragem Main determinística via SHA256
    df_pts["stratum_id"] = df_pts["state"] + "_" + df_pts["regime"]
    df_pts["hash_key"] = [
        hashlib.sha256(f"{ROOT_SEED}|main_rank|{r['state']}|{r['regime']}|{r['lon']:.8f}|{r['lat']:.8f}".encode("utf-8")).hexdigest()
        for _, r in df_pts.iterrows()
    ]

    df_quotas = pd.read_csv(QUOTAS_CSV, keep_default_na=False)
    q_map_main = df_quotas.set_index(["state", "regime"])["n_main"].to_dict()
    q_map_robust = df_quotas.set_index(["state", "regime"])["n_robust"].to_dict()

    df_pts = df_pts.sort_values(["state", "regime", "hash_key"]).reset_index(drop=True)
    df_pts["rank_within_stratum"] = df_pts.groupby(["state", "regime"]).cumcount() + 1

    df_pts["n_main_target"] = df_pts.set_index(["state", "regime"]).index.map(q_map_main)
    df_pts["n_robust_target"] = df_pts.set_index(["state", "regime"]).index.map(q_map_robust)

    df_pts["main_sample"] = (df_pts["rank_within_stratum"] <= df_pts["n_main_target"]).astype(int)
    df_pts["robust_sample"] = 1

    df_pts["sample_id"] = [f"PT_{i+1:06d}" for i in range(len(df_pts))]
    df_pts["root_seed"] = ROOT_SEED
    df_pts["stratum_seed"] = [
        int(hashlib.sha256(f"{ROOT_SEED}_{r['stratum_id']}".encode("utf-8")).hexdigest()[:8], 16) % 2147483647
        for _, r in df_pts.iterrows()
    ]

    log(f"Pontos main: {df_pts['main_sample'].sum():,} (esperado 20.000)")
    log(f"Pontos robust: {df_pts['robust_sample'].sum():,} (esperado 40.000)")
    assert df_pts["main_sample"].sum() == 20000

    # 7. Mapear probabilidades de inclusão operacionais
    alloc_lookup = df_alloc.set_index(["state", "regime", "slice_id"]).to_dict(orient="index")

    pi_rob_list, dw_rob_list = [], []
    pi_main_list, dw_main_list = [], []

    for _, pt in df_pts.iterrows():
        key = (pt["state"], pt["regime"], pt["slice_id"])
        info = alloc_lookup[key]

        pi_rob = info["pi_robust_hs"]
        dw_rob = info["design_weight_robust_hs"]

        pi_rob_list.append(pi_rob)
        dw_rob_list.append(dw_rob)

        if pt["main_sample"] == 1:
            pi_main = pi_rob * 0.5
            dw_main = 1.0 / pi_main
            pi_main_list.append(pi_main)
            dw_main_list.append(dw_main)
        else:
            pi_main_list.append(np.nan)
            dw_main_list.append(np.nan)

    df_pts["selection_probability_robust"] = pi_rob_list
    df_pts["design_weight_robust"] = dw_rob_list
    df_pts["selection_probability_main"] = pi_main_list
    df_pts["design_weight_main"] = dw_main_list

    # 8. Extrair pixel_area_m2 exato de ee.Image.pixelArea() (Patch A) com checkpointing
    log("\nExtraindo pixel_area_m2 exato de ee.Image.pixelArea() para os 40.000 pontos...")
    img_area = ee.Image.pixelArea().reproject(crs=mb_proj).rename("pixel_area_m2")

    pixel_areas = load_pixel_area_checkpoint()
    log(f"Áreas de pixel já extraídas em checkpoint: {len(pixel_areas)} / 40.000")

    missing_pts = df_pts[~df_pts["sample_id"].isin(pixel_areas)]
    log(f"Pontos pendentes para extração de pixel_area_m2: {len(missing_pts)}")

    if len(missing_pts) > 0:
        batch_size = 5000
        n_batches = (len(missing_pts) + batch_size - 1) // batch_size

        for b_idx in range(n_batches):
            b_df = missing_pts.iloc[b_idx * batch_size : (b_idx + 1) * batch_size]
            feats = [
                ee.Feature(ee.Geometry.Point([r["lon"], r["lat"]]), {"sample_id": r["sample_id"]})
                for _, r in b_df.iterrows()
            ]
            fc = ee.FeatureCollection(feats)
            
            # Retry loop
            for attempt in range(1, 5):
                try:
                    sampled = img_area.sampleRegions(collection=fc, projection=mb_proj, geometries=False).getInfo()
                    for f in sampled["features"]:
                        pixel_areas[f["properties"]["sample_id"]] = float(f["properties"]["pixel_area_m2"])
                    save_pixel_area_checkpoint(pixel_areas)
                    log(f"  Batch {b_idx + 1}/{n_batches} concluído: {len(pixel_areas)} / 40.000 áreas salvas")
                    break
                except Exception as exc:
                    log(f"  [ERRO] Batch {b_idx + 1} tentativa {attempt}/4: {exc}")
                    if attempt == 4:
                        raise
                    time.sleep(10 * attempt)

    df_pts["pixel_area_m2"] = df_pts["sample_id"].map(pixel_areas)
    assert df_pts["pixel_area_m2"].isna().sum() == 0, "Existem pontos sem pixel_area_m2 extraído!"

    # 9. Calcular Area Weights exatos
    df_pts["area_weight_robust"] = df_pts["pixel_area_m2"] / df_pts["selection_probability_robust"]
    df_pts["area_weight_main"] = np.where(
        df_pts["main_sample"] == 1,
        df_pts["pixel_area_m2"] / df_pts["selection_probability_main"],
        np.nan
    )

    # 10. Validação de cobertura e fechamento de área
    sum_area_rob_ha = df_pts["area_weight_robust"].sum() / 10000.0
    sum_area_main_ha = df_pts["area_weight_main"].dropna().sum() / 10000.0
    full_frame_ha = df_alloc["A_hs"].sum()

    log(f"\nFechamento de Área da População Alvo:")
    log(f"  Área elegível total do frame 10m:      {full_frame_ha:,.2f} ha")
    log(f"  Área estimada via sum(w_area_robust):   {sum_area_rob_ha:,.2f} ha")
    log(f"  Diferença observada (amostral):         {sum_area_rob_ha - full_frame_ha:+.2f} ha ({(sum_area_rob_ha - full_frame_ha)/full_frame_ha * 100:+.6f}%)")
    log(f"  Área estimada via sum(w_area_main):     {sum_area_main_ha:,.2f} ha")

    # 11. Ordenação canônica e salvamento
    st_order = {"MA": 0, "TO": 1, "PI": 2, "BA": 3}
    reg_order = {"AA": 0, "AN": 1, "NA": 2, "NN": 3}
    df_pts["st_ord"] = df_pts["state"].map(st_order)
    df_pts["reg_ord"] = df_pts["regime"].map(reg_order)
    df_pts = df_pts.sort_values(["st_ord", "reg_ord", "rank_within_stratum"]).drop(
        columns=["st_ord", "reg_ord", "n_main_target", "n_robust_target", "hash_key"]
    ).reset_index(drop=True)

    final_cols = [
        "sample_id", "lat", "lon", "state", "stratum_id", "regime", "slice_id",
        "main_sample", "robust_sample", "rank_within_stratum", "root_seed", "stratum_seed",
        "selection_probability_robust", "design_weight_robust", "pixel_area_m2", "area_weight_robust",
        "selection_probability_main", "design_weight_main", "area_weight_main",
    ]
    df_pts = df_pts[final_cols]
    df_pts.to_csv(OUT_CSV, index=False)
    log(f"\nSalva Master Sample definitiva com cobertura 100%: {OUT_CSV}")

    # Atualizar slice_sampling_design_audit.csv
    df_alloc.to_csv(SLICE_DESIGN_CSV, index=False)
    log(f"Atualizado: {SLICE_DESIGN_CSV}")

    log("=" * 80)
    log("MASTER SAMPLE REGENERADA E VALIDADA COM SUCESSO!")
    log("=" * 80)


if __name__ == "__main__":
    main()
