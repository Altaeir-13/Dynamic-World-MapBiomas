# Histórico científico e precedência entre versões

## Linha de desenvolvimento

O histórico Git anterior à organização tinha cinco commits, terminando em `77d17568ab92033c929bb8d2f3f5c1c340b2d73a`. Só `.gitignore`, `requirements.txt`, `PROJECT_BRIEF.md` e o script de acesso eram versionados. As principais correções, dados, fontes e artigo estavam locais/não versionados. O histórico existente foi preservado; a publicação consolidada não reescreve commits.

O brief de 26/09/2026 define pergunta, crosswalk, temporalidade e epistemologia. Os relatórios locais documentam protótipo, revisões do desenho, domínio canônico, correção mensal e preparação editorial. Não se presume memória de conversas como prova; nesta organização a evidência é o código, os arquivos e seus registros existentes.

| Problema identificado | Correção/evidência | O que usar hoje |
|---|---|---|
| Ano inicial 2024 no acesso | Brief e script preexistente atualizados para 2025 | Intervalo 2025; diferença original do usuário preservada em `user_diff_before.patch` |
| Área de célula tratada como fixa | Áreas por `pixelArea` e pesos por ponto; diferença projeção/geodésia/raster documentada | Censo e `pixel_area_m2`, nunca pixels×100m² |
| Distância sobre complemento da borda/mascaras | Núcleo canônico mede distância a edge=1 e exclui classes operacionais antes da borda | `dw_annual.py`; minimum MB/DW e truncamento 250 m |
| Subestratos com pi=0 | Realocação garantindo n_robust≥1 e amostra regenerada | Quadro/cotas/alocação finais e pontos canônicos |
| Composição dependente da fatia | Domínio-fonte fixo MATOPIBA +5km, datas congeladas, censo reexportado | Núcleo anual + exportações em lotes; auditorias de partição/convergência/paginação |
| Mensal RAW sem bilinear na grade MB | Extração harmonizada script 12 para 40k, 182 fatias | Parquets finais corrigidos; RAW somente em `data/audit/` |
| Uso de H anual canônico no lugar de H(média mensal) para JSD | Definições explicitadas na extração 11/12 | `entropy_temporal_mean−entropy_monthly_mean`; classe anual continua referência de S |
| Resíduo entre agregações anuais/mensais | Diagnóstico materializado, ressalva sobre ordem de operações/máscaras | Não exigir identidade exata nem declarar insensibilidade universal |
| Bloco 20km em texto | Conferência de semivariograma/scripts/tabelas | Bloco primário 30km, 1.999 réplicas; 10/20/40 como sensibilidades |
| Categoria 250m no diagnóstico | Faixas `[a,b)`; valor truncado 250 integra último grupo | H3 principal já correto; rascunho diagnóstico superado |
| 405 H4 na mestre em relatório | Auditoria editorial confere tabela congelada: 404, 4,1687301% | `hypothesis_h4_robust_disagreement.csv` |
| Figuras com caixas de inferência RAW | Artigo usa duas figuras editoriais derivadas das tabelas finais | `final_figure1/2`; antigas preservadas como materializações históricas |
| Mistura censo/estimativa e área/pixels | Revisão editorial separa estimandos, removes IC sem fonte e redige limitações | Manuscrito `final_title_references` |
| Projeção/S descritas incorretamente | Artigo distingue grid EPSG:4326 vs operações métricas EPSG:5880; S referência anual | Metodologia consolidada |
| Fontes, geometria, título/citações e autoria intermediários | Revisões autoral, geométrica e bibliográfica, 12/10/2026 | PDF/DOCX/Markdown com título solicitado |

## O que foi preservado do legado

`development_sources.zip` contém protótipos, testes substituídos, patches de desenvolvimento e scripts editoriais necessários para rastrear decisões. `historical_evidence.zip` contém relatórios, tabelas/figuras RAW, alocações inválidas e requisitos antigos; não são entradas finais. `editorial_provenance.zip` contém predecessores editáveis necessários à cadeia documental e evidências JSON. A conservação em ZIP evita dezenas de scripts provisórios na árvore operacional.

Os dois parquets `data/audit/legacy_raw_*` permitem inspecionar a mudança científica de S/JSD em relação ao RAW. O manifesto indica seu hash original e a cópia remota. Nem toda versão intermediária de manuscrito é publicada; textos finais, código histórico relevante e auditorias identificam a procedência suficiente para esta entrega.

## Ressalvas dos registros preservados

`config/experiment.yaml` ainda registra estado de protótipo e bloco a determinar. `sampling_manifest.yaml` é snapshot 3B e não uma especificação atualizada de todas as correções. `PROJECT_BRIEF.md` inclui intenções que diferem da execução final, como sensibilidade 30m não consolidada e alternativa logarítmica de distância. Não se alteraram esses registros para apagar o histórico; `config/release.yaml` documenta o que foi executado.

Relatórios antigos contêm 405/4,18% em H4/40k, explicações absolutas sobre neutralidade do resíduo e hashes transcritos que podem divergir do próprio manifesto existente. As tabelas congeladas, os hashes físicos e a auditoria editorial posterior têm precedência. O manuscrito final corrige a redação sem modificar resultados. Esta organização registra os conflitos, não refaz inferência para resolvê-los.

## Manuscrito definitivo

O título final é **ANÁLISE ESPACIAL E PROBABILÍSTICA DA DISCORDÂNCIA NO MAPEAMENTO DE LAVOURAS DO MATOPIBA: DYNAMIC WORLD E MAPBIOMAS**. A cadeia documentada é `final_review` → revisão autoral → correção geométrica `author_review_corrected` → título/referências `final_title_references`. A primeira tinha título provisório e marcadores de autoria; não é a entrega final. O artefato final tem autoria já preenchida e cinco páginas. A publicação no GitHub não constitui submissão ao evento nem prova adicional de aprovação formal por seus organizadores.
