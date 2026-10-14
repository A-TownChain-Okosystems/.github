"""Independently verify GitHub Actions evidence against live GitHub REST API.

Input JSON schema: {"checked_commit_sha": "<40-char SHA>", "evidence": [
 {"repository":"owner/name","workflow_run_id":123,"head_sha":"...","job":"job name",
  "step":"step name","log_sha256":"<sha256 of downloaded job-log response bytes>"}]}
This verifies evidence claims only; it does not manufacture producer verdicts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from typing import Any

API = "https://api.github.com"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class Blocked(ValueError):
    """Evidence is absent, inconsistent, inaccessible, or incomplete."""


class GitHub:
    def __init__(self, token: str) -> None:
        if not token:
            raise Blocked("GITHUB_TOKEN is required")
        self.token = token

    def get(self, url: str) -> bytes:
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "atc-live-readiness-evidence-verifier",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise Blocked(f"GitHub evidence request failed: {url}: {exc}") from exc
        if not body:
            raise Blocked(f"empty GitHub response: {url}")
        return body

    def json(self, url: str) -> dict[str, Any]:
        try:
            value = json.loads(self.get(url))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise Blocked(f"invalid JSON response: {url}") from exc
        if not isinstance(value, dict):
            raise Blocked(f"expected JSON object: {url}")
        return value

    def all_pages(self, url: str, key: str) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        page = 1
        while True:
            separator = "&" if "?" in url else "?"
            payload = self.json(f"{url}{separator}per_page=100&page={page}")
            items = payload.get(key)
            if not isinstance(items, list) or any(not isinstance(x, dict) for x in items):
                raise Blocked(f"missing or malformed {key} page {page}: {url}")
            result.extend(items)
            total = payload.get("total_count")
            if total is not None and (not isinstance(total, int) or total < 0):
                raise Blocked(f"invalid total_count for {url}")
            if total is not None and len(result) >= total:
                if len(result) != total:
                    raise Blocked(f"pagination exceeded total_count for {url}")
                break
            if len(items) < 100:
                if total is not None and len(result) != total:
                    raise Blocked(
                        f"incomplete pagination for {url}: expected {total}, got {len(result)}"
                    )
                break
            page += 1
        if not result:
            raise Blocked(f"empty required API collection: {url}")
        return result

    def verify(self, item: dict[str, Any], checked_sha: str) -> dict[str, Any]:
        repo = item.get("repository")
        run_id = item.get("workflow_run_id")
        job_name, step_name = item.get("job"), item.get("step")
        if not isinstance(repo, str) or not re.fullmatch(r"[^/\s]+/[^/\s]+", repo):
            raise Blocked("repository must be owner/name")
        if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
            raise Blocked("workflow_run_id must be a positive integer")
        if item.get("head_sha") != checked_sha:
            raise Blocked("evidence SHA does not match checked SHA")
        if not isinstance(job_name, str) or not job_name.strip():
            raise Blocked("job name is required")
        if not isinstance(step_name, str) or not step_name.strip():
            raise Blocked("step name is required")
        expected_log_hash = item.get("log_sha256")
        if not isinstance(expected_log_hash, str) or not SHA256.fullmatch(expected_log_hash):
            raise Blocked("full log_sha256 is required")

        root = f"{API}/repos/{repo}/actions"
        run = self.json(f"{root}/runs/{run_id}")
        if run.get("id") != run_id or run.get("head_sha") != checked_sha:
            raise Blocked("run identity or exact head SHA mismatch")
        if run.get("status") != "completed" or run.get("conclusion") != "success":
            raise Blocked("workflow run is not completed successfully")

        jobs = self.all_pages(f"{root}/runs/{run_id}/jobs", "jobs")
        matches = [job for job in jobs if job.get("name") == job_name]
        if len(matches) != 1:
            raise Blocked("named job is missing or ambiguous")
        job = matches[0]
        if job.get("head_sha") not in (None, checked_sha):
            raise Blocked("job SHA mismatch")
        if job.get("status") != "completed" or job.get("conclusion") != "success":
            raise Blocked("named job did not succeed")
        steps = job.get("steps")
        if not isinstance(steps, list):
            raise Blocked("job step inventory is missing")
        step_matches = [
            step for step in steps if isinstance(step, dict) and step.get("name") == step_name
        ]
        if len(step_matches) != 1:
            raise Blocked("named step is missing or ambiguous")
        step = step_matches[0]
        if step.get("status") != "completed" or step.get("conclusion") != "success":
            raise Blocked("named step did not succeed")

        job_id = job.get("id")
        if not isinstance(job_id, int) or job_id <= 0:
            raise Blocked("job ID is missing")
        logs = self.get(f"{root}/jobs/{job_id}/logs")
        actual_hash = hashlib.sha256(logs).hexdigest()
        if not logs.strip() or actual_hash != expected_log_hash:
            raise Blocked("job logs are empty or SHA-256 does not match")

        return {
            "repository": repo,
            "workflow_run_id": run_id,
            "head_sha": checked_sha,
            "job_id": job_id,
            "job": job_name,
            "step": step_name,
            "run_conclusion": run["conclusion"],
            "step_conclusion": step["conclusion"],
            "log_sha256": actual_hash,
            "result": "VERIFIED",
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claim", required=True, help="JSON claim for one source domain")
    args = parser.parse_args(argv)
    try:
        with open(args.claim, encoding="utf-8") as handle:
            claim = json.load(handle)
        if not isinstance(claim, dict):
            raise Blocked("claim must be a JSON object")
        sha = claim.get("checked_commit_sha")
        if not isinstance(sha, str) or not SHA40.fullmatch(sha):
            raise Blocked("checked_commit_sha must be a full lowercase SHA")
        items = claim.get("evidence")
        if not isinstance(items, list) or not items:
            raise Blocked("claim evidence must be a non-empty list")
        verifier = GitHub(os.environ.get("GITHUB_TOKEN", ""))
        results = [verifier.verify(item, sha) for item in items]
    except (OSError, json.JSONDecodeError, Blocked) as exc:
        print(f"LIVE_EVIDENCE=BLOCKED: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {"checked_commit_sha": sha, "evidence": results, "status": "VERIFIED"}, sort_keys=True
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
