# ADR-001 — Acesso ao Telegram via MTProto e upload manual

## Status

Aceita.

## Contexto

O projeto precisa armazenar e reproduzir vídeos de até 2 GB. A Bot API limita o
download a ~20 MB e o upload a ~50 MB, o que inviabiliza o caso de uso. Também é
preciso ler um canal privado e editar as legendas dos próprios arquivos.

## Decisão

- Usar **MTProto** por meio do **Telethon**, com uma **conta dedicada**.
- Obter `api_id`/`api_hash` em `my.telegram.org`.
- Guardar a sessão em arquivo local, fora do Git.
- **Não automatizar uploads** no MVP: o envio é feito manualmente pelo app
  oficial do Telegram.
- O app **lê** o canal, **organiza** o catálogo, **grava a legenda** e **apaga
  mensagens** apenas ao esvaziar a lixeira.
- Não usar bot no MVP; um bot, se existir, será apenas para notificações.
- Não dividir arquivos em partes: o limite de 2 GB cobre o acervo previsto.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Bot API | Limites de 20/50 MB inviabilizam vídeo |
| Bot + MTProto | Acrescenta complexidade sem benefício no MVP |
| Upload automatizado pela conta | Aumenta a superfície de risco sem necessidade |
| Dividir arquivos em partes | Complexidade de seek e remontagem; só faz sentido acima de 2 GB |

## Consequências

- O fluxo de ingestão depende de o usuário enviar o arquivo pelo Telegram.
- A experiência de upload na interface web é de orientação, não de envio.
- A conta dedicada precisa ser protegida como credencial.
- Arquivos acima de 2 GB ficam fora do MVP (ver decisão adiada).
- O risco de banimento fica restrito a leitura e escritas leves.

## Relacionados

- [`../arquitetura/TELEGRAM.md`](../arquitetura/TELEGRAM.md)
- [`../decisoes/ADR-005-streaming-e-midia.md`](ADR-005-streaming-e-midia.md)
- [`../abertos/DECISOES.md`](../abertos/DECISOES.md)
