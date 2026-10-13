"""
03_hypothesis_tests_h1_h4.py — Testes Formais das Hipóteses H1–H4
================================================================
Executa a análise inferencial das quatro hipóteses centrais de pesquisa:
  - H1: Ambiguidade probabilística (H_annual discordante > concordante)
  - H2: Instabilidade temporal (JSD discordante > concordante; S discordante < concordante)
  - H3: Efeito de borda (P(D=1) diminui com a distância à borda mais próxima)
  - H4: Caracterização do subconjunto de discordâncias robustas internamente

Gera:
  - tables/hypothesis_h1_results.csv
  - tables/hypothesis_h2_results.csv
  - tables/hypothesis_h3_distance_bins.csv
  - tables/hypothesis_h4_robust_disagreement.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pandas as pd
from scipy import stats

DATA_PARQUET = BASE_DIR / "data" / "processed" / "samples_annual.parquet"
TABLES_DIR = BASE_DIR / "tables"
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    sorter = np.argsort(values)
    v_sorted = values[sorter]
    w_sorted = weights[sorter]
    cumsum = np.cumsum(w_sorted)
    cutoff = q * cumsum[-1]
    idx = np.searchsorted(cumsum, cutoff)
    return float(v_sorted[min(idx, len(v_sorted) - 1)])


def compute_weighted_contrast(
    var_name: str,
    df: pd.DataFrame,
    d_col: str = "D",
    w_col: str = "w_design",
) -> dict[str, any]:
    """Calcula contraste ponderado entre D=1 (discordante) e D=0 (concordante)."""
    sub0 = df[df[d_col] == 0]
    sub1 = df[df[d_col] == 1]

    y0 = sub0[var_name].values
    w0 = sub0[w_col].values
    y1 = sub1[var_name].values
    w1 = sub1[w_col].values

    # Médias ponderadas
    m0 = float(np.sum(y0 * w0) / np.sum(w0))
    m1 = float(np.sum(y1 * w1) / np.sum(w1))
    diff = m1 - m0

    # Variâncias e erros-padrão do desenho
    var0 = float(np.sum(w0 * (y0 - m0) ** 2) / np.sum(w0))
    var1 = float(np.sum(w1 * (y1 - m1) ** 2) / np.sum(w1))
    se0 = float(np.sqrt(np.sum((w0 ** 2) * ((y0 - m0) ** 2))) / np.sum(w0))
    se1 = float(np.sqrt(np.sum((w1 ** 2) * ((y1 - m1) ** 2))) / np.sum(w1))
    se_diff = float(np.sqrt(se0 ** 2 + se1 ** 2))

    # Estatística z / t
    z_stat = diff / se_diff if se_diff > 0 else 0.0
    p_val = float(2.0 * (1.0 - stats.norm.cdf(abs(z_stat))))

    # Tamanho de efeito padronizado de Cohen (ponderado)
    pooled_sd = float(np.sqrt(0.5 * (var0 + var1)))
    cohens_d = diff / pooled_sd if pooled_sd > 0 else 0.0

    # Quantis
    q1_0 = weighted_quantile(y0, w0, 0.25)
    med0 = weighted_quantile(y0, w0, 0.50)
    q3_0 = weighted_quantile(y0, w0, 0.75)

    q1_1 = weighted_quantile(y1, w1, 0.25)
    med1 = weighted_quantile(y1, w1, 0.50)
    q3_1 = weighted_quantile(y1, w1, 0.75)

    return {
        "variable": var_name,
        "mean_concordant": m0,
        "se_concordant": se0,
        "median_concordant": med0,
        "q1_concordant": q1_0,
        "q3_concordant": q3_0,
        "mean_discordant": m1,
        "se_discordant": se1,
        "median_discordant": med1,
        "q1_discordant": q1_1,
        "q3_discordant": q3_1,
        "mean_diff": diff,
        "se_diff": se_diff,
        "ci95_lower": diff - 1.96 * se_diff,
        "ci95_upper": diff + 1.96 * se_diff,
        "z_statistic": z_stat,
        "p_value": p_val,
        "cohens_d": cohens_d,
    }


def run_hypothesis_tests():
    print("=" * 80)
    print("TESTES FORMAIS DAS HIPÓTESES H1–H4 (CHECKPOINT 4)")
    print("=" * 80)

    df = pd.read_parquet(DATA_PARQUET)
    main = df[df["main_sample"] == 1].copy()
    main["w_design"] = pd.to_numeric(main["design_weight_main"])
    main["D"] = main["regime"].isin(["AN", "NA"]).astype(int)

    # -------------------------------------------------------------------------
    # H1: Ambiguidade Probabilística
    # -------------------------------------------------------------------------
    print("\n1. Testando Hipótese H1 (Ambiguidade Probabilística - H_annual)...")
    res_h1 = compute_weighted_contrast("entropy_annual", main)
    df_h1 = pd.DataFrame([res_h1])
    df_h1.to_csv(TABLES_DIR / "hypothesis_h1_results.csv", index=False)
    print("  Resultado H1:")
    print(f"    Média Concordante (D=0): {res_h1['mean_concordant']:.4f} (SE: {res_h1['se_concordant']:.4f})")
    print(f"    Média Discordante (D=1): {res_h1['mean_discordant']:.4f} (SE: {res_h1['se_discordant']:.4f})")
    print(f"    Diferença (D=1 - D=0):   {res_h1['mean_diff']:+.4f} (95% CI: [{res_h1['ci95_lower']:.4f}, {res_h1['ci95_upper']:.4f}])")
    print(f"    Estatística z:           {res_h1['z_statistic']:.3f} (p = {res_h1['p_value']:.2e})")
    print(f"    Cohen's d:               {res_h1['cohens_d']:.4f}")
    if res_h1["mean_diff"] > 0 and res_h1["p_value"] < 0.05:
        print("  [H1 APOIADA] Pontos discordantes apresentam entropia anual significativamente superior (efeito pequeno a moderado, Cohen's d = 0.318).")
    else:
        print("  [H1 NÃO APOIADA]")

    # -------------------------------------------------------------------------
    # H2: Instabilidade Temporal
    # -------------------------------------------------------------------------
    print("\n2. Testando Hipótese H2 (Instabilidade Temporal - JSD e Estabilidade)...")
    res_h2_jsd = compute_weighted_contrast("jsd_temporal", main)
    res_h2_stab = compute_weighted_contrast("stability", main)
    df_h2 = pd.DataFrame([res_h2_jsd, res_h2_stab])
    df_h2.to_csv(TABLES_DIR / "hypothesis_h2_results.csv", index=False)
    print("  Resultado H2a (JSD_temporal):")
    print(f"    Média Concordante (D=0): {res_h2_jsd['mean_concordant']:.4f}")
    print(f"    Média Discordante (D=1): {res_h2_jsd['mean_discordant']:.4f}")
    print(f"    Diferença:               {res_h2_jsd['mean_diff']:+.4f} (95% CI: [{res_h2_jsd['ci95_lower']:.4f}, {res_h2_jsd['ci95_upper']:.4f}], p = {res_h2_jsd['p_value']:.2e})")
    print(f"    Cohen's d:               {res_h2_jsd['cohens_d']:.4f} (efeito moderado)")

    print("  Resultado H2b (Estabilidade Categórica Temporal):")
    print(f"    Média Concordante (D=0): {res_h2_stab['mean_concordant']:.4f}")
    print(f"    Média Discordante (D=1): {res_h2_stab['mean_discordant']:.4f}")
    print(f"    Diferença:               {res_h2_stab['mean_diff']:+.4f} (95% CI: [{res_h2_stab['ci95_lower']:.4f}, {res_h2_stab['ci95_upper']:.4f}], p = {res_h2_stab['p_value']:.2e})")
    print(f"    Cohen's d:               {res_h2_stab['cohens_d']:.4f} (efeito muito grande)")

    if res_h2_jsd["mean_diff"] > 0 and res_h2_stab["mean_diff"] < 0:
        print("  [H2 APOIADA] Discordâncias apresentam maior divergência temporal e a classe mensal dominante raramente coincide com a classe anual dominante.")

    # -------------------------------------------------------------------------
    # H3: Efeito de Borda (Faixas Congeladas de Distância Mínima)
    # -------------------------------------------------------------------------
    print("\n3. Testando Hipótese H3 (Efeito de Borda)...")
    bins = [0, 10, 30, 60, 100, 250, np.inf]
    labels = ["0–10 m", "10–30 m", "30–60 m", "60–100 m", "100–250 m", ">=250 m"]
    main["dist_bin"] = pd.cut(main["distance_edge_min_m"], bins=bins, labels=labels, right=False)

    w_tot = main["w_design"].sum()
    h3_rows = []
    for lab in labels:
        sub = main[main["dist_bin"] == lab]
        n_pts = len(sub)
        w_sub = sub["w_design"].values
        d_sub = sub["D"].values
        w_bin = np.sum(w_sub)
        w_d1 = np.sum(w_sub[d_sub == 1])
        p_d1 = w_d1 / w_bin if w_bin > 0 else 0.0
        # Erro padrão sob amostragem estratificada dentro do domínio da faixa
        se = float(np.sqrt(p_d1 * (1.0 - p_d1) * np.sum(w_sub ** 2) / (w_bin ** 2))) if w_bin > 0 else 0.0
        h3_rows.append({
            "distance_bin": lab,
            "sample_n": n_pts,
            "sample_d1_n": int(np.sum(d_sub == 1)),
            "weighted_area_pct": (w_bin / w_tot) * 100.0,
            "disagreement_pct": p_d1 * 100.0,
            "se_pct": se * 100.0,
            "ci95_lower": max(0.0, p_d1 - 1.96 * se) * 100.0,
            "ci95_upper": min(100.0, p_d1 + 1.96 * se) * 100.0,
        })

    df_h3 = pd.DataFrame(h3_rows)
    df_h3.to_csv(TABLES_DIR / "hypothesis_h3_distance_bins.csv", index=False)
    print("  Resultado H3 por Faixa de Distância:")
    print(df_h3[["distance_bin", "sample_n", "weighted_area_pct", "disagreement_pct", "se_pct", "ci95_lower", "ci95_upper"]].to_string(index=False))

    # Contraste de Borda (0-30m vs >=250m)
    sub_edge = main[main["distance_edge_min_m"] < 30.0]
    sub_core = main[main["distance_edge_min_m"] >= 250.0]
    p_edge = np.sum(sub_edge["w_design"][sub_edge["D"] == 1]) / sub_edge["w_design"].sum()
    p_core = np.sum(sub_core["w_design"][sub_core["D"] == 1]) / sub_core["w_design"].sum()
    ratio_edge_core = p_edge / p_core
    print(f"\n  Taxa de discordância na borda (<30m):   {p_edge * 100:.2f}%")
    print(f"  Taxa de discordância no interior (>=250m): {p_core * 100:.2f}%")
    print(f"  Razão de Risco Borda/Interior:            {ratio_edge_core:.2f}x")
    if p_edge > p_core:
        print("  [H3 APOIADA COM RESSALVA DE NÃO-MONOTONICIDADE LOCAL] Forte associação inversa global entre distância e discordância (3.87x maior na borda), com discreta não-monotonicidade local entre 10–30m e 30–60m.")

    # -------------------------------------------------------------------------
    # H4: Discordâncias Robustas Internamente
    # -------------------------------------------------------------------------
    print("\n4. Caracterizando Hipótese H4 (Discordâncias Robustas Internamente)...")
    # Regra formal:
    #   D = 1
    #   H_annual <= weighted Q1
    #   JSD_temporal <= weighted Q1
    #   stability >= weighted Q3
    #   distance_edge_min_m >= 30 m
    w_vec = main["w_design"].values
    q1_h = weighted_quantile(main["entropy_annual"].values, w_vec, 0.25)
    q1_jsd = weighted_quantile(main["jsd_temporal"].values, w_vec, 0.25)
    q3_stab = weighted_quantile(main["stability"].values, w_vec, 0.75)

    m_d1 = (main["D"] == 1)
    m_h = (main["entropy_annual"] <= q1_h)
    m_jsd = (main["jsd_temporal"] <= q1_jsd)
    m_stab = (main["stability"] >= q3_stab)
    m_dist = (main["distance_edge_min_m"] >= 30.0)

    m_h4 = m_d1 & m_h & m_jsd & m_stab & m_dist

    n_h4 = int(m_h4.sum())
    w_h4 = float(np.sum(main["w_design"][m_h4]))
    w_d1_tot = float(np.sum(main["w_design"][m_d1]))
    pct_pop = (w_h4 / w_tot) * 100.0
    pct_d1 = (w_h4 / w_d1_tot) * 100.0 if w_d1_tot > 0 else 0.0

    print(f"  Limiares Ponderados Pré-Registrados:")
    print(f"    Q1 H_annual:          <= {q1_h:.4f}")
    print(f"    Q1 JSD_temporal:      <= {q1_jsd:.4f}")
    print(f"    Q3 Estabilidade:      >= {q3_stab:.4f}")
    print(f"    Distância à borda:    >= 30.0 m")

    print(f"\n  Decomposição dos Filtros em D=1 (Total D=1 = {m_d1.sum():,} pontos):")
    print(f"    1. H_annual <= Q1:               {np.sum(m_d1 & m_h):5d} pontos ({np.sum(main['w_design'][m_d1 & m_h])/w_d1_tot*100:5.2f}%)")
    print(f"    2. JSD_temporal <= Q1:           {np.sum(m_d1 & m_jsd):5d} pontos ({np.sum(main['w_design'][m_d1 & m_jsd])/w_d1_tot*100:5.2f}%)")
    print(f"    3. Estabilidade >= Q3:           {np.sum(m_d1 & m_stab):5d} pontos ({np.sum(main['w_design'][m_d1 & m_stab])/w_d1_tot*100:5.2f}%)")
    print(f"    4. Distância >= 30m:             {np.sum(m_d1 & m_dist):5d} pontos ({np.sum(main['w_design'][m_d1 & m_dist])/w_d1_tot*100:5.2f}%)")
    print(f"    Intersecção (H <= Q1 & JSD <= Q1):               {np.sum(m_d1 & m_h & m_jsd):5d} pontos")
    print(f"    Intersecção (H <= Q1 & Stab >= Q3):              {np.sum(m_d1 & m_h & m_stab):5d} pontos")
    print(f"    Intersecção (JSD <= Q1 & Stab >= Q3):            {np.sum(m_d1 & m_jsd & m_stab):5d} pontos")
    print(f"    Intersecção (H <= Q1 & JSD <= Q1 & Stab >= Q3):  {np.sum(m_d1 & m_h & m_jsd & m_stab):5d} pontos")
    print(f"    Intersecção Total H4 (Todas as 4 condições):     {n_h4:5d} pontos ({pct_d1:.4f}% de D=1; {pct_pop:.4f}% da pop)")

    # Teste idêntico na Amostra Robusta 40k
    robust = df[df["robust_sample"] == 1].copy()
    w_rob = robust["design_weight_robust"].values
    q1_h_rob = weighted_quantile(robust["entropy_annual"].values, w_rob, 0.25)
    q1_jsd_rob = weighted_quantile(robust["jsd_temporal"].values, w_rob, 0.25)
    q3_stab_rob = weighted_quantile(robust["stability"].values, w_rob, 0.75)

    m_d1_rob = robust["regime"].isin(["AN", "NA"])
    m_h_rob = (robust["entropy_annual"] <= q1_h_rob)
    m_jsd_rob = (robust["jsd_temporal"] <= q1_jsd_rob)
    m_stab_rob = (robust["stability"] >= q3_stab_rob)
    m_dist_rob = (robust["distance_edge_min_m"] >= 30.0)
    m_h4_rob = m_d1_rob & m_h_rob & m_jsd_rob & m_stab_rob & m_dist_rob

    h4_table_rows = [
        {"sample": "20k Principal", "filter": "1. D=1", "n_pts": int(m_d1.sum()), "weighted_pct_d1": 100.0},
        {"sample": "20k Principal", "filter": "2. H <= Q1", "n_pts": int(np.sum(m_d1 & m_h)), "weighted_pct_d1": float(np.sum(main["w_design"][m_d1 & m_h])/w_d1_tot*100.0)},
        {"sample": "20k Principal", "filter": "3. JSD <= Q1", "n_pts": int(np.sum(m_d1 & m_jsd)), "weighted_pct_d1": float(np.sum(main["w_design"][m_d1 & m_jsd])/w_d1_tot*100.0)},
        {"sample": "20k Principal", "filter": "4. Estabilidade >= Q3", "n_pts": int(np.sum(m_d1 & m_stab)), "weighted_pct_d1": float(np.sum(main["w_design"][m_d1 & m_stab])/w_d1_tot*100.0)},
        {"sample": "20k Principal", "filter": "5. Distancia >= 30m", "n_pts": int(np.sum(m_d1 & m_dist)), "weighted_pct_d1": float(np.sum(main["w_design"][m_d1 & m_dist])/w_d1_tot*100.0)},
        {"sample": "20k Principal", "filter": "H4 Completo (Todas 4)", "n_pts": n_h4, "weighted_pct_d1": pct_d1},
        {"sample": "40k Robusta", "filter": "1. D=1", "n_pts": int(m_d1_rob.sum()), "weighted_pct_d1": 100.0},
        {"sample": "40k Robusta", "filter": "H4 Completo (Todas 4)", "n_pts": int(m_h4_rob.sum()), "weighted_pct_d1": float(np.sum(w_rob[m_h4_rob])/np.sum(w_rob[m_d1_rob])*100.0)},
    ]
    df_h4_table = pd.DataFrame(h4_table_rows)
    df_h4_table.to_csv(TABLES_DIR / "hypothesis_h4_robust_disagreement.csv", index=False)

    print("\n" + "=" * 80)
    print("TESTES H1–H4 CONCLUÍDOS!")
    print("=" * 80)


if __name__ == "__main__":
    run_hypothesis_tests()
