# Regras técnicas

## Linguagem e ambiente

- Python 3.13, gerenciado por `uv`.
- Dependências fixadas em `uv.lock`.
- Identificadores de código em inglês; textos, mensagens e documentação em pt-BR.
- Tipos explícitos nas funções de serviço e repositório.
- Sem `print`; usar logging estruturado.

## Estrutura

```text
src/
  app_admin.py
  app_viewer.py
  config/
  routes/web/
  routes/api/
  services/
  repositories/
  templates/
  static/
```

- Rotas: validam entrada, chamam serviço, respondem. Sem regra de negócio.
- Serviços: decisões e orquestração. Sem SQL.
- Repositórios: SQL e mapeamento. Sem regra de negócio.
- Templates: apresentação. Sem decisão de autorização.
- `services/telegram/` é o único lugar que fala Telethon.
- `services/media/` é o único lugar que executa ffmpeg/ffprobe.
- `services/subtitles/` cuida de extração, matching e faixas.

## Banco

- SQLite em WAL, `busy_timeout` configurado.
- Migrations SQL versionadas em `migrations/`, aplicadas por executor próprio.
- Sem ORM.
- Consultas por ID; nunca por caminho do sistema.
- Toda escrita em transação curta.
- Nomes de tabelas e colunas em inglês, `snake_case`.

## Flask

- Application factory para cada processo.
- Blueprints separados para web e API.
- Configuração somente por ambiente.
- Erros de API em JSON com `message` e código HTTP correto.
- Nenhuma rota administrativa no `app_viewer`.
- Sessão com cookie `HttpOnly`, `SameSite=Lax`, `Secure` sob HTTPS.

## API

- IDs, não caminhos.
- Paginação em listagens grandes.
- Respostas de erro sem stack trace.
- Streaming com `Range`, `206`, `Accept-Ranges` e `Content-Length`.
- Download com `Content-Disposition` e nome sanitizado.
- Ações de escrita exigem CSRF ou cabeçalho verificado.

## Telegram

- Telethon encapsulado; nenhuma rota importa Telethon diretamente.
- Sessão e credenciais por ambiente.
- Retry com backoff para `FloodWait`.
- Nunca logar `api_hash`, sessão ou conteúdo de mensagem.
- `file_reference` resolvida na leitura, não tratada como permanente.
- Varredura idempotente.

## Mídia

- ffmpeg/ffprobe via `subprocess` com lista de argumentos, sem `shell=True`.
- Caminhos de cache derivados de hash.
- Um job por arquivo; lock para evitar duplicação.
- Erros de ffmpeg não vazam caminhos internos.
- Cache fora da pasta servida estaticamente.

## Frontend

- JavaScript em módulos, sem framework.
- `textContent` para dados do usuário; nunca `innerHTML` com dado não confiável.
- Chamadas à API centralizadas em um módulo `api.js`.
- Estado de carregamento, vazio e erro sempre tratados.
- Manter as classes CSS herdadas; novas classes com prefixo do componente.
- Acessibilidade: foco visível, `aria-label`, navegação por teclado.

## Operação

- Sem Docker.
- Execução local por `uv run`; inicialização automática fica fora do repositório.
- Health check separado para app, banco e Telegram.
- Backup do banco antes de migrations destrutivas.
- Nenhum segredo em arquivo versionado.
