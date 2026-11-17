# Princípios do projeto

1. **Documentação é a fonte única.** Código não decide escopo. Divergência vira pendência em `docs/abertos/DECISOES.md`.
2. **Simplicidade primeiro.** Sem Docker, sem fila, sem multi-tenant, sem ORM, sem framework frontend enquanto o problema não exigir.
3. **O Telegram é armazenamento, não interface.** A navegação é sempre a web.
4. **Fronteira de risco explícita.** Prefira operações locais; escreva no Telegram só quando necessário.
5. **Nada é perdido por acidente.** Lixeira antes de exclusão; catálogo reconstruível; manifesto na legenda.
6. **Recuperabilidade.** O banco pode ser perdido e reconstruído a partir do canal. O canal não é alterado em massa.
7. **Sem link público.** Acesso sempre autenticado.
8. **Portabilidade.** O repositório é independente; `legacy/` é referência, não dependência.
9. **Honestidade documental.** Não descrever como pronto o que não foi implementado.
10. **Uma fase por vez.** Não misturar escopo de fases.
11. **Testes desde a fundação.** Toda regra de negócio tem teste.
12. **Interface herdada, comportamento novo.** Manter a identidade visual sem herdar as limitações da API antiga.
