# 01 — Mission & Verortung (SCR-0057)

Ökosystem-Ziel: from-scratch OS (GlobusOS/ShivaCore, Rust no_std), A-TownChain
Blockchain (Chain-ID 658467), ATCLang App-/Contract-Ebene, Desktop via Rust(std)+egui.

Verbindlich: ATC-1..40 = technische Spezifikation; ATC-41..80 = Vision/Lore OHNE
Engineering-Relevanz (keine Sprint-Planung/ETAs/Done-Metriken daraus).

Ehrlichkeit: „Build != fertig", „dokumentiert != erzwungen", keine unverified claims.
Kanonische Ist-Quelle: REALITY_STATUS.md (a-townchain-os-docs, append-only).
Standards-SSOT: registry/ im atc-standards-Repo (433 Standards (Stand 09.09.2026), Validator je CI).
Layer L0–L7 gem. REPO_ARCHITECTURE; Namenskonvention atc--Präfix (Ausnahmen
dokumentiert in NAMING_CONVENTIONS.md).

## Verbindliche Implementierungspriorität

Arbeite dependency-first und nutze die organisationsweite Reihenfolge aus `AGENTS.md §10`:
- **P0:** Security/TCB, SSOT- und ABI-Konflikte, normative Standards, CI/Evidence.
- **P1:** kanonischer ShivaCore-Kernel, ATC-VM, Blockchain-Kern, Konsensentscheidung und reproduzierbare Toolchain.
- **P2:** ATC-Lang, GlobusOS, Node und systemübergreifende Integration.
- **P3:** Aurora-AI und Genesis Engine hinter least-privilege Service-/Capability-Grenzen.
- **P4:** Fuzzing, Security Review, Traceability, Provenance/SBOM und Release-Nachweise.

Keine Arbeit als erledigt markieren, nur weil sie spezifiziert oder dokumentiert ist. `IMPLEMENTED` verlangt integrierten Code; `VERIFIED` verlangt exakten SHA plus Run → Job → Step → Exit/Logs/Artefakte. Sicherheitskritische Blocker stoppen abhängige Arbeit. Keine automatischen Merges, keine Gate-Abschwächung. Die Roadmap in `atc-engineering` bleibt bis zu Merge und erfolgreicher Validierung ein Plan, kein Governance-Nachweis.
