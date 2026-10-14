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

import base64
import datetime
import json
import os
import re
from collections import Counter

import requests
import yaml

try:
    from tools.readiness_contract import (
        collect_pages,
        response_json,
        select_runs_for_sha,
        validate_registry_counts,
    )
except ModuleNotFoundError:
    # Support the documented direct invocation: python3 tools/readiness_check.py
    from readiness_contract import (
        collect_pages,
        response_json,
        select_runs_for_sha,
        validate_registry_counts,
    )

ORG = "A-TownChain-Okosystems"
H = {"Authorization": "Bearer " + os.environ["GITHUB_ACCESS_TOKEN"]}
API = "https://api.github.com"


def get(path):
    return requests.get(API + path, headers=H, timeout=30)


def content(repo, path):
    response = get(f"/repos/{ORG}/{repo}/contents/{path}")
    payload = response_json(response, f"contents {repo}/{path}")
    encoded = payload.get("content")
    if not isinstance(encoded, str) or payload.get("encoding") != "base64":
        raise RuntimeError(f"contents {repo}/{path}: missing base64 content")
    try:
        return base64.b64decode(encoded, validate=True).decode("utf-8")
    except Exception as exc:
        raise RuntimeError(f"contents {repo}/{path}: invalid base64 or UTF-8") from exc


def ry(name):
    raw = yaml.safe_load(content("atc-standards", f"registry/{name}.yaml"))
    if not isinstance(raw, dict):
        raise RuntimeError(f"registry/{name}.yaml: expected a YAML object")
    return raw


# ── 1) IMPLEMENTATION MATRIX ──
si = ry("standard-implementation")
standards_registry = ry("standards")
registry_counts = validate_registry_counts(standards_registry, si)
stds = si.get("standards", [])
cls_field = None
for cand in ("classification", "status", "implementation", "evidence_class"):
    if stds and cand in stds[0]:
        cls_field = cand
        break
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
    if str(c).lower() in ("enforced", "implemented"):
        impl_ids.add(e.get("standard") or e.get("id"))
kpi = si.get("coverage_kpi", {})
total_reg = registry_counts["registry_total"]

# ── 2) INTEGRATION MATRIX ──
ifc = ry("interfaces").get("interfaces", [])
ifc_rows = []
for e in ifc:
    ifc_rows.append(
        (
            e.get("id"),
            e.get("title", "?")[:44],
            e.get("provider", "?"),
            len(e.get("consumers", [])),
            str(e.get("compatibility", "?"))[:10],
            str(e.get("status") or str(e.get("test_status") or "?"))[:14],
        )
    )

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
ci_unverified = []
for r in repos:
    rp = r["name"]
    repo_meta = response_json(get(f"/repos/{ORG}/{rp}"), f"repository metadata {rp}")
    default_branch = repo_meta.get("default_branch")
    if not isinstance(default_branch, str) or not default_branch:
        raise RuntimeError(f"repository metadata {rp}: missing default_branch")
    branch_data = response_json(
        get(f"/repos/{ORG}/{rp}/branches/{default_branch}"),
        f"default branch {rp}/{default_branch}",
    )
    expected_sha = (branch_data.get("commit") or {}).get("sha")
    if not isinstance(expected_sha, str) or len(expected_sha) != 40:
        raise RuntimeError(f"default branch {rp}/{default_branch}: missing exact commit SHA")
    all_runs = collect_pages(
        lambda page: get(
            f"/repos/{ORG}/{rp}/actions/runs?branch={default_branch}&per_page=100&page={page}"
        ),
        key="workflow_runs",
        context=f"workflow runs {rp}",
    )
    runs = select_runs_for_sha(all_runs, expected_sha)
    if not runs:
        ci_unverified.append((rp, expected_sha))
        continue
    latest = {}
    for rr in runs:
        if rr.get("name") and rr.get("name") not in latest:
            latest[rr["name"]] = rr.get("conclusion")
    bad = [k for k, state in latest.items() if state == "failure"]
    if bad:
        red_ci.append((rp, bad))

# ── 4) MAINTENANCE QUEUE (Dependabot) ──
dep_items = collect_pages(
    lambda page: get(
        f"/search/issues?q=org:{ORG}+type:pr+state:open+author:app/dependabot&per_page=100&page={page}"
    ),
    key="items",
    context="Dependabot PR search",
)
dep_prs = [
    (item["repository_url"].split("/")[-1], item["title"][:60])
    for item in dep_items
    if isinstance(item.get("repository_url"), str) and isinstance(item.get("title"), str)
]
alerts = collect_pages(
    lambda page: get(
        f"/repos/{ORG}/a-townchain-os/dependabot/alerts?state=open&per_page=100&page={page}"
    ),
    key=None,
    context="Dependabot alerts a-townchain-os",
)
n_alerts = len(alerts)

