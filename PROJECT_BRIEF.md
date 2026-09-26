# PROJECT_BRIEF.md — Dynamic World × MapBiomas no MATOPIBA

> **Versão metodológica definitiva — 26/09/2026**  
> Este documento substitui integralmente todas as versões anteriores do `PROJECT_BRIEF.md` e todas as decisões metodológicas antigas que entrem em conflito com ele.  
> Foi consolidado após o desenho inicial, revisões adversariais, 12 Deep Research independentes e 3 pesquisas finais de adjudicação metodológica.  
> A partir desta versão, a prioridade é **execução experimental**, não expansão teórica do projeto.

---

# 0. Status do projeto

**Evento-alvo:** Space Week Nordeste 2026  
**Prazo operacional:** aproximadamente 5 dias para implementação, análise, escrita e submissão  
**Formato esperado:** artigo curto / resumo estendido de aproximadamente 5 páginas  
**Stack principal:** Google Earth Engine + Python  
**Treinamento de novo modelo:** não haverá  
**GPU:** não necessária  
**Google Cloud Project / Earth Engine Project:** `dynamicworld-x-mapbiomas`  
**Dynamic World:** acesso já validado  
**MapBiomas 10 m:** produto 2025 identificado e disponível  
**Repositório:** já criado e versionado com Git  
**Antigravity:** workspace configurado com Rule e Skills locais

## Estado atual

A revisão metodológica está encerrada.

O projeto deve agora seguir:

```text
BRIEF DEFINITIVO
      ↓
PROTÓTIPO TÉCNICO
      ↓
AUDITORIA HUMANA
      ↓
CONGELAMENTO DOS ARTEFATOS
      ↓
EXECUÇÃO PRINCIPAL
      ↓
ROBUSTEZ
      ↓
FIGURAS E TABELAS
      ↓
ARTIGO
```

Não iniciar nova revisão bibliográfica ampla salvo se surgir uma falha concreta que impeça a execução.

---

# 1. Regra epistemológica central

Este estudo **não é uma avaliação de acurácia do Dynamic World usando MapBiomas como verdade**.

Dynamic World e MapBiomas são dois produtos modelados, com:

- metodologias diferentes;
- temporalidades diferentes;
- ontologias/legendas diferentes;
- pós-processamentos diferentes;
- possíveis erros próprios;
- dependência parcial de informações Sentinel-2.

Portanto:

> **concordância não prova correção, e discordância não identifica qual produto está errado.**

É proibido usar como linguagem principal:

- ground truth;
- verdade de referência;
- falso positivo;
- falso negativo;
- verdadeiro positivo;
- verdadeiro negativo;
- erro do Dynamic World em relação ao MapBiomas;
- precision/recall/F1 de um produto contra o outro;
- producer's accuracy;
- user's accuracy;
- Kappa como métrica principal de concordância.

Usar:

- concordância interproduto;
- discordância interproduto;
- discordância direcional;
- sobreposição;
- discordância de quantidade;
- discordância de alocação;
- ambiguidade probabilística;
- instabilidade temporal;
- sensibilidade ao suporte espacial.

---

# 2. Tema da pesquisa

## Tema geral

GeoAI e sensoriamento remoto aplicados ao mapeamento de lavouras em uma fronteira agrícola tropical.

## Tema específico

**Caracterização probabilística, temporal e espacial das discordâncias de lavouras entre Google Dynamic World V1 e MapBiomas Cobertura 10 m no MATOPIBA em 2025.**

## Título provisório em português

**Quando mapas de lavouras discordam: estrutura probabilística e dinâmica temporal do Dynamic World em comparação ao MapBiomas no MATOPIBA**

## Título provisório em inglês

**When Cropland Maps Disagree: Probabilistic Structure and Temporal Dynamics of Dynamic World versus MapBiomas in MATOPIBA**

Alternativa conservadora:

**Probabilistic, Temporal and Spatial Characterization of Dynamic World–MapBiomas Cropland Disagreement in MATOPIBA, Brazil**

---

# 3. Pergunta de pesquisa oficial

> **Em 2025, onde e sob quais condições probabilísticas, temporais e espaciais Google Dynamic World V1 e MapBiomas Cobertura 10 m discordam na identificação de lavouras no MATOPIBA? As discordâncias apresentam maior ambiguidade probabilística, maior heterogeneidade temporal e maior proximidade de bordas? Existem discordâncias internamente estáveis e de baixa ambiguidade que persistem no interior das manchas?**

A pergunta possui dois níveis complementares:

1. **wall-to-wall:** qual é a magnitude e a geografia da concordância/discordância em todo o domínio elegível?
2. **amostral:** quais características probabilísticas, temporais e espaciais distinguem os regimes de concordância e discordância?

---

# 4. Hipóteses

## H1 — Ambiguidade probabilística

Pontos discordantes apresentarão maior entropia anual do vetor de probabilidades Dynamic World:

\[
H_{\mathrm{discordante}} > H_{\mathrm{concordante}}
\]

## H2 — Instabilidade temporal

Pontos discordantes apresentarão:

- maior heterogeneidade temporal das distribuições probabilísticas;
- menor estabilidade categórica mensal.

\[
JSD_{\mathrm{discordante}} > JSD_{\mathrm{concordante}}
\]

\[
S_{\mathrm{discordante}} < S_{\mathrm{concordante}}
\]

## H3 — Efeito de borda

A discordância diminuirá conforme aumenta a distância à borda agrícola mais próxima identificada por qualquer um dos produtos:

\[
P(D=1\mid d) \downarrow \quad \text{quando } d \uparrow
\]

## H4 — Discordância robusta internamente

Existirá um subconjunto de discordâncias com simultaneamente:

- baixa entropia anual;
- baixa heterogeneidade temporal;
- alta estabilidade categórica;
- distância relevante das bordas.

Esses casos são cientificamente importantes porque não são facilmente explicados apenas por ambiguidade do classificador, sazonalidade ou mixed pixels de borda.

Não chamar esse grupo de “correto com alta confiança”.

Nome recomendado:

> **discordâncias de baixa ambiguidade e alta estabilidade**

---

# 5. Contribuição científica pretendida

A contribuição **não** é:

- uma nova arquitetura de IA;
- um novo classificador;
- um novo mapa agrícola;
- uma validação absoluta do Dynamic World;
- uma prova de superioridade do MapBiomas;
- uma classificação por cultura específica;
- uma análise causal.

A contribuição é:

> **um diagnóstico interproduto, probabilístico, temporal e espacial da discordância de lavouras entre um produto global near-real-time e um produto anual especializado no Brasil.**

O estudo deve mostrar:

