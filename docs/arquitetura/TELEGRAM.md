# Arquitetura — Telegram

## Por que MTProto

O projeto precisa de arquivos de até 2 GB e de streaming. A API oficial de bots limita o download a ~20 MB e o upload a ~50 MB, o que inviabiliza vídeo. Por isso o acesso é feito por **MTProto**, com uma **conta dedicada**, usando Telethon. Bot não é usado no MVP.

| Recurso | Bot API | MTProto (conta) |
|---|---|---|
| Download | ~20 MB | 2 GB |
| Upload | ~50 MB | 2 GB (4 GB Premium) |
| Ler canal privado | só como admin | sim, como membro |
| Editar legenda própria | sim | sim |
| Streaming de vídeo | inviável | viável |

## Conta e credenciais

- Conta **dedicada** ao drive, distinta da conta pessoal.
- `api_id` e `api_hash` obtidos em `my.telegram.org` para essa conta.
- Sessão do Telethon em arquivo local (`TELEGRAM_SESSION_PATH`), **nunca** versionado.
- O arquivo de sessão equivale a uma senha: quem o tiver controla a conta.
- A conta é dona do canal privado usado como armazenamento.

## Canal

- **Um canal privado único**, sem tópicos.
- O canal não é público e não tem link de convite divulgado.
- A navegação não acontece dentro do Telegram: a interface é a web.
- A conta que faz os uploads manuais é a mesma usada pelo app. Isso permite editar as legendas próprias sem depender de permissões de terceiros.

### Por que não usar tópicos ou grupos

- Pastas do Telegram são recurso de cliente, não existem na API.
- Tópicos engessam renomear/mover e não substituem uma árvore virtual.
- Grupos têm mensagens de serviço e respostas, mas não são necessários.
- Um canal privado é o formato mais limpo para armazenamento.

## Modelo da mensagem

Cada arquivo é uma mensagem com documento. O catálogo guarda:

- `chat_id` e `message_id` — localização da mensagem;
- `document_id` e `access_hash` — identificação do documento;
- `file_reference` — **volátil**, não é verdade permanente;
- tamanho, duração, dimensões e MIME, quando disponíveis.

### Referências voláteis

`file_reference` pode expirar ou mudar. A regra é:

1. Guardar as coordenadas da mensagem.
2. Ao ler ou baixar, resolver a referência a partir da mensagem.
3. Se a referência falhar, refazer a consulta e atualizar o catálogo.
4. Se a mensagem não existir mais, marcar o arquivo como `missing` — **nunca apagar o registro automaticamente**.

O `file_id` da Bot API não é usado como identidade: ele é específico do bot e não serve para uma conta MTProto.

## Upload e escrita

- **Upload é manual**, pelo app oficial do Telegram. O app não automatiza envio de arquivos no MVP.
- O app **lê** o canal para descobrir uploads novos.
- O app **escreve** apenas:
  - a legenda/manifesto ao organizar;
  - a exclusão da mensagem ao esvaziar a lixeira;
  - a edição de legenda quando o manifesto precisa ser corrigido.
- Nenhuma dessas escritas acontece em lote ou em rajada.

### Risco de banimento

O risco não vem do volume armazenado, e sim do **comportamento**:

| Comportamento | Risco |
|---|---|
| Enviar manualmente pelo app oficial | muito baixo |
| Ler/listar/baixar pelo app | baixo |
| Editar legendas próprias com frequência humana | baixo |
| Upload automatizado em rajada | médio |
| Encaminhamento em massa ou spam | alto |
| Canal público para distribuir conteúdo | alto |

Doze episódios de 600 MB por semana (~7 GB/semana, ~31 GB/mês) não são um padrão de abuso. O que deve ser evitado é automação em massa, muitos envios por minuto e compartilhamento público.

## Compressão e formatos

- O Telegram **não reencoda no servidor**; ele armazena o que foi enviado.
- A compressão acontece no **cliente oficial**, quando o envio é feito como “vídeo”. Enviar como **arquivo** preserva os bytes originais.
- MKV enviado como vídeo pode ser convertido ou enviado como arquivo, dependendo da plataforma. Para garantir, envie como **arquivo**.
- Legendas embutidas só sobrevivem se o arquivo for enviado sem conversão.
- O player do Telegram não lê faixas embutidas; o nosso player lê.

Detalhes de reprodução em [`MIDIA.md`](MIDIA.md).

## Varredura do canal

Algoritmo conceitual:

1. Ler `last_message_id` do estado da varredura.
2. Iterar mensagens novas do canal, da mais antiga para a mais nova.
3. Ignorar mensagens sem documento.
4. Extrair coordenadas e metadados.
5. Se a legenda tem manifesto `FD1`, aplicar os dados declarados.
6. Se não tem, criar registro no **Inbox**.
7. Se o documento já existe no catálogo, atualizar a referência.
8. Gravar o novo `last_message_id` e a data da varredura.

Regras:

- A varredura não baixa conteúdo.
- A varredura é idempotente: rodar duas vezes não duplica arquivos.
- Mensagens apagadas fora do app são detectadas e marcadas como `missing`.
- A varredura pode ser manual (botão) ou periódica; a fase 8 define o gatilho.

## Rate limit e resiliência

- Erros `FloodWait` são tratados com espera e retry, nunca com novas tentativas imediatas.
- Downloads são serializados por padrão; paralelismo é otimização, não regra.
- Toda chamada tem timeout e log sem segredos.
- O app deve continuar navegável quando o Telegram estiver indisponível.

## Reconstrução

Se o banco for perdido:

1. Criar um banco vazio.
2. Varrer o canal inteiro.
3. Ler os manifestos das legendas e recriar a árvore.
4. Arquivos sem manifesto vão para o Inbox.
5. Nenhum byte é baixado nesse processo.

O manifesto é o que torna o catálogo descartável. Por isso ele é gravado assim que o arquivo é organizado.

## Segurança

- Credenciais e sessão apenas em variáveis de ambiente/arquivos ignorados.
- Logs nunca imprimem `api_hash`, sessão ou conteúdo de mensagens.
- O canal não é divulgado.
- O app não aceita caminho de arquivo do usuário; só identificadores do catálogo.
- Excluir mensagem é a única operação destrutiva e só ocorre no esvaziamento da lixeira.
