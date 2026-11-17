# Fase 0 — Fundação

- **Status:** não iniciada
- **Depende de:** nada
- **Bloqueia:** todas as fases

## Objetivo

Ter um repositório executável, testável e configurável, com os dois processos
(admin e viewer) subindo, banco criado e health check funcionando — ainda sem
Telegram e sem catálogo.

## Escopo

- `pyproject.toml` com Python 3.13 e dependências iniciais.
- Ambiente `uv` e `uv.lock`.
- Application factory para `app_admin` e `app_viewer`.
- Configuração por variáveis de ambiente.
- Conexão SQLite com WAL e `busy_timeout`.
- Executor de migrations (mesmo que ainda sem migrations de domínio).
- Logging estruturado, sem segredos.
- Health check do processo e do banco.
- Estrutura de testes com pytest e banco temporário.
- Script de criação do primeiro admin (A8).
- Scripts de iniciar/parar no Windows.
- Verificação dos assets herdados (`src/static`, `config/mime_map.json`).
- Documentar os comandos reais no README.

## Fora de escopo

- Telethon e qualquer chamada ao Telegram.
- Tabelas de catálogo.
- Interface de navegação.
- ffmpeg.
- Túnel.

## Entregáveis

- [ ] `uv run python -m src.app_admin` sobe em `127.0.0.1:8081`.
- [ ] `uv run python -m src.app_viewer` sobe em `127.0.0.1:8080`.
- [ ] `GET /api/health` responde com estado da aplicação e do banco.
- [ ] Migrations aplicam do zero em banco vazio.
- [ ] Primeiro admin é criado por script local.
- [ ] Testes passam em ambiente limpo.
- [ ] `.env.example` cobre todas as variáveis usadas.
- [ ] `legacy/` não é importado por nenhum módulo.

## Checklist

- [ ] Criar `pyproject.toml`, `uv.lock` e estrutura `src/`.
- [ ] Implementar factories e blueprints de health.
- [ ] Implementar configuração e validação de ambiente.
- [ ] Implementar conexão SQLite e executor de migrations.
- [ ] Implementar logging.
- [ ] Implementar hash de senha e script de seed do admin.
- [ ] Configurar pytest e banco de teste.
- [ ] Criar scripts de operação.
- [ ] Atualizar README com comandos reais.
- [ ] Rodar `uv run pytest`, lint e typecheck (se adotados).

## Arquivos previstos

```text
pyproject.toml
uv.lock
src/app_admin.py
src/app_viewer.py
src/config/settings.py
src/db/connection.py
src/db/migrations.py
src/routes/web/health.py
src/services/auth/passwords.py
src/utils/logging.py
scripts/create_admin.py
scripts/start.ps1
scripts/stop.ps1
tests/conftest.py
tests/test_health.py
tests/test_migrations.py
```

## Testes

- Subir cada app e verificar health.
- Aplicar migrations em banco vazio e repetir (idempotência).
- Criar admin e autenticar com a senha criada.
- Verificar que o admin não sobe em interface externa.
- Verificar que nenhum segredo aparece no log.

## Critério de saída

A aplicação sobe em ambiente limpo, com banco criado, migrations aplicadas,
admin criado e health check respondendo. Os comandos estão documentados e os
testes passam sem depender de estado residual.

## Riscos

- Escolha de biblioteca de migrations: manter executor simples e SQL versionado.
- Fuso horário e datas: armazenar UTC e formatar na interface.
- Windows: caminhos e permissões de arquivo de sessão serão tratados na fase 2.
