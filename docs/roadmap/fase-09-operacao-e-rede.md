# Fase 9 — Operação, rede e aceite

- **Status:** não iniciada
- **Depende de:** todas as fases anteriores

## Objetivo

Colocar o sistema em uso real: iniciar com o computador, acessar de fora por túnel, fazer backup, monitorar e executar o aceite do MVP.

## Escopo

- Serviço local do Windows (iniciar/parar/reiniciar).
- Health check de aplicação, banco e Telegram.
- Backup do banco e teste de restauração.
- Limpeza de cache e rotação de logs.
- Decisão do túnel (A1): Cloudflared ou Tailscale.
- Configuração de HTTPS e cabeçalhos de proxy.
- Checklist de segurança completo.
- Execução do [`ACEITE-MVP.md`](../ACEITE-MVP.md).
- Atualização do README com operação real.
- Registro da fase.

## Fora de escopo

- Deploy em nuvem.
- Docker.
- Monitoramento com Prometheus/Grafana.
- Alta disponibilidade.

## Entregáveis

- [ ] Aplicação sobe automaticamente após reiniciar o Windows.
- [ ] Admin inacessível pelo túnel.
- [ ] Viewer acessível pelo modo de túnel escolhido.
- [ ] Streaming funciona pelo túnel em velocidade aceitável.
- [ ] Backup do banco é gerado e restaurado em teste.
- [ ] Cache é limpo e limitado.
- [ ] Logs rotacionam e não contêm segredos.
- [ ] Health check cobre app, banco e Telegram.
- [ ] Checklist de segurança completo.
- [ ] Aceite do MVP executado e registrado.

## Checklist

- [ ] Criar serviço do Windows.
- [ ] Implementar health check completo.
- [ ] Implementar backup e restauração.
- [ ] Implementar limpeza de cache e logs.
- [ ] Testar Cloudflared e/ou Tailscale.
- [ ] Documentar túnel escolhido.
- [ ] Revisar segurança.
- [ ] Executar roteiro de aceite.
- [ ] Preencher registro da fase.

## Arquivos previstos

```text
scripts/service-install.ps1
scripts/backup.ps1
scripts/restore.ps1
scripts/cache-clean.ps1
src/routes/api/health.py
docs/operacao/REDE.md
docs/registros/fase-09.md
```

## Testes

- Reinício do computador e retomada.
- Backup e restauração.
- Acesso remoto e local.
- Streaming remoto.
- Telegram offline.
- Cache cheio.
- Admin não acessível externamente.
- Aceite completo.

## Critério de saída

O MVP atende a todos os itens de [`ACEITE-MVP.md`](../ACEITE-MVP.md), com acesso remoto funcionando, backup testado e operação documentada. A decisão do túnel está registrada e justificada.

## Riscos

- Throttling do Cloudflared em vídeo.
- Tailscale exige cliente em cada dispositivo.
- Serviço do Windows e permissões de sessão do Telethon.
- Backup inconsistente se feito com o banco em escrita.
- Exposição acidental do admin.
