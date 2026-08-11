<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-dark.svg">
  <img src="docs/assets/logo-light.svg" alt="claude-bootstrap" width="430">
</picture>

### Detecta, scaffolda e reverte um setup completo do Claude Code — em um comando.

O `claude-bootstrap` inspeciona teu projeto, te diz **por que** escolheu um profile, mostra o plano, pergunta uma vez — e então emite uma árvore `.claude/` completa: baseline de permissões, skills curadas com **licença auditada** e rules path-scoped. Idempotente, com `--check` e um `uninstall` de verdade.

![status](https://img.shields.io/badge/status-stable-3fb950?style=flat-square)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21894809.svg)](https://doi.org/10.5281/zenodo.21894809)
![python](https://img.shields.io/badge/python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![license](https://img.shields.io/badge/license-MIT-3fb950?style=flat-square)
![tests](https://img.shields.io/badge/tests-271%2F271-3fb950?style=flat-square)
![skills](https://img.shields.io/badge/skills-30%20provenance--verified-7C5CFF?style=flat-square)

[Por quê](#por-que-existe) · [Instalar](#instalação) · [Início rápido](#início-rápido) · [Profiles](#profiles) · [O que você ganha](#o-que-você-ganha) · [Docs](docs/pt-br/) · [Contribuir](CONTRIBUTING.md)

<br/>

<img src="docs/assets/demo.gif" alt="claude-bootstrap init: detect → plan → emit → uninstall reversível" width="860">

🌐 [English](README.md) · [Português](README.pt-br.md) · [Español](README.es.md) · [Italiano](README.it.md) · [עברית](README.he.md)

</div>

> [!NOTE]
> **`v1.0.0` — primeiro release público (2026-08-11).** Instale a partir de um clone ou com `pip install git+https://github.com/ulissesflores/claude-bootstrap` ([Instalar](#instalação)). O nome no PyPI segue via release workflow.

---

## Por que existe

O Claude Code traz o próprio `/init` — e um setup interativo atrás de `CLAUDE_CODE_NEW_INIT=1` — que escreve um `CLAUDE.md`. O `claude-bootstrap` **não é substituto**; é complementar, e de propósito faz mais nos eixos que importam pra um setup reproduzível e auditável que você re-roda em vários repos:

| | `claude /init` nativo | `claude-bootstrap` |
|---|---|---|
| **Escreve** | `CLAUDE.md` (conversacional; explora teu código) | a árvore `.claude/` inteira a partir de um **profile detectado** |
| **Permissões** | **não** toca `settings.json` | emite um **baseline** allow/deny em `settings.json` |
| **Skills / rules** | — | bundles de skills com licença auditada e **proveniência verificada** + rules path-scoped |
| **Re-rodar** | por sessão | **idempotente**, com `--check`, `uninstall` completo, manifesto por arquivo |
| **Confiança** | — | mostra *por que* o profile foi escolhido, pergunta antes de escrever, todo artefato é podável |

Use o `/init` nativo pra um `CLAUDE.md` conversacional rápido. Use o `claude-bootstrap` quando quiser um baseline `.claude/` **reproduzível, auditável e profile-based**. (Mais: [`docs/pt-br/02-state-of-the-art.md`](docs/pt-br/02-state-of-the-art.md) §7.2.)

---

## O que você ganha

- 🔎 **Detecta e explica.** Escaneia o projeto e imprime a *evidência* do profile que escolhe (ex.: `pyproject.toml found, torch in deps → data-science`) — nunca uma caixa-preta.
- ✋ **Confirma antes de escrever.** Mostra o plano via `--check`, pergunta `[y/N]`, não escreve nada se você recusar. Pulável com `--yes`/`--non-interactive` pra CI.
- 🧱 **Uma árvore `.claude/` de verdade.** `CLAUDE.md` (política ≤60 linhas), `PROJECT-STATE.md`, baseline de permissões em `settings.json`, skills do profile + rules path-scoped, e `CLAUDE.md` por subpasta onde a pasta tem papel próprio.
- ♻️ **Idempotente + reversível.** Re-rodar nunca atropela tuas edições (create-only; `<file>.new` no `update`). Um manifesto registra cada arquivo emitido, então `claude-bootstrap uninstall` reverte tudo — e **mantém qualquer arquivo que você editou**.
- 📦 **Skills com licença auditada e proveniência verificada.** 30 skills bundled nos profiles: 25 fixadas num commit upstream e **content-verified** (`scripts/verify-skill-provenance.py`; um job semanal de CI detecta drift), mais 5 skills **first-party**, escritas neste repositório sob a licença MIT dele. Toda skill bundled carrega uma licença de redistribuição que foi de fato lida — MIT ou Apache-2.0 — com o texto integral embarcado junto. Quatro skills da Anthropic foram **de-bundled em 2026-07-26** por não trazerem essa concessão; apontamos para o upstream em vez de redistribuí-las.
- 🧹 **Anti-bloat por design.** Tudo é Markdown/JSON legível que você pode ler, editar ou apagar — e o tool te diz como (`--check`, `skill remove`, `uninstall`).

---

## Instalação

> [!IMPORTANT]
> Ainda fora do PyPI — instale a partir de um clone:
>
> ```bash
> git clone https://github.com/ulissesflores/claude-bootstrap
> cd claude-bootstrap
> bin/bootstrap.sh init --profile=universal-software      # ou: uv run -m claude_bootstrap.cli init
> ```

O método curl já está live; `uv` / `pipx` / `pip` ativam quando o pacote chegar ao PyPI:

| Método | Comando |
|---|---|
| uv (recomendado) | `uv tool install claude-bootstrap` |
| pipx | `pipx install claude-bootstrap` |
| pip | `pip install claude-bootstrap` |
| curl | `curl -LsSf https://raw.githubusercontent.com/ulissesflores/claude-bootstrap/main/install.sh \| bash` |

Verificar: `claude-bootstrap version` → `v1.0.0` ou superior. Requer **Python 3.11+**.

---

## Início rápido

```bash
# 1. (opcional) ver que tipo de projeto é este — read-only
claude-bootstrap detect

# 2. scaffold: detect → rationale → plano → confirm → emit
claude-bootstrap init --profile data-science

# 3. health-check do install (13 checks)
claude-bootstrap doctor

# mudou de ideia? reverte o emit inteiro (mantém arquivos que você editou)
claude-bootstrap uninstall
```

> [!TIP]
> `claude-bootstrap init --check` imprime o plano completo de ações e não escreve nada — a forma mais segura de pré-visualizar.

---

## Profiles

Repos single-stack recebem um profile; **monorepos recebem a união dos code stacks detectados**. Adicionar um profile é zero-touch nos outros. Cada um bundla skills com proveniência por skill no seu `NOTICE.md`.

| Profile | Skills bundled | Upstream |
|---|---|---|
| `universal-software` | 5 | — (first-party, MIT) |
| `academic` | 3 | `K-Dense-AI/scientific-agent-skills` (MIT) |
| `data-science` | 6 | `alirezarezvani/claude-skills` (MIT) |
| `frontend` | 7 | `anthropics/skills` (Apache-2.0) + `alirezarezvani/claude-skills` (MIT) |
| `devops` | 5 | `alirezarezvani/claude-skills` (MIT) |
| `backend` | 4 | `alirezarezvani/claude-skills` (MIT) |

O `detect` varre sinais do filesystem (`*.tex` → academic, `torch`/`tensorflow` nas deps → data-science, `package.json`+`tsconfig` → frontend, um web framework → backend, `*.tf`/`Chart.yaml` → devops). Um **monorepo** com vários stacks em sub-projetos (ex.: `frontend/` + `backend/`) emite uma **união** num único `.claude/` root — permissões unidas + todas as skills + `rules/<stack>.md` path-scoped — mais um `<subdir>/CLAUDE.md` fino por sub-projeto. `academic` fica exclusivo (repo inteiro). Detalhes: [`docs/pt-br/05-profiles.md`](docs/pt-br/05-profiles.md).

<div align="center"><img src="docs/assets/detect.gif" alt="claude-bootstrap detect em quatro tipos de projeto" width="640"></div>

---

## O que é instalado

```
seu-projeto/
├── CLAUDE.md                      # instruções do projeto (política ≤60 linhas)
├── PROJECT-STATE.md               # estado curado (você edita; não é a auto-memory do Claude)
├── .gitignore                     # soft-merge com o teu
└── .claude/
    ├── settings.json              # permissões allow/deny + env (merge do profile)
    ├── skills/<name>/             # skills curadas, licença auditada
    ├── rules/<name>.md            # rules path-scoped
    └── .bootstrap-manifest.json   # registra o emit pra `uninstall` reverter com segurança
```

Todos os arquivos são **create-only**: re-rodar não sobrescreve tuas edições; `update` escreve `<file>.new` pra revisão. **É só arquivo — pode podar à vontade.**

---

## Distribuição

Além da CLI, cada profile curado também é empacotado como **plugin do Claude Code** via um [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) — então os bundles podem ser puxados com `/plugin install`.

---

## Docs

Organizadas por intenção — comece pela tua necessidade. Índice completo: [`docs/pt-br/`](docs/pt-br/).

| Você quer… | Leia |
|---|---|
| Entender arquitetura & fluxo | [`00-overview`](docs/pt-br/00-overview.md) · [`06-bootstrap-flow`](docs/pt-br/06-bootstrap-flow.md) |
| Bater com a spec atual do Claude Code | [`01-canonical-anthropic`](docs/pt-br/01-canonical-anthropic.md) · [`02-state-of-the-art`](docs/pt-br/02-state-of-the-art.md) |
| Evitar erros comuns | [`03-anti-patterns`](docs/pt-br/03-anti-patterns.md) |
| Trabalhar com skills & profiles | [`04-skills-curated`](docs/pt-br/04-skills-curated.md) · [`05-profiles`](docs/pt-br/05-profiles.md) |
| Buscar um termo / se destravar | [`07-glossary`](docs/pt-br/07-glossary.md) · [`08-faq`](docs/pt-br/08-faq.md) |

---

## Contribuir

Issues e PRs bem-vindos. O setup de dev é um comando (`uv sync`), commits seguem [Conventional Commits](https://www.conventionalcommits.org), e tudo passa por `pytest` + `pre-commit`. Veja [`CONTRIBUTING.md`](CONTRIBUTING.md) e o [`CODE_OF_CONDUCT.md`](.github/CODE_OF_CONDUCT.md).

---

## Licença

[MIT](LICENSE) © Carlos Ulisses Flores. As skills de terceiros bundled mantêm suas licenças upstream (MIT ou Apache-2.0) — veja o `NOTICE.md` de cada profile e o `LICENSE.txt` que acompanha cada diretório de skill. As skills first-party do `universal-software` são MIT sob a licença do próprio projeto. Construído uma camada acima do [`superpowers`](https://github.com/obra/superpowers); declara a dependência, nunca a duplica.
