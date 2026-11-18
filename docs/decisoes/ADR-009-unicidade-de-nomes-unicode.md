# ADR-009 — Unicidade de nomes com Unicode

## Status

Aceita.

## Contexto

Pastas e arquivos têm nomes únicos por pasta, sem diferenciar maiúsculas de minúsculas. No SQLite, `COLLATE NOCASE` só dobra maiúsculas ASCII; nomes com acento, como `Ação` e `AÇÃO`, continuariam distintos. O roadmap da fase 1 aponta esse risco explicitamente.

Comparar nomes diretamente com `lower()` também não resolve: o mesmo texto pode chegar em formas Unicode diferentes (NFC e NFD), com acentos combinados ou precompostos.

## Decisão

- Cada pasta e cada arquivo guarda um `name_key` interno.
- O `name_key` é calculado em Python com normalização **NFC** seguida de **casefold**.
- A unicidade é garantida por índices únicos sobre `name_key`:
  - pastas: `(COALESCE(parent_id, 0), name_key)`;
  - arquivos: `(folder_id, name_key, version)` apenas quando `status <> 'trashed'`;
  - raiz: índice parcial que permite uma única pasta com `parent_id IS NULL`.
- O nome exibido permanece em `name`, na forma normalizada NFC, preservando maiúsculas, minúsculas e acentos.
- `name_key` é detalhe interno do catálogo; não é exibido nem aceito como entrada de serviço.

## Consequências

- `Ação`, `ação`, `AÇÃO` e a forma decomposta colidem corretamente na mesma pasta.
- A validação não depende de extensões ou de collations específicas do SQLite.
- Toda escrita de pasta ou arquivo precisa calcular o `name_key`; por isso a regra fica nos serviços de catálogo, não na interface.
- Consultas por nome usam `name_key`; consultas de exibição continuam usando `name`.

## Relacionados

- [`../domain/arquivos-e-pastas.md`](../domain/arquivos-e-pastas.md)
- [`../arquitetura/DADOS.md`](../arquitetura/DADOS.md)
- [`../roadmap/fase-01-modelo-de-dados.md`](../roadmap/fase-01-modelo-de-dados.md)
