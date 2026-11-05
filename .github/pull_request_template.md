## Problem and result

Explain the problem and resulting behavior. Include a small before/after example
when helpful, and link the related issue if there is one.

## Validation

List actual commands and outcomes. Identify checks that could not run. For
phonetic changes, include the pinned reference and exact Unicode evidence. Keep
synthetic harness checks separate from actual desktop tests.

## Review

Identify self-review or independent review and the reviewed revision. Assess
correctness, architecture, regressions and tests; cover memory ownership/leaks,
unsafe boundaries, performance, security and compatibility where relevant.
Explain why a category is not applicable when useful.

Post findings with location, severity, evidence, impact and recommended correction.
Fix findings and repeat affected checks and review. Merge only after required
checks pass on the latest revision, findings/conversations are resolved and there
are no conflicts. Verify the merge and post-merge CI before task-branch cleanup.

## Documentation and limitations

Describe relevant usage, behavior, handoff and changelog updates. Record material
limitations or remaining work. See `CONTRIBUTING.md` for the workflow.
Link related GitHub Issues; keep bug investigation and deferral decisions there.

For a release preparation PR, follow `docs/releases.md`: keep the tag, both Cargo
versions, lockfile, addon metadata and dated changelog notes consistent. Record
release-specific desktop evidence and unresolved issues. Apply relevant labels
to categorize generated release notes; version selection remains manual.
Declare the adapters, package assets, OS versions, architectures and input routes
included, with the relevant `docs/roadmap.md` acceptance results. Planned targets
must remain distinct from available support.
