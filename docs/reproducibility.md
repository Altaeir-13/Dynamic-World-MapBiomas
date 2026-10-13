# Recuperação e reprodutibilidade

## 1. Recuperar a versão congelada

```powershell
git clone https://github.com/Altaeir-13/Dynamic-World-MapBiomas.git
cd Dynamic-World-MapBiomas
python scripts/verify_release.py
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts/verify_release.py --data
```

A primeira verificação usa somente stdlib. A segunda lê os dados preservados, sem GEE e sem refazer análise. Os manifests validam o estado corrigido. `tables/checkpoint_3d_checksums.sha256` é histórico anterior à correção mensal: não é esperado que seus hashes dos parquets coincidam com o estado corrigido. Use o manifesto `manuscript_results_manifest.csv` e `docs/provenance/release_checksums.csv` para a versão final.

As referências do manuscrito estão no Markdown e DOCX. As tabelas científicas são legíveis como CSV. O clone inclui ambos os parquets finais e as coordenadas originais; não precisa recuperar esses arquivos de Google Drive. A licença de uso dos dados-fonte e o acesso ao serviço continuam aplicáveis.

## 2. Reexecutar a análise sobre as entradas materializadas

Esta seção descreve a implementação preservada; **não foi executada na organização de 13/10/2026**. Crie outro clone/diretório para que nenhum arquivo congelado seja sobrescrito. Registre seu commit de origem e mantenha os hashes do original para comparação futura.

```powershell
python src/analysis/02_weighted_descriptive_analysis.py
python src/analysis/03_hypothesis_tests_h1_h4.py
python src/analysis/04_weighted_regression_model.py
python src/analysis/05_spatial_block_bootstrap.py
python src/analysis/06_robustness_analysis.py
```

Usar o Python do ambiente instalado (`.venv\Scripts\python.exe` no Windows). A ordem importa: regressão precede bootstrap/OR espaciais. O bootstrap exige CPU e tempo; sem GPU. Não confunda correspondência de valores numéricos com hash idêntico do CSV: bibliotecas, serialização e plataforma podem afetar bytes.

O runner histórico 08 também chama 07 para gerar seis figuras; elas possuem limitações editoriais já identificadas. Para ler/apresentar os resultados finais, use as tabelas congeladas e `figures/final_figure1/2.png`. Nenhum recálculo é necessário para recuperar o artigo. A suíte futura não deve ser considerada validada integralmente enquanto não for executada e comparada de forma independente.

## 3. Refazer desde os catálogos

Pré-requisitos: conta GEE habilitada, projeto próprio autorizado, GEE API, credenciais obtidas pela CLI, Drive com escopo exigido pelo downloader e internet. Autenticação fica fora do Git. O projeto original não concede acesso automaticamente a quem clona.

```powershell
$env:EE_PROJECT = 'seu-projeto-habilitado'
.venv\Scripts\earthengine.exe authenticate
.venv\Scripts\python.exe src/gee/01_check_access.py
```

O downloader usa credenciais GEE com acesso ao Drive. Se a autenticação não fornecer esse escopo, faça consentimento adequado ou baixe os CSVs manualmente para `data/processed/batches/` com seus nomes originais. Não copie tokens para o repositório.

Sequência operacional em **cópia separada**:

1. Preserve/use as geometrias, suportes e datas congelados. `02_boundary.py` é a reconstrução de origem da lista e contorno; sua execução só é necessária para investigar regeneração, e deve ser comparada ao hash congelado. APIs públicas podem mudar. Os suportes 1/5/10 km já estão disponíveis; o módulo usa 5 km.
2. `python src/gee/submit_canonical_batch_exports.py` consome o manifesto final com as subdivisões de lotes. Para uma nova execução, mova **nessa cópia** o registro histórico de tarefas e os CSVs/checkpoints existentes para uma pasta separada; não reutilize IDs de tarefas antigas como prova de uma nova exportação. O script inicia tarefas: monitore custos/cotas.
3. `python src/gee/monitor_and_process_batches.py` consulta/baixa os lotes e, quando todos estiverem concluídos, consolida censo, quadro, cotas e alocação. Reexecute o monitor conforme o estado; não é um daemon. O manifesto final evita repetir os splitters ad hoc e o processador monolítico 19. CSVs finais originais estão preservados para comparação.
4. `python src/gee/14_regenerate_master_sample.py` gera amostra 40k e subset 20k, coordenadas, área de pixel e pesos. Para reproduzir os resultados congelados, a opção preferível é reutilizar o CSV original; um novo sorteio remoto pode não gerar as mesmas coordenadas apesar da seed.
5. `python src/gee/11_extract_analytical_dataset.py` inicializa as variáveis anuais canônicas, MB histórica e distâncias. A série mensal desta etapa é intermediária RAW; não usar seus S/JSD como resultados finais.
6. `python src/gee/12_extract_harmonized_bilinear_monthly.py` corrige a extração mensal bilinear e atualiza os quatro indicadores temporais no anual. **Esta etapa é obrigatória antes da análise final.** Os checkpoints são por fatia; limpe ou separe checkpoints de outras construções apenas no ambiente de reexecução devidamente identificado.
7. Execute a análise 02→06 como descrito acima. Auditorias 16/17/20 podem ser usadas em cópia separada para conferir domínio, partição e paginação. Elas consomem GEE e podem gravar CSVs próprios.

Nenhuma dessas consultas, exportações, amostragem ou inferência foi refeita nesta organização. Disponibilidade pública dos assets foi verificada na documentação dos provedores; acesso efetivo ao GEE por outra conta não foi testado. O resultado depende do estado dos catálogos e do mecanismo de avaliação do serviço, não apenas do clone.

## 4. Manuscrito e recuperação histórica

O DOCX final já é a fonte editável definitiva; o PDF preservado é a entrega publicada no repositório, e o Markdown é derivado para leitura. Não é necessário reconstruí-lo a partir de protótipos.

```powershell
python scripts/export_manuscript.py --output-dir .release-work/paper-export --soffice 'C:\Program Files\LibreOffice\program\soffice.exe'
```

Isso exporta uma nova cópia PDF; não garante hash/layout idêntico ao congelado. Instale Times New Roman e confira as cinco páginas após qualquer alteração autoral. Os scripts editoriais, fontes predecessoras necessárias e evidências QA estão nos ZIPs de procedência; antigos caminhos Codex não são uma dependência do leitor nem da exportação portátil.

Para abrir um artefato histórico, use `python -m zipfile -l docs/provenance/historical_evidence.zip` e extraia em um diretório separado. A estrutura original é mantida dentro dos ZIPs. Não extraia sobre os arquivos finais. Os hashes por membro estão no manifesto de preservação. Procedência histórica está distinguida de pipeline recomendado.
