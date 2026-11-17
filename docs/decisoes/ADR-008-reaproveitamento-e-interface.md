# ADR-008 — Reaproveitamento do visual e dos assets

## Status

Aceita.

## Contexto

O projeto anterior tem uma interface madura e adequada ao uso: tema escuro, tipografia Inter, breadcrumb, grid de cartões, ícones por tipo, modal de preview, tela de login e painel administrativo. Reescrever a interface seria desperdício e perderia a identidade já validada.

## Decisão

- Copiar para o novo repositório, como base ativa:
  - `src/static/css/style.css`, `login.css`, `admin.css`;
  - `src/static/icons/`;
  - `config/mime_map.json`;
  - Highlight.js e tema Tokyo Night em `src/static/.../vendor/`.
- Copiar para `legacy/`, como **referência de portabilidade**, sem uso em runtime:
  - templates HTML;
  - `app.js`, `login.js`, `admin.js`;
  - módulos Python do legado;
  - documentação antiga.
- Portar, não copiar cegamente:
  - a API passa de caminho para ID;
  - o upload deixa de ser para disco e vira orientação;
  - o login ganha rate limit, timeout e CSRF;
  - o painel administrativo ganha autenticação.
- Manter a licença MIT e o crédito ao autor original.

## Consequências

- A fase 3 começa com HTML/CSS prontos, reduzindo esforço visual.
- O JavaScript precisa ser reescrito para a nova API.
- `legacy/` não é importado; serve para consulta e histórico.
- A documentação antiga não é fonte de verdade; correções estão em [`../arquitetura/REAPROVEITAMENTO.md`](../arquitetura/REAPROVEITAMENTO.md).

## Relacionados

- [`../arquitetura/REAPROVEITAMENTO.md`](../arquitetura/REAPROVEITAMENTO.md)
- [`../arquitetura/INTERFACE.md`](../arquitetura/INTERFACE.md)
- [`../roadmap/fase-03-navegacao-e-listagem.md`](../roadmap/fase-03-navegacao-e-listagem.md)