1. a extensão e a geografia wall-to-wall dos quatro regimes de concordância;
2. como a entropia do Dynamic World varia entre concordância e discordância;
3. como a dinâmica intra-anual se relaciona à discordância;
4. como bordas espaciais se relacionam à discordância;
5. quais discordâncias permanecem mesmo em condições internas estáveis;
6. quais classes Dynamic World competem com `crops` nesses casos.

---

# 6. Domínio espacial

## 6.1 Área oficial

Usar o **MATOPIBA completo**, e não apenas sua porção nordestina.

O domínio é o polígono oficialmente/praticamente utilizado para MATOPIBA, contendo:

- Tocantins;
- porções do Maranhão;
- porções do Piauí;
- porções da Bahia.

Não usar a união dos quatro estados inteiros.

Área nominal histórica: aproximadamente 73,17 milhões de hectares.

## 6.2 Geometria congelada

A geometria efetivamente utilizada deve ser armazenada e versionada.

Salvar:

```text
data/reference/matopiba_boundary.geojson
data/reference/matopiba_municipalities.csv
```

Registrar:

- fonte;
- data de obtenção;
- versão;
- CRS original;
- códigos IBGE dos municípios;
- SHA-256;
- área calculada da geometria utilizada.

O valor de área publicado no artigo deve ser calculado a partir da geometria congelada, não copiado de uma descrição externa.

## 6.3 Balsas

Balsas/MA **não é o domínio final**.

Pode ser utilizado como:

- área de inspeção visual;
- área de depuração;
- uma das janelas do protótipo.

Não extrapolar resultados locais de Balsas para o MATOPIBA.

---

# 7. Período

## Ano principal

**2025**

Intervalo Dynamic World:

```text
[2025-01-01, 2026-01-01)
```

Não converter o estudo principal para ano-safra.

A sazonalidade agrícola será analisada por meio da estrutura mensal do Dynamic World.

## Sensibilidade temporal MapBiomas

A série 2017–2025 poderá ser utilizada apenas para uma análise de sensibilidade de estabilidade do MapBiomas.

A análise principal continua sendo 2025.

---

# 8. Produtos

## 8.1 Google Dynamic World V1

Asset:

```text
GOOGLE/DYNAMICWORLD/V1
```

Bandas probabilísticas:

```text
water
trees
grass
flooded_vegetation
crops
shrub_and_scrub
built
bare
snow_and_ice
```

Banda categórica:

```text
label
```

Papel:

- produto probabilístico principal;
- fonte da estrutura temporal intra-anual;
- fonte de entropia, heterogeneidade temporal, estabilidade e classes concorrentes.

## 8.2 MapBiomas Cobertura 10 m — Coleção 4

Asset operacional esperado:

```text
projects/mapbiomas-public/assets/brazil/lulc_10m/collection4/mapbiomas_10m_collection4_coverage_v1
```

Banda:

```text
classification_2025
```

Antes da execução final, o agente deve confirmar que esses identificadores continuam válidos no catálogo.

Papel:

- segundo produto da comparação interproduto;
- classificação anual especializada para o Brasil.

MapBiomas nunca deve ser chamado de ground truth.

## 8.3 Não adicionar datasets ao núcleo

Fora do núcleo:

- TerraClass;
- WorldCover;
- Esri Land Cover;
- WorldCereal;
- dados de campo inexistentes;
- novos classificadores;
- novo deep learning.

Dados de maior resolução só poderiam aparecer em auditoria visual exploratória, nunca como novo eixo principal do artigo nesta semana.

---

# 9. Conceito-alvo: cropland/lavoura, não “agropecuária”

O alvo científico não deve ser chamado genericamente de “agropecuária”.

O conceito é:

> **cropland / lavoura cultivada**

Isso evita equiparar `crops` a:

- pastagem;
- silvicultura;
- mosaicos de uso;
- qualquer área apenas por ser antropizada.

---

# 10. Crosswalk definitivo

## 10.1 Dynamic World

```text
CROP     = classe anual derivada = crops
NONCROP  = todas as demais classes
```

A classe anual Dynamic World será obtida por `argmax` do vetor anual de nove probabilidades, e não por modo bruto de `label`.

Não usar limiar arbitrário `p(crops) > 0.5` para definir a classe principal.

## 10.2 MapBiomas — crosswalk principal

Crosswalk principal:

```text
CROP:
- 19 — Lavoura Temporária
- 36 — Lavoura Perene

NONCROP:
- classes válidas de cobertura que não são lavouras,
  incluindo Pastagem (15) e Silvicultura (9)

AMBÍGUA / EXCLUÍDA DA COMPARAÇÃO BINÁRIA PRINCIPAL:
- 21 — Mosaico de Usos
- 18 — Agricultura, somente se aparecer como valor-pixel agregado independente
- códigos desconhecidos ou não documentados
```

A legenda oficial da **Cobertura 10 m Coleção 4** deve ser verificada antes da primeira execução.

Não usar legenda da antiga Coleção 4 de 30 m.

## 10.3 Sensibilidade de crosswalk

Executar uma única sensibilidade sem alterar a amostra:

```text
CROP_STRICT:
- 19 — Lavoura Temporária
```

A classe 36 passa a não integrar o alvo estrito.

Se o código 18 existir como valor-pixel real na banda 2025:

- excluí-lo da análise principal;
- documentar sua área;
- incluí-lo apenas em uma sensibilidade ampla previamente declarada, se o custo for trivial.

## 10.4 Mosaico de Usos

Código 21 permanece fora da comparação binária principal.

Não classificá-lo silenciosamente como crop ou noncrop.

Reportar sua área excluída.

## 10.5 Regra de congelamento

O crosswalk é aprovado **antes de observar entropia, estabilidade, borda ou resultados das hipóteses**.

Depois do congelamento:

> **é proibido alterar o crosswalk para aumentar concordância ou melhorar significância.**

---

# 11. Suporte espacial e harmonização

## 11.1 Análise principal

Suporte nominal principal:

```text
10 m
```

Os dois produtos são comparados em uma grade comum de 10 m.

A referência de alinhamento será a projeção/transformação efetivamente utilizada pelo MapBiomas `classification_2025`.

O agente deve registrar:

```text
CRS
crsTransform
nominalScale
extent
```

da banda MapBiomas utilizada.

Essa informação torna-se `grid10`.

## 11.2 Dynamic World na grade comum

As nove probabilidades Dynamic World são variáveis contínuas.

Procedimento:

1. calcular composições temporais em sua estrutura original;
2. ao materializar a comparação, alinhar as probabilidades ao `grid10`;
3. usar interpolação contínua consistente (`bilinear`) apenas nas probabilidades;
4. verificar numericamente se a soma das nove probabilidades permanece aproximadamente 1;
5. renormalizar o vetor somente por erro numérico residual, se necessário;
6. derivar a classe anual por `argmax` **depois** do alinhamento.

Nunca aplicar bilinear a códigos categóricos.

