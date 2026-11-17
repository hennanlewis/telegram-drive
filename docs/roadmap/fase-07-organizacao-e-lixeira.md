# Fase 7 — Organização e lixeira

- **Status:** não iniciada
- **Depende de:** fases 1 e 3

## Objetivo

Permitir organizar o acervo pela interface: criar, renomear e mover pastas e
arquivos, organizar o Inbox, usar a lixeira e restaurar — com o manifesto
sincronizado.

## Escopo

- Criar, renomear e excluir pasta vazia.
- Mover arquivo e pasta.
- Renomear arquivo.
- Organizar item do Inbox.
- Menu de ações no cartão e no modal.
- Enviar para a lixeira, restaurar e esvaziar.
- Confirmação de exclusão definitiva.
- Gravação/atualização do manifesto na legenda.
- Estado “manifesto pendente” em caso de falha.
- Auditoria das ações.
- Atualização da UI sem recarregar a página.

## Fora de escopo

- Duplicados e versões (fase 8).
- Favoritos.
- Arrastar e soltar (pode ser melhoria futura).

## Entregáveis

- [ ] Criar pasta e navegar até ela.
- [ ] Renomear arquivo e pasta.
- [ ] Mover arquivo para outra pasta.
- [ ] Mover pasta sem criar ciclo.
- [ ] Bloquear exclusão de pasta com conteúdo.
- [ ] Mover item do Inbox para pasta.
- [ ] Lixeira lista, restaura e esvazia.
- [ ] Restaurar para pasta inexistente recria ou usa a raiz.
- [ ] Manifesto é atualizado após organizar.
- [ ] Falha de manifesto não perde o catálogo.
- [ ] Ações aparecem na auditoria.

## Checklist

- [ ] Implementar API de pastas e arquivos.
- [ ] Implementar lixeira.
- [ ] Implementar manifesto na organização.
- [ ] Implementar menu de ações.
- [ ] Implementar confirmações.
- [ ] Implementar estados de erro.
- [ ] Testar concorrência e ciclo.
- [ ] Revisar permissões.

## Arquivos previstos

```text
src/services/catalog/move.py
src/services/catalog/trash.py
src/services/catalog/manifest_sync.py
src/routes/api/files.py
src/routes/api/trash.py
src/static/js/actions.js
src/templates/partials/action-menu.html
tests/services/test_move.py
tests/services/test_trash.py
```

## Testes

- Movimentação simples e conflito de nome.
- Ciclo de pasta.
- Exclusão de pasta vazia e não vazia.
- Lixeira e restauração.
- Restauração com pasta removida.
- Esvaziar com sucesso e com falha.
- Manifesto atualizado e falha simulada.
- Permissão de viewer negada.

## Critério de saída

Todas as operações de organização funcionam pela interface, a lixeira protege
contra exclusão acidental e o manifesto reflete o catálogo. Nenhuma operação
apaga bytes fora do esvaziamento da lixeira.

## Riscos

- Concorrência entre varredura e organização.
- Atualização de legenda pode falhar; o estado pendente precisa ser visível.
- Mover muitos itens pode ser lento; operações são por item no MVP.
