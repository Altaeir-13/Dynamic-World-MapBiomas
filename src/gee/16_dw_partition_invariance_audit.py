"""
16_dw_partition_invariance_audit.py — Auditoria de Invariância à Partição Espacial (Checkpoint 3C)
==================================================================================================
Avalia se a estratégia computacional de particionamento em fatias (slices) introduz
qualquer alteração nas probabilidades, classes ou distâncias de borda do Dynamic World.

Metodologia (Seções 1 a 5 da diretiva):
  1. Amostra de Teste (N = 1.000 pontos, seed = 25):
     - 500 pontos situados a <= 300 m da fronteira da slice
     - 500 pontos distribuídos pelo MATOPIBA
  2. Comparação dos Quatro Contextos Espaciais:
     - Contexto A: slice_geom original
     - Contexto B: slice_geom com buffer de 0.05° (~5.5 km)
     - Contexto C: state_geom (geometria completa do estado)
     - Contexto D: matopiba_geom (domínio fixo MATOPIBA)
  3. Variáveis Avaliadas:
     - 9 probabilidades anuais normalizadas (water..snow_and_ice)
     - probability_sum_before_normalization
     - n_valid_months
     - annual_class_index, dw_crop
     - distance_edge_dw_m (EPSG:5880, 250m)
  4. Processamento Concorrente com Checkpointing e Batches de 50 pontos para evitar timeout.
  5. Salva: tables/dw_partition_invariance_audit.csv
"""

from __future__ import annotations

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

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

import ee
import numpy as np
import pandas as pd
from pyproj import Transformer
from shapely.geometry import Point, box, shape
from shapely.ops import transform

from src.gee.dw_annual import (
    PROJECT_ID,
    DW_PROB_BANDS,
    build_dw_annual_2025,
    get_mapbiomas_projection,
)

DATA_REF = BASE_DIR / "data" / "reference"
DATA_PROC = BASE_DIR / "data" / "processed"
TABLES_DIR = BASE_DIR / "tables"

STATES_GEOJSON = DATA_REF / "matopiba_states.geojson"
BOUNDARY_GEOJSON = DATA_REF / "matopiba_boundary.geojson"
MASTER_POINTS_CSV = DATA_PROC / "master_sampling_points.csv"
OUT_AUDIT_CSV = TABLES_DIR / "dw_partition_invariance_audit.csv"
CHECKPOINT_INVARIANCE = DATA_PROC / "partition_invariance_checkpoint.json"

ROOT_SEED = 25
STEP_DEG = 0.75
MAX_WORKERS = 4
BATCH_SIZE = 50
LOCK = threading.Lock()


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


def make_dw_dist_image(dw_annual_img: dict[str, ee.Image], mb_proj: ee.Projection) -> ee.Image:
    annual_dw_comp = dw_annual_img["annual_10m_raw"]
    dw_max = annual_dw_comp.select(DW_PROB_BANDS).reduce(ee.Reducer.max())
    is_crop_dw = annual_dw_comp.select("crops").eq(dw_max).And(annual_dw_comp.select("crops").mask())
    is_noncrop_dw = is_crop_dw.Not().And(annual_dw_comp.select("crops").mask())

    crop_dw_5880 = is_crop_dw.unmask(0).reproject(crs="EPSG:5880", scale=10)
    noncrop_dw_5880 = is_noncrop_dw.unmask(0).reproject(crs="EPSG:5880", scale=10)

    kernel = ee.Kernel.square(radius=1, units="pixels")
    crop_has_noncrop_dw = noncrop_dw_5880.reduceNeighborhood(ee.Reducer.max(), kernel)
    noncrop_has_crop_dw = crop_dw_5880.reduceNeighborhood(ee.Reducer.max(), kernel)

    edge_dw = (
        crop_dw_5880.eq(1).And(crop_has_noncrop_dw.eq(1))
    ).Or(
        noncrop_dw_5880.eq(1).And(noncrop_has_crop_dw.eq(1))
    )

    dist_dw = (
        edge_dw.fastDistanceTransform(neighborhood=25, units="pixels", metric="squared_euclidean")
        .sqrt()
        .multiply(10)
        .clamp(0, 250)
        .reproject(crs=mb_proj)
        .rename("distance_edge_dw_m")
    )
    return dist_dw