## 11.3 MapBiomas

O MapBiomas é mantido em sua grade de referência na análise principal.

Variáveis categóricas usam vizinho mais próximo quando uma reprojeção for inevitável.

## 11.4 Áreas

Nunca usar:

```text
n_pixels * 100 m²
```

como regra geral de área.

Usar:

```text
ee.Image.pixelArea()
```

sobre a grade efetivamente processada.

## 11.5 Distâncias

Operações métricas de distância devem utilizar:

```text
EPSG:5880
```

ou projeção métrica equivalente explicitamente registrada.

Não calcular distâncias em graus de latitude/longitude.

## 11.6 Sensibilidade espacial

Executar uma sensibilidade a:

```text
30 m
```

derivada da grade comum de 10 m.

Dynamic World:

- média das nove probabilidades nas células 10 m;
- renormalização numérica se necessário;
- `argmax` do vetor agregado.

MapBiomas:

- majority/mode das células válidas da comparação binária.

A sensibilidade de 30 m usa **as mesmas localizações amostrais**.

Não criar nova amostra.

A análise principal permanece 10 m.

---

# 12. Construção temporal do Dynamic World

## 12.1 Unidade básica

Preservar as nove probabilidades.

Para cada localização/pixel e observação válida:

\[
\mathbf p_t =
(p_{water},p_{trees},...,p_{snow\_and\_ice})
\]

## 12.2 Duplicações do mesmo dia

Para evitar sobrepeso por tiles/cenas sobrepostos:

1. agrupar observações que representem o mesmo dia na mesma localização;
2. compor probabilidades do dia por média neutra;
3. não selecionar a observação “mais confiante”;
4. não ponderar pela entropia nem pelo máximo da softmax.

Resultado:

\[
\mathbf p_{d}
\]

## 12.3 Composição mensal

Para cada mês válido:

\[
\mathbf p_m =
\frac{1}{n_m}
\sum_{d \in m}\mathbf p_d
\]

Cada uma das nove bandas utiliza exatamente o mesmo conjunto de observações válidas.

Registrar:

```text
n_obs_month
```

## 12.4 Composição anual

Dar o mesmo peso a cada mês válido:

\[
\mathbf p_{year} =
\frac{1}{M}
\sum_{m \in valid}\mathbf p_m
\]

Não dar peso proporcional ao número de cenas do mês.

Classe anual:

\[
C_{year}=\arg\max_k p_{year,k}
\]

Classe mensal:

\[
C_m=\arg\max_k p_{m,k}
\]

## 12.5 Critério de meses válidos

Análise temporal principal:

```text
n_valid_months >= 8
```

Meses ausentes:

- não imputar;
- excluir do denominador;
- manter `n_valid_months`.

Regra de contingência pré-registrada:

> se mais de 20% da master sample de 40k possuir menos de 8 meses válidos, executar a análise temporal principal com `n_valid_months >= 6`, declarar explicitamente a mudança motivada apenas por cobertura observacional e manter `>=8` como sensibilidade.

Essa decisão deve ser tomada **antes de observar os resultados das hipóteses**.

A análise categórica wall-to-wall deve reportar separadamente a área sem cobertura temporal suficiente.

---

# 13. Variáveis probabilísticas e temporais

## 13.1 Probabilidade anual de crop

\[
p_{crop}=p_{year,crops}
\]

Variável descritiva.

Não interpretar como probabilidade calibrada de o pixel “estar correto”.

## 13.2 Entropia anual normalizada

\[
H_{annual}
=
-\frac{\sum_{k=1}^{9}p_{year,k}\ln p_{year,k}}
{\ln 9}
\]

Interpretação:

- próximo de 0: vetor concentrado;
- próximo de 1: vetor difuso.

Terminologia:

> **ambiguidade probabilística**

Não chamar automaticamente de:

- probabilidade de erro;
- incerteza epistêmica;
- confiança calibrada.

## 13.3 Entropia mensal média

Calcular como variável auxiliar:

\[
\overline H_{month}
=
\frac1M
\sum_m
\left[
-\frac{\sum_k p_{m,k}\ln p_{m,k}}
{\ln9}
\right]
\]

Ela não precisa aparecer no artigo principal, mas é necessária para decompor heterogeneidade temporal.

## 13.4 Heterogeneidade temporal — Jensen–Shannon generalizada

Usar:

\[
JSD_{temporal}
=
H(\mathbf p_{year})
-
\frac1M\sum_m H(\mathbf p_m)
\]

com a mesma base/log-normalização.

Interpretação:

- baixa: meses apresentam distribuições semelhantes;
- alta: vetor probabilístico muda ao longo do ano.

Essa variável separa:

- ambiguidade dentro dos meses;
- heterogeneidade entre meses.

## 13.5 Estabilidade categórica

\[
S=
\frac{
\#\{m:C_m=C_{year}\}
}{
M
}
\]

Quanto maior `S`, maior a persistência categórica da decisão anual ao longo dos meses válidos.

## 13.6 Classe concorrente

Calcular:

```text
top1_class
top2_class
top2_margin
```

A `top2_margin` é diagnóstica.

`competitor_class` é especialmente importante em discordâncias envolvendo:

- grass;
- bare;
- shrub_and_scrub;
- trees;
- flooded_vegetation.

---

# 14. Comparação categórica wall-to-wall

## 14.1 Quatro regimes

Definir:

| Código | MapBiomas | Dynamic World |
|---|---|---|
| AA | crop | crop |
| AN | crop | noncrop |
| NA | noncrop | crop |
| NN | noncrop | noncrop |

A nomenclatura é simétrica.

Não converter para TP/FP/FN/TN.

## 14.2 Variável binária de discordância

\[
D=
\begin{cases}
0,&AA\ ou\ NN\\
1,&AN\ ou\ NA
\end{cases}
\]

## 14.3 O que deve ser calculado wall-to-wall

Para MATOPIBA total e por estado:

- área elegível;
- área excluída por classe MapBiomas ambígua;
- área sem cobertura Dynamic World suficiente;
- área AA;
- área AN;
- área NA;
- área NN;
- proporção de cada regime na área elegível;
- concordância observada;
- discordância total;
- discordância de quantidade;
- discordância de alocação.

Essas quantidades vêm do raster completo.

**Não usar a amostra para estimar algo que já é conhecido wall-to-wall.**

## 14.4 Não usar Kappa

Kappa não faz parte do núcleo.

---

# 15. População amostral

A amostra existe para as variáveis computacionalmente mais caras:

- probabilidades mensais;
- entropia;
- JSD;
- estabilidade;
- distância de borda;
- classe concorrente;
- análises condicionais;
- bootstrap.

A população amostral é o conjunto de células 10 m da análise principal que:

