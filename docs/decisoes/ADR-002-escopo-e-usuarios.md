# ADR-002 — Escopo single-user e MVP

## Status

Aceita.

## Contexto

O uso é pessoal. Multiusuário traria cotas, escopo por usuário, convites, administração de contas e isolamento de acervo — custo alto para um benefício inexistente no curto prazo.

## Decisão

- **Single-user** no MVP, com login próprio.
- O modelo de dados já prevê `owner_id` e papéis, sem implementar multi-tenant.
- O acesso remoto é autenticado, por túnel; não há link público.
- O escopo do MVP é:

**Entra:**

- login, logout e sessão;
- árvore de pastas virtuais;
- listagem e breadcrumb;
- preview de imagem, PDF e texto;
- download;
- reprodução de vídeo/áudio com seek;
- legendas embutidas e avulsas;
- organização: mover, renomear, Inbox;
- lixeira com restauração e esvaziamento;
- aviso de duplicado;
- varredura de uploads manuais;
- metadados básicos.

**Fica fora:**

- compartilhamento público por link;
- busca full-text;
- criptografia client-side;
- aplicativos nativos;
- multiusuário com cotas;
- versionamento completo;
- divisão de arquivos;
- transcodificação em massa.

## Consequências

- Menos casos de borda de autorização.
- A interface pode assumir um único acervo.
- Um segundo usuário exigirá refatoração de escopo, mas não de schema.
- O aceite é focado em uma pessoa usando o sistema de ponta a ponta.

## Relacionados

- [`../ACEITE-MVP.md`](../ACEITE-MVP.md)
- [`../visao-geral.md`](../visao-geral.md)
- [`../domain/acesso.md`](../domain/acesso.md)
