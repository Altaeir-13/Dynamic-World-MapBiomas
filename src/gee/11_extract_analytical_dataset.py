"""
11_extract_analytical_dataset.py — Extração Analítica dos 40k Pontos (Checkpoint 3D)
==================================================================================
Extrai para os 40.000 pontos congelados da Master Sample (root_seed=25):
  1. Bandas Anuais Autoritativas extraídas do stack canônico fixo:
     - 9 probabilidades anuais normalizadas (p_water..p_snow_and_ice)
     - probability_sum_before_normalization_annual
     - annual_class_index, annual_class, dw_crop
     - n_valid_months (garantido >= 8)
     - mb_crop, regime_code
     - Exigência: 100.000% de paridade com o regime congelado da Master!
  2. Série mensal Dynamic World 2025 (12 meses particionada em 4 trimestres):
     - probabilidades das 9 classes normalizadas para meses válidos
     - probability_sum_before_normalization
     - n_raw_obs, n_valid_days, month_valid = (n_valid_days > 0 and prob_sum > 0)
  3. MapBiomas Cobertura 2025 e série histórica 2017–2025:
     - mapbiomas_class, mapbiomas_crop (18/21 = 0)
     - mapbiomas_stability_eligible_2017_2025
     - mapbiomas_stable_2017_2025
  4. Distâncias métricas truncadas de borda (EPSG:5880, 250m):
     - distance_edge_mb_m, distance_edge_dw_m, distance_edge_min_m
  5. Métricas Teórico-Informacionais e Temporais em Python:
     - entropy_annual = -sum(p_k * ln(p_k)) / ln(9) (autoritativo)
     - entropy_temporal_mean = H(M), onde M é a média dos p_m mensais normalizados
     - entropy_monthly_mean = mean(H(p_m))
     - jsd_temporal = max(0, entropy_temporal_mean - entropy_monthly_mean)
     - stability = mean(argmax(p_m) == annual_class)
     - top1_class, top1_probability, top2_class, top2_probability, top2_margin, competitor_class

Gera:
  - data/processed/dw_monthly.parquet (480.000 linhas, 15 colunas)
  - data/processed/samples_annual.parquet (40.000 linhas, 51 colunas)
  - data/processed/samples_annual.csv (40.000 linhas, 51 colunas)
"""

from __future__ import annotations

import json
import math
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

import ee
import numpy as np
import pandas as pd
from shapely.geometry import box, shape

from src.gee.dw_annual import (
    PROJECT_ID,
    DW_PROB_BANDS,
    DW_START,
    DW_END,
    get_harmonized_crosswalk_layers,
    get_mapbiomas_projection,
    get_source_support_domain,
    DATES_CACHE_PATH,
    DW_COLLECTION,
    MB_ASSET,
    CROP_CODES,
    EXCLUDED_CODES,
)

DATA_REF = BASE_DIR / "data" / "reference"
DATA_PROC = BASE_DIR / "data" / "processed"
TABLES_DIR = BASE_DIR / "tables"

STATES_GEOJSON = DATA_REF / "matopiba_states.geojson"
MASTER_POINTS_CSV = DATA_PROC / "master_sampling_points.csv"
EXTRACTION_DIR = DATA_PROC / "extraction_slices"

DW_MONTHLY_PARQUET = DATA_PROC / "dw_monthly.parquet"
SAMPLES_ANNUAL_PARQUET = DATA_PROC / "samples_annual.parquet"
SAMPLES_ANNUAL_CSV = DATA_PROC / "samples_annual.csv"

MAX_WORKERS = 2


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def partition_state(state: str, geom_shp, step: float = 0.75) -> list[tuple[str, any]]:
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


def get_completed_slices() -> set[str]:
    EXTRACTION_DIR.mkdir(parents=True, exist_ok=True)
    return {f.stem for f in EXTRACTION_DIR.glob("*.json")}


