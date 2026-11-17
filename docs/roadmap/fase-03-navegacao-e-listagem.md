# Fase 3 — Navegação e listagem

- **Status:** não iniciada
- **Depende de:** fases 1 e 2

## Objetivo

Entregar a experiência de explorador: login, árvore de pastas virtuais, breadcrumb, grid de cartões, ícones e navegação — usando o visual herdado.

## Escopo

- Portar `index.html`, `login.html` e o CSS herdado.
- Portar a lógica de grid, breadcrumb e modal (sem preview ainda).
- Login/logout e sessão.
- Autorização por papel.
- API de navegação por ID.
- Listagem com pastas primeiro e nome ascendente.
- Ícones via `mime_map.json` e catálogo.
- Inbox visível com contador.
- Estados vazio, carregando e erro.
- Paginação ou carregamento incremental, se necessário.

## Fora de escopo

- Preview de arquivos.
- Download.
- Player.
- Organização (mover/renomear).
- Lixeira.

## Entregáveis

- [ ] Usuário entra e é redirecionado para a raiz.
- [ ] Breadcrumb navega por qualquer nível.
- [ ] Grid exibe pastas e arquivos com ícone, nome e metadados.
- [ ] Inbox aparece com contador de pendências.
- [ ] Sessão expirada redireciona para o login.
- [ ] Viewer não tem rota administrativa.
- [ ] Layout funciona em desktop e celular.
- [ ] Nenhum caminho do sistema aparece na interface.

## Checklist

- [ ] Portar templates e CSS.
- [ ] Implementar `api.js` e módulos de UI.
- [ ] Implementar rotas de login/logout.
- [ ] Implementar API de navegação.
- [ ] Implementar breadcrumb e grid.
- [ ] Implementar estados de UI.
- [ ] Revisar acessibilidade e responsividade.
- [ ] Testar autorização.

## Arquivos previstos

```text
src/templates/base.html
src/templates/explorer.html
src/templates/login.html
src/static/css/style.css
src/static/css/login.css
src/static/js/api.js
src/static/js/explorer.js
src/static/js/login.js
src/routes/web/auth.py
src/routes/web/explorer.py
src/routes/api/folders.py
tests/web/test_auth.py
tests/api/test_folders.py
```

## Testes

- Login válido e inválido.
- Rota protegida sem sessão.
- Navegação por ID em vários níveis.
- Ordenação de pastas e arquivos.
- Inbox e contador.
- Ícone desconhecido cai no padrão.
- Viewer não responde a rota de admin.

## Critério de saída

É possível entrar, navegar por toda a árvore, ver o Inbox e reconhecer os tipos de arquivo, com a identidade visual do projeto anterior e sem qualquer caminho real do sistema exposto.

## Riscos

- O `app.js` antigo usa `path`; a portagem precisa trocar tudo por ID.
- O CSS herdado pode exigir ajustes para novos componentes.
- Paginação prematura pode complicar; medir com acervo real.
