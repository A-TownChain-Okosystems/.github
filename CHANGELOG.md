# Changelog

## [Unreleased] — 09.09.2026 (SCR-0065, Audit-Response .github)
### M1 Self-Consistency + M2 Validator-Härtung + M3-Vorbereitung
- ai/org-scope.yaml als Repository-Scope-SSOT (27 Repos, Quelle GitHub-API);
  README/AGENT_MANIFEST leiten sich ab (26→27-Inkonsistenz behoben, P2-01).
- AGENT_MANIFEST v1.2.0 vereinheitlicht (Footer/Selbstreferenz v1.1.0 → v1.2.0, P2-02).
- Kanonische Agent-Identität in ai/agent.yaml (id/instance_id/display_name/role, P2-03).
- Registry-Snapshot aktualisiert: 444 Standards (395 approved/37 candidate/12 draft),
  echtes Registry-Commit + SHA-256, binding.approved_only-Semantik.
- ai/state-machine.yaml: ungültiges YAML repariert (fehlendes Leerzeichen —
  Datei war unparierbar, fand sich über neuen T16-Parse-Gate).
- tools/test_agov.py gehärtet: T2 prüft CHECK-IDs exakt 001..020, T9 prüft die
  Kaskade wirklich (vorher wirkungslose Assertion), neu T15 Manifest-Versions-
  konsistenz + T16 Cross-File/Parse-Pflicht — jetzt 16 Tests (P1-03).
- requirements.txt (pyyaml mit Schranken) + GOV-SELF-AUDIT-001-Workflow-Patch
  bereit (docs/patches/, Owner-Aktion GH013 — P1-02/M3).
