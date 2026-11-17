# Fase 5 — Pipeline de mídia

- **Status:** não iniciada
- **Depende de:** fase 4

## Objetivo

Reproduzir vídeo e áudio no navegador, com seek, a partir de arquivos no
Telegram — priorizando remux de MKV H.264/AAC, sem reencode desnecessário.

## Escopo

- `ffprobe` para identificar container, codecs, duração e dimensões.
- Perfil de mídia armazenado no catálogo.
- Decisão: direto, remux, remux com áudio AAC, transcode.
- Cache local com chave por hash + perfil.
- Remux MKV → MP4 com `faststart` usando `-c copy`.
- Transcode de áudio AC3/DTS para AAC.
- Transcode de vídeo apenas se necessário, com aviso.
- Endpoint de status da preparação.
- Streaming com `Range`, `206` e `HEAD`.
- Seek no player.
- Cache LRU com limite de tamanho e idade.
- Lock por arquivo.
- Erro amigável para ffmpeg ausente ou falha.

## Fora de escopo

- Legendas.
- Múltiplas qualidades.
- HLS/DASH.
- Pré-geração de toda a biblioteca.

## Entregáveis

- [ ] MKV H.264/AAC toca no navegador.
- [ ] Seek funciona no vídeo remuxado.
- [ ] MP4 compatível toca direto, sem cache.
- [ ] Áudio AAC toca; AC3 é convertido.
- [ ] Preparação mostra estado e progresso.
- [ ] Cache respeita os limites e remove itens antigos.
- [ ] Requisição concorrente do mesmo arquivo não duplica preparação.
- [ ] `Range` inválido retorna erro correto.
- [ ] ffmpeg ausente não quebra a aplicação.
- [ ] Download continua funcionando.

## Checklist

- [ ] Implementar probe e perfil.
- [ ] Implementar decisão de pipeline.
- [ ] Implementar cache e LRU.
- [ ] Implementar remux.
- [ ] Implementar transcode de áudio.
- [ ] Implementar endpoint de status.
- [ ] Implementar streaming com range.
- [ ] Implementar player e estados.
- [ ] Criar fixtures pequenas de mídia.
- [ ] Testar limites e concorrência.

## Arquivos previstos

```text
src/services/media/probe.py
src/services/media/decision.py
src/services/media/cache.py
src/services/media/transcoder.py
src/services/media/streamer.py
src/routes/api/media.py
src/static/js/player.js
tests/media/test_decision.py
tests/media/test_cache.py
tests/api/test_media_range.py
tests/fixtures/ (mídia pequena)
```

## Testes

- Perfil de MKV H.264/AAC.
- Perfil de MP4 direto.
- Perfil de AC3.
- Cache hit e miss.
- Evicção LRU.
- Range válido, inválido e aberto.
- HEAD sem corpo.
- Lock de preparação.
- ffmpeg ausente.
- Falha de preparação.

## Critério de saída

Um MKV H.264/AAC do acervo real toca no navegador, com seek, sem reencode de
vídeo, e o cache permanece dentro do limite configurado. Os demais perfis têm
comportamento definido e mensagens claras.

## Riscos

- `faststart` e seek: validar em Chrome, Firefox e Safari.
- Áudio AC3: custo de transcode; medir.
- HEVC: decidir entre transcode e recusa (A6).
- Espaço em disco: monitorar e limpar.
- Windows: caminho do ffmpeg e escaping de argumentos.
