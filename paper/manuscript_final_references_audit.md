# Auditoria final do título e das referências — Space Week Nordeste 2026

Data: 12/10/2026. Resultado: **FINAL TITLE AND REFERENCES: VERIFIED**.

Foi utilizada como fonte mestre a versão editável `manuscript_space_week_nordeste_2026_author_review_corrected.docx`. Essa versão e seu PDF foram preservados, com SHA-256 conferidos. A intervenção compreendeu o título, o alcance de citações e a paginação; não houve execução de experimentos, análises estatísticas ou alteração dos artefatos científicos congelados.

## Título e autoria

Título definitivo, idêntico no corpo do DOCX, no PDF, no texto editorial derivado e nos metadados Title dos dois documentos:

**ANÁLISE ESPACIAL E PROBABILÍSTICA DA DISCORDÂNCIA NO MAPEAMENTO DE LAVOURAS DO MATOPIBA: DYNAMIC WORLD E MAPBIOMAS**

O título ocupa três linhas, em Times New Roman, 14 pt, negrito, centralizado e em maiúsculas. O autor único é **Randerson Sousa de Sá Nunes**, Instituto Federal de Educação, Ciência e Tecnologia do Maranhão (IFMA) — Campus Caxias; Bacharelado em Ciência da Computação; Caxias — MA, Brasil; **randerson.sdsn@gmail.com**. Nome e contato foram confirmados expressamente na instrução final do responsável. Não foram acrescentados coautores ou orientador. Author e last_modified_by do DOCX e Author do PDF identificam somente esse autor.

## Auditoria bidirecional

A verificação A partiu de cada entrada bibliográfica e buscou suas ocorrências no corpo anterior à seção Referências. A verificação B partiu dos grupos numéricos de citação, inclusive [2,3], e resolveu cada número contra as entradas. Intervalos decimais como [0,507; 1,212] não foram confundidos com citações. Os resultados não dependem apenas da igualdade entre contagens.

