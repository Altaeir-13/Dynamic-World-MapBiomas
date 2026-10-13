# Materializações finais

Use `samples_annual.parquet` e `dw_monthly.parquet` corrigidos. `master_sampling_points.csv` preserva as coordenadas, subconjunto principal, inclusão e pesos. `canonical_wall_to_wall_by_slice.csv`, `wall_to_wall_summary.csv` e `batches/*.csv` registram o censo canônico.

Arquivos PRE_ZERO_PI_FIX, SLICE_DEPENDENT_INVALID, checkpoints e RAW locais não integram o clone público. Os RAW necessários à auditoria da mudança temporal estão em `../audit/`. Consulte `docs/data.md` para origem, volume e limites de regeneração.
