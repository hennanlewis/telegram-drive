# Arquivos e pastas

## Árvore virtual

- A raiz é única e não pode ser renomeada nem excluída.
- Pastas têm `id`, `parent_id` e `name`; o caminho é calculado, não armazenado
  como verdade.
- Nomes são únicos por pasta, sem diferenciar maiúsculas/minúsculas.
- O caminho exibido é `Raiz / Filmes / Série / Temporada`.
- A ordem padrão é: pastas primeiro, depois arquivos, ambos por nome ascendente.
- Não existe pasta física no computador correspondente à pasta virtual.

## Inbox

- Pasta reservada “Para organizar”.
- Recebe todo arquivo descoberto sem manifesto válido.
- Não pode ser renomeada nem excluída enquanto tiver conteúdo.
- Organizar um arquivo remove-o do Inbox.
- A interface mostra um contador de pendências.

## Criar pasta

- Nome obrigatório, sem `/`, `\`, caracteres de controle ou espaços nas pontas.
- Não pode duplicar um nome existente na mesma pasta.
- A pasta é criada apenas no catálogo; nenhuma mensagem é enviada ao Telegram.

## Renomear

- Renomear pasta ou arquivo é local.
- Para arquivo, a legenda é atualizada depois, de forma assíncrona ao fluxo do
  usuário (com estado de sincronização).
- Se a atualização da legenda falhar, o catálogo permanece correto e o item fica
  marcado como “manifesto pendente”.

## Mover

- Mover arquivo ou pasta atualiza `parent_id`.
- Mover uma pasta para dentro de si mesma ou de um descendente é proibido.
- Colisão de nome no destino: pedir renomear, substituir ou cancelar.
- Mover não altera bytes nem mensagens; no máximo atualiza o manifesto.

## Excluir pasta

- Só é permitido excluir pasta vazia.
- Se houver conteúdo, a interface oferece mover o conteúdo para a lixeira ou
  cancelar.
- Excluir pasta não apaga mensagens no Telegram.

## Estados

| Estado | Significado |
|---|---|
| `active` | visível na navegação |
| `trashed` | na lixeira; mensagem preservada |
| `missing` | mensagem não encontrada no Telegram |

`missing` é um aviso, não uma exclusão. O usuário decide o que fazer.

## API conceitual

- Navegação por `folder_id`, não por caminho.
- A resposta inclui `folder`, `breadcrumbs`, `items` e `inbox_count`.
- Cada item inclui `id`, `name`, `kind`, `icon`, `size`, `modified_at`,
  `status`, `in_trash`.
- Ações usam `file_id`/`folder_id` e corpo JSON.
- Nunca aceitar `path` absoluto ou relativo do cliente.

## Regras de exibição

- Arquivos `trashed` e `missing` não aparecem na navegação normal.
- `missing` aparece no painel de metadados e na lixeira, com aviso.
- O Inbox aparece sempre, mesmo vazio, para orientar o fluxo.
- Pastas vazias mostram estado vazio.
