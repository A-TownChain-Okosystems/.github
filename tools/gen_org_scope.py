#!/usr/bin/env python3
"""Generiert ai/org-scope.yaml aus der GitHub-API (SCR-0068, Format SCR-0065).

Org-Scope als SSOT: Repository-Count darf nie manuell gepflegt werden.
Ergaenzt SCR-0065 um live Regeneration + Governance-KPIs
(GOVERNED_/UNGOVERNED_REPOSITORY_COUNT, DRIFT_COUNT)."""
import os, base64, datetime
import requests, yaml

ORG = "A-TownChain-Okosystems"
H = {"Authorization": "Bearer " + os.environ["GITHUB_ACCESS_TOKEN"]}
def get(p): return requests.get("https://api.github.com" + p, headers=H)

repos, page = [], 1
while True:
    j = get(f"/orgs/{ORG}/repos?per_page=100&page={page}").json()
    if not j: break
    repos += [r["name"] for r in j if not r.get("archived")]
    page += 1

governed, ungoverned = [], []
for rp in sorted(repos):
    r = get(f"/repos/{ORG}/{rp}/contents/AGENTS.md")
    if r.status_code == 200:
        ag = base64.b64decode(r.json()["content"]).decode("utf-8", "replace")
        (governed if (".github" in ag and "Kaskade" in ag) else ungoverned).append(rp)
    else:
        ungoverned.append(rp)

now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
scope = {
  "version": "1.1.0",
  "status": "ACTIVE",
  "organization": ORG,
  "organization_meta": {
    "repository_count": len(repos),
    "repository_scope": {"source": "github-api", "snapshot": now,
                         "generator": "tools/gen_org_scope.py"},
  },
  "governance_kpi": {
    "GOVERNED_REPOSITORY_COUNT": len(governed),
    "UNGOVERNED_REPOSITORY_COUNT": len(ungoverned),
    "DRIFT_COUNT": len(ungoverned),
    "ungoverned": ungoverned,
  },
  "repositories": sorted(repos),
  "governed": governed,
  "ungoverned": ungoverned,
}
yaml.dump(scope, open("ai/org-scope.yaml", "w", encoding="utf-8"),
          sort_keys=False, allow_unicode=True, default_flow_style=False)
print(f"Org: {len(repos)} · governed: {len(governed)} · ungoverned: {len(ungoverned)} → {ungoverned}")
