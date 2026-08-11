---
paths:
  - "**/*.tf"
  - "**/*.tfvars"
  - "**/Dockerfile"
  - "**/*.yaml"
  - "**/*.yml"
---

# Infrastructure-as-Code conventions

## Terraform
- Run `terraform plan` and read the diff before any apply; never `apply`/`destroy` unprompted.
- Never hand-edit `*.tfstate`. Prefer `moved {}` blocks and `import` blocks over `terraform state`
  surgery (`state rm/mv` orphans live resources). Treat `*.tfvars` as secrets — don't commit, don't
  paste into chat.
- Pin provider and module versions (no floating `>=`); keep `required_version` set.

## Containers & Kubernetes
- Pin image tags to a digest or explicit version — never `:latest` in committed manifests.
- Every container sets resource `requests` + `limits`; every Deployment sets liveness/readiness probes.
- No secrets in env literals or ConfigMaps — reference a Secret or an external secret manager.

## CI/CD
- Least-privilege tokens; never echo secrets into logs. Pin third-party actions/images to a SHA.
