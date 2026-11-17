# Decisões em aberto

Pendências numeradas. Cada item indica a fase que o fecha e a recomendação atual.
Ao resolver, registre um ADR (se for estrutural) ou atualize a fase (se for
operacional) e remova o item daqui.

| ID | Pendência | Fase | Recomendação |
|---|---|---|---|
| A1 | Cloudflared ou Tailscale | 9 | Testar Tailscale primeiro (melhor para vídeo); Cloudflared como alternativa de link |
| A2 | Tamanho e retenção do cache | 5 | 20 GB e 7 dias, configuráveis |
| A3 | Limite de preview de texto | 4 | 1 MB; acima disso, download |
| A4 | Biblioteca de renderização ASS no navegador | 6 | JASSUB ou SubtitlesOctopus, com fallback WebVTT |
| A5 | Política padrão para duplicados | 8 | Perguntar sempre; nunca sobrescrever |
| A6 | Tratamento de HEVC | 5 | Transcodificar sob demanda com aviso; se inviável, recusar com explicação |
| A7 | Retenção de backup do banco | 9 | 7 diários + 4 semanais |
| A8 | Como criar o primeiro admin | 0 | Script de linha de comando, senha digitada na hora |
| A9 | Idioma padrão de legenda | 6 | `pt-BR`, depois `pt`, depois a primeira faixa |
| A10 | Comportamento com Telegram offline | 9 | Catálogo em somente leitura; player informa indisponibilidade |
| A11 | Ordem de pastas e arquivos | 3 | Pastas primeiro, depois arquivos; nome ascendente |
| A12 | Nome definitivo do projeto/repositório | antes do GitHub | “Telegram Drive” é provisório |
| A13 | Retenção de logs | 9 | 30 dias, rotação por tamanho |
| A14 | Limite de concorrência de downloads | 5 | 1 por arquivo; 2 no total |
| A15 | Expiração da sessão do viewer | 0 | 60 minutos de inatividade |

## Regras

- Uma pendência bloqueia apenas a fase indicada, não o projeto inteiro.
- Se a fase começar sem a decisão, o agente deve propor a recomendação e
  registrar no ADR correspondente.
- Pendência que muda arquitetura exige ADR; pendência operacional pode ser
  registrada na fase.
