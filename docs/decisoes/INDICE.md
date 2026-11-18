# Índice de decisões

| ID | Decisão | ADR | Status |
|---|---|---|---|
| D1 | Acesso ao Telegram via MTProto com conta dedicada | [ADR-001](ADR-001-acesso-ao-telegram.md) | aceita |
| D2 | Single-user no MVP | [ADR-002](ADR-002-escopo-e-usuarios.md) | aceita |
| D3 | Catálogo local é a fonte da verdade; legenda é manifesto | [ADR-003](ADR-003-catalogo-e-manifesto.md) | aceita |
| D4 | Árvore virtual no banco e canal privado único | [ADR-003](ADR-003-catalogo-e-manifesto.md) | aceita |
| D5 | Streaming por proxy com cache e `Range` | [ADR-005](ADR-005-streaming-e-midia.md) | aceita |
| D6 | Flask + SQLite, dois processos | [ADR-006](ADR-006-stack-e-execucao.md) | aceita |
| D7 | Admin em localhost; viewer exposto por túnel | [ADR-006](ADR-006-stack-e-execucao.md) | aceita |
| D8 | Operações síncronas com retry; sem fila | [ADR-006](ADR-006-stack-e-execucao.md) | aceita |
| D9 | Sem Docker; `uv` + serviço local | [ADR-006](ADR-006-stack-e-execucao.md) | aceita |
| D10 | Escopo do MVP | [ADR-002](ADR-002-escopo-e-usuarios.md) | aceita |
| D11 | Upload manual pelo app oficial; app organiza | [ADR-001](ADR-001-acesso-ao-telegram.md) | aceita |
| D12 | Sem divisão de arquivos em partes no MVP | [ADR-001](ADR-001-acesso-ao-telegram.md) | aceita |
| D13 | Versionamento adiado; aviso de duplicado no MVP | [ADR-004](ADR-004-organizacao-e-lixeira.md) | aceita |
| D14 | Favoritos e painel de metadados adiados | [ADR-004](ADR-004-organizacao-e-lixeira.md) | aceita |
| D15 | Túnel: Cloudflared ou Tailscale | [ADR-007](ADR-007-exposicao-e-rede.md) | adiada para a fase 9 |
| D16 | Pipeline de mídia para MKV e legendas | [ADR-005](ADR-005-streaming-e-midia.md) | aceita |
| D17 | Manifesto na legenda do arquivo | [ADR-003](ADR-003-catalogo-e-manifesto.md) | aceita |
| D18 | Legendas no player: embutidas e avulsas | [ADR-005](ADR-005-streaming-e-midia.md) | aceita |
| D19 | Reaproveitar o visual e os assets do projeto anterior | [ADR-008](ADR-008-reaproveitamento-e-interface.md) | aceita |
| D20 | Unicidade de nomes com Unicode via `name_key` (NFC + casefold) | [ADR-009](ADR-009-unicidade-de-nomes-unicode.md) | aceita |

## Como ler

- **Aceita:** vale para a implementação; mudanças exigem novo ADR.
- **Adiada:** decisão consciente de não decidir agora; a fase indicada é a última responsável por fechá-la.
- **Em aberto:** ver [`../abertos/DECISOES.md`](../abertos/DECISOES.md).

## Decisões que não têm ADR próprio

Itens operacionais pequenos (tamanho de cache, limite de texto, retenção de backup) estão em [`../abertos/DECISOES.md`](../abertos/DECISOES.md) e serão fechados na fase correspondente.
