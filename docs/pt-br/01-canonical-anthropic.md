# Padrão canônico Anthropic Claude Code

> A spec do Claude Code que este projeto mira. Traduzido e reconciliado internamente em
> **2026-08-03**; cada seção carrega a data da própria verificação contra o upstream (§5 hooks:
> 2026-06-08). Fonte: https://code.claude.com/docs/en — a lista viva sempre ganha desta página.
>
> 🇬🇧 [English version](../01-canonical-anthropic.md) — the canonical copy.

---

## 1. Memory system — CLAUDE.md + Auto-Memory

**Fonte**: https://code.claude.com/docs/en/memory

- **Duas camadas complementares**:
  - `CLAUDE.md` (você escreve, instruções persistentes)
  - Auto memory (Claude escreve, lições de correções)

- **Hierarquia de escopo** (mais específico ganha):
  1. `/Library/Application Support/ClaudeCode/CLAUDE.md` (macOS managed policy, org-wide)
  2. `./CLAUDE.md` ou `./.claude/CLAUDE.md` (projeto, checkado em git)
  3. `~/.claude/CLAUDE.md` (user, todos os projetos)
  4. `./CLAUDE.local.md` (pessoal projeto-only, gitignored)

- **Comportamento de carregamento**: Sobe na árvore de diretórios desde o CWD, depois desce em subdiretórios on-demand
- **Tamanho**: manter conciso (custo de contexto) — política deste projeto: **≤60 linhas quando possível, máx ~140-150**; usar `@path/to/file` imports ou `.claude/rules/*.md` para path-scoped rules
- **Auto-memory location**: `~/.claude/projects/.../memory/` (primeiras 200 linhas ou 25KB carregadas por sessão)
- **Imports**: sintaxe `@relative/path`, máximo 4 hops de recursão, resolvidos relativos ao arquivo importador

---

## 2. Skills — Agent Skills Open Standard

**Fonte**: https://code.claude.com/docs/en/skills

- **Definição**: `.claude/skills/<name>/SKILL.md` ou `~/.claude/skills/<name>/SKILL.md`
- **Hierarquia de escopo**:
  - Enterprise (managed settings)
  - Personal (`~/.claude/skills/`)
  - Project (`.claude/skills/`)
  - Plugin (`<plugin>/skills/`)

- **Skills bundled com o cliente**: o Claude Code traz um conjunto próprio (`/simplify`, `/loop` e `/claude-api` entre elas) que **muda de release para release**; `disableBundledSkills` desliga o conjunto inteiro. Enumerar aqui só produziria uma lista rotten — o conjunto corrente sai de `/help` ou da doc live

- **Frontmatter (YAML)**:
  ```yaml
  name: skill-name                    # lowercase, max 64 chars
  description: What it does           # crítico para auto-invocação
  when_to_use: Trigger phrases        # appended to description
  argument-hint: [arg1] [arg2]        # autocomplete
  arguments: arg1 arg2                # named positional args
  disable-model-invocation: false     # true = manual-only (/name)
  user-invocable: true                # false = oculto do menu /
  allowed-tools: Read Grep            # space-sep, sem permission prompts
  model: sonnet|opus|haiku|inherit    # alias, full model ID, ou inherit (default)
  effort: low|medium|high|xhigh|max
  context: fork                       # run em isolated context
  ```

- **Estrutura de arquivos** (`my-skill/`):
  - `SKILL.md` — obrigatório: frontmatter + instruções
  - `template.md` — opcional, template para Claude preencher
  - `examples/sample.md` — opcional, exemplos
  - `scripts/validate.sh` — opcional, executável que Claude pode rodar

- **Live reload**: mudanças em `.claude/skills/` detectadas na mesma sessão (exceto novo top-level dir)
- **Nested discovery**: monorepo `packages/frontend/.claude/skills/` auto-descoberto ao editar nessa árvore
- **Plugin skills**: namespaced como `plugin-name:skill-name` (sem conflitos)
- **Governance (settings.json)**: `disableBundledSkills` (desliga as bundled `/simplify` etc.), `disableSkillShellExecution` (proíbe `scripts/` executáveis), `maxSkillDescriptionChars` / `skillListingBudgetFraction` (orçamento do listing; `description`+`when_to_use` ≤1.536 chars), `skillOverrides` (sobrescreve uma skill por nome).

