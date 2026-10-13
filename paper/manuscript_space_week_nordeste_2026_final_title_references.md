ANÁLISE ESPACIAL E PROBABILÍSTICA DA DISCORDÂNCIA NO MAPEAMENTO DE LAVOURAS DO MATOPIBA: DYNAMIC WORLD E MAPBIOMAS

Randerson Sousa de Sá Nunes

Instituto Federal de Educação, Ciência e Tecnologia do Maranhão (IFMA) - Campus Caxias

Bacharelado em Ciência da Computação - Caxias - MA, Brasil

randerson.sdsn@gmail.com

RESUMO

Este estudo caracteriza a discordância de lavouras entre Dynamic World V1 e MapBiomas Cobertura 10 m, Coleção 4, em 2025, no MATOPIBA. Compararam-se produtos cartográficos sem referência de campo independente, em uma população elegível de 52,34 milhões de hectares com pelo menos oito meses válidos. O censo foi complementado por amostras probabilísticas estratificadas de 20.000 e 40.000 pontos, ponderadas pelas probabilidades de inclusão. A discordância censitária foi de 14,2852% por área e 14,3110% por pixels. Com reamostragem espacial em blocos de 30 km e 1.999 réplicas, as células discordantes apresentaram maior entropia anual normalizada (ΔH = +0,0162), maior divergência Jensen-Shannon temporal (ΔJSD = +0,0075) e menor estabilidade categórica relativa à classe anual (ΔS = -0,0790). A proporção amostral ponderada de discordância em distâncias inferiores a 30 m foi 3,87 vezes a observada a pelo menos 250 m. Os critérios conjuntos de baixa ambiguidade, baixa heterogeneidade temporal, alta estabilidade e afastamento das bordas selecionaram 207 casos na amostra principal, equivalentes a 4,2773% dos pixels discordantes estimados. Os padrões descrevem associações observacionais e não determinam qual produto está correto.

Palavras-chave - Dynamic World; MapBiomas; MATOPIBA; discordância temática; estabilidade temporal.

ABSTRACT

This study characterizes cropland disagreement between Dynamic World V1 and MapBiomas 10 m land cover, Collection 4, for 2025 in MATOPIBA, Brazil. The comparison covers 52.34 million eligible hectares with at least eight valid months and uses no independent field reference. A wall-to-wall census was complemented by stratified probability samples of 20,000 and 40,000 points, weighted by inverse inclusion probabilities. Census disagreement was 14.2852% by area and 14.3110% by pixels. Spatial block bootstrap inference with 30 km blocks and 1,999 replicates indicated higher normalized annual entropy (ΔH = +0.0162), higher temporal Jensen-Shannon divergence (ΔJSD = +0.0075), and lower categorical stability relative to the annual class (ΔS = -0.0790) in disagreeing cells. Weighted sample disagreement below 30 m from thematic edges was 3.87 times that observed at distances of at least 250 m. Joint criteria of low ambiguity, low temporal heterogeneity, high stability, and edge separation selected 207 cases in the main sample, representing 4.2773% of estimated disagreeing pixels. These observational associations neither establish causal mechanisms nor identify which product is correct.

Key words - Dynamic World; MapBiomas; MATOPIBA; thematic disagreement; temporal stability.

1. INTRODUÇÃO

A expansão de lavouras no Cerrado e no MATOPIBA foi documentada [1] e motiva o monitoramento territorial. Dynamic World (DW) V1 produz nove probabilidades de cobertura por observação Sentinel-2 [2]; MapBiomas Cobertura 10 m, Coleção 4, disponibiliza mapas anuais [3]. Diferenças de legenda, agregação temporal e suporte espacial podem gerar discordância entre esses produtos. Ambos utilizam imagens Sentinel-2 [2,3] e compartilham parte da base observacional.

Sem referência de campo independente, concordância não prova correção e discordância não identifica erro de um produto. Adota-se uma comparação simétrica dos regimes temáticos e da discordância de quantidade e alocação [4]. O objetivo é caracterizar onde os produtos discordam sobre lavouras em 2025 e como essa discordância se associa a indicadores do DW e à proximidade de bordas.

Avaliam-se quatro hipóteses operacionais: H1, maior entropia anual nas células discordantes; H2, maior divergência probabilística temporal (H2a) e menor estabilidade categórica (H2b); H3, maior proporção de discordância próxima às bordas que no interior; e H4, existência de discordâncias que satisfazem conjuntamente baixa ambiguidade, baixa heterogeneidade temporal, alta estabilidade e distância de pelo menos 30 m às bordas.

