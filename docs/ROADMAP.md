# Roadmap

> Este arquivo é **apenas o índice das fases**. O detalhe de cada fase está em [`roadmap/`](roadmap/). O registro do que foi executado está em [`registros/`](registros/). Critérios de aceite em [`ACEITE-MVP.md`](ACEITE-MVP.md); decisões em [`decisoes/INDICE.md`](decisoes/INDICE.md); pendências em [`abertos/DECISOES.md`](abertos/DECISOES.md); risco do Telegram em [`arquitetura/TELEGRAM.md`](arquitetura/TELEGRAM.md).

## Como usar

- Cada fase é independente e testável. Só avance quando o critério de saída da fase anterior estiver atendido.
- A interface de cada módulo é construída junto com a fase do módulo; não existe uma fase única de interface no final.
- O status é atualizado com **uma linha** nesta tabela. O resto vai para o registro da fase.

## Status

Legenda: `não iniciada` · `em andamento` · `bloqueada` · `concluída`

| Fase | Objetivo | Status | Detalhe |
|---|---|---|---|
| 0 | Fundação, ambiente, testes e decisões operacionais | concluída | [fase-00](roadmap/fase-00-fundacao.md) |
| 1 | Modelo de dados, catálogo e migrations | não iniciada | [fase-01](roadmap/fase-01-modelo-de-dados.md) |
| 2 | Integração com o Telegram: conta, canal, varredura e leitura | não iniciada | [fase-02](roadmap/fase-02-integracao-telegram.md) |
| 3 | Navegação e listagem de pastas virtuais | não iniciada | [fase-03](roadmap/fase-03-navegacao-e-listagem.md) |
| 4 | Preview de imagem, PDF e texto; download | não iniciada | [fase-04](roadmap/fase-04-preview-e-download.md) |
| 5 | Pipeline de mídia: MKV, cache, streaming e seek | não iniciada | [fase-05](roadmap/fase-05-pipeline-de-midia.md) |
| 6 | Legendas: embutidas, avulsas e ASS com fontes | não iniciada | [fase-06](roadmap/fase-06-legendas.md) |
| 7 | Organização: mover, renomear, inbox e lixeira | não iniciada | [fase-07](roadmap/fase-07-organizacao-e-lixeira.md) |
| 8 | Ingestão: varredura de uploads, duplicados e conciliação | não iniciada | [fase-08](roadmap/fase-08-ingestao-e-duplicados.md) |
| 9 | Operação, rede, backup e aceite final | não iniciada | [fase-09](roadmap/fase-09-operacao-e-rede.md) |

## Progresso atual

**Fase 0 concluída.** A fundação está executável e testada: dois processos, banco com migrations, health check e admin inicial. A próxima ação é iniciar a [Fase 1 — Modelo de dados](roadmap/fase-01-modelo-de-dados.md).

## Dependências

```text
0 → 1 → 2 → 3 → 4 → 5 → 6
                └──→ 7 → 8
                         └──→ 9
```

- A fase 6 depende da 5 (pipeline de mídia).
- A fase 7 depende da 1 e da 3 (catálogo e navegação).
- A fase 8 depende da 2 e da 7 (varredura e organização).
- A fase 9 depende de todas as anteriores.

## Definição de concluída

Uma fase só é concluída quando:

- todos os itens do checklist da fase estão marcados;
- os testes previstos passam;
- o critério de saída da fase está atendido;
- o registro da fase foi preenchido;
- a linha correspondente nesta tabela foi atualizada;
- nenhuma pendência nova ficou sem registro em `abertos/DECISOES.md`.
