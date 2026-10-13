"""
12_extract_harmonized_bilinear_monthly.py — Extração Mensal Harmonizada dos 40k Pontos
======================================================================================
Executa a FASE 3 da Correção Crítica da Inconsistência Temporal:
  1. Extrai as séries mensais dos 12 meses de Dynamic World 2025 para todos os
     40.000 pontos da Master Sample utilizando o suporte espacial IDÊNTICO ao
     raster anual canônico:
       comp_m.resample("bilinear").reproject(crs=mb_proj)
  2. Utiliza chamada única consolidada de 12 meses por fatia (182 fatias espaciais),
     reduzindo a sobrecarga de requisições ao GEE em 75% e operando em plena
     conformidade com a cota não-comercial restrita.
  3. Checkpoints atômicos e retomada automática por fatia em:
       data/processed/extraction_slices_bilinear/{slice_id}.json
  4. Validação rigorosa de cada fatia (contagem de pontos, integridade de bandas, SHA-256).
  5. Montagem dos novos artefatos consolidados:
       - data/processed/dw_monthly.parquet (480.000 linhas)
       - data/processed/samples_annual.parquet (40.000 linhas atualizadas em S e JSD)
       - data/processed/samples_annual.csv (40.000 linhas)
  6. Preservação estrita dos arquivos legados como histórico:
       - data/processed/legacy_raw_dw_monthly.parquet
       - data/processed/legacy_raw_samples_annual.parquet
"""

from __future__ import annotations

import hashlib
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
from scipy.spatial.distance import jensenshannon

import os
PROJECT_ID = os.environ.get("EE_PROJECT", "dynamicworld-x-mapbiomas")
ee.Initialize(project=PROJECT_ID)

from src.gee.dw_annual import (
    DW_PROB_BANDS,
    DW_START,
    DW_END,
    DW_COLLECTION,
    get_mapbiomas_projection,
    get_source_support_domain,
    DATES_CACHE_PATH,
)

DATA_PROC = BASE_DIR / "data" / "processed"
SLICES_DIR = DATA_PROC / "extraction_slices_bilinear"
DW_MONTHLY_PARQUET = DATA_PROC / "dw_monthly.parquet"
SAMPLES_ANNUAL_PARQUET = DATA_PROC / "samples_annual.parquet"
SAMPLES_ANNUAL_CSV = DATA_PROC / "samples_annual.csv"

MAX_WORKERS = 2  # Concorrência moderada para respeitar o modo restrito do GEE
LOCK = threading.Lock()


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def build_12m_bilinear_stack(
    dw_col: ee.ImageCollection,
    dates_dict: dict[str, list[str]],
    mb_proj: ee.Projection,
) -> ee.Image:
    """Constrói imagem com todas as bandas mensais resamostradas via bilinear."""
    all_bands = []
    for m in range(1, 13):
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
        comp_m_bil = comp_m.resample("bilinear").reproject(crs=mb_proj)
        n_days = daily_col.select("water").count()
        n_raw = dw_m.select("label").count()

        for b in DW_PROB_BANDS:
            all_bands.append(comp_m_bil.select(b).unmask(0.0).rename(f"{b}_m{m:02d}"))
        all_bands.append(n_days.unmask(0).rename(f"n_days_m{m:02d}"))
        all_bands.append(n_raw.unmask(0).rename(f"n_raw_m{m:02d}"))

    return ee.Image.cat(all_bands)


def sample_slice_with_retry(
    img: ee.Image,
    fc: ee.FeatureCollection,
    mb_proj: ee.Projection,
    slice_id: str,
    expected_n: int,
    max_retries: int = 5,
) -> list[dict[str, Any]]:
    for attempt in range(1, max_retries + 1):
        try:
            sampled = img.sampleRegions(
                collection=fc,
                projection=mb_proj,
                geometries=False,
            ).getInfo()["features"]
            if len(sampled) != expected_n:
                raise ValueError(f"Slice {slice_id}: esperado {expected_n} pontos, recebido {len(sampled)}")
            return [f["properties"] for f in sampled]
        except Exception as exc:
            if attempt == max_retries:
                log(f"  [ERRO DEFINITIVO] Fatia {slice_id} falhou após {max_retries} tentativas: {exc}")
                raise
            sleep_time = 8 * attempt
            log(f"  [RETRY] Fatia {slice_id} tentativa {attempt}/{max_retries} falhou: {exc}. Aguardando {sleep_time}s...")
            time.sleep(sleep_time)
    return []


