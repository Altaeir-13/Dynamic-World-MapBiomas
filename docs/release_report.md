# Relatório da organização — 13/10/2026

Organização científica e documental publicada, com push e recuperação por clone do GitHub confirmados. Resultados congelados preservados. **Limpeza local não executada: depende de aprovação expressa da lista única consolidada.**

## Estrutura e seleção

A árvore pública contém `src/gee`, `src/analysis`, `scripts`, `config`, `data/reference`, `data/processed`, `data/audit`, `tables`, `figures`, `paper` e `docs/provenance`. O [README](../README.md) é a entrada; [arquitetura](architecture.md) lista as funções, entradas, saídas e dependências dos 11 módulos GEE, sete de análise e duas ferramentas de manutenção.

Conservados: núcleo anual canônico; exportação/consolidação por lotes; amostra 40k/20k; extração anual e mensal corrigida; auditorias de suporte/paginação; regressão e bootstrap/robustez usados no estudo. Processadores redundantes do censo, testes de desempenho/Balsas e ajustes específicos de lotes foram reunidos no ZIP de fontes. Apenas quatro arquivos eram versionados antes; os legados excluídos da seleção pública eram majoritariamente não versionados, portanto não se apagou seu histórico Git.

Manuscrito final: `final_title_references` PDF/DOCX/Markdown, título solicitado e autor preenchido. Dois gráficos definitivos foram identificados explicitamente. Os seis gráficos do manifesto original permanecem para auditoria, com aviso de anotações legadas; nenhum foi retocado. Os predecessores científicos/editoriais relevantes estão compactados como evidência, sem dezenas de scripts provisórios na árvore operacional.

## Documentação e dados

Criados README principal e por pasta; arquitetura, metodologia, recuperação/reexecução, ambiente, fontes/licenças/volumes, resultados, histórico científico e este relatório. Dependências diretas fixadas e lock do ambiente completo; `.env.example`, ignore seletivo e atributos para preservar bytes científicos. O projeto GEE foi parametrizado por `EE_PROJECT`; os parâmetros científicos permanecem preservados.

GitHub selecionado: dois parquets finais (42,8 MB no total), coordenadas/pesos, censo/sumário, 21 CSVs de lotes, geometrias/lista/datas, tabelas finais e auditorias, manuscrito, figuras e dois parquets RAW de comparação (41,8 MB). Cada arquivo selecionado é inferior a 50 MiB, sem necessidade de LFS. Rasters nacionais continuam nos catálogos públicos com IDs e instruções de acesso documentados. Normas de terceiros permanecem locais por licença de redistribuição não comprovada.

## Validação sem refazer o experimento

Os 33 hashes do manifesto científico original foram conferidos. Todos os dados, tabelas, figuras e arquivos de `paper/` preexistentes permaneceram byte a byte. Arquivos compactados foram comparados por SHA de membro e CRC. A instalação direta em um ambiente Python novo passou; `pip check` não identificou dependências quebradas. Sintaxe é verificada sem importar GEE. A verificação `--data` confere contagens/schemas/IDs/pertencimento e pesos positivos, sem reestimar métricas.

O DOCX final foi renderizado novamente em área auxiliar e as cinco páginas foram inspecionadas; título e texto normalizado conferem com o PDF preservado. Não houve refit, bootstrap novo, exportação/amostragem GEE, recálculo de hipóteses ou alteração estatística. O clone confirmou recuperação dos artefatos e funcionamento da validação offline, sem executar o experimento remoto.

## Publicação e clone independente