1. pertencem ao MATOPIBA;
2. têm estado identificado;
3. possuem MapBiomas classificado pelo crosswalk principal;
4. não pertencem às classes MapBiomas excluídas;
5. possuem Dynamic World anual classificável;
6. satisfazem o critério de cobertura temporal adotado.

---

# 16. Estratificação amostral

Estratos:

\[
estado \times regime
\]

Estados:

```text
MA
TO
PI
BA
```

Regimes:

```text
AA
AN
NA
NN
```

Máximo:

```text
16 estratos
```

Usar somente estratos com área positiva.

Exemplo:

```text
MA_AA
MA_AN
MA_NA
MA_NN
TO_AA
...
BA_NN
```

Essa estrutura:

- mantém simetria entre os dois produtos;
- garante representação das duas direções de discordância;
- permite resultados por estado;
- evita usar MapBiomas isoladamente como gatekeeper da amostra.

---

# 17. Tamanho da amostra

## Master sample

```text
N_robust = 40.000
```

## Análise principal

```text
N_main = 20.000
```

A análise de 20k deve ser um subconjunto aninhado da mesma master sample de 40k.

Não criar duas amostras independentes.

Não usar 60k/80k no caminho crítico.

---

# 18. Regra de alocação entre estratos

## 18.1 Quota principal

Para cada estrato ativo `h`:

```text
n_min_main = 400
```

Depois distribuir o restante proporcionalmente à **área elegível** do estrato:

\[
W_h=\frac{A_h}{\sum_j A_j}
\]

\[
n_{h,main}
=
400
+
(20000-400H)W_h
\]

onde `H` é o número de estratos ativos.

Usar método dos maiores restos para arredondar e garantir soma exata de 20.000.

## 18.2 Quota de robustez

Definir inicialmente:

\[
n_{h,robust}=2n_{h,main}
\]

garantindo total de 40.000.

Se um estrato não comportar a quota:

1. fazer censo daquele estrato;
2. registrar a saturação;
3. redistribuir o restante proporcionalmente à área dos estratos não saturados;
4. não substituir o estrato por outro silenciosamente.

## 18.3 Por que não usar alocação igual

Alocação igual:

- super-representaria regimes raros;
- desperdiçaria observações em alguns estratos;
- aumentaria variabilidade dos pesos.

## 18.4 Por que não usar alocação puramente proporcional

A alocação puramente proporcional pode deixar AN/NA raros sem amostra adequada.

## 18.5 Por que não usar Neyman

Neyman exige estimativas prévias de variância por estrato que ainda não existem de maneira independente.

---

# 19. Método de seleção da master sample

## Decisão operacional

Usar:

> **amostragem aleatória estratificada, sem reposição, gerada no Google Earth Engine, com auditoria espacial posterior em Python.**

Razões:

- implementação nativa;
- probabilidades de inclusão transparentes;
- integração imediata com os rasters;
- baixo risco operacional em cinco dias;
- reprodutibilidade por materialização das coordenadas;
- evita transformar GRTS/BAS em um subprojeto técnico.

GRTS e BAS foram considerados e rejeitados para o caminho crítico desta semana por custo de integração superior ao ganho esperado.

## 19.1 Seed

```text
RANDOM_SEED = 25
```

## 19.2 Seleção

Gerar de uma única vez a amostra robusta de 40k conforme as quotas por estrato.

Depois:

1. materializar coordenadas;
2. gerar chave determinística de ordenação por estrato usando `seed=25` + coordenadas + `stratum_id`;
3. marcar os primeiros `n_h_main` de cada estrato como `main_sample=true`.

Assim:

```text
40k = master/robust
20k = subconjunto aninhado
```

## 19.3 Não depender apenas da seed

A seed **não é** a garantia final de reprodução.

O artefato definitivo é:

```text
master_sampling_points.csv
```

com coordenadas materializadas e publicadas.

---

# 20. Pesos amostrais

Para estrato `h`:

```text
N_h = número de células elegíveis
n_h = tamanho da amostra
A_h = área total elegível
```

Probabilidade de inclusão, quando equiprovável dentro do estrato:

\[
\pi_h=\frac{n_h}{N_h}
\]

Peso de desenho:

\[
w_h^{design}=\frac{1}{\pi_h}=\frac{N_h}{n_h}
\]

Como a área real dos pixels pode variar na grade geográfica, também armazenar:

\[
w_i^{area}
=
\frac{pixelArea_i}{\pi_h}
\]

Para estimativas populacionais de variáveis contínuas, utilizar `area_weight`.

Campos obrigatórios:

```text
selection_probability
design_weight
pixel_area_m2
area_weight
```

Resultados por estrato podem ser apresentados sem ponderação interna, pois os pontos são equiprováveis dentro de cada estrato.

Resultados regionais agregados devem usar os pesos.

---

# 21. Auditoria espacial da amostra

A auditoria **não altera a amostra depois de ela ser observada**.

Ela documenta sua distribuição.

Calcular:

- mapa dos pontos;
- distância ao vizinho mais próximo;
- mediana e quartis da distância ao vizinho;
- distribuição por estado;
- distribuição por regime;
- cobertura de uma grade de auditoria em projeção métrica;
- opcionalmente Clark–Evans como diagnóstico, sem usá-lo como teste de validade do desenho.

Não ressortear a amostra apenas porque um diagnóstico visual “pareceu feio”.

---

# 22. Bordas

## 22.1 Simetria

Calcular bordas de ambos:

```text
MapBiomas
Dynamic World anual
```

Não usar apenas a borda MapBiomas.

## 22.2 Definição

Em cada máscara binária crop/noncrop:

> pixel de borda = pixel que possui pelo menos um vizinho em conectividade 8 com classe binária diferente.

Ignorar transições envolvendo pixels mascarados/ambíguos.

## 22.3 Distâncias

Calcular:

\[
d_{MB}
\]

\[
d_{DW}
\]

Métrica principal:

\[
d_{min}=\min(d_{MB},d_{DW})
\]

## 22.4 Raio computacional

Truncar o cálculo em:

```text
250 m
```

O valor de 250 m é um **limite computacional pré-especificado**, não uma afirmação de que efeitos de borda chegam exatamente a 250 m.

## 22.5 Faixas descritivas

```text
0–10 m
10–30 m
30–60 m
60–100 m
100–250 m
>=250 m
```

A análise principal deve também preservar `distance_edge_m` contínua.

## 22.6 Implementação

Preferir transformação de distância eficiente e truncada (`fastDistanceTransform` ou equivalente) em projeção métrica.

Se necessário, processar apenas janelas locais ao redor dos pontos.

Evitar raster global de distância ilimitada em 10 m.

---

# 23. Sensibilidade de estabilidade MapBiomas

A análise principal inclui todo o domínio elegível de 2025.

