---
name: newproj
description: Prevention loop to run BEFORE writing new code (feature, module, or project) — chains intent, then prior art, then a gated plan, so the work neither grows scope it does not need nor reinvents what the standard library, the platform, or an already-installed dependency ships. Use when starting new coding work, or when asked to "check before coding", "I don't want to reinvent the wheel", "lock the scope first". NOT project scaffolding, and NOT for healing existing code (use the `refactor` skill). It never cuts validation, error handling, or security.
license: MIT
---

# newproj — the prevention loop

The cheapest monster is the one that never gets built. This gate runs *before* the first line
and attacks the two failure modes that start there: **scope creep** ("it does 200 things") and
**reinventing the wheel** ("it builds what already ships").

## The three steps — in order, and step 2 is not optional

1. **Intent first.** Pin down what is *actually* required before any code exists — the
   `brainstorming` skill is built for exactly this. It kills "200 things" at the source: if it
   did not come out of the intent step, it is not in scope.

2. **Prior art — mandatory.** This is rungs 1–5 of the `ponytail` ladder applied *before* the
   code instead of after it. Before writing any general-purpose mechanism, answer with
   evidence:
   - Does this codebase already do it? `grep` for the candidates — an accusation without a grep
     is a guess, and so is a claim that nothing exists.
   - Does the standard library, a native platform feature, or an **already-installed**
     dependency resolve it?
   - Does a maintained package already solve it? Search by the term of art, not by your own
     description of the problem — the thing you are about to build usually has a name.

   A **yes** on any rung → stop and reuse. Do not write what already exists.

3. **A plan with a gate.** Write the plan down and have it approved *before* touching code
   (`writing-plans`). The plan is the mechanical anti-drift lock, and it needs three parts: a
   pre-mortem of how this could fail, the macro approach, and a task list specific enough that
   "done" is checkable rather than arguable. Only after that gate, write code — surgically.

## Closing

- Touch only what the approved plan requires. Do not refactor adjacent code on the way past.
- Before claiming done, run the diff through `ponytail` and apply what is worth applying.
- "Done" means tested and documented, in proportion to the size of the change
  (`verification-before-completion`).

## The floor — never negotiable

Prevention is never an excuse to cut input validation, error handling, security, or
accessibility. Minimalism without those checks is unfinished code, not lean code.
