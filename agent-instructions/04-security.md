# 04 — Security (SCR-0057)

1. KEINE Secrets/Credentials in Repos (AP-013) — Fund sofort melden, nie
   kommittieren; Scanner-/AUD-Record-Pflicht.
2. Sicherheitszustände ehrlich deklarieren (ACTIVE/PARTIAL/PLANNED); keine
   erfundenen Sicherheitszusagen (ATC-STD-PROTOCOL-003 Threat Model,
   PROTOCOL-SECURITY-Registry).
3. Workflow-Dateien (.github/workflows/) sind Owner-Aktionen (GH013) — Agenten
   erstellen Patches, installieren aber keine Workflows.
4. Destructive Operationen nur mit expliziter Autorisierung (AP-012);
   Geheimhaltung privater Daten; Agent-Gates dürfen nicht selbst geschwächt
   werden (Selbstanerkennungsverbot).
5. Security-Befunde: Klassifizierung P0–P3, Kette an AUDIT-001/BUG-005 (RCA).
