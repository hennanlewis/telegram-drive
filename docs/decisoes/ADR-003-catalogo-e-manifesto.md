# ADR-003 — Catálogo local, manifesto na legenda e canal único

## Status

Aceita.

## Contexto

O Telegram não tem pastas reais, não expõe uma árvore de diretórios e não é uma
interface adequada para navegação. Se o catálogo existir apenas no banco, a perda
do banco significa perder a organização. Se existir apenas na legenda, cada
operação vira uma escrita no Telegram e a navegação fica lenta.

## Decisão

- O **banco SQLite** é a fonte da verdade do catálogo: pastas, nomes, estados,
  referências e metadados.
- A **legenda da mensagem** carrega um manifesto `FD1` compacto, como backup
  portátil e mecanismo de reconstrução.
- O armazenamento é **um canal privado único**, sem tópicos.
- A árvore é **virtual**, definida no catálogo; não há pasta física.
- Arquivos sem manifesto entram no **Inbox**.
- O manifesto é gravado quando o arquivo é organizado; não a cada leitura.
- O `file_id` não é identidade permanente: as coordenadas da mensagem são a
  referência e a `file_reference` é resolvida na leitura.

## Formato do manifesto

```text
FD1
i=<uuid>
p=<pasta virtual>
n=<nome>
m=<mime>
s=<bytes>
h=<sha256>
t=<data ISO>
v=<versão>
```

Cabe em 1024 caracteres. O parser é tolerante: manifesto inválido leva o arquivo
para o Inbox, nunca o descarta.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Só banco | Perda do banco = perda da organização |
| Só legenda | Toda navegação dependeria de ler o canal |
| Pastas por tópicos | Não existe API de pastas; engessa mover/renomear |
| Mensagem-resposta com manifesto | Canal não tem resposta; exigiria grupo e pareamento |
| Múltiplos canais | Complexidade sem benefício para single-user |

## Consequências

- O catálogo pode ser reconstruído varrendo o canal e lendo legendas.
- Toda organização gera uma escrita leve no Telegram (legenda).
- O canal precisa ser privado e acessível pela conta dedicada.
- Arquivos enviados fora do app entram no Inbox, não se perdem.
- Se a legenda for editada manualmente e corrompida, o arquivo vai para o Inbox.

## Relacionados

- [`../arquitetura/DADOS.md`](../arquitetura/DADOS.md)
- [`../arquitetura/TELEGRAM.md`](../arquitetura/TELEGRAM.md)
- [`../domain/arquivos-e-pastas.md`](../domain/arquivos-e-pastas.md)
