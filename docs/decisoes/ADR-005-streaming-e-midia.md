# ADR-005 — Streaming, pipeline de mídia e legendas

## Status

Aceita.

## Contexto

O acervo é composto principalmente por **MKV H.264 (inclusive NVENC) com áudio
AAC**. Navegadores não reproduzem MKV nativamente, mas suportam H.264 e AAC.
Grande parte dos MKV tem legendas ASS embutidas, às vezes com fontes anexadas.
O player precisa de seek e de escolha de faixa.

## Decisão

### Streaming

- Proxy próprio com suporte a `Range`, servindo do cache ou do Telegram.
- Reprodução direta para containers/codecs compatíveis.
- **Remux** para MKV H.264 + AAC: troca o container para MP4 com `faststart` e
  `-c copy`. Sem reencode.
- Transcode de áudio apenas se o codec não for suportado (ex.: AC3/DTS).
- Transcode de vídeo é último recurso e deve ser avisado.
- Cache local com limite por tamanho e idade, política LRU.
- O arquivo é preparado antes de ser servido; a interface mostra progresso.

### Legendas

- Extrair faixas embutidas SRT/ASS para o cache.
- Extrair fontes anexadas quando houver ASS com estilos.
- Oferecer faixas no player, com preferência por português.
- Procurar legenda avulsa na mesma pasta virtual pelo nome-base do vídeo
  (ex.: `S01E01.pt-BR.srt`).
- ASS com estilos: renderizador libass no navegador (WASM) com as fontes
  extraídas; fallback para WebVTT com aviso.
- SRT: converter para WebVTT.
- Formatos de imagem (PGS/VobSub) ficam fora do MVP.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Servir MKV direto | Navegador não reproduz |
| Transcodificar tudo para MP4 | CPU e tempo altos; desnecessário para H.264/AAC |
| HLS/DASH | Complexidade desproporcional para uso pessoal |
| Baixar o arquivo inteiro para tocar | Não permite início rápido nem seek |
| Converter ASS para VTT sempre | Perde estilos e fontes, que o usuário quer preservar |

## Consequências

- ffmpeg/ffprobe passam a ser dependência de sistema.
- O primeiro play de um MKV pode levar alguns segundos.
- O cache precisa de espaço e limpeza.
- O player ganha complexidade com faixas e renderizador ASS.
- O download continua disponível mesmo quando a reprodução não for possível.

## Relacionados

- [`../arquitetura/MIDIA.md`](../arquitetura/MIDIA.md)
- [`../domain/midia-e-legendas.md`](../domain/midia-e-legendas.md)
- [`../roadmap/fase-05-pipeline-de-midia.md`](../roadmap/fase-05-pipeline-de-midia.md)
- [`../roadmap/fase-06-legendas.md`](../roadmap/fase-06-legendas.md)
