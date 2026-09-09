# SCR-0065/0066 — GOV-SELF-AUDIT-001: .github Self-Validation-Workflow (Owner-Aktion GH013)

## Status
BEREIT — wartet auf Owner-Anwendung (Workflow-Datei = GH013). Alternativ:
workflow-Scope fuer Aurora, dann pusht und verifiziert Aurora selbst.

## Patch — .github/workflows/.github-governance.yml (NEU anlegen)

```yaml
name: GOV-SELF-AUDIT-001 (.github Self-Validation)
on:
  push:
  pull_request:
  workflow_dispatch:

jobs:
  self-governance:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies (ATC-STD-CI-001, CI-003)
        run: pip install -r requirements.txt
      - name: AGOV Self-Tests (T1-T20: Cross-File, Schema, Authorization, Branch-Policy)
        run: python3 tools/test_agov.py
      - name: Org-Governance-Check Hub (.github)
        run: python3 tools/agov_check.py .github
        env:
          GITHUB_ACCESS_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Branch-Protection-Drift (Soll vs. Ist, SCR-0066)
        run: python3 tools/gov_drift.py --repo .github
        env:
          GITHUB_ACCESS_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Nachweis nach Anwendung
Self-Governance-Schleife geschlossen: jede Hub-Aenderung laeuft gegen
T1-T20 + agov_check + Branch-Protection-Drift. Danach in ai/branch-policy.yaml
require_status_checks auf true stellen (Governance-Release M5).

## F-045: GESCHLOSSEN (Owner-Entscheidung 09.09. — Ja zu PR + 10 Gates)
enforce_admins=true auf .github/main ist aktiv gesetzt (SCR-0066); kuenftig
laufen Governance-Aenderungen am Hub ausschliesslich via PR + Review —
auch fuer beide Aurora-Instanzen und den Automator.