def load_slice_checkpoint(slice_id: str) -> list[dict[str, Any]]:
    p = EXTRACTION_DIR / f"{slice_id}.json"
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_slice_checkpoint(slice_id: str, records: list[dict[str, Any]]) -> None:
    EXTRACTION_DIR.mkdir(parents=True, exist_ok=True)
    temp_file = EXTRACTION_DIR / f"{slice_id}.tmp"
    final_file = EXTRACTION_DIR / f"{slice_id}.json"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(records, f)
    temp_file.replace(final_file)


def build_canonical_annual_stack() -> ee.Image:
    """Constrói o stack de 27 bandas anuais e espaciais no domínio canônico fixo."""
    layers = get_harmonized_crosswalk_layers()
    dw_dict = layers["dw_dict"]

    bands = [
        dw_dict["normalized_probs"].rename([f"auth_p_{b}" for b in DW_PROB_BANDS]),
        dw_dict["raw_prob_sum"].rename("auth_raw_prob_sum"),
        dw_dict["annual_class_index"].rename("auth_annual_class_index"),
        dw_dict["dw_crop"].rename("auth_dw_crop"),
        dw_dict["n_valid_months"].rename("auth_n_valid_months"),
        layers["regime_code"].rename("auth_regime_code"),
        layers["mb_crop"].rename("auth_mb_crop"),
        layers["distance_edge_mb_m"],
        layers["distance_edge_dw_m"],
        layers["distance_edge_min_m"],
    ]

    mb_img = ee.Image(MB_ASSET)
    mb_bands = [f"classification_{y}" for y in range(2017, 2026)]
    mb_hist = mb_img.select(mb_bands)
    for b in mb_bands:
        bands.append(mb_hist.select(b))

    return ee.Image.cat(bands)


def build_canonical_quarter_stack(
    months: list[int],
    dw_col: ee.ImageCollection,
    dates_dict: dict[str, list[str]],
) -> ee.Image:
    """Constrói o stack trimestral (3 meses = 36 bandas) no domínio canônico fixo."""
    q_bands = []
    for m in months:
        start = f"2025-{m:02d}-01"
        end = f"2025-{m+1:02d}-01" if m < 12 else "2026-01-01"
        dw_m = dw_col.filterDate(start, end)
        dates_m = ee.List(dates_dict[f"{m:02d}"])

        def make_daily(d):
            d_start = ee.Date(d)
            d_end = d_start.advance(1, "day")
            return dw_m.filterDate(d_start, d_end).select(DW_PROB_BANDS).mean().toFloat().set("date", d)

        daily_col = ee.ImageCollection(dates_m.map(make_daily))
        comp_m = daily_col.mean().select(DW_PROB_BANDS).toFloat()
        prob_sum = comp_m.reduce(ee.Reducer.sum())
        n_raw = dw_m.select("label").count()
        n_days = daily_col.select("water").count()

        for b in DW_PROB_BANDS:
            q_bands.append(comp_m.select(b).unmask(0.0).rename(f"{b}_m{m:02d}"))
        q_bands.append(prob_sum.unmask(0.0).rename(f"prob_sum_m{m:02d}"))
        q_bands.append(n_raw.unmask(0).rename(f"n_raw_m{m:02d}"))
        q_bands.append(n_days.unmask(0).rename(f"n_days_m{m:02d}"))

    return ee.Image.cat(q_bands)


def sample_with_retry(
    img: ee.Image,
    fc: ee.FeatureCollection,
    mb_proj: ee.Projection,
    name: str,
    slice_id: str,
    expected_n: int,
    max_retries: int = 5,
) -> dict[str, dict[str, Any]]:
    for attempt in range(1, max_retries + 1):
        try:
            sampled = img.sampleRegions(
                collection=fc,
                projection=mb_proj,
                geometries=False,
            ).getInfo()["features"]
            if len(sampled) != expected_n:
                raise ValueError(f"Slice {slice_id} ({name}): esperado {expected_n} pontos, extraído {len(sampled)}")
            return {f["properties"]["sample_id"]: f["properties"] for f in sampled}
        except Exception as exc:
            if attempt == max_retries:
                log(f"  [ERRO DEFINITIVO] Fatia {slice_id} ({name}) após {max_retries} tentativas: {exc}")
                raise
            log(f"  [RETRY] Fatia {slice_id} ({name}) tentativa {attempt}/{max_retries} falhou: {exc}. Aguardando {6 * attempt}s...")
            time.sleep(6 * attempt)
    return {}