def build_context_stack(region_ee: ee.Geometry, mb_proj: ee.Projection, prefix: str) -> ee.Image:
    dw_annual = build_dw_annual_2025(region=region_ee, mb_proj=mb_proj)
    dist_img = make_dw_dist_image(dw_annual, mb_proj)

    bands = [
        dw_annual["normalized_probs"].rename([f"{prefix}_p_{b}" for b in DW_PROB_BANDS]),
        dw_annual["raw_prob_sum"].rename(f"{prefix}_raw_prob_sum"),
        dw_annual["annual_class_index"].rename(f"{prefix}_annual_class_index"),
        dw_annual["dw_crop"].rename(f"{prefix}_dw_crop"),
        dw_annual["n_valid_months"].rename(f"{prefix}_n_valid_months"),
        dist_img.rename(f"{prefix}_distance_edge_dw_m"),
    ]
    return ee.Image.cat(bands)


def load_checkpoint() -> dict[str, dict[str, Any]]:
    if CHECKPOINT_INVARIANCE.exists():
        try:
            with open(CHECKPOINT_INVARIANCE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_checkpoint_batch(batch_records: dict[str, dict[str, Any]]) -> None:
    with LOCK:
        ckpt = load_checkpoint()
        for sid, props in batch_records.items():
            if sid not in ckpt:
                ckpt[sid] = {}
            ckpt[sid].update(props)
        with open(CHECKPOINT_INVARIANCE, "w", encoding="utf-8") as f:
            json.dump(ckpt, f)


def sample_batch_with_retry(
    img_stack: ee.Image,
    pts_df: pd.DataFrame,
    mb_proj: ee.Projection,
    max_retries: int = 4
) -> dict[str, dict[str, Any]]:
    features = [
        ee.Feature(
            ee.Geometry.Point([row["lon"], row["lat"]]),
            {"sample_id": row["sample_id"]}
        )
        for _, row in pts_df.iterrows()
    ]
    fc = ee.FeatureCollection(features)

    for attempt in range(1, max_retries + 1):
        try:
            sampled = img_stack.sampleRegions(
                collection=fc,
                projection=mb_proj,
                geometries=False
            ).getInfo()
            recs = {f["properties"]["sample_id"]: f["properties"] for f in sampled["features"]}
            return recs
        except Exception as exc:
            log(f"    [ERRO Tentativa {attempt}/{max_retries}]: {exc}")
            if attempt == max_retries:
                raise
            time.sleep(10 * attempt)
    return {}


def main():
    log("=" * 80)
    log("CHECKPOINT 3C: SANITY CHECK DE INVARIÂNCIA À PARTIÇÃO ESPACIAL")
    log("=" * 80)

    ee.Initialize(project=PROJECT_ID)
    mb_proj = get_mapbiomas_projection()

    # 1. Carregar geometrias
    with open(STATES_GEOJSON, "r", encoding="utf-8") as f:
        states_data = json.load(f)

    with open(BOUNDARY_GEOJSON, "r", encoding="utf-8") as f:
        matopiba_data = json.load(f)

    matopiba_shp = shape(matopiba_data["features"][0]["geometry"])
    matopiba_ee = ee.Geometry(matopiba_shp.__geo_interface__)

    slices_shp = {}
    state_ees = {}

    for feat in states_data["features"]:
        st = feat["properties"]["state"]
        shp = shape(feat["geometry"])
        state_ees[st] = ee.Geometry(shp.__geo_interface__)
        pieces = partition_state(st, shp, STEP_DEG)
        for s_id, s_geom in pieces:
            slices_shp[s_id] = s_geom

    trans = Transformer.from_crs("EPSG:4326", "EPSG:5880", always_xy=True).transform
    slices_5880 = {s_id: transform(trans, geom) for s_id, geom in slices_shp.items()}

    # 2. Selecionar Amostra de Teste (N = 1.000 pontos)
    df_master = pd.read_csv(MASTER_POINTS_CSV, keep_default_na=False)
    log(f"Master sample lida: {len(df_master):,} pontos")

    # Calcular distâncias à fronteira das fatias em EPSG:5880
    log("Calculando distâncias à fronteira das fatias em EPSG:5880...")
    slice_boundary_dists = {}
    for s_id, grp in df_master.groupby("slice_id"):
        boundary_geom = slices_5880[s_id].boundary
        for _, r in grp.iterrows():
            pt_5880 = transform(trans, Point(r["lon"], r["lat"]))
            slice_boundary_dists[r["sample_id"]] = float(boundary_geom.distance(pt_5880))

    df_master["slice_boundary_dist_m"] = df_master["sample_id"].map(slice_boundary_dists)

    border_pool = df_master[df_master["slice_boundary_dist_m"] <= 300.0]
    log(f"Total de pontos da Master a <= 300m da fronteira da slice: {len(border_pool):,}")
    assert len(border_pool) >= 500, "Menos de 500 pontos a <= 300m da borda!"

    # 500 pontos de borda (seed = 25)
    sample_border = border_pool.sample(n=500, random_state=ROOT_SEED).copy()
    sample_border["selection_type"] = "slice_border_le_300m"

    # 500 pontos gerais (seed = 25, sem sobreposição)
    remaining_pool = df_master[~df_master["sample_id"].isin(sample_border["sample_id"])]
    sample_general = remaining_pool.sample(n=500, random_state=ROOT_SEED).copy()
    sample_general["selection_type"] = "general_matopiba"

    sample_pts = pd.concat([sample_border, sample_general], ignore_index=True)
    log(f"Amostra de teste selecionada: {len(sample_pts):,} pontos (500 borda <= 300m + 500 gerais)")

    # Distribuição das distâncias
    b_dists = sample_pts["slice_boundary_dist_m"]
    log("Distribuição das distâncias às fronteiras das slices (m):")
    log(f"  Mínimo:  {b_dists.min():.1f} m")
    log(f"  Q1:      {np.percentile(b_dists, 25):.1f} m")
    log(f"  Mediana: {np.median(b_dists):.1f} m")
    log(f"  Média:   {np.mean(b_dists):.1f} m")
    log(f"  Q3:      {np.percentile(b_dists, 75):.1f} m")
    log(f"  Máximo:  {b_dists.max():.1f} m")

    ckpt = load_checkpoint()

    # 3. Contexto A e B (Por fatia e fatia com buffer)
    slices_in_sample = sample_pts["slice_id"].unique()
    log(f"\n[1/3] Extraindo Contextos A (Slice) e B (Slice + 5km Buffer) para {len(slices_in_sample)} fatias...")

    pending_slices = []
    for s_id in slices_in_sample:
        sub_pts = sample_pts[sample_pts["slice_id"] == s_id]
        all_done = all(sid in ckpt and "ctxA_crops" in ckpt[sid] and "ctxB_crops" in ckpt[sid] for sid in sub_pts["sample_id"])
        if not all_done:
            pending_slices.append(s_id)

    log(f"  Fatias já concluídas em checkpoint: {len(slices_in_sample) - len(pending_slices)} / {len(slices_in_sample)}")
    log(f"  Fatias pendentes: {len(pending_slices)}")

    if pending_slices:
        t0 = time.time()
        completed = len(slices_in_sample) - len(pending_slices)

        def worker_slice(s_id: str):
            sub_pts = sample_pts[sample_pts["slice_id"] == s_id]
            s_shp = slices_shp[s_id]
            s_geom_A = ee.Geometry(s_shp.__geo_interface__)
            s_geom_B = ee.Geometry(s_shp.buffer(0.05).__geo_interface__)

            stack_A = build_context_stack(s_geom_A, mb_proj, prefix="ctxA")
            stack_B = build_context_stack(s_geom_B, mb_proj, prefix="ctxB")
            combined_AB = ee.Image.cat([stack_A, stack_B])

            recs = sample_batch_with_retry(combined_AB, sub_pts, mb_proj)
            save_checkpoint_batch(recs)
            return s_id, len(recs)

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(worker_slice, s_id): s_id for s_id in pending_slices}
            for fut in as_completed(futures):
                s_id = futures[fut]
                s_id, n_recs = fut.result()
                completed += 1
                if completed % 25 == 0 or completed == len(slices_in_sample):
                    log(f"    [{completed}/{len(slices_in_sample)}] Fatias concluídas ({time.time() - t0:.1f}s)")

    # 4. Contexto C (Geometria Completa do Estado em Batches de 50)
    log("\n[2/3] Extraindo Contexto C (Geometria Completa do Estado em Batches)...")
    ckpt = load_checkpoint()
    for st, st_geom in state_ees.items():
        st_pts = sample_pts[sample_pts["state"] == st]
        pending_st = st_pts[~st_pts["sample_id"].apply(lambda sid: sid in ckpt and "ctxC_crops" in ckpt[sid])]
        log(f"  Estado {st}: total {len(st_pts)} pontos, pendentes {len(pending_st)}")

        if len(pending_st) > 0:
            stack_C = build_context_stack(st_geom, mb_proj, prefix="ctxC")
            n_batches = (len(pending_st) + BATCH_SIZE - 1) // BATCH_SIZE

            def worker_st_batch(b_idx: int):
                b_df = pending_st.iloc[b_idx * BATCH_SIZE : (b_idx + 1) * BATCH_SIZE]
                recs = sample_batch_with_retry(stack_C, b_df, mb_proj)
                save_checkpoint_batch(recs)
                return len(recs)

            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = [executor.submit(worker_st_batch, i) for i in range(n_batches)]
                for fut in as_completed(futures):
                    fut.result()

    # 5. Contexto D (Domínio Fixo MATOPIBA em Batches de 50)
    log("\n[3/3] Extraindo Contexto D (Domínio Fixo MATOPIBA em Batches de 50)...")
    ckpt = load_checkpoint()
    pending_D = sample_pts[~sample_pts["sample_id"].apply(lambda sid: sid in ckpt and "ctxD_crops" in ckpt[sid])]
    log(f"  Pontos pendentes para Contexto D: {len(pending_D)} / {len(sample_pts)}")

    if len(pending_D) > 0:
        stack_D = build_context_stack(matopiba_ee, mb_proj, prefix="ctxD")
        n_batches_D = (len(pending_D) + BATCH_SIZE - 1) // BATCH_SIZE
        t0 = time.time()
        completed_D = 0

        def worker_D_batch(b_idx: int):
            b_df = pending_D.iloc[b_idx * BATCH_SIZE : (b_idx + 1) * BATCH_SIZE]
            recs = sample_batch_with_retry(stack_D, b_df, mb_proj)
            save_checkpoint_batch(recs)
            return len(recs)

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(worker_D_batch, i) for i in range(n_batches_D)]
            for fut in as_completed(futures):
                n_done = fut.result()
                completed_D += n_done
                log(f"    [{completed_D}/{len(pending_D)}] Pontos do Contexto D extraídos ({time.time() - t0:.1f}s)")

    # 6. Consolidar e Analisar Tabela de Auditoria
    log("\nConsolidando tabela final e comparando contextos...")
    ckpt = load_checkpoint()
    audit_rows = []

    for _, r in sample_pts.iterrows():
        sid = r["sample_id"]
        props = ckpt[sid]

        row_dict = {
            "sample_id": sid,
            "state": r["state"],
            "regime": r["regime"],
            "slice_id": r["slice_id"],
            "selection_type": r["selection_type"],
            "slice_boundary_dist_m": r["slice_boundary_dist_m"],
            # Contexto A
            "ctxA_class_index": int(props["ctxA_annual_class_index"]),
            "ctxA_annual_class": DW_PROB_BANDS[int(props["ctxA_annual_class_index"])],
            "ctxA_dw_crop": int(props["ctxA_dw_crop"]),
            "ctxA_n_valid_months": int(props["ctxA_n_valid_months"]),
            "ctxA_raw_prob_sum": float(props["ctxA_raw_prob_sum"]),
            "ctxA_dist_edge_dw_m": float(props["ctxA_distance_edge_dw_m"]),
            # Contexto B
            "ctxB_class_index": int(props["ctxB_annual_class_index"]),
            "ctxB_annual_class": DW_PROB_BANDS[int(props["ctxB_annual_class_index"])],
            "ctxB_dw_crop": int(props["ctxB_dw_crop"]),
            "ctxB_n_valid_months": int(props["ctxB_n_valid_months"]),
            "ctxB_raw_prob_sum": float(props["ctxB_raw_prob_sum"]),
            "ctxB_dist_edge_dw_m": float(props["ctxB_distance_edge_dw_m"]),
            # Contexto C
            "ctxC_class_index": int(props["ctxC_annual_class_index"]),
            "ctxC_annual_class": DW_PROB_BANDS[int(props["ctxC_annual_class_index"])],
            "ctxC_dw_crop": int(props["ctxC_dw_crop"]),
            "ctxC_n_valid_months": int(props["ctxC_n_valid_months"]),
            "ctxC_raw_prob_sum": float(props["ctxC_raw_prob_sum"]),
            "ctxC_dist_edge_dw_m": float(props["ctxC_distance_edge_dw_m"]),
            # Contexto D
            "ctxD_class_index": int(props["ctxD_annual_class_index"]),
            "ctxD_annual_class": DW_PROB_BANDS[int(props["ctxD_annual_class_index"])],
            "ctxD_dw_crop": int(props["ctxD_dw_crop"]),
            "ctxD_n_valid_months": int(props["ctxD_n_valid_months"]),
            "ctxD_raw_prob_sum": float(props["ctxD_raw_prob_sum"]),
            "ctxD_dist_edge_dw_m": float(props["ctxD_distance_edge_dw_m"]),
        }

        for b in DW_PROB_BANDS:
            row_dict[f"ctxA_p_{b}"] = float(props[f"ctxA_p_{b}"])
            row_dict[f"ctxB_p_{b}"] = float(props[f"ctxB_p_{b}"])
            row_dict[f"ctxC_p_{b}"] = float(props[f"ctxC_p_{b}"])
            row_dict[f"ctxD_p_{b}"] = float(props[f"ctxD_p_{b}"])

        pA = np.array([row_dict[f"ctxA_p_{b}"] for b in DW_PROB_BANDS])
        pB = np.array([row_dict[f"ctxB_p_{b}"] for b in DW_PROB_BANDS])
        pC = np.array([row_dict[f"ctxC_p_{b}"] for b in DW_PROB_BANDS])
        pD = np.array([row_dict[f"ctxD_p_{b}"] for b in DW_PROB_BANDS])

        row_dict["max_diff_prob_A_vs_B"] = float(np.max(np.abs(pA - pB)))
        row_dict["max_diff_prob_A_vs_C"] = float(np.max(np.abs(pA - pC)))
        row_dict["max_diff_prob_A_vs_D"] = float(np.max(np.abs(pA - pD)))
        row_dict["max_diff_prob_C_vs_D"] = float(np.max(np.abs(pC - pD)))

        audit_rows.append(row_dict)

    df_audit = pd.DataFrame(audit_rows)
    df_audit.to_csv(OUT_AUDIT_CSV, index=False)
    log(f"Salva tabela de auditoria: {OUT_AUDIT_CSV} ({len(df_audit)} linhas, {len(df_audit.columns)} colunas)")

    # 7. Relatório Comparativo Formal
    pairs = [
        ("A_vs_B", "Contexto A (Slice) vs Contexto B (Slice Buffered)", "ctxA", "ctxB"),
        ("A_vs_C", "Contexto A (Slice) vs Contexto C (Estado)", "ctxA", "ctxC"),
        ("A_vs_D", "Contexto A (Slice) vs Contexto D (MATOPIBA Fixo)", "ctxA", "ctxD"),
        ("C_vs_D", "Contexto C (Estado) vs Contexto D (MATOPIBA Fixo)", "ctxC", "ctxD"),
    ]

    print("\n" + "=" * 80)
    print("RELATÓRIO DE INVARIÂNCIA À PARTIÇÃO ESPACIAL:")
    print("=" * 80)

    summary_metrics = []
    for pair_id, pair_label, p1, p2 in pairs:
        max_prob_diffs = []
        for _, row in df_audit.iterrows():
            v1 = np.array([row[f"{p1}_p_{b}"] for b in DW_PROB_BANDS])
            v2 = np.array([row[f"{p2}_p_{b}"] for b in DW_PROB_BANDS])
            max_prob_diffs.append(np.max(np.abs(v1 - v2)))

        max_prob_diff = float(np.max(max_prob_diffs))
        mean_prob_diff = float(np.mean(max_prob_diffs))

        class_mismatches = int((df_audit[f"{p1}_class_index"] != df_audit[f"{p2}_class_index"]).sum())
        dw_crop_mismatches = int((df_audit[f"{p1}_dw_crop"] != df_audit[f"{p2}_dw_crop"]).sum())
        months_mismatches = int((df_audit[f"{p1}_n_valid_months"] != df_audit[f"{p2}_n_valid_months"]).sum())

        # Distâncias de borda gerais
        edge_diffs = np.abs(df_audit[f"{p1}_dist_edge_dw_m"] - df_audit[f"{p2}_dist_edge_dw_m"])
        max_edge_diff = float(np.max(edge_diffs))
        mean_edge_diff = float(np.mean(edge_diffs))

        # Distâncias de borda para pontos a <= 300m da fronteira
        border_sub = df_audit[df_audit["slice_boundary_dist_m"] <= 300.0]
        edge_diffs_border = np.abs(border_sub[f"{p1}_dist_edge_dw_m"] - border_sub[f"{p2}_dist_edge_dw_m"])
        max_edge_border = float(np.max(edge_diffs_border))
        mean_edge_border = float(np.mean(edge_diffs_border))

        summary_metrics.append({
            "pair": pair_label,
            "max_abs_prob_diff": max_prob_diff,
            "mean_abs_prob_diff": mean_prob_diff,
            "n_class_mismatches": class_mismatches,
            "n_dw_crop_mismatches": dw_crop_mismatches,
            "n_valid_months_mismatches": months_mismatches,
            "max_edge_dist_diff_m": max_edge_diff,
            "mean_edge_dist_diff_m": mean_edge_diff,
            "max_edge_border_le_300m": max_edge_border,
            "mean_edge_border_le_300m": mean_edge_border,
        })

        print(f"\n--- {pair_label} ---")
        print(f"  Diferença máxima de probabilidade: {max_prob_diff:.2e}")
        print(f"  Diferença média de probabilidade:  {mean_prob_diff:.2e}")
        print(f"  Mismatches de annual_class:        {class_mismatches} / {len(df_audit)}")
        print(f"  Mismatches de dw_crop:             {dw_crop_mismatches} / {len(df_audit)}")
        print(f"  Mismatches de n_valid_months:      {months_mismatches} / {len(df_audit)}")
        print(f"  Diferença máxima de dist_edge_dw:  {max_edge_diff:.4f} m (média: {mean_edge_diff:.4f} m)")
        print(f"  Diferença máxima na borda (<=300m):{max_edge_border:.4f} m (média: {mean_edge_border:.4f} m)")

    # 8. Verificação dos Critérios de Aceite
    print("\n" + "=" * 80)
    print("VERIFICAÇÃO DOS CRITÉRIOS DE INVARIÂNCIA (SEÇÕES 3 E 5):")
    print("=" * 80)

    total_class_mismatches = sum(s["n_class_mismatches"] for s in summary_metrics)
    total_crop_mismatches = sum(s["n_dw_crop_mismatches"] for s in summary_metrics)
    total_months_mismatches = sum(s["n_valid_months_mismatches"] for s in summary_metrics)
    max_prob_overall = max(s["max_abs_prob_diff"] for s in summary_metrics)
    max_edge_border_overall = max(s["max_edge_border_le_300m"] for s in summary_metrics)

    c1_class = (total_class_mismatches == 0)
    c2_crop = (total_crop_mismatches == 0)
    c3_months = (total_months_mismatches == 0)
    c4_prob = (max_prob_overall < 1e-5)
    c5_edge = (max_edge_border_overall <= 1.0)

    print(f"1. annual_class mismatches == 0: {c1_class} (total = {total_class_mismatches})")
    print(f"2. dw_crop mismatches == 0:      {c2_crop} (total = {total_crop_mismatches})")
    print(f"3. n_valid_months mismatches == 0: {c3_months} (total = {total_months_mismatches})")
    print(f"4. Diferença máx de probabilidade < 1e-5: {c4_prob} (max = {max_prob_overall:.2e})")
    print(f"5. Diferença de distância de borda (<=300m) <= 1.0m: {c5_edge} (max = {max_edge_border_overall:.4f} m)")

    passed_all = c1_class and c2_crop and c3_months and c4_prob and c5_edge

    print("\n" + "=" * 80)
    print(f"RESULTADO FINAL: {'CHECKPOINT 3C: PASS' if passed_all else 'CHECKPOINT 3C: BLOCKED'}")
    print("=" * 80)


if __name__ == "__main__":
    main()
