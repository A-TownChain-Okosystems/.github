"""Fail-closed helpers for the Hub readiness report.

These helpers deliberately keep readiness, AGOV, and reconciliation verdicts
as separate domains. They do not infer one domain from another.
"""

from __future__ import annotations

import base64
import re
from typing import Any, Callable

SHA40 = re.compile(r"^[0-9a-f]{40}$")
READINESS_STATES = {"NO-GO", "PREP"}
AGOV_STATES = {"PASS", "FAIL", "WARN", "N/A", "PENDING"}
RECONCILIATION_STATES = {"DETECTED", "RECONCILED", "VERIFIED"}


def decode_contents(payload: Any, context: str) -> str:
    """Decode a GitHub Contents API object with strict Base64 validation.

    GitHub may wrap Base64 text in ASCII transport whitespace. Remove only
    spaces, tabs, CR, and LF before strict alphabet/padding validation.
    """
    if not isinstance(payload, dict):
        raise RuntimeError(f"{context}: invalid contents payload type")
    encoded = payload.get("content")
    if not isinstance(encoded, str) or payload.get("encoding") != "base64":
        raise RuntimeError(f"{context}: missing base64 content")
    normalized = re.sub(r"[ \t\r\n]", "", encoded)

    try:
        return base64.b64decode(normalized, validate=True).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise RuntimeError(f"{context}: invalid Base64 content or non-UTF-8 payload") from exc


def response_json(
    response: Any, context: str, expected_type: type | tuple[type, ...] = dict
) -> Any:
    """Require HTTP 200, valid JSON, and the expected top-level shape."""
    status = getattr(response, "status_code", None)
    if status != 200:
        raise RuntimeError(f"{context}: unexpected HTTP status {status!r}")
    try:
        payload = response.json()
    except Exception as exc:
        raise RuntimeError(f"{context}: invalid JSON response") from exc
    if not isinstance(payload, expected_type):
        raise RuntimeError(f"{context}: invalid payload type {type(payload).__name__}")
    return payload


def collect_pages(
    fetch_page: Callable[[int], Any],
    *,
    key: str | None,
    context: str,
    page_size: int = 100,
) -> list[dict[str, Any]]:
    """Collect a complete page set, retrying boundedly when the API changes mid-scan."""
    last_drift: RuntimeError | None = None
    for attempt in range(3):
        try:
            return _collect_pages_once(
                fetch_page, key=key, context=context, page_size=page_size
            )
        except RuntimeError as exc:
            message = str(exc)
            if not any(
                marker in message
                for marker in (
                    "total_count changed during pagination",
                    "pagination exceeded total_count",
                    "incomplete pagination",
                )
            ):
                raise
            last_drift = exc
    raise RuntimeError(
        f"{context}: pagination did not stabilize after 3 complete-scan attempts; "
        f"last error: {last_drift}"
    ) from last_drift


def _collect_pages_once(
    fetch_page: Callable[[int], Any],
    *,
    key: str | None,
    context: str,
    page_size: int,
) -> list[dict[str, Any]]:
    """Perform one scan; a changing total_count invalidates the entire scan."""
    collected: list[dict[str, Any]] = []
    page = 1
    expected_total: int | None = None
    while True:
        payload = response_json(fetch_page(page), f"{context} page {page}", (dict, list))
        if isinstance(payload, list):
            items = payload
        else:
            items = payload.get(key) if key else None
            total = payload.get("total_count")
            if not isinstance(items, list):
                raise RuntimeError(f"{context} page {page}: missing list field {key!r}")
            if total is not None and (not isinstance(total, int) or total < 0):
                raise RuntimeError(f"{context} page {page}: invalid total_count")
            if total is not None:
                if expected_total is not None and total != expected_total:
                    raise RuntimeError(f"{context}: total_count changed during pagination")
                expected_total = total
        if any(not isinstance(item, dict) for item in items):
            raise RuntimeError(f"{context} page {page}: list contains non-object item")
        collected.extend(items)
        if expected_total is not None:
            if len(collected) >= expected_total:
                if len(collected) != expected_total:
                    raise RuntimeError(f"{context}: pagination exceeded total_count")
                break
        if len(items) < page_size:
            break
        page += 1
    if expected_total is not None and len(collected) != expected_total:
        raise RuntimeError(
            f"{context}: incomplete pagination, expected {expected_total}, got {len(collected)}"
        )
    return collected


def select_runs_for_sha(runs: list[dict[str, Any]], expected_sha: str) -> list[dict[str, Any]]:
    """Select only runs bound to the exact 40-character lowercase commit SHA."""
    if not isinstance(expected_sha, str) or not SHA40.fullmatch(expected_sha):
        raise RuntimeError("invalid expected commit SHA")
    selected = [run for run in runs if run.get("head_sha") == expected_sha]
    return selected


def validate_registry_counts(
    registry: dict[str, Any], implementation: dict[str, Any]
) -> dict[str, int]:
    """Require exact registry/matrix counts and unique, matching standard IDs."""
    registry_items = registry.get("standards")
    matrix_items = implementation.get("standards")
    if not isinstance(registry_items, list) or not isinstance(matrix_items, list):
        raise RuntimeError("registry or implementation matrix missing standards list")
    registry_ids = [item.get("id") for item in registry_items if isinstance(item, dict)]
    matrix_ids = [
        item.get("standard") or item.get("id") for item in matrix_items if isinstance(item, dict)
    ]
    if len(registry_ids) != len(registry_items) or any(not x for x in registry_ids):
        raise RuntimeError("registry contains malformed standard entries")
    if len(matrix_ids) != len(matrix_items) or any(not x for x in matrix_ids):
        raise RuntimeError("implementation matrix contains malformed entries")
    if len(set(registry_ids)) != len(registry_ids) or len(set(matrix_ids)) != len(matrix_ids):
        raise RuntimeError("duplicate standard IDs detected")
    missing = sorted(set(registry_ids) - set(matrix_ids))
    extra = sorted(set(matrix_ids) - set(registry_ids))
    if missing or extra:
        raise RuntimeError(f"registry/matrix ID mismatch: missing={missing[:5]}, extra={extra[:5]}")
    kpi = implementation.get("coverage_kpi")
    if not isinstance(kpi, dict):
        raise RuntimeError("implementation matrix missing coverage_kpi")
    actual = len(registry_ids)
    if kpi.get("registry_total") != actual or kpi.get("matrix_entries") != len(matrix_ids):
        raise RuntimeError(
            "registry KPI mismatch: "
            f"actual_registry={actual}, registry_total={kpi.get('registry_total')!r}, "
            f"actual_matrix={len(matrix_ids)}, matrix_entries={kpi.get('matrix_entries')!r}"
        )
    return {"registry_total": actual, "matrix_entries": len(matrix_ids)}


def validate_status_domains(readiness: str, agov: str, reconciliation: str) -> None:
    """Validate each domain independently; never coerce between status vocabularies."""
    if readiness not in READINESS_STATES:
        raise RuntimeError(f"invalid readiness status: {readiness!r}")
    if agov not in AGOV_STATES:
        raise RuntimeError(f"invalid AGOV status: {agov!r}")
    if reconciliation not in RECONCILIATION_STATES:
        raise RuntimeError(f"invalid reconciliation status: {reconciliation!r}")