# ── Gates & Verdict ──
today = datetime.date.today().isoformat()
md = [
    f"# ATC Integration & Readiness Control Plane — {today} (SCR-0060)",
    "",
    "Phase-4→5-Pivot: Governance-Evidenz → nachweisbar funktionierende Systeme.",
    "",
    f"Registry-Scope: {total_reg} Standards · Implementierungs-Registry: {counts['total']} erfasst",
    "",
]

md += ["## 1. IMPLEMENTATION MATRIX (standard-implementation.yaml)", ""]
for c, n in sorted(per_class.items()):
    md.append(f"- **{c}: {n}** Standards ({n / max(counts['total'], 1) * 100:.1f} %)")
if kpi:
    md += ["", f"Coverage-KPI (Registry): `{kpi}`"]
md += [
    "",
    f"Ehrlicher Kern: {len(impl_ids)}/{counts['total']} der erfassten Standards sind "
    "enforced/implemented (Code+CI), der Rest Spezifikation.",
    "",
]

md += [
    "## 2. INTEGRATION MATRIX (interfaces.yaml — IFC-Verträge)",
    "",
    "| IFC | Titel | Provider | Consumer | Compat | Status |",
    "|---|---|---|---|---|---|",
]
for row in ifc_rows:
    md.append("| " + " | ".join(str(x) for x in row) + " |")
md += [""]

md += [
    "## 3. SYSTEM READINESS",
    "",
    f"- Meilensteine ACCEPTED: {', '.join(m_acc) or 'keine'} (ATC-M-003 IN_PROGRESS)",
    f"- Release-Evidenz VERIFIED: {len(rel_ver)} ({', '.join(rel_ver[:4])}…)",
    f"- Offene P0: {len(p0)} · offene P1: {len(p1)} ({', '.join(p1) or '—'})",
    f"- Rote CI-Workflows: {len(red_ci)} Repos ({', '.join(f'{r}({len(b)})' for r, b in red_ci) or 'keine'})",
    f"- CI-Evidenz ohne passenden aktuellen Default-Branch-SHA: {len(ci_unverified)} Repos ({', '.join(r for r, _ in ci_unverified) or 'keine'})",
    "",
    "| Tier | Netzwerk | Chain-ID | Registry-Status | Gate (ehrlich) |",
    "|---|---|---|---|---|",
]
for tier, nw, cid, st in net_rows:
    gate = "NO-GO" if (p0 or p1 or red_ci or ci_unverified) else "PREP"
    md.append(
        f"| {tier} | {nw} | {cid} | {st} | {gate} — Blocker: offene P0/P1 ({len(p0)}/{len(p1)}), rote CI ({len(red_ci)}), CI-Evidenz fehlt ({len(ci_unverified)}) |"
        if tier in ("testnet", "mainnet")
        else f"| {tier} | {nw} | {cid} | {st} | {gate} |"
    )
md += [""]

md += [
    "## 4. MAINTENANCE QUEUE (getrennt von Governance — Owner-Triage)",
    "",
    f"- Offene Dependabot-PRs: {len(dep_prs)}",
    f"- Offene Dependabot-Alerts a-townchain-os: {n_alerts} (F-055)",
    "",
]
for rp, t in dep_prs[:12]:
    md.append(f"- [{rp}] {t}")

open("docs/READINESS-" + today + ".md", "w", encoding="utf-8").write("\n".join(md))
print("\n".join(md[:16]))
print(f"\n→ docs/READINESS-{today}.md")

# Optional machine-readable producer output. Workflow metadata is required; do
# not fabricate a source SHA when running outside GitHub Actions.
evidence_output = os.environ.get("ATC_EVIDENCE_JSON")
if evidence_output:
    source_sha = os.environ.get("GITHUB_SHA", "")
    source_repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not re.fullmatch(r"[0-9a-f]{40}", source_sha):
        raise RuntimeError("ATC_EVIDENCE_JSON requires a full lowercase GITHUB_SHA")
    if not re.fullmatch(r"[^/\\s]+/[^/\\s]+", source_repo):
        raise RuntimeError("ATC_EVIDENCE_JSON requires GITHUB_REPOSITORY in owner/name form")
    readiness_status = "NO-GO" if (p0 or p1 or red_ci or ci_unverified) else "PREP"
    payload = {
        "schema_version": 1,
        "producer": "readiness",
        "status": readiness_status,
        "repository": source_repo,
        "source_commit_sha": source_sha,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "summary": {
            "open_p0": len(p0),
            "open_p1": len(p1),
            "repositories_with_red_ci": len(red_ci),
            "repositories_without_exact_sha_ci_evidence": len(ci_unverified),
        },
        "evidence": [],
        "evidence_note": "Workflow run/job/step/log evidence must be attached by the independent live verifier.",
    }
    with open(evidence_output, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, sort_keys=True, indent=2)
        handle.write("\n")
    print(f"\nMachine-readable readiness claim: {evidence_output} ({readiness_status})")
