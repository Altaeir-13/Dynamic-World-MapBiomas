# Configurações

`release.yaml` reconcilia o estado final corrigido: suporte 5 km, 182 fatias amostradas, 410 subestratos, 30 km de bloco, H4 por quartis separados e definições mensais finais. `release_sources.json` lista os módulos GEE da seleção pública usada pela verificação de sintaxe.

`experiment.yaml` e `sampling_manifest.yaml` permanecem byte a byte como snapshots preexistentes. O primeiro ainda declara estado de protótipo e bloco a determinar; o segundo é manifesto 3B e precede parte da correção canônica/mensal. Não os trate como descrição completa da versão final. O manifesto inválido foi arquivado como evidência.

As configurações documentam o experimento. Os scripts antigos usam constantes próprias e não leem universalmente estes YAMLs. Apenas `EE_PROJECT` foi parametrizado para acesso de outro usuário; escolhas científicas não foram modificadas.
