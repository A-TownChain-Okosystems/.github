#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATC Org-Compliance-Scan (SCR-0074/0075, F-091) — wiederverwendbares Tool.

Prüft JEDES Produkt-Repo der Organisation gegen die Repository-Pflichtstandards
(ATC-STD-201) — 100 % API-getrieben (GitHub-Tarballs, keine lokalen Klone nötig):

  MUST-Artefakte   .atc/ x4, AGENTS.md, AGENT_MANIFEST.md, CODEOWNERS,
                   SECURITY.md, STATUS.md, CHANGELOG.md, README.md
  Governance-CI   .github/workflows/ vorhanden
  Compliance-Badge  "ATC COMPLIANCE"-Zeile im README
  Lizenz           LICENSE=Apache-2.0; keine proprietary/ARR/UNLICENSED-Reste
                   in README, .atc/, Cargo.toml, package.json (inkl. Subtrees)
  Claim-Ehrlichkeit  kein Build/Tests-PASS-Claim ohne Implementierungsdateien
  Spec-Abdeckung   docs/specs/ oder specs/ vorhanden (Doku-Repos: EXEMPT)

Nutzung:
  GITHUB_ACCESS_TOKEN=... python3 tools/org_compliance_scan.py \
      [--org A-TownChain-Okosystems] [--output docs/compliance] [--strict]

  --strict   Exit-Code 1 bei Findings (für CI-Gates)
