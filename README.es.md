<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-dark.svg">
  <img src="docs/assets/logo-light.svg" alt="claude-bootstrap" width="430">
</picture>

### Detecta, genera y revierte una configuración completa de Claude Code — en un solo comando.

`claude-bootstrap` inspecciona tu proyecto, te explica **por qué** eligió un perfil, muestra el plan, pregunta una sola vez — y luego emite un árbol `.claude/` completo: una línea base de permisos, skills curadas y **auditadas por licencia**, y reglas con alcance por ruta. Idempotente, con `--check` y un `uninstall` real.

![status](https://img.shields.io/badge/status-stable-3fb950?style=flat-square)
![python](https://img.shields.io/badge/python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![license](https://img.shields.io/badge/license-MIT-3fb950?style=flat-square)
![tests](https://img.shields.io/badge/tests-271%2F271-3fb950?style=flat-square)
![skills](https://img.shields.io/badge/skills-30%20provenance--verified-7C5CFF?style=flat-square)

[Por qué](#por-qué-existe) · [Instalación](#instalación) · [Inicio rápido](#inicio-rápido) · [Perfiles](#perfiles) · [Qué obtienes](#qué-obtienes) · [Docs](docs/) · [Contribuir](CONTRIBUTING.md)

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
> **`v1.0.0` — primer lanzamiento público (2026-08-11).** Instala desde un clon o con `pip install git+https://github.com/ulissesflores/claude-bootstrap` ([Instalación](#instalación)). El nombre en PyPI llega vía el release workflow.

---

## Por qué existe

Claude Code incluye su propio `/init` — y una configuración interactiva detrás de `CLAUDE_CODE_NEW_INIT=1` — que escribe un `CLAUDE.md`. `claude-bootstrap` **no es un reemplazo**; es complementario, y deliberadamente hace más en los ejes que importan para una configuración reproducible y auditable que vuelves a ejecutar en muchos repositorios:

| | `claude /init` nativo | `claude-bootstrap` |
|---|---|---|
| **Escribe** | `CLAUDE.md` (conversacional; explora tu código) | todo el árbol `.claude/` a partir de un **perfil detectado** |
| **Permisos** | **no** toca `settings.json` | emite una **línea base** de permitir/denegar en `settings.json` |
| **Skills / reglas** | — | paquetes de skills auditados por licencia y **con procedencia verificada** + reglas con alcance por ruta |
| **Reejecución** | por sesión | **idempotente**, con `--check`, `uninstall` completo, manifiesto por archivo |
| **Confianza** | — | muestra *por qué* se eligió el perfil, pregunta antes de escribir, cada artefacto es eliminable |

Usa `/init` nativo para un `CLAUDE.md` conversacional rápido. Recurre a `claude-bootstrap` cuando quieras una línea base `.claude/` **reproducible, auditable y basada en perfiles**. (Más: [`docs/02-state-of-the-art.md`](docs/02-state-of-the-art.md) §7.2.)

---

## Qué obtienes

- 🔎 **Detecta y luego explica.** Escanea el proyecto e imprime la *evidencia* del perfil que elige (p. ej. `pyproject.toml found, torch in deps → data-science`) — nunca una caja negra.
- ✋ **Confirma antes de escribir.** Muestra el plan vía `--check`, pregunta `[y/N]`, no escribe nada si rechazas. Omisible con `--yes`/`--non-interactive` para CI.
- 🧱 **Un árbol `.claude/` de verdad.** `CLAUDE.md` (política de ≤60 líneas), `PROJECT-STATE.md`, una línea base de permisos en `settings.json`, skills del perfil + reglas con alcance por ruta, y archivos `CLAUDE.md` en subdirectorios cuando una carpeta tiene un rol distinto.
- ♻️ **Idempotente y reversible.** Reejecutar nunca pisa tus ediciones (solo creación; `<file>.new` al hacer `update`). Un manifiesto registra cada archivo emitido para que `claude-bootstrap uninstall` revierta todo — y **conserva cualquier archivo que hayas modificado**.
- 📦 **Skills auditadas por licencia y con procedencia verificada.** 30 skills incluidas en los perfiles: 25 fijadas a un commit upstream y **verificadas por contenido** (`scripts/verify-skill-provenance.py`; un job semanal de CI señala desviaciones), más 5 skills **propias**, escritas en este repositorio bajo su licencia MIT. Cada skill incluida lleva una licencia de redistribución que realmente leímos — MIT o Apache-2.0 — con su texto completo incluido junto a ella. Cuatro skills de Anthropic fueron **excluidas del bundle el 2026-07-26** porque no otorgan ese permiso; apuntamos al upstream en lugar de redistribuirlas.
- 🧹 **Anti-bloat por diseño.** Todo es Markdown/JSON plano que puedes leer, editar o borrar — y la herramienta te dice cómo (`--check`, `skill remove`, `uninstall`).

---

## Instalación

> [!IMPORTANT]
> Aún fuera de PyPI — instala desde un clon:
>
> ```bash
> git clone https://github.com/ulissesflores/claude-bootstrap
> cd claude-bootstrap
> bin/bootstrap.sh init --profile=universal-software      # or: uv run -m claude_bootstrap.cli init
> ```

El método curl ya está activo; `uv` / `pipx` / `pip` se activan cuando el paquete llegue a PyPI:

| Método | Comando |
|---|---|
| uv (recomendado) | `uv tool install claude-bootstrap` |
| pipx | `pipx install claude-bootstrap` |
| pip | `pip install claude-bootstrap` |
| curl | `curl -LsSf https://raw.githubusercontent.com/ulissesflores/claude-bootstrap/main/install.sh \| bash` |

Verifica: `claude-bootstrap version` → `v1.0.0` o posterior. Requiere **Python 3.11+**.

---

## Inicio rápido

```bash
# 1. (opcional) ver qué tipo de proyecto es este — solo lectura
claude-bootstrap detect

# 2. scaffold: detect → rationale → plan → confirm → emit
claude-bootstrap init --profile data-science

# 3. health-check de la instalación (13 comprobaciones)
claude-bootstrap doctor

# ¿cambiaste de idea? revierte todo el emit (conserva los archivos que editaste)
claude-bootstrap uninstall
```

> [!TIP]
> `claude-bootstrap init --check` imprime el plan de acción completo y no escribe nada — la forma más segura de previsualizar.

---

## Perfiles

Los repos de un solo stack reciben un perfil; **los monorepos reciben la unión de todos los code stacks detectados**. Agregar un perfil no afecta a los demás. Cada uno agrupa skills con procedencia por skill en su `NOTICE.md`.

| Perfil | Skills incluidas | Upstream |
|---|---|---|
| `universal-software` | 5 | — (propias, MIT) |
| `academic` | 3 | `K-Dense-AI/scientific-agent-skills` (MIT) |
| `data-science` | 6 | `alirezarezvani/claude-skills` (MIT) |
| `frontend` | 7 | `anthropics/skills` (Apache-2.0) + `alirezarezvani/claude-skills` (MIT) |
| `devops` | 5 | `alirezarezvani/claude-skills` (MIT) |
| `backend` | 4 | `alirezarezvani/claude-skills` (MIT) |

`detect` escanea señales del sistema de archivos (`*.tex` → academic, `torch`/`tensorflow` en las deps → data-science, `package.json`+`tsconfig` → frontend, un web framework → backend, `*.tf`/`Chart.yaml` → devops). Un **monorepo** con varios stacks en sub-proyectos (p. ej. `frontend/` + `backend/`) emite una **unión** en un único `.claude/` raíz — permisos unidos + todas las skills + `rules/<stack>.md` con alcance por ruta — más un `<subdir>/CLAUDE.md` delgado por sub-proyecto. `academic` es exclusivo (repo entero). Detalles: [`docs/05-profiles.md`](docs/05-profiles.md).

<div align="center"><img src="docs/assets/detect.gif" alt="claude-bootstrap detect across four project types" width="640"></div>

---

## Qué se instala

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

Todos los archivos son **solo de creación**: reejecutar no sobrescribirá tus ediciones; `update` escribe `<file>.new` para revisión. **Son solo archivos — elimínalos libremente.**

---

## Distribución

Más allá del CLI, cada perfil curado también se empaqueta como un **plugin de Claude Code** vía un [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) — para que los paquetes puedan obtenerse con `/plugin install`.

---

## Docs

Organizado por intención — empieza donde esté tu necesidad. Índice completo: [`docs/`](docs/).

| Quieres… | Lee |
|---|---|
| Entender la arquitectura y el flujo | [`00-overview`](docs/00-overview.md) · [`06-bootstrap-flow`](docs/06-bootstrap-flow.md) |
| Ajustarte a la especificación actual de Claude Code | [`01-canonical-anthropic`](docs/01-canonical-anthropic.md) · [`02-state-of-the-art`](docs/02-state-of-the-art.md) |
| Evitar errores comunes | [`03-anti-patterns`](docs/03-anti-patterns.md) |
| Trabajar con skills y perfiles | [`04-skills-curated`](docs/04-skills-curated.md) · [`05-profiles`](docs/05-profiles.md) |
| Buscar un término / desatascarte | [`07-glossary`](docs/07-glossary.md) · [`08-faq`](docs/08-faq.md) |

---

## Contribuir

Issues y PRs son bienvenidos. La configuración de desarrollo es un solo comando (`uv sync`), los commits siguen [Conventional Commits](https://www.conventionalcommits.org), y todo está controlado por `pytest` + `pre-commit`. Consulta [`CONTRIBUTING.md`](CONTRIBUTING.md) y el [`CODE_OF_CONDUCT.md`](.github/CODE_OF_CONDUCT.md).

---

## Licencia

[MIT](LICENSE) © Carlos Ulisses Flores. Las skills de terceros incluidas conservan sus licencias upstream (MIT o Apache-2.0) — consulta el `NOTICE.md` de cada perfil y el `LICENSE.txt` que se incluye dentro de cada directorio de skill. Las skills propias de `universal-software` son MIT bajo la licencia del propio proyecto. Construido una capa por encima de [`superpowers`](https://github.com/obra/superpowers); declara la dependencia, nunca la duplica.
