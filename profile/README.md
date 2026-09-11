<div align="center">

# A-TownChain OS

### AI-Blockchain-Betriebssystem · ATCLang-first · 26 Repositories · 476 Standards

</div>

---

> **Ein dezentrales AI-Blockchain-Betriebssystem mit einer durchgängigen Sprache (ATCLang), deterministischer VM, Kernel-Isolation und KI-gesteuerter Governance.**

## Architektur

```
                    ┌─────────────────────────────────────┐
  L7  INTEGRATION   │  a-townchain-os · a-townchain-os-docs │  Monorepo · Wiki · Orchestrierung
                    └──────────────────┬──────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
  L6  GENESIS       │  genesis-engine · genesis-chronicles  │  Genesis-Datei · Narrativ
                    └──────────────────┬──────────────────┘
                                       │
  ┌─────────────────┴──────────────────────────────────────────┐
  │                    L5  SERVICES (13 Repos)                  │
  │  contracts · sdk · wallet · explorer · indexer · interop    │
  │  node · storage · compute · mining · oracle · launchpad     │
  │  marketplace                                                │
  └─────────────────────────────┬────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
  L4  OS            │      globus-os         │  Betriebssystem / Plattform
                    └───────────┬───────────┘
                                │
              ┌─────────────────┴─────────────────┐
  L3  CHAIN   │  a-townchain · atc-algorithm       │  Blockchain · Consensus · Algorithmen
              └─────────────────┬─────────────────┘
                                │
                    ┌───────────┴───────────┐
  L2  AI           │      aurora-ai          │  KI / Interpretation / UX
                    └───────────┬───────────┘
                                │
              ┌─────────────────┴─────────────────┐
  L1  KERNEL  │  atc-shivacore · atc-zkp            │  Kernel · Hardware · ZKP
              └─────────────────┬─────────────────┘
                                │
              ┌─────────────────┴─────────────────┐
  L0  CORE    │  atclang · atc-vm                   │  Sprache · Compiler · VM
              └─────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────┐
  │  atc-standards (476 Standards) · .github (Governance) │  Meta-Ebene
  └─────────────────────────────────────────────────────┘
```

## Schnellstart

```bash
# Monorepo klonen
git clone https://github.com/A-TownChain-Okosystems/a-townchain-os.git
cd a-townchain-os

# ATCLang-Compiler (L0)
git clone https://github.com/A-TownChain-Okosystems/atclang.git

# VM deterministisch ausführen
git clone https://github.com/A-TownChain-Okosystems/atc-vm.git
cd atc-vm && cargo test --test-threads=1
```

## Ökosystem in Zahlen

| Metrik | Wert |
|---|---|
| Repositories | 26 aktiv (+ 1 Governance-Hub) |
| Standards | 476 (ATC-STD-000 bis ENG-001) |
| Sprachen | Rust (Core) · ATCLang (Smart Contracts) · Python (AI/Tooling) · TypeScript (UI) |
| Architektur-Layer | L0 (Core) → L7 (Integration) |
| Governance | ATC-AI-GOV v1.0 · 51 Standard-Familien · CI-Gate-Score 85+ |
| Lizenz | Apache-2.0 |

## Leitprinzipien

- **ATCLang First** — Eine Sprache für Smart Contracts, VM-Bytecode und Systemlogik
- **Determinismus als First-Class-Requirement** — `F(state, tx, block)` → identisches Ergebnis auf allen Knoten
- **Security by Design** — Threat Model vor Implementierung; Key-Hygiene; Fail-Closed-CI-Gates
- **AI schlägt vor, die Kette entscheidet** — Aurora AI → Vorschlag → ATC → deterministische Decision → State
- **Evidence-only Governance** — Keine synthetischen PASS-Nachweise; API-bestätigte Evidenz

## Wichtige Repositories

| Repository | Layer | Beschreibung |
|---|---|---|
| [`atclang`](https://github.com/A-TownChain-Okosystems/atclang) | L0 | ATCLang Compiler & Toolchain |
| [`atc-vm`](https://github.com/A-TownChain-Okosystems/atc-vm) | L0 | Deterministische VM mit Receipt-Verifikation |
| [`atc-shivacore`](https://github.com/A-TownChain-Okosystems/atc-shivacore) | L1 | Kernel · Hardware-Isolation · Krypto |
| [`aurora-ai`](https://github.com/A-TownChain-Okosystems/aurora-ai) | L2 | AI-Interpretation · UX · Agent-Governance |
| [`a-townchain`](https://github.com/A-TownChain-Okosystems/a-townchain) | L3 | Blockchain Core · Consensus · State |
| [`globus-os`](https://github.com/A-TownChain-Okosystems/globus-os) | L4 | Betriebssystem / Plattform |
| [`atc-node`](https://github.com/A-TownChain-Okosystems/atc-node) | L5 | Full Node Implementation |
| [`atc-wallet`](https://github.com/A-TownChain-Okosystems/atc-wallet) | L5 | Keys · Accounts · Signing |
| [`a-townchain-os`](https://github.com/A-TownChain-Okosystems/a-townchain-os) | L7 | Integrations-Monorepo · CI/CD · Launch |
| [`atc-standards`](https://github.com/A-TownChain-Okosystems/atc-standards) | Meta | 476 Standards · Registry · Governance |

## Dokumentation

- **[Wiki (69+ Kapitel)](https://github.com/A-TownChain-Okosystems/a-townchain-os-docs)** — Vollständige Architektur- und API-Dokumentation
- **[Standards Registry](https://github.com/A-TownChain-Okosystems/atc-standards)** — 476 normative Standards (ATC-STD-000 bis ENG-001)
- **[Governance Hub](https://github.com/A-TownChain-Okosystems/.github)** — Org-weite Agent-Governance (ATC-AI-GOV v1.0)
- **[Architektur-Spec](https://github.com/A-TownChain-Okosystems/a-townchain-os/blob/main/ARCHITECTURE.md)** — Layer-Spezifikation und Modul-Sync

## Engineering-Standard

Alle Repositories folgen **[ATC-STD-ENG-001](https://github.com/A-TownChain-Okosystems/atc-standards/blob/main/standards/eng/ATC-STD-ENG-001.md)** (Software Engineering & Code Quality Standard):

> *Correct by design → deterministic where required → secure by default → testable → auditable → reproducible → versioned → standards-compliant*

## Roadmap

- **Sprint 2.x** — Consensus · Smart Contracts · Governance (aktiv)
- **Sprint 3.x** — Gateway · Backend · AI Layer (aktiv)
- **Sprint 4.0** — Mainnet Launch (Chain-ID 658467)
- **Sprint 5.0+** — Trans-Metaverse · Ultimate Architecture Tiers

---

<div align="center">

**Owner:** Michael Wroblewski · **License:** Apache-2.0 · **Standards:** ATC-STD-000 v1.3.0

</div>
