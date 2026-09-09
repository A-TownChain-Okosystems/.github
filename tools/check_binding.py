#!/usr/bin/env python3
"""ATC Registry-Binding-Checker (SCR-0059): gleicht die Standards-Registry
(atc-standards, SSOT) maschinell gegen alle Agenten-Bindungen (required_standards
je .github/ai/agent.yaml) ab und leitet P0/P1/P2-Luecken ab.

Aufruf: python3 tools/check_binding.py   →  docs/BINDING-<date>.md
Exit:   0 = keine P0/P1-Luecken · 1 = P0/P1 vorhanden
"""
import os, sys, base64, datetime
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
    if isinstance(j, list): return [e["name"] for e in j]
    return base64.b64decode(j["content"]).decode("utf-8", "replace")

def repos():
    out, page = [], 1
    while True:
        j = get(f"/orgs/{ORG}/repos?per_page=100&page={page}").json()
        if not j: break
        out += [x["name"] for x in j if not x.get("archived")]
        page += 1
    return out

# ── Registry laden (SSOT) ──
std = yaml.safe_load(content("atc-standards", "registry/standards.yaml"))["standards"]
reg = {e["id"]: e for e in std}
approved = {k for k, e in reg.items() if e["status"] == "approved"}
draft = {k for k, e in reg.items() if e["status"] == "draft"}
candidate = {k for k, e in reg.items() if e["status"] == "candidate"}

# ── Bindungen je Repo ──
gaps = {"P0": [], "P1": [], "P2": [], "INFO": []}
bound_all = set()
per_repo = {}
for rp in sorted(repos()):
    if rp == "atc-standards":
        ay_path = ".github/ai/agent.yaml"
    elif rp == ".github":
        ay_path = "ai/agent.yaml"
    else:
        ay_path = ".github/ai/agent.yaml"
    raw = content(rp, ay_path)
    if raw is None:
        gaps["P2"].append((rp, "kein .github/ai/agent.yaml — keine Standards-Bindung deklariert"))
        per_repo[rp] = (0, 0)
        continue
    ay = yaml.safe_load(raw)
    req = ay.get("required_standards", []) if isinstance(ay, dict) else []
    dangling = [s for s in req if s not in reg]
    to_draft = [s for s in req if s in draft]
    to_cand = [s for s in req if s in candidate]
    n_ok = len([s for s in req if s in approved])
    if dangling:
        gaps["P1"].append((rp, f"{len(dangling)} Bindung(en) auf nicht existierende Standard-IDs: {', '.join(dangling[:5])}"))
    if to_draft:
        gaps["P1"].append((rp, f"{len(to_draft)} Bindung(en) auf DRAFT-Standard (nicht §9-freigegeben): {', '.join(to_draft[:5])}"))
    if to_cand:
        gaps["P2"].append((rp, f"{len(to_cand)} Bindung(en) auf CANDIDATE-Standards: {', '.join(to_cand[:5])}"))
    if req and n_ok == 0:
        gaps["P1"].append((rp, "Bindung existiert, aber 0 APPROVED-Standards gebunden"))
    bound_all |= set(req)
    per_repo[rp] = (n_ok, len(req))

# ── Org-Deckung ──
unbound = approved - bound_all
if unbound:
    gaps["INFO"].append(("ORG", f"{len(unbound)} APPROVED-Standards nirgends gebunden (z. B. {', '.join(sorted(unbound)[:5])})"))

# ── Report ──
today = datetime.date.today().isoformat()
md = [f"# ATC Registry-Binding-Lücken-Report {today} (SCR-0059)", "",
      f"Registry (SSOT, atc-standards): **{len(reg)} Standards** "
      f"({len(approved)} approved, {len(candidate)} candidate, {len(draft)} draft).",
      f"Abgegleicht: {len(per_repo)} Repos mit/ohne agent.yaml-Bindung.", "",
      f"**P0: {len(gaps['P0'])} · P1: {len(gaps['P1'])} · P2: {len(gaps['P2'])} · INFO: {len(gaps['INFO'])}**", ""]
for lvl in ("P0", "P1", "P2", "INFO"):
    if gaps[lvl]:
        md.append(f"## {lvl}")
        md += [f"- **{rp}**: {det}" for rp, det in gaps[lvl]]
        md.append("")
md += ["## Bindungsquote je Repo (APPROVED / gesamt)", "",
       "| Repo | APPROVED gebunden | gesamt gebunden |", "|---|---|---|"]
md += [f"| {rp} | {a} | {t} |" for rp, (a, t) in sorted(per_repo.items())]
open("docs/BINDING-" + today + ".md", "w", encoding="utf-8").write("\n".join(md))
print(f"P0: {len(gaps['P0'])} · P1: {len(gaps['P1'])} · P2: {len(gaps['P2'])} · INFO: {len(gaps['INFO'])}")
for lvl in ("P0", "P1", "P2", "INFO"):
    for rp, det in gaps[lvl]:
        print(f"  [{lvl}] {rp}: {det[:110]}")
print("Report: docs/BINDING-" + today + ".md")
sys.exit(1 if (gaps["P0"] or gaps["P1"]) else 0)
