# Ambiente para outro computador

Instale Git e Python. O ambiente científico local auditado usa **Python 3.14.5 em Windows**, registrado em `config/experiment.yaml` e metadados do ambiente. Use ambiente virtual novo; não copie `.venv`, que contém caminhos e binários específicos do computador.

```powershell
python --version
git --version
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe scripts/verify_release.py --data
```

As versões fixadas são as efetivamente instaladas no ambiente de pesquisa, não suposições de versões atuais. O lock completo registra também bibliotecas Jupyter/geemap e ferramentas que não são necessárias para ler os resultados. `requirements.txt` é a seleção direta mínima do pipeline científico preservado. Não substitua silenciosamente versões para afirmar reprodução idêntica; se uma versão estiver indisponível na sua plataforma/índice, registre a divergência. Consulte o relatório de validação da organização para o resultado efetivo do teste de instalação.

Dependências diretas: earthengine-api; numpy; pandas; scipy; statsmodels; matplotlib; pyarrow; pyproj; shapely; geopandas; requests; google-api-python-client; google-auth; PyYAML; xlrd (leitura do XLS IBGE). As versões e o snapshot completo estão nos dois arquivos de requisitos. A verificação sem `--data` dispensa bibliotecas externas. A análise não exige GPU, CUDA, Jupyter nem QGIS. Geopandas/pyproj e wheels compatíveis com Python/OS são necessários para a regeneração geográfica.

Para Linux/macOS, adapte o caminho de Python para `.venv/bin/python` e a variável de projeto para `export EE_PROJECT=seu-projeto`. A compatibilidade integral nesses sistemas não foi demonstrada.

## Earth Engine

Crie/habilite um projeto próprio no Google Cloud, associe acesso Earth Engine e valide permissões da conta. Configure no PowerShell `$env:EE_PROJECT='seu-projeto'`. Execute `.venv\Scripts\earthengine.exe authenticate`, depois o script 01. `.env.example` só documenta a variável; não é carregado automaticamente. Scripts preservados assumem o ID original quando a variável estiver ausente; ele pode não ser acessível a você.

Credenciais GEE/Google permanecem no mecanismo de autenticação do usuário, fora do repositório. O fluxo de exportação usa Drive e pode exigir consentimento adicional. Cotas e regras de acesso não são encapsuladas no lock de Python. O [guia oficial de autenticação](https://developers.google.com/earth-engine/guides/auth) deve ser consultado para os requisitos vigentes.

## Manuscrito

Para editar: Word ou LibreOffice; para o exportador portátil: LibreOffice e Times New Roman. O PDF congelado foi produzido por LibreOffice 26.2.6.3, conforme evidências editoriais. O script de exportação usa somente stdlib, mas exige `soffice` no PATH ou `--soffice`. Não depende de runtime Codex nem de plugin para o usuário final. Mudanças de fonte/editor precisam de inspeção visual; não alteram os resultados científicos por si só.
