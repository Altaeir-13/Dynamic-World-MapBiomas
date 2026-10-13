# Dados históricos RAW

Os dois parquets `legacy_raw_*` são cópias byte a byte dos consolidados anteriores à extração mensal bilinear. Preservam a comparação com os resultados corrigidos e a procedência da mudança de S/JSD. **Não usar como entradas da análise final.**

A colocação em `data/audit/` distingue sua função dos dois parquets finais em `data/processed/`. Hashes e caminhos originais/remotos estão nos manifestos de preservação e release.
