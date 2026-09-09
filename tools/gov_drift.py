#!/usr/bin/env python3
# Copyright (c) 2026 Michael Wroblewski / A-TownChain-Okosystems. All Rights Reserved.
"""GOV-DRIFT — Branch-Protection Drift Detection (SCR-0066, Audit-Block 11/12).

Vergleicht ai/branch-policy.yaml (Soll) gegen die GitHub-API (Ist) fuer alle
Repos aus ai/org-scope.yaml. Desired != Actual => GOV-DRIFT-Finding.

Aufruf:
  python3 tools/gov_drift.py               # alle 27 Repos, Report + P1-Exit
  python3 tools/gov_drift.py --repo .github # nur ein Repo (fuer Self-CI)
Exit: 0 = kein P1-Drift, 1 = P1-Drift (Blocker).
"""
import json
import os
import sys
import urllib.request
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

bp = yaml.safe_load(open(os.path.join(ROOT, "ai/branch-policy.yaml"), encoding="utf-8"))
sc = yaml.safe_load(open(os.path.join(ROOT, "ai/org-scope.yaml"), encoding="utf-8"))
repos = sc["repositories"]
only = None
if len(sys.argv) > 2 and sys.argv[1] == "--repo":
    only = sys.argv[2]
    repos = [r for r in repos if r == only]

token = os.environ.get("GITHUB_ACCESS_TOKEN", "")
ORG = "A-TownChain-Okosystems"

def get(url):
    req = urllib.request.Request(url, headers={"Authorization": "token " + token,
                                                "Accept": "application/vnd.github+json"})
    try:
        return json.loads(urllib.request.urlopen(req).read()), None
    except urllib.error.HTTPError as e:
        return None, e.code

def desired(repo):
    return bp["branch_policy"].get(repo, bp["branch_policy"]["default_all_repositories"])["main"]

findings = []
for repo in repos:
    d = desired(repo)
    prot, code = get(f"https://api.github.com/repos/{ORG}/{repo}/branches/main/protection")
    actual = {"require_pull_request": False, "enforce_admins": False,
              "allow_force_push": True, "allow_deletions": True,
              "required_reviews": 0}
    if code == 404 or prot is None:
        sev = bp["severity_mapping"]["missing_protection"].get(repo, "P2")
        findings.append((repo, "missing_protection", "erwartet: Protection aktiv", "kein Protection-Record", sev))
        continue
    try:
        rpr = prot.get("required_pull_request_reviews") or {}
        actual = {"require_pull_request": bool(prot.get("required_pull_request_reviews")),
                  "enforce_admins": bool(prot.get("enforce_admins", {}).get("enabled")),
                  "allow_force_push": bool(prot.get("allow_force_pushes", {}).get("enabled")),
                  "allow_deletions": bool(prot.get("allow_deletions", {}).get("enabled")),
                  "required_reviews": len(rpr.get("dismissal_restrictions") or []) }
        actual["required_reviews"] = rpr.get("required_approving_review_count", 0)
    except Exception as e:
        findings.append((repo, "protection_parse", str(e), "-", "P2"))
        continue
    checks = [
        ("require_pull_request", d["require_pull_request"], actual["require_pull_request"], "P2"),
        ("enforce_admins", d["enforce_admins"], actual["enforce_admins"],
         bp["severity_mapping"]["enforce_admins_drift"].get(repo, "P2")),
        ("allow_force_push", False, actual["allow_force_push"],
         bp["severity_mapping"]["force_push_allowed"]),
        ("allow_deletions", False, actual["allow_deletions"],
         bp["severity_mapping"]["deletions_allowed"]),
    ]
    for ctrl, exp, act, sev in checks:
        if exp != act:
            findings.append((repo, "branch_protection", ctrl, f"expected={exp}, actual={act}", sev))

p1 = [f for f in findings if f[4] == "P1"]
print(f"== GOV-DRIFT ({len(repos)} Repos geprueft) ==")
for repo, ctrl, exp, act, sev in findings:
    print(f"  [DRIFT {sev}] {repo}: {ctrl} — {exp} | actual: {act}")
if not findings:
    print("  Kein Drift: alle Repos im Soll-Zustand.")
print(f"RESULT: {'P1-BLOCKER: ' + str(len(p1)) if p1 else 'OK'} ({len(findings)} Drift-Findings gesamt)")
sys.exit(1 if p1 else 0)
