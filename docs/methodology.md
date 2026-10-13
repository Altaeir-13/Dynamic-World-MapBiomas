# Metodologia efetivamente executada

## Domínio e produtos

A lista oficial IBGE MATOPIBA 2021 contém 337 municípios. Suas geometrias municipais de 2025 foram dissolvidas e preservadas em GeoJSON; EPSG:4326 na referência vetorial. A área geodésica congelada é aproximadamente 73.082.921,02 ha, distinta da área em EPSG:5880 e da área elegível censitária. Não se usam os quatro estados completos. Os contornos e a lista têm hashes no manifesto científico.

Dynamic World V1 fornece nove bandas na ordem `water, trees, grass, flooded_vegetation, crops, shrub_and_scrub, built, bare, snow_and_ice`, em 2025. O comparador é `projects/mapbiomas-public/assets/brazil/lulc_10m/collection4/mapbiomas_10m_collection4_coverage_v1`, `classification_2025`; a série 2017–2025 aparece somente na robustez histórica.

## Crosswalk e elegibilidade

DW lavoura é argmax anual igual a 4 (`crops`), não `p(crops)>0,5` nem modo dos labels originais. MapBiomas lavoura são códigos 19 e 36; outras classes válidas são não lavoura, inclusive 15 e 9. Códigos 18/21, desconhecidos e pixels sem cobertura válida são mascarados na comparação principal. Água e áreas não vegetadas não são excluídas genericamente. A sensibilidade estrita considera somente 19 como lavoura.

Regimes: AA=(MB1,DW1), AN=(MB1,DW0), NA=(MB0,DW1), NN=(MB0,DW0). Discordância D=1 em AN/NA. Cobertura temporal elegível exige pelo menos oito meses. A emenda [Checkpoint 3D](protocol_amendment_checkpoint_3d.md) documenta o congelamento dessa regra; não houve fallback para seis na população final. Meses ausentes não são imputados.

## Suporte e composição

O módulo `src/gee/dw_annual.py` fixa o domínio-fonte MATOPIBA + 5.000 m e o registro de datas `data/reference/dw_2025_monthly_dates.json`. O domínio constante evita que a composição mude com a fatia usada para redução/exportação. A grade final é MapBiomas EPSG:4326, nominal 10 m, transformação `[8.983152841195215e-05, 0, -75.62655865569857, 0, -8.983152841195215e-05, 6.763595437192701]`. A grade angular implica áreas de pixel variáveis: censos usam `ee.Image.pixelArea()` e pesos de área usam o valor materializado por ponto.

Duplicatas do mesmo dia são compostas por média neutra. O composto mensal é a média dos dias válidos; o anual é a média de meses válidos com pesos iguais. Não se seleciona a observação mais confiante nem se pondera mês por número de cenas. O anual é alinhado por bilinear nas probabilidades, renormalizado por sua soma e então classificado por argmax. Valores categóricos usam vizinho mais próximo.

A extração inicial `11_extract_analytical_dataset.py` fornece o vetor anual autoritativo, classes, distâncias e série MB histórica. Sua série mensal é RAW e **não é produto final**. Em seguida, `12_extract_harmonized_bilinear_monthly.py` aplica bilinear/reproject à composição de cada mês antes de amostrar. Define mês válido por `n_days>0` e soma bruta das nove probabilidades `>0,01`; preserva contagens e soma anterior à renormalização. Os parquets finais contêm 40.000 registros anuais e 480.000 registros mensais, incluindo meses inválidos marcados, não imputados para as métricas.

## Indicadores

Entropia normalizada: `H(p) = -Σ p_k ln(p_k) / ln(9)`, com contribuição zero para p=0. `entropy_annual` usa o vetor anual canônico. `entropy_temporal_mean` usa a média dos vetores mensais válidos e normalizados. `entropy_monthly_mean` é a média das entropias mensais. **JSD final = H(média mensal harmonizada) − média H(mês)**, limitada inferiormente em zero para resíduo numérico. Não substituir o primeiro termo por `entropy_annual`: essas construções não são idênticas.

Estabilidade `S = número de meses cujo argmax coincide com a classe anual canônica / número de meses válidos`. A referência é a classe anual, não a moda das classes mensais. `top2_margin` e `competitor_class` são diagnósticos auxiliares.

