# Relatório da organização — 13/10/2026

Organização científica e documental preparada; resultados congelados preservados. Publicação e verificação de clone serão registradas após confirmação efetiva. **Limpeza local não executada: depende de aprovação expressa da lista consolidada.**

## Estrutura e seleção

A árvore pública contém `src/gee`, `src/analysis`, `scripts`, `config`, `data/reference`, `data/processed`, `data/audit`, `tables`, `figures`, `paper` e `docs/provenance`. O [README](../README.md) é a entrada; [arquitetura](architecture.md) lista as funções, entradas, saídas e dependências dos 11 módulos GEE, sete de análise e duas ferramentas de manutenção.

Conservados: núcleo anual canônico; exportação/consolidação por lotes; amostra 40k/20k; extração anual e mensal corrigida; auditorias de suporte/paginação; regressão e bootstrap/robustez usados no estudo. Processadores redundantes do censo, testes de desempenho/Balsas e ajustes específicos de lotes foram reunidos no ZIP de fontes. Apenas quatro arquivos eram versionados antes; os legados excluídos da seleção pública eram majoritariamente não versionados, portanto não se apagou seu histórico Git.

Manuscrito final: `final_title_references` PDF/DOCX/Markdown, título solicitado e autor preenchido. Dois gráficos definitivos foram identificados explicitamente. Os seis gráficos do manifesto original permanecem para auditoria, com aviso de anotações legadas; nenhum foi retocado. Os predecessores científicos/editoriais relevantes estão compactados como evidência, sem dezenas de scripts provisórios na árvore operacional.

## Documentação e dados

Criados README principal e por pasta; arquitetura, metodologia, recuperação/reexecução, ambiente, fontes/licenças/volumes, resultados, histórico científico e este relatório. Dependências diretas fixadas e lock do ambiente completo; `.env.example`, ignore seletivo e atributos para preservar bytes científicos. O projeto GEE foi parametrizado por `EE_PROJECT`; os parâmetros científicos permanecem preservados.

GitHub selecionado: dois parquets finais (42,8 MB no total), coordenadas/pesos, censo/sumário, 21 CSVs de lotes, geometrias/lista/datas, tabelas finais e auditorias, manuscrito, figuras e dois parquets RAW de comparação (41,8 MB). Cada arquivo selecionado é inferior a 50 MiB, sem necessidade de LFS. Rasters nacionais continuam nos catálogos públicos com IDs e instruções de acesso documentados. Normas de terceiros permanecem locais por licença de redistribuição não comprovada.

## Validação sem refazer o experimento

Os 33 hashes do manifesto científico original foram conferidos. Todos os dados, tabelas, figuras e arquivos de `paper/` preexistentes permaneceram byte a byte. Arquivos compactados foram comparados por SHA de membro e CRC. A instalação direta em um ambiente Python novo passou; `pip check` não identificou dependências quebradas. Sintaxe é verificada sem importar GEE. A verificação `--data` confere contagens/schemas/IDs/pertencimento e pesos positivos, sem reestimar métricas.

O DOCX final foi renderizado novamente em área auxiliar e as cinco páginas foram inspecionadas; conteúdo e PDF original foram preservados. Não houve refit, bootstrap novo, exportação/amostragem GEE, recálculo de hipóteses ou alteração estatística. O teste do clone avaliará recuperação dos artefatos e funcionamento da validação offline, não a execução integral do experimento remoto.

## Medição e exclusões propostas

Antes: **44.080 arquivos, 2.607.667.917 bytes** (2,43 GiB), incluindo ambiente e `.git`, excluindo auxiliares criados nesta tarefa. São tamanhos lógicos; o espaço alocado e metadados NTFS podem diferir. A medição pública e a medição local após preparação serão acrescentadas após validação do clone.

Simulação inicial: **43.915 candidatos, 2.547.269.319 bytes** (2,37 GiB). Inclui `.venv` (~1,22 GB), intermediários/checkpoints e versões substituídas dos dados (~1,27 GB), scripts descartados, renders e versões editoriais. [Lista exata](provenance/deletion_candidates.csv), [manifesto completo](provenance/preservation_manifest.csv) e [resumo por grupo](provenance/cleanup_dry_run.json) registram tamanho, classificação, justificativa e destino remoto quando aplicável. O par de diretórios RAW de extração foi confirmado idêntico em seus 182 membros.

Arquivos Git, `.agents`, dados finais originais selecionados e PDFs externos não pertencem à lista. Nenhuma exclusão foi executada, e os originais fora da seleção pública continuam locais/ignorados. Auxiliares novos de instalação, render e clone em `.release-work/` serão relacionados adicionalmente antes da aprovação. A lista nunca autoriza excluir fora da raiz deste projeto.

## Limitações e pendências

Ausência de verdade de campo independente; dados DW não calibrados como correção; fonte Sentinel-2 compartilhada; suporte temporal residual; distância truncada; 30m sem suíte final identificada. Regeneração desde os catálogos exige projeto/credenciais/cotas e não foi testada nesta organização. Reexecução estatística integral não foi realizada por instrução do responsável. O lock completo é snapshot histórico; a instalação validada foi das dependências diretas, com transitivas resolvidas pelo índice. Não se promete resultado bit a bit em outros editores/OS/estados futuros do serviço.

Pendência obrigatória: aprovação humana das exclusões locais somente após push e recuperação confirmados. Este relatório será atualizado com evidências reais de publicação e clone antes desse pedido.