| Ref. | Obra | Onde é citada | O que fundamenta | Verificação bibliográfica | Situação |
|---|---|---|---|---|---|
| [1] | Spera et al., *Land-use change affects water recycling in Brazil’s last agricultural frontier* | Introdução, primeiro parágrafo: expansão de lavouras no Cerrado e MATOPIBA “foi documentada [1]”. Uma ocorrência. | Contexto histórico da expansão agrícola. Não sustenta resultados de discordância de 2025 nem uma taxa atual de expansão. | [Wiley](https://onlinelibrary.wiley.com/doi/10.1111/gcb.13298): S. A. Spera, G. L. Galford, M. T. Coe, M. N. Macedo e J. F. Mustard; *Global Change Biology* 22(10), 3405–3413, 2016; DOI 10.1111/gcb.13298. Resumo e material suplementar incluem o contexto regional. | Confirmada; citação reposicionada sobre a expansão documentada. |
| [2] | Brown et al., *Dynamic World, Near real-time global 10 m land use land cover mapping* | Introdução: nove probabilidades por observação Sentinel-2 [2] e sensor compartilhado [2,3]. Métodos 2.1: crops, índice 4 [2]. Três ocorrências. | Produto baseado em Sentinel-2, probabilidades por observação, resolução nominal e legenda. Não fundamenta o composto anual específico deste projeto. | [Scientific Data/Nature](https://www.nature.com/articles/s41597-022-01307-4): Christopher F. Brown como primeiro autor, lista de coautores conferida; volume 9, artigo 251, 2022; DOI 10.1038/s41597-022-01307-4. Não há intervalo de páginas a inventar para esse identificador de artigo. | Confirmada; acrescentadas chamadas locais para sensor e classe. |
| [3] | MapBiomas, *Cobertura 10 m, Coleção 4, série 2017–2025. Documentação e acesso aos dados* | Introdução: mapas anuais [3] e Sentinel-2 [2,3]. Métodos 2.1: classes 19 e 36, lavoura temporária e perene [3]. Três ocorrências. | Características da Coleção 4, série anual, sensor e códigos da legenda. A escolha do crosswalk e das exclusões é do projeto. | [Organização responsável](https://brasil.mapbiomas.org/iniciativas-e-produtos/cobertura-e-uso-da-terra/cobertura-10m/cobertura/): identificação Coleção 4, série 2017–2025, 10 m, Sentinel-2 e legenda confirmadas em 12/10/2026. Referência institucional eletrônica, sem DOI, volume ou páginas aplicáveis. | Confirmada; URL oficial permanece como hiperlink funcional no DOCX e no PDF. |
| [4] | Pontius Jr. e Millones, *Death to Kappa: birth of quantity disagreement and allocation disagreement for accuracy assessment* | Introdução, segundo parágrafo: comparação de quantidade e alocação [4]. Resultados, parágrafo após Tabela 1: “A decomposição em área [4] resulta, neste censo…”. Duas ocorrências. | Decomposição de discordância por quantidade e alocação em comparação de mapas. Os valores 4,99 e 9,30 pontos percentuais pertencem ao censo do projeto. | [Repositório institucional dos autores, Clark University](https://commons.clarku.edu/faculty_geography/760/): R. G. Pontius Jr. e M. Millones; *International Journal of Remote Sensing* 32(15), 4407–4429, 2011; DOI 10.1080/01431161.2011.552923. | Confirmada; chamada antecipada para evitar atribuição dos números originais à publicação. |
| [5] | Shannon, *A mathematical theory of communication* | Métodos 2.2, parágrafo das fórmulas: “entropia normalizada de Shannon [5]”. Uma ocorrência. | Entropia −Σp ln p, convenção no zero e máximo para distribuição uniforme. A divisão por ln 9 aplica esse fundamento às nove classes do projeto. | [Wiley](https://onlinelibrary.wiley.com/doi/10.1002/j.1538-7305.1948.tb01338.x): C. E. Shannon; *Bell System Technical Journal* 27(3), 379–423, julho de 1948; DOI 10.1002/j.1538-7305.1948.tb01338.x. | Confirmada; referência à parte de julho, que contém o fundamento utilizado. |
| [6] | Lin, *Divergence measures based on the Shannon entropy* | Métodos 2.2, mesmo parágrafo: “JSD temporal generalizada [6]”. Uma ocorrência. | Divergência Jensen–Shannon de várias distribuições, por diferença de entropias. Meses, pesos iguais 1/M e normalização por ln 9 são a aplicação do projeto. | [IEEE](https://ieeexplore.ieee.org/abstract/document/61115/authors): Jianhua Lin; *IEEE Transactions on Information Theory* 37(1), 145–151, 1991; DOI 10.1109/18.61115. Formulação multivariada conferida na equação 5.1 do artigo original. | Confirmada; a fonte não foi limitada indevidamente à forma de dois vetores. |
| [7] | Olofsson et al., *Good practices for estimating area and assessing accuracy of land change* | Métodos 2.3, primeiro parágrafo: “A seleção aleatória sem reposição [7]…”. Uma ocorrência. | Princípios de amostragem probabilística, probabilidades de inclusão conhecidas e positivas, e análise coerente com o desenho. Não estabelece os 16/410 estratos, tamanhos ou aninhamento específicos. | [Editora](https://www.sciencedirect.com/science/article/pii/S0034425714000704) e [repositório institucional](https://nottingham-repository.worktribe.com/output/728216/good-practices-for-estimating-area-and-assessing-accuracy-of-land-change): P. Olofsson, G. M. Foody, M. Herold, S. V. Stehman, C. E. Woodcock e M. A. Wulder; *Remote Sensing of Environment* 148, 42–57, 2014; DOI 10.1016/j.rse.2014.02.015. | Confirmada; alcance da citação esclarecido. A comparação entre produtos não foi convertida em avaliação de acurácia com referência independente. |
| [8] | Künsch, *The jackknife and the bootstrap for general stationary observations* | Métodos 2.3, terceiro parágrafo: “adaptação espacial do bootstrap em blocos para observações dependentes [8]”. Uma ocorrência. | Fundamento de reamostragem em blocos para dados dependentes. O artigo trata de sequências estacionárias; não demonstra a validade dos blocos espaciais de 30 km ou dos resultados deste projeto. | [Lista do autor na ETH Zürich](https://people.math.ethz.ch/~kuensch/papers/) e [registro disponibilizado pelo autor](https://www.researchgate.net/publication/2355926_The_Jackknife_and_the_Bootstrap_for_General_Stationary_Observations): H. R. Künsch; *Annals of Statistics* 17(3), 1217–1241, 1989; DOI 10.1214/aos/1176347265. | Confirmada como fundamento; redação qualificada para distinguir a adaptação espacial. |

Referências utilizadas: **[1]–[8]**. Nenhuma referência não citada. Nenhuma citação sem entrada correspondente. Nenhum número ou registro duplicado. Ordem das primeiras citações: **1, 2, 3, 4, 5, 6, 7, 8**, igual à ordem da bibliografia. Foram encontrados 12 grupos de citação e 13 vínculos individuais entre citação e referência, contando [2,3] como dois vínculos. Ocorrências individuais por referência: **1, 3, 3, 2, 1, 1, 1, 1**.

Os locais, trechos e resoluções das duas verificações estão registrados em [citations_bidirectional.json](<C:/Users/Altair/Documents/Dynamic World x MapBiomas/Dynamic-World-MapBiomas/paper/qa_final_references/citations_bidirectional.json>).

## Sustentação das afirmações e correções implementadas

| Trecho ou assunto | Classificação | Decisão editorial |
|---|---|---|
| Expansão no Cerrado/MATOPIBA e necessidade de monitoramento | Expansão sustentada por [1]; motivação é a justificativa dos autores | Reformulada para separar o fato histórico da motivação. Não foram acrescentadas taxas de expansão ou extrapolação para 2025. |
| Dois produtos utilizam Sentinel-2 | Característica externa de ambos os produtos | Inserida a chamada [2,3] na frase. “Compartilham parte da base observacional” evita transformar sensor comum em demonstração quantitativa de dependência dos erros. |
| Diferenças de legenda, agregação e suporte podem gerar discordância | Hipótese interpretativa motivada pelas características próximas [2,3] | Mantido o caráter de possibilidade. A frase não afirma que esses mecanismos foram identificados ou causalmente medidos. |
| Códigos {19,36} e crops = 4 | Informação externa da legenda; seleção binária é original | Inseridas [3] e [2] diretamente nos trechos. A [3] próxima também cobre a identificação de 18 e 21; exclusões e tratamento de dados ausentes permanecem decisões operacionais. |
| Médias diária/mensal, vetor anual e argmax | Metodologia original do projeto | Acrescentado “Neste estudo” para não atribuir a agregação à produção nativa de DW. |
| Entropia e JSD | Fórmulas externas sustentadas por [5,6]; normalização e série mensal são aplicações | Mantidas as fórmulas. [5] não afirma que entropia é probabilidade de erro; [6] permite várias distribuições, sem prescrever os meses deste estudo. |
| Seleção probabilística e ponderação | Fundamento geral externo [7], com desenho específico original | [7] foi aproximada do princípio de seleção. Probabilidades, pesos, 16 estratos, 410 subestratos e aninhamento não foram alterados nem atribuídos à publicação. |
| Bootstrap espacial de 30 km | Adaptação metodológica do projeto com fundamento geral [8] | Substituída a atribuição genérica por “adaptação espacial”. A fonte não foi tratada como prova do alcance espacial, da escolha de 30 km ou da cobertura dos intervalos. |
| Quantidade/alocação e seus valores | Método externo [4], resultados originais | A chamada [4] antecede “neste censo”; os números permanecem inalterados. |
| Domínio congelado, elegibilidade, estabilidade S, distância, conectividade, regressão e critérios H4 | Definições e execução originais | Não necessitam atribuição a obras que não fizeram o experimento. Foram preservadas integralmente. |
| H1–H4, OR, intervalos, robustez e comparação dos suportes temporais | Resultados originais dos artefatos finais | Não recebem atribuição bibliográfica externa. Tabelas e figuras são suas referências internas. Nenhum resultado foi substituído. |
| Mistura espectral, sazonalidade e decisões dos classificadores na Discussão | Interpretações hipotéticas dos resultados | Já qualificadas por “compatível”, “admite hipóteses” e ausência de identificação dos mecanismos. Não há afirmação causal nem pretensão de observação da fenologia. Mantidas sem acrescentar literatura que aparentasse confirmar causas não medidas. |
| Ordem de interpolação/agregação e resíduo temporal | Interpretação técnica de processamento próprio | Mantida como possibilidade, acompanhada das definições distintas dos suportes; não afirma mudança no terreno. |
| Censo sem erro amostral, restrição ao domínio elegível e ausência de ground truth | Propriedades do desenho e limites do próprio estudo | Mantidas. A ausência de referência independente impede identificar qual produto está correto. Não se afirma acurácia superior, equivalência estadual ou inutilidade preditiva da JSD. |

Não havia alegação de 10%–25% de discordância na literatura na versão utilizada. Não foram incluídas alegações de originalidade ou citações para inflar a bibliografia. Não foi encontrada outra lacuna bibliográfica comprovada depois das correções acima.

**Entradas corrigidas, substituídas, acrescentadas ou removidas: nenhuma.** Os oito registros já tinham identidade e dados bibliográficos compatíveis com as fontes consultadas. Foram corrigidos o alcance e o posicionamento de citações no texto, com comparação antes/depois em [build_checks.json](<C:/Users/Altair/Documents/Dynamic World x MapBiomas/Dynamic-World-MapBiomas/paper/qa_final_references/build_checks.json>).

## Fontes complementares e limites de acesso

A identificação de DW V1 e do índice crops = 4 foi confirmada também no [catálogo oficial Google Earth Engine](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1), que remete à publicação [2]. Isso foi consulta documental, sem processamento ou acesso experimental.

A expressão e o máximo da entropia foram confrontados com a seção 6 e o Teorema 2 da [reprodução do artigo original de Shannon](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf). A forma generalizada de JSD foi confirmada na equação 5.1, página 149, da [reprodução do artigo original de Lin](https://pdodds.w3.uvm.edu/research/papers/others/1991/lin1991a.pdf), por trechos indexados do PDF.

Algumas páginas e downloads diretos apresentaram restrições nesta sessão. Para [6], foram utilizados metadados IEEE e trechos indexados do original; para [7], metadados da editora/repositório institucional e passagens indexadas da [cópia do artigo original hospedada pelo serviço florestal](https://fsapps.nwcg.gov/gtac/CourseDownloads/IP/Cambodia/FlashDrive/Supporting_Documentation/olofsson_etal_2014.pdf). Para [8], a [página da editora Project Euclid](https://projecteuclid.org/euclid.aos/1176347265) não foi acessível diretamente; a publicação e sua autoria foram confirmadas na ETH e no registro do autor, com consulta ao resumo. Isso não equivale à leitura integral das provas de consistência.

**Nenhuma das oito obras permaneceu sem identidade bibliográfica confirmada.** As limitações de acesso acima restringem a extensão da leitura, não autorizam alegar que os artigos validam a implementação específica. A qualificação de [8] resolve a atribuição excessiva sem alterar a inferência experimental. Nenhuma dessas fontes fornece os resultados numéricos deste artigo.

## Preservação dos resultados

Foram comparados os textos da fonte mestre e da nova versão, admitindo somente as seis alterações de parágrafos documentadas e o título. A sequência de todos os números do corpo, retirados apenas os números de citação, permaneceu idêntica. As células das duas tabelas e os bytes das imagens no DOCX também permaneceram idênticos. Hipóteses, critérios, fórmulas, amostras, probabilidades de inclusão, intervalos, OR e limitações não foram modificados.

H1–H4 e os resultados censitários têm origem nos artefatos científicos finais do próprio projeto, incluindo `sampling_frame_10m.csv`, `spatial_bootstrap_contrasts.csv`, `spatial_bootstrap_distance_bins.csv`, `regression_logistic_rescaled_odds_ratios.csv` e `robustness_comprehensive_summary.csv`, na pasta `tables/`. Esses resultados não são atribuídos a [1]–[8]. Esta revisão não recalculou estimativas nem alterou arquivos dessa pasta, scripts experimentais, manifestos ou checksums científicos.

## Exportação e validação final

**Quantidade final: cinco páginas.** O PDF foi exportado exclusivamente do DOCX mestre por LibreOffice 26.2.6.3. Todas as páginas foram renderizadas e inspecionadas. Não foi realizada comparação de renderização com Microsoft Word; não se declara equivalência visual entre programas diferentes.

| Verificação | Resultado |
|---|---|
| Texto DOCX ↔ PDF | Correspondência integral após remoção de espaços e quebras de linha, incluindo tabelas, fórmulas, legendas e referências. |
| Fontes PDF | TimesNewRomanPSMT, TimesNewRomanPS-BoldMT, TimesNewRomanPS-ItalicMT e TimesNewRomanPS-BoldItalicMT, todas incorporadas como subconjuntos. |
| Tamanhos medidos nos caracteres PDF | Somente 9, 10 e 14 pt. Título 14 pt; corpo, afiliação, tabelas e referências 10 pt; legendas 9 pt em negrito. Texto desenhado dentro dos gráficos é raster, com imagens e dimensões preservadas. |
| Página e área útil | 215,9 × 279,4 mm; área útil nominal 178 × 229 mm. Margens nominais esquerda 19, superior 25, direita 18,9 e inferior 25,4 mm. Mantida a fundamentação do modelo e a quantização em twips da versão anterior. |
| Colunas | 86 mm cada e calha 6 mm nas seções em duas colunas; seções de largura total mantidas para tabelas e Figura 1. |
| Resumo / Abstract | 177 / 171 palavras; ambos dentro de 150–200. |
| Figuras | Dois objetos raster verificados em `page.images`, inclusive seus limites reais. Aproximadamente 300 dpi, sem redimensionamento ou reamostragem dos arquivos originais. |
| Objetos vetoriais | 35 linhas e 18 retângulos de tabelas verificados, além das duas imagens; nenhum objeto além da área útil. |
| Tabelas | Tabela 1 completa na página 3, 10 linhas × 5 colunas; Tabela 2 completa na página 4, 12 × 4. Limites horizontais de ambas: 19,191–196,803 mm. |
| Chamadas internas | Tabela 1, Tabela 2, Figura 1 e Figura 2 chamadas explicitamente no corpo; legendas completas preservadas. |
| Bibliografia | Oito entradas, na ordem da primeira citação, sem órfãs, duplicatas ou números sem correspondência. Hiperlink oficial da [3] presente e funcional em ambos os formatos. |
| Paginação | Sem números de página nem texto em cabeçalhos/rodapés. |

### Limites finais das figuras

Coordenadas em milímetros, com origem no canto superior esquerdo. A tolerância de 0,05 mm contempla somente quantização em PDF/twips; não é margem adicional de diagramação.

| Figura | Página | x mínimo–máximo | y mínimo–máximo | Limite permitido em x | Dimensões / resolução efetiva |
|---|---|---|---|---|---|
| 1 | 3 | 18,997–196,991 | 120,773–183,780 | 19–197 | 177,994 × 63,006 mm; 2102 × 744 pixels; 299,96 × 299,93 dpi |
| 2 | 4 | 18,997–105,004 | 94,051–165,065 | 19–105, primeira coluna | 86,007 × 71,014 mm; 1016 × 839 pixels; 300,05 × 300,09 dpi |

Não reapareceu o deslocamento de aproximadamente 3,2 mm corrigido na versão anterior. Os pequenos resíduos de milésimos de milímetro acima são de quantização.

### Inspeção visual página a página

| Página | Avaliação |
|---|---|
| 1 | Título definitivo em três linhas, sem corte ou sobreposição; autoria e afiliação centralizadas. Resumo completo; Abstract continua naturalmente na coluna direita; Introdução legível. |
| 2 | Métodos em duas colunas; fórmulas, símbolos e citações legíveis. Mantida folga inferior para não separar o título Resultados de sua tabela completa. |
| 3 | Resultados e Tabela 1 juntos; Figura 1 dentro da largura útil, com legenda e chamada. Censo, valores amostrais e H1–H4 continuam distintos e legíveis. |
| 4 | Tabela 2 completa no topo; Figura 2 na primeira coluna, próxima aos resultados e à legenda. Discussão na segunda coluna, sem sobreposição. |
| 5 | Conclusões mantidas inteiras com seu título; referências sem corte de entradas. Colunas com finais em 110,494 e 114,621 mm, diferença aproximada de 4,13 mm. Espaço inferior livre é consequência do conteúdo restante, sem redução tipográfica ou texto de preenchimento. |

O título mais extenso e as chamadas locais alteraram o fluxo de quatro para cinco páginas. Foi mantido o limite oficial sem diminuir fontes ou dimensões dos gráficos. A quebra antes de Resultados evita um título isolado; manter as Conclusões juntas evita sua fragmentação entre páginas. As imagens de conferência e os dados geométricos estão em `paper/qa_final_references/render/` e [document_checks.json](<C:/Users/Altair/Documents/Dynamic World x MapBiomas/Dynamic-World-MapBiomas/paper/qa_final_references/document_checks.json>).

## Arquivos produzidos ou atualizados

- [DOCX mestre final](<C:/Users/Altair/Documents/Dynamic World x MapBiomas/Dynamic-World-MapBiomas/paper/manuscript_space_week_nordeste_2026_final_title_references.docx>).
- [PDF exportado do mestre](<C:/Users/Altair/Documents/Dynamic World x MapBiomas/Dynamic-World-MapBiomas/paper/manuscript_space_week_nordeste_2026_final_title_references.pdf>).
- [Texto editorial derivado do DOCX](<C:/Users/Altair/Documents/Dynamic World x MapBiomas/Dynamic-World-MapBiomas/paper/manuscript_space_week_nordeste_2026_final_title_references.md>).
- [Script documental de construção e exportação](<C:/Users/Altair/Documents/Dynamic World x MapBiomas/Dynamic-World-MapBiomas/paper/build_final_title_references.py>), executado com `--render`.
- [Validador documental e auditoria bidirecional](<C:/Users/Altair/Documents/Dynamic World x MapBiomas/Dynamic-World-MapBiomas/paper/verify_final_title_references.py>).
- [Checklist manual atualizado](<C:/Users/Altair/Documents/Dynamic World x MapBiomas/Dynamic-World-MapBiomas/paper/submission_manual_checklist.md>), com título definitivo, arquivo final e autoria confirmada. Sua versão anterior foi preservada na pasta de QA.
- Este relatório e evidências em `paper/qa_final_references/`.

As versões anteriores dos manuscritos e seus scripts foram preservados. Nenhum commit, push, preenchimento ou envio de artigo foi realizado. Resta ao autor aprovar pessoalmente esta versão e efetuar o preenchimento/submissão manual; não há pendência bibliográfica ou editorial comprovada nesta revisão dirigida.

**FINAL TITLE AND REFERENCES: VERIFIED**
