# ADR-007 — Exposição, rede e operação

## Status

Aceita, com decisão de túnel adiada para a fase 9.

## Contexto

O acesso será remoto, a partir de um computador pessoal ligado em casa. É preciso expor o viewer sem abrir portas no roteador e sem expor a administração. A escolha entre Cloudflared e Tailscale depende de um teste real de streaming e das restrições de cada serviço.

## Decisão

- O **admin nunca é exposto**; escuta apenas em `127.0.0.1`.
- O **viewer** é o único alvo do túnel.
- Não existe link público de compartilhamento de arquivo.
- O modo de túnel (`TUNNEL_MODE`) é configuração, não código:
  - `none` — uso local;
  - `cloudflared` — link público autenticado;
  - `tailscale` — acesso privado por tailnet.
- A decisão final entre Cloudflared e Tailscale fica para a **fase 9**, após medir streaming, latência e aderência aos termos.
- A aplicação deve funcionar plenamente em `localhost`, sem depender do túnel.
- Backup do banco, health check e limpeza de cache são parte da operação.

## Alternativas consideradas

| Alternativa | Observação |
|---|---|
| Cloudflared | Link acessível sem instalar cliente; plano gratuito restringe banda/conteúdo não-HTML |
| Tailscale | Privado, melhor para vídeo, exige cliente em cada dispositivo |
| Port forwarding + TLS | Abre porta no roteador e exige certificado |
| ngrok | Limites de plano e link público |
| Nenhum | Não atende ao acesso fora de casa |

## Consequências

- O código não depende da escolha; só a configuração e a documentação mudam.
- Cabeçalhos de proxy precisam ser tratados com cuidado.
- O aceite final inclui acesso remoto funcionando pelo modo escolhido.
- O risco de throttling do Cloudflared fica registrado desde já.

## Relacionados

- [`../arquitetura/SEGURANCA.md`](../arquitetura/SEGURANCA.md)
- [`../roadmap/fase-09-operacao-e-rede.md`](../roadmap/fase-09-operacao-e-rede.md)
- [`../abertos/DECISOES.md`](../abertos/DECISOES.md)
