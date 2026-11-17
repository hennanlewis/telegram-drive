# Fase 4 — Preview e download

- **Status:** não iniciada
- **Depende de:** fase 3

## Objetivo

Abrir arquivos no navegador quando possível e baixar quando não for: imagem,
PDF, texto/código e tipos desconhecidos.

## Escopo

- Modal de preview herdado, com maximizar e fechar.
- Imagem via stream autenticado.
- PDF em iframe.
- Texto/código com Highlight.js e tema Tokyo Night.
- Limite de tamanho para texto (A3).
- Download com nome original e `Content-Disposition`.
- Metadados básicos no modal.
- Estado de carregamento e erro.
- Tipos não suportados oferecem download.

## Fora de escopo

- Player de vídeo/áudio.
- Legendas.
- Pipeline de mídia.
- Edição de texto.

## Entregáveis

- [ ] Imagem abre no modal e pode ser maximizada.
- [ ] PDF abre no visualizador do navegador.
- [ ] Texto é exibido com realce e sem carregar acima do limite.
- [ ] Arquivo binário oferece download.
- [ ] Download preserva nome e funciona para arquivo grande.
- [ ] Erro de leitura mostra mensagem amigável.
- [ ] Nenhum caminho interno é exposto.

## Checklist

- [ ] Implementar rota de conteúdo autenticada.
- [ ] Implementar download.
- [ ] Implementar preview por tipo.
- [ ] Implementar limite de texto e fallback.
- [ ] Portar modal e estilos.
- [ ] Testar cabeçalhos e tipos.
- [ ] Revisar acessibilidade do modal.

## Arquivos previstos

```text
src/routes/api/content.py
src/services/catalog/content.py
src/services/media/detect.py
src/templates/explorer.html
src/static/js/preview.js
tests/api/test_content.py
```

## Testes

- Imagem servida com MIME correto.
- PDF servido inline.
- Texto acima do limite não é carregado.
- Texto em UTF-8 é exibido corretamente.
- Download com nome sanitizado.
- Requisição sem sessão é recusada.
- Arquivo `missing` retorna erro claro.

## Critério de saída

Imagem, PDF e texto abrem no navegador; qualquer outro tipo pode ser baixado; o
comportamento é consistente para arquivos pequenos e grandes, e todas as rotas
exigem sessão.

## Riscos

- Texto grande pode estourar memória; limite é obrigatório.
- PDF pode não renderizar em alguns navegadores móveis; oferecer download.
- Codificação desconhecida; usar fallback e avisar.
