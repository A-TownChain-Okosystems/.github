# 05 — Testing & Validierung (SCR-0039)

1. Jede materielle Änderung wird validiert (AP-009): Tests, Validatoren,
   CI-Grün als Minimum — „kompiliert ≠ fertig".
2. Kein Test-Skip ohne dokumentierten Grund; keine grün-getunkten roten
   Suites (Mutationstest-Pflicht im Standards-Validator: M1–M12).
3. Regressionen in angrenzenden Bereichen prüfen (AP-007): abhängige
   Repos/Layer benennen und prüfen (Layer-Modell L0–L7).
4. Fehlerpfad- und Grenzfallabdeckung; deterministische Tests (Rundungen,
   Overflows, Timeouts).
5. Test-Metriken ehrlich dokumentieren (X/X grün), nicht runden/schönen.
