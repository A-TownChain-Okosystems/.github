# Engineering Audit

Repository: `.github`
Status: BASELINE
Last verified: 2026-09-16

## Scope

This repository provides organization-wide GitHub defaults, governance documents, templates, and shared automation policy for A-TownChain-Okosystems.

## Verification contract

The repository is expected to remain documentation/configuration-only unless an explicit implementation is introduced. Changes must preserve organization governance, least-privilege CI permissions, and consistency with `atc-standards` and `atc-engineering`.

## Evidence

- Repository identity is defined by `README.md`.
- Governance and agent policy are maintained in the repository root.
- Security reporting is defined by `SECURITY.md`.
- Organization architecture is documented in `ARCHITECTURE.md`.
- Fleet-level executable verification is performed by `atc-engineering`.

## Known boundary

`atc-engineering` is the executable fleet audit control plane. This repository must not duplicate that implementation.
