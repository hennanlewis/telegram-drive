# Critérios de aceite do MVP

O MVP está aceito quando **todos** os itens abaixo forem verdadeiros em uma
execução real, documentada no registro da fase 9.

## Acesso

- [ ] O visualizador exige login; nenhuma rota de dados responde sem sessão.
- [ ] A administração só responde em `127.0.0.1` e não é exposta pelo túnel.
- [ ] Senhas são armazenadas com hash; nenhuma senha aparece em log.
- [ ] A sessão expira e o logout invalida o acesso.
- [ ] Tentativas de login são limitadas.

## Catálogo e navegação

- [ ] É possível criar, renomear e excluir pastas virtuais.
- [ ] É possível navegar por vários níveis, com breadcrumb.
- [ ] A listagem mostra nome, tipo, tamanho e data.
- [ ] Arquivos na lixeira não aparecem na navegação normal.
- [ ] A ordenação por nome, data e tamanho funciona.
- [ ] Reiniciar a aplicação preserva o catálogo.

## Ingestão

- [ ] Um arquivo enviado manualmente ao canal aparece no Inbox após a varredura.
- [ ] A varredura não baixa o conteúdo dos arquivos.
- [ ] O manifesto é gravado na legenda ao organizar.
- [ ] Um arquivo repetido (mesmo hash) gera aviso com opções de manter os dois,
      substituir ou criar versão.
- [ ] Arquivo sem manifesto pode ser reconstruído a partir do canal quando o
      banco é perdido.

## Preview e download

- [ ] Imagens são exibidas no navegador.
- [ ] PDFs abrem no visualizador do navegador.
- [ ] Arquivos de texto são exibidos com limite de tamanho.
- [ ] Tipos desconhecidos oferecem download.
- [ ] O download preserva o nome original e funciona para arquivos grandes.

## Mídia

- [ ] Vídeos MKV (H.264 + AAC) são reproduzidos no navegador.
- [ ] O player permite seek em vídeos remuxados.
- [ ] Áudio é reproduzido no navegador.
- [ ] O cache é limitado por tamanho e por tempo.
- [ ] Um arquivo em preparação mostra estado claro na interface.
- [ ] A ausência do ffmpeg gera erro amigável, não quebra a aplicação.
- [ ] Um formato não suportado gera mensagem clara, não tela quebrada.

## Legendas

- [ ] Legendas embutidas (SRT/ASS) aparecem como faixas selecionáveis.
- [ ] Legendas avulsas na mesma pasta são encontradas pelo nome do vídeo.
- [ ] O player lembra a preferência de idioma.
- [ ] ASS com estilos e fontes é renderizado corretamente, ou há fallback
      explícito para WebVTT.
- [ ] Vídeo sem legenda continua reproduzindo normalmente.

## Organização e lixeira

- [ ] Mover arquivo entre pastas atualiza o catálogo.
- [ ] Mover para a lixeira preserva o caminho de origem.
- [ ] Restaurar devolve o arquivo ao caminho original.
- [ ] Se a pasta de origem não existe mais, restaurar recria ou usa a raiz.
- [ ] Esvaziar a lixeira apaga a mensagem no Telegram e o registro local.
- [ ] Nenhuma exclusão no Telegram ocorre fora do esvaziamento da lixeira.

## Operação

- [ ] A aplicação sobe com um comando documentado.
- [ ] A aplicação volta a funcionar depois de reiniciar o computador.
- [ ] Existe uma rotina de backup do banco, testada com restauração.
- [ ] O log não contém segredos nem caminhos de sessão do Telegram.
- [ ] Existe verificação de saúde da aplicação e do acesso ao Telegram.
- [ ] A indisponibilidade do Telegram produz erro amigável e modo somente
      leitura, sem perda de dados.

## Documentação

- [ ] `README.md` permite instalar e executar do zero.
- [ ] `docs/ROADMAP.md` reflete o estado real.
- [ ] Cada fase executada tem registro em `docs/registros/`.
- [ ] Nenhuma decisão tomada durante a implementação ficou fora dos ADRs.
