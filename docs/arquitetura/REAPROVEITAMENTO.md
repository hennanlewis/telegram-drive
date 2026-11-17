# Reaproveitamento do projeto anterior

Este documento registra o que veio do `file_explorer`, onde está e como deve ser
usado. O objetivo é preservar o visual e as boas decisões sem arrastar o modelo
de sistema de arquivos local.

## Matriz de reaproveitamento

| Item do legado | Destino no novo projeto | Situação | Observação |
|---|---|---|---|
| `config/mime_map.json` | `config/mime_map.json` | **usar como está** | Mapa de extensão → ícone e overrides de MIME |
| `src/static/icons/` | `src/static/icons/` | **usar como está** | Ícones de pasta, vídeo, áudio, PDF, texto etc. |
| `src/static/css/style.css` | `src/static/css/style.css` | **usar como base** | Tema escuro, header, grid, cards, modal |
| `src/static/css/login.css` | `src/static/css/login.css` | **usar como base** | Tela de login |
| `src/static/css/admin.css` | `src/static/css/admin.css` | **usar como base** | Painel administrativo |
| `highlight.min.js` + tema Tokyo Night | `src/static/js/vendor/`, `src/static/css/vendor/` | **usar como está** | Preview de texto/código |
| `templates/index.html` | `legacy/frontend/templates/index.html` | **portar** | Estrutura visual do explorer |
| `templates/login.html` | `legacy/frontend/templates/login.html` | **portar** | Estrutura visual do login |
| `templates/admin.html` | `legacy/frontend/templates/admin.html` | **portar** | Base do painel administrativo |
| `static/js/app.js` | `legacy/frontend/static/js/app.js` | **portar** | Lógica de breadcrumb, grid, modal e preview |
| `static/js/login.js` | `legacy/frontend/static/js/login.js` | **portar** | Fluxo de login |
| `static/js/admin.js` | `legacy/frontend/static/js/admin.js` | **portar** | Usuários e configuração |
| `services/mime_resolver.py` | `legacy/backend/services/` | **portar a ideia** | Ícone por extensão; sem depender do disco |
| `services/filesystem.py` | `legacy/backend/services/` | **descartar a listagem** | Substituído pelo catálogo |
| `utils/paths.py` | `legacy/backend/utils/` | **referência** | Defesa contra travessia de diretório |
| `utils/db.py` | `legacy/backend/utils/` | **descartar** | Novo schema e migrations |
| `app.py` (dois Flask apps) | `legacy/backend/app.py` | **reaproveitar o conceito** | Dois processos, portas distintas |
| `routes/api/explorer.py` | `legacy/backend/routes/api/` | **descartar a API** | Nova API por ID, não por caminho |
| `routes/web/pages.py` | `legacy/backend/routes/web/` | **portar o fluxo** | Login/logout e proteção de página |
| `routes/web/admin.py` | `legacy/backend/routes/web/` | **portar o fluxo** | Cadastro de usuários e configuração |
| `doc/ARCHITECTURE.md` | `legacy/reference/` | **referência** | Justificativa da separação de portas |
| `doc/DESCRIPTION.md` | `legacy/reference/` | **referência** | Funcionalidades e inspiração visual |
| `doc/SECURITY.md` | `legacy/reference/` | **referência com ressalvas** | Contém afirmações não implementadas |
| `LICENSE` (MIT) | `LICENSE` | **manter** | Crédito ao autor original |

## O que muda de verdade

### Modelo de dados

O legado resolve tudo por caminho (`/Documentos/Fotos`). O novo projeto resolve
por **ID de pasta e ID de arquivo**. Isso elimina travessia de diretório e
permite mover/renomear sem tocar no Telegram.

### Origem dos bytes

O legado lê o disco. O novo lê o Telegram via MTProto. A camada de listagem
passa a vir do catálogo, e a camada de leitura passa a resolver uma referência de
mensagem.

### Upload

No legado, o navegador envia o arquivo para o Flask. No novo, o upload é feito
manualmente pelo app oficial do Telegram; a interface apenas **orienta** e
**organiza**. O modal de upload do legado não é reaproveitado como fluxo real.

### Autenticação

O legado tem login por usuário/senha, mas sem rate limiting nem timeout. O novo
projeto mantém o modelo e **implementa** os controles que faltavam. O painel
administrativo deixa de depender só do localhost: ganha autenticação e continua
restrito ao loopback.

## O que o legado ensinou

1. **Separar administração de navegação** evita que um túnel transforme
   requisições externas em “locais”. O novo projeto mantém dois processos.
2. **Uma raiz virtual única** é mais simples e segura do que expor caminhos do
   sistema.
3. **Ícones e MIME configuráveis** melhoram a experiência sem código novo.
4. **O visual escuro e o grid de cards** funcionam bem em desktop e celular.

## O que não repetir

- Confiar em `request.remote_addr` para decidir privilégio.
- Servir arquivos por caminho vindo do cliente.
- Carregar arquivo de texto inteiro no navegador sem limite.
- Deixar o painel administrativo sem login.
- Documentar como implementado algo que não foi.

## Critério de conclusão do reaproveitamento

O reaproveitamento está concluído quando:

- o explorer novo usa os mesmos ícones e a mesma identidade visual;
- a API por ID substitui a API por caminho;
- login, logout e administração têm os controles de segurança previstos;
- nenhum arquivo em `legacy/` é importado pelo runtime;
- a documentação descreve o comportamento real, não o desejado.
