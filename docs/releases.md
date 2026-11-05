# Releases

Jong Bangla uses branches and pull requests, manually selected versions, and
automated draft releases. The automation does not publish releases, merge PRs,
create version bumps or publish Cargo packages. Both crates remain `publish = false`.
The [roadmap](roadmap.md) defines confirmed platform/package targets and staged
delivery. Current automation produces source archives only; it does not yet build
Linux packages, Windows installers or macOS bundles. Early source releases may
ship independently while those delivery stages are implemented.

## Everyday changes

1. Inspect open Issues and PRs, finish existing work and prioritize actionable
   bugs. Keep blocked issues open with an explanation and explain unclear
   priorities before proceeding. Create a fresh branch from up-to-date `main`
   for each coherent task, including documentation and maintenance.
2. Add meaningful regression coverage, relevant docs and notable user-facing
   entries under `Unreleased` in [the changelog](../CHANGELOG.md).
3. Run the relevant [development checks](development.md), then commit, push and
   open a PR to `main` without routine confirmation requests. The maintainer
   approved this workflow in place of the former per-commit confirmation rule.
4. Follow the [review, merge and cleanup rules](../CONTRIBUTING.md#review-merge-and-cleanup).
   Review the complete PR, post and fix findings, and require successful checks
   for the latest revision, resolved conversations and no conflicts before
   merging. Never bypass protections or push task changes directly to `main`.
5. Verify the merge and post-merge CI, close resolved linked issues, delete only
   the completed task's remote/local branches and synchronize local `main`.

Use descriptive PR titles and labels: `enhancement`, `bug`, `breaking-change`,
`documentation` or `dependencies`. The [release-note configuration](../.github/release.yml)
groups merged PRs by these labels, with a catch-all for other changes.
`skip-release-notes` excludes an internal-only PR from generated notes; it does
not remove the change from the source archive or the full Git history.

## Version policy

Select versions manually in a release preparation PR. Keep the core and all
implemented adapters at one project version, so one tag identifies the complete
source. Package rebuild revisions are separate from the upstream project version.
Document each ecosystem's prerelease version mapping when adding its recipe.
Tags use `vX.Y.Z`, or `vX.Y.Z-alpha.N`, `vX.Y.Z-beta.N`, `vX.Y.Z-rc.N` with `N >= 1`.
The metadata version omits the leading `v`. Other tag forms are rejected.

- `alpha`: experimental releases with explicitly documented missing validation
  or known defects. `v0.1.0-alpha.1` is the suggested first public release, not a
  version selected or published by this setup change.
- `beta`: the declared adapters, packages and desktop routes pass the
  [acceptance gate](roadmap.md#acceptance-gate-for-each-release-scope).
- `rc`: a candidate for a declared stable scope with no open blocking Issues for
  that scope; any accepted deferrals are recorded in the tracker.
- Before `1.0`, use a new minor version for incompatible changes to the declared
  interface or behavior; use patch versions for compatible fixes.
- `1.0.0` requires a documented API/behavior promise, installation path and
  tested support scope. After that, use SemVer major/minor/patch rules.

These are project readiness conventions. They do not convert an untested
desktop route into supported behavior. See [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
The current Cargo `0.1.0` baseline is not a published release.

## Prepare a release PR

1. Create a release branch and select the next version. Update `version` in
   [the core manifest](../Cargo.toml) and [the FFI manifest](../adapters/fcitx5/ffi/Cargo.toml),
   and `Version` in [the addon metadata](../adapters/fcitx5/jong-bangla.conf.in).
   Regenerate `Cargo.lock` with `cargo generate-lockfile --offline`; inspect its diff.
   These are the currently implemented artifacts. When adding adapters/packages,
   extend the validator and asset workflow to cover their version metadata before
   offering those artifacts in a release.
2. Copy [the release template](../.github/RELEASE_TEMPLATE.md) into `CHANGELOG.md`
   below `Unreleased`. Replace all `{{...}}` placeholders, use an ISO date
   (`YYYY-MM-DD`), and move the changes being released into this dated section.
   Keep `Unreleased` available for future work. Do not duplicate its initial
   "not a published release" baseline description into published notes.
3. Fill every template section. Use `None` for no fixes/breaking changes. Declare
   the included adapters, artifacts, OS/architecture matrix and input routes.
   State checks not performed and identify older observations as prior evidence.
   Track bugs and release-blocking/deferral decisions in GitHub Issues; the Known
   issues section links to the relevant issues or milestone without copying bug
   reports. A source release does not imply a desktop support claim.
4. Run the [documented checks](development.md), including the adapter's staged
   install check. Run the [pinned reference checks](reference-checks.md) for
   phonetic changes and the appropriate resource checks for new performance claims.
   Record real desktop results for the exact release candidate; CI covers
   synthetic tests, not GUI applications. After a changed candidate is merged,
   repeat any desktop checks needed for the final commit before tagging it.
5. Run the release validator using your selected version, for example:

   ```sh
   python3 tools/check-release.py v0.1.0-alpha.1
   ```

   The example intentionally fails against the unreleased initial baseline.
   It must pass for the prepared release version. The validator checks both
   manifests, both lockfile package versions, addon metadata, a unique dated
   changelog section, required nonempty note sections and unresolved placeholders.
   Attach the successful command and outcome to the release PR: current PR CI
   does not run this validator. Automatic validation currently starts on tag
   pushes; moving it before merge is a [planned tooling step](roadmap.md#implementation-follow-ups-from-the-documentation-review).
6. Review the complete diff, commit and submit the release PR through the same
   review and merge gates as other tasks. Version selection stays manual;
   merging a release PR does not authorize tagging or publishing a release.

## Tag and review the draft

Once the release PR is merged, fetch `origin/main`, identify the exact approved
release commit and rerun the version validator at that commit. Create an annotated
version tag pointing to that commit and push that tag explicitly. Do not tag
whatever happens to be the latest local branch commit or push unrelated tags.
Release tags are maintained by a human; a tag created using a workflow's default
`GITHUB_TOKEN` will not normally trigger another workflow.

The [release workflow](../.github/workflows/release.yml) runs on `v*` tag pushes:

1. Require the tagged commit to be an ancestor of `origin/main`, then validate
   metadata and release notes. This checks main-branch membership; GitHub branch
   rules enforce the PR-only requirement.
2. Run the same [CI workflow](../.github/workflows/ci.yml) against the tagged commit.
3. Create `jong-bangla-VERSION.tar.gz` from that commit with a matching
   `SHA256SUMS`, and prepare a GitHub **draft** with the reviewed changelog notes,
   a validation-run link and generated PR/contributor notes. Version suffixes
   automatically set the draft's prerelease flag; drafts are never marked latest.

Review the title, notes, prerequisite/install links, linked Issues, prerelease
flag and assets before manually publishing. For stable releases, deliberately
select whether it should be the latest release. Keep prereleases off latest.
Verify the downloaded archive with `sha256sum -c SHA256SUMS` in its download folder.
Checksums detect corrupted downloads; they are not a substitute for provenance.

Rerun a failed workflow at the same tag for transient build/network failures.
Existing releases are never overwritten by this workflow. If draft creation
partially succeeds, inspect it and finish or remove that unpublished draft before
retrying. If source or notes committed to the tag need changing, prepare a new
version through a PR. Never move/reuse a release tag or replace published assets.

## GitHub repository settings

Workflow files cannot enforce repository branch rules or enable immutable
releases. An administrator must configure these settings separately.

**Verified on 2026-11-05:** `main` requires PRs, both CI jobs from GitHub Actions
(app 15368), an up-to-date base and resolved review conversations. Stale approvals
are dismissed; deletion and force pushes are blocked, and there are no bypass
actors. Zero external approvals are required for the solo-maintainer setup.
[PR #3](https://github.com/shaadahmmed/jong-bangla-keyboard/pull/3) merged normally;
its [PR CI](https://github.com/shaadahmmed/jong-bangla-keyboard/actions/runs/42066375680)
and [post-merge CI](https://github.com/shaadahmmed/jong-bangla-keyboard/actions/runs/42066639505)
passed. Configuration tracking and verification are in
[Issue #2](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/2).
Tag protections and immutable-release settings were not inspected. This is
dated evidence; reinspect settings before relying on them in a later session.

- Add an active branch ruleset for `main` requiring a PR, blocking force pushes
  and deletion, and requiring the `Documentation and release tooling` and
  `Rust and Fcitx5` status checks. Select the actual checks after their first
  successful hosted run; require the branch to be up to date before merging,
  resolved review conversations and dismissal of stale approvals.
- For a solo maintainer, require PRs with **zero required approving reviewers**:
  you cannot approve your own PR. Add a required independent reviewer when one
  is available. Never bypass the branch rules to finish a task.
- Add a tag ruleset for `v*` blocking updates and deletion, while allowing
  maintainers to create new release tags.
- Enable immutable releases. Assemble all assets in the draft before publishing.
  Publication then locks the tag/assets; title and notes remain editable.
- Keep the default Actions token read-only. Only the release draft job requests
  `contents: write`; PR checks use no release credentials. External actions use
  full commit SHAs, with weekly Dependabot update PRs.
- Create the labels listed above and `skip-release-notes` if missing. Ensure
  GitHub Actions and Dependabot version updates are allowed for the repository.

CI uses an official rolling `archlinux:base-devel` container, upgrades it before
building, and records package versions in the job summary. This meets the
documented Fcitx5 prerequisite without claiming bit-for-bit reproducible builds
or a validated support matrix. Network access is used for tooling installation;
transliteration and Rust workspace checks remain local/offline.

GitHub references: [rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets),
[generated notes](https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes),
[immutable releases](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases),
[Dependabot for Actions](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/auto-update-actions),
[workflow trigger restrictions](https://docs.github.com/en/actions/how-tos/writing-workflows/choosing-when-your-workflow-runs/triggering-a-workflow).