def process_slice(
    slice_id: str,
    slice_df: pd.DataFrame,
    annual_stack: ee.Image,
    q_stacks: list[ee.Image],
    mb_proj: ee.Projection,
) -> list[dict[str, Any]]:
    n_pts = len(slice_df)
    features = [
        ee.Feature(
            ee.Geometry.Point([row["lon"], row["lat"]]),
            {"sample_id": row["sample_id"]},
        )
        for _, row in slice_df.iterrows()
    ]
    fc = ee.FeatureCollection(features)

    # 1. Extração Anual (27 bandas)
    recs_annual = sample_with_retry(annual_stack, fc, mb_proj, "annual", slice_id, n_pts)

    merged_by_id = {sid: dict(props) for sid, props in recs_annual.items()}

    # 2. Extração dos 4 Trimestres (36 bandas cada)
    for q_idx, q_stk in enumerate(q_stacks, 1):
        recs_q = sample_with_retry(q_stk, fc, mb_proj, f"Q{q_idx}", slice_id, n_pts)
        for sid, props in recs_q.items():
            merged_by_id[sid].update(props)

    # Ordenar pelos sample_id originais da fatia
    ordered_records = [merged_by_id[row["sample_id"]] for _, row in slice_df.iterrows()]
    return ordered_records


def compute_metrics(
    records: list[dict[str, Any]],
    df_pts: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    log("Calculando métricas analíticas e temporais em Python...")
    rec_by_id = {r["sample_id"]: r for r in records}

    monthly_rows = []
    annual_rows = []

    LN_9 = math.log(9)
    regime_map = {1: "AA", 2: "AN", 3: "NA", 4: "NN"}

    for _, pt in df_pts.iterrows():
        sid = pt["sample_id"]
        props = rec_by_id[sid]

        # 1. Série Mensal
        p_monthly_norm_list = []
        h_monthly_list = []
        valid_months_count = 0
        matching_months_count = 0

        auth_class_idx = int(props["auth_annual_class_index"])
        auth_class_name = DW_PROB_BANDS[auth_class_idx]
        auth_dw_crop = int(props["auth_dw_crop"])
        auth_raw_sum = float(props["auth_raw_prob_sum"])
        auth_valid_months = int(props["auth_n_valid_months"])
        auth_regime = regime_map[int(props["auth_regime_code"])]

        # Paridade estrita com o regime congelado
        assert auth_regime == pt["regime"], (
            f"Paridade violada para {sid}: extraído {auth_regime}, master {pt['regime']}"
        )
        assert auth_valid_months >= 8, (
            f"Critério de elegibilidade temporal violado para {sid}: n_valid_months={auth_valid_months} < 8"
        )

        for m in range(1, 13):
            n_raw = int(props.get(f"n_raw_m{m:02d}", 0))
            n_days = int(props.get(f"n_days_m{m:02d}", 0))
            prob_sum_m = float(props.get(f"prob_sum_m{m:02d}", 0.0))

            m_valid = 1 if (n_days > 0 and prob_sum_m > 1e-9) else 0

            raw_probs = [float(props.get(f"{b}_m{m:02d}", 0.0)) for b in DW_PROB_BANDS]

            if m_valid == 1:
                norm_probs = [val / prob_sum_m for val in raw_probs]
                p_monthly_norm_list.append(norm_probs)
                valid_months_count += 1

                # Entropia mensal de Shannon
                h_m = -sum(p * math.log(p) for p in norm_probs if p > 1e-12) / LN_9
                h_monthly_list.append(h_m)

                # Comparar argmax mensal com classe anual autoritativa
                m_class_idx = int(np.argmax(norm_probs))
                if m_class_idx == auth_class_idx:
                    matching_months_count += 1
            else:
                norm_probs = [0.0] * 9

            m_row = {
                "sample_id": sid,
                "month": m,
                "month_valid": m_valid,
                "n_raw_obs": n_raw,
                "n_valid_days": n_days,
                "probability_sum_before_normalization": prob_sum_m,
            }
            for i, b in enumerate(DW_PROB_BANDS):
                m_row[b] = norm_probs[i]

            monthly_rows.append(m_row)

        # 2. Vetor Anual Autoritativo
        auth_p_vec = [float(props[f"auth_p_{b}"]) for b in DW_PROB_BANDS]

        # Entropia Anual Autoritativa
        h_annual = -sum(p * math.log(p) for p in auth_p_vec if p > 1e-12) / LN_9

        # Métricas Temporais (JSD e Estabilidade)
        if valid_months_count > 0:
            M_vec = np.mean(p_monthly_norm_list, axis=0)
            h_temporal_mean = -sum(p * math.log(p) for p in M_vec if p > 1e-12) / LN_9
            h_monthly_mean = float(np.mean(h_monthly_list))
            jsd_temporal = max(0.0, h_temporal_mean - h_monthly_mean)
            stability = matching_months_count / valid_months_count
        else:
            h_temporal_mean = 0.0
            h_monthly_mean = 0.0
            jsd_temporal = 0.0
            stability = 0.0

        # Top 1 e Top 2 a partir do vetor anual autoritativo
        sorted_indices = np.argsort(auth_p_vec)[::-1]
        top1_idx = sorted_indices[0]
        top2_idx = sorted_indices[1]

        top1_class = DW_PROB_BANDS[top1_idx]
        top1_prob = float(auth_p_vec[top1_idx])
        top2_class = DW_PROB_BANDS[top2_idx]
        top2_prob = float(auth_p_vec[top2_idx])
        top2_margin = top1_prob - top2_prob
        competitor = top2_class

        # MapBiomas 2025
        mb_class_2025 = int(props["classification_2025"])
        mb_crop_2025 = 1 if mb_class_2025 in CROP_CODES else 0

        # MapBiomas Estabilidade Histórica 2017–2025
        mb_years_valid = True
        mb_crops_hist = []
        for y in range(2017, 2026):
            c_y = int(props.get(f"classification_{y}", 0))
            if c_y in EXCLUDED_CODES or c_y == 0:
                mb_years_valid = False
            mb_crops_hist.append(1 if c_y in CROP_CODES else 0)

        mb_elig = 1 if mb_years_valid else 0
        mb_stable = 1 if (mb_elig == 1 and len(set(mb_crops_hist)) == 1) else 0

        # Distâncias de borda (EPSG:5880, 250m)
        d_mb = float(props["distance_edge_mb_m"])
        d_dw = float(props["distance_edge_dw_m"])
        d_min = float(props["distance_edge_min_m"])

        # Montar linha anual completa unindo com master sample
        a_row = {
            # Metadados da Amostra (12 colunas)
            "sample_id": sid,
            "lat": pt["lat"],
            "lon": pt["lon"],
            "state": pt["state"],
            "stratum_id": pt["stratum_id"],
            "regime": pt["regime"],
            "slice_id": pt["slice_id"],
            "main_sample": pt["main_sample"],
            "robust_sample": pt["robust_sample"],
            "rank_within_stratum": pt["rank_within_stratum"],
            "root_seed": pt["root_seed"],
            "stratum_seed": pt["stratum_seed"],
            # Probabilidades e Pesos (7 colunas)
            "selection_probability_robust": pt["selection_probability_robust"],
            "design_weight_robust": pt["design_weight_robust"],
            "pixel_area_m2": pt["pixel_area_m2"],
            "area_weight_robust": pt["area_weight_robust"],
            "selection_probability_main": pt["selection_probability_main"],
            "design_weight_main": pt["design_weight_main"],
            "area_weight_main": pt["area_weight_main"],
            # 9 Probabilidades Anuais Autoritativas (9 colunas)
            "p_water": auth_p_vec[0],
            "p_trees": auth_p_vec[1],
            "p_grass": auth_p_vec[2],
            "p_flooded_vegetation": auth_p_vec[3],
            "p_crops": auth_p_vec[4],
            "p_shrub_and_scrub": auth_p_vec[5],
            "p_built": auth_p_vec[6],
            "p_bare": auth_p_vec[7],
            "p_snow_and_ice": auth_p_vec[8],
            # Agregados Anuais Autoritativos (5 colunas)
            "probability_sum_before_normalization_annual": auth_raw_sum,
            "n_valid_months": auth_valid_months,
            "annual_class": auth_class_name,
            "annual_class_index": auth_class_idx,
            "dw_crop": auth_dw_crop,
            # MapBiomas 2025 (2 colunas)
            "mapbiomas_class": mb_class_2025,
            "mapbiomas_crop": mb_crop_2025,
            # Métricas Teórico-Informacionais e Temporais (11 colunas)
            "entropy_annual": h_annual,
            "entropy_temporal_mean": h_temporal_mean,
            "entropy_monthly_mean": h_monthly_mean,
            "jsd_temporal": jsd_temporal,
            "stability": stability,
            "top1_class": top1_class,
            "top1_probability": top1_prob,
            "top2_class": top2_class,
            "top2_probability": top2_prob,
            "top2_margin": top2_margin,
            "competitor_class": competitor,
            # Distâncias de borda truncadas (EPSG:5880, 250m) (3 colunas)
            "distance_edge_mb_m": d_mb,
            "distance_edge_dw_m": d_dw,
            "distance_edge_min_m": d_min,
            # Sensibilidade MapBiomas Estável (2 colunas)
            "mapbiomas_stability_eligible_2017_2025": mb_elig,
            "mapbiomas_stable_2017_2025": mb_stable,
        }
        annual_rows.append(a_row)

    df_monthly = pd.DataFrame(monthly_rows)
    df_annual = pd.DataFrame(annual_rows)
    return df_monthly, df_annual


def main():
    log("=" * 80)
    log("EXTRAÇÃO ANALÍTICA DEFINITIVA DOS 40K PONTOS (CHECKPOINT 3D)")
    log("=" * 80)

    ee.Initialize(project=PROJECT_ID)
    mb_proj = get_mapbiomas_projection()

    df_pts = pd.read_csv(MASTER_POINTS_CSV, keep_default_na=False)
    log(f"Master sample lida: {len(df_pts):,} pontos")
    assert len(df_pts) == 40000

    slices_in_points = sorted(df_pts["slice_id"].unique())
    log(f"Total de fatias ativas com pontos: {len(slices_in_points)}")

    completed_slices = get_completed_slices()
    pending_slices = [s for s in slices_in_points if s not in completed_slices]
    log(f"Fatias já extraídas: {len(completed_slices)} / {len(slices_in_points)}")
    log(f"Fatias pendentes:   {len(pending_slices)}")

    if pending_slices:
        log("Construindo stack canônico anual (27 bandas)...")
        annual_stack = build_canonical_annual_stack()

        log("Construindo stacks trimestrais canônicos (4 trimestres, 36 bandas cada)...")
        source_domain = get_source_support_domain()
        dw_col = (
            ee.ImageCollection(DW_COLLECTION)
            .filterDate(DW_START, DW_END)
            .filterBounds(source_domain)
        )
        with open(DATES_CACHE_PATH, "r", encoding="utf-8") as f:
            dates_dict = json.load(f)

        q_stacks = [
            build_canonical_quarter_stack([1, 2, 3], dw_col, dates_dict),
            build_canonical_quarter_stack([4, 5, 6], dw_col, dates_dict),
            build_canonical_quarter_stack([7, 8, 9], dw_col, dates_dict),
            build_canonical_quarter_stack([10, 11, 12], dw_col, dates_dict),
        ]

        log(f"Iniciando extração concorrente com {MAX_WORKERS} workers...")
        completed_count = len(completed_slices)
        t_start = time.time()

        def worker_fn(s_id: str):
            t0 = time.time()
            sub_df = df_pts[df_pts["slice_id"] == s_id]
            recs = process_slice(s_id, sub_df, annual_stack, q_stacks, mb_proj)
            save_slice_checkpoint(s_id, recs)
            dt = time.time() - t0
            return s_id, len(recs), dt

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(worker_fn, s_id): s_id for s_id in pending_slices}
            for fut in as_completed(futures):
                s_id = futures[fut]
                try:
                    s_id, n_recs, dt = fut.result()
                    completed_count += 1
                    log(f"  [{completed_count:03d}/{len(slices_in_points)}] Concluído {s_id}: {n_recs:4d} pontos ({dt:5.1f}s)")
                except Exception as e:
                    log(f"FALHA na extração da fatia {s_id}: {e}")
                    raise

        log(f"Extração GEE concluída em {time.time() - t_start:.1f}s.")

    # Carregar todos os registros de todas as fatias
    log("\nCarregando e agregando todas as 182 fatias extraídas...")
    all_records = []
    for s_id in slices_in_points:
        recs = load_slice_checkpoint(s_id)
        assert len(recs) > 0, f"Checkpoint da fatia {s_id} vazio ou não encontrado!"
        all_records.extend(recs)

    log(f"Total de registros agregados: {len(all_records):,} / 40.000")
    assert len(all_records) == 40000, f"Esperado 40.000 registros, obtido {len(all_records)}"

    # Calcular métricas em Python
    df_monthly, df_annual = compute_metrics(all_records, df_pts)

    # Verificações de integridade estrita
    assert len(df_monthly) == 480000, f"Esperado 480.000 linhas mensais, obtido {len(df_monthly)}"
    assert len(df_annual) == 40000, f"Esperado 40.000 linhas anuais, obtido {len(df_annual)}"
    assert (df_annual["n_valid_months"] >= 8).all(), "Pontos com n_valid_months < 8 detectados!"
    assert df_annual["entropy_annual"].isna().sum() == 0, "NaNs detectados em entropy_annual!"
    assert df_annual["distance_edge_min_m"].isna().sum() == 0, "NaNs detectados em distâncias!"
    assert df_annual["jsd_temporal"].isna().sum() == 0, "NaNs detectados em jsd_temporal!"
    assert df_annual["stability"].isna().sum() == 0, "NaNs detectados em stability!"

    # Salvar artefatos finais
    log("\nSalvando artefatos processados...")
    df_monthly.to_parquet(DW_MONTHLY_PARQUET, index=False)
    log(f"  Salvo: {DW_MONTHLY_PARQUET} ({len(df_monthly):,} linhas, {len(df_monthly.columns)} colunas)")

    df_annual.to_parquet(SAMPLES_ANNUAL_PARQUET, index=False)
    log(f"  Salvo: {SAMPLES_ANNUAL_PARQUET} ({len(df_annual):,} linhas, {len(df_annual.columns)} colunas)")

    df_annual.to_csv(SAMPLES_ANNUAL_CSV, index=False)
    log(f"  Salvo: {SAMPLES_ANNUAL_CSV} ({len(df_annual):,} linhas, {len(df_annual.columns)} colunas)")

    log("=" * 80)
    log("EXTRAÇÃO ANALÍTICA CONCLUÍDA COM SUCESSO!")
    log("=" * 80)


if __name__ == "__main__":
    main()
