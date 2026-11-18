# ADR-004 — Organização, lixeira e duplicados

## Status

Aceita.

## Contexto

O Telegram é append-only para o usuário: apagar é definitivo e não há lixeira nativa. Mover e renomear precisam existir sem tocar nos bytes. Arquivos repetidos podem surgir de uploads manuais.

## Decisão

### Organização

- Pastas, nomes e posição vivem apenas no catálogo.
- Mover e renomear são operações locais; a legenda é atualizada depois.
- Todo arquivo descoberto sem manifesto entra no **Inbox** (“Para organizar”).
- O Inbox não pode ser renomeado nem excluído; a proteção é permanente.

### Lixeira

- Excluir muda o estado para `trashed` e guarda `trashed_from_folder_id`.
- Restaurar volta ao caminho original; se a pasta não existe, recria ou usa a raiz.
- **Esvaziar a lixeira** é a única operação que apaga mensagens no Telegram.
- Falha ao apagar no Telegram mantém o item em `trashed` com erro, para nova tentativa.

### Duplicados

- Identidade por `sha256` + tamanho.
- Ao detectar duplicado, a interface oferece: manter os dois, substituir (o antigo vai para a lixeira) ou criar nova versão.
- Nunca sobrescrever silenciosamente.

### Versionamento

- Adiado. Os campos `version` e `is_current` existem para permitir a evolução.
- No MVP, “criar nova versão” gera um novo registro com o mesmo nome e `version + 1`, mantendo o anterior.
- Histórico navegável de versões fica para depois do MVP.

### Favoritos e metadados

- Favoritos são apenas uma tabela local; não tocam no Telegram.
- O painel de metadados é desejável, mas adiado; os dados já existem no catálogo.

## Consequências

- A maior parte das operações tem risco zero para a conta do Telegram.
- A lixeira protege contra erro humano.
- O catálogo pode ficar temporariamente divergente do Telegram se a exclusão falhar; a reconciliação resolve.
- Duplicados exigem decisão do usuário, não regra automática.

## Relacionados

- [`../domain/arquivos-e-pastas.md`](../domain/arquivos-e-pastas.md)
- [`../domain/lixeira-e-duplicados.md`](../domain/lixeira-e-duplicados.md)
- [`../arquitetura/DADOS.md`](../arquitetura/DADOS.md)
