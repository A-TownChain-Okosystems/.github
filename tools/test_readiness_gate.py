"""Negative and positive contract tests for the live readiness consumer."""

import unittest

from tools.readiness_gate import GateBlocked, evaluate

GATE_SHA = "d" * 40
READINESS_SHA = "a" * 40
AGOV_SHA = "b" * 40
RECONCILIATION_SHA = "c" * 40
HASH = "e" * 64


def evidence(repository, source_sha):
    return [
        {
            "repository": repository,
            "workflow_run_id": 123,
            "head_sha": source_sha,
            "job": "quality",
            "step": "Readiness producer",
            "log_sha256": HASH,
            "status": "success",
        }
    ]


def valid_bundle():
    return {
        "schema_version": 1,
        "checked_commit_sha": GATE_SHA,
        "sources": {
            "readiness": {
                "status": "PREP",
                "repository": "A-TownChain-Okosystems/.github",
                "source_commit_sha": READINESS_SHA,
                "evidence": evidence("A-TownChain-Okosystems/.github", READINESS_SHA),
            },
            "agov": {
                "status": "PASS",
                "repository": "A-TownChain-Okosystems/.github",
                "source_commit_sha": AGOV_SHA,
                "evidence": evidence("A-TownChain-Okosystems/.github", AGOV_SHA),
            },
            "reconciliation": {
                "status": "VERIFIED",
                "repository": "A-TownChain-Okosystems/atc-engineering",
                "source_commit_sha": RECONCILIATION_SHA,
                "evidence": evidence("A-TownChain-Okosystems/atc-engineering", RECONCILIATION_SHA),
            },
        },
        "consumers": {"merge-gate": {"status": "EXECUTED", "checked_commit_sha": GATE_SHA}},
    }


class ReadinessGateTests(unittest.TestCase):
    def test_complete_bundle_preserves_domains_and_passes(self):
        verdict = evaluate(valid_bundle())
        self.assertEqual(verdict["decision"], "PASS")
        self.assertEqual(verdict["status"], "PREP")
        self.assertEqual(
            verdict["source_statuses"],
            {"readiness": "PREP", "agov": "PASS", "reconciliation": "VERIFIED"},
        )

    def test_missing_reconciliation_evidence_blocks(self):
        bundle = valid_bundle()
        bundle["sources"]["reconciliation"]["evidence"] = []
        with self.assertRaisesRegex(GateBlocked, "non-empty list"):
            evaluate(bundle)

    def test_unknown_consumer_blocks(self):
        bundle = valid_bundle()
        bundle["consumers"]["unknown-consumer"] = {"status": "EXECUTED"}
        with self.assertRaisesRegex(GateBlocked, "consumer coverage mismatch"):
            evaluate(bundle)

    def test_uncovered_source_blocks(self):
        bundle = valid_bundle()
        del bundle["sources"]["agov"]
        with self.assertRaisesRegex(GateBlocked, "source coverage mismatch"):
            evaluate(bundle)

    def test_sha_mismatch_blocks(self):
        bundle = valid_bundle()
        bundle["sources"]["agov"]["evidence"][0]["head_sha"] = "f" * 40
        with self.assertRaisesRegex(GateBlocked, "evidence SHA mismatch"):
            evaluate(bundle)

    def test_source_commit_sha_must_be_full_and_explicit(self):
        bundle = valid_bundle()
        bundle["sources"]["agov"]["source_commit_sha"] = "b" * 12
        with self.assertRaisesRegex(GateBlocked, "full lowercase 40-character"):
            evaluate(bundle)

    def test_evidence_repository_must_match_source_repository(self):
        bundle = valid_bundle()
        bundle["sources"]["reconciliation"]["evidence"][0]["repository"] = "attacker/other"
        with self.assertRaisesRegex(GateBlocked, "evidence repository mismatch"):
            evaluate(bundle)

    def test_empty_api_evidence_blocks(self):
        bundle = valid_bundle()
        bundle["sources"]["readiness"]["evidence"] = []
        with self.assertRaisesRegex(GateBlocked, "non-empty list"):
            evaluate(bundle)

    def test_unknown_status_domain_value_blocks(self):
        bundle = valid_bundle()
        bundle["sources"]["agov"]["status"] = "VERIFIED"
        with self.assertRaisesRegex(GateBlocked, "invalid AGOV status"):
            evaluate(bundle)

    def test_readiness_no_go_blocks_without_status_promotion(self):
        bundle = valid_bundle()
        bundle["sources"]["readiness"]["status"] = "NO-GO"
        with self.assertRaisesRegex(GateBlocked, "readiness is NO-GO"):
            evaluate(bundle)

    def test_agov_warning_blocks(self):
        bundle = valid_bundle()
        bundle["sources"]["agov"]["status"] = "WARN"
        with self.assertRaisesRegex(GateBlocked, "AGOV is WARN"):
            evaluate(bundle)

    def test_reconciliation_detected_does_not_become_verified(self):
        bundle = valid_bundle()
        bundle["sources"]["reconciliation"]["status"] = "DETECTED"
        with self.assertRaisesRegex(GateBlocked, "reconciliation is DETECTED"):
            evaluate(bundle)

    def test_merge_gate_must_be_executed_for_same_sha(self):
        bundle = valid_bundle()
        bundle["consumers"]["merge-gate"]["status"] = "DECLARED"
        with self.assertRaisesRegex(GateBlocked, "was not executed"):
            evaluate(bundle)

    def test_missing_log_hash_blocks(self):
        bundle = valid_bundle()
        del bundle["sources"]["agov"]["evidence"][0]["log_sha256"]
        with self.assertRaisesRegex(GateBlocked, "log_sha256"):
            evaluate(bundle)


if __name__ == "__main__":
    unittest.main()
