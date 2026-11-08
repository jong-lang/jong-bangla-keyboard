#!/usr/bin/env python3
"""Maintainer-run KWrite/Firefox input-path proof, not full desktop acceptance."""

import argparse
from pathlib import Path
import signal
import sys

from desktop_proof import ProofError, prerequisites, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true",
                        help="open test applications and request temporary keyboard control")
    parser.add_argument("--output", type=Path, help="new report directory (required with --run)")
    args = parser.parse_args()
    if args.run and args.output is None:
        parser.error("--run requires --output")
    try:
        prerequisites()
        if not args.run:
            print("PASS: local prerequisites only; no desktop session or apps contacted")
            print("Desktop proof not run. Use --run --output NEW_DIRECTORY to run it.")
            return 0
        def interrupted(_signal, _frame):
            raise KeyboardInterrupt("Interrupted by termination signal")
        signal.signal(signal.SIGTERM, interrupted)
        from desktop_linux import LinuxDesktop
        return run(args.output.resolve(), LinuxDesktop, Path(__file__).resolve().parents[1])
    except (ProofError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
