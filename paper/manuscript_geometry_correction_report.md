# Correção urgente de conformidade geométrica

**Data:** 12 de outubro de 2026  
**Resultado:** geometria corrigida; **READY FOR SINGLE-AUTHOR REVIEW**. Nome, e-mail e aprovação pessoal continuam pendentes; não se declara pronto para submissão.

Foram confrontados o manuscrito e os dois scripts com o [modelo oficial](https://spaceweeknordeste.com/wp-content/uploads/2026/01/normas_trabalhos_cientificos_swn_2026.pdf), as [instruções aos autores](https://spaceweeknordeste.com/wp-content/uploads/2026/01/instrucoes2_autores_swn_2026.pdf) e o [formulário Doity](https://doity.com.br/space-week-nordeste-2026/artigos?box=1). A plataforma exibe o período **02/06/2026 a 12/10/2026**; não mostra um horário-limite nessa página. A confirmação de envio com um único autor está prevista no formulário. Não foi encontrada exigência expressa de orientador nos PDFs consultados.

## Problema e correção

A inspeção anterior de `page.images` verificava dimensões/resolução, mas não validava as coordenadas dos objetos. Os limites medidos no PDF anterior eram:

- Figura 1: x=22,1897–200,1838 mm, fora do limite direito de 197 mm.
- Figura 2: x=22,1897–108,1969 mm, fora do limite da primeira coluna de 105 mm.

Foi editada uma **cópia do DOCX `author_review` atual**. Os parágrafos gráficos passaram a ter alinhamento à esquerda e recuos esquerdo, direito e de primeira linha explicitamente zerados. Também foram zerados os atributos `distT`, `distB`, `distL` e `distR` de cada objeto `wp:inline`; essa última alteração removeu o deslocamento observado na exportação. As imagens não foram substituídas, recortadas ou redimensionadas: bytes e dimensões OOXML permanecem idênticos.

A checagem ampliada identificou ainda traços externos das tabelas aproximadamente 0,1 mm além da área útil. As tabelas foram centralizadas com largura nominal de **177,6 mm**, deixando espaço para os traços. Valores, fontes, alturas e legibilidade foram preservados.

## Medidas finais do PDF exportado

Coordenadas em milímetros, com origem no canto superior esquerdo. O objeto gráfico completo, inclusive suas margens brancas, é considerado.

| Objeto | Página | x inicial | x final | y superior | y inferior | Resolução efetiva |
|---|---:|---:|---:|---:|---:|---|
| Figura 1 | 3 | 18,9971 | 196,9911 | 45,3496 | 108,3557 | 299,96 × 299,93 dpi |
| Figura 2 | 4 | 18,9971 | 105,0043 | 24,9767 | 95,9908 | 300,05 × 300,09 dpi |

Arredondadas à precisão usual: **Figura 1, x=19,00–196,99 mm; Figura 2, x=19,00–105,00 mm**. A primeira ocupa a largura total; a segunda permanece na primeira coluna. O verificador admite **0,05 mm exclusivamente para quantização PDF/twips**; os resíduos de poucos micrômetros não correspondem ao deslocamento de 3,2 mm anterior.

Foram verificados os **dois objetos de imagem** e **53 objetos vetoriais** — 35 linhas e 18 retângulos, incluindo bordas e preenchimentos das tabelas; não há curvas adicionais. Nenhum falhou na verificação geométrica final. As tabelas ficaram entre x=19,1911 e 196,8030 mm nas caixas detectadas, com seus traços também dentro da área útil.

## Revalidação documental

| Item | Resultado |
|---|---|
| Extensão | **4 páginas**, dentro do limite de cinco; sem números de página. |
| Resumo e Abstract | **177 e 171 palavras**, preservados. |
| Tipografia | Times New Roman incorporada, variantes regular/negrito/itálico/negrito-itálico; únicos tamanhos textuais: **9, 10 e 14 pt**. |
| Distribuição dos tamanhos | Título 14 pt; corpo, autoria, tabelas e referências 10 pt; legendas 9 pt em negrito. |
| Papel e margens | Carta, 215,9 × 279,4 mm; margens 25/18,9/25,4/19 mm, na ordem superior/direita/inferior/esquerda. |
| Área/colunas | 178 × 229 mm; duas colunas de aproximadamente 86 mm e calha de 6 mm; largura total nos elementos pertinentes. |
| Autoria | Um único autor no cabeçalho e nos metadados; nome/e-mail não foram alterados. |
| Legendas e chamadas | Figuras 1/2 e Tabelas 1/2 conservam legendas e chamadas no corpo. |
| Referências | Oito entradas preservadas; primeira ocorrência das citações em ordem [1] a [8]. |
| DOCX/PDF | Texto integral coincide, removendo apenas espaços e quebras de linha. PDF exportado exclusivamente do DOCX corrigido. |

Todas as páginas do último render foram inspecionadas em resolução original. Página 1: título, autoria, resumos e início dos métodos completos. Página 2: métodos, fórmulas e Tabela 1 legíveis. Página 3: Figura 1 agora alinhada à área útil, resultados e Tabela 2 íntegros. Página 4: Figura 2 dentro da primeira coluna, legenda na mesma página, discussão, conclusões e referências completas. Não foram observados cortes ou sobreposições. Não se declara equivalência entre Word e LibreOffice.

## Scripts, preservação e entrega

`build_author_review.py` agora produz arquivos com sufixo **`author_review_corrected`**, preservando a versão anterior. A opção `--fix-geometry` parte do DOCX `author_review`; `--export-only` exporta o mestre corrigido sem reconstruí-lo. O ajuste dos objetos foi incorporado também à geração documental reproduzível.

`verify_author_review.py` passou a verificar:

- As caixas `x0/top/x1/bottom` de **todas** as imagens de todas as páginas.
- Correspondência entre imagens do PDF e desenhos do DOCX, com largura da seção pertinente.
- Limites da área útil e limites de cada coluna para imagens de uma coluna.
- Caixas de linhas, retângulos e curvas; resolução efetiva das imagens.
- Limite normativo de até cinco páginas, em vez de aceitar somente quatro.
- Ordem real das primeiras citações, além das verificações documentais já existentes.

Arquivos entregues:

- `paper/manuscript_space_week_nordeste_2026_author_review_corrected.docx`
- `paper/manuscript_space_week_nordeste_2026_author_review_corrected.pdf`
- `paper/manuscript_geometry_correction_report.md`
- `paper/submission_manual_checklist.md`

As versões anteriores dos scripts estão em `paper/qa_geometry_review/previous_build_author_review.py` e `previous_verify_author_review.py`. As medidas e verificações finais estão em `document_checks.json`; as medidas anteriores, em `previous_graphic_bounds.json`, junto dos quatro renders finais.

Comandos de reprodução documental:

```powershell
& 'C:/Users/Altair/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' paper/build_author_review.py --fix-geometry --render
& 'C:/Users/Altair/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' paper/verify_author_review.py
```

O texto inteiro do DOCX anterior foi comparado ao corrigido e permanece idêntico. Dados científicos, referências, pixels das imagens e autoria foram preservados. Os hashes dos arquivos anteriores `author_review.docx/pdf` e `final_review.docx/pdf/md` conferem. Não houve análise científica, alteração de datasets, commit, push, preenchimento ou envio do formulário.

**Pendências humanas:** confirmar a grafia definitiva de **Randerson Sousa de Sá Nunes**, diante da identificação “Anderson”, confirmar **randerson.sdsn@gmail.com**, aprovar o PDF e escolher a área temática no formulário. O checklist registra uma opção realmente disponível e fornece os demais campos para preenchimento manual.
