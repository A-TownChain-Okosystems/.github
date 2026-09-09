# ATC Organisations-AGENTS.md — Master-Einstieg für alle Agenten (SCR-0057)

> Verbindlicher Org-Standard für jeden Agenten in jedem ATC-Repository.
> Repo-spezifische AGENTS.md ERGÄNZEN diese Regeln — sie dürfen keine höhere
> Sicherheits-, Compliance- oder Governance-Regel stillschweigend aushebeln.

## 1. Arbeits-Sequenz (Pflicht je Auftrag)

1. **Identität feststellen** (Modul 00): AGENT_MANIFEST-Registrierung, Git-Identität.
2. **Org-Regeln laden:** dieses Dokument + ai/policies.yaml (AP-001..016, normativ).
3. **Repo-AGENTS.md suchen** (Verweis-Block) und Anweisungen zusammenführen.
4. **Prioritäten/ Konflikte prüfen:** spezifischer ergänzt allgemeiner; bei
   Widerspruch zu Security/Compliance/Governance gilt die HÖHERE Regel + Eskalation.
5. **Repository-Audit durchführen** (Modul 02, ATC-STD-REPO-AUDIT-001/002).
6. **Änderungsumfang bestimmen** und Abhängigkeiten/Risiken prüfen (Modul 08).
7. **Implementieren** (Modul 03/07), **validieren** (Modul 05), **Regressionen
   in angrenzenden Bereichen prüfen** (Modul 09).
8. **Dokumentation/Standards/Registry aktualisieren** (Modul 06/10).
9. **Ergebnis nachvollziehbar dokumentieren:** Commit-Signatur
   `[agent: <id>]`, SCR-Referenz bei Standard-Änderungen, AUD-Records bei Audits.

## 2. Module (agent-instructions/)

00-identity · 01-mission · 02-repository-audit · 03-coding · 04-security ·
05-testing · 06-documentation · 07-git-github · 08-change-management ·
09-error-prevention · 10-compliance · 11-release

## 3. Rollen (ai/capabilities.yaml)

ATC-AI-ARCH-001 (Architektur/Koordination) · ATC-AI-AUDIT-001 (Audit) ·
ATC-AI-SEC-001 (Security) · ATC-AI-CI-001 (CI/CD) · ATC-AI-DOC-001 (Doku/Standards) ·
ATC-AI-TEST-001 (QA) · ATC-AI-RELEASE-001 (Release/Versionierung) ·
ATC-AI-GOV-001 (Governance/Compliance).

## 4. Verbindliche Fachwahrheiten (Kurzform)

ATC-1..40 = verbindliche Spezifikation; ATC-41..80 = Vision/Lore ohne
Engineering-Relevanz. OS-Standard: GlobusOS/ShivaCore bare-metal Rust (no_std);
keine Linux-basierten Kernel-Ansätze. App-/Contract-Ebene: ATCLang. Desktop:
Rust (std) + egui. Copyright: „Michael Wroblewski". Kanonisch: REALITY_STATUS.md
(a-townchain-os-docs, append-only). Standards-SSOT: registry/ im atc-standards-Repo
(433 Standards (Stand 09.09.2026), Validator-Gates je CI-Lauf). Chain-ID: 658467. Lizenz: Apache-2.0
(Repos) + ATC-LICENSE-System (Ökosystem-Ebene, licenses/ im atc-standards-Repo).

*ATC Org-AGENTS.md v1.0.0 · SCR-0057 · 09.09.2026 · Aurora (Superagent)*
