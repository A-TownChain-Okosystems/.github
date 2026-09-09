# ATC Organisations-AGENTS.md — Master-Einstieg für alle Agenten (SCR-0057)

> Verbindlicher Org-Standard für jeden Agenten in jedem ATC-Repository —
> Teil des **ATC Org-weiten Agent-Governance-Systems** (SCR-0058). Selbst-
> Compliance: geprüft via tools/agov_check.py (AGOV-CHECK-001..020).
> Repo-spezifische AGENTS.md ERGÄNZEN diese Regeln — sie dürfen keine höhere
> Sicherheits-, Compliance- oder Governance-Regel stillschweigend aushebeln.

**Hierarchie-Kaskade:** Org-Policy → AGENT_MANIFEST → Org-AGENTS.md (dieses
Dokument) → Repo-AGENTS.md → Verzeichnis-Regeln → Task; spezifischere Regeln
ergänzen, hebeln nie höhere aus.

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

## 5. Registry-Snapshot & dynamische Bindung (SCR-0059)

Neue APPROVED-Standards sind ab Freigabe verbindlich — ABER der Compliance-Scope
eines **laufenden** Tasks MUSS reproduzierbar festgehalten sein: Jede wesentliche
Aufgabe beginnt mit einem **Registry-Snapshot** (registry_version, registry_commit,
registry_hash, approved_standards), Aufzeichnung nach `.github/ai/audit/` (je Repo)
bzw. `ai/audit/` (Hub); Schema `ai/schemas/snapshot.schema.json`. Scope-Wechsel
während eines Tasks = neuer Task mit neuem Snapshot — kein stiller Kompetenzwechsel.
Später beweisbar: „Welche Standards waren für DIESEN Task verbindlich?"

## 6. MERGE-GATE (normativ)

Agenten-PRs werden NICHT gemerged, solange nicht sämtliche obligatorischen Gates
PASS sind: **1 Agent Identity · 2 Standards Compliance · 3 Registry · 4 Validation ·
5 Mutation · 6 Repository Audit · 7 Audit Record · 8 Documentation · 9 Review ·
10 Human Approval.** FAIL oder PENDING in einem verpflichtenden Gate ⇒ **NO MERGE**
(ausgenommen nur eine genehmigte Ausnahme gem. §7). Maschinenlesbar:
`ai/governance-rules.yaml`. Bekannte Durchsetzungs-Lücke: PR-Pflicht wird derzeit
von Admin-Pushes gebypasst (F-045) — owner-seitig offen.

## 7. EXCEPTION RULE (Ausnahme-/Notfallprozess)

Ein Agent DARF keinen verbindlichen Standard eigenmächtig außer Kraft setzen. Ist
ein Standard technisch nicht erfüllbar, MUSS der Agent: **1** den Konflikt
identifizieren, **2** einen AUD-Record erstellen, **3** den betroffenen Standard
referenzieren, **4** die Abweichung dokumentieren, **5** eine Ausnahme beantragen,
**6** auf HUMAN APPROVAL warten. Ohne genehmigte Ausnahme gilt: **Validation = FAIL,
Merge = BLOCKED.** Verhindert: „konnte ihn nicht erfüllen → ignoriere ihn."
Notfall-Pfad: UPDATE-001 Emergency-Regel (dokumentieren + nachholen).

## 8. STANDARD CONFLICT RULE (Priorität)

`ATC-STD-000 → APPROVED Governance-Standards → spezialisierte Standards →
Repo-spezifische Standards → Task-Anforderungen.` Eine niedrigere Stufe DARF keine
höhere überschreiben; unauflösbare Konflikte ⇒ HUMAN REVIEW. Maschinenlesbar und
normativ festgeschrieben: `ai/governance-rules.yaml` (SCR-0059).

## 9. Fehlende Tool-/CI-Fähigkeit (P2)

Kann ein Gate technisch nicht ausgeführt werden (Tool/CI fehlt), gilt: KEIN stiller
SKIP — Befund klassifizieren (F-NNN), Gate = PENDING, EXCEPTION RULE anwenden.
SKIP nur mit dokumentierter Begründung (REPO-AUDIT-002: SKIP ohne Begründung = P1).

*ATC Org-AGENTS.md v1.1.0 · SCR-0057/0058/0059 · 09.09.2026 · Aurora (Superagent)*
