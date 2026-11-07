#!/usr/bin/env python3
"""Build two package revisions and verify their lifecycle in fresh distro containers."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


# Official images, pinned by digest. Package versions are recorded, not frozen.
IMAGES = {
    "arch": "archlinux@sha256:624bdc7fc6615155d67bc34cf7146c0c9fd0e3c92943977da63a630e4ca49c30",
    "deb": "debian@sha256:c6343ac5a6f7952485fc804a1cf700bdb8af7408d4c549faf682bed42b1c7f96",
    "rpm": "fedora@sha256:15da97ed9aa94dd3d92c3925eb89520f6c80e07ea7ee24cba848d1f8b6912b3e",
}
BUILD_SETUP = {
    "arch": "sed -i '/^NoExtract.*usr\\/share\\/doc/d' /etc/pacman.conf && pacman -Syu --noconfirm --needed base-devel rust cmake ninja fcitx5 python pkgconf && useradd -m builder",
    "deb": "apt-get update && apt-get install -y build-essential debhelper cmake ninja-build libfcitx5core-dev pkg-config python3 rustup && rustup toolchain install 1.99.1 --profile minimal && rustup default 1.99.1",
    "rpm": "dnf install -y gcc-c++ cmake ninja-build rust cargo fcitx5-devel python3 rpm-build pkgconf-pkg-config",
}
# Minimal images suppress documentation by default. Enable it in the test
# container so installation verifies the actual license/instruction files.
RUNTIME_SETUP = {"arch": "sed -i '/^NoExtract.*usr\\/share\\/doc/d' /etc/pacman.conf && pacman -Syu --noconfirm --needed python",
                 "deb": "sed -i '/^path-exclude \\/usr\\/share\\/doc\\//d' /etc/dpkg/dpkg.cfg.d/docker && apt-get update && apt-get install -y python3",
                 "rpm": "sed -i '/^tsflags=nodocs/d' /etc/dnf/dnf.conf && dnf install -y python3"}


def run(args, log):
    with log.open("w") as output:
        result = subprocess.run([str(a) for a in args], stdout=output, stderr=subprocess.STDOUT)
    if result.returncode:
        # Keep full synthetic logs as artifacts, display only the failure tail.
        print("\n".join(log.read_text().splitlines()[-65:]), file=sys.stderr)
        raise ValueError(f"container check failed; full log: {log}")


def check(kind, source, output, epoch):
    output.mkdir(parents=True, exist_ok=False)
    tools = Path(__file__).resolve().parent
    common = ["docker", "run", "--rm", "-e", f"SOURCE_DATE_EPOCH={epoch}",
              "-v", f"{tools}:/tools:ro", "-v", f"{source}:/input/source.tar.gz:ro",
              "-v", f"{output}:/out"]
    dockerfile = f"FROM {IMAGES[kind]}\nRUN {BUILD_SETUP[kind]}\n"
    build_image = f"jong-package-build-{kind}:" + hashlib.sha256(dockerfile.encode()).hexdigest()[:16]
    with (output / "setup.log").open("w") as log:
        subprocess.run(["docker", "build", "--tag", build_image, "-"], input=dockerfile,
                       text=True, stdout=log, stderr=subprocess.STDOUT, check=True)
    build = " && ".join(
        f"python3 /tools/build-packages.py {kind} --source /input/source.tar.gz --output /out/revision-{rev} --revision {rev}"
        for rev in (1, 2))
    run([*common, build_image, "sh", "-ec", build], output / "build.log")
    reports = [json.loads((output / f"revision-{rev}/build.json").read_text()) for rev in (1, 2)]
    for info in reports:
        if info["source_sha256"] != hashlib.sha256(source.read_bytes()).hexdigest():
            raise ValueError("package build source identity differs")
    paths = [f"/out/revision-{rev}/{info['package']}" for rev, info in zip((1, 2), reports)]
    runtime = (RUNTIME_SETUP[kind] + " && mkdir -p /opt/jong-package-test && "
               "cp /out/revision-1/harness /opt/jong-package-test/ && "
               "cp -r /out/revision-1/harness-data /opt/jong-package-test/ && "
               f"python3 /tools/check-package-install.py {kind} {' '.join(paths)} --output /out/runtime.json")
    run([*common, "-e", "JONG_PACKAGE_TEST=1", IMAGES[kind], "sh", "-ec", runtime], output / "runtime.log")
    build_id = subprocess.check_output(["docker", "image", "inspect", "--format", "{{.Id}}", build_image], text=True).strip()
    report = {"image": IMAGES[kind], "build_image_id": build_id, "builds": reports,
              "runtime": json.loads((output / "runtime.json").read_text())}
    (output / f"package-check-{kind}.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    # Only revision 1 is a release asset. Revision 2 tests package-manager
    # revision upgrades using identical code, not a previous public release.
    shutil.copyfile(output / "revision-1" / reports[0]["package"], output / reports[0]["package"])
    for recipe in (output / "revision-1").glob("*-aur.tar.gz"):
        shutil.copyfile(recipe, output / recipe.name)
    print(f"PASS: {kind} install, revision upgrade, linking, synthetic loading and removal; {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("format", choices=IMAGES)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--epoch", required=True, type=int)
    args = parser.parse_args()
    try:
        check(args.format, args.source.resolve(), args.output.resolve(), args.epoch)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        sys.exit(f"FAIL: {error}")


if __name__ == "__main__":
    main()