Não restringir todo o artigo a “áreas estáveis segundo MapBiomas”.

Criar uma sensibilidade:

> pixel estável = status binário do crosswalk principal permanece constante em todos os anos válidos de 2017–2025.

Regras:

- usar a série da mesma Coleção 4;
- anos ambíguos quebram a elegibilidade para essa sensibilidade;
- reportar tamanho do subconjunto;
- repetir os principais contrastes H1–H4 dentro dele.

Isso permite verificar se as conclusões persistem quando mudanças reais de uso/cobertura são minimizadas.

---

# 24. Discordâncias de baixa ambiguidade e alta estabilidade

Definição pré-especificada dentro da amostra principal:

```text
D = 1
H_annual <= Q1
JSD_temporal <= Q1
S >= Q3
distance_edge_m >= 30 m
```

Quartis `Q1/Q3` são calculados na amostra principal elegível usando pesos de área.

Esses casos devem ser analisados quanto a:

- frequência ponderada;
- estado;
- direção AN/NA;
- classe Dynamic World concorrente;
- perfil mensal de `p(crops)`;
- robustez em 30 m;
- robustez no subconjunto MapBiomas estável.

Não afirmar que representam “erros sistemáticos”.

Usar:

> **discordâncias robustas internamente**

ou:

> **discordâncias de baixa ambiguidade e alta estabilidade**

---

# 25. Análises obrigatórias

## Resultado A — Geografia wall-to-wall

Produzir:

- mapa AA/AN/NA/NN;
- áreas por regime;
- áreas por estado;
- discordância total;
- discordância direcional;
- quantity disagreement;
- allocation disagreement.

## Resultado B — Ambiguidade probabilística

Comparar `H_annual` entre:

- AA;
- AN;
- NA;
- NN;
- concordantes vs discordantes.

Reportar:

- média ponderada;
- mediana ponderada quando implementável;
- quartis;
- diferença/contraste;
- IC por bootstrap espacial.

## Resultado C — Dinâmica temporal

Comparar:

```text
S
JSD_temporal
```

entre os mesmos regimes.

## Resultado D — Bordas

Avaliar:

\[
P(D=1\mid d_{min})
\]

por:

- faixas;
- curva suavizada descritiva;
- interior vs proximidade de borda.

## Resultado E — Discordâncias robustas internamente

Quantificar o subconjunto definido na seção 24.

## Resultado F — Perfil mensal

Calcular perfil mensal ponderado de:

\[
p(crops)
\]

para:

```text
AA
AN
NA
NN
```

Não atribuir automaticamente meses a plantio/colheita sem calendário externo.

---

# 26. Estatística

## 26.1 Obrigatório

- N bruto;
- N ponderado/área representada;
- médias;
- medianas/quartis;
- proporções;
- contrastes;
- intervalos de confiança;
- bootstrap espacial.

## 26.2 Bootstrap espacial

O tamanho dos blocos **não deve ser escolhido arbitrariamente antes dos dados**.

Regra pré-registrada:

1. usar a amostra principal de 20k;
2. estimar semivariograma empírico do indicador `D` em projeção métrica;
3. ajustar modelo exponencial simples;
4. definir o tamanho do bloco como o `practical range` (95% do sill);
5. arredondar para cima ao múltiplo de 5 km mais próximo;
6. limitar a faixa estimada a no máximo 100 km;
7. se o ajuste falhar, usar fallback de 25 km;
8. realizar sensibilidade com `0.5 × block_size` e `2 × block_size`.

Bootstrap:

```text
1999 replicações
seed = 25
```

O bootstrap deve reamostrar blocos, não pontos individuais.

## 26.3 Regressão

Regressão é secundária.

Só implementar se os resultados principais estiverem concluídos.

Modelo possível:

\[
logit[P(D=1)] =
\beta_0
+\beta_1H_{annual}
+\beta_2JSD
+\beta_3S
+\beta_4\log(d_{min}+1)
+\gamma_{state}
\]

Cuidado:

- H, JSD e S não são independentes conceitualmente;
- não interpretar coeficientes como efeitos causais;
- verificar colinearidade;
- eliminar a regressão se ela não acrescentar interpretação.

Não transformar o trabalho em projeto de modelagem preditiva.

---

# 27. Robustez obrigatória

A versão de 5 páginas deve priorizar apenas as robustezes mais informativas.

## R1 — Tamanho amostral

Comparar:

```text
20k principal
40k robustez
```

Mesma master sample.

## R2 — Suporte espacial

Comparar:

```text
10 m principal
30 m sensibilidade
```

## R3 — Crosswalk

Comparar:

```text
{19,36} principal
{19} estrito
```

## R4 — Estabilidade MapBiomas

Repetir contrastes centrais no subconjunto estável 2017–2025.

Não adicionar novas robustezes depois de olhar os resultados.

---

# 28. Outputs de dados

## 28.1 Manifesto do experimento

Criar:

```text
config/experiment.yaml
```

Deve conter:

```yaml
experiment:
  year: 2025
  random_seed: 25

study_area:
  name: MATOPIBA
  boundary_file: data/reference/matopiba_boundary.geojson
  states: [MA, TO, PI, BA]

products:
  dynamic_world:
    asset: GOOGLE/DYNAMICWORLD/V1
    start_date: 2025-01-01
    end_date_exclusive: 2026-01-01
  mapbiomas:
    asset: projects/mapbiomas-public/assets/brazil/lulc_10m/collection4/mapbiomas_10m_collection4_coverage_v1
    band: classification_2025

spatial:
  primary_support_m: 10
  sensitivity_support_m: 30
  distance_crs: EPSG:5880

temporal:
  primary_min_valid_months: 8
  fallback_min_valid_months: 6
  monthly_weighting: equal_valid_months
  missing_months: no_imputation

sampling:
  design: stratified_random_without_replacement
  strata: state_x_agreement_regime
  main_n: 20000
  robust_n: 40000
  min_per_active_stratum_main: 400

edges:
  max_distance_m: 250

inference:
  bootstrap_replicates: 1999
  bootstrap_seed: 25
```

O arquivo real deve também conter:

- transformações de grade;
- hash do boundary;
- versão de software;
- crosswalk aprovado;
- quotas finais por estrato.

## 28.2 Master sample

```text
data/processed/master_sampling_points.csv
```

Campos mínimos:

```text
sample_id
lat
lon
state
stratum_id
regime
main_sample
robust_sample
rank_key
seed
selection_probability
design_weight
pixel_area_m2
area_weight
```

## 28.3 Probabilidades mensais

Preferir formato longo:

```text
data/processed/dw_monthly.parquet
```

Campos:

```text
sample_id
month
n_daily_obs
water
trees
grass
flooded_vegetation
crops
shrub_and_scrub
built
bare
snow_and_ice
```

## 28.4 Dataset analítico anual

