#!/usr/bin/env python3
"""ATC Agent Authorization Engine (GOV-008/009, SCR-0064).
Entscheidet VOR der Aktion: Agent → Identity → Status → Role → Capability →
Permission → Scope → Policy → ALLOW/DENY. Fail Closed: unknown = DENY, nie ALLOW.
Aufruf: python3 tools/authorize.py <agent_id> <operation> [--repo R] [--path P] [--json]"""
import yaml, re, json, sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")

def load(p):
    with open(p) as f:
        return yaml.safe_load(f)

def decide(agent_id, op, repo=None, path=None):
    chain, evidence = [], []
    def step(name, ok, ev):
        chain.append((name, ok, ev))
        evidence.append(ev)
        return ok
    caps = load("ai/capabilities.yaml")["agent_capabilities"]
    perms = load("ai/permissions.yaml")
    manifest = open("AGENT_MANIFEST.md").read()
    # 1. Identity: Agent im Manifest/Registry bekannt?
    m = re.search(rf"^\|?\s*{re.escape(agent_id)}\b.*$", manifest, re.M)
    identity = step("identity", bool(m), f"AGENT_MANIFEST-Zeile: {'gefunden' if m else 'NICHT gefunden'}")
    if m and "PROPOSED" in m.group(0):
        step("status", False, "Status PROPOSED — keine regulären Aufgaben")
    elif m:
        inactive = [s for s in ("SUSPENDED", "DEPRECATED", "RETIRED") if s in m.group(0)]
        step("status", not inactive, f"Status: {inactive[0] if inactive else 'ACTIVE'}")
    else:
        step("status", False, "unbekannt")
    # 2. Role/Capability: Rolle definiert, covered_by (Instanz) gebunden?
    role = next((r for r in caps["roles"] if r["id"] == agent_id), None)
    step("role", role is not None, f"Rolle: {role['name'] if role else 'UNBEKANNT'}")
    if role:
        step("capability-instance", bool(role.get("covered_by")),
             f"covered_by: {role.get('covered_by') or 'NULL (kein Agent zugeordnet)'}")
    # 3. Permission: Operation fuer Agent gelistet und erlaubt?
    agent_ops = (perms.get("agents") or {}).get(agent_id)
    if agent_ops is None:
        ok = step("permission", False, f"kein permission-Eintrag fuer {agent_id} (Default DENY)")
    else:
        op_entry = next((o for o in agent_ops["operations"] if o["op"] == op), None)
        ok = step("permission", op_entry is not None and op_entry.get("allowed") is True,
                  f"op={op}: {op_entry or 'NICHT GELISTET (Default DENY)'}")
        if ok:
            note = op_entry.get("note", "")
            step("scope", True, f"scope={op_entry.get('scope', 'beliebig')}" + (f"; note={note}" if note else ""))
    # 4. Policy: ATC-POL-007 (destruktiv) / ATC-POL-009 (workflow) Owner-Gate
    pol = load("ai/policies.yaml")["agent_policies"]
    if op in ("force_push", "delete_branch", "push_workflow_file"):
        gates = perms.get("gates", {})
        if op == "push_workflow_file" and "GH013" in str(gates.get("push_workflow_file", "")) + note_for(agent_ops, op):
            step("policy-owner-gate", False, f"{op}: Owner-Gate/GH013 — Agent darf nicht selbst (CAPABILITY-001 REQ-AGOV-CAP-003)")
        else:
            step("policy-owner-gate", False, f"{op}: destruktiv/workflow — Owner-Gate erforderlich (ATC-POL-007/009)")
    decision = "ALLOW" if chain and all(ok for _, ok, _ in chain) else "DENY"
    return decision, chain, evidence

def note_for(agent_ops, op):
    if not agent_ops:
        return ""
    e = next((o for o in agent_ops["operations"] if o["op"] == op), None)
    return str(e.get("note", "")) if e else ""

if __name__ == "__main__":
    args = sys.argv[1:]
    agent, op = args[0], args[1]
    repo = args[args.index("--repo") + 1] if "--repo" in args else None
    path = args[args.index("--path") + 1] if "--path" in args else None
    d, chain, ev = decide(agent, op, repo, path)
    if "--json" in args:
        print(json.dumps({"decision": d, "chain": [{"step": s, "ok": ok, "evidence": e} for s, ok, e in chain]}, indent=1))
    else:
        print(f"DECISION: {d}")
        for s, ok, e in chain:
            print(f"  {'✓' if ok else '✗'} {s:22s} {e}")
    sys.exit(0 if d == "ALLOW" else 1)
