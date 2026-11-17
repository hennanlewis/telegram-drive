# Regras de teste

## Ferramentas

- `pytest`.
- Banco temporário por teste, criado do zero com as migrations.
- Cliente Telegram falso para testes de serviço.
- Fixtures pequenas de mídia para ffmpeg.
- Nenhum teste acessa o Telegram real.

## Pirâmide

| Nível | O que cobre |
|---|---|
| Unidade | regras puras: nomes, caminhos, estados, manifesto, matching de legenda |
| Serviço | catálogo, lixeira, duplicados, varredura, pipeline de decisão |
| Repositório | SQL, constraints, migrations, consultas recursivas |
| Integração | rotas, sessão, autorização, streaming com `Range` |
| Aceite | roteiro manual no fim de cada fase |

## Obrigatório por área

- **Migrations:** aplicar do zero e conferir constraints.
- **Catálogo:** criar/mover/renomear, unicidade por pasta, prevenção de ciclo.
- **Manifesto:** serializar, parsear, tolerar inválido, reconstruir.
- **Lixeira:** excluir, restaurar, esvaziar, falha de Telegram.
- **Duplicados:** mesmo hash, decisão, versão.
- **Telegram:** scan idempotente, referência expirada, `FloodWait`, mensagem
  ausente.
- **Mídia:** decisão por perfil, cache hit/miss, range inválido, ffmpeg ausente.
- **Legendas:** embutida, avulsa, múltiplos idiomas, ASS, fallback.
- **Segurança:** rota sem sessão, papel insuficiente, CSRF, admin não exposto.

## Regras

- Teste não depende de ordem de execução.
- Teste não usa rede.
- Teste não dorme; simula tempo.
- Teste de banco sempre limpa o estado.
- Dados sensíveis de teste são fictícios.
- Um bug corrigido ganha teste de regressão.
- Nome do teste descreve o comportamento, não a implementação.

## Comandos previstos

```bash
uv run pytest
uv run pytest -k "manifesto"
uv run pytest tests/db
```

Os comandos definitivos são fixados na fase 0.

## Critério

Uma fase não é concluída com teste vermelho, teste ignorado sem justificativa ou
teste que só passa localmente por estado residual.
