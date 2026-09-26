# PROJECT BRIEF — Dynamic World × MapBiomas no MATOPIBA/Nordeste

> Documento de transferência para outro chat/agente de IA.  
> Objetivo: permitir que um novo agente compreenda o projeto, as decisões já tomadas, o desenho experimental, as limitações e o plano de execução sem depender do histórico da conversa.

---

## 0. Status do projeto

**Evento-alvo:** Space Week Nordeste 2026  
**Prazo de execução:** 5 dias para pesquisa final, implementação, análise, escrita e submissão  
**Formato esperado:** artigo curto / resumo estendido de aproximadamente 5 páginas  
**Estado atual:** tema escolhido e revisão profunda já realizada; agora a prioridade é **execução experimental**  
**Stack principal:** Google Earth Engine + Python  
**GPU:** não necessária  
**Treinamento de modelo:** não será realizado

### Regra central do projeto

O artigo **não** deve ser uma simples comparação de acurácia entre Dynamic World e MapBiomas.

O objetivo é investigar:

> **onde, quando e sob quais condições probabilísticas, temporais e espaciais Dynamic World e MapBiomas discordam na identificação de áreas agrícolas.**

MapBiomas **não é ground truth**. O estudo é de **concordância/discordância interproduto**.

---

# 1. Tema da pesquisa

## Tema geral

GeoAI e sensoriamento remoto aplicados ao mapeamento agrícola em fronteiras tropicais.

## Tema específico

**Caracterização probabilística, temporal e espacial das discordâncias agrícolas entre Google Dynamic World e MapBiomas no MATOPIBA/Nordeste brasileiro.**

## Título provisório recomendado

### Em português

**Quando mapas agrícolas discordam: estrutura probabilística e estabilidade temporal do Dynamic World em comparação ao MapBiomas no MATOPIBA**

### Em inglês

**When Cropland Maps Disagree: Probability Structure and Temporal Stability of Dynamic World versus MapBiomas in MATOPIBA**

Alternativa mais conservadora:

**Probabilistic Characterization of Dynamic World–MapBiomas Agricultural Disagreement in MATOPIBA, Brazil**

---

# 2. Problema científico

O Dynamic World produz, para cada observação Sentinel-2, nove probabilidades de uso/cobertura da terra e uma classe final obtida por `argmax`.

Em aplicações comuns, quase toda essa informação probabilística é descartada e o usuário utiliza somente a classe final.

O MapBiomas, por outro lado, produz classificações anuais especializadas para o Brasil.

Esses produtos possuem:

- metodologias diferentes;
- temporalidades diferentes;
- legendas diferentes;
- regras de pós-processamento diferentes;
- possíveis erros próprios;
- dependência parcial da mesma fonte Sentinel-2 quando se usa MapBiomas 10 m.

Portanto:

> **concordância entre os produtos não prova correção e discordância não permite identificar automaticamente qual produto errou.**

A oportunidade científica é analisar a **estrutura da discordância**, utilizando justamente a informação probabilística e temporal do Dynamic World.

---

# 3. Pergunta de pesquisa oficial

> **Entre áreas de uso/cobertura temporalmente estáveis segundo o MapBiomas, a discordância agrícola com uma agregação temporal do Dynamic World está associada a maior ambiguidade probabilística, menor estabilidade temporal e maior proximidade das bordas agrícolas? Existem também discordâncias persistentes mesmo quando o Dynamic World apresenta alta confiança relativa?**

Essa pergunta substitui a formulação inicial, mais fraca:

> “Quanto maior `p(crops)`, maior a concordância com MapBiomas?”

A formulação inicial é parcialmente circular, porque o próprio rótulo Dynamic World deriva das probabilidades que seriam usadas para explicar a concordância.

---

# 4. Hipóteses

## H1 — Ambiguidade probabilística

Pixels discordantes apresentarão maior entropia média do Dynamic World:

\[
H_{discordante} > H_{concordante}
\]

## H2 — Estabilidade temporal

Pixels discordantes apresentarão menor estabilidade temporal:

\[
S_{discordante} < S_{concordante}
\]

## H3 — Efeito de borda

A frequência de discordância diminuirá com a distância das bordas agrícolas:

\[
P(D=1 \mid d) \downarrow \text{ quando } d \uparrow
\]

## H4 — Discordância persistente de alta confiança relativa

Existirá um subconjunto de pixels com:

