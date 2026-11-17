# Visão geral

## Problema

Guardar vídeos, músicas e PDFs em um computador pessoal e acessá-los fora de casa exige expor a máquina, manter armazenamento e lidar com backups. O Telegram já oferece armazenamento em nuvem gratuito, com aplicativos maduros e limites generosos por arquivo. Falta uma camada que transforme um canal privado em um **explorador de arquivos** com pastas, preview, player, lixeira e metadados.

## Proposta

Um aplicativo web pessoal, rodando no próprio computador, que:

- usa um **canal privado do Telegram** como armazenamento dos bytes;
- mantém um **catálogo local** com a árvore de pastas virtuais e os metadados;
- lê o canal por **MTProto** (conta dedicada), sem depender de bot;
- reproduz vídeo e áudio no navegador, com cache local e seek;
- organiza arquivos enviados manualmente pelo app oficial do Telegram;
- oferece lixeira com restauração e exclusão real apenas ao esvaziar.

## Princípios

1. **O Telegram é armazenamento, não interface.** A navegação é sempre a interface web.
2. **Upload manual é o caminho padrão.** Menos automação de conta, menos risco.
3. **O catálogo é local e reconstruível.** O banco é o índice; a legenda das mensagens é o manifesto portátil.
4. **Fronteira de risco explícita.** Pastas, favoritos, lixeira e metadados não tocam no Telegram. Só leitura, download, edição de legenda e exclusão tocam.
5. **Sem link público.** O acesso é autenticado; a exposição é feita por túnel.
6. **Simplicidade operacional.** Sem Docker, sem fila, sem multi-tenant, sem criptografia client-side no MVP.
7. **Nada é apagado sem confirmação.** Excluir move para a lixeira; esvaziar a lixeira é a única operação destrutiva no Telegram.

## Conceitos

| Conceito | Definição |
|---|---|
| **Canal** | Canal privado único do Telegram onde ficam as mensagens com arquivos. |
| **Catálogo** | Banco SQLite com a árvore virtual e os metadados. |
| **Árvore virtual** | Pastas e caminhos que existem apenas no catálogo, não no Telegram. |
| **Manifesto** | Legenda padronizada (`FD1`) gravada na mensagem, com os dados do arquivo. |
| **Inbox** | Pasta virtual “Para organizar”, destino inicial de arquivos sem manifesto. |
| **Referência Telegram** | Coordenadas da mensagem (`chat_id`, `message_id`, `document_id`, `access_hash`). |
| **Pipeline de mídia** | Etapa que decide entre reproduzir direto, remuxar ou transcodificar. |
| **Cache** | Cópias locais temporárias de mídia remuxada e de legendas extraídas. |
| **Lixeira** | Estado do catálogo que preserva o arquivo e o caminho de origem. |

## Fluxos principais

### Ingestão

1. O usuário envia o arquivo pelo app oficial do Telegram para o canal privado.
2. O app varre as mensagens novas e registra as coordenadas no catálogo.
3. Arquivos sem manifesto vão para o **Inbox**.
4. Ao organizar, o app grava o manifesto na legenda e move no catálogo.

### Navegação

1. O usuário entra com usuário e senha no visualizador.
2. A interface lista o conteúdo da pasta virtual a partir do catálogo.
3. Nenhum caminho do sistema operacional é exposto.

### Reprodução

1. O usuário abre um vídeo ou áudio.
2. O app verifica o formato: MP4 compatível toca direto; MKV é remuxado para MP4 com `faststart` em cache.
3. O player pede intervalos (`Range`) e o app responde do cache ou do Telegram.
4. Legendas embutidas ou avulsas são oferecidas como faixas.

### Exclusão

1. Excluir marca o arquivo como `lixeira` e guarda a pasta de origem.
2. Restaurar devolve ao caminho original (ou à raiz, se a pasta sumiu).
3. Esvaziar a lixeira apaga a mensagem no Telegram e remove o registro.

## Limites conhecidos

- **Telegram:** 2 GB por arquivo (4 GB com Premium); conta dedicada sujeita a limites de velocidade e às regras de uso.
- **Navegador:** não reproduz MKV nativamente; H.264 + AAC exige remux, não transcodificação.
- **Legendas ASS:** estilos e fontes embutidas exigem renderizador dedicado no navegador; a conversão para WebVTT perde a formatação.
- **Rede:** o computador precisa estar ligado; o túnel é decidido na fase 09.
- **Cloudflared:** o plano gratuito restringe uso intenso de banda e conteúdo não-HTML; streaming pesado pode sofrer throttling.

## Não objetivos

- Compartilhamento público por link.
- Busca full-text no conteúdo dos arquivos.
- Multi-usuário com cotas e escopos.
- Criptografia client-side.
- Aplicativos nativos.
- Edição de vídeo, transcodificação em massa ou organização automática por IA.
