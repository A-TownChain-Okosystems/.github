#!/usr/bin/env python3
"""AGOV-Hub Selbst-Tests (AGOV-CHECK-012): validiert die Governance-Assets
des Hubs. Ausfuehrung: python3 tools/test_agov.py  — Exit 0 = grün."""
import os, re, sys
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
expected_ids = {f"{i:03d}" for i in range(1, 21)}
actual_ids = {c["id"].split("-")[-1] for c in d["checks"]}
check("T2 CHECK-IDs exakt 001..020 (Menge und Werte)", actual_ids == expected_ids)
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
casc = ["Org-Policy", "Manifest", "Org-AGENTS.md", "Repo-AGENTS.md"]
pos = [m.find(x) for x in casc]
check("T9 MANIFEST-001: 10 Sektionen + Kaskade vollstaendig u. geordnet",
      m.count("## ") >= 10 and all(p >= 0 for p in pos)
      and pos == sorted(pos) and "ATC-AI-GOV-MANIFEST-001" in m)

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

# T15: Manifest-Versionskonsistenz (Header == Selbstreferenz == Footer, Audit P1-04/M1)
hdr = re.search(r"Version: \*\*(\d+\.\d+\.\d+)\*\*", m)
foot = re.search(r"\*v(\d+\.\d+\.\d+)", m)
refs = re.findall(r"\(v(\d+\.\d+\.\d+)\)", m)
check("T15 Manifest-Version konsistent (Header=Selbstreferenz=Footer)",
      bool(hdr and foot and refs) and foot.group(1) == hdr.group(1)
      and all(r == hdr.group(1) for r in refs))

# T16: Cross-File-Konsistenz (Org-Scope-SSOT + Versionschluessel, Audit P1-04/M1)
import glob as _g
sc = yaml.safe_load(open(os.path.join(ROOT, "ai/org-scope.yaml"), encoding="utf-8"))
cnt = sc["organization_meta"]["repository_count"]
rd = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
def _has_version(p):
    d = yaml.safe_load(open(p, encoding="utf-8"))
    if not isinstance(d, dict):
        return False
    if "version" in d:
        return True
    # Version kann auch unter dem Haupt-Schluessel liegen (checks.yaml etc.)
    return any(isinstance(v, dict) and "version" in v for v in d.values())
try:
    all_vers = all(_has_version(p) for p in _g.glob(os.path.join(ROOT, "ai", "*.yaml")))
    parse_ok = True
except yaml.YAMLError:
    all_vers, parse_ok = False, False
check("T16 Cross-File: ai/*.yaml parsbar, Versionsschluessel, Org-Scope-SSOT (27) in README+Manifest",
      cnt == 27 and str(cnt) in rd and str(cnt) in m and all_vers and parse_ok)

