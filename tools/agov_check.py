#!/usr/bin/env python3
"""ATC Agent Governance Checker — AGOV-CHECK-001..020 (SCR-0058).

Runs organization-wide or per-repository checks and emits PASS/WARN/FAIL/N/A
verdict tuples. Exit 1 is reserved for blocking P0/P1 findings.
"""

import base64
import datetime
import os
import re
import sys

import requests

ORG = "A-TownChain-Okosystems"
API = "https://api.github.com"


def headers():
    token = os.environ.get("GITHUB_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_ACCESS_TOKEN is required")
    return {"Authorization": "Bearer " + token}


def get(path):
    return requests.get(API + path, headers=headers(), timeout=30)


def verdict(status, note=""):
    return (status, note)


def repos():
    out, page = [], 1
    while True:
        response = get(f"/orgs/{ORG}/repos?per_page=100&page={page}")
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break
        out += [repo for repo in batch if not repo.get("archived")]
        page += 1
    return out


def file_content(repo, path):
    response = get(f"/repos/{ORG}/{repo}/contents/{path}")
    if response.status_code != 200:
        return None
    data = response.json()
    if isinstance(data, list):
        return [entry["name"] for entry in data]
    return base64.b64decode(data["content"]).decode("utf-8", "replace")


def tree(repo):
    response = get(f"/repos/{ORG}/{repo}/git/trees/main?recursive=1")
    if response.status_code != 200:
        response = get(f"/repos/{ORG}/{repo}/git/trees/HEAD?recursive=1")
    if response.status_code != 200:
        return []
    return response.json().get("tree", [])


SECRET_PAT = [
    re.compile(pattern)
    for pattern in (
        r"ghp_[A-Za-z0-9]{20,}",
        r"github_pat_[A-Za-z0-9_]{20,}",
        r"AKIA[0-9A-Z]{16}",
        r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",
        r"\bsk-[A-Za-z0-9]{20,}",
        r"xox[baprs]-[A-Za-z0-9-]{10,}",
    )
]


