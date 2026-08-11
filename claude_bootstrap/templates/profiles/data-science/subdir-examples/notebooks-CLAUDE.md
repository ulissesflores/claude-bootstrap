# CLAUDE.md — `notebooks/`

> Loaded automatically when editing notebooks. Use this for notebook hygiene rules that shouldn't apply to non-notebook code. See [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory) for the subdirectory `CLAUDE.md` mechanism.

## Notebook hygiene

- **Cell discipline**: each cell should have one clear purpose. Long multi-step cells should be broken up so you can re-run a single step.
- **Hidden state**: do not rely on out-of-order execution. If a notebook can't be run top-to-bottom and reproduce the same output, that's a bug to fix.
- **Imports up top**: all `import` statements in the first executable cell. Avoid mid-notebook imports unless lazy-loading is intentional and commented.
- **Outputs in git**: by default, `nbstripout` or equivalent should clear outputs before commit. Reviewers should not see cell outputs in PRs.

## Reproducibility checklist

- Random seeds set explicitly for any non-deterministic operation (`np.random.seed`, `torch.manual_seed`, `random.seed`, `tf.random.set_seed`)
- Data file paths declared as constants near the top; no hardcoded `/Users/...` paths
- Environment captured: `pip freeze > requirements.txt` or `uv export` matches what the notebook needs
- Wall-clock-heavy cells gated behind a flag — readers shouldn't accidentally trigger a 2-hour training run

## What NOT to do here

- ❌ Commit a notebook with cell outputs containing API keys, tokens, or PII
- ❌ Print large dataframes to cell output (use `.head()` or sample)
- ❌ Embed massive plots inline (export to `figures/` and reference; cell outputs bloat git blobs)