- entropia baixa;
- estabilidade alta;
- e ainda assim `Dynamic World != MapBiomas`.

Essa é a hipótese conceitualmente mais importante, porque pode falsificar a explicação simplista:

> “os produtos só discordam quando o Dynamic World está inseguro”.

---

# 5. Os três argumentos científicos centrais

## Argumento 1 — Probabilidades contêm informação que o rótulo final descarta

Dynamic World não é apenas um mapa categórico. Cada observação contém um vetor de nove probabilidades.

A entropia, a margem Top-2, `p(crops)` e a persistência temporal podem revelar ambiguidade e competição entre classes mesmo quando o rótulo final parece estável.

**Mensagem do artigo:** usar somente `argmax` perde informação útil.

## Argumento 2 — Agricultura tropical é temporalmente difícil de representar com uma classe anual rígida

Uma mesma lavoura pode aparecer ao longo do ano como:

`bare -> crops -> crops -> bare/grass`

sem deixar de ser uma área agrícola.

Isso ocorre por:

- preparo do solo;
- crescimento;
- colheita;
- palhada;
- pousio;
- segunda safra;
- condições atmosféricas.

No MATOPIBA, essa questão é particularmente importante por causa da forte sazonalidade e dos sistemas agrícolas intensivos.

**Mensagem do artigo:** uma discordância anual pode ser parcialmente explicada pela trajetória temporal da classificação.

## Argumento 3 — Algumas discordâncias podem ser sistemáticas, e não simples baixa confiança

Se a discordância ocorrer apenas com alta entropia e baixa estabilidade, a explicação é simples.

Mais interessante é encontrar:

- baixa entropia;
- alta estabilidade;
- discordância persistente.

Isso pode indicar:

- diferença de legenda;
- diferença de suporte temporal;
- `crops` versus `grass`;
- `crops` versus `bare`;
- `crops` versus `shrub_and_scrub`;
- diferença de fronteira;
- diferentes conceitos de agricultura anual.

**Mensagem do artigo:** nem toda discordância é apenas “incerteza do modelo”.

---

# 6. Contribuição pretendida

A contribuição **não** é:

- nova arquitetura de IA;
- novo classificador;
- novo mapa agrícola;
- validação absoluta do Dynamic World;
- prova de que MapBiomas é correto.

A contribuição é:

> **um diagnóstico probabilístico, temporal e espacial da discordância entre um produto global near-real-time e um produto nacional anual em uma fronteira agrícola tropical.**

Em termos práticos, o estudo pretende mostrar como:

1. probabilidades do Dynamic World se comportam em áreas concordantes e discordantes;
2. estabilidade temporal se relaciona à discordância;
3. bordas espaciais influenciam a concordância;
4. casos de alta confiança relativa continuam discordando;
5. classes concorrentes ajudam a interpretar essas contradições.

---

# 7. Escopo congelado

## Obrigatório

- Dynamic World V1;
- MapBiomas Cobertura 10 m;
- MapBiomas Áreas Estáveis ou estabilidade derivada da série;
- ano principal 2025;
- região Nordeste do MATOPIBA;
- agregação temporal Dynamic World;
- entropia;
- estabilidade temporal;
- distância de borda;
- discordância;
- discordância de alta confiança relativa;
- amostragem espacial;
- bootstrap espacial;
- análise em Python.

## Opcional, somente se estiver pronto cedo

- MapBiomas 30 m como análise de sensibilidade;
- TerraClass como triangulação;
- margem Top-2;
- análise por estado;
- 2024 como pequena sensibilidade.

## Fora do escopo

- novo modelo de deep learning;
- conformal prediction;
- classificação por cultura específica;
- soja/milho/algodão individualmente;
- WorldCover/Esri/WorldCereal no experimento principal;
- grandes exportações raster;
- análise causal;
- validação completa de todo o MATOPIBA;
- detecção de conversões em muitos anos;
- produção de um novo mapa agrícola.

---

# 8. Área de estudo

## Versão oficial para execução

Foco no **MATOPIBA pertencente ao Nordeste**:

- Maranhão;
- Piauí;
- oeste da Bahia.

O estudo deve usar **amostragem espacial estratificada**, e não todos os pixels.

### Plano B caso a região inteira fique pesada

Usar polos agrícolas representativos:

- Balsas — MA;
- Baixa Grande do Ribeiro ou Uruçuí — PI;
- São Desidério ou Luís Eduardo Magalhães — BA.

Não adicionar novas regiões depois do Dia 2.