---

## 3. Slash commands vs Skills

**Fonte**: https://code.claude.com/docs/en/slash-commands

- **Skills (preferido)**: `.claude/skills/<name>/SKILL.md` — model-invoked, contentful
- **Commands (legacy)**: `.claude/commands/<name>.md` — **subsumidos pelas skills**: `.claude/commands/deploy.md` ≡ `.claude/skills/deploy/SKILL.md`, ambos resolvem `/deploy` (se ambos existem, a Skill prevalece). `claude-bootstrap` emite **SKILL.md**, não `commands/*.md`.
- **Distinção**: Skills são "smart" (Claude decide quando); Commands são fixed logic ou triggers

---

## 4. Subagents — specialized AI assistants

**Fonte**: https://code.claude.com/docs/en/sub-agents

- **Built-in subagents**:
  - **Explore**: tools read-only, para buscar e analisar codebases
  - **Plan**: o modelo da sessão, read-only (junta contexto antes de planejar)
  - **General-purpose**: all tools (multi-step research + action)
  - **statusline-setup, claude-code-guide**: helpers específicos

- **Definição**: Markdown + YAML frontmatter em `.claude/agents/<name>.md`

- **Hierarquia de escopo**:
  1. Managed settings (organização)
  2. `--agents` CLI flag (session-only JSON)
  3. `.claude/agents/` (projeto)
  4. `~/.claude/agents/` (user, todos projetos)
  5. Plugin `agents/` directory

- **Frontmatter**:
  ```yaml
  description: When to use this agent
  prompt: System prompt / instructions
  tools: [Read, Grep, Bash]  # ou disallowedTools
  model: sonnet|opus|haiku   # alias, model ID completo, ou inherit (default)
  permissionMode: auto|ask|deny
  mcpServers: [list]
  hooks: {...}
  maxTurns: 10
  skills: [skill1, skill2]
  initialPrompt: Auto-sent on spawn
  memory: true               # auto-memory persistente per worktree
  effort: low|medium|high
  background: false|true
  isolation: none|worktree   # filesystem isolation
  color: blue                # UI display color
  ```