```text
data/processed/samples_annual.parquet
data/processed/samples_annual.csv
```

Campos mínimos:

```text
sample_id
state
lat
lon
stratum_id
regime
main_sample
selection_probability
area_weight

mapbiomas_class
mapbiomas_crop
dw_class
dw_crop

p_water
p_trees
p_grass
p_flooded_vegetation
p_crops
p_shrub_and_scrub
p_built
p_bare
p_snow_and_ice

entropy_annual
entropy_monthly_mean
jsd_temporal
stability
n_valid_months

top1_class
top2_class
top2_margin
competitor_class

distance_edge_mb_m
distance_edge_dw_m
distance_edge_min_m

mapbiomas_stable_2017_2025
robust_disagreement_flag
```

---

# 29. Arquitetura computacional

## Google Earth Engine

Fazer no GEE:

- carregar e recortar MATOPIBA;
- carregar MapBiomas;
- carregar Dynamic World;
- construir composições diárias/mensais;
- construir vetor anual;
- alinhar suporte;
- criar classe anual DW;
- criar máscaras crop/noncrop;
- criar mapa wall-to-wall AA/AN/NA/NN;
- calcular áreas;
- criar raster de estratos;
- gerar master sample;
- extrair valores nos pontos;
- calcular/consultar bordas e distâncias truncadas;
- processar sensibilidade 30 m;
- exportar tabelas.

## Python

Fazer em Python:

- validar tabelas;
- materializar ranking determinístico;
- marcar 20k principal;
- calcular pesos finais;
- calcular H, JSD, S e métricas derivadas;
- unir tabelas;
- EDA;
- análise ponderada;
- semivariograma;
- bootstrap espacial;
- figuras;
- tabelas;
- regressão opcional;
- checksums;
- artefatos reprodutíveis.

## Não fazer localmente

Não baixar rasters completos do MATOPIBA em 10 m.

---

# 30. Particionamento para evitar falhas

Se uma task GEE ficar pesada, particionar nesta ordem:

1. por estado;
2. por mês;
3. por produto;
4. por etapa de processamento.

Não particionar a ciência em “waves” independentes.

A master sample continua única.

Persistir intermediários suficientes para que uma falha não obrigue reprocessar tudo.

---

# 31. Protótipo técnico obrigatório

Antes da master sample, executar um protótipo com aproximadamente:

```text
500 pontos
```

Distribuição recomendada:

- quatro pequenas janelas, uma em cada estado;
- aproximadamente 125 pontos por janela;
- incluir visualmente crop e noncrop quando possível.

Objetivo do protótipo:

- validar assets;
- validar boundary;
- inspecionar códigos MapBiomas 2025;
- validar as nove probabilidades;
- validar soma das probabilidades;
- testar deduplicação diária;
- testar composição mensal;
- testar `n_valid_months`;
- testar alinhamento 10 m;
- testar sensibilidade 30 m;
- gerar AA/AN/NA/NN;
- testar bordas;
- testar exportação;
- estimar tempo/EECU.

O protótipo **não** deve ser usado para:

- testar H1–H4;
- escolher crosswalk com base em concordância;
- escolher limiares por significância;
- produzir resultados do artigo.

---

# 32. Checkpoints humanos

## Checkpoint 1 — dados e harmonização

Depois do protótipo, verificar:

- asset MapBiomas exato;
- banda 2025;
- legenda oficial;
- códigos realmente presentes;
- nove probabilidades DW;
- soma das probabilidades;
- mapa visual 10 m;
- 30 m sensibilidade;
- coordenadas;
- contagem de meses válidos;
- possíveis duplicações;
- bordas;
- custos GEE.

## Checkpoint 2 — congelamento metodológico operacional

Antes de gerar 40k:

Aprovar:

- crosswalk final;
- lista de classes excluídas;
- grid10 real;
- quotas dos 16 estratos;
- regra de meses válidos;
- execução da amostra.

Depois do Checkpoint 2:

> **não alterar desenho por causa dos resultados.**

## Checkpoint 3 — auditoria da master sample

Verificar:

- exatamente 40k ou justificativa de saturação;
- 20k aninhados;
- ausência de duplicatas;
- todos os pontos no domínio;
- estratos corretos;
- pesos;
- distribuição espacial;
- coordenadas materializadas.

## Checkpoint 4 — primeiros resultados

Verificar:

- efeitos não são artefatos;
- resultados 20k e 40k;
- sensibilidade 30 m;
- sensibilidade de crosswalk;
- classes concorrentes;
- bordas;
- interpretação.

## Checkpoint 5 — manuscrito

Revisar integralmente:

- Abstract;
- Methods;
- Results;
- Discussion;
- limitações;
- referências;
- figuras;
- números.

---

# 33. Figuras planejadas

## Figura 1 — MATOPIBA e geografia da discordância

Mapa:

- domínio completo;
- estados;
- AA/AN/NA/NN;
- amostra de 20k sobreposta de forma discreta.

## Figura 2 — estrutura probabilística e temporal

Painéis compactos:

- `H_annual` por regime;
- `S` por regime;
- `JSD_temporal` por regime.

## Figura 3 — bordas e discordâncias robustas

Painéis:

- discordância por distância;
- composição das classes concorrentes nos casos robustos;
- opcional mapa de hotspots descritivos, sem inferência LISA.

## Figura 4 — perfil mensal

`p(crops)` mensal para AA/AN/NA/NN.

Se faltar espaço, Figura 4 vai para material suplementar ou é incorporada à Figura 2.

---

# 34. Tabelas planejadas

## Tabela 1 — Dados e harmonização

- produto;
- versão;
- período;
- resolução nominal;
- suporte analítico;
- crosswalk;
- papel.

## Tabela 2 — Regimes wall-to-wall

Por AA/AN/NA/NN:

- área;
- proporção;
- estado;
- quantidade/alocação.

## Tabela 3 — métricas amostrais

Por regime:

- N;
- H;
- JSD;
- S;
- distância;
- IC espacial.

Se faltar espaço, Tabela 3 substitui uma figura.

---

# 35. Análises que NÃO entram no núcleo

Não implementar no caminho crítico:

- treino de novo modelo;
- Random Forest;
- XGBoost;
- CNN;
- Transformer;
- conformal prediction;
- classificação por soja/milho/algodão;
- avaliação causal;
- TerraClass;
- outros mapas globais;
- Kappa;
- F1;
- accuracy de um produto contra o outro;
- hotspot/LISA complexo;
- dezenas de thresholds;
- 60k/80k;
- 2024 como segundo experimento completo;
- ano-safra;
- auditoria manual massiva;
- grandes rasters exportados localmente.

---

# 36. Plano B científico

Se H1/H2 forem fracos:

não abandonar o projeto.

A narrativa muda para:

> **Where and under which spatial and temporal conditions do Dynamic World and MapBiomas systematically disagree on cropland in MATOPIBA?**

Enfatizar:

- geografia wall-to-wall;
- direção AN/NA;
- borda vs interior;
- classes concorrentes;
- perfil mensal;
- discordâncias robustas internamente.

Nenhum novo dataset é necessário.

---

# 37. Principais limitações a declarar

1. nenhum produto é ground truth;
2. ambos dependem de Sentinel-2 e podem possuir erros correlacionados;
3. resolução nominal igual não implica suporte físico idêntico;
4. o crosswalk binário reduz complexidade temática;
5. Dynamic World representa estado/cobertura por observação, MapBiomas é anual;
6. probabilidades DW não devem ser interpretadas como probabilidades calibradas de correção;
7. nuvens/sombras e disponibilidade mensal podem afetar séries;
8. agregação anual pode diluir fenómenos sazonais;
9. bordas representam associação, não causa;
10. análise amostral possui dependência espacial;
11. resultados de 2025 não implicam estabilidade em outros anos;
12. concordância não implica verdade;
13. discordância não identifica automaticamente o produto incorreto;
14. MapBiomas Stable/estabilidade derivada é análise de sensibilidade, não definição da população principal.

---

# 38. Reprodutibilidade

Publicar/congelar:

- boundary exato;
- lista de municípios;
- SHA-256;
- `experiment.yaml`;
- asset IDs;
- data de acesso;
- banda MapBiomas;
- legenda;
- crosswalk;
- CRS;
- `crsTransform`;
- suporte 10 m;
- suporte 30 m;
- seed 25;
- quotas por estrato;
- coordenadas 40k;
- flags 20k/40k;
- pesos;
- versões Python;
- versão `earthengine-api`;
- versões das bibliotecas;
- código;
- parâmetros temporais;
- parâmetros de borda;
- checksums dos datasets processados;
- commit Git usado para produzir resultados.

Nunca depender apenas de:

> “usamos seed 25”.

As coordenadas definitivas são o registro científico da amostra.

---

# 39. Estrutura recomendada do repositório

```text
Dynamic-World-MapBiomas/
│
├── PROJECT_BRIEF.md
├── README.md
├── requirements.txt
├── .gitignore
│
├── .agents/
│   ├── rules/
│   │   └── research-guardrails.md
│   └── skills/
│       ├── gee-prototype/
│       │   └── SKILL.md
│       └── audit-gee-prototype/
│           └── SKILL.md
│
├── config/
│   └── experiment.yaml
│
├── data/
│   ├── reference/
│   │   ├── matopiba_boundary.geojson
│   │   └── matopiba_municipalities.csv
│   ├── raw/
│   └── processed/
│       ├── prototype_samples.csv
│       ├── master_sampling_points.csv
│       ├── dw_monthly.parquet
│       ├── samples_annual.parquet
│       └── samples_annual.csv
│
├── src/
│   ├── gee/
│   │   ├── 01_check_access.py
│   │   ├── 02_boundary.py
│   │   ├── 03_mapbiomas.py
│   │   ├── 04_dynamic_world_monthly.py
│   │   ├── 05_harmonize.py
│   │   ├── 06_wall_to_wall.py
│   │   ├── 07_sampling.py
│   │   ├── 08_edges.py
│   │   └── 09_export.py
│   │
│   └── analysis/
│       ├── validate.py
│       ├── temporal_metrics.py
│       ├── weights.py
│       ├── spatial_bootstrap.py
│       ├── analysis.py
│       └── plots.py
│
├── notebooks/
│   ├── 01_prototype_audit.ipynb
│   ├── 02_main_analysis.ipynb
│   └── 03_figures.ipynb
│
├── figures/
├── tables/
├── references/
│   ├── papers.md
│   └── references.bib
│
└── paper/
    └── manuscript/
```

Evitar notebook monolítico.

---

# 40. Ambiente

Infra já validada:

```text
Google Earth Engine
Google Cloud project: dynamicworld-x-mapbiomas
Python .venv
earthengine-api
geemap
pandas
numpy
scipy
statsmodels
scikit-learn
matplotlib
jupyter
geopandas
```

Adicionar apenas dependências realmente necessárias.

Não adicionar R/GRTS/BAS ao caminho crítico desta versão.

Credenciais nunca entram no repositório.

---

# 41. Plano de execução em cinco dias

## DIA 1 — protótipo e congelamento operacional

Objetivo:

> provar que o novo desenho funciona.

Tarefas:

- atualizar `PROJECT_BRIEF.md`;
- atualizar Rules/Skills Antigravity que ainda mencionem metodologia antiga;
- congelar boundary;
- validar asset e legenda MapBiomas;
- executar protótipo 500;
- validar 10 m e 30 m;
- validar temporalidade;
- fechar crosswalk;
- fechar `experiment.yaml`.

Entrega:

```text
prototype_samples.csv
prototype audit
experiment.yaml
```

## DIA 2 — wall-to-wall + master sample

Tarefas:

- gerar MapBiomas/DW anual;
- gerar AA/AN/NA/NN;
- calcular áreas;
- gerar raster de estratos;
- calcular quotas;
- gerar 40k;
- marcar 20k;
- exportar probabilidades mensais;
- calcular bordas/distâncias.

Entrega:

```text
master_sampling_points.csv
dw_monthly.parquet
samples_annual.parquet
wall_to_wall_summary.csv
```

Depois do Dia 2:

> **não alterar datasets, crosswalk, amostra ou hipóteses por causa dos resultados.**

## DIA 3 — análise principal

Tarefas:

- validar 20k;
- calcular H/JSD/S;
- pesos;
- H1–H4;
- perfil mensal;
- semivariograma;
- bootstrap;
- figuras iniciais;
- 40k robustez.

No final do Dia 3 o artigo deve ser escrevível.

## DIA 4 — robustez e escrita

Executar somente:

- 30 m;
- crosswalk estrito;
- estabilidade MapBiomas;
- 40k;
- regressão apenas se houver tempo.

Congelar resultados no meio do dia.

Depois:

- figures;
- Methods;
- Results;
- Discussion.

## DIA 5 — artigo e submissão

Não criar novos experimentos.

Fazer:

- Abstract;
- Introdução final;
- conclusão;
- referências;
- revisão;
- PDF;
- submissão.

---

# 42. Prioridades em caso de atraso

Cortar nesta ordem:

1. regressão;
2. top-2 margin no artigo;
3. perfil mensal como figura separada;
4. estabilidade MapBiomas;
5. crosswalk sensitivity;
6. 30 m sensitivity, somente se tecnicamente impeditiva.

Não cortar:

