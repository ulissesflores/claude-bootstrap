# Skills curadas — `claude-bootstrap`

> Catálogo das 13 skills auditadas em `claude_bootstrap/registry/skills.yaml`, instaláveis individualmente via `claude-bootstrap skill add`.
>
> 🇬🇧 [English version](../04-skills-curated.md) — the canonical copy.

> [!IMPORTANT]
> **Dois mecanismos distintos de skills, e eles não se tocam.**
> (a) **Registry** (este doc): catálogo de 13 skills instaláveis uma a uma com `claude-bootstrap skill add`, classificadas por tier 1/2/3.
> (b) **Bundles de profile** ([05-profiles.md](05-profiles.md)): 30 skills embarcadas em `templates/profiles/<p>/skills/` e instaladas em bloco por `claude-bootstrap init --profile <p>`, com proveniência por skill em cada `NOTICE.md`. 25 são vendored (`anthropics/skills`, `alirezarezvani/claude-skills`, `K-Dense-AI/scientific-agent-skills`), content-verified vs upstream por `scripts/verify-skill-provenance.py`; as 5 de `universal-software` são **first-party** — escritas neste repo, sem upstream a fixar, reportadas como `FIRST-PARTY`.
> **Medido, não afirmado:** os dois conjuntos de nomes são disjuntos. O `install.py` nunca lê o registry, e nenhum dos 13 nomes do registry aparece na lista `skills:` de qualquer profile. Instalar um profile instala zero skills do registry, e `skill add` instala zero skills de bundle.

---

## 1. Schema do registry

Cada entrada em `claude_bootstrap/registry/skills.yaml` obedece ao schema abaixo. Campos não marcados como obrigatórios são opcionais.

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `name` | string | sim | Identificador único kebab-case. Usado como nome do diretório instalado. |
| `description` | string | sim | Trigger semântico: quando o modelo deve ativar a skill. Deve ser uma frase prescritiva ("Use when…"). |
| `source.type` | enum | sim | `local` ou `github` — determina como instalar. Ver §3. |
| `source.url` | string | se github | URL do repositório git. Clonado com `--depth 1 --no-tags`. |
| `source.path` | string | se github/local | Subpath dentro do repo (github) ou dentro do **pacote `claude_bootstrap/` instalado** (local). Ver §3. |
| `tier` | int | sim | 1, 2 ou 3 — rótulo consultivo mais o filtro `skill list --tier`. Ver §2.1. |
| `profiles` | list[string] | sim | Profiles para os quais a skill é *oferecida*. Ex.: `[universal-software, academic]`. Filtra o `skill list --profile`; **não** instala nada. Ver §2.1. |
| `invocation` | enum | não | `model-decided` (padrão) ou `user-invocable` (exige comando explícito do usuário). Só documentação — nenhum código lê. |
| `evidence_url` | string | não | Link para repo ou doc que comprova que a skill existe e funciona. Só documentação — nenhum código lê. |
| `last_validated_at` | date | não | Data ISO da última auditoria manual (`YYYY-MM-DD`). Lida pelo `validate`. |
| `version` | string | não | Semver da skill, se o source expuser versionamento. |
| `unstable` | bool | não | `true` em tier 3 — sinaliza que a API da skill pode mudar sem aviso. Só documentação — nenhum código lê. |

O `claude-bootstrap skill validate` checa quatro coisas: todo campo obrigatório presente, nenhum `name` duplicado, todo path de source `local` existente em disco, e todo source `github` com `url` e `path`. Também avisa quando `last_validated_at` está mais velho que `STALE_DAYS = 90` (`skill.py:236`). Ele **não** checa o range do `tier`, e não resolve URLs remotas (custo de rede) — então um subpath github que sumiu do upstream passa na validação e só falha no `skill add`. A §6 documenta um caso vivo.

---

## 2. Critérios de curadoria

Dois mecanismos, duas perguntas diferentes, logo dois conjuntos de critérios. A §2.1 governa o registry (este doc); a §2.2 governa os bundles de profile ([05-profiles.md](05-profiles.md)).

### 2.1 Registry: o que um tier de fato é

