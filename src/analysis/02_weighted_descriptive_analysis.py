"""
02_weighted_descriptive_analysis.py — Estimativas Descritivas Baseadas no Desenho Amostral
==========================================================================================
Calcula as estimativas ponderadas primárias para a Amostra Principal de 20.000 pontos
(e Amostra Robusta de 40.000 pontos como robustez) respeitando estritamente o desenho
amostral estratificado e os pesos de expansão Horvitz-Thompson.

Gera:
  - tables/descriptive_regime_proportions.csv
  - tables/descriptive_state_proportions.csv
  - tables/descriptive_continuous_indicators.csv
  - tables/descriptive_robust_40k_comparison.csv
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


def weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    """Calcula quantil ponderado empírico."""
    sorter = np.argsort(values)
    v_sorted = values[sorter]
    w_sorted = weights[sorter]
    cumsum = np.cumsum(w_sorted)
    cutoff = q * cumsum[-1]
    idx = np.searchsorted(cumsum, cutoff)
    return float(v_sorted[min(idx, len(v_sorted) - 1)])


def weighted_stats(values: np.ndarray, weights: np.ndarray) -> dict[str, float]:
    """Calcula estatísticas descritivas ponderadas completas."""
    w_sum = np.sum(weights)
    w_mean = float(np.sum(values * weights) / w_sum)
    w_var = float(np.sum(weights * (values - w_mean) ** 2) / w_sum)
    w_std = float(np.sqrt(w_var))
    # Erro padrão da média no desenho amostral: sqrt(sum(w^2 * (x - mean)^2)) / sum(w)
    se_mean = float(np.sqrt(np.sum((weights ** 2) * ((values - w_mean) ** 2))) / w_sum)
    q1 = weighted_quantile(values, weights, 0.25)
    med = weighted_quantile(values, weights, 0.50)
    q3 = weighted_quantile(values, weights, 0.75)
    return {
        "mean": w_mean,
        "std": w_std,
        "se": se_mean,
        "q1": q1,
        "median": med,
        "q3": q3,
        "min": float(np.min(values)),
        "max": float(np.max(values)),
    }


def compute_descriptive_analysis():
    print("=" * 80)
    print("ESTIMATIVAS DESCRITIVAS BASEADAS NO DESENHO AMOSTRAL (CHECKPOINT 4)")
    print("=" * 80)

    df = pd.read_parquet(DATA_PARQUET)
    print(f"Dataset lido: {len(df):,} pontos.")

    # 1. Amostra Principal 20k
    main = df[df["main_sample"] == 1].copy()
    main["w_design"] = pd.to_numeric(main["design_weight_main"])
    main["w_area_ha"] = pd.to_numeric(main["area_weight_main"]) / 10000.0  # m2 -> ha
    main["D"] = main["regime"].isin(["AN", "NA"]).astype(int)

    w_tot_pts = main["w_design"].sum()
    w_tot_ha = main["w_area_ha"].sum()

    print(f"\nAmostra Principal 20k: {len(main):,} pontos.")
    print(f"População total estimada em pixels (expandida): {w_tot_pts:,.0f}")
    print(f"Área total elegível estimada: {w_tot_ha:,.2f} ha")

    # 1.1 Proporções por Regime (AA, AN, NA, NN, Concordância, Discordância)
    regimes = ["AA", "AN", "NA", "NN"]
    regime_rows = []
    for r in regimes:
        sub = main[main["regime"] == r]
        n_unweighted = len(sub)
        w_sub = sub["w_design"].values
        w_area = sub["w_area_ha"].sum()
        pct = (np.sum(w_sub) / w_tot_pts) * 100.0
        # Erro padrão da proporção sob amostragem estratificada
        p_val = np.sum(w_sub) / w_tot_pts
        se = float(np.sqrt(p_val * (1.0 - p_val) * np.sum(main["w_design"] ** 2) / (w_tot_pts ** 2)) * 100.0)
        regime_rows.append({
            "regime": r,
            "category": "Concordância" if r in ["AA", "NN"] else "Discordância",
            "sample_n": n_unweighted,
            "sample_pct": (n_unweighted / len(main)) * 100.0,
            "weighted_area_ha": w_area,
            "weighted_pct": pct,
            "se_pct": se,
            "ci95_lower": max(0.0, pct - 1.96 * se),
            "ci95_upper": min(100.0, pct + 1.96 * se),
        })

    # Totais de Concordância e Discordância
    for cat_name, is_d in [("Total Concordância (AA+NN)", 0), ("Total Discordância (AN+NA)", 1)]:
        sub = main[main["D"] == is_d]
        n_unweighted = len(sub)
        w_sub = sub["w_design"].values
        w_area = sub["w_area_ha"].sum()
        pct = (np.sum(w_sub) / w_tot_pts) * 100.0
        p_val = np.sum(w_sub) / w_tot_pts
        se = float(np.sqrt(p_val * (1.0 - p_val) * np.sum(main["w_design"] ** 2) / (w_tot_pts ** 2)) * 100.0)
        regime_rows.append({
            "regime": cat_name,
            "category": "Agregado",
            "sample_n": n_unweighted,
            "sample_pct": (n_unweighted / len(main)) * 100.0,
            "weighted_area_ha": w_area,
            "weighted_pct": pct,
            "se_pct": se,
            "ci95_lower": max(0.0, pct - 1.96 * se),
            "ci95_upper": min(100.0, pct + 1.96 * se),
        })

    df_regime_summary = pd.DataFrame(regime_rows)
    df_regime_summary.to_csv(TABLES_DIR / "descriptive_regime_proportions.csv", index=False)
    print("\n--- Tabela 1: Proporções por Regime (20k Principal) ---")
    print(df_regime_summary.to_string(index=False))

    # 1.2 Proporções por Estado
    state_rows = []
    states = ["MA", "TO", "PI", "BA"]
    for st in states:
        sub_st = main[main["state"] == st]
        w_st_tot = sub_st["w_design"].sum()
        w_st_ha = sub_st["w_area_ha"].sum()
        for r in regimes:
            sub_r = sub_st[sub_st["regime"] == r]
            pct_within_state = (sub_r["w_design"].sum() / w_st_tot) * 100.0
            state_rows.append({
                "state": st,
                "regime": r,
                "sample_n": len(sub_r),
                "weighted_area_ha": sub_r["w_area_ha"].sum(),
                "pct_within_state": pct_within_state,
            })
        # Discordância total no estado
        sub_disc = sub_st[sub_st["D"] == 1]
        pct_disc = (sub_disc["w_design"].sum() / w_st_tot) * 100.0
        p_val = sub_disc["w_design"].sum() / w_st_tot
        se_disc = float(np.sqrt(p_val * (1.0 - p_val) * np.sum(sub_st["w_design"] ** 2) / (w_st_tot ** 2)) * 100.0)
        state_rows.append({
            "state": st,
            "regime": "Total Discordância",
            "sample_n": len(sub_disc),
            "weighted_area_ha": sub_disc["w_area_ha"].sum(),
            "pct_within_state": pct_disc,
        })

    df_state_summary = pd.DataFrame(state_rows)
    df_state_summary.to_csv(TABLES_DIR / "descriptive_state_proportions.csv", index=False)
    print("\n--- Tabela 2: Resumo por Estado (20k Principal) ---")
    print(df_state_summary[df_state_summary["regime"] == "Total Discordância"].to_string(index=False))

    # 1.3 Distribuições Ponderadas dos Indicadores Contínuos
    cont_vars = [
        ("entropy_annual", "Entropia Anual Autoritativa (H_annual)"),
        ("jsd_temporal", "Divergência Jensen-Shannon Temporal (JSD)"),
        ("stability", "Estabilidade Categórica Temporal (S)"),
        ("distance_edge_min_m", "Distância Mínima à Borda (m)"),
        ("distance_edge_mb_m", "Distância à Borda MapBiomas (m)"),
        ("distance_edge_dw_m", "Distância à Borda Dynamic World (m)"),
    ]

    cont_rows = []
    w_vec = main["w_design"].values
    for col, label in cont_vars:
        # Geral
        st_all = weighted_stats(main[col].values, w_vec)
        st_all["variable"] = col
        st_all["label"] = label
        st_all["subset"] = "População Geral"
        st_all["n_sample"] = len(main)
        cont_rows.append(st_all)

        # Concordante (D=0)
        sub0 = main[main["D"] == 0]
        st0 = weighted_stats(sub0[col].values, sub0["w_design"].values)
        st0["variable"] = col
        st0["label"] = label
        st0["subset"] = "Concordância (D=0)"
        st0["n_sample"] = len(sub0)
        cont_rows.append(st0)

        # Discordante (D=1)
        sub1 = main[main["D"] == 1]
        st1 = weighted_stats(sub1[col].values, sub1["w_design"].values)
        st1["variable"] = col
        st1["label"] = label
        st1["subset"] = "Discordância (D=1)"
        st1["n_sample"] = len(sub1)
        cont_rows.append(st1)

    df_cont_summary = pd.DataFrame(cont_rows)
    df_cont_summary.to_csv(TABLES_DIR / "descriptive_continuous_indicators.csv", index=False)
    print("\n--- Tabela 3: Indicadores Contínuos (20k Principal) ---")
    print(df_cont_summary[["variable", "subset", "mean", "std", "median", "q1", "q3"]].to_string(index=False))

    # 2. Comparação de Robustez com a Amostra Robusta 40k
    robust = df[df["robust_sample"] == 1].copy()
    robust["w_design"] = robust["design_weight_robust"]
    robust["w_area_ha"] = robust["area_weight_robust"] / 10000.0
    robust["D"] = robust["regime"].isin(["AN", "NA"]).astype(int)

    w_rob_tot = robust["w_design"].sum()
    rob_rows = []
    for r in regimes:
        sub_20k = main[main["regime"] == r]
        sub_40k = robust[robust["regime"] == r]
        pct_20k = (sub_20k["w_design"].sum() / w_tot_pts) * 100.0
        pct_40k = (sub_40k["w_design"].sum() / w_rob_tot) * 100.0
        rob_rows.append({
            "regime": r,
            "n_20k": len(sub_20k),
            "pct_20k": pct_20k,
            "n_40k": len(sub_40k),
            "pct_40k": pct_40k,
            "diff_pct_points": pct_40k - pct_20k,
        })

    # Discordância total
    disc_20k = main[main["D"] == 1]
    disc_40k = robust[robust["D"] == 1]
    pct_d_20k = (disc_20k["w_design"].sum() / w_tot_pts) * 100.0
    pct_d_40k = (disc_40k["w_design"].sum() / w_rob_tot) * 100.0
    rob_rows.append({
        "regime": "Total Discordância (AN+NA)",
        "n_20k": len(disc_20k),
        "pct_20k": pct_d_20k,
        "n_40k": len(disc_40k),
        "pct_40k": pct_d_40k,
        "diff_pct_points": pct_d_40k - pct_d_20k,
    })

    df_rob_comp = pd.DataFrame(rob_rows)
    df_rob_comp.to_csv(TABLES_DIR / "descriptive_robust_40k_comparison.csv", index=False)
    print("\n--- Tabela 4: Comparação Amostra Principal 20k vs Amostra Robusta 40k ---")
    print(df_rob_comp.to_string(index=False))

    print("\n" + "=" * 80)
    print("ANÁLISE DESCRITIVA CONCLUÍDA COM SUCESSO!")
    print("=" * 80)


if __name__ == "__main__":
    compute_descriptive_analysis()
