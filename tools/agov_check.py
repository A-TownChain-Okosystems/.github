#!/usr/bin/env python3
"""ATC Agent Governance Checker — AGOV-CHECK-001..020 (ai/checks.yaml, SCR-0058).

Fuehrt die AUTO-Checks je Repository via GitHub-API aus und erzeugt
PASS/WARN/FAIL/N/A-Verdicts mit P-Gewichtung. MANUAL-Checks werden als N/A
(dokumentationspflichtig) gefuehrt. Repo-Tiefe: REPO-AUDIT CHECK-001..064.

Aufruf:  python3 tools/agov_check.py            (Org-weit)
         python3 tools/agov_check.py atc-node   (ein Repo)
Exit:    0 = kein blockierender FAIL · 1 = P0/P1-FAIL vorhanden
"""
import os, sys, re, base64, datetime
import requests
import yaml

ORG = "A-TownChain-Okosystems"
H = {"Authorization": "Bearer " + os.environ["GITHUB_ACCESS_TOKEN"]}
API = "https://api.github.com"

def get(path):
    r = requests.get(API + path, headers=H)
    return r

def repos():
    out, page = [], 1
    while True:
        j = get(f"/orgs/{ORG}/repos?per_page=100&page={page}").json()
        if not j: break
        out += [x for x in j if not x.get("archived")]
        page += 1
    return out

def file_content(repo, path):
    r = get(f"/repos/{ORG}/{repo}/contents/{path}")
    if r.status_code != 200: return None
    j = r.json()
    if isinstance(j, list): return [e["name"] for e in j]
    return base64.b64decode(j["content"]).decode("utf-8", "replace")

def tree(repo):
    r = get(f"/repos/{ORG}/{repo}/git/trees/main?recursive=1")
    if r.status_code != 200:
        r = get(f"/repos/{ORG}/{repo}/git/trees/HEAD?recursive=1")
    return r.json().get("tree", []) if r.status_code == 200 else []

SECRET_PAT = [re.compile(p) for p in (
    r"ghp_[A-Za-z0-9]{20,}", r"github_pat_[A-Za-z0-9_]{20,}", r"AKIA[0-9A-Z]{16}",
    r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----", r"\bsk-[A-Za-z0-9]{20,}",
    r"xox[baprs]-[A-Za-z0-9-]{10,}")]

def check_repo(repo):
    v = {}   # AGOV-CHECK-NNN -> (verdict, note)
    tr = tree(repo)
    paths = [t["path"] for t in tr]

    ag = file_content(repo, "AGENTS.md")
    v["001"] = ("PASS", "") if ag else ("FAIL", "AGENTS.md fehlt")
    if ag:
        ok = "ATC Org-weiten Agent-Governance-System" in ag
        v["002"] = ("PASS" if ok else "FAIL", "" if ok else "Org-Verweisblock fehlt")
        ok3 = "Kaskade" in ag and bool(re.search(r"^# ", ag, re.M))
        v["003"] = ("PASS" if ok3 else "FAIL", "" if ok3 else "Kaskade nicht erkennbar")
        v["020"] = ("PASS" if (ok and ok3 and len(ag) > 200) else "WARN", "" if ok else "Struktur dünn")
    else:
        v["002"] = v["003"] = ("FAIL", "kein AGENTS.md"); v["020"] = ("FAIL", "kein AGENTS.md")

    v["004"] = ("PASS" if file_content(repo, "README.md") else ("WARN", "README fehlt"))
    lic = file_content(repo, "LICENSE")
    if lic is None: v["005"] = ("FAIL", "LICENSE fehlt")
    else: v["005"] = ("PASS", "") if "Apache License" in lic[:2000] else ("WARN", "nicht Apache-2.0")
    v["006"] = ("PASS" if file_content(repo, "SECURITY.md") else ("WARN", "SECURITY.md fehlt"))
    v["007"] = ("PASS" if file_content(repo, "CHANGELOG.md") else ("WARN", "CHANGELOG fehlt"))
    v["008"] = ("PASS" if any(p.endswith("CODEOWNERS") for p in paths) else ("N/A", "MAY: nicht vorhanden"))

    wf = file_content(repo, ".github/workflows")
    wf = [f for f in (wf or []) if f.endswith((".yml", ".yaml"))]
    if not wf:
        v["009"] = v["019"] = ("N/A", "keine Workflows")
    else:
        miss, wall = [], []
        for f in wf:
            c = file_content(repo, f".github/workflows/{f}") or ""
            if "permissions:" not in c: miss.append(f)
            if re.search(r"permissions:\s*write-all", c): wall.append(f)
        v["009"] = ("PASS", "") if not miss else ("FAIL", f"ohne permissions-Block: {','.join(miss[:3])}")
        v["019"] = ("PASS", "") if not wall else ("FAIL", f"write-all: {','.join(wall[:3])}")

    # C-010: Secret-Scan (vereinfachter AUTO-Pattern-Scan)
    sus = [p for p in paths if re.search(r"\.env$|\.pem$|\.key$|id_rsa|secret", p, re.I)]
    hits = []
    for p in sus[:15]:
        c = file_content(repo, p)
        if c and any(pat.search(c) for pat in SECRET_PAT): hits.append(p)
    for f in wf:
        c = file_content(repo, f".github/workflows/{f}") or ""
        if any(pat.search(c) for pat in SECRET_PAT): hits.append(f)
    v["010"] = ("FAIL", f"Pattern-Treffer: {hits[:3]}") if hits else ("PASS", "")

    locks = ("Cargo.lock","package-lock.json","yarn.lock","pnpm-lock.yaml","poetry.lock","Pipfile.lock","go.sum")
    v["011"] = ("PASS" if any(p in paths for p in locks) else ("WARN", "kein Lockfile"))
    tests = any(re.search(r"(^|/)tests?/|_test\.|test_.*\.(py|rs)$|\.spec\.|\.test\.", p) for p in paths)
    has_code = any(re.search(r"Cargo\.toml$|package\.json$|pyproject\.toml$|\.py$|\.rs$|\.ts$|\.js$", p) for p in paths)
    if tests: v["012"] = ("PASS", "")
    elif has_code: v["012"] = ("FAIL", "Code-Repo ohne Tests")
    else: v["012"] = ("N/A", "reines Docs-Repo")
    runs = get(f"/repos/{ORG}/{repo}/actions/runs?per_page=100").json().get("workflow_runs", [])
    if not runs: v["013"] = ("N/A", "keine CI-Läufe")
    else:
        latest = {}
        for rr in runs:
            wf = rr.get("name", "?")
            if wf not in latest: latest[wf] = rr.get("conclusion")
        bad = [f"{k}: {s}" for k, s in latest.items() if s == "failure"]
        pending = [k for k, s in latest.items() if s is None]
        if bad: v["013"] = ("FAIL", "; ".join(bad))
        elif pending: v["013"] = ("WARN", f"in Arbeit: {','.join(pending)}")
        else: v["013"] = ("PASS", "")

    v["014"] = v["016"] = v["018"] = ("N/A", "MANUAL — zur Task-Zeit zu führen")
    vers = any(re.search(r"Cargo\.toml$|package\.json$|pyproject\.toml$", p) for p in paths)
    v["015"] = ("PASS" if vers else ("N/A", "kein Code-Build (reines Docs-Repo)"))
    dbg = [p for p in paths if re.search(r"\.DS_Store$|(^|/)target/|(^|/)node_modules/|\.core$|\.log$", p)]
    v["017"] = ("WARN", f"Artefakte: {dbg[:3]}") if dbg else ("PASS", "")
    return v

