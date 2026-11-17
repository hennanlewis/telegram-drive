# Segurança

## Modelo de ameaça

O cenário é um computador pessoal rodando o serviço, exposto por um túnel para acesso remoto autenticado. O que precisa ser protegido:

1. O acervo no canal privado do Telegram.
2. A conta dedicada do Telegram (sessão e credenciais).
3. O catálogo local e o banco.
4. O acesso administrativo.
5. A rede local e o computador.

O que **não** existe no modelo: compartilhamento público, cadastro aberto, multi-tenant, API pública.

## Isolamento de administração

O legado já documentava o motivo: ao usar um túnel, todas as requisições chegam ao Flask vindas de `127.0.0.1`. Qualquer decisão de privilégio baseada em `request.remote_addr` seria uma falha grave.

Por isso o novo projeto mantém **dois processos**:

| Processo | Bind | Conteúdo | Exposto ao túnel? |
|---|---|---|---|
| `app_admin` | `127.0.0.1:8081` | configuração, usuários, diagnóstico, varredura | **nunca** |
| `app_viewer` | `127.0.0.1:8080` | login, navegação, preview, player, organização | sim |

Consequências obrigatórias:

- O processo viewer **não registra** rotas administrativas.
- O processo admin **não** confia em cabeçalhos de proxy para autorização.
- O túnel aponta somente para a porta do viewer.
- O admin exige login próprio, além de estar em loopback.
- Em produção, o viewer pode escutar em `0.0.0.0` apenas se o firewall/túnel restringir o acesso; o padrão é `127.0.0.1`.

## Autenticação

- Usuário e senha, sem cadastro público.
- Hash com `werkzeug.security.generate_password_hash` (scrypt/PBKDF2), nunca SHA-256 puro. O legado já usava Werkzeug; a documentação antiga estava errada.
- Comparação com `check_password_hash`.
- Mensagem de erro genérica.
- Bloqueio temporário após N tentativas por usuário e por IP.
- Primeiro usuário criado por script/seed local, não pela interface pública.
- Sessão com cookie `HttpOnly`, `SameSite=Lax` e `Secure` quando servido por HTTPS.
- Timeout de inatividade (padrão 60 minutos) e logout que limpa a sessão.
- Segredos de sessão distintos para admin e viewer.

## Autorização

Papéis e permissões estão em [`../domain/acesso.md`](../domain/acesso.md).

Regras:

- Toda rota verifica sessão e permissão **no servidor**.
- A interface apenas esconde o que o usuário não pode fazer; nunca é a única barreira.
- O usuário não escolhe o próprio papel.
- O viewer não tem rota para criar/editar usuários.
- Ações destrutivas exigem confirmação explícita.
- O `app_admin` valida o papel `admin` mesmo estando em localhost.

## CSRF e sessão

- Formulários e ações de escrita usam token CSRF ou cabeçalho customizado verificado no servidor.
- `SameSite=Lax` reduz o risco, mas não substitui a verificação.
- Requisições de leitura não alteram estado.
- O logout é `POST` ou tem proteção equivalente; um `GET` não deve ser usado para ação destrutiva.

## Caminhos e arquivos

- O cliente nunca envia caminho do sistema operacional.
- Toda operação usa ID de pasta/arquivo do catálogo.
- Nomes são normalizados e validados; não podem conter separadores de caminho.
- O legado usava `resolve_virtual_path` para bloquear `../`; no novo projeto isso vira defesa em profundidade, não o mecanismo principal.
- Downloads usam `Content-Disposition: attachment; filename="..."` com nome sanitizado.
- O tipo servido vem do catálogo, não do cliente.
- Texto tem limite de tamanho para evitar consumo excessivo de memória.

## Telegram

- `api_id`, `api_hash` e arquivo de sessão apenas em variáveis de ambiente ou arquivo local ignorado pelo Git.
- O arquivo de sessão tem permissão restrita no sistema operacional.
- Logs nunca imprimem credenciais, sessão, conteúdo de mensagem ou caminho do arquivo de sessão.
- A conta é dedicada; não é a conta pessoal principal.
- O canal é privado e não tem link divulgado.
- Escritas no Telegram são limitadas a: manifesto, correção de manifesto e exclusão ao esvaziar a lixeira.
- Upload em massa e encaminhamento automatizado são proibidos no MVP.

## Túnel e rede

- Cloudflared/Tailscale é decidido na fase 9.
- O túnel nunca aponta para a porta administrativa.
- Cabeçalhos `X-Forwarded-*` só são confiados quando a origem é o túnel local.
- Não usar IP de origem para decisão de privilégio.
- HTTPS é obrigatório fora da máquina local.
- Nenhum link público de compartilhamento de arquivo é gerado.

## Mídia

- O pipeline aceita apenas arquivos do catálogo.
- Parâmetros de `Range` são validados (início, fim, tamanho).
- O cache fica fora da árvore servida estaticamente.
- Nomes de cache são derivados de hash, não do nome enviado pelo usuário.
- ffmpeg é executado com argumentos fixos, sem shell, para evitar injeção.
- Erros de ffmpeg não expõem caminhos internos na resposta ao cliente.

## Logs e auditoria

Registrar:

- login bem-sucedido e falho (sem senha);
- bloqueio por tentativas;
- varredura do canal (início, fim, quantidade);
- organização, renomeação, lixeira e restauração;
- esvaziamento da lixeira;
- falhas de Telegram, ffmpeg e cache.

Não registrar:

- senhas, hashes de senha, tokens, `api_hash`, sessão;
- conteúdo de arquivos;
- URLs completas com parâmetros sensíveis.

## Dependências e atualização

- Dependências fixadas em `uv.lock`.
- ffmpeg/ffprobe com versão mínima documentada.
- Atualizações avaliadas antes de aplicar; sem auto-update no MVP.
- Nenhuma dependência nova sem justificativa na fase.

## Checklist mínimo antes de expor

- [ ] Admin só em `127.0.0.1`.
- [ ] Login do viewer funcionando e com rate limit.
- [ ] Senhas com hash forte.
- [ ] Sessão com timeout, `HttpOnly` e `SameSite`.
- [ ] CSRF nas ações de escrita.
- [ ] Nenhuma rota administrativa no viewer.
- [ ] Segredos fora do repositório.
- [ ] Túnel apontando só para o viewer.
- [ ] Logs sem segredos.
- [ ] Backup do banco testado.
