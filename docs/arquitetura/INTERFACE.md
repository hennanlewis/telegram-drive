# Interface e identidade visual

A interface reaproveita a identidade do `file_explorer`: tema escuro, tipografia
Inter, grid de cartões, ícones por tipo, breadcrumb e modal de preview. A
inspiração original é o Explorador de Arquivos do Windows 11.

Os arquivos de base já estão no repositório:

- `src/static/css/style.css` — explorer;
- `src/static/css/login.css` — login;
- `src/static/css/admin.css` — administração;
- `src/static/icons/` — ícones;
- `config/mime_map.json` — extensão → ícone e overrides de MIME;
- `src/static/js/vendor/highlight.min.js` e
  `src/static/css/vendor/tokyo-night-dark.min.css` — realce de código.

Os templates e o JavaScript do legado estão em `legacy/frontend/` como
referência; devem ser **portados**, não copiados sem revisão.

## Princípios

- Mesma linguagem visual do projeto anterior; nada de redesign gratuito.
- Uma única árvore de navegação: header fixo, breadcrumb, grid.
- O arquivo é o protagonista: ícone, nome, tamanho e data.
- Ações destrutivas nunca ficam a um clique acidental.
- O estado do sistema é visível: preparando mídia, Telegram offline, arquivo na
  lixeira, item sem manifesto.
- Funciona em desktop, tablet e celular; teclado e leitor de tela são
  considerados.

## Tokens visuais herdados

| Token | Valor | Uso |
|---|---|---|
| `--bg-primary` | `#0b0f19` | fundo da página |
| `--bg-secondary` | `rgba(22, 30, 49, 0.7)` | header com blur |
| `--bg-card` | `rgba(30, 41, 59, 0.4)` | cartão |
| `--bg-card-hover` | `rgba(30, 41, 59, 0.8)` | hover |
| `--border-color` | `rgba(255, 255, 255, 0.08)` | bordas |
| `--text-primary` | `#f8fafc` | texto |
| `--text-secondary` | `#94a3b8` | metadados |
| `--accent` | `#3b82f6` | ação primária |
| `--accent-gradient` | `#3b82f6 → #8b5cf6` | título e progresso |
| `--danger` | `#ef4444` | erro e exclusão |
| `--radius-lg` / `--radius-md` | `12px` / `8px` | cartões e botões |

Fonte: Inter (Google Fonts), com fallback para `system-ui`.

## Estrutura do explorer

```text
┌─────────────────────────────────────────────────────┐
│ Explorador de Arquivos          [usuário] [Sair]    │
│ Raiz / Filmes / Série                               │
└─────────────────────────────────────────────────────┘
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│  ícone   │ │  ícone   │ │  ícone   │ │  ícone   │
│  nome    │ │  nome    │ │  nome    │ │  nome    │
│  meta    │ │  meta    │ │  meta    │ │  meta    │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
```

Componentes herdados:

- `.app-header`, `.header-content`, `.header-top` — cabeçalho.
- `.user-chip`, `.role-tag` — identificação do usuário.
- `#breadcrumbs` — navegação hierárquica.
- `.explorer` — grid `repeat(auto-fill, minmax(220px, 1fr))`.
- `.file-card`, `.file-info`, `.file-name`, `.file-meta` — cartão de item.
- `.modal-overlay`, `.modal-container`, `.modal-content-body` — preview.
- `.btn`, `.btn-primary`, `.btn-ghost`, `.btn-close` — botões.
- `.error-msg` — estado de erro.
- `.progress-track`, `.progress-fill`, `.upload-meta` — progresso.

## Componentes novos ou adaptados

| Componente | Origem | Mudança |
|---|---|---|
| Cabeçalho | legado | Adicionar estado da conexão e link para a lixeira |
| Breadcrumb | legado | Navegar por ID; incluir “Para organizar” e “Lixeira” |
| Cartão de arquivo | legado | Ícone, nome, tamanho, data; menu de ações |
| Menu de contexto | novo | Mover, renomear, favoritar, excluir, metadados |
| Modal de preview | legado | Player com faixas de legenda e estado de preparação |
| Modal de upload | legado | **substituído** por instruções de envio pelo Telegram |
| Barra de progresso | legado | Usada para preparação de mídia, não para upload |
| Painel de metadados | novo | Caminho, hash, versão, data, referência Telegram |
| Seletor de legendas | novo | Faixas embutidas e avulsas, preferência de idioma |
| Lixeira | novo | Lista, restaurar, esvaziar com confirmação |
| Inbox | novo | Destaque para arquivos sem manifesto |

