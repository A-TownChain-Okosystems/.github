# ATC Org-weites Agent-Governance-System (`.github`-Hub)

Dieses Repository ist der **zentrale, vererbbare Organisationsstandard** für alle
KI-Agenten in A-TownChain-Okosystems (SCR-0057, 09.09.2026). Als `.github`-Repo
stellt es Org-weite Dateien bereit; jedes ATC-Repository dockt über den Verweis-
Block in seiner AGENTS.md an (Pflicht; Ist-Zustand API-generiert in [ai/org-scope.yaml](ai/org-scope.yaml),
Erzeugung via tools/gen_org_scope.py — Zählungen nie von Hand pflegen).

**Einstieg:** `AGENTS.md` (Org-Master) · `agent-instructions/00..11` (12 Module) ·
`ai/agent.yaml` + `ai/policies.yaml` (AP-001..016, normativ) + `ai/capabilities.yaml`
(8 Rollen ATC-AI-ARCH/AUDIT/SEC/CI/DOC/TEST/RELEASE/GOV-001) · `AGENT_MANIFEST.md`.

**Hierarchie (spezifischer ergänzt, nie höhere Regeln ausgehebelt):**
Org-Policy → AGENT_MANIFEST → Org-AGENTS.md → Repo-AGENTS.md → Verzeichnis-Regeln → Task.
**Fachliche Wahrheit:** Registry-SSOTs im atc-standards-Repo (433 Standards (Stand 09.09.2026),
Validator S-01..S-25) · kanonisch: REALITY_STATUS.md (a-townchain-os-docs).

*Copyright (c) 2026 Michael Wroblewski · Apache-2.0 · SCR-0057*