**Tier é um rótulo consultivo, não uma política de instalação.** Ele tem exatamente dois efeitos no código: é campo obrigatório, e é o filtro `skill list --tier <n>` (`skill.py:55`). Nada instala uma skill por causa do tier dela. Do mesmo modo, `profiles:` estreita o `skill list --profile <p>` e nada mais — toda skill do registry, em qualquer tier, só chega a um projeto por um `claude-bootstrap skill add <name>` explícito.

> [!WARNING]
> **Correção de um claim que versões anteriores deste documento faziam.** Até esta revisão, a §2 dizia que tier 1 era *"auto-incluído quando o profile é instalado"*. Isso é falso e aparentemente nunca foi verdade neste codebase: o `install.py` não lê o registry, e a interseção entre os 13 nomes do registry e as listas `skills:` dos seis profiles é vazia. A instalação de profile lê `templates/profiles/<p>/profile.yaml` e copia `skills/<name>/` do diretório do profile (`install.py:315`). Se você chegou aqui por uma cópia em cache, esta é a versão corrigida.

Removido isso, os tiers continuam carregando a barra de entrada para a qual foram escritos — como recomendação editorial sobre *quando vale adotar uma skill*, não como mecanismo:

**Tier 1 — core/essential.** Amplamente útil a ponto de adicioná-la em quase qualquer projeto ser custo irrisório. Barra de entrada: auditada manualmente, trigger bem definido, sem efeitos colaterais destrutivos, evidência de uso real.

**Tier 2 — recommended.** Consolidada, mas restrita a fluxos específicos (paralelismo, worktrees, meta-skills de escrita de skills). O overhead de aprendizado não compensa em projeto simples.

**Tier 3 — experimental.** Carrega `unstable: true`. A API da skill pode mudar entre versões do `claude-bootstrap`. Use onde o benefício potencial justifica o risco de quebra.

Nunca promova uma skill de tier 3 para tier 1/2 sem audit de campo mais um `evidence_url` válido. O custo de uma skill ruim sempre sugerida é alto.

### 2.2 Bundles: o que "curado" está afirmando

Este é o eixo a que o claim "curated, license-audited skills" do README se refere, e vale ser preciso, porque *curado* é uma palavra que convida a mais crédito do que o trabalho sustenta.

**O que se afirma:** toda skill embarcada passou por quatro portões de exclusão, cada um dos quais já removeu skills reais de releases reais. Os portões são dirigidos por evidência, aplicados à skill como ela existe no commit fixado do upstream.

1. **Direito de redistribuição, resolvido por diretório de skill.** A skill só embarca se uma licença conceder redistribuição — lida da fonte no commit fixado (licença raiz, override por skill, frontmatter do `SKILL.md`), nunca inferida. Removidas em 2026-07-26 (29 -> 25): `docx`, `pdf`, `pptx` (`anthropics/skills`), cujo `LICENSE.txt` é uma lista de restrições sem cláusula de concessão; e `doc-coauthoring`, que não tem licença nenhuma — ausência de licença é copyright padrão, não permissividade padrão.
2. **Proveniência verificável contra um commit fixado.** O conteúdo embarcado é comparado byte a byte com o upstream pelo `scripts/verify-skill-provenance.py`. Uma skill que some do upstream não pode mais ser verificada, então não pode ficar. Removida em 2026-06-29: `release-manager` (`devops`).
3. **O `SKILL.md` precisa descrever máquina que embarca.** Uma skill que manda o modelo usar arquivos ou flags que o bundle não contém chega quebrada. Removidas em 2026-06-06: `senior-devops`, três scripts-stub idênticos e no-op cujo `SKILL.md` documenta flags que o script rejeita; e `theme-factory`, que exige um `theme-showcase.pdf` que nunca foi embarcado. É a mesma regra que a skill embarcada `vetting-agent-skills` aplica a skills de terceiros.
4. **Encaixe de domínio com o profile que a carrega.** Removida em 2026-06-06: `xlsx`, uma skill de modelagem financeira dentro de `data-science`.

Um quinto portão governa o que pode entrar: nada específico de instituição ou de pessoa. Um profile inteiro atrelado a uma instituição foi removido em 2026-07-23, e o `scripts/pii-scan.py` hoje roda sobre todo arquivo versionado como gate.

