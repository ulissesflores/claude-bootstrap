# CLAUDE.md — `manuscript/`

> Loaded automatically when editing files under `manuscript/`. Use this for academic writing rules that shouldn't apply to non-manuscript code. See [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory) for the subdirectory `CLAUDE.md` mechanism.

## Manuscript writing conventions

- **IMRAD structure**: Introduction, Methods, Results, and Discussion. Each section earns its place — don't pad. Methods detailed enough to reproduce; Results report observation, not interpretation.
- **One claim, one citation**: every non-trivial assertion must trace to a primary or canonical secondary source. Don't claim from memory.
- **Active voice with caveats**: "We measured X" beats "X was measured" except in Methods passive-voice conventions of your field.
- **No buzzwords**: "leverages", "utilizes", "facilitates". Use "uses".

## Citation discipline

- Style determined by target journal (APA / IEEE / Vancouver / Chicago / ACM). Keep it consistent across the manuscript.
- BibTeX entries with full metadata (year, DOI, authors). No `et al.` until ≥6 authors per most styles.
- Run citation validation before submission — DOI resolution, author spelling, page ranges.
- **Citation-management skill** in this profile handles search → metadata extraction → BibTeX generation. Use it from manuscript drafts.

## What NOT to do here

- ❌ Use unstable references (URLs without snapshots, preprints without DOIs in fields that require peer-reviewed)
- ❌ Cite from abstract only — read the paper or mark "secondary citation"
- ❌ Hide negative results — write them honestly; null results are findings
- ❌ Use AI-generated prose as the final draft — disclose AI assistance per your publisher's policy

## When the manuscript is multi-author

- Track changes per author (`\textcolor` in LaTeX, or comments in DOCX)
- Single source of truth for the bibliography (`.bib` in this directory, not `~/Downloads/`)
- Don't merge formatting commits with content commits — separate PRs
