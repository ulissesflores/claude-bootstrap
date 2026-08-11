<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-dark.svg">
  <img src="docs/assets/logo-light.svg" alt="claude-bootstrap" width="430">
</picture>

### לזהות, לבנות ולהפוך הגדרה מלאה של Claude Code — בפקודה אחת.

`claude-bootstrap` בוחן את הפרויקט שלך, מסביר לך **למה** בחר פרופיל מסוים, מציג את התוכנית, שואל פעם אחת — ואז פולט עץ `.claude/` מלא: בסיס הרשאות, skills **מבוקרי-רישיון** ונבחרים בקפידה, וכללים תחומי-נתיב. אידמפוטנטי, עם `--check` ו-`uninstall` אמיתי.

![status](https://img.shields.io/badge/status-stable-3fb950?style=flat-square)
![python](https://img.shields.io/badge/python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![license](https://img.shields.io/badge/license-MIT-3fb950?style=flat-square)
![tests](https://img.shields.io/badge/tests-271%2F271-3fb950?style=flat-square)
![skills](https://img.shields.io/badge/skills-30%20provenance--verified-7C5CFF?style=flat-square)

[למה](#למה-זה-קיים) · [התקנה](#התקנה) · [התחלה מהירה](#התחלה-מהירה) · [פרופילים](#פרופילים) · [מה אתה מקבל](#מה-אתה-מקבל) · [תיעוד](docs/) · [תרומה](CONTRIBUTING.md)

<br/>

<img src="docs/assets/demo.gif" alt="claude-bootstrap init: detect → plan → emit → reversible uninstall" width="860">

🌐 [English](README.md) · [Português](README.pt-br.md) · [Español](README.es.md) · [Italiano](README.it.md) · [עברית](README.he.md)

</div>

<div dir="rtl">

<!-- Badges to enable post-release (the PyPI ones need the package on PyPI):
![PyPI](https://img.shields.io/pypi/v/claude-bootstrap?style=flat-square)
![Downloads](https://img.shields.io/pypi/dm/claude-bootstrap?style=flat-square)
![CI](https://img.shields.io/github/actions/workflow/status/ulissesflores/claude-bootstrap/ci.yml?branch=main&style=flat-square)
-->

> [!NOTE]
> **`v1.0.0` — שחרור ציבורי ראשון (2026-08-11).** התקן מתוך clone או עם `pip install git+https://github.com/ulissesflores/claude-bootstrap` ([התקנה](#התקנה)). שם החבילה ב-PyPI מגיע דרך ה-release workflow.

---

## למה זה קיים

ל-Claude Code יש `/init` משלו — וגם הגדרה אינטראקטיבית מאחורי `CLAUDE_CODE_NEW_INIT=1` — שכותב `CLAUDE.md`. `claude-bootstrap` **אינו תחליף**; הוא משלים, ובמכוון עושה יותר בצירים החשובים להגדרה ניתנת-לשחזור וניתנת-לביקורת שאתה מריץ מחדש על פני הרבה ריפוזיטוריז:

| | `claude /init` המובנה | `claude-bootstrap` |
|---|---|---|
| **כותב** | `CLAUDE.md` (שיחתי; חוקר את הקוד שלך) | את כל עץ `.claude/` מתוך **פרופיל מזוהה** |
| **הרשאות** | **אינו** נוגע ב-`settings.json` | פולט **בסיס** allow/deny ב-`settings.json` |
| **Skills / כללים** | — | חבילות skills מבוקרות-רישיון, **מאומתות-מקור**, וכללים תחומי-נתיב |
| **הרצה חוזרת** | לכל סשן | **אידמפוטנטי**, עם `--check`, `uninstall` מלא, manifest לכל קובץ |
| **ביטחון** | — | מציג *למה* הפרופיל נבחר, שואל לפני הכתיבה, כל ארטיפקט ניתן לגיזום |

השתמש ב-`/init` המובנה ל-`CLAUDE.md` שיחתי וזריז. פנה אל `claude-bootstrap` כשאתה רוצה בסיס `.claude/` **ניתן-לשחזור, ניתן-לביקורת ומבוסס-פרופיל**. (עוד: [`docs/02-state-of-the-art.md`](docs/02-state-of-the-art.md) §7.2.)

---

## מה אתה מקבל

- 🔎 **לזהות, ואז להסביר.** סורק את הפרויקט ומדפיס את *הראיות* לפרופיל שבחר (למשל `pyproject.toml found, torch in deps → data-science`) — אף פעם לא קופסה שחורה.
- ✋ **לאשר לפני הכתיבה.** מציג את התוכנית דרך `--check`, שואל `[y/N]`, ולא כותב דבר אם תסרב. ניתן לדילוג עם `--yes`/`--non-interactive` עבור CI.
- 🧱 **עץ `.claude/` אמיתי.** `CLAUDE.md` (מדיניות ≤60 שורות), `PROJECT-STATE.md`, בסיס הרשאות ב-`settings.json`, skills של הפרופיל + כללים תחומי-נתיב, וקבצי `CLAUDE.md` בתיקיות-משנה היכן שלתיקיה יש תפקיד נבדל.
- ♻️ **אידמפוטנטי + הפיך.** הרצה חוזרת לעולם לא דורסת את העריכות שלך (יצירה-בלבד; `<file>.new` ב-`update`). manifest מתעד כל קובץ שנפלט כך ש-`claude-bootstrap uninstall` הופך את כל העניין — ו**שומר כל קובץ ששינית**.
- 📦 **Skills מבוקרי-רישיון ומאומתי-מקור.** 30 skills מצורפים על פני הפרופילים: 25 מקובעים ל-commit במקור ו**מאומתי-תוכן** (`scripts/verify-skill-provenance.py`; משימת CI שבועית מסמנת סטיות), ועוד 5 skills **מקוריים** שנכתבו במאגר הזה תחת רישיון ה-MIT שלו. כל skill מצורף נושא רישיון הפצה־מחדש שקראנו בפועל — MIT או Apache-2.0 — כשהטקסט המלא נשלח לצדו. ארבעה skills של Anthropic **הוסרו מהחבילה ב-2026-07-26** משום שאינם מעניקים הרשאה כזו; אנחנו מפנים ל-upstream במקום להפיץ אותם מחדש.
- 🧹 **אנטי-נפיחות בעיצוב.** הכול הוא Markdown/JSON פשוט שאתה יכול לקרוא, לערוך או למחוק — והכלי אומר לך איך (`--check`, `skill remove`, `uninstall`).

---

## התקנה

> [!IMPORTANT]
> עדיין לא ב-PyPI — התקן מתוך clone:
>
> ```bash
> git clone https://github.com/ulissesflores/claude-bootstrap
> cd claude-bootstrap
> bin/bootstrap.sh init --profile=universal-software      # or: uv run -m claude_bootstrap.cli init
> ```

שיטת ה-curl פעילה כבר עכשיו; `uv` / `pipx` / `pip` יופעלו כשהחבילה תגיע ל-PyPI:

| שיטה | פקודה |
|---|---|
| uv (מומלץ) | `uv tool install claude-bootstrap` |
| pipx | `pipx install claude-bootstrap` |
| pip | `pip install claude-bootstrap` |
| curl | `curl -LsSf https://raw.githubusercontent.com/ulissesflores/claude-bootstrap/main/install.sh \| bash` |

אימות: `claude-bootstrap version` → `v1.0.0` ומעלה. דורש **Python 3.11+**.

---

## התחלה מהירה

```bash
# 1. (optional) see what kind of project this is — read-only
claude-bootstrap detect

# 2. scaffold: detect → rationale → plan → confirm → emit
claude-bootstrap init --profile data-science

# 3. health-check the install (13 checks)
claude-bootstrap doctor

# changed your mind? reverse the whole emit (keeps files you edited)
claude-bootstrap uninstall
```

> [!TIP]
> `claude-bootstrap init --check` מדפיס את תוכנית הפעולה המלאה ולא כותב דבר — הדרך הבטוחה ביותר לתצוגה מקדימה.

---

## פרופילים

ריפו עם stack יחיד מקבל פרופיל אחד; **מונוריפו מקבל את האיחוד של כל ה-code stacks שזוהו**. הוספת פרופיל אינה דורשת נגיעה באחרים. כל אחד מצרף skills עם מקור פר-skill ב-`NOTICE.md` שלו.

| פרופיל | Skills מצורפים | מקור |
|---|---|---|
| `universal-software` | 5 | — (מקוריים, MIT) |
| `academic` | 3 | `K-Dense-AI/scientific-agent-skills` (MIT) |
| `data-science` | 6 | `alirezarezvani/claude-skills` (MIT) |
| `frontend` | 7 | `anthropics/skills` (Apache-2.0) + `alirezarezvani/claude-skills` (MIT) |
| `devops` | 5 | `alirezarezvani/claude-skills` (MIT) |
| `backend` | 4 | `alirezarezvani/claude-skills` (MIT) |

`detect` סורק אותות מערכת-קבצים (`*.tex` → academic, `torch`/`tensorflow` בתלויות → data-science, `package.json`+`tsconfig` → frontend, web framework → backend, `*.tf`/`Chart.yaml` → devops). **מונוריפו** עם כמה stacks בתת-פרויקטים (למשל `frontend/` + `backend/`) פולט **איחוד** ב-`.claude/` שורשי יחיד — הרשאות מאוחדות + כל ה-skills + `rules/<stack>.md` תחומי-נתיב — ובנוסף `<subdir>/CLAUDE.md` דק לכל תת-פרויקט. `academic` נשאר בלעדי (ריפו שלם). פרטים: [`docs/05-profiles.md`](docs/05-profiles.md).

<div align="center"><img src="docs/assets/detect.gif" alt="claude-bootstrap detect across four project types" width="640"></div>

---

## מה מותקן

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

כל הקבצים הם **יצירה-בלבד**: הרצה חוזרת לא תדרוס את העריכות שלך; `update` כותב `<file>.new` לבדיקה. **אלה רק קבצים — גזום בחופשיות.**

---

## הפצה

מעבר ל-CLI, כל פרופיל נבחר נארז גם כ-**Claude Code plugin** דרך [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) — כך שאפשר למשוך את החבילות עם `/plugin install`.

---

## תיעוד

מאורגן לפי כוונה — התחל היכן שהצורך שלך נמצא. אינדקס מלא: [`docs/`](docs/).

| אתה רוצה… | קרא |
|---|---|
| להבין את הארכיטקטורה והזרימה | [`00-overview`](docs/00-overview.md) · [`06-bootstrap-flow`](docs/06-bootstrap-flow.md) |
| להתאים למפרט הנוכחי של Claude Code | [`01-canonical-anthropic`](docs/01-canonical-anthropic.md) · [`02-state-of-the-art`](docs/02-state-of-the-art.md) |
| להימנע מטעויות נפוצות | [`03-anti-patterns`](docs/03-anti-patterns.md) |
| לעבוד עם skills ופרופילים | [`04-skills-curated`](docs/04-skills-curated.md) · [`05-profiles`](docs/05-profiles.md) |
| לחפש מונח / להיחלץ מתקיעה | [`07-glossary`](docs/07-glossary.md) · [`08-faq`](docs/08-faq.md) |

---

## תרומה

Issues ו-PRs מתקבלים בברכה. הגדרת הפיתוח היא פקודה אחת (`uv sync`), commits עוקבים אחר [Conventional Commits](https://www.conventionalcommits.org), והכול מגודר על ידי `pytest` + `pre-commit`. ראה [`CONTRIBUTING.md`](CONTRIBUTING.md) ואת [`CODE_OF_CONDUCT.md`](.github/CODE_OF_CONDUCT.md).

---

## רישיון

[MIT](LICENSE) © Carlos Ulisses Flores. Skills של צד שלישי המצורפים שומרים על רישיונות המקור שלהם (MIT או Apache-2.0) — ראה את `NOTICE.md` של כל פרופיל ואת `LICENSE.txt` הנשלח בתוך כל ספריית skill. ה-skills המקוריים ב-`universal-software` הם MIT תחת הרישיון של הפרויקט עצמו. נבנה שכבה אחת מעל [`superpowers`](https://github.com/obra/superpowers); מצהיר על התלות, לעולם לא משכפל אותה.

</div>