---

# 9. Período

## Ano principal

**2025**

Motivos:

- ano completo;
- Dynamic World disponível;
- MapBiomas 10 m cobre o período;
- permite série intra-anual;
- está dentro da janela de estabilidade MapBiomas.

Anos anteriores devem ser usados principalmente para definir **estabilidade**, não para criar uma análise temporal longa.

---

# 10. Datasets

## 10.1 Dynamic World V1

**GEE Collection:**

```text
GOOGLE/DYNAMICWORLD/V1
```

Resolução nominal: 10 m.

Classes/probabilidades:

- `water`
- `trees`
- `grass`
- `flooded_vegetation`
- `crops`
- `shrub_and_scrub`
- `built`
- `bare`
- `snow_and_ice`

Também possui `label`.

### Papel no projeto

Produto probabilístico principal.

Não baixar o dataset inteiro. Usar diretamente no Google Earth Engine.

## 10.2 MapBiomas 10 m

Usar a coleção 10 m mais recente e disponível no GEE para 2025.

### Papel

Comparador principal da classe agrícola.

### Cuidado

MapBiomas também é produto modelado.

Não chamar de:

- ground truth;
- referência verdadeira;
- rótulo correto.

Usar:

- comparador;
- produto nacional;
- produto anual especializado.

## 10.3 MapBiomas Áreas Estáveis

Usar o produto oficial de áreas estáveis, se acessível de forma simples.

Se isso atrasar o pipeline, derivar estabilidade diretamente da série MapBiomas:

> pixel estável = classe harmonizada agricultura/não-agricultura não muda na janela escolhida.

### Papel

Reduzir a possibilidade de interpretar transição real de uso da terra como discordância cartográfica.

## 10.4 Limites geográficos

Usar limites oficiais disponíveis no Earth Engine ou shapefile/GeoJSON confiável.

Não há necessidade de baixar grandes rasters.

---

# 11. Crosswalk agricultura / não agricultura

O artigo utilizará uma harmonização binária:

```text
AGRICULTURA
NÃO AGRICULTURA
```

## Dynamic World

- `crops` -> Agricultura
- demais classes -> Não agricultura

## MapBiomas

As classes agrícolas devem ser definidas **antes de observar os resultados**.

O agente deve localizar a legenda oficial da coleção selecionada e produzir uma tabela de crosswalk para revisão humana.

### Regra

Classes semanticamente ambíguas devem ser:

- justificadas;
- analisadas separadamente;
- ou excluídas.

Nunca alterar o crosswalk para aumentar a concordância.

---

# 12. Construção temporal do Dynamic World

## Não usar apenas uma cena

Cada pixel possui várias observações durante o ano.

O pipeline deve:

1. filtrar 2025;
2. agregar observações por mês;
3. gerar uma representação mensal das nove probabilidades;
4. agregar os meses para evitar que meses com mais cenas tenham peso excessivo;
5. derivar a representação anual.

Essa escolha é importante porque a disponibilidade de cenas varia com nuvens e cobertura Sentinel-2.

---

# 13. Variáveis principais

## 13.1 Probabilidade de agricultura

\[
p_{crop}=P(crops)
\]

É intuitiva, mas **não deve ser a única variável**.

## 13.2 Entropia normalizada

Para vetor:

\[
\mathbf p=(p_1,\ldots,p_9)
\]

calcular:

\[
H=
-\frac{\sum_{k=1}^{9} p_k \ln p_k}
{\ln 9}
\]

Interpretação:

- `H ~ 0`: distribuição concentrada;
- `H ~ 1`: distribuição difusa.

### Terminologia recomendada

**ambiguidade probabilística**

Evitar afirmar que entropia = probabilidade de erro ou incerteza epistêmica calibrada.

## 13.3 Estabilidade temporal

Medida simples recomendada:

