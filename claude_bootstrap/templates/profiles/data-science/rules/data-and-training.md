---
paths:
  - "data/**"
  - "**/*.py"
---

# Data & training-script conventions

> Notebook hygiene (seeds, `nbstripout`, no PII in cell outputs) lives in `notebooks/CLAUDE.md`.
> This rule covers `data/` and `.py` training/pipeline code — it complements, not duplicates, that.

## No leakage
- Fit scalers/encoders/imputers on the **training split only**, then transform val/test. Never `fit`
  on the full dataset.
- Split before any preprocessing that learns from data; keep the test set untouched until final eval.

## Data hygiene
- Don't commit raw datasets — track large/binary data with DVC (or an external store) and commit the
  pointer. No PII, credentials, or API keys in files under `data/` or in committed sample data.

## Reproducibility
- Seed every RNG in training scripts (`random`, `numpy`, the framework's RNG); log the seed.
- Pin the environment (lockfile / `environment.yml`); record dataset version + commit alongside results.
