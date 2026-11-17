# Fase 00 — Fundação

- **Status:** concluída
- **Início:** 2026-11-17
- **Conclusão:** 2026-11-17
- **Responsável:** agente

## Resumo

Repositório executável com os dois processos Flask, configuração por ambiente, SQLite em WAL, executor de migrations, logging em JSON, health check e criação do primeiro admin. Nenhum módulo importa `legacy/`.

## Entregue

- `pyproject.toml`, `uv.lock` e ambiente `uv` com Python 3.13;
- factories de `app_admin` e `app_viewer`;
- configuração validada por ambiente, com admin restrito a loopback;
- SQLite com WAL, `busy_timeout`, chaves estrangeiras e verificação de saúde;
- executor de migrations com ledger `schema_migrations` e transação por arquivo;
- logging estruturado em JSON, sem credenciais;
- hash de senha com Werkzeug e script de seed do primeiro admin;
- `GET /api/health` no admin e no viewer;
- testes com pytest e banco temporário;
- README com os comandos reais.

## Arquivos criados/alterados

```text
.env.example
README.md
pyproject.toml
uv.lock
migrations/0000_foundation.sql
scripts/__init__.py
scripts/create_admin.py
src/__init__.py
src/app_admin.py
src/app_factory.py
src/app_viewer.py
src/config/__init__.py
src/config/settings.py
src/db/__init__.py
src/db/connection.py
src/db/migrations.py
src/repositories/__init__.py
src/repositories/users.py
src/routes/__init__.py
src/routes/api/__init__.py
src/routes/api/health.py
src/services/__init__.py
src/services/auth/__init__.py
src/services/auth/passwords.py
src/services/auth/users.py
src/utils/__init__.py
src/utils/logging.py
tests/conftest.py
tests/test_assets.py
tests/test_auth.py
tests/test_health.py
tests/test_migrations.py
```

## Decisões tomadas na execução

- A fundação usa a migration `0000_foundation.sql` para `users` e `settings`, preservando `0001_catalog.sql` para a fase 1.
- A interface de health foi colocada em `src/routes/api/health.py` (a fase previa `src/routes/web/health.py`) para respeitar a separação entre blueprints web e API.
- `APP_ENV=production` exige segredos de sessão com pelo menos 32 caracteres; em desenvolvimento/teste, segredos ausentes são efêmeros e nunca versionados.
- Timeout de sessão: 30 minutos para o admin e 60 minutos para o viewer (`ADMIN_SESSION_TIMEOUT_MINUTES` e `SESSION_TIMEOUT_MINUTES`), o que fecha A15.
- O primeiro admin é criado por `python -m scripts.create_admin`, com senha digitada e confirmada na hora, o que fecha A8.
- Lint adotado com Ruff; typecheck estático não foi adotado nesta fase.

## Testes executados

| Comando | Resultado |
|---|---|
| `uv run pytest` | 25 passed |
| `uv run ruff check .` | all checks passed |
| execução manual dos dois processos + health check | admin e viewer responderam `status: ok` |
| `ADMIN_HOST=0.0.0.0` ao carregar o admin | `ConfigurationError` (bind recusado) |
| `uv run python -m scripts.create_admin --help` | ajuda exibida |

## Pendências

- A16 registrada em `docs/abertos/DECISOES.md`: o painel administrativo herdado não tem fase explícita de portabilidade, o que afeta quando `legacy/` pode ser removido.
- A8 e A15 foram removidas de `docs/abertos/DECISOES.md` por terem sido resolvidas nesta fase.

## Riscos observados

- O viewer em `0.0.0.0` só deve ser exposto com firewall/túnel na fase 9.
- O seed do primeiro admin é interativo; automação futura deve evitar senha em argumento de linha de comando.

## Próximo passo

- Iniciar a [Fase 1 — Modelo de dados e catálogo](../roadmap/fase-01-modelo-de-dados.md).