**O que não se afirma:** nenhuma revisão sistemática de qualidade do texto de instrução das 30 skills embarcadas. Os portões 1-3 são objetivos e rechecados por máquina; o portão 4 é um juízo feito por skill, no momento em que ela entrou. "Curado" aqui significa *estas exclusões foram aplicadas e são reverificadas a cada rodada*, não *cada frase de cada skill embarcada foi revisada e endossada*.

Dois dos portões são rechecados por máquina em vez de confiados: o `scripts/verify-skill-provenance.py` reroda o **portão 2** a cada invocação (compara conteúdo byte a byte com o commit fixado; não lê licença nenhuma), e o `tests/test_redistribution_rights.py` codifica o **portão 1** — nenhuma skill sem licença, o texto da concessão embarcado dentro do diretório da skill, e uma skill desembarcada não pode reaparecer. Os portões 3 e 4 são juízos feitos por skill no momento em que ela entrou, e nada os recheca.

---

## 3. Source types suportados

### `local`

Path resolvido contra o **diretório do pacote `claude_bootstrap/` instalado** (`REPO_ROOT` em `skill.py:27`, usado em `skill.py:98`), não contra o root do repositório. Usado para skills específicas de um profile que vivem dentro do próprio pacote.

```yaml
source:
  type: local
  path: templates/profiles/academic/skills/citation-management
```

Esse valor está correto como está: resolve para `claude_bootstrap/templates/profiles/academic/skills/citation-management`. Não acrescente o prefixo `claude_bootstrap/` ao valor no YAML — resolveria para `claude_bootstrap/claude_bootstrap/…` e falharia. Os paths de shell da §7 são outra coisa e levam sim o prefixo.

`claude-bootstrap skill add` copia o diretório direto para `<target>/.claude/skills/<name>/`. Nenhuma rede envolvida. O `validate` verifica que o path existe em disco.

> [!NOTE]
> Nenhuma entrada do registry atual usa `local` — as 13 são `github`. O tipo é suportado e testado (`tests/test_skill.py`), mas a checagem do `validate` para ele é vazia contra o registry embarcado.

### `github`

Clona o repositório git com `--depth 1 --no-tags` num diretório temporário (timeout de 60 s), extrai o `path`, copia para o destino e descarta o clone. Requer `git` no `PATH`. O destino só é apagado **depois** que o clone dá certo (`skill.py:139`), então falha de rede deixa intacta uma skill já instalada.

```yaml
source:
  type: github
  url: https://github.com/obra/superpowers
  path: skills/brainstorming
```

> [!NOTE]
> `claude-bootstrap skill update [--name <name>]` re-extrai (force) as skills github já instaladas a partir das fontes atuais do registry. `skill add <name> --force` faz o mesmo para uma skill específica. Ver a ressalva na §8 antes de rodar `update` sem `--name`.

---

## 4. Skills tier 1 do registry — oferecidas a `universal-software` (8)

> Eixo **registry**, não bundle: são as **8 entradas de tier 1**. Medido em 2026-08-03: todas as
> 13 entradas do registry trazem `universal-software` em `profiles:`, então esta seção é a fatia
> tier 1 do catálogo, não um filtro por profile — `skill list --profile universal-software` devolve
> as 13. Não confundir com as **5 skills first-party embarcadas** nesse
> profile (§(b) acima), que vêm no `init` sem `skill add`. Nenhum dos dois conjuntos instala o
> outro; "oferecida" significa que o `skill list --profile universal-software` a mostra, e nada além.

