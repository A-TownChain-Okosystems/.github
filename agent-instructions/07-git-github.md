# 07 — Git & GitHub (SCR-0057)

1. Commit-Konvention: aussagekräftige Messages + `[agent: <id>]`-Signatur +
   SCR-Referenz bei Standard-/Governance-Änderungen; keine Force-Pushes auf
   main; keine Historien-Fälschung.
2. PR-Disziplin: die Org-Branch-Protection sieht PR-Pflicht vor; Agenten
   arbeiten nachweisbar (Commits, AUD-Records). Direkt-Pushes nur mit
   Owner-Mandat — der Zustand „Regel wird von Admin-Pushes gebypasst" ist
   als F-045 registriert und wartet auf die Owner-Entscheidung.
3. Workflow-Dateien (GH013): Agent erstellt Patch + Übergabe an Owner.
4. Verwaiste Referenzen (tote SHAs/Tags) sind Befunde, nicht Stillstand —
   bereinigen nur via SCR (z. B. v2.0.0-Tag, Issue 97).
5. Kein Commit ohne Registry-Gate-Konvention bei Standards-Repos.
