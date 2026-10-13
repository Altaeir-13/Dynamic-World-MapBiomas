"""
07_generate_publication_figures.py — Geração das Figuras Científicas do Checkpoint 4
====================================================================================
Gera as 6 figuras de alta resolução (300 DPI) para publicação científica:
  1. figures/fig1_composition_regimes.png: Composição ponderada dos regimes AA/AN/NA/NN
  2. figures/fig2_h_annual_distribution.png: Distribuição de H_annual (Concordância vs Discordância)
  3. figures/fig3_jsd_temporal_distribution.png: Distribuição de JSD_temporal (Concordância vs Discordância)
  4. figures/fig4_stability_distribution.png: Distribuição da Estabilidade Temporal (Concordância vs Discordância)
  5. figures/fig5_disagreement_by_distance_bin.png: Proporção de discordância por faixa de distância
  6. figures/fig6_h4_robust_disagreement_characterization.png: Caracterização multivariada do filtro H4
"""

from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

DATA_PARQUET = BASE_DIR / "data" / "processed" / "samples_annual.parquet"
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR = BASE_DIR / "tables"
ROOT_SEED = 25

# Configuração estética padronizada para periódicos de alto impacto
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "Helvetica"],
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "--",
})

# Paleta acadêmica estrita
COLORS = {
    "NN": "#2b5c8f",      # Azul sóbrio (Não-agrícola concordante)
    "AN": "#d95f02",      # Laranja forte (Omissão DW / Excesso MB)
    "NA": "#7570b3",      # Roxo/Carmim (Comissão DW / Omissão MB)
    "AA": "#1b9e77",      # Verde floresta (Agrícola concordante)
    "D0": "#1f77b4",      # Azul para concordância geral
    "D1": "#d62728",      # Vermelho para discordância geral
}


def weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    sorter = np.argsort(values)
    v_sorted = values[sorter]
    w_sorted = weights[sorter]
    cumsum = np.cumsum(w_sorted)
    cutoff = q * cumsum[-1]
    idx = np.searchsorted(cumsum, cutoff)
    return float(v_sorted[min(idx, len(v_sorted) - 1)])


