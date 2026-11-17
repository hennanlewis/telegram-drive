# Acesso, usuários e permissões

## Modelo

O MVP é **single-user**, mas o modelo de papéis existe para permitir um segundo
usuário sem refatoração.

| Papel | Onde atua | Pode |
|---|---|---|
| `admin` | `app_admin` | configurar canal, gerenciar usuários, diagnosticar, varrer |
| `editor` | `app_viewer` | navegar, visualizar, baixar, organizar, renomear, mover, lixeira |
| `viewer` | `app_viewer` | navegar, visualizar, baixar |

O usuário principal do MVP acumula `admin` + `editor`. Não há cadastro público.

## Matriz de permissões

| Ação | viewer | editor | admin |
|---|---|---|---|
| Entrar no viewer | sim | sim | sim |
| Listar pastas e arquivos | sim | sim | sim |
| Preview de imagem/PDF/texto | sim | sim | sim |
| Reproduzir mídia | sim | sim | sim |
| Baixar arquivo | sim | sim | sim |
| Criar/renomear/mover pasta | não | sim | sim |
| Renomear/mover arquivo | não | sim | sim |
| Enviar para a lixeira | não | sim | sim |
| Restaurar da lixeira | não | sim | sim |
| Esvaziar a lixeira | não | sim | sim |
| Favoritar | sim | sim | sim |
| Ver metadados | sim | sim | sim |
| Ver o Inbox | sim | sim | sim |
| Organizar o Inbox | não | sim | sim |
| Acessar o admin | não | não | sim |
| Gerenciar usuários | não | não | sim |
| Configurar o canal | não | não | sim |
| Disparar varredura | não | não | sim |

## Sessão

- Criada no login do viewer; separada da sessão do admin.
- Cookie `HttpOnly`, `SameSite=Lax`, `Secure` sob HTTPS.
- Timeout de inatividade: 60 minutos (configurável).
- Logout limpa a sessão e redireciona para o login.
- Sessão do admin expira mais rápido por padrão (30 minutos).

## Primeiro acesso

1. O banco é criado e migrado.
2. Um script local cria o primeiro `admin` com senha definida na hora.
3. O admin entra no `app_admin` em `127.0.0.1`.
4. O admin configura o canal, testa a conexão e cria o usuário do viewer, se
   quiser separar as credenciais.
5. Não existe tela de “criar primeira conta” acessível pela rede.

## Bloqueio por tentativas

- Limite padrão: 5 falhas por usuário em 15 minutos.
- Bloqueio temporário de 15 minutos; o contador zera no sucesso.
- A resposta é sempre genérica.
- O evento é registrado na auditoria, sem senha.

## Relação com a conta do Telegram

São identidades diferentes:

- **Usuário do app:** quem entra na interface web.
- **Conta do Telegram:** a conta dedicada que o servidor usa para ler o canal.

O usuário do app **nunca** recebe credenciais do Telegram. Ele só vê o catálogo.
A conta do Telegram é configuração do servidor, não um usuário do sistema.

## Regras

- O papel nunca vem do cliente.
- O usuário não altera o próprio papel.
- Desativar um usuário invalida a sessão na próxima requisição.
- Excluir usuário não apaga a auditoria.
- O admin não pode se autodesativar se for o único admin ativo.
- A senha nunca é exibida depois de criada.
- O viewer não tem rota de administração, mesmo que autenticado como admin.
