# Fase 8 — Ingestão e duplicados

- **Status:** não iniciada
- **Depende de:** fases 2 e 7

## Objetivo

Fechar o ciclo de upload manual: arquivos enviados ao canal aparecem no Inbox,
são identificados, comparados por hash e organizados com segurança.

## Escopo

- Varredura manual e periódica.
- Detecção de mensagens novas e apagadas.
- Entrada automática no Inbox.
- Cálculo de `sha256` na primeira leitura ou por rotina.
- Detecção de duplicados por hash + tamanho.
- Fluxo de decisão: manter os dois, substituir, nova versão.
- Reconciliação entre catálogo e canal.
- Aviso de arquivo `missing`.
- Gravação do manifesto na importação.
- Indicador de progresso da varredura.
- Botão “varrer agora” no admin.

## Fora de escopo

- Upload pela interface web.
- Upload automatizado pela conta.
- Edição em lote.
- Deduplicação automática sem confirmação.

## Entregáveis

- [ ] Upload manual aparece no Inbox após varredura.
- [ ] Varredura é idempotente.
- [ ] Arquivo repetido gera aviso com as três opções.
- [ ] “Manter os dois” cria nome livre.
- [ ] “Substituir” manda o antigo para a lixeira.
- [ ] “Nova versão” mantém o histórico básico.
- [ ] Mensagem apagada no Telegram marca `missing`.
- [ ] Reconciliação corrige referências.
- [ ] Manifesto é gravado ao organizar.
- [ ] Varredura não baixa conteúdo.
- [ ] Progresso e erros são visíveis.

## Checklist

- [ ] Implementar varredura agendada/manual.
- [ ] Implementar hash.
- [ ] Implementar duplicados.
- [ ] Implementar reconciliação.
- [ ] Implementar UI de decisão.
- [ ] Implementar indicador de progresso.
- [ ] Testar cenários de falha.
- [ ] Documentar o fluxo de upload manual.

## Arquivos previstos

```text
src/services/ingest/scanner.py
src/services/ingest/hash.py
src/services/ingest/duplicates.py
src/services/ingest/reconcile.py
src/routes/api/ingest.py
src/templates/partials/duplicate-dialog.html
src/static/js/ingest.js
tests/ingest/test_scanner.py
tests/ingest/test_duplicates.py
```

## Testes

- Upload novo entra no Inbox.
- Varredura repetida não duplica.
- Hash igual detecta duplicado.
- Cada decisão de duplicado.
- Mensagem apagada.
- Referência expirada.
- Falha de manifesto.
- Varredura com Telegram offline.

## Critério de saída

O fluxo “enviar pelo Telegram → varrer → organizar” funciona de ponta a ponta,
com duplicados tratados explicitamente e nenhuma perda de arquivo. A
reconciliação mantém catálogo e canal alinhados.

## Riscos

- Hash de arquivos grandes consome tempo e I/O.
- Varredura periódica pode competir com streaming; agendar com cuidado.
- Duplicados podem ser muitos; a UI precisa ser clara.
- Arquivos sem manifesto de versões antigas.
