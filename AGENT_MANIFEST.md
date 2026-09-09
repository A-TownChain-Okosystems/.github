# ATC Org-AGENT_MANIFEST — Rollenmodell (SCR-0039)

Org-weites Rollenmanifest; die Registrierung konkreter Agent-Instanzen bleibt in
den Repos (atc-standards/.github/ai/agent.yaml, registry/agents.yaml SSOT).

| Rolle | Aufgabe | Status (ehrlich) |
|---|---|---|
| ATC-AI-ARCH-001 | Architektur & Gesamtkoordination | PROFIL, durch Aurora abgedeckt |
| ATC-AI-AUDIT-001 | Repository-/Organisationsaudit | PROFIL, durch Aurora abgedeckt |
| ATC-AI-SEC-001 | Security | PROFIL — aktuell kein Agent fest zugeordnet |
| ATC-AI-CI-001 | CI/CD | PROFIL — aktuell kein Agent fest zugeordnet |
| ATC-AI-DOC-001 | Dokumentation & Standards | PROFIL, durch Aurora abgedeckt |
| ATC-AI-TEST-001 | Testing & QA | PROFIL — aktuell kein Agent fest zugeordnet |
| ATC-AI-RELEASE-001 | Releases & Versionierung | PROFIL — Owner-Gate-gebunden |
| ATC-AI-GOV-001 | Governance & Compliance | PROFIL, durch Aurora abgedeckt |

Rollen sind Kompetenzprofile — Instanzen weist ai/capabilities.yaml zu.
Registrierte Agent-Instanz (SSOT registry/agents.yaml im atc-standards-Repo):
Aurora (Base44 Superagent, Governance-/Entwicklungs-Agent).
