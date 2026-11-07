# Security and privacy

Jong Bangla sees keystrokes because it is an input method. Conversion is local:
no network access, no telemetry, no keystroke logging, and no persistence of
typed text beyond the in-memory composition and commit data needed for typing.
Applications receive committed text through the input framework.

Keep diagnostics free of typed text. Use synthetic input in tests, benchmarks,
and bug reports. Keep the core free of I/O; review native adapters for the same
privacy contract. See [architecture](docs/ARCHITECTURE.md) for ownership boundaries.

## Enforcement

Planned in [#24](https://github.com/shaadahmmed/jong-bangla-keyboard/issues/24):
CI must reject networking crates through cargo-deny and networking calls through
a source scan of the core and adapters, including native glue. It must also run
dependency license and vulnerability checks. These gates are not implemented
yet. Scans complement code review and do not prove arbitrary code safe.

## Report a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/shaadahmmed/jong-bangla-keyboard/security/advisories/new).
Include the affected revision or release, environment, impact, and a minimal
synthetic reproduction. Keep vulnerability details out of public issues while
the report is being investigated. Discuss disclosure with the maintainer in
the private advisory.

Before the first release, fixes land on `main`. After releases begin, only the
latest published release receives security fixes. Older releases receive no
backports; upgrade to the latest release.

Reference licensing and attribution are recorded in
[THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES).
