# Arquitetura — dados

## Banco

- **SQLite** em modo **WAL**, um arquivo local.
- Acesso por SQL explícito, sem ORM.
- Migrations SQL versionadas em `migrations/`, aplicadas por um executor simples e idempotente.
- Testes usam banco temporário criado do zero.
- O banco é a fonte da verdade do catálogo; a legenda é o manifesto portátil.

## Modelo conceitual

### `users`

Usuários do visualizador e da administração.

- `id`, `username` (único), `password_hash`, `role`, `active`, `created_at`.
- Papéis: `admin` e `viewer`. O MVP é single-user, mas o campo existe.

### `settings`

Configuração persistida que não é segredo.

- `key` (PK), `value`, `updated_at`.
- Exemplos: `channel_id`, `inbox_folder_id`, `manifest_version`.

### `folders`

Árvore virtual.

- `id`, `parent_id` (nulo na raiz), `name`, `created_at`, `updated_at`.
- Único por `(parent_id, name)`, sem diferenciar maiúsculas/minúsculas.
- O caminho é calculado por CTE recursiva; não é armazenado como verdade.
- Não existe pasta física correspondente no disco.

### `files`

Arquivo lógico.

- `id`, `folder_id`, `name`, `mime`, `size_bytes`, `sha256`.
- `status`: `active`, `trashed`, `missing`.
- `trashed_from_folder_id`, `trashed_at`.
- `version`, `is_current` (versionamento adiado; campos já previstos).
- `created_at`, `updated_at`, `manifest_synced_at`.
- Único por `(folder_id, name, version)`.

### `telegram_refs`

Onde o arquivo está no Telegram.

- `id`, `file_id`, `chat_id`, `message_id`, `document_id`, `access_hash`.
- `size_bytes`, `duration_seconds`, `width`, `height`, `mime`.
- `part_index`, `part_count` (1/1 no MVP; reservado para divisão futura).
- `file_reference` não é armazenado como verdade; é resolvido na leitura.
- Um arquivo pode ter mais de uma referência no futuro; no MVP, uma.

### `subtitles`

Faixas de legenda conhecidas.

- `id`, `file_id`, `source` (`embedded` ou `sidecar`), `language`, `format` (`srt`, `ass`, `vtt`), `label`.
- `telegram_message_id` para legenda avulsa; nulo para embutida.
- `cache_path` para o arquivo extraído.

### `favorites`

- `file_id` (PK), `created_at`.
- Puramente local; não altera o Telegram.

### `activity`

Auditoria simples de operações relevantes.

- `id`, `action`, `file_id`, `detail`, `created_at`.
- Ações: `ingest`, `move`, `rename`, `trash`, `restore`, `delete`, `manifest`, `duplicate`.
- Não guarda conteúdo de arquivo nem segredo.

### `scan_state`

- `id` (sempre 1), `last_message_id`, `last_scan_at`, `last_error`.

## Manifesto `FD1`

Gravado na **legenda da mensagem**, dentro do limite de 1024 caracteres.

Formato: uma linha `FD1`, seguida de pares `chave=valor`, um por linha.

```text
FD1
i=3f2a9c1e-8d4b-4f0a-9c2e-1a7b6d5e4c30
p=Filmes/Severance/S01
n=S01E01.mkv
m=video/x-matroska
s=612345678
h=9f2c1a...64 caracteres...
t=2026-11-16T20:00:00Z
v=1
```

| Chave | Significado |
|---|---|
| `i` | Identificador lógico do arquivo (UUID) |
| `p` | Pasta virtual (sem barra inicial) |
| `n` | Nome do arquivo |
| `m` | MIME |
| `s` | Tamanho em bytes |
| `h` | SHA-256 |
| `t` | Data de organização (ISO 8601, UTC) |
| `v` | Versão (padrão 1) |
| `part` | Opcional: `i/n` quando houver divisão |
| `d` | Opcional: duração em segundos |

Regras:

- O manifesto é escrito pelo app ao organizar o arquivo.
- Arquivo sem manifesto vai para o Inbox.
- Chaves desconhecidas são preservadas? **Não.** O app reescreve o manifesto completo ao atualizar; extensões futuras exigem nova versão (`FD2`).
- O parser é tolerante: linhas inválidas são ignoradas e o arquivo entra no Inbox com aviso.
- O manifesto não substitui o banco: é redundância para reconstrução.

## Caminhos e nomes

- Caminho virtual é a concatenação de nomes de pastas a partir da raiz.
- Nomes são exibidos como vieram do Telegram, mas normalizados para armazenar (trim, sem caracteres de controle).
- Colisão de nome na mesma pasta: o app pergunta renomear, substituir ou criar versão; nunca sobrescreve silenciosamente.
- O usuário nunca informa caminho absoluto do sistema operacional.
- Não há travessia de diretório: toda resolução é por ID de pasta/arquivo.

## Inbox

- Pasta virtual reservada, criada na primeira execução.
- Destino de todo arquivo descoberto sem manifesto.
- Não pode ser excluída nem renomeada enquanto contiver arquivos.
- Organizar um arquivo remove-o do Inbox.

## Lixeira

- Excluir altera `status` para `trashed` e grava `trashed_from_folder_id`.
- O arquivo e a mensagem continuam intactos.
- Restaurar volta para a pasta de origem; se ela não existe, recria ou usa a raiz.
- Esvaziar a lixeira:
  1. apaga as mensagens no Telegram;
  2. remove referências, legendas e favoritos;
  3. remove o registro do arquivo;
  4. registra a ação na auditoria.
- Falha ao apagar no Telegram mantém o registro em estado `trashed` com erro, para nova tentativa.

## Duplicados e versões

- Identidade de conteúdo: `sha256` + tamanho.
- Ao ingerir, se já existe arquivo ativo com o mesmo hash, marcar como **duplicado candidato** e pedir decisão:
  - manter os dois;
  - substituir o existente (o antigo vai para a lixeira);
  - criar nova versão.
- Versionamento completo (histórico navegável) é adiado; os campos `version` e `is_current` permitem implementá-lo sem migração destrutiva.

## Reconstrução do catálogo

1. Criar banco vazio e aplicar migrations.
2. Varrer o canal do início ao fim.
3. Para cada documento com manifesto válido: recriar pastas, arquivo e referência.
4. Para cada documento sem manifesto: criar no Inbox.
5. Ao final, comparar contagens e listar divergências.

A reconstrução não baixa bytes e não escreve no Telegram.

## Concorrência

- WAL permite leitura simultânea à escrita.
- Escritas são curtas e transacionais.
- A varredura e a organização podem competir; usar transação por arquivo e `busy_timeout`.
- O pipeline de mídia não escreve no catálogo durante o streaming, exceto para atualizar cache/estado.

## Backup

- Backup do arquivo SQLite com a API de backup ou cópia consistente com WAL.
- Frequência e retenção definidas na fase 9.
- O backup do banco não inclui os bytes (que estão no Telegram).
- Teste de restauração é obrigatório no aceite.

## Índices previstos

- `folders(parent_id, name)`.
- `files(folder_id, name)`, `files(sha256)`, `files(status)`.
- `telegram_refs(file_id)`, `telegram_refs(chat_id, message_id)`.
- `subtitles(file_id)`.
- `activity(created_at)`.
