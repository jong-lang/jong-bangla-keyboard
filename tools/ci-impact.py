#!/usr/bin/env python3
"""Select CI by PR impact and reject unsuccessful applicable job results."""

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import unittest


FORMATS = ("deb", "rpm", "arch")
CHECKS = ("native", "policy", "memory", "performance", "release_native", "bundle", "lint")
# Related regressions run together when helpers share packaging/release inputs.
RELEASE_TESTS = {"test_release_tools.py", "test_release_artifacts.py", "test_release_recovery.py"}
PACKAGE_TESTS = {"test_packages.py", "test_icons.py", "test_release_artifacts.py"}
TOOL_TESTS = {
    "check-docs.py": set(),
    "ci-impact.py": {"test_ci_impact.py"},
    "check-install.py": {"test_icons.py"},
    "check-memory.py": {"test_memory.py"},
    "valgrind-rust-tests.supp": {"test_memory.py"},
    "check-privacy.py": {"test_privacy.py"},
    "install-policy-tools.py": {"test_policy_tools.py"},
    "check-release.py": RELEASE_TESTS,
    "check-release-recovery.py": RELEASE_TESTS,
    "draft-release.py": RELEASE_TESTS,
    "assemble-release.py": RELEASE_TESTS | PACKAGE_TESTS,
    "build-release.py": RELEASE_TESTS | PACKAGE_TESTS,
    "copy-rust-notices.py": RELEASE_TESTS,
    "build-packages.py": PACKAGE_TESTS,
    "check-packages.py": PACKAGE_TESTS,
    "check-package-install.py": PACKAGE_TESTS,
    "package_bundle.py": PACKAGE_TESTS,
    "icon_payload.py": PACKAGE_TESTS,
    "measure-baseline.py": {"test_performance.py"},
    "measure-adapter.py": {"test_performance.py"},
}


def plan(paths=(), full_reason=None):
    selected = set()
    formats = set()
    tests = set()
    reasons = []
    all_tools = False

    def broad(reason):
        nonlocal all_tools
        selected.update(CHECKS)
        formats.update(FORMATS)
        all_tools = True
        reasons.append(reason)

    def payload(reason):
        selected.update(("native", "policy", "memory", "performance", "release_native"))
        formats.update(FORMATS)
        reasons.append(reason)

    paths = list(paths)
    if full_reason:
        broad(full_reason)
    elif not paths:
        broad("No changed paths available")
    else:
        for path in paths:
            parts = PurePosixPath(path).parts
            if (not parts or path.startswith("/") or ".." in parts
                    or any(ord(char) < 32 for char in path)):
                broad("Unrecognized path encoding")
            elif (path.startswith(".github/workflows/")
                  or path in ("Cargo.toml", "Cargo.lock", "adapters/fcitx5/ffi/Cargo.toml",
                              "adapters/fcitx5/CMakeLists.txt", "tools/check-build.sh", "tools/ci-impact.py",
                              "tools/tests/test_ci_impact.py")
                  or parts[0] in (".cargo", "rust-toolchain", "rust-toolchain.toml")):
                broad(f"Workflow/build/toolchain input: {path}")
            elif (path.startswith("src/") or path.startswith("adapters/fcitx5/")
                  and not path.startswith("adapters/fcitx5/tests/")):
                payload(f"Runtime payload: {path}")
            elif path.startswith("adapters/fcitx5/tests/"):
                selected.update(("native", "memory", "performance"))
                reasons.append(f"Native harness: {path}")
            elif path.startswith("tests/") or path.startswith("examples/"):
                selected.add("native")
                if path in ("examples/measure.rs",):
                    selected.add("performance")
                reasons.append(f"Rust tests/examples: {path}")
            elif path.startswith("packaging/"):
                mapping = {"debian": "deb", "fedora": "rpm", "arch": "arch"}
                if len(parts) < 3 or parts[1] not in mapping:
                    broad(f"Unknown package input: {path}")
                else:
                    formats.add(mapping[parts[1]])
                    selected.add("release_native")
                    tests.update(PACKAGE_TESTS)
                    reasons.append(f"Package recipe: {path}")
            elif path.startswith("assets/"):
                selected.update(("native", "release_native"))
                formats.update(FORMATS)
                tests.update(PACKAGE_TESTS)
                reasons.append(f"Installed/branding assets: {path}")
            elif path in ("deny.toml", "SECURITY.md"):
                selected.add("policy")
                tests.update(("test_dependency_policy.py", "test_privacy.py", "test_policy_tools.py"))
                reasons.append(f"Policy input: {path}")
            elif path.startswith("tools/tests/"):
                name = parts[-1]
                known = set().union(*TOOL_TESTS.values(), {"test_dependency_policy.py"})
                if len(parts) != 3 or name not in known:
                    broad(f"Unknown tool regression: {path}")
                else:
                    tests.add(name)
                    reasons.append(f"Tool regression: {path}")
            elif path.startswith("tools/") and len(parts) == 2 and parts[1] in TOOL_TESTS:
                name = parts[1]
                tests.update(TOOL_TESTS[name])
                if name in ("check-memory.py", "valgrind-rust-tests.supp"):
                    selected.add("memory")
                elif name in ("check-privacy.py", "install-policy-tools.py"):
                    selected.add("policy")
                elif name in ("measure-baseline.py", "measure-adapter.py"):
                    selected.add("performance")
                elif name == "check-install.py":
                    selected.add("native")
                elif name in ("build-release.py", "assemble-release.py", "copy-rust-notices.py",
                              "build-packages.py", "check-packages.py", "check-package-install.py",
                              "package_bundle.py", "icon_payload.py"):
                    selected.add("release_native")
                    formats.update(FORMATS)
                reasons.append(f"Tool implementation: {path}")
            elif (path in ("LICENSE", "THIRD_PARTY_NOTICES")):
                selected.update(("policy", "release_native"))
                formats.update(FORMATS)
                reasons.append(f"Redistribution input: {path}")
            elif (path in ("AGENTS.md", "README.md", "CLAUDE.md", "CONTRIBUTING.md",
                           "CODE_OF_CONDUCT.md", "CHANGELOG.md")
                  or path.startswith("docs/") and Path(path).suffix in (".md", ".json", ".csv")
                  or path.startswith(".github/ISSUE_TEMPLATE/") and path.endswith(".md")
                  or path == ".github/pull_request_template.md"):
                reasons.append(f"Documentation: {path}")
            else:
                broad(f"Unknown input: {path}")

    if "performance" in selected:
        selected.add("native")
    if formats:
        selected.add("release_native")
    if formats == set(FORMATS):
        selected.add("bundle")
    # Detector/dependency regressions must run with their real tools installed.
    if "test_dependency_policy.py" in tests or "test_privacy.py" in tests:
        selected.add("policy")
    if "test_memory.py" in tests:
        selected.add("memory")
    if all_tools:
        tests = {path.name for path in Path("tools/tests").glob("test_*.py")}
    if "policy" in selected:
        tests.difference_update(("test_dependency_policy.py", "test_privacy.py"))
    if "memory" in selected:
        tests.discard("test_memory.py")
    return {**{check: check in selected for check in CHECKS},
            "formats": [fmt for fmt in FORMATS if fmt in formats],
            "tests": sorted(tests), "tools": bool(tests), "reasons": reasons}