2. MATERIAL E MÉTODOS

2.1. Domínio e produtos

O domínio operacional compreende os 337 municípios do MATOPIBA, nos estados MA, TO, PI e BA, conforme a geometria congelada. A população elegível contém 5.354.669.418 células de resolução nominal de 10 m e 52.342.114,75 ha. Exige-se classificação válida nos dois produtos e pelo menos oito meses válidos de DW em 2025; meses ausentes não são imputados.

No MapBiomas, o crosswalk principal define lavoura pelas classes {19,36}, lavoura temporária e perene [3]. As classes 21 (mosaico de usos) e 18 (agricultura agregada, caso presente), códigos desconhecidos e ausência de dados são excluídos; as demais classes válidas integram não-lavoura. No DW, lavoura corresponde a crops (índice 4) [2]. A comparação ocorre na grade nativa MapBiomas (EPSG:4326, escala nominal de 10 m), com probabilidades DW interpoladas bilinearmente e categorias MapBiomas preservadas. Operações métricas de distância e blocos utilizam EPSG:5880.

2.2. Agregação e indicadores

Neste estudo, observações DW do mesmo dia são compostas por média neutra; as médias diárias formam as médias mensais. O vetor anual atribui igual peso aos meses válidos. A classe anual é o argmax das nove probabilidades após alinhamento e normalização, e não o modo das classes mensais. O vetor anual canônico define os regimes e a entropia H; a série mensal harmonizada define JSD e S.

Para um vetor unitário p, a entropia normalizada de Shannon [5] é H(p) = -Σ p(k) ln p(k) / ln 9, com k = 1,...,9 e 0 ln 0 = 0. A JSD temporal generalizada [6] é JSD = H(pmed) - (1/M)Σ H(p(m)), em que pmed é a média dos vetores mensais e M é o número de meses válidos. A normalização é por ln 9, não por ln M. A estabilidade é S = (1/M)Σ I[c(m) = c(anual)], isto é, a fração dos meses cujo argmax coincide com a classe anual canônica. S mede persistência dessa decisão anual e não a frequência do modo mensal.

A distância d é o mínimo das distâncias euclidianas às bordas das máscaras binárias lavoura/não-lavoura do DW e do MapBiomas. Consideram-se transições entre vizinhos de conectividade oito, excluindo células mascaradas. O cálculo é truncado em 250 m: a categoria ≥250 m reúne distâncias iguais ou superiores a esse limite. Bordas temáticas raster não representam limites cadastrais de parcelas.

2.3. Amostragem e inferência

A seleção aleatória sem reposição [7] utiliza 16 estratos científicos (estado × regime) e 410 subestratos operacionais ativos (hs). A amostra de 40.000 pontos tem π(40k,hs) = n(40k,hs)/N(hs), com n ≥ 1; a amostra principal de 20.000 é aninhada, selecionada por ordenação determinística dentro de cada estrato científico, com probabilidade marginal π(20k) = 0,5π(40k). Pesos de desenho w = 1/π expandem pixels; pesos a/π expandem a área da célula a. Os contrastes, a regressão e H4 usam pesos de desenho; percentuais de área são identificados separadamente.

AA significa lavoura nos dois produtos; AN, lavoura apenas no MapBiomas; NA, lavoura apenas no DW; e NN, não-lavoura nos dois. A discordância D vale 1 em AN ou NA e 0 em AA ou NN. O censo territorial fornece proporções sem erro amostral da população elegível.

A inferência usa uma adaptação espacial do bootstrap em blocos para observações dependentes [8], com blocos de 30 × 30 km, 1.999 réplicas e semente 25. O semivariograma exponencial de D estimou alcance prático de 25,62 km, arredondado ao múltiplo superior de 5 km. Os intervalos espaciais de 95% são percentis 2,5 e 97,5 das réplicas de blocos inteiros, sem fixar as margens dos estratos; representam variabilidade sob reamostragem espacial e não erro amostral do censo.

O modelo logístico ponderado ajusta D por H, JSD, S, distância linear d e estado (BA como referência). Os odds ratios (OR) expressam razões de chances, não razões de probabilidades. H4 exige D = 1, H ≤ Q1(H), JSD ≤ Q1(JSD), S ≥ Q3(S) e d ≥ 30 m; os quartis são ponderados pelo desenho e calculados separadamente em cada amostra.

3. RESULTADOS

