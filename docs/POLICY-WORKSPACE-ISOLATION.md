# Policy Workspace Isolation Contract

Status: REQUIRED
Scope: centralized CI/linting workflows in the A-TownChain organization

## Rule

A policy repository checked out by a reusable workflow is control-plane input, not caller source.

A lint, format, test, build, or discovery command MUST NOT accidentally treat the checked-out policy tree as caller-owned content.

Reusable workflows MUST satisfy one of these isolation patterns:

1. place policy material outside the scan root; or
2. use one centrally defined policy-directory variable and explicitly exclude that directory from every scan that operates on the caller workspace.

The policy directory MUST NOT be excluded by weakening the actual caller scan, continue-on-error, || true, or similar fail-open behavior.

## Canonical Ruff implementation

The organization Ruff workflow uses:

- policy repository: A-TownChain-Okosystems/.github
- reusable workflow SHA: pinned by each caller
- policy bundle SHA: pinned separately by the reusable workflow
- policy directory variable: POLICY_DIR=.org-github-policy
- Ruff: 0.16.7
- caller scans remain fail-closed

The workflow must record both exact SHAs because a Git commit cannot self-reference its own final SHA. The reusable workflow commit and the checked-out policy-content commit are therefore separate exact inputs.

## Failure classes

Three infrastructure failure classes are covered by this contract:

- Markdown gate: policy checkout/layout caused the reusable workflow to address policy content incorrectly, producing an ENOENT failure.
- Ruff gate: policy content was physically inside the caller workspace and was therefore included by ruff ... ., producing a self-scan failure.
- Policy-bundle syntax: malformed TOML in a centrally supplied policy file caused CI to fail before it could make a valid statement about caller code.

The first two are classified as WORKSPACE-ISOLATION. The third is classified as POLICY-BUNDLE-SYNTAX.

## Required policy validation

Before any policy TOML is loaded for configuration or override evaluation, the reusable workflow MUST validate the syntax of:

- the base ruff.toml;
- every TOML file under ruff-overrides/.

Validation MUST use Python 3.11+ `tomllib` and MUST fail closed. A syntax failure is a policy infrastructure failure, not a caller-code Ruff finding.

## Required evidence

For every reusable linting workflow, evidence MUST demonstrate:

1. exact caller commit/ref;
2. exact reusable-workflow SHA;
3. exact policy SHA;
4. policy checkout path;
5. scan root;
6. policy exclusion or external isolation mechanism;
7. tool version;
8. policy syntax-validation result;
9. final step exit code.

A successful run alone is insufficient to prove isolation or policy integrity.
