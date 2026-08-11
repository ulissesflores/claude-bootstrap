# Anti-patterns Claude Code

> Doc canônico de práticas a evitar. Fontes externas validadas por último em 2026-05-05; o item 10 foi corrigido contra o código deste repo em 2026-07-29. Fonte primária: [02-state-of-the-art.md §3](02-state-of-the-art.md#3-anti-patterns-rejeitadosineficazes).
>
> 🇬🇧 [English version](../03-anti-patterns.md) — the canonical copy.

---

## 1. CLAUDE.md >500 linhas

**Por que falha**: Claude carrega o arquivo inteiro no contexto, mas com >300 linhas a atenção ao conteúdo degrada exponencialmente — regras críticas se perdem no ruído de regras triviais. >500 linhas garante que a maioria das instruções seja ignorada na prática.

**Sintoma**: Claude viola regras que estão explicitamente escritas; você precisa repetir no prompt o que já está no `CLAUDE.md`; o arquivo cresce a cada sessão porque "talvez desta vez funcione".

**Como evitar**: Manter `CLAUDE.md` enxuto (~60 linhas, máx ~140-150) com apenas o que Claude violaria sem instrução. Extrair regras domain-specific para `.claude/rules/<scope>*.md` (path-scoped, padrão Q2/2026 — ver [01-canonical-anthropic.md §1](01-canonical-anthropic.md#1-memory-system--claudemd--auto-memory)). Deletar qualquer linha que Claude seguiria naturalmente.

**Fonte**: [Docs oficiais best practices](https://code.claude.com/docs/en/best-practices), [Babich UXPlanet 2026](https://uxplanet.org/claude-md-best-practices-1ef4f861ce7c)

---

## 2. "Kitchen sink session" (Context Pollution)

**Por que falha**: Claude mantém estado da conversa inteira. Misturar 3+ tasks não-relacionadas contamina o contexto: variáveis de uma task vazam para outra, o plano mental de Claude confunde objetivos, e mensagens de erro de task A interferem no raciocínio da task B.

**Sintoma**: Claude começa a misturar assuntos — referencia arquivos da task anterior ao trabalhar na atual; sugestões ficam genéricas demais; sessão longa produz outputs cada vez menos coerentes.

**Como evitar**: Uma sessão = uma task coesa. Usar `/clear` entre tasks não-relacionadas. Para trabalho paralelo genuíno, usar subagents com contexto isolado (ver [01-canonical-anthropic.md §4](01-canonical-anthropic.md#4-subagents--specialized-ai-assistants)) ou `claude --continue` com sessões nomeadas distintas.

**Fonte**: [Docs oficiais best practices](https://code.claude.com/docs/en/best-practices)

---

## 3. Ciclo fix-fail-propose infinito (Infinite Debug Loop)

**Por que falha**: Quando Claude não resolve um bug em 2-3 tentativas, entra em modo de "exploração de hipóteses" que frequentemente introduz novos problemas enquanto tenta corrigir o original. A lista de bugs cresce; progresso líquido é zero ou negativo.

**Sintoma**: Você está no turno 20+ tentando resolver o mesmo erro; cada "fix" gera 2 novos problemas; Claude passa a sugerir mudanças arquiteturais para um bug de tipagem.

**Como evitar**: Definir critério de parada explícito antes de iterar: "máximo 3 tentativas; se falhar, fazer rollback e reabrir como `/plan`". Usar `/clear` + contexto mínimo reproduzível. Se persistir após 3 trocas, escrever test que reproduz o bug antes de tentar corrigir. Ver [07-glossary.md §Plan mode](07-glossary.md#plan-mode).

**Fonte**: [GitHub issue #51856](https://github.com/anthropics/claude-code/issues/51856)

---

## 4. Negação em CLAUDE.md ("Do NOT")

**Por que falha**: Modelos de linguagem processam negação de forma instável — "Do NOT use semicolons" ativa o conceito "semicolons" no raciocínio antes de negar. Em contextos longos ou tarefas complexas, a negação é esquecida e o comportamento proibido ocorre. Quanto mais negações no arquivo, maior o risco de conflito interno.

**Sintoma**: Regras do tipo "Do NOT X" são violadas com frequência desproporcional às regras afirmativas; você encontra o comportamento proibido exatamente onde havia a instrução negativa mais proeminente.

**Como evitar**: Reescrever toda instrução negativa como instrução afirmativa de comportamento desejado. Em vez de "Do NOT use semicolons" → "Use ASI (Automatic Semicolon Insertion) — omit trailing semicolons". Em vez de "Do NOT commit to main" → "Always commit to feature branches". Ver [07-glossary.md §CLAUDE.md](07-glossary.md#claudemd).

**Fonte**: [Knightli 2026](https://www.knightli.com/en/2026/04/19/karpathy-claude-md-ai-coding-rules/)

---

## 5. Over-engineering patterns (Complexidade Desnecessária)

**Por que falha**: Claude tem viés de treinamento para padrões "bem estruturados" — factory methods, abstract classes, dependency injection — porque esses padrões aparecem em codebases grandes de treinamento. Para problemas simples, o modelo usa o padrão mais "correto" que conhece, não o mais simples que resolve.

**Sintoma**: Uma função de 10 linhas vira uma hierarquia de classes; uma config hardcoded vira um sistema de plugins; um script descartável recebe error handling enterprise-grade. Tech debt cresce sem feature equivalente.

**Como evitar**: Instruir explicitamente no `CLAUDE.md` do projeto: "Write the minimum code that solves the problem. No abstractions for single-use code. No configurability unless asked." Para tarefas específicas, ancor no prompt: "solve this with a function, not a class hierarchy". Ver [02-state-of-the-art.md §7](02-state-of-the-art.md#7-resumo-convergiu-vs-ainda-flutua) sobre tensão SOLID vs agentic patterns.

**Fonte**: [DEV Community 2026](https://dev.to/docat0209/5-patterns-that-make-claude-code-actually-follow-your-rules-44dh)

---

## 6. Skills como silver bullet (Invocação Probabilística)

**Por que falha**: Skills são invocadas por Claude quando o `description` e `when_to_use` no frontmatter fazem match semântico com a task — mas esse match é probabilístico, não determinístico. Claude não lê skills preventivamente; só invoca se o trigger faz sentido no contexto imediato. Reliability documentada: <70% em padrões de linguagem natural.

**Sintoma**: Você criou uma skill para enforcement de regra crítica, mas Claude continua violando a regra porque não invocou a skill. Você percebe que o comportamento muda dependendo de como você formula o prompt.

**Como evitar**: Para enforcement **determinístico**, usar hooks (`PreToolUse`, `PostToolUse`) — ver [01-canonical-anthropic.md §5](01-canonical-anthropic.md#5-hooks--lifecycle-event-handlers). Skills são adequadas para procedimentos opcionais de alto valor que o usuário invoca explicitamente via `/skill-name`. Não depender de auto-invocação para regras de segurança, estilo ou compliance. Ver [07-glossary.md §Skill](07-glossary.md#skill).

**Fonte**: [MindStudio memory comparison 2026](https://www.mindstudio.ai/blog/claude-code-memory-systems-compared), [Hightower 2026](https://medium.com/@richardhightower/save-hours-stop-repeating-yourself-to-claude-skills-rules-memory-and-when-to-use-each-93ce3cf83aa8)

---

## 7. Memory system não integrado (Conflito de Camadas)

**Por que falha**: Quando `CLAUDE.md`, `PROJECT-STATE.md`, auto-memory e `CONTEXT.md` existem sem hierarquia clara, Claude enfrenta instruções contraditórias entre camadas. O modelo não tem protocolo de desempate nativo — usa heurística de recência e posição no context window, o que é imprevisível.

**Sintoma**: Claude segue instruções de sessões anteriores que deveriam ter expirado; "lembra" de decisões que você reverteu; contradições entre arquivos produzem comportamento inconsistente na mesma sessão.

**Como evitar**: Adotar o modelo 4-camadas com responsabilidades exclusivas: `CLAUDE.md` (instruções estáveis que você escreve), auto-memory (lições que Claude escreve), `PROJECT-STATE.md` (estado atual da task em progresso, sobrescrito a cada sessão — renomeado de `MEMORY.md` justamente para não colidir com a auto-memory), `CONTEXT.md` (handoff entre sessões). Cada camada tem dono e TTL definido. Ver [01-canonical-anthropic.md §1](01-canonical-anthropic.md#1-memory-system--claudemd--auto-memory) e [07-glossary.md §Auto-memory](07-glossary.md#auto-memory).

**Fonte**: [Amit Ray 2026](https://amitray.com/claude-md-vs-agents-md-memory-md-skills-md-context-md-guide-2026/)

---

## 8. Hooks sem exit codes (Falsa Segurança)

**Por que falha**: Hooks são a única camada determinística de enforcement em Claude Code. Um hook script que termina sem exit code explícito retorna `0` por padrão — mesmo quando detectou violação. Claude interpreta `exit 0` como "aprovado" e segue em frente. O hook aparenta funcionar (roda, não errou) mas não bloqueia nada.

**Sintoma**: Seu hook de validação roda em todo `PreToolUse` mas você continua vendo o comportamento que deveria bloquear; logs mostram o hook executando, mas sem efeito visível.

**Como evitar**: Todo hook de enforcement deve emitir `exit 2` (block + show stderr) quando detectar violação, `exit 0` quando aprovado. Scripts que falham internamente (exception não capturada) devem ser tratados com `set -e` + trap. Testar o hook isoladamente com input de violação antes de colocá-lo em produção. Ver [01-canonical-anthropic.md §5](01-canonical-anthropic.md#5-hooks--lifecycle-event-handlers) e [07-glossary.md §Hook](07-glossary.md#hook).

**Fonte**: [Docs hooks guide](https://code.claude.com/docs/en/hooks-guide)

---

## 9. Hard-coded paths em skills (Portabilidade Zero)

**Por que falha**: Skills com paths absolutos (`/caminho/absoluto/do/autor/meu-projeto/`) ou paths relativos ao home do autor param de funcionar fora do ambiente original. Em equipes, CI/CD, ou ao portar o projeto para outro workstation, toda skill quebra silenciosamente — o path não existe, o script falha, Claude recebe erro sem contexto.

**Sintoma**: Skill funciona na máquina do autor mas falha com `FileNotFoundError` ou `command not found` no CI ou na máquina de outro colaborador. Skills que envolvem executáveis ou templates externos param de funcionar após `git clone` em path diferente.

**Como evitar**: Skills portáveis nunca referenciam paths absolutos. Usar caminhos relativos ao `SKILL.md` (`./template.md`), variáveis de ambiente (`$PROJECT_ROOT`, `$HOME`), ou `$(git rev-parse --show-toplevel)` para root do repo. Contraponto positivo: as skills embarcadas neste projeto são portáveis porque usam apenas paths relativos ao `.claude/skills/<name>/` — esse padrão é o target. Ver [07-glossary.md §Skill](07-glossary.md#skill) e [01-canonical-anthropic.md §2](01-canonical-anthropic.md#2-skills--agent-skills-open-standard).

**Fonte**: [Anthropic Skills Docs](https://code.claude.com/docs/en/skills), [obra/superpowers portability conventions](https://github.com/obra/superpowers)

---

## 10. Duplicar configuração base entre profiles (drift)

> [!IMPORTANT]
> **Este item afirmava algo falso até 2026-07-29, e a correção é a parte interessante.** Ele se chamava "Profile sem `based_on` (Composição Impossível)" e prescrevia declarar `based_on: universal-software`, afirmando que "o bootstrap engine processa herança: aplica base primeiro, depois overlay do profile específico". Medido contra o código deste próprio repo: `based_on` aparece **só** nos cinco `profile.yaml` que o declaram e não é lido por **nenhum código nem teste**. É metadado declarativo inerte. O doc prescrevia um mecanismo que o engine não implementa — ver [05-profiles.md](05-profiles.md), que carrega a mesma divergência.

**Por que falha**: Se cada profile especializado repete a configuração comum, mudar uma regra universal exige editar N arquivos, e as cópias divergem conforme algumas são atualizadas e outras não. É a principal fonte de inconsistência entre profiles no longo prazo.

**Sintoma**: `data-science`, `frontend` e `devops` replicam a mesma configuração base; uma mudança universal significa N edições; profiles novos contribuídos por outras pessoas começam de um arquivo vazio em vez de um piso comum.

**Como evitar — como está de fato implementado aqui**: a composição existe, mas vem do `_base/`, não do `based_on`. O `install.py` resolve `<templates_dir>/_base` (`install.py:525`) e o aplica para **todo** profile; o profile então sobrepõe, e `profile.get("skills")` é lido direto do arquivo do próprio profile, sem merge com pai. A regra prática, portanto: o que é universal vive no `_base/`, e o profile declara só o seu delta. Adicionar profile continua zero-touch nos existentes porque nada faz merge entre irmãos.

**O que fazer com o `based_on`**: tratar como documentação de intenção, não de comportamento, até que o merge seja implementado ou o campo seja removido. Não escreva profile que dependa dele resolver. Ver [07-glossary.md §Profile](07-glossary.md#profile) e [07-glossary.md §Profile-based, não monolítico](07-glossary.md#profile-based-não-monolítico).

**Fonte**: medido neste repo em 2026-07-29 (`git grep based_on -- claude_bootstrap/ tests/ scripts/` devolve só as cinco declarações)

---

## Resumo: tabela de remediation

| Anti-pattern | Sintoma chave | Remediação imediata | Skill/rule sugerida |
|---|---|---|---|
| CLAUDE.md >500 linhas | Rules violadas que estão escritas | Cortar para ≤150 linhas (ideal ≤60); mover para `.claude/rules/` | path-scoped rules Q2/2026 |
| Kitchen sink session | Outputs genéricos, assuntos misturados | `/clear` entre tasks | subagents para paralelismo |
| Ciclo fix-fail infinito | Turno 20+ no mesmo bug | Rollback + `/plan` + test reproduzível | `systematic-debugging` skill |
| Negação em CLAUDE.md | "Do NOT X" violado com frequência | Reescrever como afirmativo | revisar `CLAUDE.md` todo |
| Over-engineering | Hierarquias de classe para problemas simples | Anchor no prompt: "minimum code" | regra `simplicity.md` |
| Skills como silver bullet | Skill existe mas comportamento não muda | Migrar enforcement para hooks | hooks `PreToolUse` |
| Memory não integrada | Instruções contraditórias entre sessões | Adotar modelo 4-camadas com TTL | `PROJECT-STATE.md` template |
| Hooks sem exit codes | Hook roda mas não bloqueia | Adicionar `exit 2` em caminhos de erro | template de hook com `set -e` |
| Hard-coded paths em skills | Skills quebram fora da máquina do autor | Substituir por paths relativos ou env vars | convention portability |
| Configuração base duplicada | Duplicação + drift entre profiles | Colocar o universal no `_base/`; profile carrega só o delta | o schema de profile |
