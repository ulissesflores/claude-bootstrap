---
paths:
  - "**/*.tex"
  - "**/*.bib"
---

# LaTeX & citation conventions

## Citations
- One claim → one citation; cite the primary source, not a review that cites it.
- Keep a single source-of-truth `.bib`; never hand-duplicate entries. Use consistent keys
  (`author:year:keyword`). Don't invent DOIs or page numbers — leave a `% TODO` instead.
- Match the venue's citation style; don't mix `\cite`/`\citep`/`\citet` arbitrarily.

## Structure & hygiene
- Use `\label`/`\ref` (and `\cref`) for every float/section — never hardcode "Figure 3".
- Don't `\input`/`\include` untrusted or generated files without reading them.
- One sentence per source line (eases diffs/review); commit content and formatting changes separately.

## Build
- Build with `latexmk` (it resolves bib + reruns); read the `.log` for the first real error,
  not the cascade. Build artifacts (`*.aux`/`*.bbl`/`*.synctex.gz`/…) are git-ignored — don't commit them.
