# Mídia e legendas

## Reprodução

### Decisão

1. Consultar o perfil de mídia do arquivo (container, codecs, duração).
2. Se compatível com o navegador, reproduzir direto.
3. Se for MKV H.264 + AAC, remuxar para MP4 com `faststart`.
4. Se o áudio não for suportado, transcodificar apenas o áudio.
5. Se o vídeo não for suportado, transcodificar com aviso ou recusar.

### Regras

- O perfil é calculado uma vez e armazenado no catálogo.
- A preparação é idempotente: o mesmo hash/perfil não é preparado duas vezes.
- O cache tem estado `preparing`, `ready` e `failed`.
- O player mostra o estado e permite tentar de novo.
- Download nunca depende do pipeline de mídia.

## Legendas

### Fontes

1. **Embutidas** no container (SRT, ASS/SSA).
2. **Avulsas** na mesma pasta virtual, com o mesmo nome-base do vídeo.
3. **Futuras:** legenda enviada como arquivo separado no canal.

### Correspondência automática

- Comparar o nome-base do vídeo com o nome-base da legenda.
- Extensões aceitas: `.srt`, `.ass`, `.ssa`, `.vtt`.
- Sufixos de idioma reconhecidos: `pt-BR`, `pt`, `en`, `es`, `fr`, entre outros.
- Exemplo: `S01E01.mkv` encontra `S01E01.pt-BR.srt` e `S01E01.en.ass`.
- Se houver mais de uma, listar todas, ordenadas por preferência.
- A busca é apenas na pasta do vídeo, não recursiva.

### Preferência

- Padrão: `pt-BR`, depois `pt`, depois a primeira faixa.
- A escolha do usuário é lembrada no navegador.
- Não altera o catálogo nem o Telegram.

### Renderização

| Formato | Estratégia |
|---|---|
| SRT | converter para WebVTT |
| ASS/SSA simples | converter para WebVTT |
| ASS/SSA com estilos | renderizador libass no navegador, com fontes extraídas |
| PGS/VobSub | fora do MVP |

### ASS e fontes

- Fontes podem estar anexadas ao MKV.
- Extrair para o cache e servir ao renderizador.
- Se a fonte faltar, usar fallback e avisar.
- Se o renderizador não estiver disponível, oferecer WebVTT como fallback.

### Falhas

- Legenda inválida: ignorar a faixa, manter o vídeo.
- Legenda maior que o esperado: não carregar automaticamente.
- Vídeo sem legenda: reproduzir normalmente, sem erro.

## Preferências do usuário

- Idioma de legenda.
- Tamanho e cor da legenda (quando o renderizador suportar).
- Lembradas no navegador; sem conta multiusuário no MVP.
