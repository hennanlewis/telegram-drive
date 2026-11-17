# ADR-006 — Stack, dois processos e execução

## Status

Aceita.

## Contexto

O projeto anterior já usa Flask, SQLite e uma separação entre administração e
explorer que se mostrou necessária por causa de túneis. O novo projeto precisa de
streaming, cache e chamadas ao Telegram, mas não de uma infraestrutura pesada.

## Decisão

- **Python 3.13** com **Flask**.
- **SQLite** em modo WAL, com migrations SQL versionadas e sem ORM.
- **Dois processos Flask**:
  - `app_admin` em `127.0.0.1:8081`;
  - `app_viewer` em `127.0.0.1:8080`.
- Sessões e segredos distintos por processo.
- Operações **síncronas com retry**; sem fila de jobs no MVP.
- **Sem Docker**; execução com `uv`, ambiente virtual e serviço local do Windows.
- **Sem ORM** e sem framework frontend; templates Jinja + JavaScript.
- Testes com **pytest** e banco temporário.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| FastAPI | Flask já atende; o legado e o visual são Flask/Jinja |
| PostgreSQL | SQLite cobre single-user e simplifica backup |
| ORM | SQL explícito é suficiente e mais direto para consultas recursivas |
| Fila (Celery/RQ) | Complexidade operacional sem necessidade no volume previsto |
| Docker | Custo de camada no Windows, sem ganho para uma máquina pessoal |
| Next.js/React | Reescreveria o visual que se quer reaproveitar |

## Consequências

- O deploy é simples: dois processos e um banco.
- A concorrência de escrita é limitada; WAL e transações curtas resolvem.
- Operações longas (remux, download) ocupam uma requisição; o retry e o cache
  mitigam.
- Sem Docker, a reprodutibilidade depende de `uv.lock` e de um script de
  instalação bem documentado.
- O frontend permanece simples, mas exige disciplina para não virar um arquivo
  monolítico.

## Relacionados

- [`../arquitetura/VISAO.md`](../arquitetura/VISAO.md)
- [`../arquitetura/SEGURANCA.md`](../arquitetura/SEGURANCA.md)
- [`../rules/tecnicas.md`](../rules/tecnicas.md)
