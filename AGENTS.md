# AGENTS.md

Instruções para agentes de código que trabalham neste repositório.

## Papel do agente

Implementar **uma fase por vez** do [`docs/ROADMAP.md`](docs/ROADMAP.md), seguindo
as decisões registradas em [`docs/decisoes/`](docs/decisoes/INDICE.md). O agente
não define escopo nem arquitetura: isso está na documentação.

## Ordem de leitura

1. Este arquivo.
2. [`docs/INDEX.md`](docs/INDEX.md) — escolha o caminho pela tarefa.
3. [`docs/visao-geral.md`](docs/visao-geral.md) — apenas na primeira interação.
4. [`docs/roadmap/fase-XX.md`](docs/roadmap/) — **somente a fase atual**.
5. [`docs/rules/`](docs/rules/) — apenas a regra relevante à tarefa.
6. [`docs/arquitetura/`](docs/arquitetura/) — apenas o arquivo do assunto.

Não leia o roadmap inteiro nem todos os ADRs. O `INDEX.md` existe para evitar
isso.

## Regras rígidas

- Documentação em **pt-BR**; identificadores de código em **inglês**.
- A documentação é a fonte única. Se o código precisar divergir, pare e registre
  a divergência em [`docs/abertos/DECISOES.md`](docs/abertos/DECISOES.md).
- Não implemente funcionalidade fora da fase atual.
- Não crie compartilhamento público por link.
- Não automatize uploads em massa nem operações de escrita no Telegram sem
  previsão explícita na fase.
- Segredos apenas em variáveis de ambiente; nunca no repositório, no banco ou
  nos logs.
- O processo de administração escuta apenas em `127.0.0.1`.
- Autorização é aplicada no servidor, em todas as rotas.
- O usuário nunca escolhe um caminho real do sistema operacional: a árvore é
  virtual, definida no catálogo.
- Não adicione Docker, fila de jobs, multi-tenant ou criptografia client-side
  sem uma decisão registrada.

## Fluxo de trabalho

1. Abra a fase atual em `docs/roadmap/`.
2. Leia as decisões e regras citadas por ela.
3. Implemente apenas os entregáveis listados.
4. Rode os testes definidos na fase.
5. Atualize `docs/registros/fase-XX.md` com o que foi feito.
6. Troque **uma linha** na tabela de status de `docs/ROADMAP.md`.
7. Se surgir decisão nova, crie um ADR; se for pendência, registre em
   `docs/abertos/DECISOES.md`.

## Orçamento de contexto

- `AGENTS.md` e `INDEX.md`: leitura obrigatória e curta.
- Cada arquivo de documentação deve caber em ~3k tokens.
- O `ROADMAP.md` é índice: se ele crescer, o detalhe vazou para o lugar errado.
- O registro de execução mora em `docs/registros/` e nunca contamina o plano.

## Atualizações obrigatórias ao concluir uma fase

- [ ] Testes da fase passando.
- [ ] Critério de saída da fase atendido.
- [ ] `docs/registros/fase-XX.md` preenchido.
- [ ] Linha da fase atualizada em `docs/ROADMAP.md`.
- [ ] Pendências novas em `docs/abertos/DECISOES.md`.
- [ ] Nenhum segredo adicionado ao repositório.

## Proibições

- Implementar antes de a fase correspondente estar detalhada.
- Colocar regra de negócio na camada de interface.
- Expor o processo de administração pelo túnel.
- Baixar o acervo inteiro para "indexar" o canal.
- Apagar mensagens do Telegram fora do fluxo de esvaziar a lixeira.
- Usar `file_id` como verdade permanente: a referência precisa ser resolvida a
  partir da mensagem.
- Registrar tokens, sessões do Telethon ou credenciais em arquivos versionados.

## Estado atual

Especificação em andamento. Nenhuma fase iniciada. Consulte
[`docs/ROADMAP.md`](docs/ROADMAP.md) para a fase atual.
