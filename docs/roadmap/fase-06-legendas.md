# Fase 6 — Legendas

- **Status:** não iniciada
- **Depende de:** fase 5

## Objetivo

Oferecer legendas no player: embutidas no MKV, avulsas na mesma pasta e ASS com
estilos e fontes, com seleção de faixa.

## Escopo

- Extração de SRT/ASS embutidos para o cache.
- Extração de fontes anexadas ao MKV.
- Conversão de SRT/ASS simples para WebVTT.
- Renderizador ASS no navegador com fontes (A4).
- Fallback WebVTT quando o renderizador não estiver disponível.
- Correspondência automática de legenda avulsa pelo nome-base.
- Detecção de idioma por sufixo.
- Menu de faixas no player.
- Preferência de idioma (`pt-BR`, `pt`, primeira).
- Lembrança da escolha no navegador.
- Estados de erro e ausência de legenda.

## Fora de escopo

- Legendas em imagem (PGS/VobSub).
- Sincronização manual de legenda.
- Tradução automática.
- Edição de legenda.

## Entregáveis

- [ ] Faixas embutidas aparecem no menu.
- [ ] Legenda avulsa é encontrada pelo nome do vídeo.
- [ ] Múltiplos idiomas são listados.
- [ ] ASS com estilos é renderizado com as fontes extraídas.
- [ ] Fallback WebVTT funciona.
- [ ] Preferência de idioma é aplicada e lembrada.
- [ ] Vídeo sem legenda reproduz normalmente.
- [ ] Legenda inválida não quebra o player.

## Checklist

- [ ] Implementar extração de faixas.
- [ ] Implementar extração de fontes.
- [ ] Implementar matching de arquivos avulsos.
- [ ] Implementar conversão para VTT.
- [ ] Integrar renderizador ASS.
- [ ] Implementar menu de faixas.
- [ ] Implementar preferência.
- [ ] Testar formatos e idiomas.

## Arquivos previstos

```text
src/services/subtitles/extract.py
src/services/subtitles/matching.py
src/services/subtitles/languages.py
src/services/subtitles/render.py
src/routes/api/subtitles.py
src/static/js/subtitles.js
src/static/js/ass-renderer.js
tests/subtitles/test_matching.py
tests/subtitles/test_extract.py
```

## Testes

- Extração de SRT embutido.
- Extração de ASS embutido.
- Extração de fontes.
- Matching `S01E01.pt-BR.srt`.
- Múltiplos idiomas.
- Prioridade `pt-BR`.
- ASS inválido.
- Vídeo sem faixa.
- Fallback VTT.

## Critério de saída

O usuário escolhe a legenda no player, vê ASS com o estilo e as fontes
correspondentes, e legendas avulsas são encontradas automaticamente na pasta do
vídeo. Nenhum caso de legenda quebra a reprodução.

## Riscos

- Renderizador ASS no navegador: tamanho, desempenho e compatibilidade.
- Fontes anexadas: nomes e permissões.
- ASS complexo pode não renderizar igual ao VLC; documentar limitações.
- Muitas faixas podem confundir; ordenar e rotular bem.