def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    rl = [only] if only else sorted(r["name"] for r in repos())
    report, blocked = {}, []
    print(f"{'Repo':26s} FAIL WARN N/A  Blocker")
    for rp in rl:
        v = check_repo(rp)
        report[rp] = v
        fails = [k for k, x in v.items() if x[0] == "FAIL"]
        warns = [k for k, x in v.items() if x[0] == "WARN"]
        nas   = [k for k, x in v.items() if x[0] == "N/A"]
        p0p1 = [k for k in fails if k in ("010", "018", "001", "002", "003", "009", "012", "013", "019", "020")]
        if p0p1: blocked.append(rp)
        print(f"{rp:26s} {len(fails):4d} {len(warns):4d} {len(nas):3d}  {'BLOCKIERT' if p0p1 else 'ok'} ({','.join(sorted(fails))})")
    today = datetime.date.today().isoformat()
    md = [f"# ATC AGOV-Check-Lauf vom {today} (SCR-0058)", "",
          "Ausführung: tools/agov_check.py · Katalog: ai/checks.yaml (AGOV-CHECK-001..020)",
          f"**Ergebnis: {len(rl)} Repos geprüft, {len(blocked)} mit blockierenden MUST-FAILs.**", "",
          "| Repo | FAIL-Checks | WARN-Checks | Blockiert |", "|---|---|---|---|"]
    for rp, v in sorted(report.items()):
        f_ = ", ".join(sorted(k for k, x in v.items() if x[0] == "FAIL")) or "—"
        w_ = ", ".join(sorted(k for k, x in v.items() if x[0] == "WARN")) or "—"
        md.append(f"| {rp} | {f_} | {w_} | {'JA' if rp in blocked else 'nein'} |")
    md += ["", "## Details", ""]
    for rp, v in sorted(report.items()):
        md.append(f"### {rp}")
        for k in sorted(v):
            md.append(f"- AGOV-CHECK-{k}: {v[k][0]}{' — ' + v[k][1] if v[k][1] else ''}")
        md.append("")
    open("docs/AGOV-RUN-" + today + ".md", "w", encoding="utf-8").write("\n".join(md))
    print("\nReport: docs/AGOV-RUN-" + today + ".md | blockiert:", blocked or "keine")
    sys.exit(1 if blocked else 0)

if __name__ == "__main__":
    main()
