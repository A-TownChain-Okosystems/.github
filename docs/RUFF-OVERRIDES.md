# Central Ruff Overrides

## Purpose

Ruff policy remains centrally owned by `ruff.toml`. A repository-specific exception, when
temporarily required, is also centrally owned under `ruff-overrides/`.

The caller repository cannot create or modify its own policy exception.

## Resolution

The reusable Ruff workflow derives the repository name from `GITHUB_REPOSITORY`:

```
.org-github-policy/ruff-overrides/<repository>.toml
```

If that file exists, it is selected as the Ruff configuration. Otherwise the base
`.org-github-policy/ruff.toml` is used.

Each override must use Ruff configuration inheritance:

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
2. the base-policy failures contain none of the rules relaxed by the override.

This makes an obsolete exception fail closed instead of silently accumulating.

## atc-standards

`atc-standards.toml` temporarily relaxes E701 and E702 only. The verified baseline at
exact HEAD `f870085f04dacd21faebbb88ab722537fef88164` contains 107 E701 and 70 E702
findings. The exception is therefore temporary and must be removed after those findings
are remediated.

## Review contract

Changes to this directory require review in the organization `.github` repository.
The reusable workflow and every override are pinned by exact SHA by callers.
