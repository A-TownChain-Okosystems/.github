# 08 — Change-Management (SCR-0057)

1. Kette: SCR → Standard → registry/standards.yaml + versions.yaml → CHANGELOG
   → Validator → (bei MAJOR) COMPAT-001-Gate → AUDIT (ATC-STD-CHANGE-001).
2. Keine stillen Updates (UPD-G-Kernregel); PATCH/MINOR/MAJOR korrekt wählen;
   Rechte-/Status-/Breaking-Änderungen sind MAJOR mit Owner-Gate.
3. Abhängigkeiten prüfen (AP-008): Layer L0–L7, Nachbar-Standards, Versionen —
   Auswirkungen dokumentieren.
4. Rückwärtskompatibilität erhalten, außer explizit Breaking mit Migrationspfad
   und Owner-Freigabe (AP-011).
5. Emergency-Changes: dokumentieren + nachholen (UPDATE-001 Emergency-Regel).
