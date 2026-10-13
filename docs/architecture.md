# Arquitetura e catálogo dos scripts

Os números originais dos scripts foram mantidos para conservar rastreabilidade. Caminhos científicos permanecem relativos à raiz obtida de `__file__`; não há dependência do diretório deste computador para a análise. Execute comandos na raiz. Scripts GEE usam `EE_PROJECT` quando definido e, por padrão, o projeto original `dynamicworld-x-mapbiomas`. `.env.example` é um exemplo e não é carregado automaticamente.

## Pipeline GEE preservado

| Script em `src/gee/` | Entradas | Saídas/função | Dependências e motivo |
|---|---|---|---|
| `01_check_access.py` | Conta/projeto GEE e catálogos | Consulta bandas e disponibilidade DW/MB; pode solicitar autenticação | earthengine-api; valida acesso no computador novo. Alterações preexistentes 2025/MapBiomas preservadas |
| `02_boundary.py` | XLS IBGE MATOPIBA 2021; API malhas 2025 | Lista municipal, contornos e metadados operacionais | requests, pandas, xlrd, geopandas; procedência da geometria. Não rodar para sobrescrever a geometria congelada |
| `dw_annual.py` | GeoJSON suporte 5 km; datas mensais; DW/MB | Funções do composto anual, crosswalk, grade e distâncias | earthengine-api; único núcleo científico anual reutilizado |
| `submit_canonical_batch_exports.py` | Estados, manifesto de lotes final e núcleo anual | Exportações GEE/Drive por lote; registro de tarefas | earthengine-api, pandas, shapely; implementação definitiva do censo em lotes |
| `monitor_and_process_batches.py` | Tarefas/Drive e CSVs de lotes | Censo por fatia, sumário, quadro, cotas e alocação | earthengine-api, google-auth/API client, pandas; consolidação final com cobertura positiva |
| `14_regenerate_master_sample.py` | Quadro/cotas/alocação; catálogos e núcleo anual | Pontos 40k, subconjunto 20k, probabilidades e pesos, checkpoint, auditoria do desenho | earthengine-api, numpy, pandas, shapely; sorteio e aninhamento finais |
| `11_extract_analytical_dataset.py` | Pontos e stack anual, série histórica MB | Extração anual canônica, distâncias, concorrentes; RAW mensal inicial | earthengine-api, numpy, pandas, shapely, pyarrow; fornece variáveis anuais indispensáveis. Deve ser seguido pelo script 12 |
| `12_extract_harmonized_bilinear_monthly.py` | Anual inicial, coordenadas, datas, DW, grade MB | Mensal harmonizado e atualização de S/JSD nos parquets anuais | earthengine-api, numpy, pandas, scipy, pyarrow; correção temporal definitiva |
| `16_dw_partition_invariance_audit.py` | Núcleo e pontos/materializações | Evidência de dependência de partição e referência de suporte fixo | GEE + stack científico; auditoria que sustenta a escolha do domínio |
| `17_test_domain_convergence.py` | Contornos 1/5/10 km e núcleo | Auditoria de convergência do suporte | GEE + stack científico; justifica suporte 5 km |
| `20_test_pagination_invariance.py` | Pontos e raster canônico fixo | Comparação da extração por fatia, estado e domínio; CSV de auditoria | GEE + numpy/pandas; valida paginação sem alterar o raster-fonte |

Auditorias GEE podem gravar seus próprios resultados e consumir cotas. Elas são código de procedência/reexecução futura; não integram a verificação offline segura. Os três testes finais foram preservados pela função científica demonstrada, não apenas pelo nome. Testes de desempenho, protótipos Balsas e alternativas do censo foram retirados da seleção operacional e conservados no ZIP de fontes.

O antigo `19_process_canonical_wall_to_wall.py` duplica a consolidação para uma exportação monolítica; o fluxo final é o monitor de lotes. Geradores/splitters de lotes eram ajustes de falhas específicas. O manifesto final já persiste as subdivisões usadas. Esses scripts estão no arquivo de procedência e não são etapas obrigatórias da nova documentação. O script 11 permanece porque sua extração anual/histórica é necessária mesmo tendo uma mensal posteriormente corrigida.

## Análise preservada

Todos leem `data/processed/samples_annual.parquet`, com pesos materializados, e escrevem em `tables/` ou `figures/`. Necessitam numpy/pandas/pyarrow; dependências adicionais abaixo. **Executar somente em cópia de trabalho separada.**

| Script em `src/analysis/` | Saídas | Dependências/função |
|---|---|---|
| `02_weighted_descriptive_analysis.py` | `descriptive_*.csv` | Proporções por desenho/área e descrição dos indicadores |
| `03_hypothesis_tests_h1_h4.py` | `hypothesis_*.csv` | scipy; testes, faixas de distância e filtros H4 |
| `04_weighted_regression_model.py` | `regression_*.csv` | statsmodels; GLM ponderado, comparação e colinearidade |
| `05_spatial_block_bootstrap.py` | `spatial_*` e OR escalonados | statsmodels, scipy, pyproj; semivariograma, bootstrap e IC espaciais |
| `06_robustness_analysis.py` | `robustness_*.csv` | Cenários 40k, crosswalk estrito e série MB estável |
| `07_generate_publication_figures.py` | Seis gráficos históricos `fig1`–`fig6` | matplotlib/scipy; gerador usado no desenvolvimento, preservado para auditoria. Há anotações legadas; não é autoridade editorial do artigo final |
| `08_master_h1_h4_runner.py` | Executa 02→07 e verifica presença | subprocess/stdlib; sequência histórica completa. A verificação de presença não comprova correção das anotações dos gráficos |

## Ferramentas de manutenção

`scripts/verify_release.py` usa stdlib para hashes, tamanhos, syntax AST e CRC dos ZIPs. `--data` adiciona pandas/pyarrow e confere schemas, contagens, identificadores e pertencimento sem recalcular estatísticas. Não importa os scripts GEE, muitos dos quais inicializam o serviço no topo do módulo.

`scripts/export_manuscript.py` usa stdlib e LibreOffice encontrado no PATH/argumento. Lê o DOCX final; exige diretório de saída separado e recusa sobrescrever um PDF existente. Não regenera gráficos, ajusta modelos ou modifica o manuscrito. A renderização futura pode variar entre versões do editor/fontes.

`docs/provenance/source_audit.json` registra descrições, imports e referências de I/O dos scripts examinados. `development_sources.zip` guarda suas versões substituídas; scripts editoriais ali dependem de caminhos históricos/renderer Codex e são evidência, não a interface portátil de exportação. Não execute os protótipos extraídos sobre o clone congelado.

## Contratos entre pastas

`config/` documenta escolhas; os scripts antigos não são um sistema único que consome todos os YAMLs. Há constantes no código. `config/release.yaml` reconcilia o estado final sem alterar snapshots históricos. `data/reference/` fixa o domínio e datas; `data/processed/` fixa o censo e a população analítica; `tables/` fixa a inferência; `paper/` fixa a entrega editorial. `figures/final_figure1.png` e `final_figure2.png` são cópias byte a byte das figuras incorporadas no artigo, distintas das seis materializações anteriores.
