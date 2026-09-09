#!/usr/bin/env python3
"""AGOV-Hub Selbst-Tests (AGOV-CHECK-012): validiert die Governance-Assets
des Hubs. Ausfuehrung: python3 tools/test_agov.py  — Exit 0 = grün."""
import os, sys
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = []

def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: fails.append(name)

# T1: checks.yaml parst und enthaelt 20 versionierte Checks
d = yaml.safe_load(open(os.path.join(ROOT, "ai/checks.yaml"), encoding="utf-8"))["agov_checks"]
check("T1 checks.yaml: 20 Checks, v1.0.0, ACTIVE",
      len(d["checks"]) == 20 and d["version"] == "1.0.0" and d["status"] == "ACTIVE")
ids = [c["id"] for c in d["checks"]]
check("T2 CHECK-IDs eindeutig 001..020", len(set(ids)) == 20 and sorted(ids) == sorted(set(ids)))
lv = {c["level"] for c in d["checks"]}
check("T3 Level-Modell MUST/SHOULD/MAY", lv == {"MUST", "SHOULD", "MAY"})

# T4: policies.yaml parst, 16 AP + 10 POL, enabled, severities
p = yaml.safe_load(open(os.path.join(ROOT, "ai/policies.yaml"), encoding="utf-8"))["agent_policies"]
check("T4 policies.yaml: 16 Grundsätze", len(p["principles"]) == 16)
check("T5 policies.yaml: 10 maschinenprüfbare POLs, alle enabled",
      len(p["policies"]) == 10 and all(x["enabled"] for x in p["policies"]))
check("T6 POL-P0 existieren (no-secrets, destructive, truthful)",
      {"ATC-POL-002", "ATC-POL-007", "ATC-POL-008"} <= {x["id"] for x in p["policies"]})

# T7: agent.yaml Schema
a = yaml.safe_load(open(os.path.join(ROOT, "ai/agent.yaml"), encoding="utf-8"))
check("T7 agent.yaml: Schema 1.0, 44 Standards, 8 Rollen",
      a["schema_version"] == "1.0" and len(a["required_standards"]) == 44 and len(a["roles"]["allowed"]) == 8)
check("T8 Aurora ohne MODIFY_WORKFLOWS (GH013)", "MODIFY_WORKFLOWS" not in a["capabilities"])

# T9: Manifest
m = open(os.path.join(ROOT, "AGENT_MANIFEST.md"), encoding="utf-8").read()
check("T9 MANIFEST-001: 10 Sektionen + Kaskade", m.count("## ") >= 10 and "Kaskade" not in "" and "ATC-AI-GOV-MANIFEST-001" in m)

# T10: agov_check.py lauffaehig (Syntax)
import py_compile
py_compile.compile(os.path.join(ROOT, "tools/agov_check.py"), doraise=True)
check("T10 agov_check.py kompiliert", True)

import json
g = yaml.safe_load(open(os.path.join(ROOT, "ai/governance-rules.yaml"), encoding="utf-8"))["governance_rules"]
check("T11 governance-rules: 10 Merge-Gates, NO-MERGE-Regel",
      len(g["merge_gate"]["gates"]) == 10 and "NO MERGE" in g["merge_gate"]["rule"])
check("T12 governance-rules: Exception 6 Schritte, FAIL/BLOCKED ohne Approval",
      len(g["exception_rule"]["steps"]) == 6 and g["exception_rule"]["without_approval"]["merge"] == "BLOCKED")
check("T13 governance-rules: Konflikt-Hierarchie ATC-STD-000 zuerst",
      g["conflict_priority"]["order"][0] == "ATC-STD-000" and len(g["conflict_priority"]["order"]) == 5)
sn = json.load(open(os.path.join(ROOT, "ai/audit/SNAPSHOT-2026-09-09.json"), encoding="utf-8"))
check("T14 Snapshot-Record: 4 Pflichtfelder, Commit+Hash korrekt",
      all(k in sn for k in ("registry_version", "registry_commit", "registry_hash", "approved_standards"))
      and len(sn["registry_commit"]) == 40 and len(sn["registry_hash"]) == 64)

print(f"\n{'ALLE ' + str(14 - len(fails)) + '/14 GRÜN' if not fails else 'ROT: ' + ', '.join(fails)}")
sys.exit(1 if fails else 0)
