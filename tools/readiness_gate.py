"""Fail-closed consumer for the Readiness -> AGOV -> Reconciliation -> merge gate.

The input is an evidence bundle emitted by workflow adapters. This module is
intentionally strict: it does not infer evidence from Markdown summaries, test
counts, status names from another domain, or an absent source/consumer mapping.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")

# These identifiers are deliberately fixed in code: a bundle cannot make an
# unknown source or consumer disappear by omitting it from its own inventory.
REQUIRED_SOURCES = {"readiness", "agov", "reconciliation"}
REQUIRED_CONSUMERS = {"merge-gate"}
READINESS_STATES = {"PREP", "NO-GO"}
AGOV_STATES = {"PASS", "FAIL", "WARN", "N/A", "PENDING"}
RECONCILIATION_STATES = {"DETECTED", "RECONCILED", "VERIFIED"}


class GateBlocked(ValueError):
    """The evidence bundle is incomplete, inconsistent, or not releaseable."""


def _object(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise GateBlocked(f"{context}: expected object")
    return value


def _full_sha(value: Any, context: str) -> str:
    if not isinstance(value, str) or not SHA40.fullmatch(value):
        raise GateBlocked(f"{context}: expected full lowercase 40-character commit SHA")
    return value


def _evidence(value: Any, context: str, checked_sha: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise GateBlocked(f"{context}: evidence must be a non-empty list")
    result = []
    for index, raw in enumerate(value):
        item = _object(raw, f"{context}[{index}]")
        if item.get("head_sha") != checked_sha:
            raise GateBlocked(f"{context}[{index}]: evidence SHA mismatch")
        run_id = item.get("workflow_run_id")
        if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
            raise GateBlocked(f"{context}[{index}]: invalid workflow_run_id")
        for field in ("repository", "job", "step"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise GateBlocked(f"{context}[{index}]: missing {field}")
        if not re.fullmatch(r"[^/\s]+/[^/\s]+", item["repository"]):
            raise GateBlocked(f"{context}[{index}]: repository must be owner/name")
        log_hash = item.get("log_sha256")
        if not isinstance(log_hash, str) or not SHA256.fullmatch(log_hash):
            raise GateBlocked(f"{context}[{index}]: missing full log_sha256")
        if item.get("status") != "success":
            raise GateBlocked(f"{context}[{index}]: evidence status is not success")
        result.append(item)
    return result


def evaluate(bundle: Any) -> dict[str, Any]:
    """Validate the complete cross-domain contract; never promote statuses."""
    root = _object(bundle, "bundle")
    if root.get("schema_version") != 1:
        raise GateBlocked("unsupported or missing schema_version")
    checked_sha = _full_sha(root.get("checked_commit_sha"), "checked_commit_sha")

    sources = _object(root.get("sources"), "sources")
    missing_sources = REQUIRED_SOURCES - set(sources)
    unknown_sources = set(sources) - REQUIRED_SOURCES
    if missing_sources or unknown_sources:
        raise GateBlocked(
            f"source coverage mismatch: missing={sorted(missing_sources)}, "
            f"unknown={sorted(unknown_sources)}"
        )

    consumers = _object(root.get("consumers"), "consumers")
    missing_consumers = REQUIRED_CONSUMERS - set(consumers)
    unknown_consumers = set(consumers) - REQUIRED_CONSUMERS
    if missing_consumers or unknown_consumers:
        raise GateBlocked(
            f"consumer coverage mismatch: missing={sorted(missing_consumers)}, "
            f"unknown={sorted(unknown_consumers)}"
        )
    merge_gate = _object(consumers["merge-gate"], "consumers.merge-gate")
    if merge_gate.get("status") != "EXECUTED":
        raise GateBlocked("merge-gate consumer was not executed")
    if merge_gate.get("checked_commit_sha") != checked_sha:
        raise GateBlocked("merge-gate checked_commit_sha mismatch")

    readiness = _object(sources["readiness"], "sources.readiness")
    agov = _object(sources["agov"], "sources.agov")
    reconciliation = _object(sources["reconciliation"], "sources.reconciliation")

    readiness_status = readiness.get("status")
    agov_status = agov.get("status")
    reconciliation_status = reconciliation.get("status")
    if readiness_status not in READINESS_STATES:
        raise GateBlocked(f"invalid readiness status: {readiness_status!r}")
    if agov_status not in AGOV_STATES:
        raise GateBlocked(f"invalid AGOV status: {agov_status!r}")
    if reconciliation_status not in RECONCILIATION_STATES:
        raise GateBlocked(f"invalid reconciliation status: {reconciliation_status!r}")

    # A gate can consume only positive, domain-correct evidence. PREP is the
    # strongest current readiness status; it is not rewritten to READY.
    if readiness_status != "PREP":
        raise GateBlocked("readiness is NO-GO; merge is blocked")
    if agov_status != "PASS":
        raise GateBlocked(f"AGOV is {agov_status}; merge is blocked")
    if reconciliation_status != "VERIFIED":
        raise GateBlocked(f"reconciliation is {reconciliation_status}; merge is blocked")

    evidence = {
        "readiness": _evidence(readiness.get("evidence"), "readiness.evidence", checked_sha),
        "agov": _evidence(agov.get("evidence"), "agov.evidence", checked_sha),
        "reconciliation": _evidence(
            reconciliation.get("evidence"), "reconciliation.evidence", checked_sha
        ),
    }
    return {
        "schema_version": 1,
        "checked_commit_sha": checked_sha,
        "decision": "PASS",
        "status": "PREP",
        "source_statuses": {
            "readiness": readiness_status,
            "agov": agov_status,
            "reconciliation": reconciliation_status,
        },
        "evidence_counts": {name: len(items) for name, items in evidence.items()},
        "consumer": "merge-gate",
        "note": "PASS is a gate decision only; it does not promote any source status.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True, help="Path to machine-readable evidence JSON")
    args = parser.parse_args(argv)
    try:
        with Path(args.bundle).open(encoding="utf-8") as handle:
            bundle = json.load(handle)
        verdict = evaluate(bundle)
    except (OSError, json.JSONDecodeError, GateBlocked) as exc:
        print(f"READINESS_GATE=BLOCKED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(verdict, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