def event_plan(event_name, event):
    if event_name != "pull_request":
        return plan(full_reason=f"Full integration/release validation: {event_name}")
    try:
        base = event["pull_request"]["base"]["sha"]
        head = event["pull_request"]["head"]["sha"]
        if not all(isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{40}", sha) for sha in (base, head)):
            raise ValueError("invalid PR commit identities")
        ancestor = subprocess.check_output(["git", "merge-base", base, head], text=True).strip()
        data = subprocess.check_output(["git", "diff", "--name-only", "--no-renames", "-z", ancestor, head])
        paths = data.decode("utf-8").split("\0")
        if paths[-1] != "":
            raise ValueError("unterminated Git path list")
        return plan(paths[:-1])
    except Exception as error:
        # Routing failures, including unexpected classifier bugs, must increase
        # validation rather than leave needed jobs intentionally unselected.
        return plan(full_reason=f"Classification unavailable: {error}")


def gate(selection, needs):
    """Only explicitly non-applicable jobs may be skipped; all others must pass."""
    expected = {"impact": True, "docs": True, "tools": selection["tools"],
                "native": selection["native"], "policy": selection["policy"],
                "memory": selection["memory"], "release-native": selection["release_native"],
                "packages": bool(selection["formats"]), "release-bundle": selection["bundle"],
                "lint": selection["lint"]}
    if set(needs) != set(expected):
        raise ValueError("gate dependencies differ from the complete job inventory")
    for job, applicable in expected.items():
        result = needs[job]["result"]
        if result != ("success" if applicable else "skipped"):
            raise ValueError(f"{job}: {result}; expected {'success' if applicable else 'skipped'}")
    return expected


def run_tests(selection):
    # Match `python3 -m unittest` so regressions can import the tools namespace.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    suite = unittest.TestSuite()
    for name in selection["tests"]:
        selected = unittest.defaultTestLoader.discover("tools/tests", pattern=name)
        if not selected.countTestCases():
            raise ValueError(f"selected regression suite is missing or empty: {name}")
        suite.addTests(selected)
    return unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "gate", "test"))
    args = parser.parse_args()
    if args.command == "plan":
        try:
            event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
            selection = event_plan(os.environ["GITHUB_EVENT_NAME"], event)
        except (OSError, ValueError, KeyError, TypeError) as error:
            selection = plan(full_reason=f"Event unavailable: {error}")
        with open(os.environ["GITHUB_OUTPUT"], "a") as output:
            output.write("plan=" + json.dumps(selection, separators=(",", ":")) + "\n")
        summary = "## CI selection\n\nDocumentation checks always run.\n\n"
        summary += "```json\n" + json.dumps(selection, indent=2) + "\n```\n"
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as output:
            output.write(summary)
        print(summary)
    else:
        selection = json.loads(os.environ["CI_PLAN"])
        if args.command == "test":
            if not run_tests(selection):
                sys.exit(1)
        else:
            needs = json.loads(os.environ["CI_NEEDS"])
            summary = "## CI results\n\n| Check | Result |\n| --- | --- |\n"
            summary += "".join(f"| {job} | {value['result']} |\n" for job, value in needs.items())
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as output:
                output.write(summary)
            print(summary)
            gate(selection, needs)


if __name__ == "__main__":
    main()