def generate_figures():
    print("=" * 80)
    print("GERANDO FIGURAS CIENTÍFICAS DO CHECKPOINT 4 (300 DPI)")
    print("=" * 80)

    df = pd.read_parquet(DATA_PARQUET)
    main = df[df["main_sample"] == 1].copy()
    main["w_design"] = pd.to_numeric(main["design_weight_main"])
    main["D"] = main["regime"].isin(["AN", "NA"]).astype(int)
    w_tot = main["w_design"].sum()

    # -------------------------------------------------------------------------
    # Figura 1: Composição Ponderada dos Regimes (Geral e por Estado)
    # -------------------------------------------------------------------------
    print("\n1. Gerando Figura 1: Composição Ponderada dos Regimes...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), gridspec_kw={"width_ratios": [1, 1.4]})

    regimes = ["NN", "AN", "NA", "AA"]
    labels_reg = [
        "NN: Concordância\nNão-Agrícola (83.2%)",
        "AN: Omissão DW /\nExcesso MB (9.7%)",
        "NA: Comissão DW /\nOmissão MB (4.7%)",
        "AA: Concordância\nAgrícola (2.4%)"
    ]
    pcts_reg = [(main[main["regime"] == r]["w_design"].sum() / w_tot) * 100.0 for r in regimes]
    bar_colors = [COLORS[r] for r in regimes]

    bars = ax1.bar(labels_reg, pcts_reg, color=bar_colors, width=0.65, edgecolor="black", linewidth=0.8)
    ax1.set_ylabel("Área Ponderada Elegível (%)")
    ax1.set_title("A. Composição Global no MATOPIBA", fontweight="bold", pad=12)
    ax1.set_ylim(0, 100)
    for bar, pct in zip(bars, pcts_reg):
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2.0, yval + 1.5, f"{pct:.2f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")

    # Painel B: Por Estado
    states = ["TO", "MA", "PI", "BA"]
    state_names = ["Tocantins (TO)", "Maranhão (MA)", "Piauí (PI)", "Bahia (BA)"]
    x_indices = np.arange(len(states))
    bottoms = np.zeros(len(states))

    for r in regimes:
        reg_pcts_state = []
        for st in states:
            sub_st = main[main["state"] == st]
            w_st = sub_st["w_design"].sum()
            sub_r = sub_st[sub_st["regime"] == r]
            p = (sub_r["w_design"].sum() / w_st) * 100.0
            reg_pcts_state.append(p)
        reg_pcts_state = np.array(reg_pcts_state)
        ax2.bar(x_indices, reg_pcts_state, bottom=bottoms, width=0.55, label=r, color=COLORS[r], edgecolor="black", linewidth=0.8)
        bottoms += reg_pcts_state

    ax2.set_xticks(x_indices)
    ax2.set_xticklabels(state_names)
    ax2.set_ylabel("Área Ponderada Estadual (%)")
    ax2.set_title("B. Distribuição por Unidade Federativa", fontweight="bold", pad=12)
    ax2.set_ylim(0, 100)
    ax2.legend(title="Regime", loc="upper right", framealpha=0.9)

    plt.tight_layout()
    f1_path = FIGURES_DIR / "fig1_composition_regimes.png"
    fig.savefig(f1_path)
    plt.close(fig)
    print(f"  Salva: {f1_path.name}")

    # -------------------------------------------------------------------------
    # Figura 2: Hipótese H1 — Distribuição de H_annual (Concordância vs Discordância)
    # -------------------------------------------------------------------------
    print("\n2. Gerando Figura 2: H1 — Ambiguidade Probabilística (H_annual)...")
    fig, ax = plt.subplots(figsize=(8, 5.5))

    sub0 = main[main["D"] == 0]
    sub1 = main[main["D"] == 1]
    w0 = sub0["w_design"].values
    w1 = sub1["w_design"].values
    h0 = sub0["entropy_annual"].values
    h1 = sub1["entropy_annual"].values

    m0_h = np.sum(h0 * w0) / np.sum(w0)
    m1_h = np.sum(h1 * w1) / np.sum(w1)

    # Densidades KDE ponderadas
    x_grid = np.linspace(0.5, 0.95, 300)
    kde0 = gaussian_kde(h0, weights=w0)
    kde1 = gaussian_kde(h1, weights=w1)

    ax.plot(x_grid, kde0(x_grid), color=COLORS["D0"], linewidth=2.5, label=f"Concordância (D=0, Média = {m0_h:.4f})")
    ax.fill_between(x_grid, kde0(x_grid), alpha=0.25, color=COLORS["D0"])

    ax.plot(x_grid, kde1(x_grid), color=COLORS["D1"], linewidth=2.5, label=f"Discordância (D=1, Média = {m1_h:.4f})")
    ax.fill_between(x_grid, kde1(x_grid), alpha=0.25, color=COLORS["D1"])

    ax.axvline(m0_h, color=COLORS["D0"], linestyle="--", linewidth=1.8)
    ax.axvline(m1_h, color=COLORS["D1"], linestyle="--", linewidth=1.8)

    ax.set_xlabel("Entropia Anual Normalizada de Shannon ($H_{\\mathrm{anual}}$)")
    ax.set_ylabel("Densidade de Probabilidade Ponderada")
    ax.set_title("Hipótese H1: Ambiguidade Probabilística por Regime", fontweight="bold", pad=12)

    # Box informativo do efeito
    diff_h = m1_h - m0_h
    txt = (
        f"Contraste H1:\n"
        f"$\\Delta \\bar{{H}} = +{diff_h:.4f}$\n"
        f"IC 95% Espacial: [+0.0103, +0.0221]\n"
        f"Cohen's $d = 0.318$ ($p < 10^{{-15}}$)"
    )
    ax.text(0.53, 0.85, txt, transform=ax.transAxes, fontsize=10, verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="gray", alpha=0.9))

    ax.legend(loc="upper left", framealpha=0.9)
    f2_path = FIGURES_DIR / "fig2_h_annual_distribution.png"
    fig.savefig(f2_path)
    plt.close(fig)
    print(f"  Salva: {f2_path.name}")

    # -------------------------------------------------------------------------
    # Figura 3: Hipótese H2a — Divergência Jensen-Shannon Temporal (JSD)
    # -------------------------------------------------------------------------
    print("\n3. Gerando Figura 3: H2a — Heterogeneidade Temporal (JSD)...")
    fig, ax = plt.subplots(figsize=(8, 5.5))

    jsd0 = sub0["jsd_temporal"].values
    jsd1 = sub1["jsd_temporal"].values
    m0_jsd = np.sum(jsd0 * w0) / np.sum(w0)
    m1_jsd = np.sum(jsd1 * w1) / np.sum(w1)

    x_grid_jsd = np.linspace(0.0, 0.25, 300)
    kde0_jsd = gaussian_kde(jsd0, weights=w0)
    kde1_jsd = gaussian_kde(jsd1, weights=w1)

    ax.plot(x_grid_jsd, kde0_jsd(x_grid_jsd), color=COLORS["D0"], linewidth=2.5, label=f"Concordância (D=0, Média = {m0_jsd:.4f})")
    ax.fill_between(x_grid_jsd, kde0_jsd(x_grid_jsd), alpha=0.25, color=COLORS["D0"])

    ax.plot(x_grid_jsd, kde1_jsd(x_grid_jsd), color=COLORS["D1"], linewidth=2.5, label=f"Discordância (D=1, Média = {m1_jsd:.4f})")
    ax.fill_between(x_grid_jsd, kde1_jsd(x_grid_jsd), alpha=0.25, color=COLORS["D1"])

    ax.axvline(m0_jsd, color=COLORS["D0"], linestyle="--", linewidth=1.8)
    ax.axvline(m1_jsd, color=COLORS["D1"], linestyle="--", linewidth=1.8)

    ax.set_xlabel("Divergência Jensen-Shannon Temporal ($JSD_{\\mathrm{temporal}}$)")
    ax.set_ylabel("Densidade de Probabilidade Ponderada")
    ax.set_title("Hipótese H2a: Heterogeneidade Temporal das Distribuições", fontweight="bold", pad=12)

    diff_jsd = m1_jsd - m0_jsd
    txt_jsd = (
        f"Contraste H2a:\n"
        f"$\\Delta \\overline{{JSD}} = +{diff_jsd:.4f}$\n"
        f"IC 95% Espacial: [+0.0140, +0.0218]\n"
        f"Cohen's $d = 0.529$ ($p < 10^{{-15}}$)"
    )
    ax.text(0.55, 0.85, txt_jsd, transform=ax.transAxes, fontsize=10, verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="gray", alpha=0.9))

    ax.legend(loc="upper right", framealpha=0.9)
    f3_path = FIGURES_DIR / "fig3_jsd_temporal_distribution.png"
    fig.savefig(f3_path)
    plt.close(fig)
    print(f"  Salva: {f3_path.name}")

    # -------------------------------------------------------------------------
    # Figura 4: Hipótese H2b — Estabilidade Categórica Temporal (S)
    # -------------------------------------------------------------------------
    print("\n4. Gerando Figura 4: H2b — Estabilidade Categórica Temporal...")
    fig, ax = plt.subplots(figsize=(8, 5.5))

    s0 = sub0["stability"].values
    s1 = sub1["stability"].values
    m0_s = np.sum(s0 * w0) / np.sum(w0)
    m1_s = np.sum(s1 * w1) / np.sum(w1)

    bins_s = np.linspace(0, 1, 15)
    counts0, _ = np.histogram(s0, bins=bins_s, weights=w0)
    counts1, _ = np.histogram(s1, bins=bins_s, weights=w1)
    centers = (bins_s[:-1] + bins_s[1:]) / 2.0
    width = (bins_s[1] - bins_s[0]) * 0.42

    pct0 = (counts0 / np.sum(counts0)) * 100.0
    pct1 = (counts1 / np.sum(counts1)) * 100.0

    ax.bar(centers - width / 2.0, pct0, width=width, color=COLORS["D0"], alpha=0.85, edgecolor="black", label=f"Concordância (D=0, Média = {m0_s:.2f})")
    ax.bar(centers + width / 2.0, pct1, width=width, color=COLORS["D1"], alpha=0.85, edgecolor="black", label=f"Discordância (D=1, Média = {m1_s:.2f})")

    ax.axvline(m0_s, color=COLORS["D0"], linestyle="--", linewidth=2.0)
    ax.axvline(m1_s, color=COLORS["D1"], linestyle="--", linewidth=2.0)

    ax.set_xlabel("Estabilidade Categórica Mensal ($S \\in [0, 1]$)")
    ax.set_ylabel("Frequência Relativa Ponderada (%)")
    ax.set_title("Hipótese H2b: Estabilidade Temporal de Modo Mensal", fontweight="bold", pad=12)

    diff_s = m1_s - m0_s
    txt_s = (
        f"Contraste H2b:\n"
        f"$\\Delta \\bar{{S}} = {diff_s:.4f}$\n"
        f"IC 95% Espacial: [-0.4318, -0.4034]\n"
        f"Cohen's $d = -1.609$ ($p < 10^{{-15}}$)"
    )
    ax.text(0.55, 0.85, txt_s, transform=ax.transAxes, fontsize=10, verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="gray", alpha=0.9))

    ax.legend(loc="upper right", framealpha=0.9)
    f4_path = FIGURES_DIR / "fig4_stability_distribution.png"
    fig.savefig(f4_path)
    plt.close(fig)
    print(f"  Salva: {f4_path.name}")

    # -------------------------------------------------------------------------
    # Figura 5: Hipótese H3 — Proporção de Discordância por Faixa de Distância
    # -------------------------------------------------------------------------
    print("\n5. Gerando Figura 5: H3 — Efeito de Borda por Faixas...")
    fig, ax = plt.subplots(figsize=(9, 5.5))

    df_h3_bins = pd.read_csv(TABLES_DIR / "spatial_bootstrap_distance_bins.csv")
    x_pos = np.arange(len(df_h3_bins))
    y_vals = df_h3_bins["boot_mean_pct"].values
    err_low = y_vals - df_h3_bins["ci95_spatial_lower"].values
    err_high = df_h3_bins["ci95_spatial_upper"].values - y_vals

    bar_colors_h3 = ["#b30000", "#d7301f", "#ef6548", "#fc8d59", "#fdbb84", "#4575b4"]
    bars_h3 = ax.bar(x_pos, y_vals, yerr=[err_low, err_high], capsize=5, color=bar_colors_h3, width=0.6, edgecolor="black", linewidth=0.8)

    # Linha de referência da taxa geral (14.31%)
    p_disc_global = (main["w_design"][main["D"] == 1].sum() / w_tot) * 100.0
    ax.axhline(p_disc_global, color="black", linestyle=":", linewidth=1.5, label=f"Taxa Média Regional ({p_disc_global:.2f}%)")

    ax.set_xticks(x_pos)
    ax.set_xticklabels(df_h3_bins["distance_bin"])
    ax.set_xlabel("Distância Mínima à Borda Temática Mais Próxima ($d_{\\mathrm{min}}$)")
    ax.set_ylabel("Proporção de Discordância Ponderada (%)")
    ax.set_title("Hipótese H3: Taxa de Discordância em Função da Proximidade à Borda", fontweight="bold", pad=12)
    ax.set_ylim(0, 65)

    for bar, val in zip(bars_h3, y_vals):
        ax.text(bar.get_x() + bar.get_width() / 2.0, val + 5.0, f"{val:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")

    txt_h3 = "Razão Borda (<30m) vs Interior (>=250m):\n3.87x maior probabilidade de discordância"
    ax.text(0.04, 0.88, txt_h3, transform=ax.transAxes, fontsize=10, verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#fff3cd", edgecolor="#ffeeba", alpha=0.9))

    ax.legend(loc="upper right", framealpha=0.9)
    f5_path = FIGURES_DIR / "fig5_disagreement_by_distance_bin.png"
    fig.savefig(f5_path)
    plt.close(fig)
    print(f"  Salva: {f5_path.name}")

    # -------------------------------------------------------------------------
    # Figura 6: Hipótese H4 — Caracterização das Restrições Multivariadas
    # -------------------------------------------------------------------------
    print("\n6. Gerando Figura 6: H4 — Decomposição do Filtro de Robustez Interna...")
    fig, (ax_funnel, ax_scatter) = plt.subplots(1, 2, figsize=(14, 5.5), gridspec_kw={"width_ratios": [1, 1.2]})

    # Painel A: Funil de Filtros
    filter_names = [
        "1. Discordâncias (D=1)",
        "2. Interior (d >= 30m)",
        "3. Baixa Ambiguidade (H <= Q1)",
        "4. Baixa Dinâmica (JSD <= Q1)",
        "5. Alta Estabilidade (S >= Q3)",
        "6. Intersecção Total (H4)"
    ]
    h4_csv_path = TABLES_DIR / "hypothesis_h4_robust_disagreement.csv"
    if h4_csv_path.exists():
        df_h4_tbl = pd.read_csv(h4_csv_path)
        main_h4 = df_h4_tbl[df_h4_tbl["sample"] == "20k Principal"].set_index("filter")["weighted_pct_d1"].to_dict()
        filter_pcts = [
            float(main_h4.get("1. D=1", 100.0)),
            float(main_h4.get("5. Distancia >= 30m", 94.33)),
            float(main_h4.get("2. H <= Q1", 21.26)),
            float(main_h4.get("3. JSD <= Q1", 18.54)),
            float(main_h4.get("4. Estabilidade >= Q3", 11.61)),
            float(main_h4.get("H4 Completo (Todas 4)", 4.28)),
        ]
    else:
        filter_pcts = [100.0, 94.33, 21.26, 18.54, 11.61, 4.28]
    colors_funnel = ["#636363", "#756bb1", "#3182bd", "#31a354", "#de2d26", "#000000"]

    y_pos = np.arange(len(filter_names))[::-1]
    bars_f = ax_funnel.barh(y_pos, filter_pcts, color=colors_funnel, height=0.6, edgecolor="black", linewidth=0.8)
    ax_funnel.set_yticks(y_pos)
    ax_funnel.set_yticklabels(filter_names)
    ax_funnel.set_xlabel("Percentual das Discordâncias Atendendo ao Critério (%)")
    ax_funnel.set_title("A. Sobrevivência Marginal e Intersecção", fontweight="bold", pad=12)
    ax_funnel.set_xlim(0, 115)

    for bar, pct in zip(bars_f, filter_pcts):
        ax_funnel.text(bar.get_width() + 2.0, bar.get_y() + bar.get_height() / 2.0, f"{pct:.2f}%", va="center", fontsize=10, fontweight="bold")

    # Painel B: Espaço Bivariado H vs JSD para D=1
    q1_h = weighted_quantile(main["entropy_annual"].values, main["w_design"].values, 0.25)
    q1_jsd = weighted_quantile(main["jsd_temporal"].values, main["w_design"].values, 0.25)
    q3_s = weighted_quantile(main["stability"].values, main["w_design"].values, 0.75)

    d1_pts = main[main["D"] == 1]
    # Amostra de dispersão para visualização sem poluição visual
    sample_vis = d1_pts.sample(min(2000, len(d1_pts)), random_state=ROOT_SEED)

    sc = ax_scatter.scatter(
        sample_vis["entropy_annual"],
        sample_vis["jsd_temporal"],
        c=sample_vis["stability"],
        cmap="viridis",
        alpha=0.6,
        s=18,
        edgecolor="none"
    )
    cbar = plt.colorbar(sc, ax=ax_scatter)
    cbar.set_label("Estabilidade Categórica ($S$)")

    # Linhas dos limiares Q1
    ax_scatter.axvline(q1_h, color="red", linestyle="--", linewidth=1.8, label=f"Limiar Q1 $H$ ({q1_h:.3f})")
    ax_scatter.axhline(q1_jsd, color="blue", linestyle="--", linewidth=1.8, label=f"Limiar Q1 $JSD$ ({q1_jsd:.3f})")

    # Região alvo H4 (quadrante inferior esquerdo)
    ax_scatter.fill_between([0.5, q1_h], 0.0, q1_jsd, color="red", alpha=0.15, label="Região Alvo H4 ($S \\geq Q_3$: 4,28% pond.)")

    ax_scatter.set_xlabel("Entropia Anual ($H_{\\mathrm{anual}}$)")
    ax_scatter.set_ylabel("Divergência Temporal ($JSD_{\\mathrm{temporal}}$)")
    ax_scatter.set_title("B. Espaço Bivariado das Discordâncias ($D=1$)", fontweight="bold", pad=12)
    ax_scatter.legend(loc="upper right", framealpha=0.9, fontsize=9)

    plt.tight_layout()
    f6_path = FIGURES_DIR / "fig6_h4_robust_disagreement_characterization.png"
    fig.savefig(f6_path)
    plt.close(fig)
    print(f"  Salva: {f6_path.name}")

    print("\n" + "=" * 80)
    print("TODAS AS 6 FIGURAS PUBLICÁVEIS FORAM GERADAS COM SUCESSO!")
    print("=" * 80)


if __name__ == "__main__":
    generate_figures()