## Ícones e tipos

`config/mime_map.json` mapeia extensões para ícones. O resolvedor do novo
projeto recebe o MIME e o nome do catálogo, não um `Path` do sistema.

| Tipo | Ícone |
|---|---|
| pasta | `folder.png` / `empty-folder.png` |
| áudio | `audio-file.png` |
| vídeo | `video-file.png` |
| imagem | `image-file.png` |
| texto | `text-file.png` |
| compactado | `zip-file.png` |
| ISO | `iso-file.png` |
| PDF | `svg/pdf-file.svg` |
| HTML/CSS/JS/TS/Python/React | ícones SVG específicos |

Regra: se a extensão não estiver no mapa, usar `file.png`. O tipo lógico
(`folder`, `image`, `video`, `audio`, `text`, `pdf`, `file`) continua sendo
calculado pelo MIME, como no legado, mas a partir dos dados do catálogo.

## Preview

| Tipo | Comportamento |
|---|---|
| Imagem | `<img>` no modal, com maximizar |
| Vídeo | `<video controls>` com faixas e estado de preparação |
| Áudio | `<audio controls>` |
| PDF | `<iframe>` no modal |
| Texto/código | `<pre><code>` com Highlight.js e tema Tokyo Night |
| Outros | download direto |

Limites:

- Texto: carregar no máximo 1 MB; acima disso, oferecer download.
- PDF: deixar o navegador renderizar; não converter.
- Imagem: sem transformação no MVP.
- Vídeo: sempre passar pelo pipeline de mídia.

## Login

Tela herdada (`login.css`): cartão central, título, subtítulo, campos de usuário
e senha, mensagem de erro. Manter:

- `autocomplete="username"` e `current-password`;
- foco automático no usuário;
- erro genérico (“Usuário ou senha inválidos”) sem revelar qual campo falhou;
- bloqueio temporário após tentativas excessivas;
- nenhuma opção de cadastro público.

## Administração

Painel local herdado (`admin.css`): cartões, formulário e tabela de usuários.
Adaptar para:

- configurar o canal e testar a conexão com o Telegram;
- cadastrar e desativar usuários;
- exibir estado da sessão do Telethon (sem mostrar segredos);
- exibir uso do cache e botão de limpeza;
- executar varredura manual do canal;
- mostrar diagnóstico de ffmpeg/ffprobe.

O painel continua com o selo “Local Only (127.0.0.1)” e **não** é exposto pelo
túnel.

## Estados e mensagens

| Estado | Mensagem |
|---|---|
| Pasta vazia | “Esta pasta está vazia.” |
| Inbox com itens | “Há N arquivos aguardando organização.” |
| Telegram offline | “Sem conexão com o Telegram. Exibindo o catálogo local.” |
| Mídia preparando | “Preparando vídeo…” com progresso |
| Mídia falhou | “Não foi possível preparar este vídeo.” + tentar de novo |
| Cache cheio | “Cache cheio; liberando espaço…” |
| Arquivo missing | “O arquivo não está mais disponível no Telegram.” |
| Lixeira vazia | “A lixeira está vazia.” |
| Exclusão definitiva | Confirmação explícita com contagem de itens |

## Responsividade

- Grid fluido com mínimo de 220px por cartão.
- Em telas estreitas, o header quebra em duas linhas.
- Modal ocupa 90% da largura e 85% da altura; botão de maximizar disponível.
- Áreas de toque com pelo menos 44px.
- Evitar hover como único meio de revelar ações.

## Acessibilidade

- Navegação por teclado no grid e nos modais.
- `Esc` fecha o modal; `Enter`/`Espaço` abrem o item focado.
- `aria-label` nos botões de ícone.
- Contraste mínimo AA para texto e metadados.
- Não depender apenas de cor para indicar estado.
- Respeitar `prefers-reduced-motion`.

## O que não fazer

- Reintroduzir upload para o disco local.
- Usar caminhos do sistema na interface.
- Exibir segredos, tokens ou caminho da sessão do Telethon.
- Criar uma segunda identidade visual para o player.
- Copiar o `app.js` do legado sem trocar a API por ID.
