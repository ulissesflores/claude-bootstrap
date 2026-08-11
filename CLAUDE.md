# CLAUDE.md — instruções de operação dentro de `claude-bootstrap`

> Carregado automaticamente em toda sessão Claude Code dentro deste repo. Mantenha **≤60 linhas quando possível, máx ~140-150**. Se crescer além disso, quebre em `.claude/rules/<scope>*.md` path-scoped (padrão Anthropic Q2/2026).

---

## Estilo

- **Idioma**: EN é canônico na documentação publicada (`docs/`, `README.md`); PT-BR é espelho (`docs/pt-br/`, `README.pt-br.md`). Identifiers, comandos e tipos sempre em EN. `AGENTS.md`, este arquivo e o `CHANGELOG` seguem em PT-BR
- **Tom**: opinativo, direto, denso. Sem floreio. Sem perguntas vazias.
- **Output**: markdown válido GFM (Typora-friendly). Pipe tables, callouts `> [!NOTE]`, mermaid OK. Proibido box-drawing ASCII.
- **CLAUDE.md em qualquer arquivo**: ≤60 linhas quando possível, máx ~140-150. Se passar, quebrar.

---

## Princípios não-negociáveis

1. **Idempotente** — re-rodar bootstrap em projeto configurado não quebra
2. **Detectivo antes de prescritivo** — escaneia antes de perguntar
3. **Profile-based, não monolítico** — adicionar profile é zero-touch nos demais
4. **Documenta o porquê** — `docs/` cita fontes com URL
5. **Compatível com superpowers** — declara dependência, não duplica
6. **Zero alucinação em refs** — toda recomendação tem URL fonte validável

---

## Decisões travadas (não reabra)

| Tópico | Valor |
|---|---|
| Nome | `claude-bootstrap` |
| Posicionamento | Camada acima de `superpowers`, não compete |
| Linguagem do engine | Python 3.11+ (`questionary`, `jinja2`, `pyyaml`, `rich`) |
| Idioma | EN canônico em `docs/` e nos READMEs, PT-BR como espelho (invertido na F2, 2026-08-03); identifiers em EN |
| Licença | MIT |
| Alvo | Universal (`universal-software` default) + 5 profiles especializados |

---

## O que NÃO fazer aqui

- ❌ Embarcar cópia de `superpowers` — o projeto declara dependência e oferece install
- ❌ Commit, push, tag ou release sem aprovação explícita do operador
- ❌ Editar à mão as skills embarcadas em `claude_bootstrap/templates/profiles/*/skills/` — são cópias pinadas do upstream; sincronize com `scripts/verify-skill-provenance.py --sync`
- ❌ Versionar contexto pessoal ou institucional (paths de home, workspaces privados, códigos de disciplina) — `scripts/pii-scan.py` é o gate

---

## Workflow padrão

1. **Plan mode primeiro** quando o trabalho cruza 3+ arquivos ou tem múltiplas abordagens
2. **Verificar antes de declarar concluído** — o gate completo:
   ```bash
   uv run python -m pytest tests/ -q      # nunca `uv run pytest` (pega o Python do sistema)
   python3 scripts/verify-skill-provenance.py
   python3 scripts/pii-scan.py
   uv run cffconvert --validate
   ```
3. **Conventional Commits**: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`

---

## Herança de instruções globais

Este `CLAUDE.md` **NÃO duplica** instruções globais do usuário (`~/.claude/CLAUDE.md`), que já carregam em toda sessão. Aqui só vai o que é **específico deste repo**.

Em caso de conflito: regras deste repo prevalecem (escopo mais específico).

---

## Quando travar / pedir ajuda

- `docs/` aparenta contradição interna → pause e reporte
- Anthropic publicou feature nova depois da última validação registrada em [`docs/01-canonical-anthropic.md`](docs/01-canonical-anthropic.md) → valide via `WebFetch` em `code.claude.com/docs/en` e atualize o doc antes de seguir
- `superpowers` mudou estrutura significativa → reporte ao operador

---

## Próximo passo

Ver [`docs/00-overview.md`](docs/00-overview.md) para estado do projeto, arquitetura e o gate de publicação.
