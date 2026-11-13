"""Fail-closed eligibility checks for recovering a tagged release's policy job."""

import copy
import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("release_recovery", Path(__file__).parents[1] / "check-release-recovery.py")
recovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recovery)


class ReleaseRecovery(unittest.TestCase):
    def setUp(self):
        self.commit = "a" * 40
        self.repository = "example/jong"
        self.tag = "v0.1.0"
        self.run = {
            "id": 123, "repository": {"full_name": self.repository},
            "head_repository": {"full_name": self.repository},
            "path": ".github/workflows/release.yml", "event": "push",
            "head_branch": self.tag, "head_sha": self.commit,
            "status": "completed", "conclusion": "failure",
        }
        self.jobs = [{"name": name, "status": "completed", "conclusion": "success"}
                     for name in recovery.SUCCESSFUL_JOBS]
        self.policy = {"name": recovery.POLICY, "status": "completed", "conclusion": "failure",
                       "steps": [{"name": "Install pinned policy tools", "conclusion": "failure"},
                                 *({"name": name, "conclusion": "skipped"} for name in recovery.POLICY_CHECKS)]}
        self.jobs.extend((self.policy, {"name": recovery.DRAFT, "status": "completed", "conclusion": "skipped"}))
        self.artifact = {"id": 456, "name": "release-bundle", "expired": False,
                         "size_in_bytes": 12345, "workflow_run": {"id": 123, "head_sha": self.commit}}
        self.artifacts = [self.artifact]

    def validate(self):
        return recovery.validate_run(self.run, self.jobs, self.artifacts, self.repository, self.tag, self.commit)

    def test_only_installation_failure_with_complete_original_evidence_is_eligible(self):
        self.assertEqual(self.validate(), 456)

    def test_selective_release_requires_every_workload_and_failed_aggregate(self):
        self.jobs = [{"name": name, "status": "completed", "conclusion": "success"}
                     for name in recovery.SELECTIVE_JOBS]
        gate = {"name": recovery.GATE, "status": "completed", "conclusion": "failure"}
        self.jobs.extend((self.policy, gate,
                          {"name": recovery.DRAFT, "status": "completed", "conclusion": "skipped"}))
        self.assertEqual(self.validate(), 456)
        for job in self.jobs:
            original = job["conclusion"]
            for conclusion in ("failure", "cancelled", "skipped", "success", None):
                if conclusion == original:
                    continue
                job["conclusion"] = conclusion
                with self.subTest(job=job["name"], conclusion=conclusion), self.assertRaises(ValueError):
                    self.validate()
            job["conclusion"] = original

    def test_wrong_repository_tag_commit_workflow_event_or_incomplete_run_rejected(self):
        for key, value in (
            ("repository", {"full_name": "foreign/jong"}),
            ("head_repository", {"full_name": "foreign/jong"}),
            ("head_branch", "main"), ("head_sha", "b" * 40),
            ("path", ".github/workflows/ci.yml"), ("event", "pull_request"),
            ("status", "in_progress"), ("conclusion", "success"),
        ):
            with self.subTest(key=key):
                original = self.run[key]
                self.run[key] = value
                with self.assertRaises(ValueError):
                    self.validate()
                self.run[key] = original

    def test_any_unsuccessful_original_gate_blocks_recovery(self):
        for job in self.jobs:
            if job["name"] not in recovery.SUCCESSFUL_JOBS:
                continue
            for conclusion in ("failure", "cancelled", "skipped", None):
                with self.subTest(name=job["name"], conclusion=conclusion):
                    job["conclusion"] = conclusion
                    with self.assertRaises(ValueError):
                        self.validate()
            job["conclusion"] = "success"

    def test_missing_duplicate_or_unexpected_jobs_rejected(self):
        original = copy.deepcopy(self.jobs)
        for jobs in (original[:-1], original + [original[0]],
                     [dict(original[0], name="unrecognized gate"), *original[1:]]):
            self.jobs = jobs
            with self.assertRaises(ValueError):
                self.validate()

    def test_policy_violations_and_partial_draft_cannot_be_recovered(self):
        steps = copy.deepcopy(self.policy["steps"])
        for check in recovery.POLICY_CHECKS:
            self.policy["steps"] = [{"name": "Install pinned policy tools", "conclusion": "success"},
                                    {"name": check, "conclusion": "failure"}]
            with self.subTest(check=check), self.assertRaises(ValueError):
                self.validate()
        self.policy["steps"] = steps
        self.jobs[-1]["conclusion"] = "failure"
        with self.assertRaises(ValueError):
            self.validate()

    def test_missing_expired_duplicate_empty_or_foreign_bundle_rejected(self):
        for key, value in (("expired", True), ("size_in_bytes", 0),
                           ("workflow_run", {"id": 789, "head_sha": self.commit}),
                           ("workflow_run", {"id": 123, "head_sha": "b" * 40})):
            original = self.artifact[key]
            self.artifact[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.validate()
            self.artifact[key] = original
        for artifacts in ([], [self.artifact, self.artifact]):
            self.artifacts = artifacts
            with self.assertRaises(ValueError):
                self.validate()

    def check_with_api(self, api):
        self.run["run_attempt"] = 5
        with patch.object(recovery.subprocess, "check_output", return_value=self.commit + "\n"), \
                patch.object(recovery.subprocess, "run"), patch.object(recovery, "api", side_effect=api):
            return recovery.check(Path("source"), self.repository, self.tag, "123")

    def test_api_failure_cannot_be_treated_as_missing_evidence(self):
        for index in range(4):
            responses = [self.run, [{"jobs": self.jobs}], [{"artifacts": self.artifacts}], self.run]
            responses[index] = subprocess.CalledProcessError(1, "gh api")
            with self.subTest(index=index), self.assertRaises(subprocess.CalledProcessError):
                self.check_with_api(responses)

    def test_new_retry_during_verification_rejected(self):
        changed = dict(self.run, run_attempt=6, status="in_progress")
        with self.assertRaisesRegex(ValueError, "changed during verification"):
            self.check_with_api([self.run, [{"jobs": self.jobs}], [{"artifacts": self.artifacts}], changed])

    def test_checks_all_job_pages_and_returns_exact_bundle_identity(self):
        responses = [self.run, [{"jobs": self.jobs[:3]}, {"jobs": self.jobs[3:]}],
                     [{"artifacts": []}, {"artifacts": self.artifacts}], self.run]
        self.assertEqual(self.check_with_api(responses), (self.commit, 456, 5))

    def test_invalid_inputs_never_access_git_or_github(self):
        for repository, tag, run_id in (("../bad", self.tag, "123"),
                                        (self.repository, "main", "123"),
                                        (self.repository, "v0.1.0\ncommit=bad", "123"),
                                        (self.repository, self.tag, "123?extra=true")):
            with patch.object(recovery.subprocess, "check_output") as command:
                with self.assertRaises(ValueError):
                    recovery.check(Path("source"), repository, tag, run_id)
                command.assert_not_called()


if __name__ == "__main__":
    unittest.main()
