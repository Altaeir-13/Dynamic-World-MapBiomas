# Dynamic World × MapBiomas — MATOPIBA 2025

Este repositório preserva o experimento científico **ANÁLISE ESPACIAL E PROBABILÍSTICA DA DISCORDÂNCIA NO MAPEAMENTO DE LAVOURAS DO MATOPIBA: DYNAMIC WORLD E MAPBIOMAS**. O estudo investiga onde dois produtos de cobertura da terra discordam e como essa discordância se associa à ambiguidade probabilística, à variação temporal e à proximidade de bordas temáticas.

O domínio é a delimitação operacional dos **337 municípios do MATOPIBA**, reconstruída com a lista IBGE 2021 e a malha municipal 2025. Abrange Tocantins e porções do Maranhão, Piauí e Bahia. O período principal é 2025. Não há treinamento de classificador nem verdade de campo independente: **concordância não demonstra correção e discordância não identifica qual produto está errado**.

## Estado desta versão

Os resultados corrigidos estão congelados. A organização de 13/10/2026 não executou novamente o experimento, não ajustou modelos nem alterou tabelas, parquets, figuras congeladas ou o manuscrito. Os dados finais, coordenadas, pesos, geometrias, censo e tabelas estão incluídos no Git comum. As probabilidades mensais finais já incorporam a correção de resamostragem bilinear.

O clone permite **recuperar e auditar os resultados materializados sem Earth Engine**. Refazer o processamento desde os catálogos requer conta habilitada, projeto Google Cloud/Earth Engine, permissões, internet e cotas. A execução integral em outro computador e a reprodução bit a bit de futuras respostas do serviço não foram demonstradas. Veja [reprodutibilidade](docs/reproducibility.md) e [relatório da organização](docs/release_report.md).

## Começar em outro computador

```powershell
git clone https://github.com/Altaeir-13/Dynamic-World-MapBiomas.git
cd Dynamic-World-MapBiomas
python scripts/verify_release.py
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts/verify_release.py --data
```

Ambiente científico registrado: **Python 3.14.5, Windows**. `requirements.txt` fixa as dependências diretas; `requirements-lock.txt` registra o ambiente local completo. Em Linux/macOS, use `.venv/bin/python`. Leia [ambiente](docs/environment.md) antes de preparar acesso ao GEE. Não execute os scripts de análise sobre a cópia congelada: eles escrevem nas tabelas e figuras.

## Dados e desenho

- Dynamic World V1: `GOOGLE/DYNAMICWORLD/V1`, intervalo `[2025-01-01, 2026-01-01)`, nove probabilidades.
- MapBiomas Cobertura 10 m, Coleção 4: banda `classification_2025`; série 2017–2025 usada em robustez.
- Lavoura: Dynamic World `crops` (argmax anual, índice 4); MapBiomas `{19,36}`. Classes operacionais 18/21, códigos inválidos e ausência de cobertura elegível ficam fora da comparação principal. Pastagem e silvicultura são não lavoura.
- Grade primária: grade nativa MapBiomas, EPSG:4326 e transformação congelada, resolução nominal 10 m. Bilinear somente nas probabilidades; operações métricas em EPSG:5880. Áreas usam `pixelArea`, não uma constante de 100 m².
- Temporalidade: média neutra de duplicatas no mesmo dia → média de dias válidos por mês → média anual com pesos iguais entre meses válidos. Pelo menos oito meses, sem imputação.
- Regimes: AA (ambos lavoura), AN (somente MapBiomas lavoura), NA (somente DW lavoura), NN (ambos não lavoura).
- Amostra mestre: 40.000 pontos; principal: 20.000 aninhados. Dezesseis estratos estado × regime, 410 subestratos operacionais ativos e 182 fatias com amostra. Coordenadas e probabilidades de inclusão estão materializadas; seed 25.

## Fluxo científico

```text
Geometria e suporte fixo MATOPIBA + 5 km
  → composições DW e crosswalk alinhados à grade MapBiomas
  → censo canônico em 182 fatias, quadro e cotas
  → amostra mestre e subconjunto principal com pesos
  → extração anual, série mensal harmonizada e indicadores H/JSD/S/distância
  → descrição ponderada, H1–H4, regressão e bootstrap espacial
  → robustez, tabelas corrigidas e manuscrito definitivo
```