def check_repo(repo):
    findings = {}
    paths = [entry["path"] for entry in tree(repo)]

    agents = file_content(repo, "AGENTS.md")
    findings["001"] = verdict("PASS") if agents else verdict("FAIL", "AGENTS.md fehlt")
    if agents:
        org_ref = "ATC Org-weiten Agent-Governance-System" in agents
        cascade = "Kaskade" in agents and bool(re.search(r"^# ", agents, re.MULTILINE))
        findings["002"] = verdict("PASS") if org_ref else verdict("FAIL", "Org-Verweisblock fehlt")
        findings["003"] = verdict("PASS") if cascade else verdict("FAIL", "Kaskade nicht erkennbar")
        findings["020"] = verdict("PASS") if org_ref and cascade and len(agents) > 200 else verdict("WARN", "Struktur dünn")
    else:
        findings["002"] = verdict("FAIL", "kein AGENTS.md")
        findings["003"] = verdict("FAIL", "kein AGENTS.md")
        findings["020"] = verdict("FAIL", "kein AGENTS.md")

    findings["004"] = verdict("PASS") if file_content(repo, "README.md") else verdict("WARN", "README fehlt")

    license_text = file_content(repo, "LICENSE")
    if license_text is None:
        findings["005"] = verdict("FAIL", "LICENSE fehlt")
    else:
        findings["005"] = verdict("PASS") if "Apache License" in license_text[:2000] else verdict("WARN", "nicht Apache-2.0")

    findings["006"] = verdict("PASS") if file_content(repo, "SECURITY.md") else verdict("WARN", "SECURITY.md fehlt")
    findings["007"] = verdict("PASS") if file_content(repo, "CHANGELOG.md") else verdict("WARN", "CHANGELOG fehlt")
    findings["008"] = verdict("PASS") if any(path.endswith("CODEOWNERS") for path in paths) else verdict("N/A", "MAY: nicht vorhanden")

    workflows = file_content(repo, ".github/workflows") or []
    workflows = [name for name in workflows if name.endswith((".yml", ".yaml"))]
    if not workflows:
        findings["009"] = verdict("N/A", "keine Workflows")
        findings["019"] = verdict("N/A", "keine Workflows")
    else:
        missing_permissions, write_all = [], []
        for name in workflows:
            content = file_content(repo, f".github/workflows/{name}") or ""
            if "permissions:" not in content:
                missing_permissions.append(name)
            if re.search(r"permissions:\s*write-all", content):
                write_all.append(name)
        findings["009"] = verdict("PASS") if not missing_permissions else verdict("FAIL", f"ohne permissions-Block: {','.join(missing_permissions[:3])}")
        findings["019"] = verdict("PASS") if not write_all else verdict("FAIL", f"write-all: {','.join(write_all[:3])}")

    suspicious_paths = [path for path in paths if re.search(r"\.env$|\.pem$|\.key$|id_rsa|secret", path, re.IGNORECASE)]
    secret_hits = []
    for path in suspicious_paths[:15]:
        content = file_content(repo, path)
        if content and any(pattern.search(content) for pattern in SECRET_PAT):
            secret_hits.append(path)
    for name in workflows:
        content = file_content(repo, f".github/workflows/{name}") or ""
        if any(pattern.search(content) for pattern in SECRET_PAT):
            secret_hits.append(name)
    findings["010"] = verdict("FAIL", f"Pattern-Treffer: {secret_hits[:3]}") if secret_hits else verdict("PASS")

    lockfiles = {"Cargo.lock", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Pipfile.lock", "go.sum"}
    findings["011"] = verdict("PASS") if lockfiles.intersection(paths) else verdict("WARN", "kein Lockfile")

    has_tests = any(re.search(r"(^|/)tests?/|_test\.|test_.*\.(py|rs)$|\.spec\.|\.test\.", path) for path in paths)
    has_code = any(re.search(r"Cargo\.toml$|package\.json$|pyproject\.toml$|\.py$|\.rs$|\.ts$|\.js$", path) for path in paths)
    if has_tests:
        findings["012"] = verdict("PASS")
    elif has_code:
        findings["012"] = verdict("FAIL", "Code-Repo ohne Tests")
    else:
        findings["012"] = verdict("N/A", "reines Docs-Repo")

    runs_response = get(f"/repos/{ORG}/{repo}/actions/runs?per_page=100")
    runs_response.raise_for_status()
    runs = runs_response.json().get("workflow_runs", [])
    if not runs:
        findings["013"] = verdict("N/A", "keine CI-Läufe")
    else:
        latest = {}
        for run in runs:
            workflow_name = run.get("name", "?")
            latest.setdefault(workflow_name, run.get("conclusion"))
        failures = [f"{name}: {state}" for name, state in latest.items() if state == "failure"]
        pending = [name for name, state in latest.items() if state is None]
        if failures:
            findings["013"] = verdict("FAIL", "; ".join(failures))
        elif pending:
            findings["013"] = verdict("WARN", f"in Arbeit: {','.join(pending)}")
        else:
            findings["013"] = verdict("PASS")

    findings["014"] = verdict("N/A", "MANUAL — zur Task-Zeit zu führen")
    findings["016"] = verdict("N/A", "MANUAL — zur Task-Zeit zu führen")
    findings["018"] = verdict("N/A", "MANUAL — zur Task-Zeit zu führen")
    has_build_manifest = any(re.search(r"Cargo\.toml$|package\.json$|pyproject\.toml$", path) for path in paths)
    findings["015"] = verdict("PASS") if has_build_manifest else verdict("N/A", "kein Code-Build (reines Docs-Repo)")

    debug_artifacts = [path for path in paths if re.search(r"\.DS_Store$|(^|/)target/|(^|/)node_modules/|\.core$|\.log$", path)]
    findings["017"] = verdict("WARN", f"Artefakte: {debug_artifacts[:3]}") if debug_artifacts else verdict("PASS")
    return findings


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    repo_list = [only] if only else sorted(repo["name"] for repo in repos())
    report, blocked = {}, []
    print(f"{'Repo':26s} FAIL WARN N/A  Blocker")
    for repo in repo_list:
        findings = check_repo(repo)
        report[repo] = findings
        failures = [code for code, result in findings.items() if result[0] == "FAIL"]
        warnings = [code for code, result in findings.items() if result[0] == "WARN"]
        not_applicable = [code for code, result in findings.items() if result[0] == "N/A"]
        blocking = [code for code in failures if code in {"001", "002", "003", "009", "010", "012", "013", "018", "019", "020"}]
        if blocking:
            blocked.append(repo)
        print(f"{repo:26s} {len(failures):4d} {len(warnings):4d} {len(not_applicable):3d}  {'BLOCKIERT' if blocking else 'ok'} ({','.join(sorted(failures))})")

    today = datetime.date.today().isoformat()
    markdown = [
        f"# ATC AGOV-Check-Lauf vom {today} (SCR-0058)",
        "",
        "Ausführung: `tools/agov_check.py` · Katalog: `ai/checks.yaml` (AGOV-CHECK-001..020)",
        f"**Ergebnis: {len(repo_list)} Repos geprüft, {len(blocked)} mit blockierenden MUST-FAILs.**",
        "",
        "| Repo | FAIL-Checks | WARN-Checks | Blockiert |",
        "|---|---|---|---|",
    ]
    for repo, findings in sorted(report.items()):
        failures = ", ".join(sorted(code for code, result in findings.items() if result[0] == "FAIL")) or "—"
        warnings = ", ".join(sorted(code for code, result in findings.items() if result[0] == "WARN")) or "—"
        markdown.append(f"| {repo} | {failures} | {warnings} | {'JA' if repo in blocked else 'nein'} |")
    markdown.extend(["", "## Details", ""])
    for repo, findings in sorted(report.items()):
        markdown.append(f"### {repo}")
        for code in sorted(findings):
            status, note = findings[code]
            markdown.append(f"- AGOV-CHECK-{code}: {status}{' — ' + note if note else ''}")
        markdown.append("")

    report_path = f"docs/AGOV-RUN-{today}.md"
    with open(report_path, "w", encoding="utf-8") as report_file:
        report_file.write("\n".join(markdown))
    print(f"\nReport: {report_path} | blockiert:", blocked or "keine")
    sys.exit(1 if blocked else 0)


if __name__ == "__main__":
    main()
