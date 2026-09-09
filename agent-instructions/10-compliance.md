# 10 — Compliance (SCR-0039)

1. Registry-Gate: kein Eintrag = kein Standard; Validierung S-01..S-25 je
   CI-Lauf MUSS PASS sein; Agent darf Gates nicht schwächen (Selbstanerkennungs-
   verbot), Ausnahmen nur Owner.
2. Standards-Bindung: AGENT_MANIFEST/agent.yaml je Repo verbindlich (aktuell
   396 Standards im atc-standards-Repo gebunden).
3. Lizenz-Compliance: Apache-2.0 (Repos) + ATC-LICENSE-Manifeste (LICENSE-
   001..009); kein Pseudo-Open-Source (OSD-Kompatibilität für OPEN-Typen).
4. Ehrlichkeits-Regeln: REQ-PROTO-021 (Protokoll-Status draft bis verifizierte
   Implementierung), Umsetzungsstatus ehrlich (E0–E3), Health-Grades nicht
   beschönigen.
5. Findings-Disziplin: F-NNN-SSOT (registry/findings.yaml), Duplikate vermeiden,
   RESOLVED nur mit dokumentierter Lösung.
