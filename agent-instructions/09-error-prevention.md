# 09 — Fehler-Prävention (SCR-0039)

1. Fehler NIEMALS stillschweigend ignorieren (AP-004): jeder Fehler wird
   geloggt, klassifiziert (F-NNN) und behandelt oder explizit vertagt.
2. Ursachen statt Symptome beheben (AP-006): RCA-Pflicht je behobenem Fehler
   (ATC-STD-BUG-005); kein Symptom-Patch ohne Ursachen-Statement.
3. Prüfen, ob derselbe Defekt anderswo existiert (AP-007) — Muster-Suche in
   angrenzenden Repos/Modulen.
4. Rezidiv-Prävention (AP-008): Standard/Automatisierung nachziehen
   (z. B. Validator-Check statt manueller Disziplin).
5. Fehler-Kultur ehrlich: rote Zustände benennen, nicht umfärben (CI rot =
   rot bis fix verifiziert).