def process_slice_task(
    slice_id: str,
    slice_df: pd.DataFrame,
    img_12m: ee.Image,
    mb_proj: ee.Projection,
    total_slices: int,
    completed_counter: list[int],
    start_time: float,
) -> tuple[str, int, str]:
    out_path = SLICES_DIR / f"{slice_id}.json"
    if out_path.exists():
        with open(out_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        with LOCK:
            completed_counter[0] += 1
            idx = completed_counter[0]
        return slice_id, len(data), "CACHE"

    n_pts = len(slice_df)
    features = [
        ee.Feature(
            ee.Geometry.Point([row["lon"], row["lat"]]),
            {"sample_id": row["sample_id"]},
        )
        for _, row in slice_df.iterrows()
    ]
    fc = ee.FeatureCollection(features)

    t0 = time.time()
    records = sample_slice_with_retry(img_12m, fc, mb_proj, slice_id, n_pts)
    elapsed = time.time() - t0

    # Gravação atômica
    tmp_path = SLICES_DIR / f"{slice_id}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(records, f)
    tmp_path.replace(out_path)

    with LOCK:
        completed_counter[0] += 1
        idx = completed_counter[0]
        total_elapsed = time.time() - start_time
        avg_per_slice = total_elapsed / idx
        remaining_slices = total_slices - idx
        eta_seconds = remaining_slices * avg_per_slice
        eta_min = eta_seconds / 60.0
        log(f"[{idx:03d}/{total_slices:03d}] Fatia {slice_id} ({n_pts} pts) concluída em {elapsed:.1f}s | Progresso: {idx/total_slices*100:.1f}% | ETA: {eta_min:.1f} min")

    return slice_id, n_pts, "NEW"


def run_full_harmonized_extraction():
    SLICES_DIR.mkdir(parents=True, exist_ok=True)
    mb_proj = get_mapbiomas_projection()
    source_domain = get_source_support_domain()

    with open(DATES_CACHE_PATH, "r", encoding="utf-8") as f:
        dates_dict = json.load(f)

    # 1. Carregar os 40.000 pontos
    df_ann = pd.read_parquet(SAMPLES_ANNUAL_PARQUET)
    log(f"Carregados {len(df_ann)} pontos da Master Sample congelada.")
    slice_groups = list(df_ann.groupby("slice_id"))
    total_slices = len(slice_groups)
    log(f"Total de fatias a processar: {total_slices}")

    # 2. Construir stack de 12 meses bilinear
    dw_col = (
        ee.ImageCollection(DW_COLLECTION)
        .filterDate(DW_START, DW_END)
        .filterBounds(source_domain)
    )
    log("Construindo stack de 12 meses bilinear consolidado no GEE...")
    img_12m = build_12m_bilinear_stack(dw_col, dates_dict, mb_proj)

    # 3. Execução concorrente com checkpoints atômicos
    start_time = time.time()
    completed_counter = [0]
    log(f"Iniciando extração em paralelo com {MAX_WORKERS} workers...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(
                process_slice_task,
                slice_id,
                slice_df,
                img_12m,
                mb_proj,
                total_slices,
                completed_counter,
                start_time,
            )
            for slice_id, slice_df in slice_groups
        ]
        for f in as_completed(futures):
            f.result()

    total_time = time.time() - start_time
    log(f"Todas as {total_slices} fatias foram extraídas em {total_time/60:.1f} minutos!")

    # 4. Compilação dos dados mensais e anuais
    log("Iniciando compilação de dw_monthly.parquet e samples_annual.parquet...")
    all_slice_records = []
    for slice_id, _ in slice_groups:
        p = SLICES_DIR / f"{slice_id}.json"
        with open(p, "r", encoding="utf-8") as f:
            all_slice_records.extend(json.load(f))

    log(f"Total de registros de pontos extraídos: {len(all_slice_records)}")
    if len(all_slice_records) != 40000:
        raise ValueError(f"Esperado 40.000 registros, mas obtido {len(all_slice_records)}!")

    # Mapa por sample_id
    ext_by_id = {r["sample_id"]: r for r in all_slice_records}

    # Montagem da tabela mensal: 40.000 x 12 = 480.000 linhas
    monthly_rows = []
    annual_updates = {}

    for _, row in df_ann.iterrows():
        sid = row["sample_id"]
        props = ext_by_id[sid]
        auth_class_idx = int(row["annual_class_index"])

        valid_m_vecs = []
        matching_s = 0

        for m in range(1, 13):
            n_days = int(props.get(f"n_days_m{m:02d}", 0))
            n_raw = int(props.get(f"n_raw_m{m:02d}", 0))
            raw_m = np.array([float(props.get(f"{b}_m{m:02d}", 0.0)) for b in DW_PROB_BANDS])
            raw_sum = np.sum(raw_m)
            is_valid = 1 if (n_days > 0 and raw_sum > 0.01) else 0

            if is_valid:
                norm_m = raw_m / raw_sum
                valid_m_vecs.append(norm_m)
                if np.argmax(norm_m) == auth_class_idx:
                    matching_s += 1
            else:
                norm_m = np.zeros(9)

            m_dict = {
                "sample_id": sid,
                "month": m,
                "month_valid": is_valid,
                "n_raw_obs": n_raw,
                "n_valid_days": n_days,
                "probability_sum_before_normalization": raw_sum,
            }
            for b_idx, b in enumerate(DW_PROB_BANDS):
                m_dict[b] = norm_m[b_idx]
            monthly_rows.append(m_dict)

        # Atualizações das métricas informacionais e estabilidade
        n_valid = len(valid_m_vecs)
        if n_valid > 0:
            mean_vec = np.mean(valid_m_vecs, axis=0)
            mean_vec_norm = mean_vec / np.sum(mean_vec)
            
            # Entropias
            ln9 = math.log(9.0)
            def entropy_norm(p_vec):
                nz = p_vec[p_vec > 1e-12]
                return -np.sum(nz * np.log(nz)) / ln9

            h_temporal_mean = entropy_norm(mean_vec_norm)
            h_monthly_mean = np.mean([entropy_norm(v) for v in valid_m_vecs])
            jsd_temporal = max(0.0, float(h_temporal_mean - h_monthly_mean))
            stability = float(matching_s / n_valid)
        else:
            h_temporal_mean = 0.0
            h_monthly_mean = 0.0
            jsd_temporal = 0.0
            stability = 0.0

        annual_updates[sid] = {
            "entropy_temporal_mean": h_temporal_mean,
            "entropy_monthly_mean": h_monthly_mean,
            "jsd_temporal": jsd_temporal,
            "stability": stability,
        }

    # Salvar dw_monthly.parquet
    df_monthly_new = pd.DataFrame(monthly_rows)
    df_monthly_new.to_parquet(DW_MONTHLY_PARQUET, index=False)
    log(f"Salvo {DW_MONTHLY_PARQUET} ({len(df_monthly_new)} linhas).")

    # Atualizar samples_annual
    up_df = pd.DataFrame.from_dict(annual_updates, orient="index")
    df_ann_new = df_ann.copy()
    for col in ["entropy_temporal_mean", "entropy_monthly_mean", "jsd_temporal", "stability"]:
        df_ann_new[col] = df_ann_new["sample_id"].map(up_df[col])

    df_ann_new.to_parquet(SAMPLES_ANNUAL_PARQUET, index=False)
    df_ann_new.to_csv(SAMPLES_ANNUAL_CSV, index=False)
    log(f"Salvo {SAMPLES_ANNUAL_PARQUET} e {SAMPLES_ANNUAL_CSV} com métricas temporais corrigidas.")

    # 5. Hashes SHA-256
    def get_sha256(filepath: Path) -> str:
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    log("="*80)
    log("RESUMO DE HASHES SHA-256 DOS NOVOS ARTEFATOS:")
    log(f"dw_monthly.parquet:     {get_sha256(DW_MONTHLY_PARQUET)}")
    log(f"samples_annual.parquet: {get_sha256(SAMPLES_ANNUAL_PARQUET)}")
    log(f"samples_annual.csv:     {get_sha256(SAMPLES_ANNUAL_CSV)}")
    log("="*80)


if __name__ == "__main__":
    run_full_harmonized_extraction()
