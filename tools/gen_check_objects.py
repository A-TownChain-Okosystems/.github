#!/usr/bin/env python3
"""Generiert ai/checks/CHECK-001..020.yaml aus dem Katalog ai/checks.yaml (Phase 2, SCR-0063).
Regenerierung nur via SCR; Pilot-Objekte 001/010 bleiben unberuehrt, wenn --force fehlt."""
import yaml, os, sys

TYPES = {
    "001": ("file_exists", {"path": "AGENTS.md"}),
    "002": ("content_match", {"path": "AGENTS.md", "pattern": "AGENT_MANIFEST|\\.github/AGENTS\\.md|ATC-AI-GOV"}),
    "003": ("content_match", {"path": "AGENTS.md", "pattern": "[Kk]askade|Org-AGENTS|Vererbung|\\.github"}),
    "004": ("file_exists", {"path": "README.md"}),
    "005": ("file_exists", {"path": "LICENSE"}),
    "006": ("file_exists", {"path": "SECURITY.md"}),
    "007": ("file_exists", {"path": "CHANGELOG.md"}),
    "008": ("file_exists", {"path": ".github/CODEOWNERS"}),
    "009": ("workflow_permissions", {"expect": "permissions-block je workflow"}),
    "010": ("secret_scan", {"pattern": "legacy: siehe Pilot-Objekt CHECK-010"}),
    "011": ("file_pattern", {"pattern": "requirements.txt|poetry.lock|package-lock.json|Cargo.lock|uv.lock"}),
    "012": ("tests_present", {"pattern": "tests?/|test_.*\\.(py|rs|ts)|tools/test_"}),
    "013": ("ci_success", {"expect": "letzter Workflow-Lauf success"}),
    "014": ("content_match", {"path": "README.md", "pattern": "REALITY_STATUS|Status", "note": "MANUAL: Doku-Konsistenz pruefen"}),
    "015": ("version_consistency", {"expect": "Manifest-/Versionsangaben konsistent"}),
    "016": ("git_diff_clean", {"expect": "kein Junk im finalen Diff"}),
    "017": ("file_pattern", {"pattern": "\\.orig$|~$|\\.rej$|debug_.*\\.(log|txt)$", "expect": "0 Treffer"}),
    "018": ("no_destructive", {"expect": "keine destruktiven Operationen ohne Autorisierung"}),
    "019": ("workflow_permissions", {"expect": "least-privilege: kein write-all"}),
    "020": ("schema_valid", {"schema": "agents-md-structure", "note": "Struktur/Schema der AGENTS.md"}),
}

cat = yaml.safe_load(open("ai/checks.yaml"))
os.makedirs("ai/checks", exist_ok=True)
gen, skip = 0, 0
for c in cat["agov_checks"]["checks"]:
    n = c["id"].split("-")[-1]
    out = f"ai/checks/CHECK-{n}.yaml"
    if os.path.exists(out) and "--force" not in sys.argv:
        skip += 1
        continue
    typ, req = TYPES[n]
    obj = {
        "id": f"ATC-CHECK-{n}", "version": "1.0.0", "status": "ACTIVE", "alias": c["id"],
        "metadata": {"name": c["name"].lower().replace(" ", "-").replace("/", "-").replace("(", "").replace(")", "")[:60],
                     "category": "governance" if n in {"001","002","003","020"} else
                                 "security" if n in {"010","018","019"} else "quality",
                     "severity": c["severity"], "level": c["level"], "automation": c["automation"]},
        "scope": {"level": "repository"},
        "requirement": {"type": typ, **req},
        "evaluation": {"pass_when": [{"type": typ, **{k: v for k, v in req.items() if k not in ("note",)}}],
                        "fail_closed": True},
        "result": {"allowed": ["PASS", "FAIL", "WARN", "N/A"]},
        "remediation": {"required_on": ["FAIL"] if c["level"] == "MUST" else ["FAIL", "WARN"],
                         "creates_finding": "on_fail" if c["severity"] in ("P0", "P1") else "always"},
        "evidence": {"required": True, "kind": ["api_response", "file_content"]},
    }
    with open(out, "w") as f:
        f.write("# ATC-CHECK-%s — generiert von tools/gen_check_objects.py (Phase 2, SCR-0063)\n" % n)
        yaml.dump(obj, f, sort_keys=True, allow_unicode=True)
    gen += 1
print(f"CHECK-Objekte: {gen} generiert, {skip} Pilot-Objekte unberuehrt")
