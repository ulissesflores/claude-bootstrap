---
paths:
  - "**/*.tsx"
  - "**/*.ts"
  - "**/*.jsx"
  - "**/*.vue"
  - "**/*.svelte"
  - "**/*.astro"
---

# Frontend conventions

- Type props and return values explicitly; avoid `any` — prefer `unknown` + narrowing at boundaries.
- Co-locate a component's test (`*.test.tsx`) and styles with the component.
- Accessibility: use semantic elements, label every interactive control, keep it keyboard-reachable
  with a visible focus state.
- Never put secrets/API keys in client code or in `NEXT_PUBLIC_*` / `VITE_*` env vars — those ship
  to the browser.
- Keep render pure; put side effects in hooks/effects, not in the render path.
