#!/usr/bin/env python3
# Copyright (c) 2026 Michael Wroblewski / A-TownChain-Okosystems. All Rights Reserved.
"""GOV-IMPACT — Change Impact Analysis (SCR-0067, Audit-Block 22).

Bei einer Aenderung an einer Governance-Datei wird automatisch ermittelt,
welche Policies, Checks, Tests, Workflows und Repositories betroffen sind.

Aufruf: python3 tools/gov_impact.py ai/policies.yaml
Ergebnis: impact-Objekt mit risk-Bewertung + owner_gate (wie Owner-Vorgabe).
"""
import json
import os
import sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

def load(p):
    return yaml.safe_load(open(os.path.join(ROOT, p), encoding="utf-8"))

def impact_for(path):
    pg = load("ai/policy-graph.yaml")
    gs = load("ai/governance-sources.yaml")["governance_sources"]
    canonical = {v["canonical"]: k for k, v in gs.items()}
    domain = canonical.get(path)
    hits = []
    for n in pg.get("nodes", []):
        f = n.get("file", "")
        if f == path or (f and f.rstrip('/') and path.startswith(f.rstrip('/'))):
            hits.append(n)
    pols, checks, tests, wfs, repos = set(), set(), set(), set(), set()
    for n in hits:
        if n.get("type") == "policy":
            pols.add(n["id"])
        if n.get("type") == "check":
            checks.add(n["id"])
        checks.update(n.get("checks", []))
        tests.update(n.get("validates", []) or n.get("tested_by", []))
        if n.get("workflows"):
            wfs.add(n["workflows"])
        if n.get("scopes"):
            repos.update(n["scopes"])
    risk = "P1" if (domain in ("policies", "merge_gates", "authorization", "branch_policy") or
                    path.endswith("governance-rules.yaml")) else "P2"
    return {"changed_file": path, "domain": domain,
            "policies": sorted(pols), "checks": sorted(checks), "tests": sorted(tests),
            "workflows": sorted(wfs), "repositories": sorted(repos),
            "risk": risk, "owner_gate": "required" if risk == "P1" else "recommended"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Aufruf: gov_impact.py <geaenderte Datei>"); sys.exit(2)
    print(json.dumps(impact_for(sys.argv[1]), indent=2, ensure_ascii=False))
    sys.exit(0)
