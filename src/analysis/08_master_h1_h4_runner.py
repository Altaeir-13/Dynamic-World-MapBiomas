"""
08_master_h1_h4_runner.py — Orquestrador Mestre de Análise e Inferência (Checkpoint 4)
=====================================================================================
Executa em sequência reprodutível todos os módulos de análise estatística, espacial
e visual das hipóteses H1–H4 sobre a população analítica congelada:
  1. 02_weighted_descriptive_analysis.py
  2. 03_hypothesis_tests_h1_h4.py
  3. 04_weighted_regression_model.py
  4. 05_spatial_block_bootstrap.py
  5. 06_robustness_analysis.py
  6. 07_generate_publication_figures.py

Valida a existência e integridade de todas as tabelas e figuras produzidas.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

ANALYSIS_DIR = BASE_DIR / "src" / "analysis"
TABLES_DIR = BASE_DIR / "tables"
FIGURES_DIR = BASE_DIR / "figures"

SCRIPTS = [
    "02_weighted_descriptive_analysis.py",
    "03_hypothesis_tests_h1_h4.py",
    "04_weighted_regression_model.py",
    "05_spatial_block_bootstrap.py",
    "06_robustness_analysis.py",
    "07_generate_publication_figures.py",
]

EXPECTED_TABLES = [
    "descriptive_regime_proportions.csv",
    "descriptive_state_proportions.csv",
    "descriptive_continuous_indicators.csv",
    "descriptive_robust_40k_comparison.csv",
    "hypothesis_h1_results.csv",
    "hypothesis_h2_results.csv",
    "hypothesis_h3_distance_bins.csv",
    "hypothesis_h4_robust_disagreement.csv",
    "regression_collinearity_diagnostics.csv",
    "regression_logistic_primary_model.csv",
    "regression_logistic_rescaled_odds_ratios.csv",
    "regression_model_comparison.csv",
    "spatial_semivariogram_parameters.csv",
    "spatial_bootstrap_contrasts.csv",
    "spatial_bootstrap_distance_bins.csv",
    "spatial_bootstrap_logistic_model.csv",
    "spatial_bootstrap_block_sensitivity.csv",
    "robustness_r1_sample_size_comparison.csv",
    "robustness_r2_strict_crosswalk_comparison.csv",
    "robustness_r3_mapbiomas_stability_subset.csv",
    "robustness_comprehensive_summary.csv",
]

EXPECTED_FIGURES = [
    "fig1_composition_regimes.png",
    "fig2_h_annual_distribution.png",
    "fig3_jsd_temporal_distribution.png",
    "fig4_stability_distribution.png",
    "fig5_disagreement_by_distance_bin.png",
    "fig6_h4_robust_disagreement_characterization.png",
]


def main():
    print("=" * 80)
    print("ORQUESTRADOR MESTRE: EXECUÇÃO DO CHECKPOINT 4 (H1–H4)")
    print("=" * 80)

    python_exe = sys.executable
    t_start = time.time()

    for script_name in SCRIPTS:
        script_path = ANALYSIS_DIR / script_name
        print(f"\n>>> Executando {script_name}...")
        t0 = time.time()
        res = subprocess.run([python_exe, str(script_path)], capture_output=True, text=True, cwd=str(BASE_DIR))
        if res.returncode != 0:
            print(f"ERRO na execução de {script_name}:")
            print(res.stderr)
            sys.exit(1)
        print(f"    Concluído em {time.time() - t0:.1f}s.")

    print("\n" + "=" * 80)
    print("VALIDANDO ARTEFATOS PRODUZIDOS NO CHECKPOINT 4")
    print("=" * 80)

    print("\n1. Verificando Tabelas CSV:")
    for t_name in EXPECTED_TABLES:
        t_path = TABLES_DIR / t_name
        assert t_path.exists(), f"Tabela ausente: {t_path}"
        sz_kb = t_path.stat().st_size / 1024.0
        print(f"  [OK] {t_name:<42} ({sz_kb:6.1f} KB)")

    print("\n2. Verificando Figuras Científicas (PNG 300 DPI):")
    for f_name in EXPECTED_FIGURES:
        f_path = FIGURES_DIR / f_name
        assert f_path.exists(), f"Figura ausente: {f_path}"
        sz_kb = f_path.stat().st_size / 1024.0
        print(f"  [OK] {f_name:<42} ({sz_kb:6.1f} KB)")

    print(f"\nTempo total de execução do Checkpoint 4: {time.time() - t_start:.1f}s.")
    print("=" * 80)
    print("SUÍTE COMPLETA DO CHECKPOINT 4 EXECUTADA E VERIFICADA COM SUCESSO!")
    print("=" * 80)


if __name__ == "__main__":
    main()