Todas originam de [github.com/obra/superpowers](https://github.com/obra/superpowers). Invocação: `model-decided` — o modelo decide quando aplicar com base no trigger descrito.

### `brainstorming`

**Trigger**: antes de criar features, componentes ou modificar comportamento existente.
**Profiles**: `universal-software`, `academic`
**O que faz**: força exploração de intenção do usuário antes de qualquer implementação. Impede o loop "implementa errado -> reescreve".
**Source**: `skills/brainstorming` em [obra/superpowers](https://github.com/obra/superpowers)

---

### `writing-plans`

**Trigger**: ao receber spec ou requisitos de tarefa multi-passo, antes de tocar código.
**Profiles**: `universal-software`, `academic`
**O que faz**: produz um plano de implementação estruturado que pode ser executado em sessão separada. Separa o ciclo de design do ciclo de execução.
**Source**: `skills/writing-plans` em [obra/superpowers](https://github.com/obra/superpowers)

---

### `executing-plans`

**Trigger**: ao ter um plano de implementação escrito para executar, em sessão separada do planejamento.
**Profiles**: `universal-software`, `academic`
**O que faz**: define checkpoints de revisão durante execução. Parceiro de `writing-plans` — juntos implementam o loop planejar/executar/revisar que reduz retrabalho.
**Source**: `skills/executing-plans` em [obra/superpowers](https://github.com/obra/superpowers)

---

### `test-driven-development`

**Trigger**: ao implementar qualquer feature ou bugfix, antes de escrever código de implementação.
**Profiles**: `universal-software` (não oferecida para `academic`)
**O que faz**: enforça ciclo red/green/refactor. A ausência de testes antes da implementação é o erro mais comum em coding agents.
**Source**: `skills/test-driven-development` em [obra/superpowers](https://github.com/obra/superpowers)

---

### `systematic-debugging`

**Trigger**: ao encontrar qualquer bug, falha de teste ou comportamento inesperado, antes de propor correções.
**Profiles**: `universal-software`, `academic`
**O que faz**: impõe hipótese -> evidência -> correção em vez de "edita e reza". Previne o anti-pattern de aplicar patches cegos.
**Source**: `skills/systematic-debugging` em [obra/superpowers](https://github.com/obra/superpowers)

---

### `verification-before-completion`

**Trigger**: antes de declarar que o trabalho está completo, antes de fazer commit ou criar PRs.
**Profiles**: `universal-software`, `academic`
**O que faz**: exige rodar comandos de verificação e confirmar output antes de qualquer afirmação de sucesso. Elimina o "acho que funciona" sem evidência.
**Source**: `skills/verification-before-completion` em [obra/superpowers](https://github.com/obra/superpowers)

---

### `requesting-code-review`

**Trigger**: ao completar tarefas, implementar features maiores ou antes de merge.
**Profiles**: `universal-software` (não oferecida para `academic`)
**O que faz**: estrutura como solicitar code review de forma que o revisor tenha contexto suficiente. Reduz round-trips de clarificação.
**Source**: `skills/requesting-code-review` em [obra/superpowers](https://github.com/obra/superpowers)

---

### `receiving-code-review`

**Trigger**: ao receber feedback de code review, antes de implementar sugestões.
**Profiles**: `universal-software` (não oferecida para `academic`)
**O que faz**: impede concordância performativa cega. Exige rigor técnico: verificar se a sugestão é válida antes de aplicar. Ver também [01-canonical-anthropic.md](01-canonical-anthropic.md) §2 (Skills standard Anthropic).
**Source**: `skills/receiving-code-review` em [obra/superpowers](https://github.com/obra/superpowers)

---

## 5. Skills tier 2 — recommended (5)

Opt-in. Instalar via `skill add <name>`. Todas de [obra/superpowers](https://github.com/obra/superpowers), invocação `model-decided`.

### `dispatching-parallel-agents`

**Trigger**: ao enfrentar 2+ tarefas independentes que podem ser trabalhadas sem estado compartilhado.
**Profiles**: `universal-software`, `academic`
**O que faz**: define protocolo para despachar subagentes em paralelo com handoff correto de contexto e coleta de resultados.
**Source**: `skills/dispatching-parallel-agents` em [obra/superpowers](https://github.com/obra/superpowers)

---

### `using-git-worktrees`

**Trigger**: ao iniciar trabalho de feature que precisa de isolamento do workspace atual.
**Profiles**: `universal-software`
**O que faz**: guia criação de git worktrees com verificação de segurança. Evita o problema de múltiplos agentes editando o mesmo working tree.
**Source**: `skills/using-git-worktrees` em [obra/superpowers](https://github.com/obra/superpowers)

---

### `subagent-driven-development`

**Trigger**: ao executar planos de implementação com tarefas independentes na sessão atual.
**Profiles**: `universal-software`
**O que faz**: complementa `executing-plans` para casos onde as subtarefas do plano são independentes o suficiente para rodar em subagentes na mesma sessão (vs. sessões separadas).
**Source**: `skills/subagent-driven-development` em [obra/superpowers](https://github.com/obra/superpowers)

---

### `writing-skills`

**Trigger**: ao criar novas skills, editar skills existentes ou verificar que uma skill funciona antes de deploy.
**Profiles**: `universal-software`
**O que faz**: meta-skill — define o formato correto de `SKILL.md`, critérios de trigger e como testar uma skill antes de adicioná-la ao registry.
**Source**: `skills/writing-skills` em [obra/superpowers](https://github.com/obra/superpowers)

---

### `finishing-a-development-branch`

**Trigger**: quando a implementação está completa e todos os testes passam, antes de decidir a estratégia de integração.
**Profiles**: `universal-software`
**O que faz**: apresenta opções estruturadas de merge, PR ou cleanup. Impede o anti-pattern de fazer push direto em main sem considerar impacto.
**Source**: `skills/finishing-a-development-branch` em [obra/superpowers](https://github.com/obra/superpowers)

---

## 6. Skills tier 3 — experimental (0)

O registry não tem entrada de tier 3 hoje. O tier segue definido (§2.1) e a próxima skill experimental entra aqui; `skill list --tier 3` devolve lista vazia, não erro.

> [!NOTE]
> **`graphify` era a única entrada de tier 3, e foi removida em 2026-08-03 porque não instalava.** Medido naquele dia: a árvore git recursiva de `obra/superpowers` no `HEAD` tem 234 paths, não está truncada, e não contém `skills/graphify` — o subpath para o qual a entrada apontava. O comando devolvia `subpath-missing: skills/graphify`, exit code 1.
>
> A parte que vale guardar: **o `skill list` a imprimia como `available` esse tempo todo.** O `fmt_status` (`skill.py:59`) informa se a skill está instalada *no target*, nunca se a fonte dela resolve — ou seja, "available" queria dizer "não instalada aqui", e a única superfície que o usuário de fato lê afirmava o oposto da verdade. O flag `unstable: true` também não ajudava: esse campo é só documentação, lido por nenhum código (§1).
>
> É a mesma classe de falha que desembarcou `release-manager` em 2026-06-29 (§2.2, portão 2), reaparecendo no eixo registry, onde nada a recheca: o `validate` não resolve URL remota por design, e nenhum teste resolve subpath do github. Uma entrada de registry é uma afirmação sobre o repositório de outra pessoa, e esta era verdadeira quando foi escrita.

---

## 7. Como adicionar uma skill ao registry

Passos para adicionar uma nova skill curada. Os paths abaixo são **paths de shell a partir do root do repositório**, e é por isso que levam o prefixo `claude_bootstrap/` — diferente do valor `source.path` dentro do YAML, que é resolvido contra o diretório do pacote (§3).

**1. Decidir source type**

- Skill nova que só faz sentido neste contexto: crie o diretório em `claude_bootstrap/templates/profiles/<profile>/skills/<name>/` e use `type: local` com `path: templates/profiles/<profile>/skills/<name>` (sem o prefixo `claude_bootstrap/` no YAML).
- Skill de repo externo existente: use `type: github` com URL e subpath.

**2. Criar o diretório da skill (se local)**

A estrutura mínima de uma skill é um arquivo `SKILL.md` com:
- Seção de trigger (quando usar)
- Instruções de comportamento

**3. Editar `claude_bootstrap/registry/skills.yaml`**

Adicione a entrada com todos os campos obrigatórios: `name`, `description`, `source`, `tier`, `profiles`. Defina `last_validated_at` com a data de hoje (`YYYY-MM-DD`) — o `validate` avisa quando ela passa de 90 dias.

```yaml
- name: minha-skill
  description: Use when <trigger preciso e mensurável>
  source:
    type: local
    path: templates/profiles/meu-profile/skills/minha-skill
  tier: 2
  profiles: [meu-profile]
  invocation: model-decided
  last_validated_at: 2026-05-05
```

**4. Validar**

```bash
claude-bootstrap skill validate
```

As falhas que ele de fato reporta: campo obrigatório ausente, `name` duplicado, path `local` inexistente, e source `github` sem `url` ou sem `path`. Ele **não** valida o range do tier — `tier: 0` e `tier: 9` passam os dois — e não resolve URLs remotas, então o passo 5 é a única coisa que prova que uma entrada `github` funciona.

**5. Testar instalação**

```bash
claude-bootstrap skill add minha-skill --target /tmp/test-install
ls /tmp/test-install/.claude/skills/minha-skill/
```

Para source `github` isso não é opcional: é a única checagem de que o subpath existe upstream. Ver §6 para uma entrada que passa no `validate` e falha aqui.

**6. Commit**

```bash
git add claude_bootstrap/registry/skills.yaml claude_bootstrap/templates/profiles/<profile>/skills/<name>/
git commit -m "feat(skills): add <name> to registry (tier N)"
```

Não commite sem ter rodado `validate`. O CI não bloqueia hoje, mas o registry corrompido quebra todos os `skill add` downstream.

---

## 8. Comandos do `claude-bootstrap skill`

| Comando | Descrição | Exemplo |
|---|---|---|
| `skill list` | Lista skills do registry. Filtrável por `--profile` e `--tier`. Mostra status installed/available contra o `--target`. | `claude-bootstrap skill list --profile academic --tier 1` |
| `skill list --json` | Output JSON com status por skill. | `claude-bootstrap skill list --json \| jq '.[].name'` |
| `skill add <name>` | Instala skill em `<target>/.claude/skills/<name>/`. Default target: `.`. Já instalada sem `--force` dá `exists-skipped`, exit 0. | `claude-bootstrap skill add brainstorming --target ~/meu-projeto` |
| `skill add <name> --force` | Re-instala mesmo que já instalada. | `claude-bootstrap skill add writing-skills --force` |
| `skill remove <name>` | Remove `<target>/.claude/skills/<name>/` (apenas a skill nomeada; para reverter um emit inteiro use `claude-bootstrap uninstall`). | `claude-bootstrap skill remove using-git-worktrees` |
| `skill show <name>` | Imprime a entrada completa do registry para uma skill, em JSON. | `claude-bootstrap skill show brainstorming` |
| `skill validate` | Checa campos obrigatórios, nomes duplicados, paths locais e `url`+`path` do github. URLs remotas não são resolvidas. | `claude-bootstrap skill validate` |
| `skill update [--name <name>]` | Re-instala (force) as skills já instaladas a partir das fontes atuais do registry; sem `--name`, todas as instaladas. | `claude-bootstrap skill update --name brainstorming` |

**Flags globais**:

- `--registry <path>`: usa registry alternativo (default: `claude_bootstrap/registry/skills.yaml`, injetado pela CLI em `cli.py:266`)
- `--target <path>`: diretório de instalação (default: `.`)

> [!WARNING]
> **`skill update` sem `--name` sai com 1 em qualquer projeto bootstrapado.** Ele itera sobre todo diretório em `<target>/.claude/skills/`, e as skills que o `init` colocou ali vêm do bundle do profile, não do registry — então cada uma é reportada como `not-in-registry` e o comando sai com 1 mesmo sem nada errado. Medido contra um target contendo só skills de bundle: duas entradas, ambas `not-in-registry`, rc 1. Use `skill update --name <name>` para uma skill do registry que você de fato instalou.

> [!NOTE]
> O módulo requer `pyyaml`. A CLI `claude-bootstrap` já resolve as dependências; para invocar o módulo direto: `uv run --with pyyaml --no-project python3 -m claude_bootstrap.skill <cmd>`.

---

*Cross-references: [01-canonical-anthropic.md](01-canonical-anthropic.md) §2 (Skills standard Anthropic) | [05-profiles.md](05-profiles.md) (profiles que carregam os bundles) | [07-glossary.md](07-glossary.md) (terminologia)*
