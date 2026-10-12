---
document_id: ATC-DOC-SEC-LAYER-001
title: ATC Security Layer
version: 1.0.0
status: active
owner: A-TownChain-Okosystems
---

# ATC Security Layer

The .github repository provides the organisation security baseline and audit implementation.

## Controls

| ID | Control | Severity | Enforcement |
|---|---|---:|---|
| SEC-P0-SECRET | Private keys and common credential patterns must not be committed | P0 | fail-closed |
| SEC-P0-PR-TARGET | pull_request_target requires explicit security review | P0 | fail-closed |
| SEC-P1-WORKFLOW-PERMISSIONS | Every workflow declares least-privilege permissions | P1 | fail-closed |
| SEC-P1-ACTION-PIN | Third-party Actions are pinned to immutable commit SHA | P1 | fail-closed |
| SEC-P1-CHECKOUT-CREDENTIALS | Checkout must disable credential persistence | P1 | fail-closed |
| SEC-P1-SECURITY-POLICY | SECURITY.md is present | P1 | fail-closed |
| SEC-P1-CODEOWNERS | CODEOWNERS is present | P1 | fail-closed |
| SEC-P1-LOCKFILE | A supported dependency lockfile is present | P1 | fail-closed |

## Execution

python3 tools/security_layer.py
python3 tools/security_layer.py --json

A PASS is valid only for the exact source SHA executed by CI.

## Design Rules

1. Fail closed on P0/P1 findings.
2. Never suppress or downgrade a finding to obtain PASS.
3. Keep workflow permissions least-privilege.
4. Pin external Actions to immutable commit SHAs.
5. Do not execute untrusted pull-request code with privileged credentials.
6. Security status is evidence-backed and source-SHA specific.
