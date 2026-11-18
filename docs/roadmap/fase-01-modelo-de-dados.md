# Fase 1 — Modelo de dados e catálogo

- **Status:** concluída
- **Depende de:** fase 0

## Objetivo

Criar o schema do catálogo, as migrations e as regras puras de pastas, arquivos, manifesto e lixeira — sem Telegram e sem interface.

## Escopo

- Tabelas: `users`, `settings`, `folders`, `files`, `telegram_refs`, `subtitles`, `favorites`, `activity`, `scan_state`.
- Constraints e índices.
- Criação da raiz e do Inbox.
- Consulta recursiva de caminho e breadcrumb.
- Serialização e parsing do manifesto `FD1`.
- Serviços de catálogo: criar pasta, renomear, mover, listar, excluir vazio.
- Estados `active`, `trashed`, `missing`; campos de lixeira.
- Hash e campos de duplicado/versão (sem fluxo de UI).
- Auditoria básica.
- Testes de repositório e de serviço.

## Fora de escopo

- Varredura do Telegram.
- UI.
- Pipeline de mídia.
- Fluxo completo de duplicados.

## Entregáveis

- [x] Migrations criam todas as tabelas do zero.
- [x] Unicidade de nome por pasta é garantida pelo banco.
- [x] Caminho e breadcrumb são calculados corretamente.
- [x] Manifesto serializa e parseia com teste de ida e volta.
- [x] Manifesto inválido não derruba a aplicação.
- [x] Raiz e Inbox existem após a migration inicial.
- [x] Mover pasta para descendente é bloqueado.
- [x] Excluir pasta com conteúdo é bloqueado.
- [x] Lixeira guarda a pasta de origem.

## Checklist

- [x] Escrever migrations SQL.
- [x] Implementar repositórios.
- [x] Implementar serviços de catálogo.
- [x] Implementar manifesto.
- [x] Implementar auditoria.
- [x] Criar fixtures de teste.
- [x] Testar constraints diretamente no banco.

## Arquivos previstos

```text
migrations/0001_catalog.sql
src/db/schema.py
src/repositories/settings.py
src/repositories/folders.py
src/repositories/files.py
src/repositories/activity.py
src/services/catalog/errors.py
src/services/catalog/folders.py
src/services/catalog/files.py
src/services/catalog/manifest.py
src/services/catalog/paths.py
src/utils/time.py
tests/test_migrations.py
tests/db/test_catalog_schema.py
tests/services/test_catalog.py
tests/services/test_manifest.py
tests/services/test_paths.py
```

## Testes

- Migrations do zero e reaplicação.
- Nome duplicado na mesma pasta falha.
- Caminho de pasta aninhada.
- Mover pasta para dentro de si mesma falha.
- Excluir pasta não vazia falha.
- Manifesto com campos faltando ou inválidos.
- Manifesto com caminho e nome corretos.
- Estado da lixeira e restauração no nível de serviço.

## Critério de saída

O catálogo funciona sem Telegram: é possível criar, listar, mover, renomear, colocar na lixeira e restaurar por testes de serviço. O schema está completo e as constraints são garantidas pelo banco.

## Riscos

- SQLite e `COLLATE NOCASE`: mitigado por `name_key` (NFC + casefold) e testes com acentos e formas Unicode, conforme [ADR-009](../decisoes/ADR-009-unicidade-de-nomes-unicode.md).
- Caminho recursivo pode ficar caro; medir com profundidade realista.
- Manifesto de 1024 caracteres: validado com caminhos longos nos testes.
