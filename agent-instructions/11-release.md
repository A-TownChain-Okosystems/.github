# 11 — Release (SCR-0057)

1. Jedes Release MUSS reproduzierbar und auditierbar sein (AP-016): Tag,
   CHANGELOG, Evidence, AUD-Records.
2. Release-Readiness RR-G01..G08 (FAM-10) + CONF-Gates (PROTOCOL-002) müssen
   PASS sein; offenes P0 blockiert (REPO-AUDIT-002 E-Blockade).
3. Kein Release ohne: Validator ALL COMPLIANT, Tests grün, offene kritische
   Meilensteine akzeptiert (MILESTONE-001), COMPAT UNKNOWN verboten.
4. Version-Baseline je Repo (VERSION-001): Tag = CHANGELOG = Manifest = Registry
   (Issue 96 offen — ehrlich als ausstehend geführt).
5. Rollback-/Recovery-Plan je Release dokumentiert; Release-Gates sind
   Owner-Aktionen (Human Gate).