\[
S_i=
\frac{\#\{\text{meses em que a classe dominante coincide com a classe anual}\}}
{\#\{\text{meses válidos}\}}
\]

Quanto maior `S`, mais estável a classificação.

## 13.4 Margem Top-2 — opcional

\[
M=p_{(1)}-p_{(2)}
\]

Pequena margem = maior competição entre as duas classes mais prováveis.

Só implementar se não comprometer o cronograma.

## 13.5 Distância da borda

Gerar borda da máscara agrícola MapBiomas e calcular:

\[
d_i=\text{distância do ponto até a borda agrícola}
\]

Faixas possíveis:

- 0–20 m;
- 20–50 m;
- 50–100 m;
- >100 m.

---

# 14. Variável de discordância

Criar:

\[
D_i=
\begin{cases}
0, & DW_i = MB_i \\
1, & DW_i \neq MB_i
\end{cases}
\]

Também separar quatro regimes:

| MapBiomas | Dynamic World | Código |
|---|---|---|
| Agricultura | Agricultura | AA |
| Agricultura | Não agricultura | AN |
| Não agricultura | Agricultura | NA |
| Não agricultura | Não agricultura | NN |

Evitar:

- verdadeiro positivo;
- falso positivo;
- verdadeiro negativo;
- falso negativo.

Esses termos pressupõem ground truth.

---

# 15. Discordância de alta confiança relativa

Não definir alta confiança como:

> `p > 0.90` = 90% de chance de estar correto.

As probabilidades não foram necessariamente calibradas dessa forma.

Definição recomendada baseada na própria distribuição:

- entropia no quartil inferior (`H in Q1`);
- estabilidade no quartil superior (`S in Q4`);
- `D = 1`.

Esses casos serão chamados de:

> **discordâncias de alta confiança relativa**

Depois analisar a classe concorrente Dynamic World.

Especial atenção a:

- `grass`;
- `bare`;
- `shrub_and_scrub`;
- `trees`.

---

# 16. Unidade de análise e amostragem

## Não usar todos os pixels

Meta inicial:

**15.000–25.000 pontos**

Estratificar por:

- estado/região;
- agricultura/não agricultura MapBiomas;
- blocos espaciais.

Utilizar blocos para evitar pseudorreplicação.

### CSV final esperado

```text
id
estado
lat
lon
mapbiomas_class
dw_class
agreement
p_crop
entropy
stability
distance_border
competitor_class
n_valid_months
```

Opcional:

```text
top2_margin
```

Quando esse CSV existir, a maior parte do risco técnico do projeto terminou.

---

# 17. Experimentos obrigatórios

Todas as análises usam o mesmo dataset.

## Experimento 1 — Entropia

Comparar:

\[
H_{concordante}
\]

versus:

\[
H_{discordante}
\]

Pergunta:

> discordâncias aparecem em regiões probabilisticamente mais ambíguas?

## Experimento 2 — Estabilidade temporal

Comparar:

\[
S_{concordante}
\]

versus:

\[
S_{discordante}
\]

Pergunta:

> discordâncias estão associadas a maior instabilidade temporal?

## Experimento 3 — Efeito de borda

Estimar:

\[
P(D=1 \mid d)
\]

Pergunta:

> discordâncias diminuem à medida que se afasta da fronteira agrícola?

## Experimento 4 — Alta confiança discordante

Selecionar:

```text
H baixo
S alto
D = 1
```

e analisar:

- frequência;
- localização;
- classe concorrente;
- comportamento mensal.

Pergunta:

> quais divergências permanecem mesmo quando Dynamic World é internamente consistente?

---

# 18. Análise sazonal

Calcular perfil mensal de:

\[
p(crops)
\]

para:

- AA;
- AN;
- NA;
- NN.

Objetivo:

> verificar se a discordância é persistente ou se aparece em partes específicas do ano.

Evitar atribuir automaticamente cada mês a plantio/colheita/safrinha sem calendário agrícola externo.

---

# 19. Estatística

## Obrigatório

- N;
- média/mediana;
- quartis;
- proporções;
- intervalos de confiança;
- bootstrap espacial.

## Modelo simples recomendado

\[
logit[P(D_i=1)] =
\beta_0 +
\beta_1 H_i +
\beta_2 S_i +
\beta_3 \log(d_i+1) +
\gamma_{região}
\]

O modelo é auxiliar.

Não transformar o trabalho em projeto de machine learning.

---

# 20. Figuras planejadas

## Figura 1 — Área de estudo

Mapa da região e distribuição amostral.

## Figura 2 — Resultado principal

Painéis:

- entropia × concordância/discordância;
- estabilidade × concordância/discordância;
- discordância × distância de borda.

## Figura 3 — Discordâncias de alta confiança

Distribuição espacial e/ou classes concorrentes.

## Figura 4 — Perfil mensal

`p(crops)` por mês nos quatro regimes AA/AN/NA/NN.

Se faltar espaço, combinar Figuras 3 e 4.

---

# 21. Tabelas planejadas

## Tabela 1 — Dados e harmonização

Produto, ano, resolução nominal, classes e crosswalk.

## Tabela 2 — Regimes de concordância

Para AA, AN, NA, NN:

- N;
- entropia;
- estabilidade;
- distância de borda;
- IC.

## Tabela 3 — Regressão

Odds ratios / coeficientes e intervalos.

Tabela 3 pode ser eliminada se faltar espaço.

---

# 22. TerraClass: papel e regra de decisão

Uma das Deep Research propôs um desenho triangular:

```text
MapBiomas + TerraClass -> definem discordância externa
Dynamic World -> fornece entropia, margem e persistência
```

Vantagem:

- reduz circularidade entre `p(crops)` e o próprio rótulo Dynamic World.

Problema:

- harmonização adicional;
- ano compatível;
- mais risco operacional.

## Regra oficial

**TerraClass é opcional.**

Só incorporar se:

- acesso estiver funcionando no Dia 1;
- legenda estiver clara;
- alinhamento para 2022 estiver simples.

Caso contrário, eliminar imediatamente.

### Observação

Se TerraClass entrar no núcleo, o ano-base deve migrar para **2022**, pois é o período de triangulação recomendado nas pesquisas.

Não misturar os dois desenhos.

---

# 23. Versão oficial versus versão triangular

## Versão oficial / padrão

```text
Dynamic World + MapBiomas
Ano: 2025
Área: Nordeste do MATOPIBA
```

Esta é a versão a executar por padrão.

## Versão triangular — somente se extraordinariamente simples

```text
Dynamic World + MapBiomas + TerraClass
Ano: 2022
Quatro municípios ou área compacta
```

O agente não deve trocar para essa versão sem decisão humana explícita.

---

# 24. Plano B científico

Se:

- entropia;
- estabilidade;

não separarem concordância e discordância de forma relevante, **não abandonar o projeto**.

Pivotar para:

> **Where do Dynamic World and MapBiomas systematically disagree on stable agricultural landscapes in MATOPIBA?**

Usar o mesmo dataset e enfatizar:

- borda vs interior;
- estado/região;
- classe concorrente;
- perfil mensal;
- discordância persistente.

Nenhum novo dataset é necessário.

---

# 25. Riscos metodológicos que o agente deve respeitar

1. MapBiomas não é ground truth.
2. Dynamic World e MapBiomas 10 m podem compartilhar Sentinel-2 e ter erros correlacionados.
3. “10 m” nominal não significa suporte espacial físico idêntico.
4. Crosswalk binário perde informação temática.
5. Áreas estáveis privilegiam paisagens consolidadas.
6. Probabilidades Dynamic World não devem ser presumidas perfeitamente calibradas.
7. Nuvens/sombras residuais podem influenciar a série.
8. Bordas e discordância são associação, não causalidade.
9. Sem referência independente, não é possível decidir qual produto está correto.
10. Milhões de pixels vizinhos não são observações independentes.
11. `p(crops)` sozinho pode produzir um resultado quase tautológico.
12. A contribuição não deve ser exagerada como “primeira comparação Dynamic World × MapBiomas”.

---

# 26. Referências essenciais

Estas são as referências que o próximo agente deve priorizar antes de procurar literatura adicional.

## Dynamic World

Brown, C. F. et al. (2022).  
**Dynamic World, Near real-time global 10 m land use land cover mapping.**  
Scientific Data.  
DOI: `10.1038/s41597-022-01307-4`

Dataset de treinamento:  
DOI: `10.1594/PANGAEA.933475`

Catálogo Earth Engine:

```text
GOOGLE/DYNAMICWORLD/V1
```

## Comparação/validação de produtos LULC

Referência importante identificada na Deep Research:

**Comparative validation of recent 10 m land-cover products**  
Remote Sensing of Environment (2024).  
DOI: `10.1016/j.rse.2024.114316`

## Probabilidades Dynamic World

Myers et al. (2025).  
Trabalho mostrando uso das probabilidades Dynamic World além do rótulo final.  
Remote Sensing.  
DOI: `10.3390/rs17152570`

Small & Sousa (2023).  
Análise espectral das classes Dynamic World.  
Remote Sensing.  
DOI: `10.3390/rs15030575`

## Discordância de quantidade/alocação

Pontius Jr., R. G.; Millones, M. (2011).  
**Death to Kappa: birth of quantity disagreement and allocation disagreement for accuracy assessment.**  
DOI: `10.1080/01431161.2011.552923`

## MapBiomas

Consultar obrigatoriamente:

- documentação oficial da coleção 10 m usada;
- legenda oficial;
- documentação de áreas estáveis;
- notas metodológicas;
- licença.

Nunca copiar IDs de classes de memória: verificar a legenda da coleção efetivamente carregada.

## MATOPIBA

Usar literatura recente de:

- expansão agrícola;
- Cerrado;
- Alto Parnaíba;
- sul do Maranhão;
- sudoeste do Piauí;
- oeste da Bahia.

A introdução não precisa virar revisão extensa do MATOPIBA. São necessárias apenas referências suficientes para justificar:

1. relevância agrícola;
2. agricultura tropical altamente sazonal;
3. transformação recente da paisagem.

---

# 27. Estrutura do repositório

Recomendação:

```text
dynamicworld-mapbiomas/
│
├── README.md
├── PROJECT_BRIEF.md
├── requirements.txt
├── .gitignore
│
├── references/
│   ├── papers.md
│   └── bib/
│
├── src/
│   ├── gee/
│   │   ├── 01_check_access.py
│   │   ├── 02_load_regions.py
│   │   ├── 03_dynamic_world.py
│   │   ├── 04_mapbiomas.py
│   │   ├── 05_stability_borders.py
│   │   └── 06_sample_export.py
│   │
│   └── analysis/
│       ├── metrics.py
│       ├── bootstrap.py
│       └── plots.py
│
├── notebooks/
│   ├── 01_audit.ipynb
│   ├── 02_main_analysis.ipynb
│   └── 03_figures.ipynb
│
├── data/
│   ├── raw/
│   └── processed/
│       └── samples.csv
│
├── figures/
├── tables/
└── paper/
    ├── manuscript.tex
    └── references.bib
```

Evitar notebook monolítico.

---

# 28. Ambiente

Pacotes Python previstos:

```bash
pip install earthengine-api geemap pandas numpy scipy statsmodels scikit-learn matplotlib jupyter geopandas
```

Autenticação Earth Engine:

```python
import ee

ee.Authenticate()
ee.Initialize(project="SEU_GOOGLE_CLOUD_PROJECT_ID")
```

Não colocar tokens, credenciais ou arquivos sensíveis no GitHub.

Adicionar ao `.gitignore`:

```text
.venv/
__pycache__/
.ipynb_checkpoints/
.env
credentials*
*.tif
*.tiff
data/raw/*
```

---

# 29. Fluxo de execução em 5 dias

## DIA 1 — Fazer o pipeline funcionar

### Objetivo

Provar que todos os dados essenciais podem ser acessados e amostrados.

### Tarefas

- confirmar Earth Engine;
- carregar Dynamic World;
- carregar MapBiomas;
- localizar legenda oficial;
- fechar crosswalk;
- definir região;
- criar protótipo em área pequena;
- exportar aproximadamente 500 pontos.

### Entrega obrigatória

Tabela com:

- coordenadas;
- nove probabilidades;
- MapBiomas;
- rótulo Dynamic World.

### Escrita

Começar:

- Introdução;
- pergunta;
- hipóteses;
- descrição dos dados.

## DIA 2 — Criar o dataset definitivo

### Tarefas

- agregação mensal/anual;
- entropia;
- estabilidade;
- bordas;
- distância;
- amostragem espacial;
- exportação.

### Entrega obrigatória

```text
data/processed/samples.csv
```

com aproximadamente 15k–25k amostras.

### Regra

Depois do Dia 2:

> **não adicionar novos datasets ao núcleo.**

## DIA 3 — Executar toda a ciência principal

### Tarefas

- EDA;
- entropia concordante vs discordante;
- estabilidade;
- borda;
- alta confiança discordante;
- classes concorrentes;
- perfil mensal;
- bootstrap;
- regressão opcional.

### Entrega obrigatória

Todos os números principais e primeira versão das figuras.

Ao final do Dia 3, o artigo já deve ser escrevível mesmo sem novos experimentos.

## DIA 4 — Robustez + escrita

Somente análises previamente planejadas:

- excluir bordas;
- comparar regiões;
- quartis alternativos;
- opcional MapBiomas 30 m.

### Meio do Dia 4

**CONGELAR RESULTADOS.**

Depois:

- figuras finais;
- tabelas;
- Métodos;
- Resultados;
- Discussão.

Meta: 80–90% do manuscrito pronto.

## DIA 5 — Manuscrito e submissão

Não fazer novo experimento.

### Tarefas

- Abstract;
- Introdução final;
- Discussão;
- Conclusão;
- referências;
- template;
- revisão científica;
- PDF;
- submissão.

---

# 30. Divisão entre humano, agente de IA e automação

## Tarefas que DEVEM permanecer sob decisão humana

### Decisões científicas

- aprovar a pergunta final;
- aprovar o crosswalk MapBiomas;
- escolher área final;
- aprovar exclusões de classes;
- decidir se TerraClass entra;
- decidir quando congelar resultados;
- interpretar se o resultado faz sentido cientificamente;
- revisar todas as conclusões;
- validar versão final antes da submissão.

### Auditoria visual

O pesquisador deve olhar mapas e exemplos reais.

Nunca aceitar automaticamente que um script correto sintaticamente produziu uma classificação correta.

### Autoria

A interpretação final e as alegações científicas são responsabilidade humana.

## Tarefas que um agente de IA pode fazer quase integralmente

### Código

- criar estrutura do repositório;
- escrever scripts Earth Engine;
- escrever funções Python;
- implementar entropia;
- implementar estabilidade;
- criar bordas;
- implementar amostragem;
- exportar CSV;
- depurar erros;
- gerar notebooks;
- gerar figuras;
- gerar tabelas;
- bootstrap;
- regressão.

### Pesquisa bibliográfica

- organizar referências;
- resumir artigos;
- extrair DOI;
- preparar BibTeX;
- localizar metodologia relevante;
- comparar trabalhos.

A inclusão final de referências e afirmações deve ser conferida pelo autor.

### Escrita

O agente pode rascunhar:

- Introdução;
- Métodos;
- Resultados;
- Discussão;
- legendas;
- Abstract;
- conclusão.

Sempre baseado nos resultados reais.

## Tarefas totalmente automatizáveis

Depois que o código estiver correto:

- consultas GEE;
- agregações;
- cálculo das probabilidades;
- entropia;
- estabilidade;
- distâncias;
- amostragem;
- exportações;
- estatísticas;
- bootstrap;
- regressões;
- criação repetível de gráficos;
- criação repetível de tabelas;
- compilação LaTeX.

---

# 31. Workflow humano + agente

Fluxo recomendado:

```text
HUMANO
aprova pergunta/crosswalk
        |
        v
AGENTE
implementa protótipo
        |
        v
AUTOMAÇÃO/GEE
gera dados
        |
        v
HUMANO
audita mapas e amostras
        |
        v
AGENTE
corrige e gera dataset
        |
        v
AUTOMAÇÃO/PYTHON
calcula estatísticas e figuras
        |
        v
HUMANO
interpreta e aprova resultados
        |
        v
AGENTE
redige artigo
        |
        v
HUMANO
revisa ciência e submete
```

---

# 32. Protocolo de interação com o agente

O agente deve trabalhar em etapas curtas.

## Nunca fazer

- implementar o projeto inteiro sem checkpoints;
- alterar pergunta sem autorização;
- adicionar dataset por iniciativa própria;
- mudar crosswalk após observar resultados;
- interpretar MapBiomas como ground truth;
- escrever resultados que ainda não foram produzidos;
- inventar referências;
- substituir código funcionando por arquitetura mais sofisticada sem necessidade.

## Sempre fazer

Depois de cada etapa:

1. dizer o que foi feito;
2. mostrar arquivos alterados;
3. mostrar output mínimo;
4. apontar problemas;
5. parar em decisões científicas que precisam de aprovação humana.

---

# 33. Primeiro prompt recomendado para o agente de código

> Você está entrando em um projeto científico GeoAI com prazo extremamente curto. Leia integralmente `PROJECT_BRIEF.md` antes de editar qualquer arquivo. Não altere a pergunta científica, os datasets obrigatórios, o ano de 2025 ou o crosswalk sem aprovação humana.
>
> Sua primeira tarefa é somente configurar e testar o acesso aos dados.
>
> 1. Configure um ambiente Python.
> 2. Verifique autenticação Google Earth Engine.
> 3. Carregue `GOOGLE/DYNAMICWORLD/V1`.
> 4. Identifique e carregue o asset oficial MapBiomas 10 m que contém 2025.
> 5. Carregue uma área pequena de teste no MATOPIBA.
> 6. Gere um script que amostre cerca de 500 pontos e retorne:
>    - coordenadas;
>    - as nove probabilidades Dynamic World;
>    - `label`;
>    - classe MapBiomas 2025.
> 7. Não implemente ainda entropia, bordas, estabilidade ou análise estatística.
> 8. Salve o resultado em `data/processed/prototype_samples.csv`.
> 9. Documente exatamente os IDs de assets usados e suas bandas.
> 10. Pare depois disso para auditoria humana.
>
> Se algum asset ou versão descrita neste briefing não existir como esperado, não invente um substituto. Documente o problema e proponha opções.

---

# 34. Checkpoints humanos

## Checkpoint 1 — depois do protótipo

Humano verifica:

- as nove probabilidades existem;
- valores estão entre 0 e 1;
- classes MapBiomas parecem corretas;
- mapa visual parece plausível;
- coordenadas estão na região certa.

## Checkpoint 2 — antes da amostra final

Humano aprova:

- crosswalk;
- definição de estabilidade;
- região;
- método de borda;
- tamanho da amostra.

## Checkpoint 3 — depois dos primeiros resultados

Humano verifica:

- efeitos não são artefatos;
- gráficos fazem sentido;
- classes concorrentes são plausíveis;
- interpretação não extrapola os dados.

## Checkpoint 4 — artigo final

Humano lê integralmente:

- Abstract;
- resultados;
- discussão;
- limitações;
- referências.

---

# 35. Estrutura de 5 páginas

## Página 1

- contexto;
- gap;
- pergunta;
- hipótese.

## Página 2

- dados;
- área;
- método.

## Página 3

- método final;
- resultados iniciais.

## Página 4

- resultados principais;
- figuras.

## Página 5

- discussão;
- limitações;
- conclusão.

Não gastar espaço com revisão bibliográfica extensa.

---

# 36. Critério de sucesso

O projeto está cientificamente completo se responder:

1. Discordâncias possuem maior ambiguidade probabilística?
2. Discordâncias possuem menor estabilidade temporal?
3. Discordâncias se concentram nas bordas?
4. Existem discordâncias persistentes mesmo em alta confiança relativa?
5. Quais classes do Dynamic World competem com `crops` nesses casos?

Não é necessário:

- superar outro método;
- produzir mapa mais acurado;
- treinar IA;
- provar causalidade.

---

# 37. Prioridades em caso de atraso

Cortar nesta ordem:

1. TerraClass;
2. MapBiomas 30 m;
3. análise por estado;
4. margem Top-2;
5. regressão logística;
6. Figura 4 separada.

Nunca cortar:

- discordância;
- entropia;
- estabilidade;
- borda;
- alta confiança discordante.

---

# 38. Regra de ouro para a semana

```text
DADOS -> RESULTADOS -> FIGURAS -> ARTIGO -> EXTENSÕES
```

Nunca:

```text
MAIS LITERATURA -> MAIS IDEIAS -> MAIS DATASETS -> SEM RESULTADOS
```

A revisão científica já foi realizada.

A partir deste ponto, a prioridade é execução.

---

# 39. Estado de infraestrutura atual

Já foi criado:

- conta Google Earth Engine;
- repositório GitHub.

Próximos passos:

1. identificar/criar Google Cloud Project associado;
2. ativar Earth Engine API se necessário;
3. autenticar `earthengine-api`;
4. clonar/abrir o repositório;
5. criar `.venv`;
6. instalar dependências;
7. adicionar este arquivo como `PROJECT_BRIEF.md` ao repositório;
8. entregar ao agente o prompt da seção 33;
9. produzir o protótipo de ~500 amostras.

---

# 40. Informação importante para qualquer novo agente

Este projeto possui **deadline de cinco dias**.

Qualquer decisão deve ser avaliada primeiro por:

1. isso é necessário para responder a pergunta?
2. já temos dados suficientes?
3. isso pode atrasar a entrega?
4. a contribuição científica melhora o suficiente para justificar o custo?

Se a resposta à pergunta 1 for “não”, não implementar.

Se a resposta à pergunta 3 for “sim” e a 4 não for claramente “sim”, cortar.

---

# 41. Resumo de uma frase

> **Vamos usar as probabilidades e a dinâmica temporal do Dynamic World para entender onde e por que seu mapeamento agrícola diverge do MapBiomas em paisagens agrícolas estáveis do MATOPIBA nordestino, com foco em ambiguidade probabilística, estabilidade temporal, bordas e discordâncias persistentes de alta confiança relativa.**
