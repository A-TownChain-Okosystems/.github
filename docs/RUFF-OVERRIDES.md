# Central Ruff Overrides

## Purpose

Ruff policy remains centrally owned by `ruff.toml`. Temporary repository-specific
exceptions are centrally owned under `ruff-overrides/`.

The caller repository cannot create or modify its own policy exception.

## Resolution

The reusable Ruff workflow derives the repository name from `GITHUB_REPOSITORY`:

```
.org-github-policy/ruff-overrides/<repository>.toml
```

If that file exists, it is selected as the Ruff configuration. Otherwise the base
`.org-github-policy/ruff.toml` is used.

Each override must inherit the base policy and may only relax rules present in
`ruff-overrides/ALLOWLIST.toml`:

```toml
extend = "../ruff.toml"

[lint]
ignore = ["<approved-rule>"]
```

The override must not replace the base policy, disable formatting, or add exclusions.

## Stale detection

Every active override is checked against the base policy before the normal lint gate.

The check fails if:

1. the base policy is already clean, or
2. none of the rules relaxed by the override still occur in the base-policy report, or
3. the override requests a rule that is not in the central allowlist.

This makes obsolete or unauthorized exceptions fail closed.

## atc-standards

`atc-standards.toml` temporarily relaxes E701 and E702 only. The verified baseline at
exact HEAD `f870085f04dacd21faebbb88ab722537fef88164` contains 107 E701 and 70 E702
findings. The exception must be removed after those findings are remediated.

## Review contract

Changes to this directory require review in the organization `.github` repository.
Caller workflows pin the complete policy bundle by exact SHA.
The base policy file SHA is recorded separately in the reusable workflow.
