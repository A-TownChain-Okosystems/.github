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
`ruff-overrides/ALLOWLIST.toml`.

The override must not replace the base policy, disable formatting, or add exclusions.

## Stale and sunset detection

Every active override is checked against the base policy before the normal lint gate.

The check fails if:

1. the base policy is already clean, or
2. none of the rules relaxed by the override still occur in the base-policy report, or
3. the override requests a rule that is not in the central allowlist, or
4. the override has passed its declared sunset date.

Temporary overrides MUST declare:

- `sunset.date`: ISO date on which CI stops accepting the exception;
- `sunset.tracking_issue`: issue tracking removal/remediation.

The CI gate compares `sunset.date` with the current UTC date and fails on or after
the sunset date.

## atc-standards result

The temporary `atc-standards` E701/E702 override was introduced during the C-1
baseline cycle but became stale after the dedicated Ruff format commit
`94e948cce94c6a9e050735e082dbad1c78bede97`.

Exact-head Ruff evidence on `bafcde76a6fbcc53dec8387e26b16adc41ff2107` reports:

`RUFF_OVERRIDE_STALE: base-policy failures contain none of the relaxed rules: E701, E702`.

The override is therefore removed rather than retained as a permanent exception.
The historical raw baseline remains documented as 107 E701 + 70 E702; these are
not current gate debt after formatting.

Tracking issue: A-TownChain-Okosystems/.github#25.

## Review contract

Changes to this directory require review in the organization `.github` repository.
Caller workflows pin the reusable workflow and policy content by separate exact SHAs.
