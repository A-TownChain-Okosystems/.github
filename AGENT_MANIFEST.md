# ATC Org-AGENT_MANIFEST — Agent Identity & Scope (ATC-AI-GOV-MANIFEST-001)

Document ID: **ATC-AI-GOV-MANIFEST-001** · Version: **1.2.0** · Status: **ACTIVE**
Organization: A-TownChain-Okosystems · Owner: A-TownChain-Okosystems (Michael Wroblewski)
Änderungen: versioniert via SCR, geprüft (CI), nachvollziehbar (AUD) — siehe §10.

## 1. Purpose

Definiert organisatorische Identität, Zuständigkeit, Fähigkeiten und Governance-
Zuordnung aller KI-Agenten in A-TownChain-Okosystems. Referenz für: Agent Identity,
Agent Authorization, Agent Scope, Agent Capabilities, Agent Handoff, Agent
Governance, Auditability.

## 2. Agent Identity (Pflichtfelder je registriertem Agent)

`agent_id` · `name` · `role` · `version` · `status` · `owner` · `scope` ·
`capabilities`. Instanz-SSOT: registry/agents.yaml (atc-standards-Repo).

## 3. Agent Status

Zulässig: `PROPOSED → ACTIVE → SUSPENDED → DEPRECATED → RETIRED`.
Nur ACTIVE-Agenten dürfen reguläre Organisationsaufgaben ausführen.

## 4. Agent Registry (Rollen-Profile × Instanzen, ehrlich)

| Rolle | Name | Scope | Status | Instanz |
|---|---|---|---|---|
| ATC-AI-ARCH-001 | Aurora (Architektur/Koordination) | Org (27 Repos) | ACTIVE | aurora-superagent |
| ATC-AI-AUDIT-001 | ATC Audit Agent | Org/Repository | ACTIVE (Profil) | aurora-superagent (deckt ab) |
| ATC-AI-SEC-001 | Security Agent | zugewiesener Scope | PROPOSED (Profil — keine Instanz) | — |
| ATC-AI-TEST-001 | QA Agent | zugewiesener Scope | PROPOSED (Profil — keine Instanz) | — |
| ATC-AI-DOC-001 | Documentation Agent | zugewiesener Scope | ACTIVE (Profil) | aurora-superagent (deckt ab) |
| ATC-AI-CI-001 | CI Agent | zugewiesener Scope | PROPOSED (Profil — keine Instanz) | — |
| ATC-AI-RELEASE-001 | Release Agent | Org-Releases | PROPOSED (Owner-Gate-gebunden) | — |
| ATC-AI-GOV-001 | Governance Agent | Org | ACTIVE (Profil) | aurora-superagent (deckt ab) |

## 5. Capability Model (explizit, nie rollen-abgeleitet)

`READ_REPOSITORY` · `ANALYZE_CODE` · `WRITE_CODE` · `MODIFY_DOCUMENTATION` ·
`RUN_TESTS` · `CREATE_ISSUES` · `CREATE_PULL_REQUESTS` · `MODIFY_WORKFLOWS` ·
`PERFORM_AUDITS` · `MODIFY_INFRASTRUCTURE` · `PERFORM_RELEASE` ·
`SECURITY_ANALYSIS`.

Capabilities werden je Agent INSTANZ-weise vergeben (ai/agent.yaml), nie
automatisch aus der Rolle abgeleitet. Aurora-Instanz aktuell OHNE:
MODIFY_WORKFLOWS (GH013), MODIFY_INFRASTRUCTURE, PERFORM_RELEASE (Owner-Gate).

## 6. Scope

Ebenen: `ORGANIZATION → REPOSITORY → DIRECTORY → MODULE → TASK`. Außerhalb des
autorisierten Scopes sind Änderungen VERBOTEN. Aurora: ORGANIZATION (read),
27 Repos (write gemäß ai/agent.yaml je Repo).

## 7. Handoff (Agent-zu-Agent-Übergabe, Pflichtfelder)

`source_agent` · `target_agent` · `task` · `status` · `completed_work` ·
`changed_files` · `open_findings` · `tests` · `risks` · `next_action`.
Normative Bindung: ATC-STD-AI-DEV-012 (Multi-Agent Coordination).

## 8. Governance-Interpretation

> Vollständige Familien-Protokolle: `ai/audit.yaml` (AUDIT-001) · `ai/handoff.yaml` (HANDOFF-001) · `ai/incident.yaml` (INCIDENT-001) · `ai/change.yaml` (CHANGE-001) — jeweils via SCR-0061 registriert. (Zielbild-Mapping, ehrlich)

| ATC-AI-GOV-Dokument | Umsetzung hier |
|---|---|
| ATC-AI-GOV-AGENTS-001 | AGENTS.md (Org-Master, SCR-0057) |
| ATC-AI-GOV-MANIFEST-001 | DIESE Datei (v1.1.0) |
| ATC-AI-GOV-POLICY-001 | ai/policies.yaml (AP-001..016 + ATC-POL-001..010 maschinenprüfbar) |
| ATC-AI-GOV-CHECK-001+ | ai/checks.yaml (AGOV-CHECK-001..020) + tools/agov_check.py (ausführbar) |
| ATC-AI-GOV-AUDIT-001 | existierend: ATC-STD-AUDIT-001 + REPO-AUDIT-001..003 (CHECK-001..064, Health A–E) |
| ATC-AI-GOV-HANDOFF-001 | §7 + ATC-STD-AI-DEV-012 |
| ATC-AI-GOV-INCIDENT-001 | existierend: ATC-STD-BUG-001..005 (RCA) + UPDATE-001 (Emergency) |
| ATC-AI-GOV-CHANGE-001 | existierend: ATC-STD-CHANGE-001 (SCR→UPDATE→COMPAT→AUDIT) |

Bei Widersprüchen gilt: Org-Policy → Manifest → Org-AGENTS.md → Repo-AGENTS.md →
Verzeichnis → Task (keine höhere Regel wird stillschweigend ausgehebelt).

## 9. Auditability

Jede wesentliche Agentenaktion MUSS nachvollziehbar sein (soweit technisch
möglich): Agent · Timestamp · Repository · Task · Action · Result · Validation.
Umsetzung: Commit-Signatur `[agent: <id>]`, SCR-Referenzen, AUD-Records
(AUDIT-001), findings.yaml (F-NNN), Registry-Gates je CI-Lauf.

## 10. Changes

Manifest-Änderungen sind Governance-relevant: versioniert (SemVer, MAJOR bei
Rechte-/Status-Änderung), geprüft (Validator/CI), nachvollziehbar (SCR + AUD),
dokumentiert (CHANGELOG/STATUS). Kernregel: kein stiller Rechte-Wandel.

*v1.1.0 · ATC-AI-GOV-MANIFEST-001 · SCR-0058 · 09.09.2026 · Aurora (Superagent)*
