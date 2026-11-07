#!/usr/bin/env python3
"""Build and compare two x86-64 Fcitx5 payloads; never install into the host."""

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tarfile
import tempfile
import tomllib


def run(args, **kwargs):
    return subprocess.run([str(arg) for arg in args], check=True, **kwargs)


def output(args):
    return subprocess.check_output([str(arg) for arg in args], text=True).strip()


def archive(destination, files, prefix, epoch):
    """Write only regular files, with stable ordering, modes and gzip/tar metadata."""
    with destination.open("xb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as tar:
                for name, path in sorted(files.items()):
                    if not path.is_file() or path.is_symlink():
                        raise ValueError(f"payload must contain only regular files: {name}")
                    info = tarfile.TarInfo(f"{prefix}/{name}")
                    info.size = path.stat().st_size
                    info.mode = 0o755 if name.endswith(".so") else 0o644
                    info.mtime = epoch
                    with path.open("rb") as source:
                        tar.addfile(info, source)


def staged_files(stage):
    files = {path.relative_to(stage).as_posix(): path for path in stage.rglob("*")
             if not path.is_dir()}
    expected = {"usr/lib/fcitx5/libjong-bangla.so", "usr/share/fcitx5/addon/jong-bangla.conf",
                "usr/share/fcitx5/inputmethod/jong-bangla.conf"}
    if set(files) != expected or any(path.is_symlink() for path in files.values()):
        raise ValueError("release stage must contain exactly the three expected Fcitx5 files")
    return files


def compare(first, second):
    if first.keys() != second.keys() or any(first[name].read_bytes() != second[name].read_bytes()
                                           for name in first):
        raise ValueError("independent release builds differ; refusing to prepare artifacts")


def checksum_manifest(directory):
    files = sorted(directory.iterdir())
    if not files or any(not path.is_file() or path.is_symlink() for path in files):
        raise ValueError("artifact directory must contain only regular files")
    with (directory / "SHA256SUMS").open("x", encoding="utf-8") as manifest:
        for path in files:
            manifest.write(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n")


def build(root, destination):
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise ValueError("native release builds require x86-64 Linux")
    # An existing directory could contain stale artifacts from a failed build.
    destination.mkdir(parents=True, exist_ok=False)
    commit = output(["git", "-C", root, "rev-parse", "HEAD^{commit}"])
    epoch = int(output(["git", "-C", root, "show", "-s", "--format=%ct", commit]))
    source_tar = subprocess.check_output(["git", "-C", str(root), "archive", "--format=tar", commit])
    with tempfile.TemporaryDirectory(prefix="jong-release-") as temporary:
        work = Path(temporary)
        sources = []
        payloads = []
        for index in range(2):
            source = work / f"source-{index}"
            source.mkdir()
            with tarfile.open(fileobj=io.BytesIO(source_tar)) as tar:
                tar.extractall(source, filter="data")
            sources.append(source)
            build_dir, stage = work / f"build-{index}", work / f"stage-{index}"
            env = dict(os.environ, SOURCE_DATE_EPOCH=str(epoch), TZ="UTC", LC_ALL="C",
                       CARGO_INCREMENTAL="0")
            # Mapping each build/source separately avoids build-0 vs build-1 paths.
            env["RUSTFLAGS"] = (f"--remap-path-prefix={source}=/usr/src/jong-bangla "
                                f"--remap-path-prefix={build_dir}=/usr/src/jong-build")
            # Encoded flags take precedence, including when empty: let RUSTFLAGS apply.
            env.pop("CARGO_ENCODED_RUSTFLAGS", None)
            flags = f"-ffile-prefix-map={source}=/usr/src/jong-bangla -ffile-prefix-map={build_dir}=/usr/src/jong-build"
            run(["cmake", "-S", source / "adapters/fcitx5", "-B", build_dir, "-G", "Ninja",
                 "-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_INSTALL_PREFIX=/usr",
                 "-DFCITX_INSTALL_USE_FCITX_SYS_PATHS=ON", "-DJONG_ENABLE_SANITIZERS=OFF",
                 f"-DCMAKE_CXX_FLAGS={flags}"], env=env)
            run(["cmake", "--build", build_dir], env=env)
            run(["ctest", "--test-dir", build_dir, "--output-on-failure"], env=env)
            run([sys.executable, source / "tools/check-install.py", build_dir], env=env)
            run(["cmake", "--install", build_dir], env=dict(env, DESTDIR=str(stage)))
            payloads.append(staged_files(stage))
        compare(*payloads)
        source = sources[0]
        version = tomllib.loads((source / "Cargo.toml").read_text())["package"]["version"]
        prefix = f"jong-bangla-{version}"
        source_name = f"{prefix}.tar.gz"
        # Preserve git archive semantics and normalize the gzip header.
        with (destination / source_name).open("xb") as raw:
            source_archive = subprocess.check_output([
                "git", "-C", str(root), "archive", "--format=tar", f"--prefix={prefix}/", commit,
            ])
            with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as compressed:
                compressed.write(source_archive)
        for name in ("LICENSE", "THIRD_PARTY_NOTICES", "README.md", "CONTRIBUTING.md"):
            payloads[0][name] = source / name
        native_name = f"{prefix}-fcitx5-x86_64-linux-gnu.tar.gz"
        archive(destination / native_name, payloads[0], native_name.removesuffix(".tar.gz"), epoch)
        info = {
            "commit": commit, "version": version, "source_date_epoch": epoch,
            "target": "x86_64-linux-gnu", "independent_builds_identical": True,
            "build_image": os.environ.get("RELEASE_BUILD_IMAGE", "local (not pinned)"),
            "arch_snapshot": os.environ.get("RELEASE_ARCH_SNAPSHOT", "local (not pinned)"),
            "packages": output(["pacman", "-Q"]).splitlines(),
            "rustc": output(["rustc", "-vV"]), "cxx": output(["c++", "--version"]),
        }
        (destination / "build-info.json").write_text(json.dumps(info, indent=2, sort_keys=True) + "\n")
        checksum_manifest(destination)
    print(f"PASS: two identical native builds; source, payload, build info and checksums in {destination}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="new artifact directory")
    args = parser.parse_args()
    try:
        build(Path.cwd(), args.output.resolve())
    except (OSError, ValueError, subprocess.CalledProcessError, tarfile.TarError) as error:
        sys.exit(f"FAIL: {error}")


if __name__ == "__main__":
    main()