Bilinear espacial e média temporal com máscaras variáveis não comutam em geral. A discrepância residual materializada é 3.296 mudanças de argmax (8,24%) e 1.035 inversões lavoura/não lavoura (2,5875%) em 40.000 pontos. É uma limitação do suporte e da ordem de operações; a evidência não prova neutralidade causal ou insensibilidade a qualquer processamento alternativo.

## Bordas e amostragem

As bordas crop/noncrop dos dois produtos são obtidas no suporte fixo, mascarando classes excluídas, conectividade 8; distância via `fastDistanceTransform` diretamente sobre edge=1. Operações métricas usam EPSG:5880. São materializadas distâncias MB, DW e seu mínimo simétrico, truncadas em 250 m. As faixas são `[0,10)`, `[10,30)`, `[30,60)`, `[60,100)`, `[100,250)` e `≥250 m`. O último grupo contém os valores truncados em 250, não distâncias exatas além do limite.

Censo canônico: 182 fatias elegíveis, 410 subestratos estado × regime × fatia e 16 estratos estado × regime. Cotas principais: piso de 400 por estrato ativo, restante proporcional com alocação Hamilton. Mestre 40k e principal 20k aninhada, seed raiz 25. A alocação corrigida garante n_robust_hs≥1 em todo subestrato com população positiva; antigas alocações com pi=0 são inválidas para inferência final.

`pi_robust_hs = n_robust_hs / N_hs_exact`; peso de desenho = 1/pi. O subconjunto principal é obtido por ranking determinístico SHA-256 de seed, estado, regime e coordenadas; a implementação registra `pi_main = pi_robust × 0,5` e peso correspondente. Peso de área = `pixel_area_m2/pi`, convertido para hectares nas estimativas. Preserve coordenadas, pertencimento e pesos materializados; seed sozinho não garante reproduzir os mesmos pontos em futuras versões do GEE.

## Hipóteses e inferência

H1 compara H dos discordantes e concordantes. H2 compara JSD e S. H3 compara taxas por distância e borda <30 m com interior ≥250 m; há ressalva de não monotonicidade local. H4 descreve D=1 com H≤Q1 ponderado, JSD≤Q1 ponderado, S≥Q3 ponderado e distância≥30 m. Quartis são calculados separadamente na principal e na mestre; 20k e 40k não compartilham automaticamente os mesmos cortes.

Regressão final: `logit P(D=1) ~ entropy_annual + jsd_temporal + stability + distance_edge_min_m + estado`, referência BA. É um GLM binomial com pesos de desenho normalizados pela média (`freq_weights`); distância linear no modelo principal. OR apresentados por +0,10 H, +0,01 JSD, +0,10 S, +100 m e contrastes estaduais. IC analíticos são suplementares; os IC espaciais estão em tabelas próprias. Intervalo que inclui 1 não prova equivalência nem ausência de utilidade preditiva.

Bootstrap: semivariograma exponencial no indicador D em coordenadas métricas, alcance prático materializado 25,62164 km; arredondamento superior a múltiplo de 5 km → **30 km**. Reamostragem em blocos, 1.999 réplicas, seed 25, IC percentis 2,5/97,5%. Sensibilidades de bloco 10/20/40 km; não confundir bloco principal com 20 km.

Robustez final disponível: 40k, crosswalk {19}, subconjunto MB estável 2017–2025, sensibilidade do tamanho de bloco e diagnóstico da harmonização. A agregação 30 m existe como intenção/código de teste histórico, mas uma suíte final completa de resultados nessa escala não foi identificada. Não é apresentada como executada na versão final.

## Limites interpretativos

Não há validação independente em campo. Os mapas compartilham observações Sentinel-2; suas probabilidades e erros não são independentes nem calibrados como correção. H4 é filtro operacional descritivo, não prova de erro de um mapa. Não há identificação de causalidade, cultura específica ou fenologia validada. Elegibilidade, máscaras, grid, bilinear e distância truncada limitam a generalização. As escolhas e ressalvas estão preservadas com os resultados, sem novos cálculos nesta organização.
