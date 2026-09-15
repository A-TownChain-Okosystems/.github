# A-TownChain-Okosystems — Organization Current State

**Snapshot:** 2026-09-15  
**Scope:** all repositories currently visible through the organization GitHub connection  
**Principle:** No Evidence, No Trust

## 1. Repository inventory

The current organization inventory contains **31 repositories**:

- `.github`
- `a-townchain-os`
- `a-townchain-os-docs`
- `a-townchain`
- `atc-shivacore`
- `globus-os`
- `aurora-ai`
- `atclang`
- `atc-contracts`
- `atc-wallet`
- `atc-node`
- `atc-sdk`
- `atc-vm`
- `atc-standards`
- `atc-compute`
- `atc-oracle`
- `atc-storage`
- `atc-mining`
- `atc-indexer`
- `atc-interop`
- `atc-explorer`
- `atc-marketplace`
- `atc-launchpad`
- `atc-algorithm`
- `atc-zkp`
- `genesis-engine`
- `genesis-chronicles`
- `genesis-franchise-factory`
- `atc-ide`
- `atc-engineering`
- `demo-repository` (private/template/exempt)

`atc-standards` has already incorporated the current 31-repository registry state. The organization inventory must be treated as 31, not the older 26/27/28/29/30 snapshots.

## 2. Canonical architecture cross-check

```text
ATCLang -> ATC-VM -> A-TownChain
             ^
             |
        execution boundary

Rust -> native infrastructure / transport / node / OS services

Aurora -> GlobusOS IPC/API -> ShivaCore

KAI-OS = architecture composed of ATCLang + ShivaCore + ATC-VM + A-TownChain + Aurora + GlobusOS
```

KAI-OS is an architecture/platform concept, not a replacement name for GlobusOS or ShivaCore.

## 3. Active P0/P1 blockers

### P0 — organization dependency graph

- `atc-launchpad#3` — organization Dependency Graph must be enabled for Dependency Review/SBOM support.
- `atc-algorithm#3` — same organization-level dependency graph blocker.

This cannot be truthfully marked PASS by repository-local code changes alone.

### P0 — a-townchain-os production gate

`a-townchain-os#112` remains OPEN. GATE-KAI-001 Iteration 2 requires Model Registry + Verified Cache, persistent WAL/snapshot/crash recovery, real TCP transport with limits/backpressure and discovery persistence, versioned upgrade/rollback semantics, and external-security-audit preparation. Therefore `a-townchain-os` remains `NOT_READY`.

### P0 — deterministic CI gates

`atc-standards#13` remains OPEN. Repository-local deterministic gate scripts exist for the listed repos, but the remaining workflow rollout cannot be represented as 26/26 PASS until the workflows are actually present and CI evidence is current.

### P0 — language/execution boundary

`.github#12` remains OPEN. AD-008 requires `atc-contracts` to use ATCLang for consensus-critical on-chain logic, Rust for native infrastructure/transport, and ATC-VM as the execution boundary. UI/AI TypeScript remains permitted where it is not consensus-critical. Migration requires functional equivalence and deterministic test parity.

## 4. Active implementation blocker found by code search

`atc-shivacore/modules/atc-shivacore/kernel/src/lkm.rs` still contains a real `unimplemented!()` in `DependencyGraph::dependencies()`.

The backing graph uses `BTreeSet<String>`, so the declared `&[String]` return type cannot be implemented by borrowing the set. `get_dependencies()` already exposes the deterministic owned `Vec<String>` representation.

The copy under `a-townchain-os-docs/docs/archive/` is historical archive material and is not active source.

## 5. Current GlobusOS state

`globus-os` is the current userspace/OS platform repository above ShivaCore. Its workspace contains explicit system boundaries for identity, wallet service and settings in addition to core, IPC, security, process, memory, VFS, networking, devices, services, graphics, audio, package, update and runtime.

Current production status remains `NOT_READY`. Hardware-specific execution evidence is still required for UEFI/ACPI, PCIe enumeration, IOMMU/DMA, NVMe, NIC DMA, persistent filesystem recovery and measured/cryptographic boot.

An open PR exists as `globus-os#13` (`feat: implement P1 platform integration contracts and deterministic init`). It is currently **not mergeable** and must not be treated as integrated mainline functionality until conflicts are resolved and CI/hardware evidence is reviewed.

## 6. Documentation synchronization rule

`a-townchain-os-docs` is an archive/knowledge-base repository. Historical TODOs, READMEs and monorepo copies inside `docs/archive/`, `docs/monorepo-legacy/` and similar paths must not override active repository source.

Current implementation truth is derived from the active repository default branch, current CI evidence, current issues/PRs and the canonical standards registry.

## 7. Current standards state

`atc-standards` is the canonical standards SSOT. Its generated views are authoritative only for their current generated snapshot; historical audit narrative below a generated snapshot is retained as audit history and must not be interpreted as the current state.

Recent organization work includes the approved standards expansion, `atc-engineering` registry integration, code-quality gates and maintenance/readiness implementation work. `atc-engineering` remains a separate engineering control-plane repository and must not become a second standards SSOT.

## 8. Release-readiness rule

No repository may be promoted to `PRODUCTION_READY` solely because a README claims completion, an archived document says 100%, a unit test passes without required hardware/runtime evidence, a specification exists, or a repository has been registered in the standards registry.

Production readiness requires the repository's defined implementation, test, security, compatibility and evidence gates to be satisfied.

## 9. Cross-check result

**Organization consistency:** architecture is substantially aligned, but the organization is **not yet globally release-ready**.

The verified blockers are explicitly retained above rather than being hidden by documentation updates. This document is a dated audit snapshot and must be superseded by a newer evidence-backed snapshot after the blockers change.
