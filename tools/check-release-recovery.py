#!/usr/bin/env python3
"""Permit policy-only recovery of a failed, otherwise successful tagged release."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys


SUCCESSFUL_JOBS = {
    "Validate release tag",
    *("Release checks / " + name for name in (
        "Reproducible x86-64 release payload", "Native package lifecycle (deb)",
        "Native package lifecycle (rpm)", "Native package lifecycle (arch)",
        "Assemble verified release artifacts", "Documentation and release tooling",
        "Rust and Fcitx5", "Native sanitizers and release Memcheck")),
}
POLICY = "Release checks / Dependency and privacy policy"
DRAFT = "Prepare complete release draft"
POLICY_CHECKS = {
    "Check policy tools and deliberate violations",
    "Check all workspace dependency licenses, bans and sources",
    "Audit locked dependencies against current RustSec advisories",
}


def validate_run(run, jobs, artifacts, repository, tag, commit):
    if (run["repository"]["full_name"] != repository
            or run["head_repository"]["full_name"] != repository
            or run["path"] != ".github/workflows/release.yml"
            or run["event"] != "push" or run["head_branch"] != tag
            or run["head_sha"] != commit or run["status"] != "completed"
            or run["conclusion"] != "failure"):
        raise ValueError("source run must be the failed tagged release in this repository")
    expected = SUCCESSFUL_JOBS | {POLICY, DRAFT}
    if len(jobs) != len(expected) or {job["name"] for job in jobs} != expected:
        raise ValueError("source run has missing, duplicate or unexpected jobs")
    for job in jobs:
        conclusion = "success" if job["name"] in SUCCESSFUL_JOBS else (
            "failure" if job["name"] == POLICY else "skipped")
        if job["status"] != "completed" or job["conclusion"] != conclusion:
            raise ValueError(f"ineligible source job: {job['name']}")
        if job["name"] == POLICY:
            failed = [step["name"] for step in job["steps"] if step["conclusion"] == "failure"]
            skipped = [step["name"] for step in job["steps"] if step["conclusion"] == "skipped"]
            if failed != ["Install pinned policy tools"] or not POLICY_CHECKS.issubset(skipped):
                raise ValueError("only a policy-tool installation failure can be recovered")
    bundles = [asset for asset in artifacts if asset["name"] == "release-bundle"]
    if (len(bundles) != 1 or bundles[0]["expired"] is not False
            or bundles[0]["size_in_bytes"] <= 0
            or bundles[0]["workflow_run"]["id"] != run["id"]
            or bundles[0]["workflow_run"]["head_sha"] != commit):
        raise ValueError("source run requires one unexpired matching release bundle")
    return bundles[0]["id"]


def api(endpoint, paginate=False):
    flags = ["--paginate", "--slurp"] if paginate else []
    return json.loads(subprocess.check_output(["gh", "api", *flags, endpoint], text=True))


def check(source, repository, tag, run_id):
    if (not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+", repository)
            or repository.split("/")[-1] in (".", "..")):
        raise ValueError("repository must be OWNER/NAME")
    if not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+(?:-(?:alpha|beta|rc)\.[1-9][0-9]*)?", tag):
        raise ValueError("expected a semantic release tag")
    if not re.fullmatch(r"[1-9][0-9]*", run_id):
        raise ValueError("source run ID must be a positive integer")

    def git(*args):
        return subprocess.check_output(["git", "-C", str(source), *args], text=True).strip()

    commit = git("rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}")
    if commit != git("rev-parse", "HEAD^{commit}"):
        raise ValueError("source checkout must match the existing release tag")
    subprocess.run(["git", "-C", str(source), "merge-base", "--is-ancestor", commit, "origin/main"], check=True)
    subprocess.run([sys.executable, "tools/check-release.py", tag], cwd=source, check=True)
    endpoint = f"repos/{repository}/actions/runs/{run_id}"
    run = api(endpoint)
    if run["id"] != int(run_id):
        raise ValueError("source run ID mismatch")
    pages = api(f"{endpoint}/attempts/{run['run_attempt']}/jobs?per_page=100", paginate=True)
    jobs = [job for page in pages for job in page["jobs"]]
    pages = api(f"{endpoint}/artifacts?per_page=100", paginate=True)
    artifacts = [asset for page in pages for asset in page["artifacts"]]
    artifact_id = validate_run(run, jobs, artifacts, repository, tag, commit)
    # Fail closed if a retry started while evidence was being collected.
    if api(endpoint) != run:
        raise ValueError("source run changed during verification; inspect before retrying")
    return commit, artifact_id, run["run_attempt"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    parser.add_argument("--run", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    try:
        commit, artifact_id, attempt = check(args.source.resolve(), args.repo, args.tag, args.run)
        if args.github_output:
            with args.github_output.open("a") as output:
                output.write(f"commit={commit}\nartifact_id={artifact_id}\n")
        print(f"PASS: run {args.run} attempt {attempt}, {args.tag}, {commit}, bundle {artifact_id}")
        print("Original non-policy gates passed; fresh tagged-source policy checks are still required.")
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        sys.exit(f"FAIL: {error}")


if __name__ == "__main__":
    main()
