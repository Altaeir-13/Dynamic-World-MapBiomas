"""
submit_canonical_batch_exports.py — Submete 10 batches de exportação do censo canônico 10m
========================================================================================
Atende integralmente às seções 1–5 da instrução:
  1. Carrega o manifesto tables/canonical_w2w_batch_manifest.csv (182 slices balanceadas em 10 lotes).
  2. Constrói o RASTER CANÔNICO FIXO UMA VEZ no domínio de suporte MATOPIBA + 5.000 m.
  3. Prepara as 42 bandas canônicas (16 bandas centrais + 26 bandas de meses m_0..m_12).
  4. Para cada batch_id (canonical_w2w_batch_00..canonical_w2w_batch_09):
     - Seleciona as geometrias das slices pertencentes ao lote;
     - Executa reduceRegions sobre a grade congelada MapBiomas 10m (crs, crsTransform, tileScale=16);
     - Dispara ee.batch.Export.table.toDrive com prefixo '{batch_id}_10m';
     - Registra os metadados da tarefa em tables/canonical_w2w_batch_tasks.csv.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from shapely.geometry import box, shape

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

import ee
from src.gee.dw_annual import (
    PROJECT_ID,
    get_harmonized_crosswalk_layers,
    get_mapbiomas_projection,
    get_source_support_domain,
)

DATA_REF = BASE_DIR / "data" / "reference"
TABLES_DIR = BASE_DIR / "tables"
MANIFEST_CSV = TABLES_DIR / "canonical_w2w_batch_manifest.csv"
TASKS_CSV = TABLES_DIR / "canonical_w2w_batch_tasks.csv"

FOLDER_NAME = "matopiba_exports"


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def build_slice_geometries() -> dict[str, dict]:
    """Reconstrói o dicionário {slice_id: {'state': st, 'ee_geom': ee.Geometry}}."""
    with open(DATA_REF / "matopiba_states.geojson", "r", encoding="utf-8") as f:
        states_data = json.load(f)

    step = 0.75
    geoms = {}

    for feat in states_data["features"]:
        st = feat["properties"].get("state") or feat["properties"].get("sigla") or feat["properties"].get("name")
        shp = shape(feat["geometry"])
        min_x, min_y, max_x, max_y = shp.bounds
        nx = int((max_x - min_x) / step) + 1
        ny = int((max_y - min_y) / step) + 1
        dx = (max_x - min_x) / nx
        dy = (max_y - min_y) / ny
        for ix in range(nx):
            for iy in range(ny):
                b = box(min_x + ix * dx, min_y + iy * dy, min_x + (ix + 1) * dx, min_y + (iy + 1) * dy)
                sub = shp.intersection(b)
                if not sub.is_empty and sub.area > 1e-6:
                    s_id = f"{st}_x{ix:02d}_y{iy:02d}"
                    geoms[s_id] = {
                        "state": st,
                        "ee_geom": ee.Geometry(sub.__geo_interface__),
                    }
    return geoms


def main():
    log("=" * 80)
    log("SUBMISSÃO DOS 10 BATCHES CANÔNICOS DE EXPORTAÇÃO WALL-TO-WALL 10M")
    log("=" * 80)

    ee.Initialize(project=PROJECT_ID)
    mb_proj = get_mapbiomas_projection()
    proj_info = mb_proj.getInfo()
    crs = proj_info["crs"]
    transform = proj_info["transform"]
    log(f"Grade MapBiomas 10m: CRS={crs}, transform={transform}")

    # 1. Carregar manifesto
    assert MANIFEST_CSV.exists(), f"Manifesto não encontrado: {MANIFEST_CSV}"
    df_manifest = pd.read_csv(MANIFEST_CSV)
    log(f"Manifesto carregado: {len(df_manifest)} slices distribuídas em {df_manifest['batch_id'].nunique()} lotes.")

    # 2. Construir geometrias das slices
    log("Carregando geometrias vetoriais das slices...")
    slice_geoms = build_slice_geometries()

    # 3. Construir RASTER CANÔNICO FIXO (Section 3)
    log("Construindo RASTER CANÔNICO FIXO no domínio de suporte MATOPIBA + 5.000 m...")
    support_domain = get_source_support_domain()
    layers = get_harmonized_crosswalk_layers(source_region=support_domain, mb_proj=mb_proj)

    pixel_area_ha = ee.Image.pixelArea().divide(10000.0)
    mb = layers["mb"]
    valid_mb_mask = layers["valid_mb_mask"]
    n_valid_months = layers["dw_dict"]["n_valid_months"]

    bands = [
        # 1. Áreas em hectares (ellipsoidal exact)
        pixel_area_ha.updateMask(mb.mask()).rename("total_covered_ha"),
        pixel_area_ha.updateMask(layers["eligible_mask"]).rename("eligible_ha"),
        pixel_area_ha.updateMask(layers["is_excluded"].updateMask(mb.mask())).rename("excluded_mb_ha"),
        pixel_area_ha.updateMask(layers["insufficient_dw_temporal"]).rename("insufficient_dw_temporal_ha"),
        pixel_area_ha.updateMask(layers["regime_AA"]).rename("AA_ha"),
        pixel_area_ha.updateMask(layers["regime_AN"]).rename("AN_ha"),
        pixel_area_ha.updateMask(layers["regime_NA"]).rename("NA_ha"),
        pixel_area_ha.updateMask(layers["regime_NN"]).rename("NN_ha"),

        # 2. Contagens de pixels exatas (unweighted count)
        ee.Image(1).updateMask(mb.mask()).rename("total_covered_count"),
        ee.Image(1).updateMask(layers["eligible_mask"]).rename("eligible_count"),
        ee.Image(1).updateMask(layers["is_excluded"].updateMask(mb.mask())).rename("excluded_mb_count"),
        ee.Image(1).updateMask(layers["insufficient_dw_temporal"]).rename("insufficient_dw_temporal_count"),
        ee.Image(1).updateMask(layers["regime_AA"]).rename("AA_count"),
        ee.Image(1).updateMask(layers["regime_AN"]).rename("AN_count"),
        ee.Image(1).updateMask(layers["regime_NA"]).rename("NA_count"),
        ee.Image(1).updateMask(layers["regime_NN"]).rename("NN_count"),
    ]

    # 3. Bandas mensais m_0..m_12 (área e contagem)
    for m in range(13):
        m_mask = valid_mb_mask.And(n_valid_months.eq(m))
        bands.append(pixel_area_ha.updateMask(m_mask).rename(f"m_{m}_ha"))
        bands.append(ee.Image(1).updateMask(m_mask).rename(f"m_{m}_count"))

    canonical_stack = ee.Image.cat(bands)
    log(f"Stack canônico montado com sucesso ({len(bands)} bandas).")

    import argparse
    parser = argparse.ArgumentParser(description="Submeter batches W2W")
    parser.add_argument("--batch-ids", nargs="+", help="Lista de batch_ids específicos a submeter")
    args = parser.parse_args()

    # 4. Iterar sobre cada batch e submeter
    if args.batch_ids:
        batch_ids = [b for b in args.batch_ids if b in df_manifest["batch_id"].values]
        log(f"Submetendo apenas os batches solicitados: {batch_ids}")
    else:
        batch_ids = sorted(df_manifest["batch_id"].unique())

    task_records = []
    for b_id in batch_ids:
        sub_manifest = df_manifest[df_manifest["batch_id"] == b_id]
        log(f"\n--- Preparando {b_id} ({len(sub_manifest)} slices) ---")

        features = []
        for _, row in sub_manifest.iterrows():
            s_id = row["slice_id"]
            st = row["state"]
            assert s_id in slice_geoms, f"Slice {s_id} não encontrada nas geometrias!"
            features.append(
                ee.Feature(
                    slice_geoms[s_id]["ee_geom"],
                    {
                        "slice_id": s_id,
                        "state": st,
                        "batch_id": b_id,
                    }
                )
            )

        fc_batch = ee.FeatureCollection(features)

        # Redução unweighted na grade exata MapBiomas 10m
        reduced_batch = canonical_stack.reduceRegions(
            collection=fc_batch,
            reducer=ee.Reducer.sum().unweighted(),
            crs=crs,
            crsTransform=transform,
            tileScale=16,
        )

        task_desc = f"{b_id}_10m"
        file_prefix = f"{b_id}_10m"

        task = ee.batch.Export.table.toDrive(
            collection=reduced_batch,
            description=task_desc,
            fileNamePrefix=file_prefix,
            folder=FOLDER_NAME,
            fileFormat="CSV",
        )
        task.start()
        t_id = task.id
        status = task.status()
        log(f"Tarefa submetida: {b_id} -> Task ID: {t_id} (State: {status.get('state')})")

        task_records.append({
            "batch_id": b_id,
            "task_id": t_id,
            "description": task_desc,
            "state": status.get("state"),
            "downloaded": False,
            "create_time": status.get("creation_timestamp_ms"),
            "start_time": status.get("start_timestamp_ms"),
            "update_time": status.get("update_timestamp_ms"),
            "error_message": status.get("error_message"),
        })

        time.sleep(1.0)

    # 5. Salvar/Atualizar registro de tarefas em tables/canonical_w2w_batch_tasks.csv
    df_new = pd.DataFrame(task_records)
    if TASKS_CSV.exists():
        df_old = pd.read_csv(TASKS_CSV)
        new_batch_ids = set(df_new["batch_id"])
        # Se sub-batches (ex: 00a, 04a) foram submetidos, remover a tarefa base anterior
        for nb in list(new_batch_ids):
            if nb.endswith("a") or nb.endswith("b"):
                base_batch = nb[:-1]
                new_batch_ids.add(base_batch)
            elif any(nb.endswith(sfx) for sfx in ("a1", "a2", "b1", "b2")):
                base_batch = nb[:-1]
                new_batch_ids.add(base_batch)
        df_kept = df_old[~df_old["batch_id"].isin(new_batch_ids)]
        df_tasks = pd.concat([df_new, df_kept], ignore_index=True).sort_values("batch_id").reset_index(drop=True)
    else:
        df_tasks = df_new

    df_tasks.to_csv(TASKS_CSV, index=False)
    log(f"\nRegistro de tarefas atualizado em: {TASKS_CSV}")
    print(df_tasks[["batch_id", "task_id", "description", "state"]])


if __name__ == "__main__":
    main()
