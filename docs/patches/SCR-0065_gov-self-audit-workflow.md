# SCR-0065 — GOV-SELF-AUDIT-001: .github Self-Validation-Workflow (Owner-Aktion GH013)

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
      - name: AGOV Self-Tests (T1-T16, SCR-0065 gehaertet)
        run: python3 tools/test_agov.py
      - name: Org-Governance-Check Hub (.github)
        run: python3 tools/agov_check.py .github
        env:
          GITHUB_ACCESS_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Nachweis nach Anwendung
Erster Workflow-Lauf = Self-Governance-Schleife geschlossen (Audit P1-02/M3).
F-045 (Admin-Push-Bypass) bleibt separat als Owner-Entscheidung (M4):
Option enforce_admins=true auf .github/main wuerde auch Agenten-Direktpushes
blockieren (auch die beider Aurora-Instanzen) — bewusste Prozessentscheidung.