Repositório: [Altaeir-13/Dynamic-World-MapBiomas](https://github.com/Altaeir-13/Dynamic-World-MapBiomas), branch **main**, permissão ADMIN verificada. Commit científico: [`38a3d0cc1aabc98849c7d68e3a1e024842d9aa0f`](https://github.com/Altaeir-13/Dynamic-World-MapBiomas/commit/38a3d0cc1aabc98849c7d68e3a1e024842d9aa0f). O hash remoto coincidiu com o local após push; o commit anterior `77d1756` permanece ancestral. Nenhum push forçado, rebase ou reescrita de histórico foi usado. Um commit subsequente registra as evidências deste relatório, sem mudar os dados científicos.

Clone HTTPS diretamente do GitHub em `.release-work/verification-clone`, sem copiar a árvore local. No commit científico, os **153 arquivos públicos** foram comparados por SHA-256 contra a origem: todos idênticos. O clone recuperou os 33 artefatos do manifesto científico e os 150 do manifesto ampliado. Sintaxe dos 20 scripts/módulos de execução passou; CRC dos três ZIPs passou. `--data` confirmou 40.000 registros anuais, 480.000 mensais, 20.000 principais, 337 municípios, IDs/pertencimento e pesos elegíveis positivos.

O ambiente de teste foi criado vazio e instalado com os requisitos diretos selecionados. O hash desses requisitos coincidiu com o arquivo do clone, e resolução `--dry-run --no-index` dos requisitos clonados passou nesse ambiente novo. Imports científicos e `pip check` passaram. Os links relativos da documentação principal foram conferidos no clone. Relatórios históricos preservam referências locais antigas como evidência; a documentação nova não depende delas. Não se afirma que foi testado fisicamente outro computador/OS nem autenticado um projeto de outra conta. [Evidências do clone](provenance/clone_verification.json) e [validação](provenance/validation.json).

## Medição e exclusões propostas

| Medição | Arquivos | Bytes lógicos |
|---|---:|---:|
| Local antes da organização, incluindo venv/Git | 44.080 | 2.607.667.917 (2,43 GiB) |
| Local após publicação científica e clone, antes do commit de evidências | 62.446 | 3.721.089.538 (3,47 GiB) |
| Seleção pública no commit científico | 153 | 125.099.784 (119,30 MiB) |
| Auxiliares novos de instalação/render/clone, incluídos no local acima | 18.333 | 967.315.298 (922,50 MiB) |
| Candidatos consolidados à exclusão | 62.248 | 3.514.584.617 (3,27 GiB) |

O espaço local aumentou durante a preparação porque os originais continuam preservados e foram criados ambiente/clone de teste e cópias públicas de auditoria. **Não houve liberação de espaço ainda.** A seleção pública é distinta do total local. Novos commits, logs e arquivos deste relatório alteram levemente a medição subsequente. São tamanhos lógicos; NTFS pode alocar espaço diferente. O snapshot e sua fase estão em [cleanup_proposal.json](provenance/cleanup_proposal.json).

Com a lista consolidada e as evidências de recuperação, a seleção pública passa a **155 arquivos, aproximadamente 130,2 MB decimais**. O acréscimo corresponde à documentação da limpeza/clone, sem novos resultados científicos.

Simulação inicial: 43.915 candidatos preexistentes, 2.547.269.319 bytes (2,37 GiB). Somados os 18.333 auxiliares de verificação, a proposta consolidada libera **aproximadamente 3,51 GB decimais (3,27 GiB)**. Inclui `.venv` (~1,22 GB), intermediários/checkpoints e versões substituídas dos dados (~1,27 GB), scripts descartados, renders/versões editoriais e `.release-work/` (~967 MB). [Lista única exata](provenance/deletion_candidates.csv), [manifesto dos preexistentes](provenance/preservation_manifest.csv) e [resumo por grupo](provenance/cleanup_dry_run.json) registram caminhos, tamanho, classificação, justificativa e destino remoto quando aplicável. O par de diretórios RAW de extração foi confirmado idêntico em seus 182 membros.

O Git principal, `.agents`, dados finais originais selecionados e PDFs externos não pertencem à lista. Nenhuma exclusão foi executada, e os originais fora da seleção pública continuam locais/ignorados. O Git dentro do clone auxiliar pertence ao diretório descartável `.release-work/`, não ao histórico principal. A lista nunca autoriza excluir fora da raiz deste projeto. Exclusão permanece condicionada à sua aprovação; antes de executá-la, os caminhos devem ser resolvidos e validados contra a raiz, e arquivos modificados desde o inventário devem ser reavaliados.

## Limitações e pendências

Ausência de verdade de campo independente; dados DW não calibrados como correção; fonte Sentinel-2 compartilhada; suporte temporal residual; distância truncada; 30m sem suíte final identificada. Regeneração desde os catálogos exige projeto/credenciais/cotas e não foi testada nesta organização. Reexecução estatística integral não foi realizada por instrução do responsável. O lock completo é snapshot histórico; a instalação validada foi das dependências diretas, com transitivas resolvidas pelo índice. Não se promete resultado bit a bit em outros editores/OS/estados futuros do serviço.

Pendência obrigatória: sua aprovação das exclusões locais. Push e recuperação do commit científico foram confirmados e documentados. Até a aprovação e execução, a limpeza deve ser descrita como **pendente**, nunca concluída.