Exit-Code: 0 (oder 1 mit --strict). Report: JSON + Markdown + Konsolen-Tabelle.
Kopplung: läuft wöchentlich via .github/workflows/org-compliance-scan.yml UND
ist Pflicht-Bestandteil jedes SCR-Abschlusses (Agent-Koordination, Hub-AGENTS.md).
"""
import argparse, io, json, os, re, sys, tarfile, tempfile
import requests
from datetime import datetime, timezone

ORG_DEFAULT = "A-TownChain-Okosystems"
API = "https://api.github.com"

MUST = [".atc/repository.yaml", ".atc/compliance.yaml", ".atc/lifecycle.yaml",
        ".atc/ownership.yaml", "AGENTS.md", "AGENT_MANIFEST.md", "CODEOWNERS",
        "SECURITY.md", "STATUS.md", "CHANGELOG.md", "README.md"]

# Spec-Check-Klasse: Doku-/Standards-Repos tragen ihre Spec-Last anderswo.
EXEMPT_SPECS = {"atc-standards": "Standards-SSOT (normative standards/)",
                "a-townchain-os-docs": "Docs-Hub (kanonische Doku-Struktur)",
                ".github": "Governance-Hub (eigenes Regime)",
                "demo-repository": "ungoverned (F-059, Owner-Entscheidung offen)"}

BADGE = re.compile(r"ATC[\s-]*COMPLIANCE", re.I)
LIZBAD = re.compile(r"proprietary|all\s+rights\s+reserved|UNLICENSED", re.I)
PASSCLAIM = re.compile(r"passing|tests?\s*[:=]?\s*pass\b", re.I)
IMPL_END = (".rs", ".py", ".ts", ".tsx", ".js", ".go", ".c", ".cpp")
SKIP_PATH = re.compile(r"(^|/)(\.git|archive|archives|node_modules|target|dist|build|docs/archive|monorepo-legacy)(/|$)")

def gh(path, token, stream=False):
    r = requests.get(API + path, headers={"Authorization": f"Bearer {token}"},
                     timeout=60, stream=stream)
    if r.status_code != 200:
        raise RuntimeError(f"API {path} -> {r.status_code}")
    return r

def list_repos(org, token):
    repos, page = [], 1
    while True:
        d = gh(f"/orgs/{org}/repos?per_page=100&page={page}", token).json()
        repos += d
        if len(d) < 100:
            break
        page += 1
    return [r for r in repos if not r.get("archived") and not r.get("fork")]

def fetch_tree(repo, token):
    """Repo-Tarball herunterladen, in Temp-Dir entpacken, Root-Pfad zurückgeben."""
    data = gh(f"/repos/{repo['full_name']}/tarball/{repo['default_branch']}", token, stream=True)
    buf = io.BytesIO()
    for chunk in data.iter_content(65536):
        buf.write(chunk)
    buf.seek(0)
    tmp = tempfile.mkdtemp(prefix="atcscan_")
    with tarfile.open(fileobj=buf, mode="r:gz") as tf:
        names = tf.getnames()
        root = os.path.commonpath([n for n in names if n]) + "/"
        # SCR-0092: robuste Extraktion — absolute Symlinks (z.B. venv-bin/python3)
        # ueberspringen statt den Scan abbrechen zu lassen (tarfile.AbsoluteLinkError).
        import warnings as _w
        skipped = 0
        for _m in tf.getmembers():
            if _m.issym() and (_m.linkname.startswith("/") or _m.linkname.startswith("\\") or _m.name.startswith("/")):
                skipped += 1
                continue
            try:
                tf.extract(_m, tmp, filter="data")
            except (tarfile.AbsoluteLinkError, tarfile.OutsideDestinationError, OSError):
                skipped += 1
        if skipped:
            print(f"  Hinweis: {skipped} Tarball-Mitglieder (Symlinks/unsicher) uebersprungen")
    return os.path.join(tmp, root.rstrip("/"))

def read(root, rel):
    p = os.path.join(root, rel)
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return None

def walk_files(root):
    out = []
    for d, _, fs in os.walk(root):
        rel = os.path.relpath(d, root)
        if SKIP_PATH.search(rel):
            continue
        for f in fs:
            out.append(os.path.normpath(os.path.join(rel, f)))
    return out

def check_repo(repo, token):
    name = repo["name"]
    res = {"repo": name, "verdict": "COMPLIANT", "findings": []}
    tree = fetch_tree(repo, token)
    try:
        files = walk_files(tree)
        res["files"] = len(files)
        # 1) MUST-Artefakte
        missing = [m for m in MUST if m not in files]
        res["must_ok"] = len(MUST) - len(missing)
        if missing:
            res["findings"].append(f"MUST-Artefakte fehlen: {', '.join(missing)}")
        # 2) Governance-CI
        res["gov_ci"] = any(f.startswith(".github/workflows/") for f in files)
        if not res["gov_ci"]:
            res["findings"].append("Governance-CI fehlt (.github/workflows/ leer)")
        # 3) Compliance-Badge
        res["badge"] = bool(BADGE.search(read(tree, "README.md") or ""))
        if not res["badge"]:
            res["findings"].append("Compliance-Badge 'ATC COMPLIANCE' fehlt im README")
        # 4) Lizenz-Konsistenz
        lic = read(tree, "LICENSE") or ""
        res["license"] = "OK" if "Apache" in lic else "FEHLT/Abweichend"
        if "Apache" not in lic:
            res["findings"].append("LICENSE enthaelt keinen Apache-2.0-Text")
        bad = []
        for f in files:
            if f.startswith("licenses/"):
                continue  # ATC-LICENSE-Registry: beschreibt Lizenz-TYPEN (inkl. PROPRIETARY-005), keine Lizenz-Zuordnung
            base = os.path.basename(f)
            if (base in ("README.md",) or f.startswith(".atc/") or base in ("Cargo.toml", "package.json")):
                txt = read(tree, f)
                if txt and LIZBAD.search(txt):
                    bad.append(f)
        if bad:
            res["license_files_bad"] = bad
            res["findings"].append(f"Lizenz-Reste (proprietary/ARR/UNLICENSED): {', '.join(bad[:5])}")
        # 5) Claim-Ehrlichkeit: PASS-Claim ohne Implementierung?
        impl = [f for f in files if f.endswith(IMPL_END) or os.path.basename(f) in ("Cargo.toml", "package.json", "setup.py", "pyproject.toml")]
        status = read(tree, "STATUS.md") or ""
        res["has_impl"] = bool(impl)
        if not impl and status and PASSCLAIM.search(status):
            res["findings"].append("Unbelegter Build/Tests-PASS-Claim in STATUS.md ohne Implementierungsdateien")
        # 6) Spec-Abdeckung
        specs = [f for f in files if f.startswith(("docs/specs/", "specs/"))]
        if name in EXEMPT_SPECS:
            res["specs"] = "EXEMPT"
        else:
            res["specs"] = bool(specs)
            if not specs:
                res["findings"].append("Keine Spezifikationen (docs/specs/ oder specs/)")
        if res["findings"]:
            res["verdict"] = "FINDINGS"
        return res
    finally:
        import shutil
        shutil.rmtree(tree.rsplit(os.sep, 1)[0], ignore_errors=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--org", default=ORG_DEFAULT)
    ap.add_argument("--output", default="docs/compliance")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    token = os.environ.get("GITHUB_ACCESS_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("Kein Token: GITHUB_ACCESS_TOKEN setzen")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    repos = sorted(list_repos(args.org, token), key=lambda r: r["name"])
    results, exempt = [], []
    for r in repos:
        if r["name"] in EXEMPT_SPECS and r["name"] != "atc-standards":
            exempt.append({"repo": r["name"], "grund": EXEMPT_SPECS[r["name"]]})
            continue
        res = check_repo(r, token)
        results.append(res)
        print(f"{res['repo']:24s} {res['verdict']:9s} MUST {res.get('must_ok', 0)}/11 "
              f"CI={res.get('gov_ci')} Badge={res.get('badge')} "
              f"Liz={res.get('license')} Impl={res.get('has_impl')} Specs={res.get('specs')}")
    bad = [x for x in results if x["verdict"] == "FINDINGS"]
    summary = {"org": args.org, "generated": now, "repos_checked": len(results),
               "compliant": len(results) - len(bad), "findings": len(bad), "exempt": exempt}
    report = {"summary": summary, "results": results}
    os.makedirs(args.output, exist_ok=True)
    jpath = os.path.join(args.output, f"ORG-COMPLIANCE-SCAN-{now}.json")
    json.dump(report, open(jpath, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    mpath = os.path.join(args.output, f"ORG-COMPLIANCE-SCAN-{now}.md")
    with open(mpath, "w", encoding="utf-8") as m:
        m.write(f"# ATC Org-Compliance-Scan — {now}\n\n")
        m.write(f"Generiert von `tools/org_compliance_scan.py` (SCR-0075, F-091). "
                f"**{summary['compliant']}/{summary['repos_checked']} konform, {len(bad)} mit Findings.**\n\n")
        m.write("| Repo | Verdict | MUST | CI | Badge | Lizenz | Impl | Specs |\n|---|---|---|---|---|---|---|---|\n")
        for x in results:
            m.write(f"| {x['repo']} | {x['verdict']} | {x.get('must_ok', 0)}/11 | "
                    f"{res_str(x.get('gov_ci'))} | {res_str(x.get('badge'))} | {x.get('license')} | "
                    f"{res_str(x.get('has_impl'))} | {x.get('specs')} |\n")
        if bad:
            m.write("\n## Findings\n\n")
            for x in bad:
                m.write(f"### {x['repo']}\n" + "\n".join(f"- {f}" for f in x["findings"]) + "\n")
    print(f"\nReport: {jpath}\n         {mpath}")
    print(f"Bilanz: {summary['compliant']}/{summary['repos_checked']} COMPLIANT, {len(bad)} FINDINGS")
    if bad and args.strict:
        sys.exit(1)

def res_str(v):
    return "OK" if v else "FAIL" if v is False else str(v)

if __name__ == "__main__":
    main()
