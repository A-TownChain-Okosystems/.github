<div align="center">

# A-TownChain OS

### AI-Blockchain-Betriebssystem · ATCLang-first · A-TownChain-Ökosystem

</div>

---

> **Ein dezentrales AI-Blockchain-Betriebssystem mit ATCLang, deterministischer ATC-VM, ShivaCore, A-TownChain, GlobusOS und Aurora AI.**

## Aktueller kanonischer Stand — 14.09.2026

Die bisher im Profil genannten historischen Organisationszahlen sind nicht mehr als aktuelle SSOT zu verwenden. Der aktuelle Repository-Bestand wird direkt aus GitHub und der aktuelle Standardbestand aus `atc-standards/registry/standards.yaml` abgeleitet.

### Architektur

```text
ATCLang ──> ATC-VM ──> A-TownChain
   │           │            │
   └───────────┼────────────┘
               ▼
          ShivaCore
               │
               ▼
           GlobusOS
               │
        Aurora AI / UI
               │
               ▼
       Ecosystem Services

Meta: atc-standards + .github + atc-engineering
Integration: a-townchain-os + a-townchain-os-docs
```

### Sprach-/Systemgrenze

- **ATCLang:** On-Chain-Logik, Contracts und deterministische Chain-Semantik.
- **ATC-VM:** verbindliche Ausführungsgrenze zwischen ATCLang und Chain-Infrastruktur.
- **Rust:** Chain-tragende Infrastruktur, Node, Networking, Kernel und Systemkomponenten.
- **A-TownChain:** souveräne deterministische L1-Blockchain.
- **ShivaCore:** Rust/no_std Capability-Microkernel.
- **GlobusOS:** Betriebssystem-/Userspace-Plattform.
- **Aurora AI:** KI-/Agenten- und UI-Schicht; darf die autoritative Chain-Wahrheit nicht überschreiben.

## Governance

`atc-standards` ist die normative Standards-SSOT. APPROVED Standards werden nicht stillschweigend verändert. Die neue Family-scoped Taxonomie verwendet `ATC-STD-F{family_id}-{sequence}` mit eigener Sequenznummer je Family. Legacy-IDs bleiben unverändert und werden während der kontrollierten Migration ausdrücklich gemappt. **Canonical Allocation bleibt bis zur formalen Governance-Freigabe gesperrt.**

## Leitprinzipien

- **Evidence-only Governance:** No Evidence, No Trust.
- **Determinismus:** gleiche autorisierte Eingaben → gleiches Ergebnis.
- **Fail-Closed:** fehlende oder widersprüchliche Evidenz blockiert Gates.
- **Separation of Duties:** Implementierung, Validierung, Audit und Release-Freigabe sind getrennte Verantwortungen.
- **Human Approval:** Governance-Freigaben bleiben autoritative Entscheidungen.

## Wichtige Repositories

| Repository | Verantwortung |
|---|---|
| `atclang` | ATCLang Sprache, Compiler und Toolchain |
| `atc-vm` | ATC-VM / Ausführungsgrenze |
| `atc-shivacore` | Capability-Microkernel |
| `a-townchain` | Blockchain-Orchestrierung / Chain |
| `atc-algorithm` | Konsens-/Algorithmus-Komponenten |
| `globus-os` | Betriebssystem |
| `aurora-ai` | KI-/Agentenplattform |
| `a-townchain-os` | L7 Integration und Orchestrierung |
| `a-townchain-os-docs` | Dokumentations-/Wiki-Hub |
| `atc-standards` | Normative Standards-SSOT |
| `atc-engineering` | Engineering & Governance Software |

## Dokumentation

- `atc-standards` — Registry, Standards, Validatoren und Governance
- `a-townchain-os-docs` — Architektur-, Wiki- und Projekt-Dokumentation
- `a-townchain-os` — Integrationsarchitektur
- `atc-engineering` — Engineering-/Evidence-/Governance-Runtime

---

**Owner:** Michael Wroblewski · **Organization:** A-TownChain-Okosystems · **License:** Apache-2.0
