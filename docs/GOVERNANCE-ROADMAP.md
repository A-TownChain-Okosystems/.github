# Governance-Roadmap — .github als ausfuehrbare Control Plane

Owner-Architekturvision 09.09.2026 (25 Bausteine) — Ziel: .github wird von einem
Governance-Dokumentations-Hub zu einer ausfuehrbaren Governance-Control-Plane:
Schema -> Registry -> Policy -> Control -> Validator -> Evidence -> Finding ->
Remediation -> Regression -> Enforcement.

## P1 — Status

| # | Baustein | Status | Umsetzung |
|---|---|---|---|
| 1 | SSOT-Matrix (governance_sources) | ✅ LIVE | ai/governance-sources.yaml + T16-Verdrahtung |
| 2 | Schema-System | ✅ LIVE | ai/schemas/ (7 Vertraege) + T17 Schema-Selbstvalidierung |
| 3 | Finding-Lifecycle | ✅ LIVE | finding-schema.yaml: OPEN->CLASSIFIED->...->CLOSED + owner/component/root_cause/affected_scope/duplicate_of/regression_check/resolution/validation_evidence |
| 4 | Exception-Lifecycle | ✅ LIVE | Fail-Closed (expires Pflicht), risiko/kompensationskontrolle/review_date + T19 |
| 5 | Agent Authorization Matrix | ✅ LIVE | ai/authorization.yaml (Capability->Repo->Branch->Operation->Approval) + T18 |
| 6 | Branch-/Ruleset-Drift Detection | ✅ LIVE | tools/gov_drift.py (Soll vs. Ist, GOV-DRIFT-Findings, P1/P2-Mapping) |
| 7 | Self-Test haerten | ✅ LIVE | 20 Tests (T2 exakt, T9 echte Kaskade, T15/T16 Cross-File, T17-T20) |
| 8 | Cross-File-Consistency | ✅ LIVE | T15/T16/T17 |
| 9 | Self-CI (GOV-SELF-AUDIT-001) | ⏳ Owner-Patch | docs/patches/SCR-0065_gov-self-audit-workflow.md (GH013) |
| 10 | F-045 Admin-Push-Enforcement | ✅ CLOSED | Owner-Ja 09.09.: enforce_admins=true auf .github/main, Governance via PR + 10 Gates |
| — | Change Impact Analysis | ⏳ SCR-0067 | tools/gov_impact.py geplant (Policy-Aenderung -> betroffene Standards/Agenten/Repos) |

## P2 — Backlog (Reihenfolge gemaess Owner-Priorisierung)

11. Provenance Chain (REQ->STD->SCR->TASK->CHG->PR->VALIDATION->AUDIT->REL)
12. Regression Knowledge Base (knowledge/regressions/REG-XXX.yaml)
13. Dependency/Supply-Chain Governance (CVEs, Lockfiles, transitive, Lizenzen)
14. SBOM/Release Provenance
15. Repository Bootstrap/Onboarding (NEW REPO->...->COMPLIANT)
16. Repository Decommissioning (ACTIVE->...->ARCHIVED)
17. Compliance Score (Score darf P0/P1 nicht verschleiern: P1 exists = BLOCKED)
18. Policy Dependency Graph
19. Disaster Recovery (GOV-ROLLBACK/RECOVERY/RESTORE)
20. Governance Release/Compatibility System (ATC-GOV v1.x)
21. Session/Task Identity je Commit (task_id/session_id/scr)
22. Secrets: History-Scan, Rotation/Revocation-Workflow, Incident-Linkage
23. Org-Level Rulesets (statt 27 Einzelkonfigurationen)
24. Test-Coverage-Matrix (Control->Policy->Validator->Test->CI je normativer Regel)
25. Incident->Governance Feedback Loop (RCA->Missing Control->Standard->Validator->Regression->Org-Scan)

## Zielarchitektur

IDENTITY + POLICY + STANDARDS -> CONTROL ENGINE -> AUDIT/SECURITY/VALIDATION/
DRIFT/COMPLIANCE -> EVIDENCE STORE (Findings/Audits/Snapshots) -> CHANGE
CONTROL (SCR->PR->REVIEW->MERGE) -> RELEASE CONTROL.
