# Dados, acesso, volumes e direitos

## Fontes externas

| Fonte | Identificador congelado/acesso | Uso |
|---|---|---|
| Dynamic World V1 | `GOOGLE/DYNAMICWORLD/V1`; `[2025-01-01,2026-01-01)` | Nove probabilidades, composições diária/mensal/anual |
| MapBiomas Cobertura 10m Coleção 4 | `projects/mapbiomas-public/assets/brazil/lulc_10m/collection4/mapbiomas_10m_collection4_coverage_v1`; `classification_2025` | Comparação binária 2025; série 2017–2025 em robustez |
| IBGE MATOPIBA 2021 | [MATOPIBA_2021.xls](https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/MATOPIBA/2021/MATOPIBA_2021.xls) | Lista de 337 municípios |
| IBGE malhas municipais 2025 | `https://servicodados.ibge.gov.br/api/v3/malhas/estados/{UF}?intrarregiao=municipio&formato=application/vnd.geo+json&qualidade=maxima&data=2025`; UF 17/21/22/29 | Contorno operacional e dissolução por estado |

A [documentação oficial DW](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1) declara licença CC BY 4.0 e exige atribuição ao Dynamic World Project, produzido por Google em parceria com National Geographic Society e World Resources Institute. A [página oficial MapBiomas 10m](https://brasil.mapbiomas.org/iniciativas-e-produtos/cobertura-e-uso-da-terra/cobertura-10m/cobertura/) identifica Coleção 4/2017–2025, asset, legenda e uso aberto com referência sob CC BY 4.0. Consultadas em 13/10/2026; não se transfere a licença do serviço GEE para seus dados.

As geometrias derivam dos dados públicos IBGE e devem citar IBGE, lista MATOPIBA 2021 e malha 2025. Consulte [malha municipal e suas informações técnicas/legais](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/15774-mlhas.html). Não atribuímos ao IBGE uma licença Creative Commons não verificada. Contornos de finalidade estatística não são instrumentos para delimitação legal de propriedade. Não se redistribuem os PDFs de normas do evento cuja licença não foi comprovada; seus links oficiais constam na procedência editorial.

## Incluídos no GitHub

| Artefato | Formato/volume lógico | Bytes originais | Papel |
|---|---|---:|---|
| `data/processed/samples_annual.parquet` | 40.000 pontos, 51 colunas | 7.958.753 | Amostra anual final com probabilidades, indicadores temporais corrigidos, pesos, regime e distâncias |
| `data/processed/dw_monthly.parquet` | 480.000 ponto-mês, 15 colunas | 34.847.652 | Série mensal bilinear corrigida, validade/contagens/soma bruta |
| `data/processed/master_sampling_points.csv` | 40.000 coordenadas, flags e pesos | 8.075.891 | Registro definitivo da amostra e pertencimento ao subset principal |
| `data/processed/canonical_wall_to_wall_by_slice.csv` | 182 fatias | 927.664 | Censo materializado, contagens, áreas e cobertura mensal |
| `data/processed/wall_to_wall_summary.csv` | MATOPIBA + quatro estados | 1.887 | Síntese censitária |
| `data/processed/batches/*.csv` | 21 lotes finais, 182 fatias no total | 938.065 no total | Exportações persistidas; auditoria da consolidação sem Drive |
| `data/reference/matopiba_boundary.geojson` | Contorno dissolvido | 1.236.998 | Geometria congelada, hash científico |
| `data/reference/matopiba_municipalities.csv` | 337 municípios | 11.993 | Códigos IBGE e identificação do domínio |
| `data/reference/matopiba_states.geojson` | Quatro geometrias dissolvidas | 673.886 | Subdomínios estaduais |
| `data/reference/matopiba_support_{1,5,10}km.geojson` | Suportes espaciais | Manifesto de hashes | Domínio 5 km e auditoria de convergência |
| `data/reference/dw_2025_monthly_dates.json` | Datas por mês | 5.686 | Universo temporal consultado no suporte canônico |
| `data/audit/legacy_raw_dw_monthly.parquet` | Mensal RAW, substituído | 33.863.705 | Comparação histórica, jamais entrada da análise final |
| `data/audit/legacy_raw_samples_annual.parquet` | Anual RAW, substituído | 7.957.392 | Auditoria da correção de S/JSD |

O CSV anual final de 24.847.888 bytes não é duplicado no repositório público porque o parquet preserva os mesmos dados finais com tipos e menor tamanho. A recuperação tabular pode ser feita com pandas em **outro diretório**: `pd.read_parquet('data/processed/samples_annual.parquet').to_csv('annual_copy.csv', index=False)`. Isso regenera uma representação, não uma análise; bytes do CSV podem variar com serialização.

Algumas colunas da amostra principal, inclusive `design_weight_main`, estão materializadas como texto para acomodar registros fora do subset. Os scripts de análise e o verificador usam `pd.to_numeric` no subconjunto elegível. Essa conversão em memória faz parte da leitura do schema; o parquet original não foi regravado.

Todos os arquivos selecionados têm menos de 50 MiB. Não há necessidade de Git LFS ou upload de rasters nacionais. O manifesto [release_checksums.csv](provenance/release_checksums.csv) lista caminho/tamanho/hash; o manifesto histórico [manuscript_results_manifest.csv](../tables/manuscript_results_manifest.csv) continua intacto. O [preservation_manifest.csv](provenance/preservation_manifest.csv) registra inclusive arquivos locais não publicados.

## Não incluídos e estratégia

Rasters completos DW/MapBiomas permanecem nos catálogos públicos: identificadores, período, bandas, grid e parâmetros estão preservados. O projeto não requer baixar rasters nacionais para auditar os resultados congelados. MapBiomas também disponibiliza download de [GeoTIFF 2025 Coleção 4 10m](https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/lulc_10m/collection4/coverage/brazil_coverage/brazil_coverage-col4_10m_2025.tif), se necessário para outro fluxo. O arquivo nacional não foi baixado nem hashado nesta organização.

JSONs por fatia, checkpoints, CSVs/Parquets pré-correção do desenho e caches de trabalho foram classificados segundo sua função e conteúdo, com justificativa e tamanho por caminho. Muitos armazenam cópias das observações, coordenadas e probabilidades já consolidadas nos parquets; versões RAW consolidadas foram preservadas para comparação. Reextração GEE pode recuperar intermediários operacionais, mas não prometemos igualdade byte a byte de todos os JSONs antigos. Não são entradas necessárias para usar os resultados congelados. A cópia `extraction_slices/` é byte a byte duplicada de `legacy_raw_extraction_slices/`, verificada por hashes por arquivo.

Normas de terceiros e instruções locais `.agents/` permanecem locais. Nenhum artefato científico indispensável identificado na seleção final depende exclusivamente de um arquivo ignorado; a recuperação dos dados finais e do registro da amostra é testada no clone. Não há destino externo contratado, DOI de depósito ou snapshot completo dos catálogos. Código/manuscrito do autor não receberam nova licença de reutilização por esta organização.
