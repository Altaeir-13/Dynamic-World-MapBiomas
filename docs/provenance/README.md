# Manifestos e procedência

| Arquivo | Conteúdo |
|---|---|
| `preservation_manifest.csv` | Todos os 44.080 arquivos preexistentes, incluindo ambiente e Git: caminho relativo, tamanho, classificação, ação, justificativa e destino remoto; hash de arquivos do projeto fora de Git/venv/.agents |
| `deletion_candidates.csv` | Lista única consolidada: candidatos preexistentes e auxiliares novos em `.release-work/`; nenhuma exclusão executada. Aprovação humana obrigatória |
| `cleanup_dry_run.json` | Simulação, contagem e bytes por grupo; `executed=false` |
| `before_summary.json` | Medição inicial por pasta; bytes lógicos dos arquivos, não tamanho alocado em disco |
| `cleanup_proposal.json` | Medição local após publicação/clone, seleção pública e total que pode ser liberado; fase e escopo explícitos |
| `release_checksums.csv` | Hashes dos artefatos selecionados para a publicação; exclui a si próprio e o relatório/evidências que registram a validação/publicação |
| `source_audit.json` | Docstrings, imports e I/O dos scripts inspecionados; fontes de ferramenta privada sem função científica excluídas |
| `content_audit.csv` | Inspeção de schemas/metadados de dados, manuscritos e duplicações |
| `validation.json` | Verificações locais efetivamente executadas, sem recálculo experimental |
| `clone_verification.json` | Recuperação do commit científico num clone do GitHub, hashes e verificação offline |
| `user_diff_before.patch` | Mudança preexistente do usuário no acesso GEE, preservada no código publicado |
| `development_sources.zip` | Implementações substituídas, testes exploratórios e fontes editoriais; caminhos originais mantidos por membro |
| `historical_evidence.zip` | Relatórios históricos, tabelas/figuras RAW e inválidas, manifesto antigo e requisitos originais |
| `editorial_provenance.zip` | Predecessores DOCX necessários à cadeia e QA JSON de documento/citações/figuras |

Os ZIPs foram validados por CRC e SHA-256 de cada membro contra o original; o manifesto registra `arquivo.zip::caminho_original`. Podem ser listados com `python -m zipfile -l ...` e extraídos em outro diretório. Não sobrescreva a versão final com um arquivo histórico. Ferramenta que lia logs privados de conversa não foi publicada.

A classificação `obsoleto` significa substituído para execução científica, não ausência de valor histórico. Por isso as fontes/evidências relevantes permanecem compactadas. Checkpoints com nomes antigos foram examinados quanto à função e à materialização atual. O clone contém as entradas finais, coordenadas, pesos e versões RAW necessárias para auditar a mudança; não representa backup integral de todos os caches nem dos catálogos externos.

Nada no manifesto autoriza automaticamente exclusões. A limpeza exige aprovação da lista consolidada após push e clone confirmados. A lista só vale dentro da raiz deste projeto. O Git principal, orientações locais e PDFs externos foram mantidos fora dos candidatos. `.release-work/` é exclusivamente auxiliar e foi criado nesta tarefa; inclui o Git do clone descartável, distinto do histórico principal preservado. Tamanhos correspondem à medição registrada antes do commit de evidências; novos metadados/logs auxiliares podem variar ligeiramente até a aprovação.
