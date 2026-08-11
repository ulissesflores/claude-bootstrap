<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-dark.svg">
  <img src="docs/assets/logo-light.svg" alt="claude-bootstrap" width="430">
</picture>

### Rileva, genera e annulla una configurazione completa di Claude Code — con un solo comando.

`claude-bootstrap` ispeziona il tuo progetto, ti spiega **perché** ha scelto un profilo, mostra il piano, chiede una volta — poi genera un albero `.claude/` completo: una baseline di permessi, skill curate e **verificate sotto il profilo della licenza**, e regole con ambito di percorso. Idempotente, con `--check` e una vera `uninstall`.

![status](https://img.shields.io/badge/status-stable-3fb950?style=flat-square)
![python](https://img.shields.io/badge/python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![license](https://img.shields.io/badge/license-MIT-3fb950?style=flat-square)
![tests](https://img.shields.io/badge/tests-271%2F271-3fb950?style=flat-square)
![skills](https://img.shields.io/badge/skills-30%20provenance--verified-7C5CFF?style=flat-square)

[Perché](#perché-esiste) · [Installazione](#installazione) · [Avvio rapido](#avvio-rapido) · [Profili](#profili) · [Cosa ottieni](#cosa-ottieni) · [Docs](docs/) · [Contribuire](CONTRIBUTING.md)

<br/>

<img src="docs/assets/demo.gif" alt="claude-bootstrap init: detect → plan → emit → reversible uninstall" width="860">

🌐 [English](README.md) · [Português](README.pt-br.md) · [Español](README.es.md) · [Italiano](README.it.md) · [עברית](README.he.md)

</div>

<!-- Badges to enable post-release (the PyPI ones need the package on PyPI):
![PyPI](https://img.shields.io/pypi/v/claude-bootstrap?style=flat-square)
![Downloads](https://img.shields.io/pypi/dm/claude-bootstrap?style=flat-square)
![CI](https://img.shields.io/github/actions/workflow/status/ulissesflores/claude-bootstrap/ci.yml?branch=main&style=flat-square)
-->

> [!NOTE]
> **`v1.0.0` — primo rilascio pubblico (2026-08-11).** Installa da un clone o con `pip install git+https://github.com/ulissesflores/claude-bootstrap` ([Installazione](#installazione)). Il nome su PyPI arriva via release workflow.

---

## Perché esiste

Claude Code include il proprio `/init` — e una configurazione interattiva dietro `CLAUDE_CODE_NEW_INIT=1` — che scrive un `CLAUDE.md`. `claude-bootstrap` **non è un sostituto**; è complementare e fa deliberatamente di più sugli assi che contano per una configurazione riproducibile e verificabile che riesegui su molti repo:

| | `claude /init` nativo | `claude-bootstrap` |
|---|---|---|
| **Scrive** | `CLAUDE.md` (conversazionale; esplora il tuo codice) | l'intero albero `.claude/` da un **profilo rilevato** |
| **Permessi** | **non** tocca `settings.json` | genera una **baseline** allow/deny in `settings.json` |
| **Skill / regole** | — | bundle di skill verificate sotto il profilo della licenza, **provenance-verified** + regole con ambito di percorso |
| **Riesecuzione** | per sessione | **idempotente**, con `--check`, `uninstall` completa, manifest per file |
| **Trasparenza** | — | mostra *perché* il profilo è stato scelto, chiede prima di scrivere, ogni artefatto è rimovibile |

Usa `/init` nativo per un rapido `CLAUDE.md` conversazionale. Affidati a `claude-bootstrap` quando vuoi una baseline `.claude/` **riproducibile, verificabile e basata su profili**. (Altro: [`docs/02-state-of-the-art.md`](docs/02-state-of-the-art.md) §7.2.)

---

## Cosa ottieni

- 🔎 **Rileva, poi spiega.** Esegue la scansione del progetto e stampa l'*evidenza* del profilo che sceglie (es. `pyproject.toml found, torch in deps → data-science`) — mai una scatola nera.
- ✋ **Conferma prima di scrivere.** Mostra il piano con `--check`, chiede `[y/N]`, non scrive nulla in caso di rifiuto. Saltabile con `--yes`/`--non-interactive` per la CI.
- 🧱 **Un vero albero `.claude/`.** `CLAUDE.md` (policy ≤60 righe), `PROJECT-STATE.md`, una baseline di permessi in `settings.json`, skill del profilo + regole con ambito di percorso, e file `CLAUDE.md` nelle sottocartelle dove una cartella ha un ruolo distinto.
- ♻️ **Idempotente + reversibile.** La riesecuzione non sovrascrive mai le tue modifiche (solo creazione; `<file>.new` in caso di `update`). Un manifest registra ogni file generato, così `claude-bootstrap uninstall` annulla l'intera operazione — e **mantiene qualunque file tu abbia modificato**.
- 📦 **Skill verificate sotto il profilo della licenza, provenance-verified.** 30 skill in bundle distribuite tra i profili: 25 fissate a un commit upstream e **verificate nel contenuto** (`scripts/verify-skill-provenance.py`; un job CI settimanale segnala i disallineamenti), più 5 skill **proprie**, scritte in questo repository sotto la sua licenza MIT. Ogni skill in bundle porta una licenza di ridistribuzione che abbiamo davvero letto — MIT o Apache-2.0 — con il testo integrale incluso accanto. Quattro skill di Anthropic sono state **rimosse dal bundle il 2026-07-26** perché non concedono quel diritto; puntiamo all'upstream invece di ridistribuirle.
- 🧹 **Anti-bloat per progettazione.** Tutto è semplice Markdown/JSON che puoi leggere, modificare o eliminare — e lo strumento ti dice come (`--check`, `skill remove`, `uninstall`).

---

## Installazione

> [!IMPORTANT]
> Non ancora su PyPI — installa da un clone:
>
> ```bash
> git clone https://github.com/ulissesflores/claude-bootstrap
> cd claude-bootstrap
> bin/bootstrap.sh init --profile=universal-software      # or: uv run -m claude_bootstrap.cli init
> ```

Il metodo curl è già attivo; `uv` / `pipx` / `pip` si attivano quando il pacchetto arriva su PyPI:

| Metodo | Comando |
|---|---|
| uv (consigliato) | `uv tool install claude-bootstrap` |
| pipx | `pipx install claude-bootstrap` |
| pip | `pip install claude-bootstrap` |
| curl | `curl -LsSf https://raw.githubusercontent.com/ulissesflores/claude-bootstrap/main/install.sh \| bash` |

Verifica: `claude-bootstrap version` → `v1.0.0` o successivo. Richiede **Python 3.11+**.

---

## Avvio rapido

```bash
# 1. (opzionale) vedi che tipo di progetto è questo — sola lettura
claude-bootstrap detect

# 2. scaffold: detect → rationale → piano → confirm → emit
claude-bootstrap init --profile data-science

# 3. health-check dell'installazione (13 controlli)
claude-bootstrap doctor

# cambiato idea? annulla l'intero emit (mantiene i file che hai modificato)
claude-bootstrap uninstall
```

> [!TIP]
> `claude-bootstrap init --check` stampa il piano d'azione completo e non scrive nulla — il modo più sicuro per l'anteprima.

---

## Profili

I repo a stack singolo ricevono un profilo; **i monorepo ricevono l'unione di tutti i code stack rilevati**. Aggiungere un profilo non richiede alcun intervento sugli altri. Ciascuno raggruppa skill con la provenienza per singola skill nel proprio `NOTICE.md`.

| Profilo | Skill in bundle | Upstream |
|---|---|---|
| `universal-software` | 5 | — (proprie, MIT) |
| `academic` | 3 | `K-Dense-AI/scientific-agent-skills` (MIT) |
| `data-science` | 6 | `alirezarezvani/claude-skills` (MIT) |
| `frontend` | 7 | `anthropics/skills` (Apache-2.0) + `alirezarezvani/claude-skills` (MIT) |
| `devops` | 5 | `alirezarezvani/claude-skills` (MIT) |
| `backend` | 4 | `alirezarezvani/claude-skills` (MIT) |

`detect` analizza i segnali del filesystem (`*.tex` → academic, `torch`/`tensorflow` nelle deps → data-science, `package.json`+`tsconfig` → frontend, un web framework → backend, `*.tf`/`Chart.yaml` → devops). Un **monorepo** con più stack in sotto-progetti (es. `frontend/` + `backend/`) emette una **unione** in un unico `.claude/` radice — permessi uniti + tutte le skill + `rules/<stack>.md` con ambito di percorso — più un `<subdir>/CLAUDE.md` sottile per sotto-progetto. `academic` resta esclusivo (intero repo). Dettagli: [`docs/05-profiles.md`](docs/05-profiles.md).

<div align="center"><img src="docs/assets/detect.gif" alt="claude-bootstrap detect across four project types" width="640"></div>

---

## Cosa viene installato

```
your-project/
├── CLAUDE.md                      # project instructions (≤60-line policy)
├── PROJECT-STATE.md               # curated state (you edit; not Claude's auto-memory)
├── .gitignore                     # soft-merged with yours
└── .claude/
    ├── settings.json              # permissions allow/deny + env (profile-merged)
    ├── skills/<name>/             # curated, license-audited skills
    ├── rules/<name>.md            # path-scoped rules
    └── .bootstrap-manifest.json   # records the emit so `uninstall` reverses it safely
```

Tutti i file sono **solo in creazione**: la riesecuzione non sovrascriverà le tue modifiche; `update` scrive `<file>.new` per la revisione. **Sono solo file — eliminali liberamente.**

---

## Distribuzione

Oltre alla CLI, ogni profilo curato è anche pacchettizzato come **plugin di Claude Code** tramite un [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) — così i bundle possono essere scaricati con `/plugin install`.

---

## Docs

Organizzate per intento — inizia da dove serve. Indice completo: [`docs/`](docs/).

| Vuoi… | Leggi |
|---|---|
| Capire l'architettura e il flusso | [`00-overview`](docs/00-overview.md) · [`06-bootstrap-flow`](docs/06-bootstrap-flow.md) |
| Allinearti alla spec attuale di Claude Code | [`01-canonical-anthropic`](docs/01-canonical-anthropic.md) · [`02-state-of-the-art`](docs/02-state-of-the-art.md) |
| Evitare errori comuni | [`03-anti-patterns`](docs/03-anti-patterns.md) |
| Lavorare con skill e profili | [`04-skills-curated`](docs/04-skills-curated.md) · [`05-profiles`](docs/05-profiles.md) |
| Cercare un termine / sbloccarti | [`07-glossary`](docs/07-glossary.md) · [`08-faq`](docs/08-faq.md) |

---

## Contribuire

Issue e PR sono benvenute. La configurazione di sviluppo è un solo comando (`uv sync`), i commit seguono [Conventional Commits](https://www.conventionalcommits.org), e tutto è vincolato da `pytest` + `pre-commit`. Vedi [`CONTRIBUTING.md`](CONTRIBUTING.md) e il [`CODE_OF_CONDUCT.md`](.github/CODE_OF_CONDUCT.md).

---

## Licenza

[MIT](LICENSE) © Carlos Ulisses Flores. Le skill di terze parti in bundle conservano le loro licenze upstream (MIT o Apache-2.0) — vedi il `NOTICE.md` di ciascun profilo e il `LICENSE.txt` incluso in ogni directory di skill. Le skill proprie di `universal-software` sono MIT sotto la licenza del progetto stesso. Costruito un livello sopra [`superpowers`](https://github.com/obra/superpowers); dichiara la dipendenza, non la duplica mai.
