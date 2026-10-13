# Tabelas e auditorias preservadas

## Resultados finais corrigidos

`manuscript_results_manifest.csv` cataloga 21 tabelas estatísticas finais. As famílias são:

- `descriptive_*`: regimes, estados, indicadores contínuos e comparação 40k.
- `hypothesis_h1_results`, `hypothesis_h2_results`, `hypothesis_h3_distance_bins`, `hypothesis_h4_robust_disagreement`: H1–H4. H4 final tem 207 e 404 casos.
- `regression_*`: coeficientes, OR escalonados/IC, especificações e colinearidade.
- `spatial_semivariogram_parameters` e `spatial_bootstrap_*`: bloco 30km, contrastes, faixas H3, coeficientes e sensibilidade 10/20/40km.
- `robustness_*`: 40k, crosswalk estrito e subset MB estável.

Veja [resultados](../docs/results.md) para métricas e estimandos. O IC espacial é primário; não misturar proporções por área/pixels nem censo/amostra.

## Desenho e procedência

`sampling_frame_10m.csv` é o quadro final por subestrato (728 combinações registradas, das quais 410 têm população positiva). `sampling_quotas.csv` e `slice_sampling_allocation_final.csv` são cotas/alocação final. `slice_sampling_design_audit.csv` e `zero_inclusion_substrata_audit.csv` documentam o desenho e a correção de pi=0. `canonical_w2w_batch_manifest.csv` fixa os lotes e subdivisões realmente usados; `canonical_w2w_batch_tasks.csv` registra IDs/estados históricos e não concede acesso a tarefas em outra conta.

`dw_partition_invariance_audit`, `domain_convergence_audit`, `pagination_invariance_audit`, `boundary_vs_raster_area_comparison`, `dw_valid_months_area` e `dw_annual_identity_diagnostic` são evidências do suporte/cobertura; `pilot_evaluation_summary` e `pilot2_evaluation_summary` são diagnósticos controlados da correção, não estimativas principais para MATOPIBA.

Os resultados/alocações explicitamente invalidados estão no ZIP histórico, fora desta árvore pública. Foram identificados por relatórios, conteúdo e relação com o pipeline, não apenas pelo nome.

`manuscript_results_checksums.sha256` confere os 33 arquivos corrigidos do manifesto; foi preservado. `checkpoint_3d_checksums.sha256` é um registro anterior à correção mensal e seus hashes de dados temporais são históricos. O registro ampliado da organização é `docs/provenance/release_checksums.csv`. Nenhum manifesto científico original foi regenerado nesta tarefa.