- wall-to-wall AA/AN/NA/NN;
- entropia anual;
- estabilidade temporal;
- JSD temporal;
- borda;
- amostra principal 20k;
- pesos;
- reprodutibilidade;
- discordância robusta internamente.

A robustez 40k deve ser preservada se possível, mas não pode impedir a submissão.

---

# 43. Divisão humano × agente

## Decisões humanas obrigatórias

- aprovação final do crosswalk;
- aprovação do boundary;
- aprovação da tabela de códigos MapBiomas;
- aprovação do `experiment.yaml`;
- aprovação da master sample;
- interpretação científica;
- congelamento dos resultados;
- versão final do manuscrito.

## Agente pode implementar

- scripts GEE;
- scripts Python;
- validações;
- exportações;
- métricas;
- bootstrap;
- gráficos;
- tabelas;
- rascunho do artigo;
- bibliografia.

## Regra

O agente nunca deve alterar silenciosamente:

- domínio;
- ano;
- crosswalk;
- N;
- seed;
- suporte;
- hipóteses;
- datasets;
- regras temporais.

---

# 44. Protocolo do agente

Antes de cada etapa:

```text
git status --short
```

Depois de cada etapa, reportar:

1. arquivos criados/modificados;
2. comandos executados;
3. inputs;
4. outputs;
5. validações;
6. warnings;
7. custo/tempo GEE quando disponível;
8. checkpoint alcançado.

Nunca:

- `git push` sem aprovação;
- apagar dados;
- mudar metodologia;
- adicionar datasets;
- inventar asset IDs;
- inventar referências;
- reportar resultados não executados;
- chamar MapBiomas de verdade.

---

# 45. Atualização obrigatória das customizações Antigravity

As customizações existentes foram criadas antes desta revisão metodológica e podem conter decisões antigas.

Depois de substituir o brief, revisar:

```text
.agents/rules/research-guardrails.md
.agents/skills/gee-prototype/SKILL.md
.agents/skills/audit-gee-prototype/SKILL.md
```

Remover qualquer referência antiga a:

- “MATOPIBA nordestino” como domínio final;
- 15k–25k;
- estratificação apenas MapBiomas agriculture/non-agriculture;
- borda apenas MapBiomas;
- protótipo apenas em um estado;
- qualquer regra incompatível com este brief.

O `PROJECT_BRIEF.md` é a especificação científica autoritativa.

---

# 46. Primeira missão do Antigravity após esta versão

A primeira tarefa **não** é gerar 40k.

É atualizar as customizações e executar o protótipo metodológico.

Prompt lógico:

```text
Leia PROJECT_BRIEF.md integralmente.

Atualize apenas as customizações locais do workspace que ficaram
incompatíveis com o novo brief.

Depois execute somente o protótipo técnico da Seção 31.

Não gere ainda a master sample de 40k.
Não execute H1–H4.
Não escreva resultados científicos.

No final, entregue o relatório do Checkpoint 1 e pare.
```

---

# 47. Critério de sucesso científico

O trabalho está completo se responder, com evidência quantitativa:

1. Qual é a magnitude e a geografia da discordância crop/noncrop no MATOPIBA em 2025?
2. Discordâncias apresentam maior ambiguidade probabilística Dynamic World?
3. Discordâncias apresentam maior heterogeneidade/instabilidade temporal?
4. Discordâncias se concentram perto das bordas?
5. Existem discordâncias internamente estáveis e pouco ambíguas no interior?
6. Quais classes Dynamic World competem com `crops` nesses casos?
7. As conclusões principais permanecem com 40k, suporte 30 m e crosswalk estrito?

Não é necessário:

- decidir qual produto está correto;
- treinar IA;
- superar um benchmark;
- produzir um novo mapa agrícola;
- provar causalidade.

---

# 48. Referências essenciais de trabalho

Antes do manuscrito final, verificar novamente metadados, títulos e DOI.

## Dynamic World

Brown, C. F. et al. (2022).  
**Dynamic World, Near real-time global 10 m land use land cover mapping.**  
Scientific Data.  
DOI: `10.1038/s41597-022-01307-4`

Earth Engine:

```text
GOOGLE/DYNAMICWORLD/V1
```

## MapBiomas

Usar obrigatoriamente:

- documentação oficial da Cobertura 10 m — Coleção 4;
- legenda oficial da Coleção 4 10 m;
- documentação oficial de metodologia;
- informações do asset Earth Engine efetivamente carregado.

## Comparação de mapas

Pontius Jr., R. G.; Millones, M. (2011).  
**Death to Kappa: birth of quantity disagreement and allocation disagreement for accuracy assessment.**

Usar os conceitos de quantidade/alocação sem transformar MapBiomas em ground truth.

## Amostragem / áreas

Olofsson et al. (2014).  
Boas práticas de amostragem estratificada e estimativas de área em produtos de sensoriamento remoto.

Usar seus princípios de desenho/ponderação, não sua terminologia de referência verdadeira quando ela não se aplica.

---

# 49. Resumo executivo final

```text
DOMÍNIO
MATOPIBA completo

ANO
2025

PRODUTOS
Dynamic World V1
MapBiomas Cobertura 10 m Collection 4

OBJETO
concordância/discordância de lavouras
sem ground truth

CROSSWALK PRINCIPAL
DW crops
vs
MB Temporary Crop (19) + Perennial Crop (36)

WALL-TO-WALL
AA / AN / NA / NN
áreas e geografia

SUPORTE
10 m principal
30 m sensibilidade

TEMPORALIDADE DW
composição diária neutra
→ média mensal
→ peso igual aos meses
→ vetor anual de 9 classes

MÉTRICAS
H_annual
JSD_temporal
stability
p(crops)
competitor class
distance to edge

AMOSTRA
40.000 master
20.000 principal
40.000 robustez

ESTRATOS
4 estados × AA/AN/NA/NN

ALOCAÇÃO
mínimo 400 por estrato ativo
+ restante proporcional à área

SEED
25

SELEÇÃO
stratified random without replacement no GEE
coordenadas materializadas

BORDA
MapBiomas + Dynamic World
d_min
truncada a 250 m

INFERÊNCIA
pesos de desenho/área
spatial block bootstrap

ROBUSTEZ
40k
30 m
crosswalk estrito {19}
MapBiomas stable 2017–2025

TREINAMENTO DE IA
nenhum
```

---

# 50. Regra de ouro

```text
DADOS
→ AUDITORIA
→ AMOSTRA CONGELADA
→ RESULTADOS
→ ROBUSTEZ
→ FIGURAS
→ ARTIGO
```

Nunca:

```text
RESULTADO NÃO GOSTEI
→ MUDO CROSSWALK
→ MUDO AMOSTRA
→ MUDO LIMIAR
→ RODO DE NOVO
```

A metodologia está pré-especificada.

A partir daqui:

> **executar, auditar, documentar e escrever.**
