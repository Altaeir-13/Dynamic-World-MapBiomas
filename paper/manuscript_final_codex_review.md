# Revisão científica e editorial final

**Projeto:** Dynamic World × MapBiomas, MATOPIBA 2025 — Space Week Nordeste 2026  
**Data:** 12 de outubro de 2026  
**Resultado:** **READY FOR AUTHOR APPROVAL**

O DOCX revisado é o mestre editável. O PDF foi exportado exclusivamente desse DOCX pelo LibreOffice 26.2.6.3 e tem **cinco páginas**, sem numeração. As cinco páginas foram renderizadas e examinadas visualmente. O texto extraído do PDF coincide com os nós de texto do DOCX depois de remover espaços e quebras de linha. Essa comparação não demonstra equivalência entre LibreOffice e Microsoft Word: Word não está disponível neste ambiente.

Restam o preenchimento dos marcadores de autoria, afiliações e contatos e a aprovação científica do grupo. Após esse preenchimento, deve-se reexportar o DOCX e repetir a conferência de paginação. Não há desconformidade editorial comprovada pendente na versão entregue.

## 1. Escopo, fontes e preservação

O trabalho foi estritamente editorial e de verificação dos artefatos já produzidos. Não houve chamadas ao Google Earth Engine, geração de amostras, ajuste de modelos, execução de bootstrap ou alteração de resultados. Foram consultados `PROJECT_BRIEF.md`, a emenda do Checkpoint 3D, os relatórios de inferência e correção temporal, `manuscript_final_release_check.md`, as tabelas finais, o manifesto e as seis figuras existentes. Os scripts anteriores de produção documental foram inspecionados, mas não executados ou modificados.

A raiz Git está na subpasta `Dynamic-World-MapBiomas`. O estado inicial já continha `src/gee/01_check_access.py` modificado e numerosas pastas não rastreadas. Esse trabalho existente foi preservado. Nenhum commit, push ou submissão foi realizado.

Os **33 arquivos** catalogados em `tables/manuscript_results_manifest.csv` conferem com seus SHA-256. A verificação adicional de **830 arquivos** registrados antes da autoria não identificou alteração. Foram preservados dados, tabelas, figuras, configurações, scripts experimentais, relatórios científicos, manifests, checksums e os quatro arquivos principais da V3.1. Resultados legados em `tables_legacy_raw/` e `figures_legacy_raw/` não foram usados como resultados finais.

Evidências programáticas estão em `paper/qa_final_review/final_audit.json`, `protected_before.json` e `v3_1_parity.json`. A comparação dos vetores mensais usa apenas o cache materializado em `data/processed/extraction_slices_bilinear/`, sem extração remota ou produção de um novo dataset.

## 2. Normas consultadas e decisões

