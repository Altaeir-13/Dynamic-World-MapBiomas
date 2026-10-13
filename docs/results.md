# Resultados finais e suas fontes

## Autoridade e integridade

As 21 tabelas estatísticas do manifesto científico são o estado corrigido. O quadro censitário e as tabelas de desenho complementam esse conjunto. O manifesto original tem 33 artefatos; seus hashes foram conferidos sem regenerá-lo. Seu texto ainda chama as seis figuras antigas de publicação, mas a auditoria editorial posterior encontrou anotações legadas. A classificação desta documentação prevalece para uso editorial. O manifesto continua preservado como registro de bytes, não certificado universal de validade das legendas.

## Métricas congeladas

| Resultado | Valor | Fonte primária preservada |
|---|---|---|
| Domínio elegível | 52.342.114,746229 ha; 5.354.669.418 pixels | `sampling_frame_10m.csv` |
| Discordância censitária AN+NA | 7.477.177,227037 ha; 14,2852028% por área; 14,3109606% por pixels | Quadro e censo materializado |
| Estimativa principal | 14,3148430% por pixels; 14,2896974% por área | `descriptive_regime_proportions.csv`; auditoria editorial existente |
| H1 | ΔH=+0,0162135; IC [+0,0102649;+0,0221115] | `hypothesis_h1_results.csv`, `spatial_bootstrap_contrasts.csv` |
| H2a | ΔJSD=+0,0074922; IC [+0,0046759;+0,0102306] | `hypothesis_h2_results.csv`, bootstrap corrigido |
| H2b | ΔS=−0,0789586; IC [−0,0974054;−0,0599416] | Mesmas fontes |
| H3 | <30m: 45,9057%; ≥250m: 11,8669%; razão 3,868381 | `robustness_comprehensive_summary.csv`, H3 por faixa |
| H4 principal | 207/5.143; 4,0249% bruto; 4,2772950% ponderado por pixels | `hypothesis_h4_robust_disagreement.csv` |
| H4 mestre | 404/10.286; 3,9277% bruto; 4,1687301% ponderado por pixels | Mesma tabela final |
| Incerteza espacial | Alcance 25,62164 km → bloco 30 km; 1.999 réplicas | `spatial_semivariogram_parameters.csv` e implementação |

Todos os números foram transcritos das tabelas e auditorias já persistidas; não houve novos cálculos. Percentuais censitários de área e pixels têm denominadores diferentes. Não aplicar IC amostral a parâmetro censitário. O IC [3,25;4,61] da razão H3 em rascunhos não tem suporte em tabela final identificada; não é reportado.

A regressão autoritativa está em `regression_logistic_rescaled_odds_ratios.csv`, com IC analítico e espacial separados; coeficientes brutos e diagnósticos são suplementos. Por +100 m, OR≈0,360; por +0,10 H, OR≈1,421; por +0,10 S, OR≈0,925; por +0,01 JSD, OR≈0,987 com IC espacial incluindo 1. Use a tabela para todos os algarismos/contrastes; não interpretar inclusão de 1 como prova de equivalência ou ausência de informação.

## Figuras definitivas

**Somente estas duas são as figuras definitivas incorporadas no artigo com o título solicitado:**

- `figures/final_figure1.png`, idêntica a `paper/final_review_assets/figure1.png`: proporções amostrais por pixels e discordância estadual.
- `figures/final_figure2.png`, idêntica a `paper/final_review_assets/figure2.png`: taxas pontuais H3 e IC espaciais já tabulados.

Tabelas 1 e 2 definitivas estão no PDF/DOCX/Markdown `paper/manuscript_space_week_nordeste_2026_final_title_references.*`. Tabela 1 distingue censo/estimativa e denominadores; Tabela 2 reporta contrastes/OR e IC espaciais. A fonte editável é o DOCX, com o título e autor final já presentes.

As seis `figures/fig1_...` a `fig6_...` foram preservadas nos caminhos do manifesto para manter auditoria do congelamento. **Não são todas adequadas para republicação.** A auditoria `paper/manuscript_final_codex_review.md` identificou IC/tamanhos de efeito RAW nas anotações de fig3 JSD e fig4 estabilidade, e rotulagem inadequada de ponderação em fig1. O gerador 07 também contém constantes de anotações. Não corrigimos figuras congeladas nem usamos essas imagens no artigo final. Figuras RAW anteriores também estão no ZIP histórico e não devem ser confundidas com dados corrigidos.

## Robustez e limites

R1 (40k): discordância por pixels 14,31096%; R2 ({19}): 14,27820%; R3 (MB estável, 17.957 pontos): 12,12549%, conforme `robustness_comprehensive_summary.csv`. Sensibilidade espacial bootstrap 10/20/40 km é distinta da resolução nominal dos mapas. Resultados completos 30m não foram identificados como finalizados.

H4 descreve discordâncias que satisfazem os quatro filtros; não demonstra erro em campo. A ausência de verdade independente, a base Sentinel-2 compartilhada e a discrepância residual entre vetores anuais/mensais permanecem limitações. O relatório antigo com 405 casos H4/40k foi superado pela tabela final com 404 e pela auditoria editorial posterior, conservada como evidência.