| Regime / estado | Área censitária(ha) | Censo área(%) | Censo pixels(%) | Amostra 20kpixels (%) |
| AA | 1.274.055,76 | 2,4341 | 2,4401 | 2,4398 |
| AN | 5.044.314,26 | 9,6372 | 9,6466 | 9,6557 |
| NA | 2.432.862,97 | 4,6480 | 4,6644 | 4,6592 |
| NN | 43.590.881,76 | 83,2807 | 83,2489 | 83,2454 |
| D = AN + NA | 7.477.177,23 | 14,2852 | 14,3110 | 14,3148 |
| MA (D) | 1.093.012,71 | 10,9703 | 10,9896 | 10,9757 |
| TO (D) | 1.338.414,64 | 5,9059 | 5,9038 | 5,9012 |
| PI (D) | 1.639.895,31 | 21,8114 | 21,7832 | 21,7956 |
| BA (D) | 3.405.854,56 | 27,9214 | 27,9341 | 27,9519 |

Tabela 1. Regimes e discordância por estado em 2025. Censo: quadro elegível. Amostra: proporções ponderadas por 1/π. Linhas estaduais usam o domínio elegível de cada estado como denominador; censo sem IC amostral.

A discordância censitária soma 7.477.177,23 ha (14,2852% da área elegível) e 766.304.630 pixels (14,3110%). A Tabela 1 distingue esses parâmetros dos percentuais amostrais ponderados por pixels. A estimativa de área da amostra principal é 7.479.568,87 ha e 14,2897%; a proximidade com o censo decorre também da estratificação por regime, não de validação independente. A decomposição em área [4] resulta, neste censo, em 4,99 pontos percentuais de discordância de quantidade e 9,30 de alocação.

Figura 1. Amostra principal: (A) proporções de pixels AA, AN, NA e NN; (B) proporção de discordância por estado. Pesos de desenho 1/π. Valores amostrais, sem interpretação de acurácia ou de omissão de um produto.

A Figura 1 resume as estimativas amostrais por regime e estado. No censo por área, BA apresenta 27,9214% de discordância, PI 21,8114%, MA 10,9703% e TO 5,9059%. O predomínio de NN caracteriza o domínio territorial elegível, que inclui áreas de não-lavoura.

Os contrastes H1–H3 e os OR ajustados são apresentados na Tabela 2. H1 e H2 mostram maior H e JSD e menor S nas células discordantes; seus intervalos espaciais excluem zero. Em H3, a proporção é 45,91% para d < 30 m e 11,87% para d ≥ 250 m, com razão 3,87. A Figura 2 apresenta os intervalos por faixa e evidencia a ausência de monotonicidade estrita: 30-60 m tem 45,77%, frente a 44,59% em 10-30 m.

H4 seleciona 207 de 5.143 pontos discordantes na amostra principal (4,0249% bruto; 4,2773% ponderado por pixels) e 404 de 10.286 na amostra de 40.000 (3,9277% bruto; 4,1687% ponderado). Os indicadores de ambiguidade e estabilidade pertencem exclusivamente ao DW. Esses casos não constituem erros confirmados.

| Contraste / termo | Escala | Estimativa | IC espacial 95% |
| H1: ΔH | D = 1 menos D = 0 | +0,0162 | [+0,0103; +0,0221] |
| H2a: ΔJSD | D = 1 menos D = 0 | +0,0075 | [+0,0047; +0,0102] |
| H2b: ΔS | D = 1 menos D = 0 | -0,0790 | [-0,0974; -0,0599] |
| H3: borda / interior | <30 m / ≥250 m | 3,87 | Por faixa: Figura 2 |
| OR: distância | +100 m | 0,360 | [0,319; 0,404] |
| OR: entropia H | +0,10 | 1,421 | [1,036; 1,988] |
| OR: estabilidade S | +0,10 | 0,925 | [0,861; 0,992] |
| OR: JSD temporal | +0,01 | 0,987 | [0,914; 1,059] |
| OR: PI / BA | BA: referência | 0,798 | [0,507; 1,212] |
| OR: MA / BA | BA: referência | 0,378 | [0,242; 0,575] |
| OR: TO / BA | BA: referência | 0,160 | [0,114; 0,225] |

Tabela 2. Contrastes ponderados H1–H3 e regressão logística multivariada. IC percentis do bootstrap espacial (30 km; 1.999 réplicas). H3 apresenta razão pontual; IC por faixa na Figura 2. OR ajustados por H, JSD, S, d linear e estado.

