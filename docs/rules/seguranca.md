# Regras de segurança

Checklist normativo. O modelo completo está em [`../arquitetura/SEGURANCA.md`](../arquitetura/SEGURANCA.md).

## Acesso

- [ ] Admin escuta apenas em `127.0.0.1`.
- [ ] Admin exige login, mesmo em localhost.
- [ ] Viewer nunca registra rotas administrativas.
- [ ] Túnel aponta somente para o viewer.
- [ ] Toda rota verifica sessão e permissão no servidor.
- [ ] Nenhum cadastro público.
- [ ] Primeiro admin criado por script local.

## Credenciais

- [ ] Senhas com `generate_password_hash` (scrypt/PBKDF2), nunca SHA-256 puro.
- [ ] Comparação com `check_password_hash`.
- [ ] Rate limit e bloqueio temporário.
- [ ] Sessão com timeout, `HttpOnly`, `SameSite=Lax` e `Secure` sob HTTPS.
- [ ] Segredos distintos para admin e viewer.
- [ ] `api_id`, `api_hash` e sessão do Telethon fora do Git.
- [ ] Logs sem senha, hash, token, sessão ou conteúdo de mensagem.

## Requisições

- [ ] CSRF em toda ação de escrita.
- [ ] Nenhuma decisão de privilégio baseada em IP ou `X-Forwarded-For`.
- [ ] IDs validados como UUID/inteiro; sem caminho do cliente.
- [ ] `Range` validado.
- [ ] Nome de download sanitizado.
- [ ] Erros sem stack trace para o cliente.

## Filesystem e mídia

- [ ] Nenhuma operação usa caminho absoluto vindo do cliente.
- [ ] Cache fora da árvore estática.
- [ ] Nome de cache derivado de hash.
- [ ] ffmpeg sem `shell=True`.
- [ ] Texto limitado por tamanho antes de carregar.

## Telegram

- [ ] Conta dedicada.
- [ ] Canal privado.
- [ ] Escritas limitadas a manifesto e exclusão da lixeira.
- [ ] Sem upload automatizado em massa.
- [ ] `file_reference` resolvida na leitura.
- [ ] Falha de exclusão não perde o registro.

## Operação

- [ ] Backup do banco testado.
- [ ] Health check separado para app, banco e Telegram.
- [ ] Dependências fixadas.
- [ ] Logs com rotação.
- [ ] Nenhum link público de arquivo.