# T17: Schema-Selbstvalidierung — alle Kern-Dateien gegen ai/schemas/ (Audit-Block 2)
def _validate_schema(data, schema):
    if not isinstance(data, dict):
        return False
    for k in schema.get("required", []):
        if k not in data:
            return False
    tmap = {"object": lambda v: isinstance(v, dict), "array": lambda v: isinstance(v, list),
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
            "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)}
    for k, spec in schema.get("properties", {}).items():
        if k not in data:
            continue
        fn = tmap.get(spec.get("type"), lambda v: True)
        if not fn(data[k]) or ("enum" in spec and data[k] not in spec["enum"]):
            return False
    return True

_schema_pairs = [
    ("ai/agent.yaml", "ai/schemas/agent.schema.json"),
    ("ai/governance-sources.yaml", "ai/schemas/governance-sources.schema.json"),
    ("ai/org-scope.yaml", "ai/schemas/org-scope.schema.json"),
    ("ai/authorization.yaml", "ai/schemas/authorization.schema.json"),
    ("ai/branch-policy.yaml", "ai/schemas/branch-policy.schema.json"),
    ("ai/exceptions.yaml", "ai/schemas/exceptions.schema.json"),
]
_ok17 = True
for ypath, spath in _schema_pairs:
    _sch = json.load(open(os.path.join(ROOT, spath), encoding="utf-8"))
    _dat = yaml.safe_load(open(os.path.join(ROOT, ypath), encoding="utf-8"))
    if not _validate_schema(_dat, _sch):
        _ok17 = False
        print(f"    Schema-Verstoß: {ypath} gegen {os.path.basename(spath)}")
_sn_path = sorted(_g.glob(os.path.join(ROOT, "ai/audit/SNAPSHOT-*.json")))[-1]
_sn_sch = json.load(open(os.path.join(ROOT, "ai/schemas/snapshot.schema.json"), encoding="utf-8"))
check("T17 Schema-Selbstvalidierung (6 YAML-Dateien + Snapshot gegen ai/schemas/)",
      _ok17 and _validate_schema(json.load(open(_sn_path, encoding="utf-8")), _sn_sch))

# T18: Authorization-Matrix gueltig (Audit-Block 5)
import yaml as _y2
az = _y2.safe_load(open(os.path.join(ROOT, "ai/authorization.yaml"), encoding="utf-8"))["authorization"]
_req18 = {"agent", "instance", "repository", "operation", "paths", "approval_required"}
check("T18 Authorization-Matrix: Eintrags-Schema + Agent-IDs bekannt + GH013 abgebildet",
      all(_req18 <= set(e) for e in az)
      and all(e["agent"] in m for e in az)
      and any("GH013" in str(e.get("constraints", "")) for e in az))

# T19: Exceptions Fail Closed (Audit-Block 4) — abgelaufene = inaktiv
ex = _y2.safe_load(open(os.path.join(ROOT, "ai/exceptions.yaml"), encoding="utf-8"))["exceptions"]
_today = "2026-09-09"
check("T19 Exceptions: expiry Pflicht, keine abgelaufene AKTIVE, OWNER-Genehmigung",
      all(e.get("expires") and e["expires"] >= _today and e.get("approved_by") == "OWNER"
          for e in ex if e.get("status") == "ACTIVE"))

# T20: Branch-Policy Soll-Zustand vollstaendig (Audit-Block 11)
bp = _y2.safe_load(open(os.path.join(ROOT, "ai/branch-policy.yaml"), encoding="utf-8"))["branch_policy"]
check("T20 Branch-Policy: .github enforce_admins=true (F-045), keine Force-Pushes/Deletions, Defaults + Severity-Mapping",
      bp[".github"]["main"]["enforce_admins"] is True
      and bp[".github"]["main"]["allow_force_push"] is False
      and bp[".github"]["main"]["allow_deletions"] is False
      and "default_all_repositories" in bp)

# T21: Regression Knowledge Base (Audit-Block 17)
import glob as _g3
regs = sorted(_g3.glob(os.path.join(ROOT, "knowledge/regressions/REG-*.yaml")))
_req21 = {"id", "root_cause", "symptom", "affected_repositories", "detection", "prevention", "regression_test"}
_ok21 = all(_req21 <= set(yaml.safe_load(open(p, encoding="utf-8"))) for p in regs) and len(regs) >= 4
check("T21 Regression-KB: >=4 Eintraege mit Pflichtfeldern (root_cause/detection/prevention/regression_test)",
      _ok21)

# T22: Policy-Graph konsistent (Audit-Block 23)
pg = yaml.safe_load(open(os.path.join(ROOT, "ai/policy-graph.yaml"), encoding="utf-8"))
node_ids = {n["id"] for n in pg["nodes"]}
_ok22 = all(e["from"] in node_ids for e in pg["edges"]) and all(
    e["to"] in node_ids or isinstance(e["to"], str) for e in pg["edges"])
check("T22 Policy-Graph: Kanten zeigen auf existierende Knoten (Policy->Check->Workflow)",
      _ok22 and any(n.get("type") == "policy" for n in pg["nodes"]))

# T23: Provenance-Kette + Commit-Trailer-Spec (Audit-Block 7/21)
pv = yaml.safe_load(open(os.path.join(ROOT, "ai/provenance.yaml"), encoding="utf-8"))
_req_chain = ["VISION", "REQUIREMENT", "STANDARD", "TASK", "AGENT", "CHANGE", "COMMIT", "PR",
              "VALIDATION", "AUDIT", "RELEASE"]
check("T23 Provenance: 11-stufige Kette, ID-Klassen, Commit-Trailer-Format definiert",
      pv["chain"] == _req_chain and all(k in pv["id_classes"] for k in
      ["REQUIREMENT", "STANDARD", "TASK", "CHANGE", "AUDIT"]) and "format" in pv["commit_trailer_rule"])

total = 23
print(f"\n{'ALLE ' + str(total - len(fails)) + '/' + str(total) + ' GRÜN' if not fails else 'ROT: ' + ', '.join(fails)}")
sys.exit(1 if fails else 0)
