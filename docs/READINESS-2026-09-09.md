# ATC Integration & Readiness Control Plane — 2026-09-09 (SCR-0060)

Phase-4→5-Pivot: Governance-Evidenz → nachweisbar funktionierende Systeme.

Registry-Scope: 433 Standards · Implementierungs-Registry: 432 erfasst

## 1. IMPLEMENTATION MATRIX (standard-implementation.yaml)

- **enforced: 62** Standards (14.4 %)
- **implemented: 129** Standards (29.9 %)
- **reference: 1** Standards (0.2 %)
- **specification_only: 240** Standards (55.6 %)

Coverage-KPI (Registry): `{'registry_total': 431, 'matrix_entries': 432, 'matrix_coverage': '100%', 'enforced_target': 'je Wartungszyklus steigend (REQ-IMP-007)', 'hinweis': 'Wertigkeit der 21 SCR-0045-Detail-Eintraege bleibt; Familien-Evidence konsolidiert'}`

Ehrlicher Kern: 191/432 der erfassten Standards sind enforced/implemented (Code+CI), der Rest Spezifikation.

## 2. INTEGRATION MATRIX (interfaces.yaml — IFC-Verträge)

| IFC | Titel | Provider | Consumer | Compat | Status |
|---|---|---|---|---|---|
| IFC-0001 | ATCLang Bytecode & Compiler-API | atclang | 5 | evolving | seed |
| IFC-0002 | ShivaCore Kernel-API | atc-shivacore | 7 | evolving | seed |
| IFC-0003 | A-TownChain L1 Chain-Protokoll (PoW+PoS+PoH) | a-townchain | 9 | evolving | seed |
| IFC-0004 | SDK Client-API | atc-sdk | 5 | evolving | seed |
| IFC-0005 | Smart-Contract-Schnittstelle (ATC-001/8300/9 | atc-contracts | 3 | evolving | seed |
| IFC-0006 | Genesis-Engine Game-API | genesis-engine | 1 | experiment | seed |
| IFC-0007 | Aurora-AI Model-/Inference-API | aurora-ai | 1 | experiment | seed |
| IFC-0008 | Globus-OS Runtime-/Driver-API | globus-os | 1 | experiment | seed |
| IFC-0009 | ATVM Execution-API (Gas, Memory, Sandbox) | atc-vm | 0 | evolving | seed |
| IFC-0010 | a-townchain-os Build-Stack (Workspace, CI/CD | a-townchain-os | 0 | stable | seed |

## 3. SYSTEM READINESS

- Meilensteine ACCEPTED: ATC-M-001, ATC-M-002 (ATC-M-003 IN_PROGRESS)
- Release-Evidenz VERIFIED: 4 (EV-ATC-M-001, EV-ATC-M-002, EV-P2P-SPEC-001, EV-GOV-CORE-001…)
- Offene P0: 0 · offene P1: 3 (F-044, F-055, F-056)
- Rote CI-Workflows: 3 Repos (atc-standards(1), atc-shivacore(1), a-townchain(1))

| Tier | Netzwerk | Chain-ID | Registry-Status | Gate (ehrlich) |
|---|---|---|---|---|
| devnet | ATC-DEVNET | 658469 | planned | NO-GO |
| testnet | ATC-TESTNET | 658468 | planned | NO-GO — Blocker: offene P1 (3), rote CI (3) |
| mainnet | ATC-MAINNET | 658467 | planned | NO-GO — Blocker: offene P1 (3), rote CI (3) |

## 4. MAINTENANCE QUEUE (getrennt von Governance — Owner-Triage)

- Offene Dependabot-PRs: 100
- Offene Dependabot-Alerts a-townchain-os: 14 (F-055)

- [atc-sdk] chore(deps): update pyyaml requirement from >=6.0 to >=6.0.3
- [atc-sdk] chore(deps): update requests requirement from >=2.28 to >=2.
- [atc-sdk] chore(deps): update click requirement from >=8.1 to >=8.5.0 
- [atc-sdk] chore(deps): update rich requirement from >=13.0 to >=15.0.0
- [globus-os] chore(deps): bump typescript from 5.9.3 to 7.0.2 in /modules
- [globus-os] chore(deps-dev): bump @types/node from 20.19.43 to 26.4.1 in
- [globus-os] chore(deps-dev): bump @types/jest from 29.5.14 to 30.0.0 in 
- [globus-os] chore(deps-dev): bump jest from 29.7.0 to 30.5.1 in /modules
- [globus-os] chore(deps): update eframe requirement from 0.27 to 0.36 in 
- [globus-os] chore(deps): update egui requirement from 0.27 to 0.36 in /m
- [atc-wallet] chore(deps): update ed25519-dalek requirement from 2.0 to 3.
- [aurora-ai] chore(deps): bump three from 0.184.0 to 0.185.1 in /modules/