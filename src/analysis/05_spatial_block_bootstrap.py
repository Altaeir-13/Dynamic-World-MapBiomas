"""
05_spatial_block_bootstrap.py — Incerteza Espacial via Semivariograma e Block Bootstrap
========================================================================================
Procedimento pré-registrado de incerteza espacial:
  1. Amostra principal de 20k projetada em CRS métrico (EPSG:5880).
  2. Semivariograma empírico do indicador de discordância D.
  3. Ajuste de modelo exponencial: alcance prático (95% do sill) arredondado para múltiplo de 5 km superior (30 km).
  4. Spatial Block Bootstrap: 1.999 replicações, seed=25.
  5. Intervalos de confiança de 95% (percentis 2.5% e 97.5%) para os contrastes H1–H3 e modelo logístico.
  6. Análise de sensibilidade ao tamanho do bloco: 10 km, 20 km, 40 km.

Gera:
  - tables/spatial_semivariogram_parameters.csv
  - tables/spatial_bootstrap_contrasts.csv
  - tables/spatial_bootstrap_distance_bins.csv
  - tables/spatial_bootstrap_logistic_model.csv
  - tables/spatial_bootstrap_block_sensitivity.csv
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.optimize import curve_fit
from scipy.spatial.distance import pdist
import statsmodels.api as sm

DATA_PARQUET = BASE_DIR / "data" / "processed" / "samples_annual.parquet"
TABLES_DIR = BASE_DIR / "tables"
TABLES_DIR.mkdir(parents=True, exist_ok=True)

N_BOOT = 1999
ROOT_SEED = 25


def exp_semivariogram(h: np.ndarray, c0: float, c: float, a: float) -> np.ndarray:
    """Modelo de semivariograma exponencial: gamma(h) = c0 + c * (1 - exp(-3 * h / a))."""
    return c0 + c * (1.0 - np.exp(-3.0 * h / a))


def fit_empirical_semivariogram(main: pd.DataFrame) -> tuple[dict[str, float], int]:
    print("\n1. Ajustando Semivariograma Empírico do Indicador D...")
    coords = np.column_stack([main["x"].values, main["y"].values])
    d_vals = main["D"].values.astype(float)

    # Subamostra reprodutível de 6.000 pontos para cálculo exato de 18M pares
    rng = np.random.default_rng(ROOT_SEED)
    sub_idx = rng.choice(len(main), 6000, replace=False)
    sub_coords = coords[sub_idx]
    sub_d = d_vals[sub_idx]

    dists = pdist(sub_coords)
    diffs = pdist(sub_d[:, None], metric="sqeuclidean") / 2.0

    # Bins de 5 km até 200 km
    max_dist = 200000.0
    bin_size = 5000.0
    bins = np.arange(0, max_dist + bin_size, bin_size)
    bin_centers = (bins[:-1] + bins[1:]) / 2.0

    bin_indices = np.digitize(dists, bins) - 1
    gamma = np.zeros(len(bin_centers))
    counts = np.zeros(len(bin_centers))
    for i in range(len(bin_centers)):
        m = (bin_indices == i)
        counts[i] = np.sum(m)
        if counts[i] > 0:
            gamma[i] = np.mean(diffs[m])

    # Ajuste não-linear
    p0 = [0.05, float(np.var(sub_d) - 0.05), 50000.0]
    bounds = ([0.0, 0.0, 1000.0], [0.5, 0.5, 300000.0])
    popt, _ = curve_fit(exp_semivariogram, bin_centers, gamma, p0=p0, bounds=bounds)
    c0_fit, c_fit, a_fit = popt
    total_sill = c0_fit + c_fit
    practical_range_km = a_fit / 1000.0

    # Regra pré-registrada:
    # Arredondar para cima ao múltiplo de 5 km mais próximo, limitado entre 5 e 100 km
    block_size_km = int(np.ceil(practical_range_km / 5.0) * 5.0)
    block_size_km = min(100, max(5, block_size_km))

    semiv_params = {
        "nugget_c0": float(c0_fit),
        "partial_sill_c": float(c_fit),
        "total_sill": float(total_sill),
        "practical_range_km": float(practical_range_km),
        "selected_block_size_km": float(block_size_km),
        "subsample_n": 6000,
        "n_pairs_evaluated": int(len(dists)),
    }

    df_semiv = pd.DataFrame([semiv_params])
    df_semiv.to_csv(TABLES_DIR / "spatial_semivariogram_parameters.csv", index=False)
    print(f"  Nugget (c0):            {c0_fit:.4f}")
    print(f"  Sill Parcial (c):       {c_fit:.4f}")
    print(f"  Sill Total:             {total_sill:.4f}")
    print(f"  Alcance Prático (a):    {practical_range_km:.2f} km")
    print(f"  Tamanho do Bloco Eleito: {block_size_km} km")

    return semiv_params, block_size_km


def partition_into_blocks(main: pd.DataFrame, block_size_km: int) -> list[np.ndarray]:
    block_size_m = block_size_km * 1000.0
    bx = np.floor(main["x"].values / block_size_m).astype(int)
    by = np.floor(main["y"].values / block_size_m).astype(int)
    block_keys = [f"{x}_{y}" for x, y in zip(bx, by)]

    unique_keys = np.unique(block_keys)
    key_to_indices = {k: [] for k in unique_keys}
    for idx, k in enumerate(block_keys):
        key_to_indices[k].append(idx)

    return [np.array(indices, dtype=int) for indices in key_to_indices.values()]


def run_spatial_bootstrap():
    print("=" * 80)
    print("INCERTEZA ESPACIAL: SEMIVARIOGRAMA E BLOCK BOOTSTRAP (CHECKPOINT 4)")
    print("=" * 80)

    df = pd.read_parquet(DATA_PARQUET)
    main = df[df["main_sample"] == 1].copy()
    main["D"] = main["regime"].isin(["AN", "NA"]).astype(int)
    main["w"] = pd.to_numeric(main["design_weight_main"])

    # Projeção métrica EPSG:5880
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:5880", always_xy=True)
    x, y = transformer.transform(main["lon"].values, main["lat"].values)
    main["x"] = x
    main["y"] = y

    # 1. Ajuste do Semivariograma e Escolha do Bloco
    semiv_params, primary_block_km = fit_empirical_semivariogram(main)

    # 2. Particionamento em Blocos (30 km)
    block_list = partition_into_blocks(main, primary_block_km)
    n_blocks = len(block_list)
    print(f"\n2. Particionamento Espacial ({primary_block_km} km): {n_blocks} blocos ativos.")

    # Preparação de Matrizes Vetorizadas
    y_h = main["entropy_annual"].values
    y_jsd = main["jsd_temporal"].values
    y_s = main["stability"].values
    d_arr = main["D"].values
    w_arr = main["w"].values
    dist_arr = main["distance_edge_min_m"].values

    # Faixas de Distância H3
    bins = [0, 10, 30, 60, 100, 250, np.inf]
    labels = ["0–10 m", "10–30 m", "30–60 m", "60–100 m", "100–250 m", ">=250 m"]
    bin_codes = np.digitize(dist_arr, bins, right=False) - 1

    # Matriz de Regressão Logística
    state_dummies = pd.get_dummies(main["state"], drop_first=True, dtype=float)
    state_names = list(state_dummies.columns)
    X_reg = np.column_stack([
        np.ones(len(main)),
        y_h,
        y_jsd,
        y_s,
        dist_arr,
        state_dummies.values
    ])
    term_names = ["Intercept", "entropy_annual", "jsd_temporal", "stability", "distance_edge_min_m"] + [f"state_{s}" for s in state_names]

    # Arrays de Armazenamento das 1.999 Replicações
    boot_diff_h = np.zeros(N_BOOT)
    boot_diff_jsd = np.zeros(N_BOOT)
    boot_diff_s = np.zeros(N_BOOT)
    boot_p_disc = np.zeros(N_BOOT)
    boot_dist_bins = {lab: np.zeros(N_BOOT) for lab in labels}
    boot_reg_coefs = np.zeros((N_BOOT, X_reg.shape[1]))

    print(f"\n3. Executando Spatial Block Bootstrap ({N_BOOT} replicações, seed={ROOT_SEED})...")
    rng = np.random.default_rng(ROOT_SEED)
    t0 = time.time()

    for r in range(N_BOOT):
        # Reamostragem de blocos com reposição
        sampled_block_idx = rng.choice(n_blocks, n_blocks, replace=True)
        idx_boot = np.concatenate([block_list[b] for b in sampled_block_idx])

        w_b = w_arr[idx_boot]
        d_b = d_arr[idx_boot]
        h_b = y_h[idx_boot]
        jsd_b = y_jsd[idx_boot]
        s_b = y_s[idx_boot]
        b_codes = bin_codes[idx_boot]

        w0 = w_b[d_b == 0]
        w1 = w_b[d_b == 1]
        sum_w0 = np.sum(w0)
        sum_w1 = np.sum(w1)
        sum_wtot = sum_w0 + sum_w1

        # Taxa geral de discordância
        boot_p_disc[r] = (sum_w1 / sum_wtot) * 100.0

        # Contrastes H1, H2
        m0_h = np.sum(h_b[d_b == 0] * w0) / sum_w0
        m1_h = np.sum(h_b[d_b == 1] * w1) / sum_w1
        boot_diff_h[r] = m1_h - m0_h

        m0_jsd = np.sum(jsd_b[d_b == 0] * w0) / sum_w0
        m1_jsd = np.sum(jsd_b[d_b == 1] * w1) / sum_w1
        boot_diff_jsd[r] = m1_jsd - m0_jsd

        m0_s = np.sum(s_b[d_b == 0] * w0) / sum_w0
        m1_s = np.sum(s_b[d_b == 1] * w1) / sum_w1
        boot_diff_s[r] = m1_s - m0_s

        # Faixas de Distância H3
        for b_idx, lab in enumerate(labels):
            m_bin = (b_codes == b_idx)
            w_bin = w_b[m_bin]
            d_bin = d_b[m_bin]
            if len(w_bin) > 0 and np.sum(w_bin) > 0:
                boot_dist_bins[lab][r] = (np.sum(w_bin[d_bin == 1]) / np.sum(w_bin)) * 100.0
            else:
                boot_dist_bins[lab][r] = np.nan

        # Regressão Logística
        X_b = X_reg[idx_boot]
        w_norm_b = w_b / np.mean(w_b)
        try:
            mod_b = sm.GLM(d_b, X_b, family=sm.families.Binomial(), freq_weights=w_norm_b).fit(maxiter=15)
            boot_reg_coefs[r, :] = mod_b.params
        except Exception:
            boot_reg_coefs[r, :] = np.nan

        if (r + 1) % 500 == 0 or (r + 1) == N_BOOT:
            print(f"  [{r + 1:4d}/{N_BOOT}] replicações concluídas em {time.time() - t0:5.1f}s...")

    print(f"Bootstrap espacial concluído com sucesso em {time.time() - t0:.1f}s.")

    # 4. Compilação dos Resultados dos Contrastes
    contrasts_summary = [
        {
            "contrast": "H1: Delta_H_annual (D=1 - D=0)",
            "boot_mean": float(np.mean(boot_diff_h)),
            "boot_se": float(np.std(boot_diff_h, ddof=1)),
            "ci95_spatial_lower": float(np.percentile(boot_diff_h, 2.5)),
            "ci95_spatial_upper": float(np.percentile(boot_diff_h, 97.5)),
        },
        {
            "contrast": "H2a: Delta_JSD_temporal (D=1 - D=0)",
            "boot_mean": float(np.mean(boot_diff_jsd)),
            "boot_se": float(np.std(boot_diff_jsd, ddof=1)),
            "ci95_spatial_lower": float(np.percentile(boot_diff_jsd, 2.5)),
            "ci95_spatial_upper": float(np.percentile(boot_diff_jsd, 97.5)),
        },
        {
            "contrast": "H2b: Delta_Stability (D=1 - D=0)",
            "boot_mean": float(np.mean(boot_diff_s)),
            "boot_se": float(np.std(boot_diff_s, ddof=1)),
            "ci95_spatial_lower": float(np.percentile(boot_diff_s, 2.5)),
            "ci95_spatial_upper": float(np.percentile(boot_diff_s, 97.5)),
        },
        {
            "contrast": "Taxa Geral de Discordância (%)",
            "boot_mean": float(np.mean(boot_p_disc)),
            "boot_se": float(np.std(boot_p_disc, ddof=1)),
            "ci95_spatial_lower": float(np.percentile(boot_p_disc, 2.5)),
            "ci95_spatial_upper": float(np.percentile(boot_p_disc, 97.5)),
        },
    ]
    df_contrasts = pd.DataFrame(contrasts_summary)
    df_contrasts.to_csv(TABLES_DIR / "spatial_bootstrap_contrasts.csv", index=False)
    print("\n--- Intervalos de Confiança por Bootstrap Espacial (Contrastes H1–H2) ---")
    print(df_contrasts.to_string(index=False))

    # 5. Compilação das Faixas de Distância H3
    bins_summary = []
    for lab in labels:
        vals = boot_dist_bins[lab][~np.isnan(boot_dist_bins[lab])]
        bins_summary.append({
            "distance_bin": lab,
            "boot_mean_pct": float(np.mean(vals)),
            "boot_se_pct": float(np.std(vals, ddof=1)),
            "ci95_spatial_lower": float(np.percentile(vals, 2.5)),
            "ci95_spatial_upper": float(np.percentile(vals, 97.5)),
        })
    df_boot_bins = pd.DataFrame(bins_summary)
    df_boot_bins.to_csv(TABLES_DIR / "spatial_bootstrap_distance_bins.csv", index=False)
    print("\n--- Intervalos Espaciais por Faixa de Distância H3 ---")
    print(df_boot_bins.to_string(index=False))

    # 6. Compilação da Regressão Logística Espacial
    reg_summary = []
    valid_reg_mask = ~np.isnan(boot_reg_coefs[:, 0])
    valid_coefs = boot_reg_coefs[valid_reg_mask, :]
    for i, term in enumerate(term_names):
        b_vals = valid_coefs[:, i]
        or_vals = np.exp(b_vals)
        reg_summary.append({
            "term": term,
            "boot_coef_mean": float(np.mean(b_vals)),
            "boot_coef_se": float(np.std(b_vals, ddof=1)),
            "ci95_coef_lower": float(np.percentile(b_vals, 2.5)),
            "ci95_coef_upper": float(np.percentile(b_vals, 97.5)),
            "boot_or_median": float(np.median(or_vals)),
            "ci95_or_lower": float(np.percentile(or_vals, 2.5)),
            "ci95_or_upper": float(np.percentile(or_vals, 97.5)),
        })
    df_boot_reg = pd.DataFrame(reg_summary)
    df_boot_reg.to_csv(TABLES_DIR / "spatial_bootstrap_logistic_model.csv", index=False)
    print("\n--- Modelo Logístico com Incerteza por Bootstrap Espacial ---")
    print(df_boot_reg[["term", "boot_coef_mean", "ci95_coef_lower", "ci95_coef_upper", "boot_or_median", "ci95_or_lower", "ci95_or_upper"]].to_string(index=False))

    # 7. Sensibilidade ao Tamanho do Bloco (10 km, 20 km, 40 km)
    print("\n4. Avaliando Sensibilidade ao Tamanho do Bloco (10 km, 20 km, 40 km)...")
    sens_sizes = [10, 20, 40]
    sens_rows = []
    for b_sz in sens_sizes:
        b_list_s = partition_into_blocks(main, b_sz)
        n_bl_s = len(b_list_s)
        rng_s = np.random.default_rng(ROOT_SEED)
        diff_h_s = np.zeros(500)
        diff_s_s = np.zeros(500)
        p_disc_s = np.zeros(500)
        for r in range(500):
            samp = rng_s.choice(n_bl_s, n_bl_s, replace=True)
            idx_s = np.concatenate([b_list_s[b] for b in samp])
            w_s = w_arr[idx_s]
            d_s = d_arr[idx_s]
            h_s = y_h[idx_s]
            st_s = y_s[idx_s]

            w0_s = w_s[d_s == 0]
            w1_s = w_s[d_s == 1]
            sum_w0_s = np.sum(w0_s)
            sum_w1_s = np.sum(w1_s)

            p_disc_s[r] = (sum_w1_s / (sum_w0_s + sum_w1_s)) * 100.0
            diff_h_s[r] = (np.sum(h_s[d_s == 1] * w1_s) / sum_w1_s) - (np.sum(h_s[d_s == 0] * w0_s) / sum_w0_s)
            diff_s_s[r] = (np.sum(st_s[d_s == 1] * w1_s) / sum_w1_s) - (np.sum(st_s[d_s == 0] * w0_s) / sum_w0_s)

        sens_rows.append({
            "block_size_km": b_sz,
            "n_blocks": n_bl_s,
            "disc_rate_se": float(np.std(p_disc_s, ddof=1)),
            "disc_rate_ci95": f"[{np.percentile(p_disc_s, 2.5):.2f}%, {np.percentile(p_disc_s, 97.5):.2f}%]",
            "delta_h_se": float(np.std(diff_h_s, ddof=1)),
            "delta_h_ci95": f"[{np.percentile(diff_h_s, 2.5):.4f}, {np.percentile(diff_h_s, 97.5):.4f}]",
            "delta_stab_se": float(np.std(diff_s_s, ddof=1)),
            "delta_stab_ci95": f"[{np.percentile(diff_s_s, 2.5):.4f}, {np.percentile(diff_s_s, 97.5):.4f}]",
        })

    df_sens = pd.DataFrame(sens_rows)
    df_sens.to_csv(TABLES_DIR / "spatial_bootstrap_block_sensitivity.csv", index=False)
    print("\n--- Sensibilidade ao Tamanho do Bloco Espacial ---")
    print(df_sens.to_string(index=False))

    print("\n" + "=" * 80)
    print("ANÁLISE DE INCERTEZA ESPACIAL CONCLUÍDA COM SUCESSO!")
    print("=" * 80)


if __name__ == "__main__":
    run_spatial_bootstrap()