> **Campo `model`** (frontmatter de skills/subagents): aceita um **alias**, um **model ID completo**, ou **`inherit`** (default = mesmo modelo da sessão). **`inherit` é específico do frontmatter — NÃO é alias da flag `--model`.**
>
> A flag/config **`--model`** (top-level) aceita os aliases `default`, `best`, `fable`, `sonnet`, `opus`, `haiku`, `sonnet[1m]`, `opus[1m]`, `opusplan`, ou um model ID completo (fonte: https://code.claude.com/docs/en/model-config). Os **nomes** dos aliases são estáveis; **para qual modelo concreto cada um resolve, não** — `best` resolve para o melhor modelo a que a organização tem acesso, e cada família resolve para o seu membro corrente. Alias recém-lançado costuma exigir um cliente acima de certa versão mínima.
>
> **Esta página não registra o lineup de modelos, de propósito.** Ele muda mais rápido do que ela é revalidada, e o `claude-bootstrap` não pina modelo nenhum. A lista viva e autoritativa é a documentação de modelos da Anthropic, ou `GET /v1/models`.

- **Invocação**: Claude auto-delega quando task casa com description; manual via `/agents` ou `--agents` JSON
- **Persistência**: cada subagent mantém auto-memory próprio per worktree

---

## 5. Hooks — lifecycle event handlers

**Fonte**: https://code.claude.com/docs/en/hooks

- **Eventos** (lifecycle completo — **30**, verificados vs `/docs/en/hooks` em 2026-06-08):
  - **Session**: `SessionStart`, `SessionEnd`, `Setup`
  - **Turn**: `UserPromptSubmit`, `UserPromptExpansion`, `Stop`, `StopFailure`
  - **Tool**: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`
  - **Permission**: `PermissionRequest`, `PermissionDenied`
  - **Subagent/Task**: `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `TeammateIdle`
  - **Display/Notify**: `Notification`, `MessageDisplay`, `Elicitation`, `ElicitationResult`
  - **Env/FS/Worktree**: `ConfigChange`, `CwdChanged`, `FileChanged`, `InstructionsLoaded`, `WorktreeCreate`, `WorktreeRemove`
  - **Compact**: `PreCompact`, `PostCompact`

- **Tipos de handler** (5): `command` (shell), `http` (POST JSON), `mcp_tool` (chama um tool de um MCP server), `prompt` (avaliação por modelo), `agent` (spawna subagent verificador)

- **Exit codes** (handler `command`):

  | Code | Efeito |
  |---|---|
  | `0` | Sucesso; stdout parseado como JSON. Em `UserPromptSubmit`/`UserPromptExpansion`/`SessionStart`, o stdout vira contexto que Claude vê |
  | `2` | **Blocking**: stderr → Claude; bloqueia conforme o evento (`PreToolUse` bloqueia a tool, `UserPromptSubmit` rejeita o prompt, `Stop` impede parar, …) |
  | outro (`1`, `3+`) | Non-blocking — execução segue. **Exceção**: `WorktreeCreate` aborta em qualquer código ≠ 0 |

- **Configuração** em `settings.json`:
  ```json
  {
    "hooks": {
      "PreToolUse": [{
        "matcher": "Bash",
        "if": "Bash(rm *)",
        "type": "command",
        "command": "./.claude/hooks/block-rm.sh"
      }]
    }
  }
  ```

- **Matcher syntax**:
  - `"*"` = todas
  - `"Tool1|Tool2"` = exact tool names
  - Regex JS contra tool_name field

- **Locais**:
  - `~/.claude/settings.json` (user, all projects)
  - `.claude/settings.json` (projeto, shared)
  - `.claude/settings.local.json` (projeto, personal)
  - Managed settings (org)
  - Plugin `hooks/hooks.json`
  - Skill/Agent frontmatter

---

## 6. MCP — Model Context Protocol

**Fonte**: https://code.claude.com/docs/en/mcp

- **Transports**:
  - HTTP (recomendado para cloud): `claude mcp add --transport http <name> <url>`
  - SSE (streaming): `claude mcp add --transport sse <name> <url>`
  - Stdio (local processes): `claude mcp add --transport stdio <name> -- <command> [args]`

- **Scopes**:
  - **Local** (default): `~/.claude.json` per-project entry, private
  - **Project**: `.mcp.json` root, shared via git
  - **User**: `~/.claude.json` global

- **Configuração** (`.mcp.json`):
  ```json
  {
    "mcpServers": {
      "server-name": {
        "command": "/path/to/server",
        "args": ["--flag"],
        "env": {"VAR": "value"}
      }
    }
  }
  ```

- **Plugin MCP servers**: bundled em plugin `.mcp.json` ou `plugin.json`, auto-start quando plugin habilitado
- **Dynamic updates**: MCP `list_changed` notifications auto-refresh sem reconectar
- **Auto-reconnect**: HTTP/SSE até 5 tentativas com exponential backoff (1s → 2s → 4s → 8s → 16s)
- **Managed config**: admin-controlled em `managed-mcp.json` com `allowedMcpServers` / `deniedMcpServers`

---

## 7. Plugins — extensões reutilizáveis (v2025+)

**Fonte**: https://code.claude.com/docs/en/plugins

- **Definição**: diretório com `.claude-plugin/plugin.json` manifest

- **Manifest** (`.claude-plugin/plugin.json`):
  ```json
  {
    "$schema": "https://json.schemastore.org/claude-code-plugin-manifest.json",
    "name": "my-plugin",
    "displayName": "My Plugin",
    "description": "What it does",
    "version": "1.0.0",
    "author": {"name": "Your Name"},
    "homepage": "url",
    "repository": "url",
    "license": "MIT",
    "keywords": ["claude-code", "domain"],
    "defaultEnabled": false,
    "userConfig": {}
  }
  ```
  - Só `name` é obrigatório. `displayName` (≥2.1.143, pode ter espaços) · `defaultEnabled` (≥2.1.154, default `true`; `false` = instala desabilitado, opt-in via `/plugin` ou `claude plugin enable`) · `keywords[]` (discovery) · `userConfig` (entradas marcadas `sensitive` vão pro keychain) · `$schema` (ignorado no load, só p/ editor).

- **Componentes** (todos opcionais, sob a raiz do plugin):
  - `.claude-plugin/plugin.json` — o manifest
  - `skills/<name>/SKILL.md` — skills
  - `commands/*.md` — slash commands (legacy)
  - `agents/` — definições de subagents
  - `hooks/hooks.json` — event handlers
  - `.mcp.json` — configs de MCP server
  - `.lsp.json` — configs de language server
  - `monitors/monitors.json` — watchers de log em background (v2.1.105+)
  - `themes/` — `experimental.themes` (color tokens)
  - `output-styles/` — `outputStyles` (presets de estilo de resposta)
  - `bin/` — executáveis adicionados ao PATH do Bash
  - `settings.json` — settings default (`agent`, `subagentStatusLine`)
  - `README.md` e demais arquivos de apoio
  - **Skills-dir plugin**: uma pasta com `.claude-plugin/plugin.json` sob um skills dir carrega como `<name>@skills-dir` (sem marketplace). `themes`/`monitors` no top-level ainda funcionam, mas `claude plugin validate` avisa → migrar p/ `experimental.*`.

- **Versionamento**: campo `version` explícito OU auto-derive do git commit SHA
- **Test local**: `claude --plugin-dir ./my-plugin` (overrides marketplace)
- **Reload**: `/reload-plugins` pega skill/agent/hook/MCP/LSP changes sem restart
- **Namespacing**: plugin skills como `/plugin-name:skill-name` (sem conflitos)
- **Marketplace**: discovery + install built-in (community-driven)

---

## 8. Settings hierarchy — configuration scopes

**Fonte**: https://code.claude.com/docs/en/settings

- **Prioridade** (alta → baixa):
  1. **Managed** (IT-deployed, unoverridable): OS registry, plist, `/etc/claude-code/managed-settings.json`, `managed-settings.d/*.json`
  2. **CLI flags** (session-only)
  3. **Local** (`.claude/settings.local.json`, gitignored)
  4. **Project** (`.claude/settings.json`, team-shared)
  5. **User** (`~/.claude/settings.json`, all projects)

- **Settings-chave**:
  ```json
  {
    "$schema": "https://json.schemastore.org/claude-code-settings.json",
    "permissions": {
      "allow": ["Bash(npm test)", "Read(~/.zshrc)"],
      "deny": ["Bash(curl *)", "Read(./.env)"]
    },
    "env": {"CLAUDE_CODE_ENABLE_TELEMETRY": "1"},
    "companyAnnouncements": ["Welcome message"],
    "hooks": {...},
    "allowManagedHooksOnly": false,
    "allowManagedMcpServersOnly": false,
    "allowManagedPermissionRulesOnly": false
  }
  ```

- **Arquivos carregados**:
  - `CLAUDE.md` / `CLAUDE.local.md`
  - Subagents (`.claude/agents/`, `~/.claude/agents/`)
  - MCP servers (`.mcp.json`, `~/.claude.json`)
  - Plugins (enabled em settings)
  - Skills (`.claude/skills/`, `~/.claude/skills/`)

- **`claudeMdExcludes`** — glob patterns / paths absolutos de `CLAUDE.md` a **pular** ao carregar memory (ex.: `"claudeMdExcludes": ["**/vendor/**/CLAUDE.md"]`). Match contra path absoluto; aplica só a user/project/local — managed policy **não** é excluível. Em monorepo, evita carregar o `CLAUDE.md` de subprojetos vendored.

- **AGENTS.md interop** — `claude-bootstrap` emite `@AGENTS.md` no `CLAUDE.md` raiz **quando o repo já tem um `AGENTS.md`** (detectado no emit; imports `@path` resolvem ≤4 hops, relativos ao arquivo importador). Alternativa sem import, quando `AGENTS.md` deve ser a fonte única: symlink `ln -s AGENTS.md CLAUDE.md`.

- **Permission modes** (`--permission-mode` / ciclo Shift+Tab; tabela completa em `/docs/en/permission-modes`): `default`, `acceptEdits`, `plan`, `auto` (v2.1.83+, classificador de segurança em background), `dontAsk` (auto-nega o que não foi pré-aprovado; CI travado), `bypassPermissions`. `disableAutoMode: "disable"` remove `auto` do ciclo. Managed-only: `allowManagedHooksOnly` / `allowManagedMcpServersOnly` / `allowManagedPermissionRulesOnly`.

- **Novas settings keys (jun/2026, status 2026-06-29)**: `fallbackModel` (v2.1.166 — **lista** de até 3 modelos, para degradar quando o preferido estiver indisponível), `enforceAvailableModels` / `requiredMinimumVersion` / `requiredMaximumVersion` (managed), `disableBundledSkills`, `respondToBashCommands`, `teammateMode`, `footerLinksRegexes`, `autoMode.classifyAllShell`. `claude-bootstrap` **não** as emite por default; documentadas para referência.

### 8.1 Sandbox (`settings.json` → `sandbox`, **off por default**)

**Fonte**: https://code.claude.com/docs/en/sandboxing

```json
{
  "sandbox": {
    "enabled": true,
    "excludedCommands": ["docker *"],
    "filesystem": { "denyRead": ["~/.aws", "~/.ssh"], "allowWrite": ["/tmp/build"] },
    "network": { "allowedDomains": ["registry.npmjs.org"], "httpProxyPort": 8080 }
  }
}
```

- ⚠️ **O default ainda permite ler `~/.aws/credentials` e `~/.ssh/`** — adicione-os a `denyRead` para bloquear (a política default é "ler todo o computador exceto dirs negados").
- `filesystem`: `denyRead` / `denyWrite` / `allowWrite` / `allowRead` / `allowManagedReadPathsOnly`. `network`: `allowedDomains` / `deniedDomains` / `httpProxyPort` / `socksProxyPort` / `allowManagedDomainsOnly` / `enableWeakerNetworkIsolation` / `allowUnixSockets`. Outros: `failIfUnavailable`, `allowUnsandboxedCommands` (`false` = strict), `excludedCommands`.
- **Novos (jun/2026)**: `sandbox.credentials` (v2.1.187, 2026-06-23 — bloqueia leitura de arquivos + unseta env vars p/ comandos sandboxed: `{path,mode:"deny"}` / `{name,mode:"deny"}`); `sandbox.allowAppleEvents` (v2.1.181, 2026-06-17, macOS). Aprovação de host de rede é lembrada pela sessão (v2.1.191).
- Plataformas: macOS **Seatbelt**; Linux/WSL2 **bubblewrap** (+`socat` p/ rede). **Windows nativo não suportado.** Liga via `/sandbox` ou `sandbox.enabled = true`.

---

## 9. Frontmatter canonical reference

| Tipo | Local | Frontmatter | Body |
|---|---|---|---|
| **SKILL.md** | `.claude/skills/<name>/` | `name`, `description`, `when_to_use`, `arguments`, `argument-hint`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `model`, `effort`, `context` | Instruções para Claude |
| **Agent.md** | `.claude/agents/<name>.md` | `description`, `prompt` (= body), `tools`, `disallowedTools`, `model`, `permissionMode`, `mcpServers`, `hooks`, `maxTurns`, `skills`, `initialPrompt`, `memory`, `effort`, `background`, `isolation`, `color` | System prompt |
| **CLAUDE.md** | `./CLAUDE.md`, `./.claude/CLAUDE.md`, `~/.claude/CLAUDE.md` | Nenhum (markdown puro) | Instruções TODAS sessões |
| **settings.json** | `.claude/settings.json`, `~/.claude/settings.json` | JSON keys: `permissions`, `env`, `hooks`, `agent`, `allowedChannelPlugins`, etc. | N/A |
| **plugin.json** | `.claude-plugin/plugin.json` | `name`, `description`, `version`, `author`, `homepage`, `repository`, `license` | N/A |

---

## 10. Hierarquia de diretórios — onde tudo vive

**Enterprise / organização** (managed):

- `/Library/Application Support/ClaudeCode/` (macOS)
  - `CLAUDE.md` — instruções org-wide
  - `managed-settings.json` — política da org (não sobrescrevível)
- `/etc/claude-code/` (Linux/WSL)
- `C:\Program Files\ClaudeCode\` (Windows)

**User** (pessoal, todos os projetos) — `~/.claude/`:

- `CLAUDE.md` — instruções pessoais
- `settings.json` — settings pessoais
- `skills/<name>/SKILL.md`
- `agents/<name>.md`
- `keybindings.json`
- `plugins/` — plugins instalados
- `projects/<path>/` — estado por projeto
  - `memory/` — auto-memory
  - `mcpServers.json`

**Project** (time, repo atual) — raiz do repo:

- `CLAUDE.md` — instruções do time (versionado)
- `.claude/`
  - `settings.json` — settings do time
  - `settings.local.json` — overrides pessoais (gitignored)
  - `CLAUDE.md` — instruções de projeto, alternativa à raiz
  - `skills/<name>/SKILL.md`
  - `agents/<name>.md`
  - `rules/<path>*.md` — path-scoped rules (Q2/2026)
  - `hooks/*.sh`, `hooks/*.py`
  - `plugins/` — teste local de plugin
- `.mcp.json` — MCP servers do projeto (versionado)
- `Subdir/.claude/` — nested (monorepo)

**Local** (só a sessão atual) — na raiz ou numa subpasta:

- `CLAUDE.local.md` — notas pessoais (gitignored)

---

## 11. Breaking changes & new features (jan/2025 – jun/2026)

**Fonte**: https://code.claude.com/docs/en/overview + https://code.claude.com/docs/llms.txt

- **Q4 2025 / Q1 2026**: Plugins system launched (`.claude-plugin/` manifest, marketplace discovery, namespaced skills)
- **Início 2026**: Skills lifted para Agent Skills open standard (https://agentskills.io/) — funciona cross-tool
- **Q2 2026**: Auto-memory expandido para subagents (cada um mantém memory per worktree)
- **Q2 2026**: Nested `.claude/` discovery em monorepos (`packages/*/.claude/skills/` auto-loaded)
- **Q2 2026**: Path-scoped rules (`.claude/rules/<path>*.md`) — substitui CLAUDE.md monolítico
- **Q2 2026**: Agent SDK documentation (separado do CLI, para construir agents production)
- **Q2 2026 (mai–jun)**: Agent teams + background agents (`/agent-view`); forked subagents; bundled skills `/run` `/verify` `/run-skill-generator` (v2.1.145+); auto permission mode (background classifier); MCP Tool Search (default on, `ENABLE_TOOL_SEARCH`); **Dynamic workflows** (v2.1.154+, docs live já sem rótulo "research preview", sem GA declarado): scripts **JavaScript** que orquestram subagents em escala — Claude os escreve, salvos via `/workflows`→`s` em `.claude/workflows/` (projeto) ou `~/.claude/workflows/` (home), rodados como `/<name>` (`/deep-research` é o bundled; trigger `ultracode`); **não são markdown estático** → claude-bootstrap não emite workflows. Distintas de **Routines** (`/schedule`, agents remotos em infra Anthropic) + `/loop` (repete prompt na sessão); Channels (Telegram/Discord/webhooks); interactive `/init` via `CLAUDE_CODE_NEW_INIT=1`; auto-memory (v2.1.59+, `~/.claude/projects/<project>/memory/MEMORY.md`)
- **Lineup de modelos**: deliberadamente não registrado aqui — ver a nota em §4 e a fonte viva. Os aliases da flag `--model`, esses sim estáveis, estão em §4.
- **Sem breaking changes** em CLAUDE.md, Skills, Hooks, MCP schemas entre jan/2025 – jun/2026

### 11.1 Workflows & routines — fronteira do que `claude-bootstrap` emite

- **Workflows** (`.claude/workflows/`) são **scripts JavaScript de orquestração** de subagents que **Claude escreve** para uma tarefa e o usuário salva de um run via `/workflows`→`s` (v2.1.154+; os docs live deixaram de rotular "research preview" — mas também **não** declaram GA; disponível em planos pagos + API/Bedrock/Vertex; `/deep-research` é o bundled; limites: ≤16 concorrentes, 1000 agents/run). São gerados pelo modelo, **não** templates estáticos → **`claude-bootstrap` não os emite** (escrever um à mão seria um artefato inválido).
- **Routines** (`/schedule`) rodam em infra Anthropic (server-side) → também **não-emittable** por um scaffolder estático.
- `claude-bootstrap` emite só a **camada estática** (CLAUDE.md, settings, skills/agents/rules/output-styles); Workflows e Routines o usuário cria sob demanda dentro do próprio Claude Code.

---

## 12. Lacunas documentadas (gaps em docs oficiais)

1. **Skill invocation control**: docs mencionam mas detalhes esparsos sobre `allowed-tools` × permission system
2. **Hook async patterns**: command/HTTP error handling e timeout under-documented
3. **Plugin marketplace**: discovery mencionado mas sem URL/listing oficial documentado
4. **Monorepo best practices**: nested `.claude/` discovery descrito, mas patterns shared vs per-package não detalhados
5. **Memory size limits**: "25KB" e "200 linhas" mencionados mas reconciliação unclear
6. **Subagent memory durability**: edge cases (fork, resume, clear) under-specified
7. **MCP server diagnostics**: `/mcp` panel mostra tool count mas troubleshooting "tools desaparecendo mid-session" sem guia
8. **Managed settings distribution**: MDM templates em GitHub repo, mas sem versioning ou rollback strategy

---

## 13. Segurança & trust boundary (jun/2026)

**Fontes**: GHSA-4fgq-fpq9-mr3g (CVE-2025-59536), GHSA-jh7p-qr78-84p7 (CVE-2026-21852), adversa.ai, snyk.io.

- **Trust boundary (pre-trust-dialog)**: ao abrir/clonar um repo, o Claude Code carrega `.claude/settings.json` + init (incl. hooks). CVE-2025-59536 (fix v1.0.111) mostrou execução **antes** do trust dialog → um `.claude/` malicioso de terceiros é superfície de RCE. **`claude-bootstrap` emite um settings.json benigno** — isto **não é uma vuln nossa**, mas é a razão de (a) recomendar uma versão atual do Claude Code e (b) tratar `.claude/` de terceiros como código não-confiável.
- **Versão mínima recomendada**: rode uma **versão estável atual** do Claude Code (≥ v2.1.x; última estável v2.1.195 em 2026-06-29). As classes conhecidas de bypass de deny-rule (cap de 50 subcomandos, fix v2.1.90) e de pre-trust-dialog foram corrigidas bem antes; mantenha atualizado (fato time-sensitive).
- **Deny rules = defesa-em-profundidade, não barreira única**: regras `Read(**/...)` (path-based) são robustas; regras `Bash(...)` dependem do parser do cliente (protegidas em ≥v2.1.90). Combine com `sandbox` (denyRead `~/.aws`/`~/.ssh`) + o `auto` mode hardening.
- **Supply-chain de skills**: 36,8% das skills do ClawHub têm ≥1 flaw de segurança (Snyk, fev/2026; 1ª campanha coordenada de skills maliciosas). **Vete qualquer skill de terceiros antes de instalar**; prefira bundles provenance-pinned. O subcomando `claude-bootstrap audit` (provenance + integridade) e a skill `vetting-agent-skills` existem exatamente para isto.

---

## 14. URLs e entrypoints oficiais

- **Main docs**: https://code.claude.com/docs/en/overview
- **Documentation index**: https://code.claude.com/docs/llms.txt
- **Installation**: `curl -fsSL https://claude.ai/install.sh | bash` (macOS/Linux/WSL)
- **CLI install**: `brew install --cask claude-code` ou `winget install Anthropic.ClaudeCode`
- **Web Claude Code**: https://claude.ai/code
- **VS Code extension**: https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code
- **JetBrains plugin**: https://plugins.jetbrains.com/plugin/27310-claude-code-beta-
- **Examples repo** (MDM templates, etc.): https://github.com/anthropics/claude-code

---

**Takeaway**: Padrão canônico Claude Code centra em **escopo hierárquico** (managed > user > project > local), **lazy loading** (skills & subagents carregam só quando invocados), e **composability** (plugins agregam skills + agents + hooks + MCP servers como unidades reutilizáveis). Toda config é markdown ou JSON — sem binários compilados. Sistema lê árvore para cima ao iniciar, depois desce on-demand para subdiretórios — habilitando monorepos e nested team structures sem imports explícitos.
