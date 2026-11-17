# Registros de execução

Este diretório guarda o **histórico do que foi feito** em cada fase. É separado
do roadmap de propósito: o plano é estável, o registro cresce.

## Regras

- Um arquivo por fase: `fase-00.md`, `fase-01.md` etc.
- Somente **acrescentar** ao final; não reescrever o passado.
- O registro não substitui o checklist da fase nem o ADR.
- O `docs/ROADMAP.md` recebe apenas uma linha de status, não o detalhe.
- Use [`_TEMPLATE.md`](_TEMPLATE.md) como ponto de partida.
- Datas no formato `AAAA-MM-DD`.
- Não registre segredos, tokens ou conteúdo de arquivos.

## O que registrar

- resumo do que foi entregue;
- arquivos criados/alterados;
- decisões tomadas durante a execução;
- testes executados e resultado;
- pendências e riscos;
- próximo passo.

## O que não registrar

- checklist completo copiado da fase;
- logs extensos;
- credenciais;
- conversas;
- código-fonte.

## Quando criar

- Ao iniciar a fase, crie o arquivo com status `em andamento`.
- Ao concluir, atualize o status e preencha o resultado.
- Se a fase for bloqueada, registre o motivo e a pendência.
