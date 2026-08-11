# Estado da arte: práticas Claude Code (jan/2025 – jun/2026)

> Documentação canônica do projeto. Fontes externas validadas por último em **2026-06-02** (SOTA refresh jun/2026 — ver §7.2); as contagens de stars do GitHub em §4 e §7.1 foram remedidas em **2026-08-02** via API do GitHub (`obra/superpowers` remedido em **2026-08-10**). 36 fontes únicas, listadas em §8: docs Anthropic, Reddit, HN, X, Medium, GitHub, TechCrunch.
>
> 🇬🇧 [English version](../02-state-of-the-art.md) — the canonical copy.

---

## 1. Padrão consensual (>70% das fontes)

| Prática | Consenso | Fontes |
|---------|----------|--------|
| **CLAUDE.md como foundation** | Markdown único ~100-300 linhas, carregado toda sessão, com instruções estáveis (código, workflow, gotchas) | [Docs oficiais](https://code.claude.com/docs/en/best-practices), [Bruniaux 2026](https://github.com/FlorianBruniaux/claude-code-ultimate-guide), [Marmelab 2026](https://marmelab.com/blog/2026/04/24/claude-code-tips-i-wish-id-had-from-day-one.html) |
| **Hierarquia .claude/** | `~/.claude/CLAUDE.md` (global) + `./CLAUDE.md` (projeto) + `./CLAUDE.local.md` (gitignored); subpastas: agents/, skills/, hooks/, commands/, plugins/ | [Docs Claude Directory 2026](https://code.claude.com/docs/en/claude-directory), [codewithmukesh 2026](https://codewithmukesh.com/blog/anatomy-of-the-claude-folder/) |
| **Concisão é crítica** | Remover linha que Claude não violaria; >300 linhas causa Claude ignorar; ~100 linhas estilo Karpathy/Cherny | [Docs oficiais](https://code.claude.com/docs/en/best-practices), [mindwiredai 2026](https://mindwiredai.com/2026/03/25/claude-code-creator-workflow-claudemd/) |
| **Plan mode padrão** | Usar `/plan` para 3+ passos; separar exploração → planning → implementação | [Docs oficiais best practices](https://code.claude.com/docs/en/best-practices), [shanraisshan 2026](https://github.com/shanraisshan/claude-code-best-practice) |
| **Verificação auto-suficiente** | Claude verifica próprio trabalho: testes, screenshots, linters; highest-leverage pattern | [Docs oficiais](https://code.claude.com/docs/en/best-practices), [Marmelab 2026](https://marmelab.com/blog/2026/04/24/claude-code-tips-i-wish-id-had-from-day-one.html) |
| **Memory 4-camadas** | CLAUDE.md (estável) + auto-memory (atual) + camada de estado (`MEMORY.md` na convenção da comunidade; `claude-bootstrap` emite como `PROJECT-STATE.md` p/ evitar colisão — ver §7.2 Auto-memory) + CONTEXT.md (handoff) | [Knight 2026](https://www.knightli.com/en/2026/04/23/claude-code-claude-md-rules-memory-hooks-guide/) |
| **Hooks para enforcing** | `.claude/settings.json` com PreToolUse/PostToolUse/Stop; determinístico (exit 0/2), não advisory | [Docs hooks guide](https://code.claude.com/docs/en/hooks-guide), [MindStudio 2026](https://www.mindstudio.ai/blog/self-evolving-claude-code-memory-obsidian-hooks) |
| **Subagents para isolamento** | `/agents` para delegação complexa; fresh context, tool restrictions via frontmatter YAML | [Docs subagents](https://code.claude.com/docs/en/sub-agents), [Anthropic whitepaper 2026](https://resources.anthropic.com/hubfs/Claude%20Code%20Advanced%20Patterns_%20Subagents,%20MCP,%20and%20Scaling%20to%20Real%20Codebases.pdf) |
| **MCP como bridge externo** | Model Context Protocol = USB-C para AI; oficial, aberto; conecta BD, APIs, Notion, Figma, CLI tools | [Docs MCP](https://code.claude.com/docs/en/mcp), [Anthropic engineering 2026](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) |
| **Git workflow integrado** | Commit early, verificar com git status, usar `/pr` para PRs | [Docs best practices](https://code.claude.com/docs/en/best-practices) |

---

## 2. Práticas emergentes (30-50% adoção)

| Prática | Status | Observação | Fonte |
|---------|--------|-----------|-------|
| **Skills como modularidade** | Maturando; debate: nem sempre Claude invoca (probabilístico) | SKILL.md em `.claude/skills/`; útil quando CLAUDE.md não escala; falha de reliability é ponto fraco | [MindStudio 2026](https://www.mindstudio.ai/blog/claude-code-memory-systems-compared), [Hightower 2026](https://medium.com/@richardhightower/save-hours-stop-repeating-yourself-to-claude-skills-rules-memory-and-when-to-use-each-93ce3cf83aa8) |
| **Auto-memory persistência** | Experimental; `/memory` command; não universalizado | Alguns projetos usam Obsidian + hooks para capture automático; sem standard oficial | [MindStudio hooks 2026](https://www.mindstudio.ai/blog/self-evolving-claude-code-memory-obsidian-hooks), [johnoct 2026](https://johnoct.com/blog/2026/02/14/claude-mem-persistent-memory-for-claude-code/) |
| **Plugins como composable extensions** | Adotando; ~5k+ no registry Anthropic mai/2026 | Bundlam skills + hooks + MCP; one-click install via `/plugin` | [Anthropic plugins oficial](https://github.com/anthropics/claude-plugins-official), [Plugins docs](https://code.claude.com/docs/en/plugins) |
| **Agentic engineering patterns** | Documentação iniciada; Simon Willison liderando | Coloca padrões vivos; não congelados em lançamento | [simonwillison.net agentic patterns](https://simonw.substack.com/p/agentic-engineering-patterns) |
| **Session renaming + resumption** | Low-friction branching; `/rename` + `claude --continue` | Workflow branch-like para múltiplas threads | [Docs sessions](https://code.claude.com/docs/en/sessions) |
| **Sandbox mode** | Lançado recente; maturando | OS-level isolation, `claude --sandbox` | [Docs permission modes](https://code.claude.com/docs/en/permission-modes) |
| **Superpowers framework** | ~270k stars (medido em 2026-08-10); cross-tool (Cursor, Codex, Gemini) | Agentic skills framework, methodology; tornou-se de facto standard | [Medium Anil Mathew abr/2026](https://medium.com/@anilmathewm/i-gave-claude-code-a-brain-its-called-superpowers), [GitHub obra/superpowers](https://github.com/obra/superpowers) |

---

## 3. Anti-patterns (rejeitados/ineficazes)

| Anti-pattern | Por que falha | Fonte |
|--------------|---------------|-------|
| **CLAUDE.md >500 linhas** | Claude ignora regras importantes no noise; rules se perdem | [Docs best practices](https://code.claude.com/docs/en/best-practices), [Babich UXPlanet 2026](https://uxplanet.org/claude-md-best-practices-1ef4f861ce7c) |
| **"Kitchen sink session"** | Misturar 3+ tasks não-relacionadas → context pollution | [Docs best practices](https://code.claude.com/docs/en/best-practices); fix: `/clear` entre tasks |
| **Ciclo fix-fail-propose infinito** | Claude propõe new bugs para mesma issue → bug list cresce, progresso = 0 | [GitHub issue #51856](https://github.com/anthropics/claude-code/issues/51856) |
| **Negação em CLAUDE.md** | "Do NOT use semicolons" ativa o conceito; modelo luta com negação | [Knightli 2026](https://www.knightli.com/en/2026/04/19/karpathy-claude-md-ai-coding-rules/); use positivo "Use ASI instead" |
| **Over-engineering patterns** | Modelo converte problemas simples em complex; factory patterns, abstract classes desnecessárias → tech debt | [Dev.to 2026](https://dev.to/docat0209/5-patterns-that-make-claude-code-actually-follow-your-rules-44dh) |
| **Skills como silver bullet** | Skill pode não invocar (probabilístico); <70% reliability em padrão de linguagem | [MindStudio memory comparison 2026](https://www.mindstudio.ai/blog/claude-code-memory-systems-compared) |
| **Memory system não integrado** | Misturar CLAUDE.md + MEMORY.md + auto-memory sem hierarquia clara → conflito | [Amit Ray 2026](https://amitray.com/claude-md-vs-agents-md-memory-md-skills-md-context-md-guide-2026/) |
| **Hooks sem exit codes** | Script sem validação → falsas positivos, segurança reduzida | [Docs hooks guide](https://code.claude.com/docs/en/hooks-guide) |

---

## 4. Frameworks & templates emergentes

| Nome | Repo | Stars | Foco | Status |
|------|------|-------|------|--------|
| **Superpowers** | [obra/superpowers](https://github.com/obra/superpowers) | ~270k | Agentic skills framework + methodology; cross-tool | Ativo, crescendo rápido |
| **Claude Code Best Practice** | [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) | 63.896 | Vibe coding → agentic engineering patterns | Ativo |
| **Claude Code Ultimate Guide** | [FlorianBruniaux/claude-code-ultimate-guide](https://github.com/FlorianBruniaux/claude-code-ultimate-guide) | 5.639 | Production-ready templates, quizzes, cheatsheet | Ativo |
| **Awesome Claude Code Toolkit** | [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit) | 2.433 | 135 agents, 35 skills, 176+ plugins, 20 hooks, 7 templates | Ativo, curated |
| **VILA-Lab / Dive into Claude Code** | [VILA-Lab/Dive-into-Claude-Code](https://github.com/VILA-Lab/Dive-into-Claude-Code) | 2.015 | Análise sistemática do design do Claude Code | Ativo |
| **dotclaude** | [poshan0126/dotclaude](https://github.com/poshan0126/dotclaude) | 839 | Standard `.claude/` folder structure | Ativo |

Stars medidas em 2026-08-02 pela API do GitHub, exceto `obra/superpowers` (~270k), remedida em 2026-08-10 e mantida em sincronia com [`07-glossary.md`](07-glossary.md) e [`00-overview.md`](00-overview.md). Contagem de star é fato datado, não propriedade do projeto — remeça antes de citar em qualquer outro lugar.

---

## 5. Recursos canônicos (tier de relevância)

### Tier 1: Documentação oficial Anthropic
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices) — atualizado mai/2026
- [Claude Code Memory Guide](https://code.claude.com/docs/en/memory) — official 4-layer model
- [Subagents Guide](https://code.claude.com/docs/en/sub-agents) — official patterns
- [MCP Documentation](https://code.claude.com/docs/en/mcp) — Model Context Protocol spec
- [Hooks Guide](https://code.claude.com/docs/en/hooks-guide) — lifecycle event automation
- [Plugins Marketplace](https://github.com/anthropics/claude-plugins-official) — official registry

### Tier 2: Comunidade de alta autoridade
- [Simon Willison / Agentic Engineering Patterns](https://simonw.substack.com/p/agentic-engineering-patterns) — living docs
- [Anthropic Advanced Patterns Whitepaper](https://resources.anthropic.com/hubfs/Claude%20Code%20Advanced%20Patterns_%20Subagents,%20MCP,%20and%20Scaling%20to%20Real%20Codebases.pdf) — official technical deep-dive
- [Superpowers Framework](https://github.com/obra/superpowers) — de facto standard cross-tool
- [Claude Code Ultimate Guide (Bruniaux)](https://github.com/FlorianBruniaux/claude-code-ultimate-guide) — comprehensive

### Tier 3: Posts & análises especializadas
- [Marmelab: Claude Code Tips I Wish I'd Had](https://marmelab.com/blog/2026/04/24/claude-code-tips-i-wish-id-had-from-day-one.html) — abr/2026
- [MindStudio Memory Systems Comparison](https://www.mindstudio.ai/blog/claude-code-memory-systems-compared)
- [DEV Community: 5 Patterns That Make Claude Code Follow Rules](https://dev.to/docat0209/5-patterns-that-make-claude-code-actually-follow-your-rules-44dh)
- [Amit Ray: Claude.md vs Agents.md vs Memory.md Hierarchy](https://amitray.com/claude-md-vs-agents-md-memory-md-skills-md-context-md-guide-2026/)

### Tier 4: Dados estatísticos
- [Pragmatic Engineer Survey Feb 2026](https://claude5.ai/news/developer-survey-2026-ai-coding-73-percent-daily) — 15k devs, 73% daily usage, Claude Code 46% "most loved" (números como publicados em fev/2026; não reverificados aqui)
- [Claude Code Statistics 2026](https://www.gradually.ai/en/claude-code-statistics/) — market data, ARR $2.5B (como publicado; não reverificado aqui)

---

## 6. Tensões não resolvidas & debates abertos

1. **Skills confiabilidade**: Skills são probabilísticas; comunidade debate se CLAUDE.md bem-escrito é suficiente vs overhead de skills. Sem standard emergente; depende caso-a-caso.

2. **Memory hierarchy tradeoffs**: Mundo converge para 4-camadas mas não há consenso sobre order/precedence ótima.

3. **Hooks vs permission allowlists**: Debate entre enforcement via hooks (determinístico) vs auto mode + allowlists (UX melhor, segurança reduzida). Nenhum ganhou.

4. **Subagent overhead**: Subagents isolam context (bom) mas adicionam latência & complexity. Métricas de "quando usar" ainda empíricas.

5. **MCP server discovery**: 5k+ servidores no registry em mai/2026; comunidade quer curadores/recomendações oficiais. Atual é ruído alto.

6. **Non-interactive automation escalability**: Claude Code escala paralelo bem (multi-session, fan-out) mas custo é barreira — as fontes de mai/2026 põem heavy users em ~$15-20/dia.

7. **Agentic patterns divergem de traditional SWE**: SOLID/DRY às vezes conflitam com necessidades agentic (explicit over implicit). Community explorando novo ruleset.

8. **Plugins vs Skills vs Subagents taxonomy**: Distinções fuzzy; comunidade pede clareza em "quando usar qual".

---

## 7. Resumo: convergiu vs ainda flutua

**Convergiu (>85% consenso mai/2026):**
- CLAUDE.md ~100-300 linhas é padrão ouro
- Hierarquia `.claude/` com agents/, skills/, hooks/ é canônica
- Plan mode para 3+ passos
- 4-camadas de memory
- Hooks para enforcement determinístico
- Subagents para isolamento
- MCP como bridge externo oficial

**Ainda emergente (30-50%):**
- Skills trigger reliability
- Auto-memory persistence
- Plugins market saturation
- Agentic patterns framework

**Quadro geral:**
Comunidade evoluiu de "vibe coding" (jan/2025) para **metodologia agentic estruturada** (mai/2026). Superpowers (~270k stars, medido em 2026-08-10) virou lingua franca. Anthropic oficializou skills (out/2025) + plugins (mar/2026) + MCP. Tensão entre simplicidade (CLAUDE.md puro) vs modularidade (skills/plugins) segue sem resolução definitiva.

---

## 7.1. Ecosistema de skills community-curated (mai/2026)

Fora `anthropics/skills` (o upstream canônico), o ecosistema community produziu coleções MIT-redistribuíveis que servem como base para profiles especializados:

| Coleção | Stars | Skills (count) | Domínio | Licença | Citação |
|---|---|---|---|---|---|
| `forrestchang/andrej-karpathy-skills` | 198.785 | 1 (`karpathy-guidelines`) | LLM coding behavior meta | MIT | https://github.com/forrestchang/andrej-karpathy-skills |
| `K-Dense-AI/scientific-agent-skills` | 32.404 | 137 (em `scientific-skills/`) | Pesquisa científica, química, biologia, citação, IMRAD | MIT | https://github.com/K-Dense-AI/scientific-agent-skills |
| `alirezarezvani/claude-skills` | 23.658 | 625 total; 41 engineering/, 32 engineering-team/, 16 ra-qm-team/ | DevOps, Frontend, Data-science, ML, Security, Compliance | MIT | https://github.com/alirezarezvani/claude-skills |

**Curated indices** (não consumidos diretamente como skill, citados como ecosystem reference):

| Index | Stars | Foco | Citação |
|---|---|---|---|
| `Shubhamsaboo/awesome-llm-apps` | 129.840 | 100+ AI agent / RAG apps prontos pra rodar | https://github.com/Shubhamsaboo/awesome-llm-apps |
| `punkpeye/awesome-mcp-servers` | 91.737 | Coleção de servidores MCP | https://github.com/punkpeye/awesome-mcp-servers |
| `hesreallyhim/awesome-claude-code` | 51.537 | Curated index: skills, hooks, slash-commands, plugins | https://github.com/hesreallyhim/awesome-claude-code |

**MCPs notáveis** (Q2/2026):

- `ChromeDevTools/chrome-devtools-mcp` (48.388 stars) — Chrome DevTools para coding agents

As stars desta seção foram medidas em 2026-08-02 pela API do GitHub. As contagens de skills vêm do levantamento de mai/2026 e não foram recontadas.

`claude-bootstrap` v1.0.0 incorpora skills selecionadas destas fontes nos profiles `frontend`, `data-science`, `devops`, `backend` e `academic` — sempre preservando licença e atribuição original na frontmatter da SKILL.md copiada (compliance MIT).

---

## 7.2. Atualizações jun/2026 (SOTA refresh)

Validação primária contra `code.claude.com/docs/en` (jun/2026). Novidades desde mai/2026, relevantes pra posicionamento de tooling de bootstrap:

| Feature | O que é | Impacto p/ scaffolders |
|---|---|---|
| **`/init` interativo** (`CLAUDE_CODE_NEW_INIT=1`) | Multi-fase: entrevista + exploração por subagente + proposta revisável de CLAUDE.md/skills/hooks; idempotente | **Competidor direto** de tools de bootstrap; ainda opt-in (env-gated), não default |
| **Agent teams + background agents** | lead coordena subagentes; sessões paralelas monitoradas (`/agent-view`) | Orquestração nativa; reduz necessidade de wrappers externos |
| **Forked subagents** | `context: fork` (skills) + fork da conversa atual | — |
| **Bundled skills `/run` `/verify` `/run-skill-generator`** | rodar/verificar o app; gravar recipe em `.claude/skills/run-<name>/` (v2.1.145+) | UX de "ver rodar" agora nativa |
| **Auto permission mode** | classificador em background avalia comandos/escritas | alternativa a allowlists estáticas |
| **MCP Tool Search** | default on; tools deferidas, carregadas on-demand (`ENABLE_TOOL_SEARCH`) | escala MCP sem inflar contexto |
| **Routines + `/loop`** | cron Anthropic-managed (`/schedule`) + polling in-session | — |
| **Channels** | Telegram/Discord/webhooks empurram eventos pra sessão | — |
| **Auto-memory** (v2.1.59+) | Claude escreve `~/.claude/projects/<project>/memory/MEMORY.md` | colisão de nome com `MEMORY.md` emitido por scaffolders — `claude-bootstrap` resolve emitindo `PROJECT-STATE.md` (nome distinto) |

Model lineup como registrado na checagem de 2026-06-29: Opus 4.8 (`claude-opus-4-8`), Sonnet 4.6 (`claude-sonnet-4-6`) e Haiku 4.5 (`claude-haiku-4-5-20251001`), com Fable 5 e Mythos 5 (`claude-fable-5`/`claude-mythos-5`) em GA desde 2026-06-09. Trate isso como um retrato datado, não como o lineup atual: ele muda mais rápido do que este documento é revalidado, e o `claude-bootstrap` deliberadamente não pina modelo nenhum. Os aliases da flag `--model` estão em `01-canonical-anthropic.md` §4; a lista viva e autoritativa é a documentação de modelos da Anthropic, ou `GET /v1/models`.

> **Implicação p/ `claude-bootstrap`**: o diferencial não é "gerar um CLAUDE.md" (o `/init` nativo já faz), e sim profiles opinativos + bundles MIT auditados + baseline de permissions + distribuição via plugin/marketplace.

---

## 8. Fontes

36 URLs únicas validadas.

1. https://code.claude.com/docs/en/best-practices
2. https://github.com/FlorianBruniaux/claude-code-ultimate-guide
3. https://marmelab.com/blog/2026/04/24/claude-code-tips-i-wish-id-had-from-day-one.html
4. https://code.claude.com/docs/en/claude-directory
5. https://codewithmukesh.com/blog/anatomy-of-the-claude-folder/
6. https://mindwiredai.com/2026/03/25/claude-code-creator-workflow-claudemd/
7. https://github.com/shanraisshan/claude-code-best-practice
8. https://www.knightli.com/en/2026/04/23/claude-code-claude-md-rules-memory-hooks-guide/
9. https://code.claude.com/docs/en/hooks-guide
10. https://www.mindstudio.ai/blog/self-evolving-claude-code-memory-obsidian-hooks
11. https://code.claude.com/docs/en/sub-agents
12. https://resources.anthropic.com/hubfs/Claude%20Code%20Advanced%20Patterns_%20Subagents,%20MCP,%20and%20Scaling%20to%20Real%20Codebases.pdf
13. https://code.claude.com/docs/en/mcp
14. https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
15. https://www.mindstudio.ai/blog/claude-code-memory-systems-compared
16. https://medium.com/@richardhightower/save-hours-stop-repeating-yourself-to-claude-skills-rules-memory-and-when-to-use-each-93ce3cf83aa8
17. https://simonw.substack.com/p/agentic-engineering-patterns
18. https://medium.com/@anilmathewm/i-gave-claude-code-a-brain-its-called-superpowers
19. https://github.com/obra/superpowers
20. https://dev.to/docat0209/5-patterns-that-make-claude-code-actually-follow-your-rules-44dh
21. https://amitray.com/claude-md-vs-agents-md-memory-md-skills-md-context-md-guide-2026/
22. https://github.com/anthropics/claude-plugins-official
23. https://claude5.ai/news/developer-survey-2026-ai-coding-73-percent-daily
24. https://github.com/VILA-Lab/Dive-into-Claude-Code
25. https://github.com/anthropics/skills
26. https://github.com/K-Dense-AI/scientific-agent-skills
27. https://github.com/alirezarezvani/claude-skills
28. https://github.com/forrestchang/andrej-karpathy-skills
29. https://github.com/hesreallyhim/awesome-claude-code
30. https://github.com/Shubhamsaboo/awesome-llm-apps
31. https://github.com/punkpeye/awesome-mcp-servers
32. https://github.com/ChromeDevTools/chrome-devtools-mcp
33. https://github.com/langchain-ai/langchain
34. https://github.com/crewAIInc/crewAI
35. https://github.com/ollama/ollama
36. https://github.com/qdrant/qdrant