Há duas construções temporais distintas: o vetor anual canônico e a média dos vetores mensais harmonizados. Máscaras variáveis e ordem de operações produzem discrepância residual; não se pressupõe identidade exata. [Metodologia](docs/methodology.md) descreve as definições executadas.

## Principais resultados preservados

| Estimando | Resultado final | Fonte |
|---|---|---|
| Área elegível censitária | 52.342.114,75 ha | `tables/sampling_frame_10m.csv` |
| Discordância censitária por área | 7.477.177,23 ha; 14,2852% | Quadro censitário, AN + NA |
| Discordância amostral por pixels, 20k | 14,3148% | `tables/descriptive_regime_proportions.csv` |
| H1, ΔH | +0,0162135; IC espacial [+0,0102649; +0,0221115] | Hipóteses e bootstrap |
| H2, ΔJSD / ΔS | +0,0074922 / −0,0789586 | Hipóteses e bootstrap corrigidos |
| H3, borda <30 m / interior ≥250 m | 45,9057% / 11,8669%; razão 3,868381 | `tables/robustness_comprehensive_summary.csv` |
| H4, 20k / 40k | 207 / 404 casos; 4,2773% / 4,1687% dos discordantes, ponderados por pixels | `tables/hypothesis_h4_robust_disagreement.csv` |

O bootstrap principal usa blocos de **30 km**, 1.999 réplicas e seed 25. O modelo logístico final usa distância **linear**, entropia, JSD, estabilidade e estado. Não confunda proporções por pixels com proporções por área, IC analítico com espacial, nem censo com estimativa amostral. [Resultados](docs/results.md) identifica fontes, figuras definitivas e ressalvas.

## Estrutura pública

| Pasta/arquivo | Função |
|---|---|
| `src/gee/` | Implementação do suporte anual, censo, amostragem, extração corrigida e auditorias indispensáveis |
| `src/analysis/` | Implementação efetivamente usada na descrição, H1–H4, regressão, bootstrap e robustez |
| `scripts/` | Verificação local sem recálculo e exportação documental em diretório separado |
| `config/` | Snapshots históricos preservados e registro consolidado da versão final |
| `data/reference/` | Geometrias, 337 municípios, domínios de suporte e datas observadas |
| `data/processed/` | Parquets finais, amostra mestre, censo e CSVs de exportação |
| `data/audit/` | Dois parquets RAW para comparação com o processamento corrigido |
| `tables/` | Tabelas finais e evidências do desenho/auditorias |
| `figures/` | Duas figuras finais do artigo e seis figuras congeladas para auditoria, com ressalvas explícitas |
| `paper/` | PDF/DOCX/Markdown definitivos, figuras incorporadas e procedência editorial |
| `docs/` | Metodologia, arquitetura, dados, ambiente, execução e histórico científico |
| `docs/provenance/` | Manifestos, hashes, simulação de exclusão e arquivos compactos de procedência |

Versões substituídas não integram o pipeline operacional. Fontes históricas necessárias foram reunidas em três ZIPs auditáveis; sua listagem consta dos manifestos. Arquivos locais excluídos da seleção pública continuam no computador até aprovação expressa de sua exclusão. [Arquitetura](docs/architecture.md) explica cada script preservado.

## Limitações e direitos

Sem referência independente, o estudo não estima acurácia absoluta. As probabilidades DW não são probabilidades calibradas de correção; associações não são efeitos causais. Produtos compartilham parte da base Sentinel-2. Suporte, masks, legenda, elegibilidade e truncamento de distância condicionam os resultados; a sensibilidade espacial 30 m prevista no brief não possui uma tabela final completa identificada nesta auditoria.

Dados-fonte mantêm seus termos e atribuições: [Dynamic World no catálogo oficial](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1), [MapBiomas Cobertura 10 m](https://brasil.mapbiomas.org/iniciativas-e-produtos/cobertura-e-uso-da-terra/cobertura-10m/cobertura/) e [malhas IBGE](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/15774-mlhas.html). Consulte [dados e licenças](docs/data.md). Esta organização não atribui uma nova licença ao código ou manuscrito do autor.
