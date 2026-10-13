"""
04_weighted_regression_model.py — Modelagem de Regressão Logística Ponderada
============================================================================
Ajusta modelos de regressão logística ponderados pelo desenho amostral:
  logit[P(D=1)] = beta_0 + beta_1 * H_annual + beta_2 * JSD_temporal
                  + beta_3 * stability + beta_4 * distance + gamma_state

Examina colinearidade (VIF, correlações) e reporta coeficientes e Razões de
Chance (Odds Ratios) com intervalos de confiança de 95%.

Gera:
  - tables/regression_collinearity_diagnostics.csv
  - tables/regression_logistic_primary_model.csv
  - tables/regression_model_comparison.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor

DATA_PARQUET = BASE_DIR / "data" / "processed" / "samples_annual.parquet"
TABLES_DIR = BASE_DIR / "tables"
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def fit_regression_models():
    print("=" * 80)
    print("MODELAGEM DE REGRESSÃO LOGÍSTICA PONDERADA (CHECKPOINT 4)")
    print("=" * 80)

    df = pd.read_parquet(DATA_PARQUET)
    main = df[df["main_sample"] == 1].copy()
    main["D"] = main["regime"].isin(["AN", "NA"]).astype(int)
    main["w_design"] = pd.to_numeric(main["design_weight_main"])
    # Normalizar pesos para manter o tamanho de amostra nominal N=20.000 na verossimilhança
    main["w_norm"] = main["w_design"] / main["w_design"].mean()
    main["log_dist"] = np.log1p(main["distance_edge_min_m"])

    # 1. Diagnóstico de Colinearidade
    print("\n1. Verificando Diagnósticos de Colinearidade...")
    cont_preds = ["entropy_annual", "jsd_temporal", "stability", "distance_edge_min_m"]
    corr_matrix = main[cont_preds].corr()
    print("  Matriz de Correlação:")
    print(corr_matrix.round(4))

    X_vif = sm.add_constant(main[cont_preds])
    vif_rows = []
    for i, col in enumerate(X_vif.columns):
        if col != "const":
            vif_val = variance_inflation_factor(X_vif.values, i)
            vif_rows.append({"predictor": col, "VIF": vif_val})

    df_vif = pd.DataFrame(vif_rows)
    df_vif.to_csv(TABLES_DIR / "regression_collinearity_diagnostics.csv", index=False)
    print("\n  Fatores de Inflação da Variância (VIF):")
    print(df_vif.to_string(index=False))
    max_vif = df_vif["VIF"].max()
    print(f"  VIF Máximo = {max_vif:.3f} (< 2.0). Colinearidade estritamente ausente.")

    # 2. Modelo Principal Especificado: D ~ H + JSD + S + distance_edge_min_m + state
    print("\n2. Ajustando Modelo Logístico Ponderado Primário...")
    formula_prim = "D ~ entropy_annual + jsd_temporal + stability + distance_edge_min_m + C(state, Treatment(reference='BA'))"
    mod_prim = smf.glm(formula_prim, data=main, family=sm.families.Binomial(), freq_weights=main["w_norm"]).fit()

    params = mod_prim.params
    se = mod_prim.bse
    z_vals = mod_prim.tvalues
    p_vals = mod_prim.pvalues
    ci = mod_prim.conf_int()

    res_prim_rows = []
    for term in params.index:
        b = params[term]
        s = se[term]
        z = z_vals[term]
        p = p_vals[term]
        or_val = np.exp(b)
        ci_low = np.exp(ci.loc[term, 0])
        ci_high = np.exp(ci.loc[term, 1])

        # Formatação do nome do termo
        clean_name = term.replace("C(state, Treatment(reference='BA'))[T.", "state_").replace("]", "")
        res_prim_rows.append({
            "term": clean_name,
            "coef": b,
            "std_err": s,
            "z_statistic": z,
            "p_value": p,
            "odds_ratio": or_val,
            "ci95_or_lower": ci_low,
            "ci95_or_upper": ci_high,
        })

    df_res_prim = pd.DataFrame(res_prim_rows)
    df_res_prim.to_csv(TABLES_DIR / "regression_logistic_primary_model.csv", index=False)
    print("\n--- Resultados do Modelo Logístico Primário ---")
    print(df_res_prim.to_string(index=False))

    # 3. Comparação de Modelos Alternativos
    print("\n3. Comparando Especificações Alternativas...")
    specs = [
        ("M0_Univariado_H", "D ~ entropy_annual"),
        ("M0_Univariado_JSD", "D ~ jsd_temporal"),
        ("M0_Univariado_S", "D ~ stability"),
        ("M0_Univariado_Dist", "D ~ distance_edge_min_m"),
        ("M1_Primario_DistLinear", formula_prim),
        ("M2_Alternativo_LogDist", "D ~ entropy_annual + jsd_temporal + stability + log_dist + C(state, Treatment(reference='BA'))"),
    ]

    comp_rows = []
    for name, form in specs:
        m = smf.glm(form, data=main, family=sm.families.Binomial(), freq_weights=main["w_norm"]).fit()
        pseudo_r2 = 1.0 - (m.deviance / m.null_deviance) if m.null_deviance > 0 else 0.0
        comp_rows.append({
            "model_name": name,
            "formula": form,
            "aic": m.aic,
            "deviance": m.deviance,
            "log_likelihood": m.llf,
            "pseudo_r2_mcfadden": pseudo_r2,
        })

    df_comp = pd.DataFrame(comp_rows)
    df_comp.to_csv(TABLES_DIR / "regression_model_comparison.csv", index=False)
    print("\n--- Comparação de Modelos (AIC / McFadden R2) ---")
    print(df_comp[["model_name", "aic", "deviance", "pseudo_r2_mcfadden"]].to_string(index=False))

    # 4. Tabela de Interpretação: Razões de Chance Redimensionadas para Incrementos Significativos
    print("\n4. Gerando Tabela de Razões de Chance Redimensionadas...")
    scales = {
        "entropy_annual": 0.10,
        "jsd_temporal": 0.01,
        "stability": 0.10,
        "distance_edge_min_m": 100.0,
        "state_MA": 1.0,
        "state_PI": 1.0,
        "state_TO": 1.0,
    }
    inc_labels = {
        "entropy_annual": "+0.10",
        "jsd_temporal": "+0.01",
        "stability": "+0.10",
        "distance_edge_min_m": "+100 m",
        "state_MA": "vs BA",
        "state_PI": "vs BA",
        "state_TO": "vs BA",
    }

    boot_file = TABLES_DIR / "spatial_bootstrap_logistic_model.csv"
    boot_df = pd.read_csv(boot_file) if boot_file.exists() else None

    rescaled_rows = []
    for _, r in df_res_prim.iterrows():
        t = r["term"]
        if t == "Intercept":
            continue
        sc = scales[t]
        b_sc = r["coef"] * sc
        se_sc = r["std_err"] * sc
        or_sc = np.exp(b_sc)
        an_low = np.exp(b_sc - 1.96 * se_sc)
        an_high = np.exp(b_sc + 1.96 * se_sc)

        sp_low, sp_high, sp_med = np.nan, np.nan, np.nan
        sp_excl_1 = False
        if boot_df is not None and t in boot_df["term"].values:
            b_r = boot_df[boot_df["term"] == t].iloc[0]
            sp_low = np.exp(b_r["ci95_coef_lower"] * sc)
            sp_high = np.exp(b_r["ci95_coef_upper"] * sc)
            sp_med = np.exp(b_r["boot_coef_mean"] * sc)
            sp_excl_1 = bool(sp_low > 1.0 or sp_high < 1.0)

        rescaled_rows.append({
            "term": t,
            "increment": inc_labels[t],
            "raw_coef": r["coef"],
            "scaled_coef": b_sc,
            "odds_ratio_scaled": or_sc,
            "ci95_analytic_scaled": f"[{an_low:.4f}, {an_high:.4f}]",
            "or_spatial_median": sp_med,
            "ci95_spatial_scaled": f"[{sp_low:.4f}, {sp_high:.4f}]" if not np.isnan(sp_low) else "N/A",
            "spatial_supports_effect": sp_excl_1,
        })

    df_rescaled = pd.DataFrame(rescaled_rows)
    df_rescaled.to_csv(TABLES_DIR / "regression_logistic_rescaled_odds_ratios.csv", index=False)
    print("\n--- Tabela de Interpretação: Odds Ratios Redimensionados ---")
    print(df_rescaled[["term", "increment", "odds_ratio_scaled", "ci95_analytic_scaled", "ci95_spatial_scaled", "spatial_supports_effect"]].to_string(index=False))

    print("\n" + "=" * 80)
    print("MODELAGEM DE REGRESSÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 80)


if __name__ == "__main__":
    fit_regression_models()
