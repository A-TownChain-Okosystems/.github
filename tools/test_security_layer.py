import tempfile
from pathlib import Path
from security_layer import scan_baseline, scan_secrets, scan_workflows

def write(root, rel, content):
    p=root/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(content,encoding="utf-8")

def test_secret_detection():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp); write(root,"x.txt","-----BEGIN RSA PRIVATE KEY-----")
        assert scan_secrets(root)

def test_workflow_controls():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        write(root,".github/workflows/x.yml","name: x\non: [push]\njobs:\n  x:\n    steps:\n      - uses: actions/checkout@v4\n")
        controls={x["control"] for x in scan_workflows(root)}
        assert "SEC-P1-WORKFLOW-PERMISSIONS" in controls
        assert "SEC-P1-ACTION-PIN" in controls
        assert "SEC-P1-CHECKOUT-CREDENTIALS" in controls

def test_lockfile_baseline():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp); write(root,"SECURITY.md","# Security"); write(root,"CODEOWNERS","* @ShivaCoreDev")
        assert any(x["control"]=="SEC-P1-LOCKFILE" for x in scan_baseline(root))
