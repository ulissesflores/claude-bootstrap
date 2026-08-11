# FAQ — `claude-bootstrap`

> Última atualização: 2026-07-29. Para questões mais profundas, ver [`00-overview.md`](00-overview.md) (visão geral) ou [`06-bootstrap-flow.md`](06-bootstrap-flow.md) (fluxo detalhado).
>
> 🇬🇧 [English version](../08-faq.md) — the canonical copy.

---

## Posicionamento

### Q: Por que não usar só `superpowers`?

`superpowers` resolve primitivas (skills modulares, commands, methodology) mas não faz bootstrap adaptativo, não curatura de skills por tier, nem gera `CLAUDE.md` configurado para o tipo do projeto. `claude-bootstrap` é a camada de orquestração acima, não substituto. Ver [`00-overview.md` §3](00-overview.md#3-arquitetura--3-camadas).

### Q: Em que `claude-bootstrap` difere de outros frameworks (`claude-code-ultimate-guide`, `awesome-claude-code-toolkit`, `dotclaude`)?

Esses projetos são coleções curatoriais ou checklists manuais. `claude-bootstrap` tem um **engine idempotente** (`bin/bootstrap.sh`) que detecta o projeto, faz interview e instala configuração via Jinja templates. É executável, não só referência. Ver [`02-state-of-the-art.md`](02-state-of-the-art.md) para comparativo com 36 fontes.

### Q: Por que Python e não shell puro / TypeScript?

Shell puro limita parsing de YAML (`registry/skills.yaml`) e interface interativa de interview. TypeScript exigiria runtime Node instalado — menos universal em ambientes acadêmicos e devops. Python 3.11+ está onipresente e o stack (`questionary`, `jinja2`, `pyyaml`, `rich`) é maduro.

---

## Uso prático

### Q: Como rodar `bootstrap.sh init` em projeto existente?

`claude-bootstrap init` (ou `bin/bootstrap.sh init`) detecta `.claude/` existente e reporta `mode: update`. A semântica é **create-only**: arquivos existentes não são sobrescritos. Com `claude-bootstrap update`, um arquivo divergido é escrito como `<path>.new` para revisão (não sobrescreve). Por padrão `init` mostra o plano e pede `[y/N]` antes de escrever. Detalhes em [`00-overview.md` §4](00-overview.md#4-fluxo-do-claude-bootstrap-init).

### Q: Vai sobrescrever meu `CLAUDE.md`?

Não. A semântica é **create-only**: se o `CLAUDE.md` já existe, o `init` o pula (status `exists-skipped`); só cria quando ausente. `update` escreve um `CLAUDE.md.new` ao lado para você comparar. `--force` sobrescreve (use com cuidado). E o confirm-before-write `[y/N]` precede qualquer escrita. Ver princípio 1 em [`CLAUDE.md`](../../CLAUDE.md).

### Q: Como criar profile customizado?

Crie `templates/profiles/<nome>/` com um `profile.yaml` (campos `name`, `description`, `version`; opcionais `skills`, `rules`, `settings_overrides`). O `_base/` é sempre aplicado; o profile adiciona por cima. Registre a heurística em `claude_bootstrap/detect.py` e o nome em `interview.py`. Zero-touch nos demais (princípio 3). Passo a passo em [`05-profiles.md` §7](05-profiles.md).

### Q: Como adicionar skill ao registry?

Edite `claude_bootstrap/registry/skills.yaml` com `name`, `source` (`local`/`github`), `path`, `tier` (1-3), `profiles`. Valide com `claude-bootstrap skill validate` e teste com `claude-bootstrap skill add <name> --target /tmp/x`. Ver [`04-skills-curated.md` §7](04-skills-curated.md). (Distinto dos bundles de profile — ver lá.)

### Q: Como fazer dry-run sem escrever?

Passe `--check` para `claude-bootstrap init` (ou `update`). Imprime o plano de ações (`would-create`/`would-overwrite`/…) sem tocar o disco e sem gravar o manifesto. É também o que o confirm-before-write usa para mostrar o plano antes do `[y/N]`.

---

## Profiles

### Q: Qual profile acadêmico usar?

Use `academic` (detectado por `*.tex`, `*.csl`, ou `*.bib` sem projeto de código): **3 skills curadas, todas de `K-Dense-AI/scientific-agent-skills` (MIT)**. Quatro skills do `anthropics/skills` ficaram embarcadas aqui até 2026-07-26 e foram desembarcadas — o `LICENSE.txt` delas é lista de restrição sem cláusula de concessão, e uma não tinha licença nenhuma; o `NOTICE.md` guarda o registro do porquê. `universal-software` é o default para o resto. Heurísticas em [`05-profiles.md` §3](05-profiles.md).

### Q: O profile `data-science` está pronto?

Sim. `data-science` (6 skills), `frontend` (7), `devops` (5) e `backend` (4) estão **populados** com skills curadas e content-verified (ver `NOTICE.md` de cada). Os 6 profiles estão prontos; ver [`05-profiles.md` §6](05-profiles.md).

### Q: Posso ter múltiplos profiles ativos?

Sim, em **monorepos**. Um repo single-stack recebe um profile; um monorepo com vários stacks
(ex.: `frontend/` React + `backend/` FastAPI + `infra/` terraform) recebe a **união** dos stacks
detectados — `--profile` é repetível, e o `detect` descobre sub-projetos sozinho. `academic` é
exclusivo (domínio de repo inteiro, nunca entra numa união). Detalhes em
[`05-profiles.md` §10](05-profiles.md).

---

## Skills e superpowers

### Q: Skills duplicam o que `superpowers` já tem?

Não, e não há conteúdo copiado. As skills do `superpowers` são **dependência declarada**, nunca embarcadas. O que vai dentro dos profiles é outro conjunto: o `universal-software` embarca **5 skills first-party escritas para este projeto** (MIT, `LICENSE.txt` em cada), e os profiles de domínio (`academic`/`data-science`/`frontend`/`devops`/`backend`) embarcam skills curadas de upstreams MIT, com proveniência por skill no `NOTICE.md` e commit-pins em `scripts/skill-pins.json`. Ver princípio 5 em [`CLAUDE.md`](../../CLAUDE.md).

### Q: O que acontece se `superpowers` não estiver instalado?

O `detect`/`interview` checa presença em `~/.claude/skills/superpowers` (ou `~/.claude/superpowers`) e grava a flag `superpowers_available`, que o `CLAUDE.md` emitido referencia. **Não** instala o `superpowers` automaticamente — instale-o você (é uma dependência declarada, não embarcada). Ver [`00-overview.md` §3](00-overview.md#3-arquitetura--3-camadas).

### Q: Skills do registry são versionadas?

Sim. Skills do registry: `claude-bootstrap skill update` re-extrai as instaladas das fontes atuais. Skills de **bundle de profile**: fixadas a commits upstream em `scripts/skill-pins.json`; `scripts/verify-skill-provenance.py` confere o conteúdo vs o pin e `--sync` atualiza, com o workflow `skill-drift.yml` checando semanalmente. Skill first-party não tem upstream pra fixar, então verifica como `FIRST-PARTY` — evidência mais fraca que uma comparação byte-a-byte, e rotulada assim de propósito.

---

## Memory e instruções

### Q: Por que manter `CLAUDE.md` enxuto (≤60 linhas)?

Arquivos grandes no contexto da sessão consomem tokens e aumentam latência de leitura. A política do projeto: **≤60 linhas quando possível, máx ~140-150**; o que for path-específico vai pra `.claude/rules/<scope>*.md` e o que for de subpasta pra `<subdir>/CLAUDE.md` (carregam sob demanda). Fonte: `docs/01-canonical-anthropic.md`. Regra explícita em [`CLAUDE.md`](../../CLAUDE.md).

### Q: Quando usar `.claude/rules/<scope>*.md` em vez de `CLAUDE.md`?

Use `rules/` quando a regra se aplica a um subconjunto de paths (ex: `rules/python-*.md` só ativa em arquivos `.py`) ou quando `CLAUDE.md` já está em ~150 linhas. Path-scoped rules são carregadas por contexto — menos tokens desperdiçados. Padrão Anthropic Q2/2026 descrito em [`01-canonical-anthropic.md`](01-canonical-anthropic.md).

### Q: Como funciona auto-memory?

`claude-bootstrap` não implementa memória própria. Se o operador usa `agentic-stack` (`~/.agent/`), o `detect` acha o diretório e grava a flag `agentic_stack_interop`, e o `CLAUDE.md` gerado referencia o stack. Para projetos sem `agentic-stack`, a memória fica no `CLAUDE.md`, no `PROJECT-STATE.md` e em `.claude/rules/`. Ver heurísticas em [`05-profiles.md` §3](05-profiles.md).

---

## Contribuição

### Q: Como reportar bug?

Use GitHub Issues — os templates estão em `.github/ISSUE_TEMPLATE/` (bug report, feature request); reporte de segurança vai pelo canal privado descrito em `.github/SECURITY.md`, nunca por issue pública.

### Q: Como adicionar novo profile?

1. Crie `templates/profiles/<nome>/` com um `profile.yaml` (+ `skills/`, `rules/`, `NOTICE.md` se embarcar skills).
2. Adicione a heurística em `claude_bootstrap/detect.py` (`infer_profile`) e o nome em `interview.py` (`PROFILES`).
3. Documente em [`docs/05-profiles.md`](05-profiles.md) e adicione um teste `test_init_with_<nome>_profile`.
4. Zero-touch nos outros profiles — não edite `_base/` sem discussão.

### Q: Posso publicar isso em meu próprio fork?

Sim, licença MIT. Pedido: mantenha o crédito a `superpowers` (obra/superpowers) como dependência — o posicionamento de camada acima, não competidor, é intencional e evita confusão na comunidade. Ver [`LICENSE`](../../LICENSE) e [`README.md`](../../README.md#license).
