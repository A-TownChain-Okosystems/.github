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
3. the override requests a rule that is not in the central allowlist, or
4. the override has passed its declared sunset date.

This makes obsolete, expired, or unauthorized exceptions fail closed.

## Sunset contract

Temporary overrides MUST declare:

- `sunset`: ISO date on which CI stops accepting the exception;
- `tracking_issue`: the organization issue tracking removal/remediation.

The CI gate compares `sunset` with the current UTC date and fails on or after the sunset date.

## atc-standards

`atc-standards.toml` temporarily relaxes E701 and E702 only.

- sunset: 2027-03-31
- tracking issue: A-TownChain-Okosystems/.github#25
- raw baseline at exact HEAD `f870085f04dacd21faebbb88ab722537fef88164`: 107 E701 + 70 E702
- gate baseline with the override at exact HEAD `80c241dbc53f158e3c608d4b56a7ca0ed24313db`: 32 active findings

The 177 E701/E702 findings are not fixed by the override; they are intentionally suppressed
while the temporary exception is active. The exception must be removed after those findings
are remediated and no later than the sunset date.

## Review contract

Changes to this directory require review in the organization `.github` repository.
Caller workflows pin the reusable workflow and policy content by separate exact SHAs.
