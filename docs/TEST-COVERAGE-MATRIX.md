# Test-Coverage-Matrix — Governance-Nachweise (SCR-0067, Block 24)

Jede normative Regel erhaelt, soweit technisch moeglich, einen automatisierten Nachweis.
Gesamtstand: 23 Self-Tests (tools/test_agov.py) + 12 AGOV-Checks (tools/agov_check.py) + E-Stages.

| Control-Bereich | Policy / Regel | Validator | Test | Status |
|---|---|---|---|---|
| Checks-Katalog | GOV-012 | checks.yaml | T1, T2 | ✅ |
| Level-Modell | checks.yaml MUST/SHOULD | checks.yaml | T3 | ✅ |
| Policies | 16 Grundsaetze | policies.yaml | T4-T6 | ✅ |
| Agent-Identitaet | ATC-POL-001 | agent.yaml + Schema | T7, T17 | ✅ |
| Workflow-Scope | ATC-POL-009 / GH013 | agent.yaml capabilities | T8 | ✅ |
| Manifest | MANIFEST-001 (10 Sektionen + Kaskade) | AGENT_MANIFEST.md | T9, T15 | ✅ |
| Validator-Qualitaet | tools lauffaehig | py_compile | T10 | ✅ |
| Merge-Gates | governance-rules 10 Gates + NO-MERGE | governance-rules.yaml | T11-T13 | ✅ |
| Registry-Snapshot | Snapshot-Record | ai/audit/SNAPSHOT | T14, T17 | ✅ |
| Cross-File | Org-Scope-SSOT 27 | org-scope + README + Manifest | T16 | ✅ |
| Schema-Vertraege | 7 Schemas | ai/schemas/ | T17 | ✅ |
| Authorization | Capability-Kette | authorization.yaml | T18 | ✅ |
| Exceptions | Fail-Closed/expiry | exceptions.yaml | T19 | ✅ |
| Branch-Policy | F-045 enforce_admins | branch-policy.yaml + gov_drift | T20 + gov_drift | ✅ |
| Regression-KB | bekannte Fehlerfamilien | knowledge/regressions/ | T21 | ✅ |
| Policy-Graph | Abhaegigkeitskette | policy-graph.yaml | T22 | ✅ |
| Provenance | ID-Kette + Trailer | provenance.yaml | T23 | ✅ |
| Secrets | POL-002 | agov_check Secret-Scan | AGOV-CHECK-010 | ✅ (History-Scan: Roadmap) |
| Workflow-Perms | permissions read-all | agov_check | AGOV-CHECK-009/019 | ✅ |
| Drift | Branch-Protection Soll=Ist | gov_drift.py | org-weiter Lauf | ✅ |
| Score | P1 darf nicht verschleiert werden | gov_score.py | BLOCKED-Regel | ✅ |
| PR-Gates | 10 Merge-Gates | governance-rules.yaml | technisch: M3 ausstehend | ⚠️ Owner-Patch |
