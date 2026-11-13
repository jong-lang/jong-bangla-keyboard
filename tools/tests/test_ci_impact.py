"""CI selection boundaries, real Git diffs and required-gate failure handling."""

import copy
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'tools/ci-impact.py'
spec = importlib.util.spec_from_file_location('ci_impact', SCRIPT)
impact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(impact)


class Selection(unittest.TestCase):
    def test_documentation_only_has_no_heavy_jobs_or_tool_regressions(self):
        selection = impact.plan(['README.md', 'docs/TESTING.md', 'CHANGELOG.md'])
        self.assertFalse(any(selection[key] for key in impact.CHECKS))
        self.assertEqual(selection['formats'], [])
        self.assertEqual(selection['tests'], [])

    def test_unknown_workflow_toolchain_and_empty_inputs_are_broad(self):
        for path in ('new-file', 'new-guide.md', 'tools/new-helper.py', 'docs/new-script.py',
                     'packaging/new-distro/recipe', '.github/workflows/ci.yml',
                     '.github/workflows/release.yml', '.cargo/config.toml', 'Cargo.lock',
                     'rust-toolchain.toml', 'tools/ci-impact.py', 'tools/check-build.sh',
                     'adapters/fcitx5/CMakeLists.txt', '../README.md', 'odd\nname'):
            with self.subTest(path=path):
                self.assert_broad(impact.plan([path]))
        self.assert_broad(impact.plan([]))

    def assert_broad(self, selection):
        self.assertTrue(all(selection[key] for key in impact.CHECKS))
        self.assertEqual(selection['formats'], list(impact.FORMATS))
        # No supported tool regression disappears in full runs; detector-dependent
        # suites execute in jobs which install their required tools.
        suites = set(selection['tests']) | {'test_memory.py', 'test_dependency_policy.py', 'test_privacy.py'}
        self.assertEqual(suites, {p.name for p in (ROOT / 'tools/tests').glob('test_*.py')})

    def test_runtime_changes_cover_artifacts_memory_policy_and_performance(self):
        for path in ('src/composition.rs', 'src/transliteration/rules.rs',
                     'adapters/fcitx5/addon.cpp', 'adapters/fcitx5/ffi/src/lib.rs'):
            with self.subTest(path=path):
                selected = impact.plan([path])
                self.assertTrue(all(selected[key] for key in impact.CHECKS if key != 'lint'))
                self.assertEqual(selected['formats'], list(impact.FORMATS))

    def test_package_formats_and_combined_changes_form_a_union(self):
        for directory, fmt in (('debian', 'deb'), ('fedora', 'rpm'), ('arch', 'arch')):
            selected = impact.plan([f'packaging/{directory}/recipe', 'README.md'])
            self.assertEqual(selected['formats'], [fmt])
            self.assertTrue(selected['release_native'])
            self.assertFalse(selected['bundle'])
            self.assertFalse(selected['memory'])
            self.assertIn('test_packages.py', selected['tests'])
        combined = impact.plan(['packaging/debian/control', 'packaging/arch/PKGBUILD', 'deny.toml'])
        self.assertEqual(combined['formats'], ['deb', 'arch'])
        self.assertTrue(combined['policy'])
        self.assertFalse(combined['memory'])

    def test_tool_regressions_are_targeted_without_duplicate_detector_runs(self):
        selected = impact.plan(['tools/check-release.py'])
        self.assertEqual(set(selected['tests']), impact.RELEASE_TESTS)
        self.assertFalse(selected['native'])
        selected = impact.plan(['tools/check-memory.py', 'tools/check-privacy.py'])
        self.assertTrue(selected['memory'])
        self.assertTrue(selected['policy'])
        self.assertNotIn('test_memory.py', selected['tests'])
        self.assertNotIn('test_privacy.py', selected['tests'])
        for name, key in (('test_memory.py', 'memory'), ('test_dependency_policy.py', 'policy')):
            self.assertTrue(impact.plan([f'tools/tests/{name}'])[key])

    def test_test_only_and_performance_inputs(self):
        selected = impact.plan(['tests/conversion.rs'])
        self.assertTrue(selected['native'])
        self.assertFalse(selected['release_native'])
        selected = impact.plan(['adapters/fcitx5/tests/harness.cpp'])
        self.assertTrue(selected['memory'])
        selected = impact.plan(['tools/measure-baseline.py'])
        self.assertTrue(selected['performance'])
        self.assertTrue(selected['native'])
        self.assertFalse(selected['memory'])

    def test_main_and_reusable_release_calls_always_run_full_suite(self):
        for event in ('push', 'workflow_call', 'workflow_dispatch', 'unrecognized'):
            with self.subTest(event=event):
                self.assert_broad(impact.event_plan(event, {}))

    def test_missing_invalid_or_unavailable_diff_selects_full_suite(self):
        for event in ({}, {'pull_request': None}, {'pull_request': {'base': {'sha': 'oops'}}}):
            self.assert_broad(impact.event_plan('pull_request', event))
        event = {'pull_request': {'base': {'sha': 'a' * 40}, 'head': {'sha': 'b' * 40}}}
        for error in (OSError('missing Git'), subprocess.CalledProcessError(1, 'git'),
                      UnicodeError('bad path'), RuntimeError('unexpected classifier failure')):
            with patch.object(impact.subprocess, 'check_output', side_effect=error):
                self.assert_broad(impact.event_plan('pull_request', event))

    def test_real_git_rename_deletion_and_large_diff_keep_runtime_impact(self):
        with tempfile.TemporaryDirectory() as directory:
            def git(*args):
                return subprocess.check_output(['git', '-C', directory, *args], text=True).strip()
            git('init', '-q')
            git('config', 'user.name', 'Synthetic Test')
            git('config', 'user.email', 'synthetic@example.invalid')
            root = Path(directory)
            (root / 'src').mkdir()
            (root / 'src/lib.rs').write_text('synthetic payload')
            git('add', '.')
            git('commit', '-qm', 'base')
            base = git('rev-parse', 'HEAD')
            (root / 'src/lib.rs').rename(root / 'README.md')
            for index in range(350):
                (root / f'doc-{index}.md').write_text('synthetic')
            git('add', '-A')
            git('commit', '-qm', 'rename and many files')
            head = git('rev-parse', 'HEAD')
            event = {'pull_request': {'base': {'sha': base}, 'head': {'sha': head}}}
            original = impact.subprocess.check_output
            with patch.object(impact.subprocess, 'check_output',
                              side_effect=lambda args, **kw: original(['git', '-C', directory, *args[1:]], **kw)):
                selected = impact.event_plan('pull_request', event)
            self.assertTrue(any('src/lib.rs' in reason for reason in selected['reasons']))
            self.assertTrue(selected['memory'])
            self.assertTrue(selected['release_native'])

    def test_cli_malformed_event_emits_full_plan_and_reason(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'event').write_text('{bad json')
            env = dict(os.environ, GITHUB_EVENT_PATH=str(root / 'event'), GITHUB_EVENT_NAME='pull_request',
                       GITHUB_OUTPUT=str(root / 'output'), GITHUB_STEP_SUMMARY=str(root / 'summary'))
            subprocess.run([sys.executable, str(SCRIPT), 'plan'], env=env, cwd=ROOT,
                           check=True, capture_output=True)
            selected = json.loads((root / 'output').read_text().removeprefix('plan='))
            self.assert_broad(selected)
            self.assertIn('Event unavailable', (root / 'summary').read_text())

    def test_missing_selected_tool_regressions_cannot_silently_pass(self):
        with self.assertRaisesRegex(ValueError, 'missing or empty'):
            impact.run_tests({'tests': ['test_missing_synthetic_suite.py']})

    def test_cli_runner_supports_repository_namespace_imports(self):
        env = dict(os.environ, CI_PLAN=json.dumps({'tests': ['test_icons.py']}))
        result = subprocess.run([sys.executable, str(SCRIPT), 'test'], env=env, cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


class RequiredGate(unittest.TestCase):
    def needs(self, selected):
        # Independent workflow inventory: selected artifact consumers depend on
        # producers, but a producer failure must never make their skip acceptable.
        return {job: {'result': 'success' if run else 'skipped'} for job, run in {
            'impact': True, 'docs': True, 'native': selected['native'],
            'tools': selected['tools'], 'policy': selected['policy'], 'lint': selected['lint'],
            'memory': selected['memory'], 'release-native': selected['release_native'],
            'packages': bool(selected['formats']), 'release-bundle': selected['bundle'],
        }.items()}

    def test_docs_only_and_full_results_pass_with_explicit_skips(self):
        for selected in (impact.plan(['README.md']), impact.plan(full_reason='release')):
            impact.gate(selected, self.needs(selected))

    def test_every_failed_cancelled_missing_or_skipped_needed_job_fails_gate(self):
        selected = impact.plan(full_reason='release')
        needs = self.needs(selected)
        for job in needs:
            for result in ('failure', 'cancelled', 'skipped', None):
                changed = copy.deepcopy(needs)
                changed[job]['result'] = result
                with self.subTest(job=job, result=result), self.assertRaises(ValueError):
                    impact.gate(selected, changed)
        for job in needs:
            with self.subTest(missing=job), self.assertRaises(ValueError):
                impact.gate(selected, {key: value for key, value in needs.items() if key != job})

    def test_failed_artifact_dependency_with_skipped_consumers_fails(self):
        selected = impact.plan(['packaging/debian/control'])
        needs = self.needs(selected)
        needs['release-native']['result'] = 'failure'
        needs['packages']['result'] = 'skipped'
        with self.assertRaises(ValueError):
            impact.gate(selected, needs)

    def test_cli_failed_dependency_is_nonzero_and_keeps_results_summary(self):
        selected = impact.plan(['packaging/debian/control'])
        needs = self.needs(selected)
        needs['release-native']['result'] = 'failure'
        needs['packages']['result'] = 'skipped'
        with tempfile.TemporaryDirectory() as directory:
            summary = Path(directory) / 'summary'
            env = dict(os.environ, CI_PLAN=json.dumps(selected), CI_NEEDS=json.dumps(needs),
                       GITHUB_STEP_SUMMARY=str(summary))
            result = subprocess.run([sys.executable, str(SCRIPT), 'gate'], env=env,
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('| release-native | failure |', summary.read_text())
            self.assertIn('| packages | skipped |', summary.read_text())

    def test_unexpected_jobs_and_unscheduled_failures_are_rejected(self):
        selected = impact.plan(['README.md'])
        needs = self.needs(selected)
        needs['new-job'] = {'result': 'success'}
        with self.assertRaises(ValueError):
            impact.gate(selected, needs)
        del needs['new-job']
        needs['native']['result'] = 'failure'
        with self.assertRaises(ValueError):
            impact.gate(selected, needs)

    def test_workflow_gate_inventory_and_required_status_names(self):
        workflow = (ROOT / '.github/workflows/ci.yml').read_text()
        jobs = set(re.findall(r'^  ([a-z-]+):$', workflow.split('jobs:\n', 1)[1], re.M))
        gate = workflow.split('\n  build:\n')[1]
        dependencies = set(re.search(r'needs: \[([^]]+)\]', gate)[1].split(', '))
        self.assertEqual(dependencies, jobs - {'build'})
        self.assertEqual(dependencies, set(self.needs(impact.plan(['README.md']))))
        self.assertIn('if: always()', gate)
        self.assertIn('name: Rust and Fcitx5\n', gate)
        self.assertIn('name: Documentation and release tooling\n', workflow)
        self.assertNotIn('paths-ignore:', workflow)
        self.assertNotIn('continue-on-error:', workflow)
