# Emenda Pré-Resultado ao Protocolo Científico (Checkpoint 3D)

**Data e Hora Formal da Emenda:** 2026-10-07 21:16:11-03:00  
**Status de Execução:** Pré-resultado (Registrada ANTES da execução das hipóteses H1–H4)  
**Projeto:** Dinâmica da Concordância e Discordância entre Dynamic World e MapBiomas no MATOPIBA (2025)  

---

## 1. Redação Original da Regra de Fallback Temporal

No protocolo metodológico preliminar e nas especificações técnicas do projeto (`PROJECT_BRIEF.md`, seção temporal):
```yaml
temporal:
  primary_min_valid_months: 8
  fallback_min_valid_months: 6
  monthly_weighting: equal_valid_months
  missing_months: no_imputation
```
Previa-se que:
> "Caso a cobertura temporal anual no MATOPIBA se revelasse insuficiente (por exemplo, proporção substancial de pontos com menos de 8 meses válidos), acionar-se-ia a regra de contingência/fallback reduzindo a exigência de elegibilidade para $\ge 6$ meses válidos."

---

## 2. Diagnóstico Técnico: Por que o Gatilho Original Era Circular

Durante a auditoria forense do Checkpoint 3D, identificou-se que o teste proposto para ativação do fallback a partir da amostra era **tecnicamente malformado e tautológico/circular**:

1. **Construção do Plano Amostral Canônico:** O universo de amostragem canônico (*sampling frame*) foi construído a partir de uma máscara raster wall-to-wall que impôs estritamente a condição de suficiência temporal $n_{\text{valid\_months}} \ge 8$.
2. **Consequência Amostral Inevitável:** Qualquer amostra extraída sem reposição desse universo (incluindo a Master Sample de 40.000 pontos com `root_seed=25`) conteria, por definição matemática e desenho amostral, **exatamente zero pontos** com $n_{\text{valid\_months}} < 8$.
3. **Circularidade:** Avaliar a proporção de pontos com $< 8$ meses na Master Sample para decidir se o critério de 8 meses devia ser relaxado era uma verificação circular. O fato de existirem 0 pontos abaixo de 8 meses na amostra reflete a regra de inclusão do *frame*, não a inexistência de pixels com 6 ou 7 meses na paisagem geográfica real.

---

## 3. Decisão Formal Pré-Resultado

1. **Congelamento da População Analítica Primária:**
   - O critério de elegibilidade temporal primário é formal e definitivamente congelado como:
     $$n_{\text{valid\_months}} \ge 8$$
   - Todos os 40.000 pontos da Master Sample congelada no Checkpoint 3D atendem a esse critério com média de $9,73 \pm 1,33$ meses válidos.
2. **Proibição de Falsa Sensibilidade $\ge 6$ Meses:**
   - Como os pixels com exatamente 6 ou 7 meses válidos foram excluídos na etapa de geração do *sampling frame*, a Master Sample atual **não pode** ser usada diretamente para inferir uma sensibilidade $\ge 6$ meses sem incorrer em vício de seleção amostral.
   - Qualquer análise de sensibilidade para $\ge 6$ meses fica postergada para momento oportuno, exigindo a reconstrução formal de um *sampling frame* suplementar com suas respectivas probabilidades de inclusão e pesos de expansão.
3. **Invariância do Checkpoint 3D:**
   - Todos os 10 artefatos e os hashes SHA-256 gerados no Checkpoint 3D permanecem intocados e congelados como a população de inferência primária autoritativa.
4. **Confirmação Pré-Resultado:**
   - Registra-se solenemente que esta emenda foi formalizada **antes** da realização dos testes inferenciais das hipóteses H1–H4 e antes da visualização dos modelos estatísticos.
