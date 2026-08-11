# CLAUDE.md — `infra/`

> Loaded automatically when editing infrastructure code. Use this for IaC guardrails that shouldn't apply to application code. See [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory) for the subdirectory `CLAUDE.md` mechanism.

## Infrastructure-as-code guardrails

- **Plan before apply**: every Terraform / Pulumi / CDK change requires a `plan` (or equivalent diff) reviewed BEFORE `apply`. No exceptions for "small" changes.
- **Drift is real**: assume the live infra has drifted from the code. Run `plan` even on a clean checkout. Reconcile drift explicitly — don't override it without understanding what changed.
- **Secrets never inline**: no API keys, passwords, certificates, or connection strings in IaC files. References to a secrets manager (AWS SSM, GCP Secret Manager, HashiCorp Vault, sealed-secrets) only.
- **Destroy is sacred**: `terraform destroy`, `kubectl delete`, `helm uninstall` require explicit operator authorization for each environment. Never assume "the lower env is safe to destroy".

## Change-blast-radius checklist

Before opening a PR that touches infrastructure, verify:

- [ ] Plan output reviewed and matches intent
- [ ] Resources that will be **replaced** (destroy + recreate) are called out explicitly
- [ ] Backups verified for any stateful resource (database, storage bucket, volume) being modified
- [ ] Rollback procedure documented in the PR description
- [ ] On-call paged if change affects production

## What NOT to do here

- ❌ Run `apply` from your laptop against shared environments — use the CI pipeline
- ❌ Commit `.tfstate` files (use remote state)
- ❌ Force-delete a resource with `terraform state rm` to "make the plan clean"
- ❌ Use `--auto-approve` on production
