---
document_id: ATC-DOC-ARC-HUB-001
title: Repository Architecture Specification — Organisation Hub
version: 1.0.0
status: active
owner: A-TownChain-Okosystems
created: 2026-09-13
updated: 2026-09-13
standard: ATC-STD-MD-001
---

# Architecture Specification — .github (Organisation Hub)

## Übersicht

Das `.github`-Repository ist der Governance-Hub der Organisation (Registry: `ATC-REPO-HUB-001`,
Domäne `governance_hub`, EXEMPT-Klasse SCR-0075): org-weite Profil-Workflows, Agenten-Infrastruktur
und geteilte Ressourcen. Es enthält KEINEN Produktionscode.

## Subsysteme

1. **Org-Profile (`.github/workflows`, `profile/`):** Standard-Workflows und Profil-Definitionen, die auf alle Repos vererbt werden.
2. **Agenten-Infrastruktur (`agent-instructions/`, `ai/`, AGENTS.md, AGENT_MANIFEST.md):** Verbindliche Regeln und Manifeste für AI-Agenten (Governance: `a-townchain-os-docs` AGENT_POLICY).
3. **Wissen (`knowledge/`, `docs/`):** Org-weite Referenz-Dokumentation.
4. **Werkzeuge (`tools/`):** Geteilte Hilfsskripte.
5. **Evidence (`.atc/evidence/evidence.yaml`):** Ehrlicher Status-Level des Hubs (SCR-0080).

## Verantwortungsgrenzen

- Normative Standards und Registry: kanonisch in `atc-standards` — der Hub verteilt nur.
- Governance-Dokumentation: kanonisch in `a-townchain-os-docs` (AGENT_POLICY, DECISIONS_REGISTER).

## Registry-Einordnung

| Property | Value |
|---|---|
| Layer | L7 · Criticality C1 · Security S3 |
| Klasse | EXEMPT (SCR-0075) · Tier T0 · Maturity-Class A |
