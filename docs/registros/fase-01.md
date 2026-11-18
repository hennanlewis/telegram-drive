# Fase 01 — Modelo de dados e catálogo

- **Status:** concluída
- **Início:** 2026-11-18
- **Conclusão:** 2026-11-18
- **Responsável:** agente

## Resumo

Catálogo local completo e funcional sem Telegram: schema SQLite, migrations, árvore virtual com raiz e Inbox, caminhos por CTE recursiva, manifesto `FD1`, serviços de pastas e arquivos, lixeira, duplicados por hash e auditoria. As regras são exercitadas por testes de serviço e por testes que atacam as constraints diretamente no banco.

## Entregue

- migration `0001_catalog.sql` com `folders`, `files`, `telegram_refs`, `subtitles`, `favorites`, `activity` e `scan_state`;
- criação da raiz `Raiz` e do Inbox `Para organizar`, com IDs em `settings`;
- unicidade de nomes por pasta no banco, inclusive com acentos e formas Unicode diferentes;
- índice parcial que impede dois arquivos ativos com o mesmo nome e versão na mesma pasta, liberando o nome quando o original vai para a lixeira;
- raiz única garantida por índice parcial;
- consulta recursiva de linhagem, breadcrumb e caminho virtual;
- manifesto `FD1` com serialização, parsing estrito e parsing tolerante para ingestão;
- serviços de criar, listar, renomear, mover e excluir pasta vazia;
- serviços de criar, renomear, mover, colocar na lixeira, restaurar e detectar duplicados de arquivo;
- invalidação de `manifest_synced_at` em renomeações e movimentações;
- auditoria de ações de catálogo;
- testes de schema, serviços, caminhos e manifesto.

## Arquivos criados/alterados

```text
migrations/0001_catalog.sql
src/db/connection.py
src/db/schema.py
src/repositories/settings.py
src/repositories/folders.py
src/repositories/files.py
src/repositories/activity.py
src/services/catalog/__init__.py
src/services/catalog/errors.py
src/services/catalog/paths.py
src/services/catalog/manifest.py
src/services/catalog/folders.py
src/services/catalog/files.py
src/utils/time.py
tests/test_migrations.py
tests/db/test_catalog_schema.py
tests/services/test_catalog.py
tests/services/test_manifest.py
tests/services/test_paths.py
docs/decisoes/ADR-009-unicidade-de-nomes-unicode.md
```

## Decisões tomadas na execução

- `name_key` (NFC + casefold) foi adotado para unicidade de nomes, porque `COLLATE NOCASE` no SQLite só trata ASCII. Registrado em [ADR-009](../decisoes/ADR-009-unicidade-de-nomes-unicode.md).
- A raiz e o Inbox são protegidos de forma permanente, inclusive quando o Inbox está vazio. A documentação foi ajustada para refletir a proteção permanente, necessária para manter estável a configuração `inbox_folder_id`.
- Arquivos na lixeira mantêm `folder_id` e guardam `trashed_from_folder_id` e `trashed_at`; o índice de nome só vale para itens fora da lixeira.
- A restauração usa a pasta de origem e recorre à raiz apenas se ela não existir; com as constraints atuais, a origem não pode ser apagada enquanto referencia o arquivo.
- `activity` recebeu `folder_id` e `result` para auditar operações de pasta e distinguir sucesso de erro, sem guardar conteúdo de arquivo.
- `telegram_refs` guarda apenas coordenadas e metadados; `file_reference` continua resolvida na leitura e não é armazenada como verdade.
- `activity` não usa a ação `version` nesta fase, porque o versionamento completo está adiado.

## Testes executados

| Comando | Resultado |
|---|---|
| `uv run pytest` | 117 passed |
| `uv run ruff check .` | all checks passed |
| migration do zero e reaplicação | `0000_foundation`, `0001_catalog`; segunda execução vazia |
| `PRAGMA integrity_check` e `PRAGMA foreign_key_check` no banco migrado | `ok` e sem violações |

Cobertura relevante:

- nomes duplicados por caixa e acento falham na mesma pasta e passam em pastas diferentes;
- raiz única, MIME, SHA-256, versão e referência de mensagem validados pelo banco;
- pasta não pode ser movida para si mesma nem para descendente;
- pasta com conteúdo não pode ser excluída;
- raiz e Inbox não podem ser renomeados, movidos ou excluídos;
- lixeira esconde o arquivo da listagem, preserva a origem e restaura no lugar;
- manifesto aceita ida e volta, campos opcionais e chaves desconhecidas; entradas inválidas viram `None` no parser tolerante;
- manifesto respeita o limite de 1024 caracteres da legenda.

## Pendências

- A16 permanece aberta em [`docs/abertos/DECISOES.md`](../abertos/DECISOES.md): o destino do painel administrativo herdado será decidido na fase 2.
- A transição para `missing` e o esvaziamento da lixeira pertencem às fases de varredura e organização; nesta fase existem apenas o estado e os campos.

## Riscos observados

- A restauração pode falhar por conflito de nome; o serviço devolve `NameConflictError` e mantém o item na lixeira.
- O caminho e o breadcrumb usam CTE recursiva; a profundidade real esperada é pequena, mas deve ser medida na navegação.
- Caminhos longos podem consumir o limite do manifesto; a serialização falha com `ManifestError` e o arquivo deve ser tratado como inválido na ingestão.

## Próximo passo

- Iniciar a [Fase 2 — Integração com o Telegram](../roadmap/fase-02-integracao-telegram.md).
