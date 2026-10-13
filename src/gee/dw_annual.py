"""
Dynamic World x MapBiomas — Authoritative Annual Dynamic World 2025 Module
========================================================================
Single authoritative implementation for Dynamic World annual 2025 aggregation
and harmonized MapBiomas crosswalk.

All subsequent scripts (wall-to-wall, sampling, extraction, auditing) MUST
import and reuse this module.

Core Scientific Design (Checkpoint 3D Canonical Architecture):
  1. Fixed Source Support Domain:
     - SOURCE_SUPPORT_DOMAIN = MATOPIBA + 5,000 m buffer
     - ImageCollection filtering, temporal compositing, resampling, and edge
       detection are evaluated ONCE on this canonical support domain.
     - Operational geometries (slices, state boundaries) are STRICTLY prohibited
       as scientific source filtering bounds. Slices serve COMPUTATIONAL PURPOSES
       ONLY (reduceRegion, sample, pagination, memory control).
  2. Temporal Aggregation:
     - Filter date: [2025-01-01, 2026-01-01)
     - Distinct date: neutral mean of images on same day
     - Distinct month: mean of valid days of that month
     - Month valid indicator: unmasked observation count > 0
     - Annual vector: equal-weighted mean ONLY among valid months
  3. Resampling & Normalization:
     - Continuous 9 probabilities aligned to grid10 (MapBiomas 10m) using bilinear resampling
     - Probability sum before normalization preserved
     - Normalization: p'_k = p_k / sum(p)
     - Annual class: argmax of 9 normalized probabilities (crops is index 4)
  4. Harmonized Crosswalk & Regimes:
     - MapBiomas 2025: Crop = [19, 36], Excluded = [18, 21], Noncrop = all other valid
     - Temporal eligibility: n_valid_months >= 8
     - Regimes on eligible domain: AA (1), AN (2), NA (3), NN (4)
  5. Canonical Edge Distances:
     - distance_edge_mb_m: crop vs noncrop in fixed support domain (EPSG:5880, 250m clamp)
     - distance_edge_dw_m: annual_class crop vs noncrop in fixed support domain (EPSG:5880, 250m clamp)
     - distance_edge_min_m = min(distance_edge_mb_m, distance_edge_dw_m)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import ee

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS & CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
import os
PROJECT_ID = os.environ.get("EE_PROJECT", "dynamicworld-x-mapbiomas")
DW_COLLECTION = "GOOGLE/DYNAMICWORLD/V1"
MB_ASSET = "projects/mapbiomas-public/assets/brazil/lulc_10m/collection4/mapbiomas_10m_collection4_coverage_v1"
MB_BAND = "classification_2025"
DW_START = "2025-01-01"
DW_END = "2026-01-01"

DW_PROB_BANDS = [
    "water", "trees", "grass", "flooded_vegetation", "crops",
    "shrub_and_scrub", "built", "bare", "snow_and_ice"
]

CROP_CODES = [19, 36]           # Lavoura Temporária + Perene
CROP_STRICT_CODES = [19]        # Sensibilidade: apenas Temporária
EXCLUDED_CODES = [21, 18]       # Mosaico de Usos + Agricultura se aparecer como pixel
MIN_VALID_MONTHS = 8            # Regra principal de elegibilidade temporal

SUPPORT_GEOJSON_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "reference" / "matopiba_support_5km.geojson"
DATES_CACHE_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "reference" / "dw_2025_monthly_dates.json"

_CACHED_SUPPORT_GEOM: Optional[ee.Geometry] = None


def get_source_support_domain() -> ee.Geometry:
    """
    Returns the frozen canonical source support domain geometry:
    MATOPIBA + 5,000 m buffer.
    """
    global _CACHED_SUPPORT_GEOM
    if _CACHED_SUPPORT_GEOM is None:
        with open(SUPPORT_GEOJSON_PATH, "r", encoding="utf-8") as f:
            d = json.load(f)
        _CACHED_SUPPORT_GEOM = ee.Geometry(d["features"][0]["geometry"])
    return _CACHED_SUPPORT_GEOM


def get_mapbiomas_projection() -> ee.Projection:
    """Returns the official 10m projection of MapBiomas classification_2025."""
    mb = ee.Image(MB_ASSET).select(MB_BAND)
    return mb.projection()


def build_dw_annual_2025(
    source_region: Optional[ee.Geometry] = None,
    mb_proj: Optional[ee.Projection] = None,
) -> dict[str, ee.Image]:
    """
    Builds the authoritative annual Dynamic World 2025 products.

    Parameters
    ----------
    source_region : ee.Geometry, optional
        Fixed computational support region to filter Dynamic World scenes.
        Defaults strictly to get_source_support_domain() (MATOPIBA + 5,000m).
        Variable operational geometries (slices) are PROHIBITED.
    mb_proj : ee.Projection, optional
        MapBiomas 10m reference projection. If None, loaded from MB_ASSET.

    Returns
    -------
    dict with:
        'annual_10m_raw': 9 continuous probability bands on grid10 before normalization
        'raw_prob_sum': sum of 9 probabilities before normalization
        'normalized_probs': 9 continuous probability bands normalized to sum to 1.0
        'annual_class_index': integer band 0..8 corresponding to argmax of DW_PROB_BANDS
        'dw_crop': binary image (1 if argmax == crops, 0 otherwise)
        'n_valid_months': integer band (0..12) counting months with valid unmasked data
        'temporal_eligible': binary mask (1 if n_valid_months >= 8, 0 otherwise)
        'count_stack': 12 bands ('n_obs_m01'..'n_obs_m12') with observation counts
        'dw_annual_stack': single image containing all above bands
    """
    if source_region is None:
        source_region = get_source_support_domain()

    if mb_proj is None:
        mb_proj = get_mapbiomas_projection()

    dw_col = (
        ee.ImageCollection(DW_COLLECTION)
        .filterDate(DW_START, DW_END)
        .filterBounds(source_region)
    )

    m_comps = []
    count_bands = []
    month_valid_masks = []

    empty_template = (
        ee.ImageCollection(DW_COLLECTION)
        .filterDate(DW_START, DW_END)
        .first()
        .select(DW_PROB_BANDS)
        .toFloat()
        .multiply(0)
        .updateMask(ee.Image(0))
    )

    for m in range(1, 13):
        start = f"2025-{m:02d}-01"
        end = f"2025-{m+1:02d}-01" if m < 12 else "2026-01-01"
        dw_m = dw_col.filterDate(start, end)

        # Unmasked observation count per pixel in month m
        n_obs_m = dw_m.select("label").count().rename(f"n_obs_m{m:02d}")
        count_bands.append(n_obs_m)

        # Month is valid at a pixel if at least 1 observation exists
        m_valid = n_obs_m.gt(0).rename(f"m_valid_{m:02d}")
        month_valid_masks.append(m_valid)

        # Neutral daily composite for each distinct date in month
        if DATES_CACHE_PATH.exists():
            with open(DATES_CACHE_PATH, "r", encoding="utf-8") as f:
                cached_dates = json.load(f)
            dates_m = ee.List(cached_dates.get(f"{m:02d}", []))
        else:
            dates_m = ee.List(dw_m.aggregate_array("system:time_start")).map(
                lambda t: ee.Date(t).format("YYYY-MM-dd")
            ).distinct()

        def make_daily(d):
            d_start = ee.Date(d)
            d_end = d_start.advance(1, "day")
            return (
                dw_m.filterDate(d_start, d_end)
                .select(DW_PROB_BANDS)
                .mean()
                .set("date", d)
            )

        daily_col_m = ee.ImageCollection(dates_m.map(make_daily))
        comp_m = ee.Image(ee.Algorithms.If(
            dates_m.size().gt(0),
            daily_col_m.mean().select(DW_PROB_BANDS).toFloat(),
            empty_template,
        ))
        m_comps.append(comp_m)

    count_stack = ee.Image.cat(count_bands)

    # Annual composite: equal-weighted mean ONLY among valid months
    # (ee.ImageCollection.mean() automatically ignores masked months at each pixel)
    annual_dw = ee.ImageCollection(m_comps).mean()

    # Align 9 continuous probabilities to grid10 using bilinear interpolation
    annual_10m_raw = annual_dw.resample("bilinear").reproject(crs=mb_proj)

    # Raw sum before normalization (sum of all 9 continuous probabilities)
    raw_prob_sum = annual_10m_raw.select(DW_PROB_BANDS[0])
    for b in DW_PROB_BANDS[1:]:
        raw_prob_sum = raw_prob_sum.add(annual_10m_raw.select(b))
    raw_prob_sum = raw_prob_sum.rename("probability_sum_before_normalization")

    # Normalized 9-probability vector (p'_k = p_k / sum(p))
    normalized_probs = annual_10m_raw.divide(raw_prob_sum).rename(DW_PROB_BANDS)

    # Annual class via argmax of normalized vector
    annual_class_index = (
        normalized_probs.toArray()
        .arrayArgmax()
        .arrayGet([0])
        .rename("annual_class_index")
    )

    # dw_crop: 1 if annual class is crops (index 4), 0 otherwise
    dw_crop = annual_class_index.eq(4).rename("dw_crop")

    # Number of valid months: sum of valid month indicators (n_obs > 0)
    n_valid_months = (
        count_stack.gt(0)
        .reduce(ee.Reducer.sum())
        .rename("n_valid_months")
    )

    # Main temporal eligibility rule: n_valid_months >= 8
    temporal_eligible = n_valid_months.gte(MIN_VALID_MONTHS).rename("temporal_eligible")

    # Combined stack for unified sampling or analysis
    dw_annual_stack = ee.Image.cat([
        normalized_probs,
        raw_prob_sum,
        annual_class_index,
        dw_crop,
        n_valid_months,
        temporal_eligible,
        count_stack,
    ])

    return {
        "annual_10m_raw": annual_10m_raw,
        "raw_prob_sum": raw_prob_sum,
        "normalized_probs": normalized_probs,
        "annual_class_index": annual_class_index,
        "dw_crop": dw_crop,
        "n_valid_months": n_valid_months,
        "temporal_eligible": temporal_eligible,
        "count_stack": count_stack,
        "dw_annual_stack": dw_annual_stack,
    }


def get_harmonized_crosswalk_layers(
    source_region: Optional[ee.Geometry] = None,
    mb_proj: Optional[ee.Projection] = None,
) -> dict[str, ee.Image]:
    """
    Returns the complete set of authoritative canonical MapBiomas x Dynamic World layers
    on the official 10m grid, adhering strictly to the frozen crosswalk and fixed
    support domain.

    Crosswalk:
      MapBiomas:
        CROP:     19 (Lavoura Temporária), 36 (Lavoura Perene)
        EXCLUDED: 18 (Agricultura), 21 (Mosaico de Usos)
        NONCROP:  All other valid classes (including 15 Pastagem, 9 Silvicultura)
      Dynamic World:
        CROP:     dw_annual_class == 'crops' (index 4)
        NONCROP:  All other classes

    Eligibility:
      eligible = (mb is not excluded) AND (mb is unmasked) AND
                 (dw is unmasked) AND (n_valid_months >= 8)

    Regimes (defined only where eligible):
      AA = mb_crop == 1 AND dw_crop == 1
      AN = mb_crop == 1 AND dw_crop == 0
      NA = mb_crop == 0 AND dw_crop == 1
      NN = mb_crop == 0 AND dw_crop == 0
    """
    if source_region is None:
        source_region = get_source_support_domain()

    if mb_proj is None:
        mb_proj = get_mapbiomas_projection()

    mb = ee.Image(MB_ASSET).select(MB_BAND)

    # Excluded codes: 18, 21
    is_excluded = mb.eq(21).Or(mb.eq(18)).rename("is_excluded")
    valid_mb_mask = is_excluded.Not().And(mb.mask()).rename("valid_mb_mask")

    # MapBiomas crop binary (1 = crop, 0 = noncrop, masked if excluded or outside)
    mb_crop = (
        mb.remap(CROP_CODES, [1] * len(CROP_CODES), 0)
        .updateMask(valid_mb_mask)
        .rename("mb_crop")
    )

    # Build authoritative Dynamic World 2025 on fixed support domain
    dw_dict = build_dw_annual_2025(source_region=source_region, mb_proj=mb_proj)
    dw_crop = dw_dict["dw_crop"]
    temporal_eligible = dw_dict["temporal_eligible"]
    n_valid_months = dw_dict["n_valid_months"]

    # Dynamic World valid mask
    dw_valid = dw_dict["raw_prob_sum"].mask().rename("dw_valid")

    # Full eligible mask
    eligible_mask = (
        valid_mb_mask
        .And(dw_valid)
        .And(temporal_eligible)
        .rename("eligible_mask")
    )

    # Insufficient temporal coverage mask (valid MB, but DW has <8 months)
    insufficient_dw_temporal = (
        valid_mb_mask
        .And(temporal_eligible.Not().Or(dw_valid.Not()))
        .rename("insufficient_dw_temporal")
    )

    # 4 Regimes (strictly on eligible domain)
    regime_AA = mb_crop.eq(1).And(dw_crop.eq(1)).updateMask(eligible_mask).rename("regime_AA")
    regime_AN = mb_crop.eq(1).And(dw_crop.eq(0)).updateMask(eligible_mask).rename("regime_AN")
    regime_NA = mb_crop.eq(0).And(dw_crop.eq(1)).updateMask(eligible_mask).rename("regime_NA")
    regime_NN = mb_crop.eq(0).And(dw_crop.eq(0)).updateMask(eligible_mask).rename("regime_NN")

    # Integer regime raster: 1=AA, 2=AN, 3=NA, 4=NN (masked elsewhere)
    regime_code = (
        ee.Image(0)
        .where(regime_AA.eq(1), 1)
        .where(regime_AN.eq(1), 2)
        .where(regime_NA.eq(1), 3)
        .where(regime_NN.eq(1), 4)
        .updateMask(eligible_mask)
        .rename("regime_code")
    )

    # ── Canonical Edge Distances (Section 5) ──────────────────────────────
    kernel = ee.Kernel.square(radius=1, units="pixels")

    # 1. MapBiomas Edge & Distance (EPSG:5880, 250m)
    crop_mb_5880 = mb_crop.eq(1).unmask(0).reproject(crs="EPSG:5880", scale=10)
    noncrop_mb_5880 = mb_crop.eq(0).unmask(0).reproject(crs="EPSG:5880", scale=10)
    crop_has_noncrop_mb = noncrop_mb_5880.reduceNeighborhood(ee.Reducer.max(), kernel)
    noncrop_has_crop_mb = crop_mb_5880.reduceNeighborhood(ee.Reducer.max(), kernel)

    edge_mb = (
        crop_mb_5880.eq(1).And(crop_has_noncrop_mb.eq(1))
    ).Or(
        noncrop_mb_5880.eq(1).And(noncrop_has_crop_mb.eq(1))
    ).rename("edge_mb")

    distance_edge_mb_m = (
        edge_mb.fastDistanceTransform(neighborhood=25, units="pixels", metric="squared_euclidean")
        .sqrt()
        .multiply(10)
        .clamp(0, 250)
        .reproject(crs=mb_proj)
        .rename("distance_edge_mb_m")
    )

    # 2. Dynamic World Edge & Distance (EPSG:5880, 250m)
    crop_dw_5880 = dw_crop.eq(1).unmask(0).reproject(crs="EPSG:5880", scale=10)
    noncrop_dw_5880 = dw_crop.eq(0).unmask(0).reproject(crs="EPSG:5880", scale=10)
    crop_has_noncrop_dw = noncrop_dw_5880.reduceNeighborhood(ee.Reducer.max(), kernel)
    noncrop_has_crop_dw = crop_dw_5880.reduceNeighborhood(ee.Reducer.max(), kernel)

    edge_dw = (
        crop_dw_5880.eq(1).And(crop_has_noncrop_dw.eq(1))
    ).Or(
        noncrop_dw_5880.eq(1).And(noncrop_has_crop_dw.eq(1))
    ).rename("edge_dw")

    distance_edge_dw_m = (
        edge_dw.fastDistanceTransform(neighborhood=25, units="pixels", metric="squared_euclidean")
        .sqrt()
        .multiply(10)
        .clamp(0, 250)
        .reproject(crs=mb_proj)
        .rename("distance_edge_dw_m")
    )

    # 3. Minimum Edge Distance
    distance_edge_min_m = distance_edge_mb_m.min(distance_edge_dw_m).rename("distance_edge_min_m")

    # Canonical Stack combining all authoritative layers
    canonical_raster_stack = ee.Image.cat([
        dw_dict["normalized_probs"],
        dw_dict["raw_prob_sum"],
        dw_dict["annual_class_index"],
        dw_crop,
        n_valid_months,
        temporal_eligible,
        mb.rename("mb_raw"),
        mb_crop,
        is_excluded,
        eligible_mask,
        insufficient_dw_temporal,
        regime_AA,
        regime_AN,
        regime_NA,
        regime_NN,
        regime_code,
        distance_edge_mb_m,
        distance_edge_dw_m,
        distance_edge_min_m,
    ])

    return {
        "mb": mb,
        "mb_crop": mb_crop,
        "is_excluded": is_excluded,
        "valid_mb_mask": valid_mb_mask,
        "dw_crop": dw_crop,
        "dw_dict": dw_dict,
        "eligible_mask": eligible_mask,
        "insufficient_dw_temporal": insufficient_dw_temporal,
        "regime_AA": regime_AA,
        "regime_AN": regime_AN,
        "regime_NA": regime_NA,
        "regime_NN": regime_NN,
        "regime_code": regime_code,
        "edge_mb": edge_mb,
        "distance_edge_mb_m": distance_edge_mb_m,
        "edge_dw": edge_dw,
        "distance_edge_dw_m": distance_edge_dw_m,
        "distance_edge_min_m": distance_edge_min_m,
        "canonical_raster_stack": canonical_raster_stack,
    }
