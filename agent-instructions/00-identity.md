# 00 — Agent-Identität (SCR-0039)

1. Vor JEDEM Auftrag: Identität feststellen. Nur registrierte Agenten arbeiten
   in ATC-Repos (AGENT_MANIFEST / registry/agents.yaml im atc-standards-Repo).
2. Git-Identität MUSS der registrierten Instanz entsprechen; fremde Identitäten
   sind zu melden (Eskalation an Owner), nicht zu übernehmen.
3. Rollen-Selbstzuordnung nach ai/capabilities.yaml; außerhalb der Rollen-
   Kompetenz = Eskalation, keine Selbst-Ausweitung.
4. Jeder Commit trägt die Signatur `[agent: <agent-id>]`; jeder Standard-Änderung
   eine SCR-Referenz.
5. Unregistrierte/unsichere Identität → Arbeit einstellen, Befund klassifizieren
   (F-NNN), Owner informieren.
