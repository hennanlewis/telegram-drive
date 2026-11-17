# Arquitetura — mídia e streaming

## Objetivo

Reproduzir vídeo e áudio no navegador a partir de arquivos que estão no Telegram, com seek, sem baixar o arquivo inteiro antes de começar e sem reencodar quando não for necessário.

## Compatibilidade do navegador

| Container / codec | Suporte no navegador | Estratégia |
|---|---|---|
| MP4 + H.264 + AAC | universal | reprodução direta |
| MKV + H.264 + AAC | container não suportado | **remux** para MP4 com `faststart` |
| MKV + H.264 + AC3/DTS | áudio não suportado | remux + transcode do áudio para AAC |
| MKV + HEVC | suporte parcial | transcode de vídeo (pesado) ou recusa explicada |
| WebM + VP9/Opus | bom | reprodução direta |
| AVI/WMV/MPEG-2 | não suportado | transcode ou recusa explicada |

O acervo previsto é **MKV H.264 (inclusive NVENC) + AAC**. Nesse caso, o caminho é sempre **remux com cópia de vídeo e áudio** — rápido e com baixo uso de CPU.

## Pipeline

```text
pedido do player
   │
   ├─ arquivo já em cache? ──sim──► serve do cache (Range)
   │
   ├─ ffprobe: container, codecs, duração, faixas
   │
   ├─ compatível? ──sim──► stream direto do Telegram (Range)
   │
   └─ precisa preparar?
        ├─ cria tarefa de remux/transcode
        ├─ responde 202 + status
        └─ ao concluir, serve do cache
```

### Etapas

1. **Sondagem:** `ffprobe` obtém container, codecs de vídeo/áudio, duração, dimensões e faixas de legenda.
2. **Decisão:** tabela de compatibilidade.
3. **Preparação:** gera o arquivo de cache com ffmpeg.
4. **Publicação:** cache pronto e registrado no catálogo de cache.
5. **Entrega:** HTTP com `Range`, `Accept-Ranges`, `Content-Length` e `206`.

### Perfis de preparação

| Perfil | Quando | Comando conceitual |
|---|---|---|
| `direct` | MP4/WebM compatível | nenhum |
| `remux` | MKV H.264 + AAC | `-c copy` para MP4 com `faststart` |
| `remux-aac` | MKV H.264 + AC3/DTS | vídeo `copy`, áudio AAC |
| `transcode` | codec de vídeo incompatível | reencode (último recurso) |

O perfil é parte da chave do cache: o mesmo arquivo pode ter mais de uma versão preparada se o perfil mudar.

## Cache

- Diretório local (`CACHE_DIR`), separado do banco.
- Chave: `{sha256}-{perfil}.mp4` (ou `.m4a`, `.vtt`, `.ass`).
- Limite por tamanho (`CACHE_MAX_GB`) e por idade (`CACHE_TTL_HOURS`).
- Política **LRU**: ao faltar espaço, remove o menos usado recentemente.
- Limpeza na inicialização e periodicamente.
- Arquivo em preparação tem estado (`preparing`, `ready`, `failed`) e não é servido parcialmente.
- Um mesmo arquivo não é preparado duas vezes ao mesmo tempo: lock por chave.

## Streaming e seek

- O endpoint de mídia responde a `Range` com `206 Partial Content`.
- `HEAD` retorna tamanho e tipo sem corpo.
- Para `direct`, o intervalo é traduzido em offset no Telegram.
- Para cache, o intervalo é lido do arquivo local.
- Seek por tempo depende do índice do container; com MP4 `faststart`, o navegador faz a busca por byte.
- O player mostra buffer e estado de preparação.
- Não há HLS, DASH, DRM ou transmissão adaptativa no MVP.

## Legendas

### Fontes

1. **Embutidas** no MKV (SRT, ASS/SSA).
2. **Avulsas** na mesma pasta virtual, com o mesmo nome-base do vídeo (ex.: `S01E01.pt-BR.srt`).
3. Futuro: legenda embutida em arquivo separado enviado ao canal.

### Extração

- SRT/ASS embutidos são extraídos para o cache com ffmpeg.
- ASS com fontes embutidas: as fontes são anexos do MKV e precisam ser extraídas junto.
- Formatos de imagem (PGS/VobSub) não são suportados no MVP.

### Renderização

| Formato | Estratégia |
|---|---|
| SRT | converter para WebVTT e usar `<track>` |
| ASS/SSA simples | converter para WebVTT (perde estilo) |
| ASS/SSA com estilos e fontes | renderizador libass no navegador (WASM) com as fontes extraídas |

A biblioteca do renderizador ASS será escolhida na fase 6. O requisito é preservar estilos e fontes; se não for viável, o fallback é WebVTT com aviso explícito.

### Correspondência automática

- Na mesma pasta virtual, procurar arquivos cujo nome-base seja igual ao do vídeo e cuja extensão seja de legenda.
- Vários idiomas: usar o sufixo (`pt-BR`, `pt`, `en`, `es`).
- Preferência padrão: português (`pt-BR`, depois `pt`), depois a primeira faixa.
- A escolha do usuário é lembrada no navegador; não altera o catálogo.

## Desempenho esperado

- Remux de MKV H.264/AAC: próximo da velocidade de disco, baixo CPU.
- Transcode de vídeo: lento; deve ser evitado e avisado.
- Primeiro play de um MKV grande pode levar alguns segundos; a interface mostra progresso.
- Downloads do Telegram podem ser limitados; o cache evita repetição.

## Falhas e mensagens

| Situação | Comportamento |
|---|---|
| ffmpeg/ffprobe ausente | erro claro; download continua disponível |
| Preparação falhou | estado `failed`, motivo no log, botão tentar de novo |
| Telegram indisponível | erro amigável; cache continua servindo o que já existe |
| Codec não suportado | mensagem explicando e oferta de download |
| Cache cheio | LRU; se ainda faltar, erro claro |
| Legenda inválida | ignora a faixa e mantém o vídeo |

## Fora de escopo

- Transcodificação em massa ou pré-geração de toda a biblioteca.
- Múltiplas qualidades (480p/720p/1080p).
- Legendas em imagem.
- Sincronização de legendas.
- Edição de vídeo.
