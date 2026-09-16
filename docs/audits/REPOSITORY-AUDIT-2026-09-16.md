# Repository Audit — `.github`

Date: 2026-09-16
Status: **FINDINGS OPEN**
Mode: source/static GitHub audit; runtime CI is not inferred.

## Findings

### F-20260916-GH-001
- Priority: P1
- Class: Governance / Consistency
- Category: Stale generated metadata
- Family: Organization Governance / Agent Manifest / Registry Binding
- Tags: `P1`, `governance`, `manifest`, `registry`, `stale-metadata`, `consistency`
- Evidence: `AGENT_MANIFEST.md` contains a 449-standard / 50-family snapshot and 27 governed repositories, while the current organization audit baseline is 505 standards / 75 families and 31 repositories.
- Remediation: regenerate from the standards SSOT; do not maintain a second registry.
- Closure: re-read generated manifest and compare registry/repository snapshot with SSOT.

### F-20260916-GH-002
- Priority: P2
- Class: Configuration Quality
- Category: YAML duplicate key
- Family: Agent Governance / Machine-readable Configuration
- Tags: `P2`, `yaml`, `duplicate-key`, `agent-config`, `quality`
- Evidence: `ai/agent.yaml` contains `agent.role` twice with the same value.
- Remediation: remove the duplicate key and enforce duplicate-key-aware YAML validation.
- Closure: parse/lint the file with duplicate-key detection enabled.

### F-20260916-GH-003
- Priority: P1
- Class: Governance / Enforcement
- Category: Merge-gate enforcement
- Family: Agent Governance / Repository Protection
- Tags: `P1`, `merge-gate`, `admin-bypass`, `human-approval`, `enforcement`
- Evidence: `AGENTS.md` and `ai/governance-rules.yaml` explicitly document the known F-045 administrative-push bypass gap.
- Remediation: enforce required gates/human approval through effective branch protection/rulesets, or use a narrowly scoped audited emergency exception.
- Closure: inspect effective GitHub ruleset/branch-protection configuration and verify enforcement.

## Positive controls

- `AGENTS.md` defines an explicit governance hierarchy and fail-closed merge gates.
- `ai/governance-rules.yaml` defines registry snapshots, mandatory gates, exceptions, and conflict priority.
- `ai/agent.yaml` requires inspection, validation, security, regression, diff, and documentation review.
- README identifies `atc-standards/registry/standards.yaml` as the standards SSOT.

## Format / language

Markdown is appropriate for governance/audit records. YAML is appropriate for machine-readable governance configuration when schema and duplicate-key validation are enforced. Python is appropriate for governance tooling. No language migration is justified by this inspection.

## Closure rule

`.github` is **not complete** until the findings are remediated or accepted through the normative exception process and re-audited. No runtime CI PASS is claimed here.
