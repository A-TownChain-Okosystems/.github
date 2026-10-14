"""Negative tests for fail-closed readiness evidence validation."""
import unittest

from tools.readiness_contract import (
    collect_pages,
    response_json,
    select_runs_for_sha,
    validate_registry_counts,
    validate_status_domains,
)


class FakeResponse:
    def __init__(self, status_code=200, payload=None, error=None):
        self.status_code = status_code
        self.payload = payload
        self.error = error

    def json(self):
        if self.error:
            raise self.error
        return self.payload


class ReadinessContractTests(unittest.TestCase):
    def test_http_error_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "HTTP status 403"):
            response_json(FakeResponse(403, {"message": "forbidden"}), "registry")

    def test_malformed_json_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "invalid JSON"):
            response_json(FakeResponse(200, error=ValueError("bad json")), "registry")

    def test_wrong_payload_shape_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "invalid payload type"):
            response_json(FakeResponse(200, ["not", "an", "object"]), "registry")

    def test_pagination_collects_all_pages(self):
        pages = {
            1: FakeResponse(200, {"total_count": 3, "items": [{"id": 1}, {"id": 2}]}),
            2: FakeResponse(200, {"total_count": 3, "items": [{"id": 3}]}),
        }
        items = collect_pages(lambda page: pages[page], key="items", context="test", page_size=2)
        self.assertEqual([item["id"] for item in items], [1, 2, 3])

    def test_incomplete_pagination_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "incomplete pagination"):
            collect_pages(
                lambda page: FakeResponse(200, {"total_count": 3, "items": [{"id": 1}]}),
                key="items",
                context="test",
                page_size=2,
            )

    def test_total_count_drift_fails_closed(self):
        pages = {
            1: FakeResponse(200, {"total_count": 3, "items": [{"id": 1}, {"id": 2}]}),
            2: FakeResponse(200, {"total_count": 4, "items": [{"id": 3}, {"id": 4}]}),
        }
        with self.assertRaisesRegex(RuntimeError, "total_count changed"):
            collect_pages(lambda page: pages[page], key="items", context="test", page_size=2)

    def test_stale_sha_runs_are_excluded(self):
        expected = "a" * 40
        runs = [
            {"id": 1, "head_sha": expected},
            {"id": 2, "head_sha": "b" * 40},
            {"id": 3},
        ]
        self.assertEqual([run["id"] for run in select_runs_for_sha(runs, expected)], [1])

    def test_malformed_expected_sha_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "invalid expected commit SHA"):
            select_runs_for_sha([], "main")

    def test_registry_count_mismatch_fails_closed(self):
        registry = {"standards": [{"id": "S-1"}, {"id": "S-2"}]}
        matrix = {
            "standards": [{"standard": "S-1"}, {"standard": "S-2"}],
            "coverage_kpi": {"registry_total": 1, "matrix_entries": 2},
        }
        with self.assertRaisesRegex(RuntimeError, "registry KPI mismatch"):
            validate_registry_counts(registry, matrix)

    def test_registry_matrix_id_mismatch_fails_closed(self):
        registry = {"standards": [{"id": "S-1"}, {"id": "S-2"}]}
        matrix = {
            "standards": [{"standard": "S-1"}, {"standard": "S-3"}],
            "coverage_kpi": {"registry_total": 2, "matrix_entries": 2},
        }
        with self.assertRaisesRegex(RuntimeError, "ID mismatch"):
            validate_registry_counts(registry, matrix)

    def test_status_domains_remain_separate(self):
        validate_status_domains("NO-GO", "FAIL", "DETECTED")
        with self.assertRaisesRegex(RuntimeError, "invalid reconciliation"):
            validate_status_domains("NO-GO", "FAIL", "NO-GO")


if __name__ == "__main__":
    unittest.main()
