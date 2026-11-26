# GitHub issue tracker

Track issues and specs in `jong-lang/jong-bangla-keyboard` with `gh`.
Follow the repository workflow in [CONTRIBUTING.md](../../CONTRIBUTING.md).
Use `--repo jong-lang/jong-bangla-keyboard` when writing to the tracker.

## Common operations

- Publish a ticket or spec with `gh issue create --title "<title>" --body-file <file>`.
  Use the repository's issue templates where applicable.
- Fetch a ticket with `gh issue view <number> --json number,title,body,labels,comments`.
- Find tickets with `gh issue list --state open`. Filter by label or search as needed.
- Comment with `gh issue comment <number> --body-file <file>`.
- Apply or remove labels with `gh issue edit <number> --add-label <label>` or
  `--remove-label <label>`. Use the [triage mapping](triage-labels.md) for issue status.
- Post the resolution before closing with `gh issue close <number>`.

## Development labels

| Label | Use for |
| --- | --- |
| `bug` | Defects in existing behavior |
| `enhancement` | New features and improvements |
| `documentation` | Documentation changes |
| `accessibility` | Accessibility work |
| `refactor` | Internal changes that preserve behavior |
| `performance` | Speed, memory, or responsiveness work |
| `testing` | Test coverage, fixtures, and acceptance automation |
| `build` | Build tooling, packaging, and installation |
| `ci` | Continuous integration and release automation |
| `dependencies` | Dependency updates and maintenance |

## Pull requests as a triage surface

**PRs as a request surface: no.**

## Wayfinding operations

- Create the map as an issue with the `wayfinder:map` label.
- Link tickets as native sub-issues using `gh issue create --parent <map>` or
  `gh issue edit <map> --add-sub-issue <child>`. Use `wayfinder:<type>` labels.
- Record blockers with `gh issue edit <child> --add-blocked-by <blocker>`.
- Pick the first open, unassigned child in map order whose blockers are closed.
  Inspect `subIssues`, `assignees`, and `blockedBy` with `gh issue view --json`.
- Claim with `gh issue edit <number> --add-assignee @me`. After resolving the
  ticket, post the result, close the issue, and link the outcome from the map.
