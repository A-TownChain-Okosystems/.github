#!/usr/bin/env python3
# Copyright (c) 2026 Michael Wroblewski / A-TownChain-Okosystems. All Rights Reserved.
"""GOV-SCORE — Compliance-Gesamtbewertung (SCR-0067, Block 18).

Score darf P0/P1-Probleme NICHT verschleiern: offene P1-Findings => BLOCKED,
unabhaengig vom Prozentwert.
Eingaben: test_agov-Ergebnis (Subprocess), gov_drift-Baseline, aktive Exceptions.
"""
import os
import subprocess
import sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

def main():
    tests = subprocess.run([sys.executable, os.path.join(ROOT, "tools/test_agov.py")],
                           capture_output=True, text=True)
    t_out = tests.stdout
    t_total = t_out.count("PASS ") + t_out.count("FAIL ")
    t_pass = t_out.count("PASS ")
    test_ratio = t_pass / t_total if t_total else 0.0

    drift_path = os.path.join(ROOT, "docs/drift")
    p1, p2 = 0, 0
    if os.path.isdir(drift_path):
        for f in sorted(os.listdir(drift_path)):
            if "baseline" in f:   # Historie (Ist-Aufnahme vor Fixes) zaehlt nicht
                continue
            txt = open(os.path.join(drift_path, f), encoding="utf-8").read()
            p1 += txt.count("[DRIFT P1]")
            p2 += txt.count("[DRIFT P2]")
    ex = yaml.safe_load(open(os.path.join(ROOT, "ai/exceptions.yaml"), encoding="utf-8"))["exceptions"]
    active_exc = sum(1 for e in ex if e.get("status") == "ACTIVE")

    score = round(100 * test_ratio)
    score -= 2 * active_exc
    score = max(score, 0)
    blocked = (t_pass != t_total) or p1 > 0
    print(f"Governance Score: {score}/100  (Tests {t_pass}/{t_total}, aktive Exceptions={active_exc})")
    print(f"Debt (zulaessig, kein Blocker): {p2} P2-Drift-Findings (Org-Rollout, Roadmap)")
    print("STATUS: BLOCKED — offene P1/Test-Failures existieren (Score verscholeiert nichts)" if blocked else "STATUS: COMPLIANT")
    sys.exit(1 if blocked else 0)

if __name__ == "__main__":
    main()
