# Fase 2 — Integração com o Telegram

- **Status:** não iniciada
- **Depende de:** fase 1

## Objetivo

Conectar a conta dedicada ao canal privado, varrer mensagens, registrar
referências e ler bytes com suporte a offset — sem interface.

## Escopo

- Configuração de `api_id`, `api_hash`, sessão e canal.
- Validação da sessão e do acesso ao canal.
- Cliente encapsulado em `services/telegram/`.
- Varredura incremental e idempotente.
- Extração de metadados de documentos.
- Resolução de `file_reference` na leitura.
- Leitura de bytes por offset/limite.
- Tratamento de `FloodWait`, timeout e mensagem ausente.
- Modo de teste com cliente falso.
- Comando de diagnóstico no admin (sem interface completa).

## Fora de escopo

- Upload automatizado.
- UI de navegação.
- Pipeline de mídia.
- Legendas.

## Entregáveis

- [ ] O app valida a sessão e o canal no início.
- [ ] A varredura registra mensagens novas no catálogo.
- [ ] Rodar a varredura duas vezes não duplica registros.
- [ ] Documentos sem manifesto entram no Inbox.
- [ ] Metadados (tamanho, MIME, duração) são preenchidos quando disponíveis.
- [ ] Referência expirada é recoletada.
- [ ] Mensagem ausente marca `missing`.
- [ ] Leitura por offset funciona para arquivos de teste.
- [ ] Testes não usam rede.

## Checklist

- [ ] Implementar cliente e fábrica.
- [ ] Implementar validação de canal.
- [ ] Implementar varredura e estado.
- [ ] Implementar resolução de referência.
- [ ] Implementar leitura por offset.
- [ ] Implementar retry/backoff.
- [ ] Implementar cliente falso de teste.
- [ ] Documentar configuração da conta e do canal.

## Arquivos previstos

```text
src/services/telegram/client.py
src/services/telegram/scanner.py
src/services/telegram/references.py
src/services/telegram/reader.py
src/services/telegram/errors.py
tests/fakes/telegram.py
tests/services/test_scanner.py
tests/services/test_reader.py
scripts/telegram_check.py
```

## Testes

- Canal configurado e acessível.
- Canal inválido gera erro claro.
- Varredura inicial e incremental.
- Idempotência.
- `FloodWait` simulado com retry.
- Referência expirada recoletada.
- Mensagem apagada marca `missing`.
- Leitura de intervalo de bytes.

## Critério de saída

Dado um canal de teste com documentos, a varredura popula o catálogo e a leitura
por offset retorna os bytes corretos. Nenhum teste depende de rede ou de
credencial real.

## Riscos

- Sessão do Telethon no Windows: permissões e caminho.
- Limites de velocidade: medir e registrar.
- Referências voláteis: nunca assumir estabilidade.
- Conta bloqueada: mensagem clara e sem perda de catálogo.
