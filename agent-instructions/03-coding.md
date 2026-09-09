# 03 — Coding-Regeln (SCR-0057)

1. Kernel (ShivaCore): strikt Rust, no_std, bare-metal — Linux-basierte
   Ansätze sind explizit ABGELEHNT. ATCLang für App-/Contract-Ebene.
   Desktop: Rust (std) + egui, kein alternatives OS.
2. From-scratch-Prinzip: keine unnötige architektonische Divergenz (AP-015).
3. Copyright-Header „Michael Wroblewski" ist verbindlich und bleibt unverändert.
4. Trait-basierte Subsysteme mit testbaren Backends; kein toter Code ohne
   Kennzeichnung; keine Stub-Regressionen als „fertig" deklarieren.
5. Vor Implementieren: verstehen (AP-002); Bibliotheks-Reuse dokumentieren
   (Third-Party gem. ATC-STD-LICENSE-005).
6. Zeilenanzahl-Validierung bei Automatisierungen (Wiki/Data-Sync): Push
   blockieren bei >15 % Schrumpfung (Datenschutz-Vorfall-Prävention).
