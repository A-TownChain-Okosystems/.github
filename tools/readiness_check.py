#!/usr/bin/env python3
"""ATC Integration & Readiness Control Plane (SCR-0060).

Phase-5-Pivot: keine neuen Standards — vorhandene Governance in messbare
Umsetzungs-/Readiness-Evidenz ueberfuehren. Generiert aus den Registry-SSOTs
(atc-standards) + Live-GitHub-API:

  1. IMPLEMENTATION MATRIX   (standard-implementation.yaml: enforced /
     implemented / specification_only / reference + Coverage-KPI)
  2. INTEGRATION MATRIX       (interfaces.yaml: IFC-0001.. provider/consumers)
  3. SYSTEM READINESS         (releases/milestones/networks + offene P0/P1
     + rote CIs) → TESTNET / RELEASE / PRODUCTION-Gates
  4. MAINTENANCE QUEUE        (offene Dependabot-PRs/Alerts — bewusst von
     Governance getrennt)

Aufruf: python3 tools/readiness_check.py  → docs/READINESS-<date>.md
"""
import os, sys, base64, datetime
from collections import Counter
import requests, yaml

ORG = "A-TownChain-Okosystems"
H = {"Authorization": "Bearer " + os.environ["GITHUB_ACCESS_TOKEN"]}
API = "https://api.github.com"

def get(path):
    return requests.get(API + path, headers=H)

def content(repo, path):
    r = get(f"/repos/{ORG}/{repo}/contents/{path}")
    if r.status_code != 200: return None
    j = r.json()
    return base64.b64decode(j["content"]).decode("utf-8", "replace")

def ry(name):
    return yaml.safe_load(content("atc-standards", f"registry/{name}.yaml"))

# ── 1) IMPLEMENTATION MATRIX ──
si = ry("standard-implementation")
stds = si.get("standards", [])
cls_field = None
for cand in ("classification", "status", "implementation", "evidence_class"):
    if stds and cand in stds[0]: cls_field = cand; break
counts, per_class = Counter(), Counter()
impl_ids = set()
for e in stds:
    raw = (e.get(cls_field) or "?") if cls_field else "?"
    if isinstance(raw, dict):
        c = str(raw.get("status") or raw.get("class") or raw.get("stage") or "?")
    else:
        c = str(raw)
    per_class[c] += 1
    counts["total"] += 1
    if str(c).lower() in ("enforced", "implemented"): impl_ids.add(e.get("standard") or e.get("id"))
kpi = si.get("coverage_kpi", {})
total_reg = 433

# ── 2) INTEGRATION MATRIX ──
ifc = ry("interfaces").get("interfaces", [])
ifc_rows = []
for e in ifc:
    ifc_rows.append((e.get("id"), e.get("title","?")[:44], e.get("provider","?"),
        len(e.get("consumers", [])), str(e.get("compatibility","?"))[:10],
        str(e.get("status") or str(e.get("test_status") or "?"))[:14]))

# ── 3) SYSTEM READINESS ──
mile = ry("milestones").get("milestones", [])
m_acc = [m["id"] for m in mile if m.get("status") == "ACCEPTED"]
rel = ry("releases").get("releases", [])
rel_ver = [r["id"] for r in rel if str(r.get("status")).upper() == "VERIFIED"]
net = ry("networks").get("networks", [])
net_rows = [(n.get("tier"), n.get("network"), n.get("chain_id"), n.get("status")) for n in net]
fnd = ry("findings")
items = fnd.get("findings", fnd if isinstance(fnd, list) else [])
p0 = [e["id"] for e in items if e.get("status") == "OPEN" and e.get("severity") == "P0"]
p1 = [e["id"] for e in items if e.get("status") == "OPEN" and e.get("severity") == "P1"]
# Rote CIs je Repo (letzte Laufe je Workflow) — Stichprobe via AGOV-Logik
repos = ry("repositories").get("repositories", [])
red_ci = []
for r in repos:
    rp = r["name"]
    runs = get(f"/repos/{ORG}/{rp}/actions/runs?per_page=100").json().get("workflow_runs", [])
    latest = {}
    for rr in runs:
        if rr.get("name") not in latest: latest[rr.get("name")] = rr.get("conclusion")
    bad = [k for k, s in latest.items() if s == "failure"]
    if bad: red_ci.append((rp, bad))

