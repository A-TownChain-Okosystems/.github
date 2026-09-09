#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# OWNER-ONLY (GH013): AGOV-CHECK-009/019 — fuegt je Workflow-Datei einen
# permissions-Block ein (read-all, least-privilege) und pusht je Repo.
# VORHER pruefen: Workflows mit Write-Bedarf (release/pages/deploy/sync)
# brauchen individuelle permissions — nicht blind read-all setzen.
# Ausfuehrung: im .github-Hub-Verzeichnis mit Owner-authentifiziertem Git.
# Arbeitskopien unter .tmp-owner-fix/ — nach Lauf manuell loeschen.
# ═══════════════════════════════════════════════════════════════════════════
set -euo pipefail
REPOS="a-townchain a-townchain-os a-townchain-os-docs atc-algorithm atc-compute atc-contracts atc-explorer atc-indexer atc-interop atc-launchpad atc-marketplace atc-mining atc-node atc-oracle atc-sdk atc-shivacore atc-standards atc-storage atc-vm atc-wallet atc-zkp atclang aurora-ai genesis-chronicles genesis-engine globus-os"
mkdir -p .tmp-owner-fix
for r in $REPOS; do
  echo "== $r"
  git clone -q "https://github.com/A-TownChain-Okosystems/$r.git" ".tmp-owner-fix/$r"
  changed=0
  for wf in ".tmp-owner-fix/$r"/.github/workflows/*.yml ".tmp-owner-fix/$r"/.github/workflows/*.yaml; do
    [ -f "$wf" ] || continue
    if ! grep -q "^permissions:" "$wf"; then
      sed -i '0,/^jobs:/s//permissions: read-all\njobs:/' "$wf"
      git -C ".tmp-owner-fix/$r" add "$wf" && changed=1
      echo "   permissions-Block ergänzt: $(basename "$wf")"
    fi
  done
  if [ "$changed" = "1" ]; then
    git -C ".tmp-owner-fix/$r" commit -q -m "fix(ci): permissions read-all je Workflow (AGOV-CHECK-009, ATC-POL-009, SCR-0058 Owner-Aktion)"
    git -C ".tmp-owner-fix/$r" push -q origin main && echo "   gepusht"
  else
    echo "   nichts zu tun"
  fi
done
echo "Fertig. Arbeitskopien unter .tmp-owner-fix/ manuell entfernen."
echo "Danach: python3 tools/agov_check.py  (Erneuter AGOV-Lauf)"
