# AGENTS.md — mapa para Claude entrando neste repo

> Você é um agente Claude (Code, Opus, Sonnet ou outro) abrindo `claude-bootstrap` pela primeira vez. Este arquivo te orienta. Leia em ordem e não pule.

---

## Estado atual do repo

`v1.0.0` — engine completo (`claude_bootstrap/` + wrapper `bin/bootstrap.sh`), 6 profiles com skills reais e provenance pinada, monorepo multi-profile, CI verde.

**Profiles** (skills embarcadas por profile):

| Profile | Skills | Origem |
|---|---|---|
| `universal-software` | 5 | first-party (escritas aqui, MIT) |
| `academic` | 3 | K-Dense 3 |
| `frontend` | 7 | Anthropic 3 + alirezarezvani 4 |
| `data-science` | 6 | alirezarezvani 6 |
| `devops` | 5 | alirezarezvani 5 |
| `backend` | 4 | alirezarezvani 4 |

Total embarcado: **30 skills**, todas com `NOTICE.md` de provenance. As 25 vendored têm commit-pin em [`scripts/skill-pins.json`](scripts/skill-pins.json); as 5 first-party de `universal-software` não têm upstream a fixar e são reportadas como `FIRST-PARTY`. O **registry** ([`claude_bootstrap/registry/skills.yaml`](claude_bootstrap/registry/skills.yaml)) é um catálogo separado de **13 skills** instaláveis individualmente.

Raiz `claude-bootstrap/`:

- `README.md` — entrypoint humano (+ `.pt-br` / `.es` / `.it` / `.he`)
- `AGENTS.md` — você está aqui
- `CLAUDE.md` — instruções de operação dentro deste repo
- `CONTRIBUTING.md`
- `llms.txt` — ponteiros otimizados LLM
- `LICENSE` — MIT
- `CITATION.cff`
- `CHANGELOG.md`
- `RELEASE.md` — checklist de release
- `bin/bootstrap.sh` — wrapper shell
- `claude_bootstrap/` — engine Python (detect / interview / install / doctor / skill)
  - `registry/skills.yaml` — catálogo curado (13 skills)
  - `templates/` — `_base/` + `profiles/<name>/`
- `scripts/` — gates: provenance, PII, schema-currency, refs
- `tests/`
- `docs/` — documentação Diátaxis (00-08)

---

## Ordem de leitura obrigatória

1. **[`docs/00-overview.md`](docs/00-overview.md)** — o que é, por que existe, arquitetura
2. **[`CLAUDE.md`](CLAUDE.md)** — restrições e estilo deste repo (leitura rápida)
3. **[`docs/05-profiles.md`](docs/05-profiles.md)** — anatomia dos profiles e como adicionar um
4. **[`docs/01-canonical-anthropic.md`](docs/01-canonical-anthropic.md)** — referência canônica Anthropic
5. **[`docs/02-state-of-the-art.md`](docs/02-state-of-the-art.md)** — quando comparar com prática de mercado
6. **[`docs/07-glossary.md`](docs/07-glossary.md)** — em caso de dúvida terminológica

---

## O que NÃO fazer

- ❌ Duplicar `superpowers` — o projeto declara dependência, não embarca cópia
- ❌ Editar à mão as skills em `claude_bootstrap/templates/profiles/*/skills/` — são cópias pinadas do upstream
- ❌ Versionar contexto pessoal ou institucional — `scripts/pii-scan.py` reprova o commit
- ❌ Fazer commit, push, tag ou release sem aprovação explícita do operador

---

## Quando fazer o quê

| Situação | Ação |
|---|---|
| Doc canônico (`docs/01-`) parece desatualizado | `WebFetch` em `code.claude.com/docs/en` + abre PR de update; não edita silente |
| Precisa entender termo técnico | `docs/07-glossary.md` primeiro, depois Anthropic docs |
| Trabalho cruza múltiplos arquivos | Plan mode antes de escrever |
| Vai declarar algo "feito" | Rode o gate completo do [`CLAUDE.md`](CLAUDE.md) §Workflow padrão |

---

## Publicação

O repo é **público desde 2026-08-11** (v1.0.0). Push, tag, release e publicação em índice continuam exigindo autorização explícita do operador — o flip não mudou essa regra.
