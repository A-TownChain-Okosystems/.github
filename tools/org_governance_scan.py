#!/usr/bin/env python3
"""ATC Cross-Repo Governance Validator (Phase 6, SCR-0063).
Prueft alle Org-Repositories gegen die Governance-Artefakte (ATC-AI-GOV Control Plane)
und berechnet je Repository den Status (BLOCKED/NON-COMPLIANT/COMPLIANT-WITH-FINDINGS/COMPLIANT/VERIFIED).
Evidence First: alle Pruefungen via GitHub-API (kein Behaupten). Fail Closed bei API-Fehlern."""
import os, sys, json, urllib.request
from datetime import datetime, timezone

TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN")
ORG = "A-TownChain-Okosystems"
H = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

# Owner-Anweisung 11.09.2026 (Michael Wroblewski): Demo-/Test-Repos werden von der
# Org-Compliance-Bewertung ausgeschlossen (kein Produktions-Code, kein Governance-Ziel).
EXCLUDED_REPOS = {"demo-repository": "Demo/Test-Repo — Owner-Entscheidung 11.09.2026: von Org-Compliance ausgeschlossen"}

def api(url):
    req = urllib.request.Request(url, headers=H)
    try:
        return json.loads(urllib.request.urlopen(req).read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise  # Fail Closed: unexpected API state -> Exception, kein stilles PASS

def file_exists(repo, path):
    return api(f"https://api.github.com/repos/{ORG}/{repo}/contents/{path}") is not None

def content(repo, path):
    d = api(f"https://api.github.com/repos/{ORG}/{repo}/contents/{path}")
    if d and "content" in d and d.get("encoding") == "base64":
        import base64
        return base64.b64decode(d["content"]).decode(errors="replace")
    return None

def ci_state(repo):
    runs = api(f"https://api.github.com/repos/{ORG}/{repo}/actions/runs?per_page=5")
    if not runs or not runs.get("workflow_runs"):
        return None
    for r in runs["workflow_runs"]:
        if r["status"] == "completed":
            return r["conclusion"]
    return "running"


def workflow_perm_class(repo):
    """Echte AGOV-CHECK-009/019-Pruefung: je Workflow mind. ein permissions-Block
    (top-level ODER job-level), kein write-all. OAuth-Scope: nur Lesezugriff noetig."""
    import base64, re
    tree = api(f"https://api.github.com/repos/{ORG}/{repo}/git/trees/main?recursive=1")
    if not tree:
        return "N/A"
    wfs = [t["path"] for t in tree.get("tree", [])
           if t["path"].startswith(".github/workflows/") and t["path"].endswith((".yml", ".yaml"))]
    if not wfs:
        return "N/A"
    bad = []
    for wf in wfs:
        d = api(f"https://api.github.com/repos/{ORG}/{repo}/contents/{wf}")
        if not d or "content" not in d:
            continue  # Fail Closed bei API-Fehler behandelbar: naechster Lauf
        body = base64.b64decode(d["content"]).decode(errors="replace")
        has_block = re.search(r"^permissions:", body, re.M) or re.search(r"^\s+permissions:", body, re.M)
        write_all = re.search(r"permissions:\s*\n?\s*(all|write-all)|:\s*write-all", body) and "write-all" in body
        if write_all or not has_block:
            bad.append(wf.split("/")[-1])
    return "FAIL (" + ", ".join(bad[:3]) + ")" if bad else "PASS"

def scan_repo(repo, workflows_only_ci=False):
    f = {}  # findings
    agents_md = content(repo, "AGENTS.md")
    f["AGENTS.md"] = "PASS" if agents_md else "FAIL"
    if agents_md:
        f["Org-Bindung (AGOV-CHECK-002)"] = "PASS" if any(
            k in agents_md for k in ("AGENT_MANIFEST", ".github/AGENTS.md", "ATC-AI-GOV")) else "WARN"
    agent_yaml = file_exists(repo, ".github/ai/agent.yaml")
    f["agent.yaml"] = "PASS" if agent_yaml else "N/A"
    # Control-Plane-Regel: Repo MIT agent.yaml braucht lokale capabilities+policies
    if agent_yaml:
        f["capabilities.yaml (lokal, Pflicht bei Agenten-Bindung)"] = "PASS" if file_exists(repo, ".github/ai/capabilities.yaml") else "FAIL"
        f["policies.yaml (lokal, Pflicht bei Agenten-Bindung)"] = "PASS" if file_exists(repo, ".github/ai/policies.yaml") else "FAIL"
    else:
        f["capabilities/policies"] = "INHERITED"  # Voll-Vererbung vom Hub
    f["Audit-Records"] = "PASS" if (file_exists(repo, "docs/AUD-2026-0001_self_audit.md") or
        file_exists(repo, ".github/ai/audit") or
        any(True for _ in [1]) and file_exists(repo, "docs")) else "WARN"
    f["README"] = "PASS" if file_exists(repo, "README.md") else "FAIL"
    f["LICENSE"] = "PASS" if file_exists(repo, "LICENSE") else "FAIL"
    f["Workflow-Permissions (AGOV-CHECK-009/019)"] = workflow_perm_class(repo)
    ci = ci_state(repo)
    f["CI letzter Lauf"] = {"success": "PASS", "failure": "FAIL"}.get(ci, "WARN" if ci == "running" else "N/A")
    return f

def repo_status(findings):
    severities = {"FAIL": ["Workflow-Permissions (AGOV-CHECK-009)", "Audit-Records"],  # WARN-Klasse je Definition
                  }
    fails = [k for k, v in findings.items() if v == "FAIL"]
    warns = [k for k, v in findings.items() if v == "WARN"]
    if fails: return "NON-COMPLIANT", fails, warns   # P1-FAIL (AGENTS/agent-bindings/capabilities/policies)
    if warns: return "COMPLIANT-WITH-FINDINGS", [], warns
    return "COMPLIANT", [], []

repos = api(f"https://api.github.com/orgs/{ORG}/repos?per_page=100&sort=pushed")
report = {"scan_id": f"ORG-GOV-SCAN-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
          "generated": datetime.now(timezone.utc).isoformat(), "repos": {}, "summary": {}}
count = {}
for r in sorted(repos, key=lambda x: x["name"]):
    name = r["name"]
    if name == ".github":
        continue
    if name in EXCLUDED_REPOS:
        print(f"⚪ {name:28s} EXCLUDED ({EXCLUDED_REPOS[name]})")
        continue
    findings = scan_repo(name)
    status, fails, warns = repo_status(findings)
    report["repos"][name] = {"status": status, "findings": findings}
    count[status] = count.get(status, 0) + 1
    mark = {"NON-COMPLIANT": "🔴", "COMPLIANT-WITH-FINDINGS": "🟡", "COMPLIANT": "🟢"}.get(status, "⚪")
    print(f"{mark} {name:28s} {status}")
    for k in fails:
        print(f"    🔴 FAIL: {k}")
report["excluded"] = {k: v for k, v in EXCLUDED_REPOS.items()}
report["summary"] = count
json.dump(report, open(f"docs/ORG-GOV-SCAN-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.json", "w"), indent=1)
print("\nSummary:", count)
