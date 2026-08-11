---
name: refactor
description: Healing loop for existing code that turned into a monster — finds the hotspot from DATA (churn x size, not a hunch), produces a structural report, applies the fix with the reuse ladder, and documents it so the monster does not regrow. Use when facing accumulated debt, or when asked to "refactor this", "tame the monster", "clean up the file nobody wants to open". NOT a bug hunt (use a code-review skill) and NOT for new code (use the `newproj` skill). It never cuts validation, error handling, or security.
license: MIT
---

# refactor — the healing loop

One bounded refactor at a time. This attacks **accumulated debt**: the file that grew until
nobody wants to open it.

## The steps

1. **Find the target from data, not from a hunch.** The hotspot is where churn × size is
   highest — a file that changes often *and* is large is where future pain concentrates.

   ```bash
   # Commits touching each file in a recent window, next to that file's size.
   # A recent window predicts better than all-time history.
   git log --since="6 months ago" --name-only --pretty=format: \
     | sed '/^$/d' | sort | uniq -c | sort -rn | head -20 \
     | while read -r churn file; do
         [ -f "$file" ] && printf '%5s commits  %6s lines  %s\n' \
           "$churn" "$(wc -l < "$file")" "$file"
       done
   ```

   The top of that list is the first target. It is a heuristic, not a law — the decision to
   refactor is still a human one. (Paths containing spaces need a `-z`-based variant; for a
   first pass this is enough.)

2. **Structural report on the hotspot, and only the hotspot.** What is the file actually
   doing, where do responsibilities blur, which change would deepen the module rather than
   just move code around? Produce the report and **stop** — a human picks what to apply. Do
   not auto-edit at this step, and do not widen the analysis to the whole repository.

   If the analysis would flood the working session, delegate it to a subagent with fresh
   context that returns only the report.

3. **Apply with the reuse ladder.** Run the target through `ponytail` — it finds reuse missed,
   gratuitous indirection, and abstractions with no second use — then apply the fixes it
   justifies.

4. **Safety net.** Tests green **before** and **after**; that is the regression gate. If the
   code under the knife has no test, write the test first (`test-driven-development`).
   Refactoring without a net is demolition without shoring.

5. **Close.** A short architecture decision record: what changed and why. Undocumented
   refactors regrow. "Done" includes documented.

## Batch mode — paying debt as one package

When a hotspot carries **several** debt items, pay them as one package rather than in separate
rounds; each round reopens the context and re-verifies from zero.

```
item 1 -> [cheap test: GREEN] -> item 2 -> [cheap test: GREEN] -> ...
       -> cross-consistency test -> extraction to its destination
       -> ONE full verification at the end
```

The verification rule:

- **Keep the cheap tests green between chunks.** This preserves bisection: if the final check
  goes red, the last green chunk localises the culprit.
- **Reserve "one check at the end" for when re-verifying is genuinely expensive** — a live
  service, an LLM-graded evaluation, a slow suite. Then, and only then, verify once at the end.
- So: bisect when it is cheap, batch when re-verification hurts. It is not a dogmatic either/or.

Close the batch with the full suite plus the record from step 5.

## The floor — never negotiable

Simplifying never removes input validation, error handling, security, or accessibility. A
cryptic one-liner loses to two readable lines — understand the code before you shorten it.
