# 02 — Repository-Audit-Pflicht (SCR-0057)

Inspect before modify — vor Eingriffen gilt (ATC-STD-REPO-AUDIT-001/002):

1. 16 Prüfbereiche, CHECK-001..064 (registry/repo-audit-checks.yaml, SSOT);
   AUTO-Checks laufen je Lauf, HYBRID/MANUAL nach Evidenzlage.
2. Health Score 0–100 → A–E; P0 blockiert Release.
3. Jeder Befund wird klassifiziert (F-NNN in registry/findings.yaml) — „jeder
   entdeckte Defekt MUSS klassifiziert werden" (AP-005).
4. Nicht annehmen, dass Repos vollständig sind (AP-003): Live-Verifikation
   (GitHub-API, Datei-Ist) statt Behauptungen Dritter übernehmen; Fremd-
   Behauptungen sind zu verifizieren (bekannte Halluzinations-Vorfälle:
   atc-whitepaper, P0-Versionskonflikt — beide widerlegt).
5. SKIP nur mit Begründung (ohne = P1); AUD-Record je Auditlauf (AUDIT-001).
