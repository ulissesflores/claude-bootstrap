# Glossário — `claude-bootstrap`

> Termos canônicos do domínio Claude Code + termos próprios deste projeto. Em caso de dúvida sobre nomenclatura, consulte aqui antes de inventar nome novo. Para o padrão Anthropic completo, ver [`01-canonical-anthropic.md`](01-canonical-anthropic.md).
>
> 🇬🇧 [English version](../07-glossary.md) — the canonical copy.

---

## Termos canônicos Anthropic

### CLAUDE.md
Arquivo markdown de instruções persistentes carregado em toda sessão Claude Code. Hierarquia de escopo: managed (org) > project (`./CLAUDE.md`) > user (`~/.claude/CLAUDE.md`) > local (`./CLAUDE.local.md`, gitignored). Política do projeto: **≤60 linhas quando possível, máx ~140-150**; passar disso quebrar em [`.claude/rules/<scope>*.md`](https://code.claude.com/docs/en/memory) (path-scoped, padrão Q2/2026). Ver [`01-canonical-anthropic.md` §1](01-canonical-anthropic.md#1-memory-system--claudemd--auto-memory).

### Skill
Capacidade modular invocável por Claude. Definição em `.claude/skills/<name>/SKILL.md` (projeto) ou `~/.claude/skills/<name>/SKILL.md` (user). YAML frontmatter + corpo markdown. Pode ser model-invoked (Claude decide) ou user-invocable (`/skill-name`). Ver [`01-canonical-anthropic.md` §2](01-canonical-anthropic.md#2-skills--agent-skills-open-standard).

### Agent (subagent)
Assistente AI especializado com contexto fresco e ferramentas restritas. Definido em `.claude/agents/<name>.md`. Built-in: `Explore` (read-only, para busca), `Plan` (read-only para planning), `general-purpose` (todas as ferramentas). Cada subagent mantém auto-memory próprio per worktree. Ver [`01-canonical-anthropic.md` §4](01-canonical-anthropic.md#4-subagents--specialized-ai-assistants).

### Hook
Handler de evento de lifecycle (session, turn, tool, permission). Configurado em `settings.json`. Tipos (5): `command` (shell), `http` (POST JSON), `mcp_tool`, `prompt` (LLM-based), `agent` (spawna subagent verificador). Determinístico (exit 0 = pass, exit 2 = block). Ver [`01-canonical-anthropic.md` §5](01-canonical-anthropic.md#5-hooks--lifecycle-event-handlers).

### MCP (Model Context Protocol)
Protocolo aberto para conectar Claude a sistemas externos (BD, APIs, ferramentas CLI, Notion, Figma). Transports: HTTP, SSE, stdio. Configuração em `.mcp.json` (projeto) ou `~/.claude.json` (user). 5k+ servidores no registry mai/2026. Análogo a "USB-C para AI". Ver [`01-canonical-anthropic.md` §6](01-canonical-anthropic.md#6-mcp--model-context-protocol).

### Plugin
Extensão reutilizável que bundla skills + commands + agents + hooks + MCP servers. Manifest em `.claude-plugin/plugin.json`. Discovery via marketplace + `/plugin install`. Skills do plugin têm namespace `plugin-name:skill-name`. Ver [`01-canonical-anthropic.md` §7](01-canonical-anthropic.md#7-plugins--extensões-reutilizáveis-v2025).

### Settings hierarchy
Ordem de prioridade de `settings.json` (alta → baixa): managed (IT-deployed) > CLI flags > local (`.claude/settings.local.json`, gitignored) > project (`.claude/settings.json`) > user (`~/.claude/settings.json`). Mais específico ganha. Ver [`01-canonical-anthropic.md` §8](01-canonical-anthropic.md#8-settings-hierarchy--configuration-scopes).

### Plan mode
Modo de operação Claude Code (`/plan`) onde só ferramentas read-only são permitidas. Usado para explorar codebase + apresentar plano antes de implementar. Padrão ouro para 3+ passos. Ver [`02-state-of-the-art.md` §1](02-state-of-the-art.md#1-padrão-consensual-70-das-fontes).

### Auto-memory
Memória escrita automaticamente por Claude (lições de correções) em `~/.claude/projects/<path>/memory/`. Primeiras 200 linhas ou 25KB carregadas por sessão. Diferente de `CLAUDE.md` (que você escreve). Ver [`01-canonical-anthropic.md` §1](01-canonical-anthropic.md#1-memory-system--claudemd--auto-memory).

---

## Termos próprios deste projeto

### Profile
Conjunto opinativo de templates + skills + rules + settings para um tipo de projeto. Definido em `templates/profiles/<name>/profile.yaml`. Profiles populados (v1.0.0): `frontend` (7 skills), `data-science` (6), `universal-software` (default, 5), `devops` (5), `backend` (4), `academic` (3) — 30 skills embarcadas no total. Adicionar profile novo é zero-touch nos demais (princípio profile-based).

### Registry
`claude_bootstrap/registry/skills.yaml` — catálogo curado de 13 skills, instaláveis individualmente via `claude-bootstrap skill add`. Cada entrada tem `name`, `source` (URL git ou `local`), `path`, `tier` (1-3), `profiles` aplicáveis, `description`, `evidence_url`, `last_validated_at`. Distinto dos **bundles de profile** (skills embarcadas em `templates/profiles/<p>/skills/`, com commit-pins em `scripts/skill-pins.json`) — ver [04-skills-curated.md](04-skills-curated.md).

### Tier (de skill)
Nível de confiança/maturidade de uma skill no registry — rótulo consultivo, não política de instalação. **Nenhum tier instala nada**: toda skill do registry, em qualquer tier, só chega a um projeto por um `claude-bootstrap skill add <name>` explícito. No código, `tier` é campo obrigatório mais o filtro `skill list --tier`.
- **Tier 1 (core)**: amplamente útil, auditada manualmente, trigger bem definido, sem efeitos colaterais destrutivos, evidência de uso real
- **Tier 2 (recommended)**: consolidada, mas restrita a fluxos específicos cujo overhead de aprendizado não compensa em todo projeto
- **Tier 3 (experimental)**: marcado como `unstable: true` — a API pode mudar entre versões do `claude-bootstrap`

Critérios completos, e os critérios separados que governam os bundles de profile, em [04-skills-curated.md](04-skills-curated.md) §2.

### Idempotente
Princípio operacional: re-rodar `bootstrap.sh init` em projeto já configurado **não quebra nada e não duplica**. Verificação: `init` 2 vezes consecutivas → `git diff` vazio.

### Detectivo antes de prescritivo
Princípio operacional: `detect.py` escaneia projeto (heurísticas em [`00-overview.md` §4](00-overview.md#4-fluxo-do-claude-bootstrap-init)) antes que `interview.py` pergunte. Reduz fricção: o sistema sabe o que vê e só pergunta o que importa.

### Profile-based, não monolítico
Princípio arquitetural: lógica do bootstrap é genérica; especialização vive em `templates/profiles/<name>/`. Adicionar profile novo é zero-touch nos profiles existentes.

---

## Termos do ecossistema

### Superpowers
Framework de skills + commands + methodology criado por @obra (https://github.com/obra/superpowers). ~270k stars (medido em 2026-08-10). Lingua franca cross-tool (Cursor, Codex, Gemini, Claude Code). `claude-bootstrap` declara dependência de `superpowers`, **não** embarca cópia. Se ausente em `~/.claude/superpowers/`, oferece `git clone`.

### Agentic-stack
Conjunto de convenções que parte dos usuários de Claude Code implementa em `~/.agent/`: memória episódica/semântica, dream cycle, review queue, host-agent CLI tools (Python), documentado no `AGENTS.md` do próprio diretório. No `claude-bootstrap` é uma **flag de interop detectada** (`agentic_stack_interop`) e não um profile: o `detect` acha `~/.agent/` (ou `.agent/`) e o `CLAUDE.md` emitido aponta pro stack em vez de duplicá-lo.

---

## Termos de operação

### Conventional Commits
Convenção de mensagens de commit: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`, `build:`, `ci:`, `perf:`, `style:`. Adotada neste repo a partir do primeiro commit. Ref: https://www.conventionalcommits.org/

### Path-scoped rules
Padrão Anthropic Q2/2026: `.claude/rules/<path>*.md` aplicam-se apenas quando Claude está editando arquivos no path. Substitui `CLAUDE.md` monolítico quando este passa de ~150 linhas. Ex: `.claude/rules/frontend*.md` carrega só ao trabalhar em `packages/frontend/`.

### PII scan
Gate em [`scripts/pii-scan.py`](../../scripts/pii-scan.py) que varre os arquivos versionados (`git ls-files`) atrás de contexto pessoal ou identificador de máquina. Roda no pre-commit e no CI; falha o build em qualquer ocorrência. São duas camadas: os padrões **estruturais** vêm no próprio script (paths de home absolutos, que identificam uma máquina de desenvolvimento para qualquer usuário), enquanto os padrões que nomeiam pessoa, organização ou host privado são lidos de um `.pii-patterns.local` gitignorado — um `regex<TAB>motivo` por linha — de modo que a lista em si nunca é publicada. A linha de sucesso diz quais camadas rodaram, porque um resultado limpo com menos padrões não é o mesmo resultado. Metadado de **autoria** (nome, ORCID, e-mail em `CITATION.cff`/`pyproject.toml`) é atribuição deliberada e está fora do escopo.