# ── 4) MAINTENANCE QUEUE (Dependabot) ──
q = get(f"/search/issues?q=org:{ORG}+type:pr+state:open+author:app/dependabot&per_page=100").json()
dep_prs = [(i["repository_url"].split("/")[-1], i["title"][:60]) for i in q.get("items", [])]
alerts = get(f"/repos/{ORG}/a-townchain-os/dependabot/alerts?state=open").json()
n_alerts = len(alerts) if isinstance(alerts, list) else 0

# ── Gates & Verdict ──
today = datetime.date.today().isoformat()
md = [f"# ATC Integration & Readiness Control Plane — {today} (SCR-0060)", "",
      "Phase-4→5-Pivot: Governance-Evidenz → nachweisbar funktionierende Systeme.", "",
      f"Registry-Scope: {total_reg} Standards · Implementierungs-Registry: {counts['total']} erfasst", ""]

md += ["## 1. IMPLEMENTATION MATRIX (standard-implementation.yaml)", ""]
for c, n in sorted(per_class.items()):
    md.append(f"- **{c}: {n}** Standards ({n / max(counts['total'],1) * 100:.1f} %)")
if kpi: md += ["", f"Coverage-KPI (Registry): `{kpi}`"]
md += ["", f"Ehrlicher Kern: {len(impl_ids)}/{counts['total']} der erfassten Standards sind "
      "enforced/implemented (Code+CI), der Rest Spezifikation.", ""]

md += ["## 2. INTEGRATION MATRIX (interfaces.yaml — IFC-Verträge)", "",
       "| IFC | Titel | Provider | Consumer | Compat | Status |", "|---|---|---|---|---|---|"]
for row in ifc_rows:
    md.append("| " + " | ".join(str(x) for x in row) + " |")
md += [""]

md += ["## 3. SYSTEM READINESS", "",
       f"- Meilensteine ACCEPTED: {', '.join(m_acc) or 'keine'} (ATC-M-003 IN_PROGRESS)",
       f"- Release-Evidenz VERIFIED: {len(rel_ver)} ({', '.join(rel_ver[:4])}…)",
       f"- Offene P0: {len(p0)} · offene P1: {len(p1)} ({', '.join(p1) or '—'})",
       f"- Rote CI-Workflows: {len(red_ci)} Repos ({', '.join(f'{r}({len(b)})' for r, b in red_ci) or 'keine'})", "",
       "| Tier | Netzwerk | Chain-ID | Registry-Status | Gate (ehrlich) |", "|---|---|---|---|---|"]
for tier, nw, cid, st in net_rows:
    gate = "NO-GO" if (p0 or p1 or red_ci) else "PREP"
    md.append(f"| {tier} | {nw} | {cid} | {st} | {gate} — Blocker: offene P1 ({len(p1)}), rote CI ({len(red_ci)}) |" if tier in ("testnet","mainnet") else f"| {tier} | {nw} | {cid} | {st} | {gate} |")
md += [""]

md += ["## 4. MAINTENANCE QUEUE (getrennt von Governance — Owner-Triage)", "",
       f"- Offene Dependabot-PRs: {len(dep_prs)}", f"- Offene Dependabot-Alerts a-townchain-os: {n_alerts} (F-055)", ""]
for rp, t in dep_prs[:12]:
    md.append(f"- [{rp}] {t}")

open("docs/READINESS-" + today + ".md", "w", encoding="utf-8").write("\n".join(md))
print("\n".join(md[:16]))
print(f"\n→ docs/READINESS-{today}.md")
