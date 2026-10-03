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

The organization Ruff workflow currently uses:

- policy repository: A-TownChain-Okosystems/.github
- policy SHA: 7994fca8b24aef3572be1fa44adaf9c59fc13eb8
- policy directory variable: POLICY_DIR=.org-github-policy
- Ruff: 0.16.7
- caller scans remain fail-closed

The policy path is defined once and reused by checkout, configuration, and exclusion arguments.

## Failure class

Two prior incidents establish this as an infrastructure failure class:

- Markdown gate: policy checkout/layout caused the reusable workflow to address policy content incorrectly, producing an ENOENT failure.
- Ruff gate: policy content was physically inside the caller workspace and was therefore included by ruff ... ., producing a self-scan failure.

These are classified as WORKSPACE-ISOLATION, not caller-code baseline findings.

## Required evidence

For every reusable linting workflow, evidence MUST demonstrate:

1. exact caller commit/ref;
2. exact reusable-workflow SHA;
3. exact policy SHA;
4. policy checkout path;
5. scan root;
6. policy exclusion or external isolation mechanism;
7. tool version;
8. final step exit code.

A successful run alone is insufficient to prove isolation.
