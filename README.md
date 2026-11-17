# Telegram Drive

> Nome provisório. Explorador de arquivos pessoal que usa um **canal privado do
> Telegram** como armazenamento e uma interface web local para navegar,
> visualizar e organizar os arquivos.

O projeto reaproveita a experiência do `file_explorer` (navegação em pastas,
preview por tipo de arquivo, login, ícones e streaming), mas troca o disco local
pelo Telegram e adiciona um catálogo próprio de pastas virtuais, metadados,
lixeira e pipeline de mídia.

## Status

**Especificação — implementação não iniciada.** A fonte única do projeto é
[`docs/`](docs/INDEX.md). O andamento está em
[`docs/ROADMAP.md`](docs/ROADMAP.md).

## Como funciona

- **Upload manual:** os arquivos são enviados pelo app oficial do Telegram para
  um canal privado. O app não automatiza uploads, o que reduz o risco para a
  conta.
- **Catálogo local:** um banco SQLite guarda a árvore de pastas virtuais e os
  metadados de cada arquivo. O Telegram é apenas o armazenamento dos bytes.
- **Manifesto na legenda:** cada mensagem recebe uma legenda compacta com os
  dados do arquivo, permitindo reconstruir o catálogo se o banco for perdido.
- **Leitura via MTProto:** a conta acessa o canal (Telethon) para listar,
  baixar e transmitir arquivos de até 2 GB.
- **Player com cache:** vídeos MKV (H.264 + AAC) são remuxados para MP4
  MP4 com `faststart` em cache local, permitindo reprodução e seek no navegador.
- **Legendas:** o player oferece faixas embutidas (ASS/SRT) e legendas avulsas
  na mesma pasta, com preferência por português.
- **Lixeira:** excluir move para a lixeira no catálogo; só esvaziar a lixeira
  apaga a mensagem no Telegram.

## Stack

| Item | Escolha |
|---|---|
| Linguagem | Python 3.13 |
| Aplicação | Flask (dois processos: administração e visualizador) |
| Banco | SQLite (WAL) com migrations SQL versionadas |
| Telegram | MTProto via Telethon, conta dedicada |
| Mídia | ffmpeg/ffprobe (remux e extração de legendas) |
| Testes | pytest |
| Ambiente | `uv` + ambiente virtual |
| Exposição | túnel local (Cloudflared ou Tailscale — decisão adiada) |
| Docker | não utilizado |

## Estrutura do repositório (prevista)

```text
src/
  app_admin.py          # configuração e administração (localhost)
  app_viewer.py         # navegador de arquivos (exposto por túnel)
  config/               # configuração por ambiente
  routes/               # rotas web e API
  services/             # regras de negócio
    telegram/           # cliente MTProto, varredura, leitura
    catalog/            # pastas, arquivos, lixeira, duplicados
    media/              # ffprobe, remux, cache, streaming
    subtitles/          # extração, correspondência e faixas
  repositories/         # acesso ao SQLite
  templates/            # interface (Jinja)
  static/               # CSS, JS, ícones (base herdada)
migrations/             # migrations SQL versionadas
tests/                  # testes automatizados
docs/                   # especificação (fonte única)
scripts/                # utilitários de operação
legacy/                 # referência do projeto anterior (não executado)
```

Os arquivos de `legacy/` são cópia de referência do `file_explorer` (MIT). O
visual, os ícones e o mapa de MIME já estão em `src/static/` e `config/`; o
restante serve para portabilidade e histórico.

## Documentação

- [`docs/INDEX.md`](docs/INDEX.md) — roteador da documentação.
- [`docs/visao-geral.md`](docs/visao-geral.md) — produto, conceitos e limites.
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — fases e status.
- [`docs/ACEITE-MVP.md`](docs/ACEITE-MVP.md) — critérios de aceite.
- [`docs/arquitetura/REAPROVEITAMENTO.md`](docs/arquitetura/REAPROVEITAMENTO.md)
  — o que veio do projeto anterior e como será usado.
- [`docs/arquitetura/INTERFACE.md`](docs/arquitetura/INTERFACE.md) — identidade
  visual e componentes.
- [`docs/arquitetura/SEGURANCA.md`](docs/arquitetura/SEGURANCA.md) — modelo de
  segurança.
- [`AGENTS.md`](AGENTS.md) — conduta para agentes de código.

## Princípios

- A documentação é a fonte única da verdade; código não decide escopo.
- Sem compartilhamento público por link: o acesso é sempre autenticado.
- O Telegram é armazenamento, não interface de navegação.
- Toda operação de escrita no Telegram é exceção e precisa de justificativa.
- Simplicidade primeiro: sem Docker, sem fila, sem multi-tenant no MVP.
- O visual e os ícones vêm do projeto anterior; a API e o modelo de dados são
  novos.

## Licença

MIT. O projeto reaproveita código e assets do `file_explorer`, de Hennan Lewis;
o aviso original está preservado em [`LICENSE`](LICENSE).
