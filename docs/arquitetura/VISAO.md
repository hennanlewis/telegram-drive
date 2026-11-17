# Arquitetura — visão geral

## Topologia

```text
Navegador (você, fora de casa)
        │  HTTPS (túnel)
        ▼
Computador pessoal
┌──────────────────────────────────────────────┐
│  túnel (Cloudflared ou Tailscale)            │
│        │                                     │
│        ▼                                     │
│  app_viewer  (127.0.0.1:8080)                │
│    ├── catálogo (SQLite)                     │
│    ├── cliente Telegram (Telethon)  ─────────┼──► Canal privado
│    ├── pipeline de mídia (ffmpeg)            │
│    └── cache local de mídia                  │
│                                              │
│  app_admin   (127.0.0.1:8081, só localhost)  │
│    └── catálogo (SQLite)                     │
└──────────────────────────────────────────────┘
```

O processo de **administração** nunca é exposto pelo túnel. Ele serve para
configuração inicial, usuários e diagnóstico. O processo **visualizador** é o
único que o túnel alcança.

## Componentes

| Componente | Responsabilidade |
|---|---|
| `app_admin` | Configuração, usuários, diagnóstico, estado do canal. Escuta só em localhost. |
| `app_viewer` | Login, navegação, preview, player, organização, lixeira. |
| Catálogo | Árvore virtual, metadados, estado da lixeira, favoritos, auditoria. |
| Cliente Telegram | Varredura do canal, resolução de referências, download e streaming. |
| Pipeline de mídia | Decisão de reprodução, remux, transcodificação de áudio, cache. |
| Legendas | Extração de faixas, correspondência de arquivos avulsos, fontes. |
| Cache | Arquivos temporários de mídia e legendas, com limite e expiração. |
| Túnel | Exposição do visualizador; decisão adiada para a fase 9. |

## Dois processos, um banco

- Ambos usam o mesmo SQLite em modo **WAL**.
- O `app_admin` escreve configuração e usuários; o `app_viewer` escreve catálogo.
- Sessões e segredos de sessão são **distintos** entre os processos.
- O visualizador nunca depende do processo de administração estar no ar.
- Se a concorrência de escrita crescer, a fase 9 avalia mover a escrita para um
  único processo; não é necessário no MVP.

Essa separação vem do projeto anterior e existe porque, atrás de um túnel, todas
as requisições parecem vir de `127.0.0.1`. Decidir privilégio por IP de origem
seria uma falha grave. Detalhes em
[`SEGURANCA.md`](SEGURANCA.md).

## Reaproveitamento visual

A interface mantém a identidade do `file_explorer`: tema escuro, Inter,
breadcrumb, grid de cartões, ícones por tipo e modal de preview. Os assets já
estão em `src/static/`; os templates e o JavaScript originais estão em
`legacy/frontend/` como referência de portabilidade. O que muda é a fonte dos
dados (catálogo por ID, não sistema de arquivos) e o fluxo de upload (manual pelo
Telegram).

Ver [`REAPROVEITAMENTO.md`](REAPROVEITAMENTO.md) e [`INTERFACE.md`](INTERFACE.md).

## Fronteira de risco

Toda funcionalidade é classificada pelo que faz no Telegram:

| Camada | Operações | Risco para a conta |
|---|---|---|
| **Local** | pastas, nomes, favoritos, lixeira, metadados, ordenação, busca por nome | nenhum |
| **Leitura** | listar canal, resolver referência, baixar bytes, streaming | baixo |
| **Escrita leve** | editar legenda/manifesto, apagar mensagem ao esvaziar lixeira | baixo, se esporádico |
| **Escrita pesada** | upload automatizado, encaminhamento em massa | evitado no MVP |

O desenho deve manter o máximo de funcionalidades na camada local.

## Fluxos

### Varredura do canal

1. O cliente lê mensagens novas a partir do último `message_id` conhecido.
2. Para cada documento, registra as coordenadas e os metadados básicos.
3. Se a legenda contém um manifesto `FD1`, usa os dados declarados.
4. Caso contrário, o arquivo entra no **Inbox** com o nome original.
5. O estado da varredura é atualizado ao final.

A varredura **não baixa conteúdo**. Ela só lê metadados de mensagens.

### Organização

1. O usuário move o arquivo para uma pasta virtual no catálogo.
2. O app grava/atualiza o manifesto na legenda da mensagem.
3. A operação é registrada na auditoria.
4. Se a gravação da legenda falhar, o catálogo continua válido e a divergência é
   marcada para reconciliação.

### Reprodução

1. O app resolve a referência da mensagem e verifica o cache.
2. Se o formato é compatível, transmite direto do Telegram com `Range`.
3. Se é MKV H.264/AAC, gera o remux em cache e transmite do cache.
4. Legendas são extraídas ou localizadas e servidas ao player.
5. O player pede faixas conforme a escolha do usuário.

### Exclusão

1. Excluir no catálogo marca `trashed` e guarda a pasta de origem.
2. Restaurar volta ao estado `active`.
3. Esvaziar a lixeira apaga as mensagens no Telegram e remove os registros.

## Estrutura modular prevista

```text
src/
  app_admin.py
  app_viewer.py
  config/            # leitura de ambiente
  routes/
    web/             # páginas Jinja
    api/             # JSON e streaming
  services/
    auth/            # login, sessão, autorização
    catalog/         # pastas, arquivos, lixeira, duplicados
    telegram/        # cliente, varredura, leitura
    media/           # ffprobe, remux, cache, range
    subtitles/       # extração, matching, faixas
  repositories/      # SQL e mapeamento
  templates/
  static/
```

Regra: **regra de negócio não fica na rota nem no template**. Rotas validam,
chamam serviço e respondem; serviços concentram decisão.

## Modos de falha

| Falha | Comportamento esperado |
|---|---|
| Telegram indisponível | catálogo continua navegável em modo somente leitura; player informa erro |
| ffmpeg ausente | preview/download continuam; player explica que a mídia não pode ser preparada |
| Cache cheio | remoção LRU antes de nova preparação |
| Referência expirada | recoleta a mensagem e atualiza a referência; se sumiu, marca `missing` |
| Banco corrompido | restaurar backup; se não houver, reconstruir a partir dos manifestos |
| Túnel fora do ar | acesso local continua; nada no catálogo é perdido |

## Decisões relacionadas

- Acesso ao Telegram: [`../decisoes/ADR-001-acesso-ao-telegram.md`](../decisoes/ADR-001-acesso-ao-telegram.md)
- Catálogo e manifesto: [`../decisoes/ADR-003-catalogo-e-manifesto.md`](../decisoes/ADR-003-catalogo-e-manifesto.md)
- Stack e execução: [`../decisoes/ADR-006-stack-e-execucao.md`](../decisoes/ADR-006-stack-e-execucao.md)
- Exposição e rede: [`../decisoes/ADR-007-exposicao-e-rede.md`](../decisoes/ADR-007-exposicao-e-rede.md)