Foram lidos diretamente o [modelo normativo oficial](https://spaceweeknordeste.com/wp-content/uploads/2026/01/normas_trabalhos_cientificos_swn_2026.pdf) e as [instruções aos autores](https://spaceweeknordeste.com/wp-content/uploads/2026/01/instrucoes2_autores_swn_2026.pdf). Ambos já estavam no repositório; não foi encontrado um modelo oficial DOCX. Não se utilizou a alegação de conformidade do relatório V3.1 como prova.

| Item | Exigência e aplicação |
|---|---|
| Extensão e envio | Até cinco páginas, incluindo referências e elementos gráficos; submissão em PDF; sem números de página. |
| Área e margens | Área de 178 × 229 mm; esquerda 19 mm; topo 25 mm; título começa a 35 mm. |
| Colunas | Duas colunas de 86 mm, separadas por 6 mm; texto justificado. |
| Tipografia | Times New Roman; título 14 pt, negrito, maiúsculas e centralizado; artigo 10 pt. |
| Autoria | Nomes e afiliações abaixo do título; 10 pt, sem exceção para redução. |
| Resumos | Resumo e Abstract com 150–200 palavras; Abstract e seu título em itálico. |
| Seções | Títulos principais numerados, centralizados, maiúsculos e negrito; uma linha de espaço antes/depois. Subseções à esquerda, negrito. |
| Parágrafos | Entrelinha simples; primeiro sem recuo, seguintes com 0,63 cm. |
| Figuras e tabelas | Dentro da área útil, podendo abranger duas colunas; chamadas no texto; legenda posterior, centralizada, 9 pt e negrito. |
| Equações | Sem regra tipográfica específica adicional nos PDFs; preservadas dentro da área útil. |
| Referências | Numeradas por primeira ocorrência; citações entre colchetes. |

**Decisões documentadas:**

- Não existe autorização explícita para tabelas/referências em 7,5 pt ou afiliações em 8 pt. Aplicou-se 10 pt; 9 pt ficou restrito às quatro legendas.
- O PDF do modelo existente tem MediaBox de **612 × 792 pt**, papel Carta. O texto normativo não nomeia A4/Carta; adotou-se a dimensão efetiva do modelo, 215,9 × 279,4 mm. Com a área prescrita, as margens direita e inferior são 18,9 e 25,4 mm. O uso anterior de A4 não foi tratado como infração comprovada isoladamente.
- O modelo inclui um logotipo cuja posição visual não coincide com a instrução textual de início do título a 35 mm. Prevaleceu essa instrução textual; não foi inserido logotipo, cuja reprodução não é exigida no texto normativo.
- Termos ingleses e títulos bibliográficos em inglês foram italicizados. Identificadores matemáticos e siglas permanecem em notação convencional.
- As equações são texto matemático editável em Times New Roman 10 pt. `pmed` identifica o vetor médio mensal e evita ambiguidade de extração de um acento combinante; a fórmula é definida no próprio parágrafo.

## 3. Problemas efetivamente encontrados na V3.1

| Problema | Evidência e consequência |
|---|---|
| Tipografia reduzida | OOXML e PDF confirmam tabelas e referências em **7,5 pt** e afiliações em **8 pt**. O relatório anterior qualificava indevidamente esses tamanhos como conformes. |
| Tabela 1 mistura estimandos | Colunas censitárias de pixels traziam valores de estimativas amostrais; taxas estaduais amostrais eram apresentadas como censo. Intervalos rotulados como espaciais não eram rastreáveis às fontes citadas. |
| Áreas individuais transcritas | Valores por regime/estado diferiam da soma efetiva de `A_hs` no quadro congelado, inclusive diferenças inferiores a um hectare. A nova tabela é montada diretamente do CSV. |
| Intervalo da razão H3 | O IC [3,25; 4,61] aparecia na Tabela 2, mas não consta das tabelas finais de bootstrap. Foi retirado, sem recalcular inferência. |
| Projeção descrita incorretamente | O manuscrito dizia que a comparação e as séries mensais estavam em EPSG:5880; o manifesto operacional registra grade MapBiomas EPSG:4326, reservando EPSG:5880 às operações métricas. |
| Elegibilidade mal descrita | A exclusão geral de água e áreas não vegetadas não corresponde ao crosswalk operacional. A exclusão normativa do desenho é das classes 18/21, códigos desconhecidos e dados inválidos. |
| Estabilidade chamada de modal | A implementação conta coincidências com a **classe anual**, não com a classe modal mensal. A redação foi alinhada à fórmula executada, preservando valores e método. |
| H4 ponderado mal identificado | Os percentuais finais usam `design_weight_main/robust`, não peso de área. Um relatório auxiliar ainda registra 405 casos; o CSV final e sua conferência mostram **404**. |
| Interpretação excessiva | A V3.1 inferia ausência de poder preditivo adicional de JSD e equivalência PI/BA a partir de intervalos que incluíam 1. Incluía mecanismos fenológicos e exemplos de parcelas não observados diretamente. |
| Comparação bibliográfica sem suporte | A alegação genérica de 10%–25% de discordância não era sustentada diretamente pelas referências citadas para aquela comparação. |
| Chamadas incompletas | Figura 2 e Tabela 2 não eram chamadas explicitamente na narrativa principal. |
| Gráfico de regimes | A figura anterior dizia “área ponderada” para números que correspondem a pixels e usava “omissão/excesso”, inadequados a uma comparação sem verdade independente. |

**DOCX versus PDF originais:** ambos contêm cinco páginas completas e o mesmo texto substantivo. A extração de dois símbolos `∈` em posições diferentes impedia igualdade literal da sequência; removendo apenas espaços e esses símbolos, o restante coincide. Uma reexportação independente do DOCX reproduziu o texto integral do PDF original. Comparando rasterizações na mesma escala, páginas 1, 2, 3 e 5 foram idênticas; a diferença na página 4 ficou confinada à região da Figura 1. Portanto, não se confirma a alegação anterior de identidade absoluta de renderização. Não foram observados cortes de páginas ou sobreposições na V3.1; a legibilidade das tabelas/referências era limitada pela fonte pequena, e a Figura 2 estava excessivamente reduzida.

As figuras congeladas de JSD e estabilidade, embora não incorporadas à V3.1, ainda exibem **IC e tamanhos de efeito legados nas caixas de anotação**, incompatíveis com as tabelas corrigidas. Foram preservadas, documentadas e excluídas do manuscrito revisado. Isso não altera os resultados congelados nem impede a entrega: as figuras usadas nesta revisão foram produzidas exclusivamente das tabelas finais, como artefatos editoriais separados.

## 4. Correções implementadas e conferência científica

As tabelas foram simplificadas, com fontes de 10 pt e sem colunas narrativas redundantes. A Tabela 1 tem cinco colunas que distinguem hectares censitários, percentuais censitários por área/pixels e percentuais amostrais por pixels. Seus totais foram obtidos por soma dos subestratos já persistidos. Percentuais estaduais usam o domínio elegível do estado. Não se atribui IC amostral ao parâmetro censitário.

A Tabela 2 conserva H1–H3 e todos os sete OR pertinentes, com escalas e IC espaciais explícitos. O ponto H3 = 3,87 é conservado; os intervalos por faixa aparecem na Figura 2. Não se substituiu um IC ausente por um intervalo inventado ou derivado dos limites marginais.

| Resultado | Valor conferido | Fonte autoritativa |
|---|---|---|
| População | 52.342.114,746229 ha; 5.354.669.418 pixels; 410 subestratos ativos | `sampling_frame_10m.csv` |
| Discordância censitária | 7.477.177,227037 ha; 14,2852028% por área; 766.304.630 pixels; 14,3109606% por pixels | Soma de AN + NA no quadro |
| Discordância amostral 20k | 14,3148430% por pixels; 14,2896974% por área; 7.479.568,868491 ha | `descriptive_regime_proportions.csv` e leitura do CSV anual |
| H1 | ΔH = +0,0162135; IC espacial [+0,0102649; +0,0221115] | `hypothesis_h1_results.csv`; `spatial_bootstrap_contrasts.csv` |
| H2a | ΔJSD = +0,0074922; IC [+0,0046759; +0,0102306] | `hypothesis_h2_results.csv`; bootstrap corrigido |
| H2b | ΔS = -0,0789586; IC [-0,0974054; -0,0599416] | Mesmas fontes corrigidas |
| H3 | 45,9057% em <30 m; 11,8669% em ≥250 m; razão 3,868381 | `robustness_comprehensive_summary.csv`; tabelas por faixa |
| H4 principal | 207/5.143; 4,0249% bruto; 4,2772950% ponderado por pixels | `hypothesis_h4_robust_disagreement.csv`; conferência do CSV anual |
| H4 robusta | 404/10.286; 3,9277% bruto; 4,1687301% ponderado por pixels | Mesmas fontes |
| Bloco e replicações | Alcance 25,62164 km; bloco 30 km; 1.999 réplicas | `spatial_semivariogram_parameters.csv`; scripts/relatórios de inferência |

O documento diferencia probabilidades de inclusão e pesos de desenho/área; mantém 16 estratos, 20k/40k aninhados, {19,36}, pelo menos oito meses, interpolação apenas de probabilidades e distância mínima simétrica, truncada em 250 m. A regressão reportada utiliza **distância linear**, como no modelo final, sem introduzir a especificação alternativa logarítmica do brief inicial.

A inspeção independente dos registros anuais confirma 40.000 pontos, 20.000 principais, mínimo de oito meses e pesos principais positivos. A seleção de H4 sobre esses registros reproduz os totais e percentuais do CSV final. Os quartis são calculados **separadamente por amostra**, conforme o script: principal Q1(H)=0,80903118, Q1(JSD)=0,01743829 e Q3(S)=0,75; robusta 0,80898926, 0,01739491 e 0,75. Não se alterou o critério.

A comparação somente de vetores **já materializados** nos 40.000 pontos confirma diferença absoluta média 0,0049828597, 3.296 mudanças de argmax (8,24%) e 1.035 inversões lavoura/não-lavoura (2,5875%, arredondadas para 2,59%). A limitação foi mantida, com definições distintas para o vetor anual canônico e a média mensal harmonizada. Os relatórios antigos não foram usados para justificar neutralidade causal ou insensibilidade absoluta.

Foram removidas a afirmação de exclusão de 21,74% sem explicitação de seu denominador, a faixa bibliográfica 10%–25%, exemplos específicos de carreadores/parcelas e alegações de fenologia observada. A discussão preserva mecanismos como hipóteses interpretativas, distingue chances de probabilidades, não afirma igualdade PI/BA, não elimina utilidade preditiva de JSD e não interpreta filtros de H4 como explicação causal do complemento.

## 5. Figuras e tabelas finais

| Elemento | Conferência |
|---|---|
| Tabela 1 | Página 3; dez linhas incluindo cabeçalho; cinco colunas; largura medida **177,9999 mm**; inteira; fonte 10 pt. |
| Tabela 2 | Página 4; doze linhas incluindo cabeçalho; quatro colunas; **177,9999 mm**; inteira; fonte 10 pt. |
| Figura 1 | Nova representação das proporções amostrais por pixels e discordância estadual, lidas diretamente das tabelas; 2.102 × 744 px; 178 × 63 mm; aproximadamente 300 dpi. |
| Figura 2 | Proporções pontuais da tabela H3 e IC espaciais da tabela de bootstrap; 1.016 × 839 px; 86 × 71 mm; aproximadamente 300 dpi. |

As figuras têm rótulos em Times New Roman de aproximadamente **10,08 pt** à dimensão de inserção (42 pixels a 300 dpi). Por serem imagens, sua fonte não é um recurso textual incorporado ao PDF; a verificação usa o script, os arquivos de fonte do Windows e a inspeção visual. Não houve ampliação de uma imagem pequena para simular resolução maior. As figuras originais foram preservadas.

Figura 1, Figura 2, Tabela 1 e Tabela 2 têm chamadas no corpo e legendas completas. Na Figura 2, a faixa final representa distâncias iguais ou superiores ao truncamento de 250 m; as demais faixas são [a,b). Os pontos são estimativas originais, não médias do bootstrap; as barras são os IC espaciais persistidos.

## 6. Tipografia, geometria e paridade verificadas

| Uso | DOCX e PDF final |
|---|---|
| Título | Times New Roman negrito, **14 pt** |
| Texto, autores, afiliações e referências | Times New Roman, **10 pt** |
| Células e cabeçalhos das tabelas | Times New Roman, **10 pt** |
| Seções e subseções | Times New Roman negrito, **10 pt** |
| Abstract | Times New Roman itálico, **10 pt**; título negrito e itálico |
| Quatro legendas | Times New Roman negrito, **9 pt**, com itálico nos termos ingleses pertinentes |

Os recursos incorporados são `TimesNewRomanPSMT`, `TimesNewRomanPS-BoldMT`, `TimesNewRomanPS-ItalicMT` e `TimesNewRomanPS-BoldItalicMT`, todos com **FontFile2**. Os únicos tamanhos extraídos do PDF são **9, 10 e 14 pt**. Não há 7,5 ou 8 pt, substituição por OpenSymbol/Cambria ou numeração de páginas.

Todas as páginas medem 215,9 × 279,4 mm, dentro do arredondamento de twips. A posição lógica do título é topo de 25 mm mais 10 mm de espaço; o topo da caixa dos glifos no PDF é **35,745 mm**, diferença de métrica tipográfica. Colunas são 86 mm com vão de aproximadamente 6 mm. As tabelas começam em x=19,0147 mm e terminam em x=197,0146 mm, compatíveis com a área de 178 mm após arredondamento.

A verificação exclui espaços sem tinta e usa tolerância geométrica de 0,15 mm para arredondamento das caixas de glifos. Não foram encontrados caracteres com tinta fora desse envelope. Essa tolerância não representa diminuição de fontes nem aumento deliberado da área útil.

Resumo: **177 palavras**. Abstract: **171 palavras**. As fórmulas H, JSD e S são legíveis, editáveis, definem seus símbolos e coincidem na extração DOCX/PDF. Não há sintaxe LaTeX crua ou imagens de equações. O hiperlink da documentação MapBiomas é preservado na referência [3].

## 7. Avaliação visual de cada página

Inspeção das imagens do último render, em resolução original de 1.547 × 2.002 pixels:

| Página | Conteúdo e avaliação |
|---|---|
| 1 | Título, marcadores de autoria, resumos e introdução. Afiliações em 10 pt, sem cortes; Resumo inicia na coluna esquerda. Abstract continua na direita em itálico; introdução termina completa. Sem linha decorativa sob o título. |
| 2 | Métodos, com colunas equilibradas. Crosswalk, grade, fórmulas, pesos e inferência legíveis. Não há caracteres ausentes ou equações sobrepostas. Espaço inferior é mantido por decisão de começar resultados em página própria. |
| 3 | Introdução aos resultados, Tabela 1, Figura 1 e resultados H1–H4. Tabela inteira, colunas numéricas legíveis e margens preservadas. Rótulos do gráfico separados, sem sobreposição. |
| 4 | Tabela 2 no topo, Figura 2, regressão, robustez e discussão. IC e escalas são legíveis; barras do gráfico não invadem a legenda. A passagem de coluna segue o fluxo de leitura. Sem clipping ou sobreposição. |
| 5 | Conclusões completas e oito referências, sem quebra de entrada bibliográfica entre colunas. Colunas equilibradas respeitando a integridade dos parágrafos; bases textuais em 115,26 e 122,21 mm. A área branca remanescente é aceitável e não foi preenchida artificialmente. |

O renderer disponível é LibreOffice 26.2.6.3; sua mensagem de diagnóstico sobre bibliotecas independentes não impediu exportação nem renderização. O primeiro render falhou ao usar o diretório temporário protegido do sistema; o script passou a usar um diretório temporário restrito ao workspace. O caminho padrão de Word, a classe COM Word.Application e seu registro App Paths não foram encontrados. **Não houve comparação efetiva com Word**, nem declaração de paridade perfeita entre programas.

## 8. Referências

A bibliografia foi reduzida de quinze para **oito referências relevantes**, numeradas pela primeira ocorrência, mantendo título, periódico, volume/páginas ou identificador e DOI/URL. Não há citação órfã. Os títulos e metadados mantidos foram conferidos em fontes primárias:

| Final | Fonte de conferência e função |
|---|---|
| [1] Spera et al., 2016 | [Editora Wiley](https://onlinelibrary.wiley.com/doi/10.1111/gcb.13298); expansão agrícola no Cerrado/MATOPIBA. |
| [2] Brown et al., 2022 | [Scientific Data](https://www.nature.com/articles/s41597-022-01307-4) e [Google Research](https://research.google/pubs/dynamic-world-near-real-time-global-10-m-land-use-land-cover-mapping/); produto DW. |
| [3] MapBiomas | [Documentação oficial da Cobertura 10m](https://brasil.mapbiomas.org/iniciativas-e-produtos/cobertura-e-uso-da-terra/cobertura-10m/cobertura/); Coleção 4, legenda e asset 2025. Não se confunde ano do mapa com ano de publicação; registro de acesso em 12/10/2026. |
| [4] Pontius Jr. e Millones, 2011 | [Repositório dos autores, Clark University](https://commons.clarku.edu/faculty_geography/760/); quantidade e alocação. |
| [5] Shannon, 1948 | [Editora Wiley](https://onlinelibrary.wiley.com/doi/10.1002/j.1538-7305.1948.tb01338.x); entropia. |
| [6] Lin, 1991 | [IEEE Xplore](https://ieeexplore.ieee.org/abstract/document/61115/authors); divergência Jensen-Shannon generalizada. |
| [7] Olofsson et al., 2014 | [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0034425714000704); princípios de desenho/ponderação, sem tratar um mapa como referência verdadeira. |
| [8] Künsch, 1989 | [Lista de publicações do autor, ETH](https://people.math.ethz.ch/~kuensch/papers/); base da reamostragem de observações dependentes, sem afirmar que prova validade exata do esquema espacial aplicado. |

Foram retiradas citações desnecessárias de contextualização geral, acurácia e autocorrelação. Souza et al. (2020), baseado no produto Landsat, não foi mantido como documentação específica da Coleção 4 de 10 m. Roberts et al. (2017), sobre validação cruzada, não foi usado como prova do bootstrap. A entrada anterior atribuída a da Silva et al. (2017) tinha a ordem autoral incorreta para o artigo de Martinelli et al.; como a citação era redundante, foi excluída. Fritz et al. não foi usado para sustentar a faixa de discordância removida.

## 9. Arquivos criados e reprodução

Entregas:

- `paper/manuscript_space_week_nordeste_2026_final_review.docx`
- `paper/manuscript_space_week_nordeste_2026_final_review.pdf`
- `paper/manuscript_final_codex_review.md`

Artefatos editoriais auxiliares:

- `paper/manuscript_space_week_nordeste_2026_final_review.md`, derivado da ordem real dos nós do DOCX.
- `paper/build_final_review.py`, criação de DOCX e figuras editoriais e exportação DOCX → PDF.
- `paper/audit_final_review.py`, conferências independentes de documentação e de dados já materializados.
- `paper/final_review_assets/figure1.png` e `figure2.png`.
- `paper/qa_final_review/`, evidências JSON, renders de todas as páginas e reexportação da V3.1.

Nenhum arquivo anterior foi sobrescrito. Não houve mudanças em `src/`, `tables/`, `figures/`, `docs/` ou nos manifests.

Com o Python disponibilizado pelo runtime Codex, a reprodução no PowerShell é:

```powershell
& 'C:/Users/Altair/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' paper/build_final_review.py --render
& 'C:/Users/Altair/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' paper/audit_final_review.py
```

Esses comandos só escrevem em `paper/`. O script usa o LibreOffice nativo instalado no Windows, o renderer `render_docx.py` da habilidade de documentos e o Poppler do runtime. Os registros de hashes estão no JSON de auditoria; os checksums científicos não são regenerados.

## 10. Pendências humanas

1. Substituir os marcadores por nomes, ordem autoral, instituições e contatos reais.
2. Aprovar a redação e a interpretação pelo grupo de autores.
3. Após preencher autoria, reexportar e confirmar novamente o limite de cinco páginas. Se os autores editarem no Word, conferir o PDF efetivamente exportado por esse programa.

O artigo está tecnicamente pronto para essa aprovação. Não foi submetido ao evento.
