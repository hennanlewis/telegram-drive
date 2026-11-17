# Lixeira, duplicados e versões

## Lixeira

### Ciclo de vida

```text
ativo ──excluir──► lixeira ──restaurar──► ativo
                     │
                     └──esvaziar──► excluído (Telegram + catálogo)
```

- Excluir grava `status = trashed`, `trashed_from_folder_id` e `trashed_at`.
- O arquivo continua disponível para preview enquanto está na lixeira.
- Restaurar usa a pasta de origem; se ela não existe, recria o caminho ou coloca
  na raiz, informando o usuário.
- Esvaziar a lixeira é irreversível e exige confirmação com a contagem de itens.

### Esvaziar

1. Para cada item, apagar a mensagem no Telegram.
2. Se a exclusão falhar, manter o item em `trashed` e registrar o erro.
3. Remover referências, legendas, favoritos e cache associado.
4. Remover o registro do arquivo.
5. Registrar a ação na auditoria.

Nunca apagar mensagens fora desse fluxo.

### Itens `missing`

- Se a mensagem já não existe no Telegram, o item pode ser removido do catálogo
  ao esvaziar a lixeira, sem chamada ao Telegram.
- Se o arquivo está `missing` e ativo, a interface mostra aviso e oferece mover
  para a lixeira.

## Duplicados

### Identidade

- `sha256` do conteúdo + tamanho.
- O hash é calculado na ingestão, quando o arquivo é baixado pela primeira vez,
  ou por rotina explícita.
- Arquivos ainda sem hash não são comparados.

### Fluxo ao detectar

1. Existe arquivo ativo com o mesmo hash.
2. A interface mostra os dois: nome, pasta, tamanho, data.
3. Opções:
   - **Manter os dois:** cria um novo registro com nome livre.
   - **Substituir:** o antigo vai para a lixeira, o novo assume o nome.
   - **Nova versão:** mesmo nome, `version + 1`, antigo marcado `is_current = false`.

Nunca sobrescrever sem escolha explícita.

## Versões

- Adiado como funcionalidade completa.
- O modelo já suporta `version` e `is_current`.
- No MVP, “nova versão” mantém os dois registros e mostra apenas a atual na
  navegação.
- Excluir uma versão segue o fluxo normal da lixeira.
- O histórico de versões fica para uma fase futura.

## Auditoria

Registrar:

- `trash`, `restore`, `delete`, `duplicate`, `version`;
- arquivo, pasta de origem, data e resultado;
- falha de exclusão no Telegram.

Não registrar conteúdo nem hash completo em log de texto livre.
