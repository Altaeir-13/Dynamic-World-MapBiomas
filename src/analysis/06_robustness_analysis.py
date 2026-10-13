"""
06_robustness_analysis.py — Análises de Robustez Obrigatórias (Checkpoint 4)
===========================================================================
Executa as análises de robustez que utilizam a mesma população elegível congelada (n_valid_months >= 8):
  - R1: Tamanho Amostral (Amostra Principal 20k vs Amostra Robusta 40k)
  - R2: Crosswalk Estrito MapBiomas ({19} Lavoura Temporária vs Primário {19, 36})
  - R3: Subconjunto com Estabilidade Histórica MapBiomas 2017–2025 (9 anos contínuos)

Gera:
  - tables/robustness_r1_sample_size_comparison.csv
  - tables/robustness_r2_strict_crosswalk_comparison.csv
  - tables/robustness_r3_mapbiomas_stability_subset.csv
  - tables/robustness_comprehensive_summary.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pandas as pd

DATA_PARQUET = BASE_DIR / "data" / "processed" / "samples_annual.parquet"
TABLES_DIR = BASE_DIR / "tables"
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def compute_weighted_diff(var_name: str, df: pd.DataFrame, d_col: str, w_col: str) -> float:
    sub0 = df[df[d_col] == 0]
    sub1 = df[df[d_col] == 1]
    m0 = np.sum(sub0[var_name] * sub0[w_col]) / np.sum(sub0[w_col])
    m1 = np.sum(sub1[var_name] * sub1[w_col]) / np.sum(sub1[w_col])
    return float(m1 - m0)


def compute_metrics_for_subset(df_sub: pd.DataFrame, d_col: str, w_col: str, label: str) -> dict[str, any]:
    w = df_sub[w_col].values
    d = df_sub[d_col].values

    w_tot = np.sum(w)
    w_d1 = np.sum(w[d == 1])
    p_disc = (w_d1 / w_tot) * 100.0

    delta_h = compute_weighted_diff("entropy_annual", df_sub, d_col, w_col)
    delta_jsd = compute_weighted_diff("jsd_temporal", df_sub, d_col, w_col)
    delta_s = compute_weighted_diff("stability", df_sub, d_col, w_col)
    delta_dist = compute_weighted_diff("distance_edge_min_m", df_sub, d_col, w_col)

    # Discordância na borda (<30m) vs interior (>=250m)
    sub_edge = df_sub[df_sub["distance_edge_min_m"] < 30.0]
    sub_core = df_sub[df_sub["distance_edge_min_m"] >= 250.0]
    p_edge = (np.sum(sub_edge[w_col][sub_edge[d_col] == 1]) / np.sum(sub_edge[w_col])) * 100.0
    p_core = (np.sum(sub_core[w_col][sub_core[d_col] == 1]) / np.sum(sub_core[w_col])) * 100.0

    return {
        "scenario": label,
        "n_sample": len(df_sub),
        "disagreement_rate_pct": p_disc,
        "delta_h_annual": delta_h,
        "delta_jsd_temporal": delta_jsd,
        "delta_stability": delta_s,
        "delta_distance_m": delta_dist,
        "disc_edge_30m_pct": p_edge,
        "disc_core_250m_pct": p_core,
        "edge_core_ratio": p_edge / p_core if p_core > 0 else np.nan,
    }


def run_robustness_analysis():
    print("=" * 80)
    print("ANÁLISES DE ROBUSTEZ OBRIGATÓRIAS (CHECKPOINT 4)")
    print("=" * 80)

    df = pd.read_parquet(DATA_PARQUET)

    # 1. Base Primária: Amostra 20k
    main = df[df["main_sample"] == 1].copy()
    main["w_design"] = pd.to_numeric(main["design_weight_main"])
    main["D_primary"] = main["regime"].isin(["AN", "NA"]).astype(int)

    # 2. R1: Amostra Robusta 40k
    robust = df[df["robust_sample"] == 1].copy()
    robust["w_design"] = robust["design_weight_robust"]
    robust["D_primary"] = robust["regime"].isin(["AN", "NA"]).astype(int)

    # 3. R2: Crosswalk Estrito MapBiomas (apenas classe 19 = lavoura temporária)
    # Class 36 = lavoura perene. Se estrito, classe 36 torna-se não-agrícola (0)
    main["mb_crop_strict"] = (main["mapbiomas_class"] == 19).astype(int)
    # Recalcular regime sob crosswalk estrito
    # regime_strict:
    #   DW=1, MB=1 -> AA
    #   DW=0, MB=1 -> AN
    #   DW=1, MB=0 -> NA
    #   DW=0, MB=0 -> NN
    dw_crop = main["dw_crop"].values
    mb_strict = main["mb_crop_strict"].values
    reg_strict = np.where(
        (dw_crop == 1) & (mb_strict == 1), "AA",
        np.where((dw_crop == 0) & (mb_strict == 1), "AN",
        np.where((dw_crop == 1) & (mb_strict == 0), "NA", "NN"))
    )
    main["regime_strict"] = reg_strict
    main["D_strict"] = main["regime_strict"].isin(["AN", "NA"]).astype(int)

    # 4. R3: Subconjunto com Estabilidade Histórica MapBiomas 2017–2025
    main_stable = main[main["mapbiomas_stable_2017_2025"] == 1].copy()

    # Compilar Métricas para Todos os Cenários
    rows = [
        compute_metrics_for_subset(main, "D_primary", "w_design", "Primário (20k Main, Crosswalk {19,36})"),
        compute_metrics_for_subset(robust, "D_primary", "w_design", "R1: Amostra Robusta (40k, Crosswalk {19,36})"),
        compute_metrics_for_subset(main, "D_strict", "w_design", "R2: Crosswalk Estrito MapBiomas ({19})"),
        compute_metrics_for_subset(main_stable, "D_primary", "w_design", "R3: MapBiomas Estável 2017–2025 (20k Main)"),
    ]

    df_summary = pd.DataFrame(rows)
    df_summary.to_csv(TABLES_DIR / "robustness_comprehensive_summary.csv", index=False)
    print("\n--- Sumário Comparativo de Robustez ---")
    print(df_summary[["scenario", "n_sample", "disagreement_rate_pct", "delta_h_annual", "delta_jsd_temporal", "delta_stability", "edge_core_ratio"]].to_string(index=False))

    # Tabelas Individuais Detalhadas
    # R1: 20k vs 40k por Regime
    r1_regimes = []
    w_20k_tot = main["w_design"].sum()
    w_40k_tot = robust["w_design"].sum()
    for r in ["AA", "AN", "NA", "NN"]:
        p20 = (main[main["regime"] == r]["w_design"].sum() / w_20k_tot) * 100.0
        p40 = (robust[robust["regime"] == r]["w_design"].sum() / w_40k_tot) * 100.0
        r1_regimes.append({
            "regime": r,
            "pct_20k": p20,
            "pct_40k": p40,
            "diff_pct_points": p40 - p20,
        })
    df_r1 = pd.DataFrame(r1_regimes)
    df_r1.to_csv(TABLES_DIR / "robustness_r1_sample_size_comparison.csv", index=False)

    # R2: Impacto da Classe 36 (Lavoura Perene)
    c36_pts = (main["mapbiomas_class"] == 36).sum()
    w_c36 = main[main["mapbiomas_class"] == 36]["w_design"].sum()
    df_r2 = pd.DataFrame([{
        "points_class_36": int(c36_pts),
        "weighted_pct_class_36": (w_c36 / w_20k_tot) * 100.0,
        "disagreement_primary_pct": df_summary.loc[0, "disagreement_rate_pct"],
        "disagreement_strict_pct": df_summary.loc[2, "disagreement_rate_pct"],
        "delta_disagreement_pct": df_summary.loc[2, "disagreement_rate_pct"] - df_summary.loc[0, "disagreement_rate_pct"],
    }])
    df_r2.to_csv(TABLES_DIR / "robustness_r2_strict_crosswalk_comparison.csv", index=False)

    # R3: Estabilidade MapBiomas
    df_r3 = pd.DataFrame([{
        "stable_subset_n": len(main_stable),
        "stable_subset_pct_sample": (len(main_stable) / len(main)) * 100.0,
        "disagreement_primary_pct": df_summary.loc[0, "disagreement_rate_pct"],
        "disagreement_stable_pct": df_summary.loc[3, "disagreement_rate_pct"],
        "delta_h_annual_stable": df_summary.loc[3, "delta_h_annual"],
        "delta_stability_stable": df_summary.loc[3, "delta_stability"],
    }])
    df_r3.to_csv(TABLES_DIR / "robustness_r3_mapbiomas_stability_subset.csv", index=False)

    print("\n" + "=" * 80)
    print("ANÁLISES DE ROBUSTEZ CONCLUÍDAS COM SUCESSO!")
    print("=" * 80)


if __name__ == "__main__":
    run_robustness_analysis()
