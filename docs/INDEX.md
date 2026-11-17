# Índice da documentação

Este índice é o **roteador** do projeto. Leia apenas o que a sua tarefa pede.

## Por tarefa

| Se você quer... | Leia |
|---|---|
| Entender o produto e os conceitos | [`visao-geral.md`](visao-geral.md) |
| Saber o que implementar agora | [`ROADMAP.md`](ROADMAP.md) e a fase correspondente em [`roadmap/`](roadmap/) |
| Entender as decisões fechadas | [`decisoes/INDICE.md`](decisoes/INDICE.md) |
| Resolver uma pendência | [`abertos/DECISOES.md`](abertos/DECISOES.md) |
| Integrar com o Telegram | [`arquitetura/TELEGRAM.md`](arquitetura/TELEGRAM.md) |
| Mexer em pastas, arquivos, lixeira ou duplicados | [`domain/arquivos-e-pastas.md`](domain/arquivos-e-pastas.md), [`domain/lixeira-e-duplicados.md`](domain/lixeira-e-duplicados.md) |
| Mexer em streaming, MKV ou cache | [`arquitetura/MIDIA.md`](arquitetura/MIDIA.md) |
| Mexer em legendas | [`domain/midia-e-legendas.md`](domain/midia-e-legendas.md) |
| Entender o banco e o manifesto | [`arquitetura/DADOS.md`](arquitetura/DADOS.md) |
| Ver a arquitetura geral | [`arquitetura/VISAO.md`](arquitetura/VISAO.md) |
| Saber o que veio do projeto anterior | [`arquitetura/REAPROVEITAMENTO.md`](arquitetura/REAPROVEITAMENTO.md) |
| Mexer na interface ou no visual | [`arquitetura/INTERFACE.md`](arquitetura/INTERFACE.md) |
| Revisar o modelo de segurança | [`arquitetura/SEGURANCA.md`](arquitetura/SEGURANCA.md) |
| Entender login, papéis e permissões | [`domain/acesso.md`](domain/acesso.md) |
| Codificar | [`rules/tecnicas.md`](rules/tecnicas.md) |
| Escrever testes | [`rules/testes.md`](rules/testes.md) |
| Revisar segurança | [`rules/seguranca.md`](rules/seguranca.md) |
| Conferir critérios de aceite | [`ACEITE-MVP.md`](ACEITE-MVP.md) |
| Registrar a execução de uma fase | [`registros/README.md`](registros/README.md) |

## Ordem de leitura para um agente novo

1. [`../AGENTS.md`](../AGENTS.md)
2. Este índice
3. [`visao-geral.md`](visao-geral.md)
4. A fase atual em [`roadmap/`](roadmap/)
5. A regra ou arquitetura citada pela fase
6. [`abertos/DECISOES.md`](abertos/DECISOES.md) se a fase tiver pendência

## Mapa da pasta

```text
docs/
├── INDEX.md                  # este arquivo
├── visao-geral.md            # produto, conceitos, limites
├── ROADMAP.md                # índice de fases e status
├── ACEITE-MVP.md             # critérios de aceite
├── arquitetura/
│   ├── VISAO.md              # componentes, processos, fluxos
│   ├── TELEGRAM.md           # conta, canal, limites, risco
│   ├── DADOS.md              # catálogo, manifesto, reconstrução
│   ├── MIDIA.md              # codecs, remux, cache, legendas
│   ├── INTERFACE.md          # identidade visual e componentes
│   ├── SEGURANCA.md          # modelo de segurança
│   └── REAPROVEITAMENTO.md   # o que veio do projeto anterior
├── decisoes/
│   ├── INDICE.md             # mapa D1..D18 → ADR
│   └── ADR-*.md
├── abertos/
│   └── DECISOES.md           # pendências numeradas
├── roadmap/
│   └── fase-00..fase-09.md
├── domain/
│   ├── acesso.md             # papéis e permissões
│   ├── arquivos-e-pastas.md
│   ├── lixeira-e-duplicados.md
│   └── midia-e-legendas.md
├── rules/
│   ├── principios.md
│   ├── tecnicas.md
│   ├── testes.md
│   └── seguranca.md
└── registros/
    ├── README.md
    └── _TEMPLATE.md
```

## Regra de ouro

Nenhum documento deve ser lido por inteiro sem necessidade. Se um arquivo passar de ~3k tokens, ele deve ser dividido por **responsabilidade**, não por tamanho.