Figura 2. H3: pontos são proporções ponderadas por 1/π; barras são IC de 95% do bootstrap espacial. Faixas [a,b), em metros; ≥250 reúne distâncias truncadas. A borda é a mais próxima entre DW e MapBiomas.

A regressão associa distância e S inversamente à discordância, e H positivamente (Tabela 2). O IC da JSD inclui 1; essa imprecisão da associação ajustada não estabelece mediação causal nem ausência de utilidade preditiva. Para PI/BA, o IC analítico é [0,709; 0,900], mas o espacial é [0,507; 1,212]. Incluir 1 não demonstra igualdade entre os estados.

Na amostra de 40.000, os contrastes mantêm os sinais: ΔH = +0,0167, ΔJSD = +0,0071 e ΔS = -0,0774. A discordância ponderada por pixels é 14,2782% sob o crosswalk estrito {19} e 12,1255% no subconjunto MapBiomas estável de 2017-2025 (17.957 pontos). Este último restringe a população analisada; não substitui o resultado territorial principal.

4. DISCUSSÃO

A associação com bordas é compatível com diferenças de suporte e mistura espectral; a associação temporal admite hipóteses ligadas à sazonalidade e às decisões dos classificadores. O desenho observacional não identifica esses mecanismos. Não foram medidos calendário agrícola, fenologia ou limites de parcelas, e o indicador S também depende da agregação vetorial anual. Não se pode atribuir o restante das discordâncias a causas explicadas pelos filtros de H4.

Há uma limitação de suporte temporal residual: a média mensal harmonizada difere do vetor anual canônico. A comparação dos dois suportes nos 40.000 pontos registra diferença absoluta média de 0,004983 nas probabilidades, mudança de argmax em 8,24% e inversão lavoura/não-lavoura em 2,59%. A ordem da agregação e da interpolação com máscaras variáveis pode produzir essa diferença. Os indicadores temporais e a classe anual têm essas definições distintas; os resíduos não são prova de mudança no terreno.

A elegibilidade de pelo menos oito meses restringe a inferência às células observáveis e não autoriza extrapolação às áreas excluídas. O censo não tem erro amostral, mas continua sujeito às limitações dos produtos e do processamento. Os intervalos do bootstrap dependem da representação espacial e da escolha de blocos. H4 delimita casos para eventual validação independente, sem transferir probabilidades ou confiança do DW ao MapBiomas.

5. CONCLUSÕES

Em 2025, os produtos discordam sobre lavouras em 14,2852% da área elegível do MATOPIBA. As discordâncias associam-se a maior ambiguidade e heterogeneidade temporal do DW, menor persistência categórica e maior proximidade de bordas. H4 identifica 207 e 404 casos nas amostras principal e robusta, sob critérios relativos a cada distribuição. A análise caracteriza a divergência cartográfica sem atribuir superioridade de acurácia, causalidade ou correção a qualquer produto.

6. REFERÊNCIAS

[1] S. A. Spera et al. Land-use change affects water recycling in Brazil’s last agricultural frontier. Global Change Biology, 22(10):3405-3413, 2016. DOI: 10.1111/gcb.13298.

[2] C. F. Brown et al. Dynamic World, Near real-time global 10 m land use land cover mapping. Scientific Data, 9:251, 2022. DOI: 10.1038/s41597-022-01307-4.

[3] MapBiomas. Cobertura 10 m, Coleção 4, série 2017-2025. Documentação e acesso aos dados. Acesso em 12 out. 2026.

[4] R. G. Pontius Jr. e M. Millones. Death to Kappa: birth of quantity disagreement and allocation disagreement for accuracy assessment. International Journal of Remote Sensing, 32(15):4407-4429, 2011. DOI: 10.1080/01431161.2011.552923.

[5] C. E. Shannon. A mathematical theory of communication. Bell System Technical Journal, 27(3):379-423, 1948. DOI: 10.1002/j.1538-7305.1948.tb01338.x.

[6] J. Lin. Divergence measures based on the Shannon entropy. IEEE Transactions on Information Theory, 37(1):145-151, 1991. DOI: 10.1109/18.61115.

[7] P. Olofsson et al. Good practices for estimating area and assessing accuracy of land change. Remote Sensing of Environment, 148:42-57, 2014. DOI: 10.1016/j.rse.2014.02.015.

[8] H. R. Künsch. The jackknife and the bootstrap for general stationary observations. Annals of Statistics, 17(3):1217-1241, 1989. DOI: 10.1214/aos/1176347265.
