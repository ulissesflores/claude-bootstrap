# CLAUDE.md — `src/`

> Loaded automatically when editing files under `src/`. Does not bloat the root `CLAUDE.md`. See [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory) for the subdirectory `CLAUDE.md` mechanism.

## Frontend conventions

- **Component structure**: one component per file unless trivially co-located. Default-export the component named after the file (`Button.tsx` → `export default function Button`).
- **Styling**: project's CSS strategy (Tailwind / CSS modules / styled-components) — match existing files in this subtree, don't introduce new approaches without discussion.
- **State**: prefer co-located state (`useState`/`useReducer`) over global stores unless ≥3 unrelated components read/write the same shape.
- **Accessibility**: any interactive element needs a name (label, aria-label, or visible text). Buttons get `<button>`, links get `<a>` — don't fake them with divs.

## What NOT to do here

- ❌ Inline styles for layout (use the project's CSS strategy)
- ❌ Bypass type-checking with `as any` or `// @ts-ignore` without a comment explaining why
- ❌ `dangerouslySetInnerHTML` without a sanitizer

## Renaming this file or removing it

Subdirectory `CLAUDE.md` files are optional. If your project doesn't follow these conventions, delete this file or replace it with your own. The bootstrap added it as a starting point — it's not load-bearing.
