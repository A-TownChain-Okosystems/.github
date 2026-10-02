#!/usr/bin/env python3
"""ATC Security Layer — deterministic repository security baseline."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"][^'\"]+['\"]"),
]
ACTION_RE = re.compile(r"^\s*-\s*uses:\s*([^\s#]+)\s*(?:#.*)?$", re.MULTILINE)
SHA_REF_RE = re.compile(r"^[0-9a-f]{40}$")
WRITE_ALL_RE = re.compile(r"(?im)^\s*permissions:\s*write-all\s*$")
PR_TARGET_RE = re.compile(r"(?im)^\s*pull_request_target\s*:")
CHECKOUT_RE = re.compile(r"actions/checkout@([^\s#]+)")
PERMISSIONS_RE = re.compile(r"(?im)^permissions:\s*$")
LOCKFILES = {"Cargo.lock","package-lock.json","pnpm-lock.yaml","yarn.lock","uv.lock","poetry.lock","Pipfile.lock","requirements.lock"}
SKIP_DIRS = {".git",".venv","node_modules","__pycache__"}

def iter_files(root):
    for path in root.rglob("*"):
        if path.is_file() and not any(part in SKIP_DIRS for part in path.parts):
            yield path

def scan_secrets(root):
    findings=[]
    for path in iter_files(root):
        try: data=path.read_text(encoding="utf-8")
        except (UnicodeDecodeError,OSError): continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(data):
                findings.append({"control":"SEC-P0-SECRET","path":str(path),"pattern":pattern.pattern})
    return findings

def scan_workflows(root):
    findings=[]
    workflow_dir=root/".github"/"workflows"
    if not workflow_dir.exists():
        return [{"control":"SEC-P1-WORKFLOW-DIR","path":".github/workflows","reason":"missing"}]
    for path in sorted(workflow_dir.glob("*")):
        if path.suffix not in {".yml",".yaml"}: continue
        text=path.read_text(encoding="utf-8"); rel=str(path.relative_to(root))
        if not PERMISSIONS_RE.search(text):
            findings.append({"control":"SEC-P1-WORKFLOW-PERMISSIONS","path":rel,"reason":"missing permissions block"})
        if WRITE_ALL_RE.search(text):
            findings.append({"control":"SEC-P1-WORKFLOW-PERMISSIONS","path":rel,"reason":"write-all permissions"})
        if PR_TARGET_RE.search(text):
            findings.append({"control":"SEC-P0-PR-TARGET","path":rel,"reason":"pull_request_target requires explicit security review"})
        for action in ACTION_RE.findall(text):
            if "@" not in action: continue
            ref=action.rsplit("@",1)[1]
            if not SHA_REF_RE.fullmatch(ref):
                findings.append({"control":"SEC-P1-ACTION-PIN","path":rel,"action":action,"reason":"action is not pinned to immutable commit SHA"})
        for ref in CHECKOUT_RE.findall(text):
            if not SHA_REF_RE.fullmatch(ref):
                findings.append({"control":"SEC-P1-CHECKOUT-PIN","path":rel,"ref":ref,"reason":"checkout must be pinned to immutable commit SHA"})
            if "persist-credentials: false" not in text:
                findings.append({"control":"SEC-P1-CHECKOUT-CREDENTIALS","path":rel,"reason":"checkout persist-credentials must be false"})
    return findings

def scan_baseline(root):
    findings=[]
    if not (root/"SECURITY.md").exists(): findings.append({"control":"SEC-P1-SECURITY-POLICY","path":"SECURITY.md","reason":"missing"})
    if not (root/"CODEOWNERS").exists(): findings.append({"control":"SEC-P1-CODEOWNERS","path":"CODEOWNERS","reason":"missing"})
    if not any((root/name).exists() for name in LOCKFILES):
        findings.append({"control":"SEC-P1-LOCKFILE","path":".","reason":"no supported dependency lockfile detected"})
    return findings

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--root",default="."); parser.add_argument("--json",action="store_true")
    args=parser.parse_args(); root=Path(args.root).resolve()
    findings=scan_secrets(root)+scan_workflows(root)+scan_baseline(root)
    report={"schema":"ATC-SECURITY-LAYER-1.0","status":"FAIL" if findings else "PASS","finding_count":len(findings),"findings":findings}
    if args.json: print(json.dumps(report,indent=2,sort_keys=True))
    else:
        print(f"ATC Security Layer: {report['status']} ({len(findings)} findings)")
        for f in findings: print(f"- {f['control']}: {f.get('path','?')}: {f.get('reason',f.get('pattern','finding'))}")
    return 1 if findings else 0

if __name__=="__main__": sys.exit(main())
