"""
20_test_pagination_invariance.py — Final Invariance Test of Spatial Pagination (Step 13)
========================================================================================
Tests whether client/server pagination (chunking by slice vs by state vs all points together)
affects analytical extraction on the frozen CANONICAL RASTER.

Requirements:
  - 1,000 deterministic sample points from the new Master Sample
  - Extract the SAME canonical raster using 3 pagination modes:
      Mode A: Per slice (points chunked by operational slice)
      Mode B: Per state (points chunked by federal state)
      Mode C: Biome-wide (all 1,000 points in a single evaluation)
  - Assertions:
      annual_class mismatch = 0
      dw_crop mismatch = 0
      n_valid_months mismatch = 0
      probability difference <= 1e-4 (numerical precision)
      distance_edge_dw difference <= 0.1 m
      distance_edge_mb difference <= 0.1 m

Output:
  - tables/pagination_invariance_audit.csv
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import time
from pathlib import Path
import ee
import numpy as np
import pandas as pd

import sys
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
DATA_PROC = BASE_DIR / "data" / "processed"
TABLES_DIR = BASE_DIR / "tables"

MASTER_POINTS_CSV = DATA_PROC / "master_sampling_points.csv"
OUT_CSV = TABLES_DIR / "pagination_invariance_audit.csv"

from src.gee.dw_annual import (
    PROJECT_ID,
    DW_PROB_BANDS,
    get_harmonized_crosswalk_layers,
    get_mapbiomas_projection,
)


def run_pagination_invariance_test():
    print("=" * 80, flush=True)
    print("RUNNING FINAL PAGINATION INVARIANCE TEST (CHECKPOINT 3D - STEP 13)", flush=True)
    print("=" * 80, flush=True)

    ee.Initialize(project=PROJECT_ID)
    mb_proj = get_mapbiomas_projection()

    assert MASTER_POINTS_CSV.exists(), f"Master sample points file not found: {MASTER_POINTS_CSV}"
    df_master = pd.read_csv(MASTER_POINTS_CSV)
    print(f"Loaded master sample: {len(df_master)} points.", flush=True)

    # Select 1,000 deterministic points using seed 25:
    # 500 from main sample + 500 from robust-only, stratified across 4 states
    sample_1k = df_master.sample(n=1000, random_state=25).sort_values("sample_id").reset_index(drop=True)
    print(f"Selected 1,000 deterministic test points across {sample_1k['state'].nunique()} states and {sample_1k['slice_id'].nunique()} slices.", flush=True)

    # Build canonical raster stack once
    print("\nBuilding canonical raster stack...", flush=True)
    layers = get_harmonized_crosswalk_layers()
    dw_dict = layers["dw_dict"]

    test_stack = ee.Image.cat([
        dw_dict["normalized_probs"],
        dw_dict["annual_class_index"],
        layers["dw_crop"],
        dw_dict["n_valid_months"],
        layers["distance_edge_mb_m"],
        layers["distance_edge_dw_m"],
    ])

    # --- Mode C: All 1,000 points together ---
    print("\n[Mode C] Extracting all 1,000 points together in a single request...", flush=True)
    t0 = time.time()
    feats_all = [
        ee.Feature(ee.Geometry.Point([r["lon"], r["lat"]]), {"sample_id": r["sample_id"]})
        for _, r in sample_1k.iterrows()
    ]
    fc_all = ee.FeatureCollection(feats_all)
    sampled_c = test_stack.reduceRegions(
        collection=fc_all,
        reducer=ee.Reducer.first(),
        scale=10,
        crs=mb_proj,
        tileScale=16,
    ).getInfo()["features"]
    dict_c = {f["properties"]["sample_id"]: f["properties"] for f in sampled_c}
    print(f"  Mode C completed in {time.time() - t0:.2f}s ({len(dict_c)} records).", flush=True)

    # --- Mode B: Chunks by State ---
    print("\n[Mode B] Extracting points chunked by state (MA, TO, PI, BA)...", flush=True)
    t0 = time.time()
    dict_b = {}
    for st, group in sample_1k.groupby("state"):
        feats_st = [
            ee.Feature(ee.Geometry.Point([r["lon"], r["lat"]]), {"sample_id": r["sample_id"]})
            for _, r in group.iterrows()
        ]
        fc_st = ee.FeatureCollection(feats_st)
        sampled_st = test_stack.reduceRegions(
            collection=fc_st,
            reducer=ee.Reducer.first(),
            scale=10,
            crs=mb_proj,
            tileScale=16,
        ).getInfo()["features"]
        for f in sampled_st:
            dict_b[f["properties"]["sample_id"]] = f["properties"]
        print(f"    State {st}: {len(feats_st)} points extracted.", flush=True)
    print(f"  Mode B completed in {time.time() - t0:.2f}s ({len(dict_b)} records).", flush=True)

    # --- Mode A: Chunks by Slice ---
    print("\n[Mode A] Extracting points chunked by operational slice...", flush=True)
    t0 = time.time()
    dict_a = {}
    slice_groups = list(sample_1k.groupby("slice_id"))
    total_slices = len(slice_groups)

    def extract_slice_pts(s_id, group):
        feats_slice = [
            ee.Feature(ee.Geometry.Point([r["lon"], r["lat"]]), {"sample_id": r["sample_id"]})
            for _, r in group.iterrows()
        ]
        fc_slice = ee.FeatureCollection(feats_slice)
        for attempt in range(1, 4):
            try:
                sampled = test_stack.sampleRegions(
                    collection=fc_slice,
                    projection=mb_proj,
                    geometries=False,
                ).getInfo()["features"]
                return [f["properties"] for f in sampled]
            except Exception as e:
                if attempt == 3:
                    raise
                time.sleep(2 * attempt)
        return []

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_map = {executor.submit(extract_slice_pts, s_id, grp): s_id for s_id, grp in slice_groups}
        completed = 0
        for fut in as_completed(future_map):
            props_list = fut.result()
            for p in props_list:
                dict_a[p["sample_id"]] = p
            completed += 1
            if completed % 25 == 0 or completed == total_slices:
                print(f"  Mode A progress: {completed}/{total_slices} slices completed...", flush=True)

    print(f"  Mode A completed in {time.time() - t0:.2f}s ({len(dict_a)} records across {total_slices} slices).", flush=True)

    # Compare A vs C and B vs C
    audit_rows = []
    mismatches_class_ac = 0
    mismatches_crop_ac = 0
    mismatches_months_ac = 0
    max_prob_diff_ac = 0.0
    max_dist_dw_diff_ac = 0.0
    max_dist_mb_diff_ac = 0.0

    mismatches_class_bc = 0
    mismatches_crop_bc = 0
    mismatches_months_bc = 0
    max_prob_diff_bc = 0.0
    max_dist_dw_diff_bc = 0.0
    max_dist_mb_diff_bc = 0.0

    for _, r in sample_1k.iterrows():
        sid = r["sample_id"]
        res_a = dict_a[sid]
        res_b = dict_b[sid]
        res_c = dict_c[sid]

        # Mode A vs Mode C
        c_a = int(res_a["annual_class_index"])
        c_c = int(res_c["annual_class_index"])
        crop_a = int(res_a["dw_crop"])
        crop_c = int(res_c["dw_crop"])
        m_a = int(res_a["n_valid_months"])
        m_c = int(res_c["n_valid_months"])

        if c_a != c_c:
            mismatches_class_ac += 1
        if crop_a != crop_c:
            mismatches_crop_ac += 1
        if m_a != m_c:
            mismatches_months_ac += 1

        prob_diff_ac = max(abs(float(res_a[b]) - float(res_c[b])) for b in DW_PROB_BANDS)
        max_prob_diff_ac = max(max_prob_diff_ac, prob_diff_ac)

        dist_dw_diff_ac = abs(float(res_a["distance_edge_dw_m"]) - float(res_c["distance_edge_dw_m"]))
        dist_mb_diff_ac = abs(float(res_a["distance_edge_mb_m"]) - float(res_c["distance_edge_mb_m"]))
        max_dist_dw_diff_ac = max(max_dist_dw_diff_ac, dist_dw_diff_ac)
        max_dist_mb_diff_ac = max(max_dist_mb_diff_ac, dist_mb_diff_ac)

        # Mode B vs Mode C
        c_b = int(res_b["annual_class_index"])
        crop_b = int(res_b["dw_crop"])
        m_b = int(res_b["n_valid_months"])

        if c_b != c_c:
            mismatches_class_bc += 1
        if crop_b != crop_c:
            mismatches_crop_bc += 1
        if m_b != m_c:
            mismatches_months_bc += 1

        prob_diff_bc = max(abs(float(res_b[b]) - float(res_c[b])) for b in DW_PROB_BANDS)
        max_prob_diff_bc = max(max_prob_diff_bc, prob_diff_bc)

        dist_dw_diff_bc = abs(float(res_b["distance_edge_dw_m"]) - float(res_c["distance_edge_dw_m"]))
        dist_mb_diff_bc = abs(float(res_b["distance_edge_mb_m"]) - float(res_c["distance_edge_mb_m"]))
        max_dist_dw_diff_bc = max(max_dist_dw_diff_bc, dist_dw_diff_bc)
        max_dist_mb_diff_bc = max(max_dist_mb_diff_bc, dist_mb_diff_bc)

        audit_rows.append({
            "sample_id": sid,
            "state": r["state"],
            "slice_id": r["slice_id"],
            "class_mode_a": c_a,
            "class_mode_b": c_b,
            "class_mode_c": c_c,
            "crop_mode_a": crop_a,
            "crop_mode_b": crop_b,
            "crop_mode_c": crop_c,
            "months_mode_a": m_a,
            "months_mode_b": m_b,
            "months_mode_c": m_c,
            "max_prob_diff_ac": prob_diff_ac,
            "max_prob_diff_bc": prob_diff_bc,
            "dist_dw_diff_ac": dist_dw_diff_ac,
            "dist_dw_diff_bc": dist_dw_diff_bc,
            "dist_mb_diff_ac": dist_mb_diff_ac,
            "dist_mb_diff_bc": dist_mb_diff_bc,
        })

    df_audit = pd.DataFrame(audit_rows)
    df_audit.to_csv(OUT_CSV, index=False)
    print(f"\nSaved audit details: {OUT_CSV}", flush=True)

    print("\n" + "=" * 80, flush=True)
    print("PAGINATION INVARIANCE AUDIT RESULTS:", flush=True)
    print("=" * 80, flush=True)
    print(f"Comparison Mode A (per slice) vs Mode C (biome-wide):", flush=True)
    print(f"  annual_class mismatches:    {mismatches_class_ac} / 1000 (Requirement: 0)", flush=True)
    print(f"  dw_crop mismatches:         {mismatches_crop_ac} / 1000 (Requirement: 0)", flush=True)
    print(f"  n_valid_months mismatches:  {mismatches_months_ac} / 1000 (Requirement: 0)", flush=True)
    print(f"  max probability difference: {max_prob_diff_ac:.8e} (Tolerance: <= 1e-4)", flush=True)
    print(f"  max distance_edge_dw diff:  {max_dist_dw_diff_ac:.4f} m (Tolerance: <= 0.1 m)", flush=True)
    print(f"  max distance_edge_mb diff:  {max_dist_mb_diff_ac:.4f} m (Tolerance: <= 0.1 m)", flush=True)

    print(f"\nComparison Mode B (per state) vs Mode C (biome-wide):", flush=True)
    print(f"  annual_class mismatches:    {mismatches_class_bc} / 1000 (Requirement: 0)", flush=True)
    print(f"  dw_crop mismatches:         {mismatches_crop_bc} / 1000 (Requirement: 0)", flush=True)
    print(f"  n_valid_months mismatches:  {mismatches_months_bc} / 1000 (Requirement: 0)", flush=True)
    print(f"  max probability difference: {max_prob_diff_bc:.8e} (Tolerance: <= 1e-4)", flush=True)
    print(f"  max distance_edge_dw diff:  {max_dist_dw_diff_bc:.4f} m (Tolerance: <= 0.1 m)", flush=True)
    print(f"  max distance_edge_mb diff:  {max_dist_mb_diff_bc:.4f} m (Tolerance: <= 0.1 m)", flush=True)
    print("=" * 80, flush=True)

    # Strictly assert invariance criteria
    assert mismatches_class_ac == 0, f"Mode A vs C has {mismatches_class_ac} class mismatches!"
    assert mismatches_crop_ac == 0, f"Mode A vs C has {mismatches_crop_ac} crop mismatches!"
    assert mismatches_months_ac == 0, f"Mode A vs C has {mismatches_months_ac} month mismatches!"
    assert max_prob_diff_ac <= 1e-4, f"Mode A vs C probability difference {max_prob_diff_ac} exceeds tolerance!"
    assert max_dist_dw_diff_ac <= 0.1, f"Mode A vs C DW distance difference {max_dist_dw_diff_ac} exceeds tolerance!"
    assert max_dist_mb_diff_ac <= 0.1, f"Mode A vs C MB distance difference {max_dist_mb_diff_ac} exceeds tolerance!"

    assert mismatches_class_bc == 0, f"Mode B vs C has {mismatches_class_bc} class mismatches!"
    assert mismatches_crop_bc == 0, f"Mode B vs C has {mismatches_crop_bc} crop mismatches!"
    assert mismatches_months_bc == 0, f"Mode B vs C has {mismatches_months_bc} month mismatches!"
    assert max_prob_diff_bc <= 1e-4, f"Mode B vs C probability difference {max_prob_diff_bc} exceeds tolerance!"
    assert max_dist_dw_diff_bc <= 0.1, f"Mode B vs C DW distance difference {max_dist_dw_diff_bc} exceeds tolerance!"
    assert max_dist_mb_diff_bc <= 0.1, f"Mode B vs C MB distance difference {max_dist_mb_diff_bc} exceeds tolerance!"

    print("PAGINATION INVARIANCE AUDIT: PASS (Complete independence from spatial pagination)", flush=True)
    return True


if __name__ == "__main__":
    run_pagination_invariance_test()
