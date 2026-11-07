#!/usr/bin/env python3
"""Build a native package from a release source archive inside its distro image."""

import argparse
from email.utils import formatdate
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib


def run(args, **kwargs):
    return subprocess.run([str(arg) for arg in args], check=True, **kwargs)


def capture(args, **kwargs):
    return subprocess.check_output([str(arg) for arg in args], text=True, **kwargs).strip()


def versions(version, revision):
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.]+)?", version):
        raise ValueError("unsupported package version")
    if revision < 1:
        raise ValueError("package revision must be positive")
    base, _, pre = version.partition("-")
    return {
        "deb": (version.replace("-", "~"), str(revision)),
        "rpm": (base, f"0.{revision}.{pre}" if pre else str(revision)),
        "arch": (base + pre, str(revision)),
    }


def render(template, values):
    for key, value in values.items():
        template = template.replace(f"@{key}@", str(value))
    if re.search(r"@[A-Z_]+@", template):
        raise ValueError("unresolved package template variable")
    return template


def source_root(archive, destination):
    with tarfile.open(archive) as source:
        # Release sources contain regular files and directories only. Reject
        # links and ambiguous roots before letting packaging tools read them.
        members = source.getmembers()
        if not members or any(not (m.isfile() or m.isdir()) for m in members):
            raise ValueError("source must contain only regular files/directories")
        paths = [Path(m.name) for m in members]
        if any(not p.parts or p.is_absolute() or ".." in p.parts for p in paths):
            raise ValueError("source must have one safe top-level directory")
        roots = {p.parts[0] for p in paths}
        if len(roots) != 1:
            raise ValueError("source must have one safe top-level directory")
        source.extractall(destination, filter="data")
    return destination / roots.pop()


def build(kind, archive, destination, revision):
    destination.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix="jong-package-") as directory:
        work = Path(directory)
        root = source_root(archive, work)
        manifest = tomllib.loads((root / "Cargo.toml").read_text())
        version = manifest["package"]["version"]
        pkgver, pkgrel = versions(version, revision)[kind]
        epoch = int(os.environ["SOURCE_DATE_EPOCH"])
        env = dict(os.environ, SOURCE_DATE_EPOCH=str(epoch), CARGO_INCREMENTAL="0")
        values = {"VERSION": pkgver, "REVISION": pkgrel, "SOURCE_DIR": root.name,
                  "SOURCE_URL": f"https://github.com/shaadahmmed/jong-bangla-keyboard/releases/download/v{version}/jong-bangla-{version}.tar.gz",
                  "SHA256": hashlib.sha256(archive.read_bytes()).hexdigest()}
        if kind == "deb":
            # Debhelper isolates HOME. Preserve an explicitly configured rustup
            # installation when the distro compiler is below the manifest MSRV.
            if shutil.which("rustup"):
                env["RUSTUP_HOME"] = capture(["rustup", "show", "home"])
            shutil.copytree(root / "packaging/debian", root / "debian")
            (root / "debian/rules").chmod(0o755)
            (root / "debian/changelog").write_text(
                f"jong-bangla ({pkgver}-{pkgrel}) unstable; urgency=medium\n\n"
                "  * Build native Fcitx5 package from the identified release source.\n\n"
                f" -- Jong Bangla maintainers <shaadahmmed@users.noreply.github.com>  {formatdate(epoch)}\n")
            run(["dpkg-buildpackage", "--build=binary", "--no-sign"], cwd=root,
                env=dict(env, DEB_BUILD_OPTIONS="noautodbgsym"))
            packages = list(work.glob("jong-bangla_*.deb"))
        elif kind == "rpm":
            top = work / "rpmbuild"
            for name in ("BUILD", "BUILDROOT", "RPMS", "SOURCES", "SPECS", "SRPMS"):
                (top / name).mkdir(parents=True)
            shutil.copyfile(archive, top / "SOURCES/source.tar.gz")
            spec = top / "SPECS/jong-bangla.spec"
            spec.write_text(render((root / "packaging/fedora/jong-bangla.spec.in").read_text(), values))
            run(["rpmbuild", "-bb", spec, "--define", f"_topdir {top}",
                 "--define", "debug_package %{nil}", "--define", "_build_id_links none"], env=env)
            packages = list((top / "RPMS").rglob("jong-bangla-*.rpm"))
        else:
            recipe = work / "aur"
            recipe.mkdir()
            (recipe / "PKGBUILD").write_text(render((root / "packaging/arch/PKGBUILD.in").read_text(), values))
            shutil.copyfile(archive, recipe / "source.tar.gz")
            run(["chown", "-R", "builder:builder", work])
            with (recipe / ".SRCINFO").open("w") as output:
                run(["runuser", "-u", "builder", "--", "makepkg", "--printsrcinfo"], cwd=recipe, stdout=output, env=env)
            run(["runuser", "-u", "builder", "--", "makepkg", "--cleanbuild", "--noconfirm"], cwd=recipe, env=env)
            packages = list(recipe.glob("jong-bangla-*.pkg.tar.zst"))
            if revision == 1:
                maintained = work / "maintained-aur"
                maintained.mkdir()
                for name in ("PKGBUILD", ".SRCINFO"):
                    shutil.copyfile(root / "packaging/arch" / name, maintained / name)
                run(["chown", "-R", "builder:builder", maintained])
                generated = capture(["runuser", "-u", "builder", "--", "makepkg", "--printsrcinfo"], cwd=maintained, env=env)
                if generated != (maintained / ".SRCINFO").read_text().strip():
                    raise ValueError("maintained .SRCINFO differs from PKGBUILD")
                run(["runuser", "-u", "builder", "--", "makepkg", "--verifysource"], cwd=maintained, env=env)
                run(["runuser", "-u", "builder", "--", "makepkg", "--cleanbuild", "--noconfirm"], cwd=maintained, env=env)
                with tarfile.open(destination / f"jong-bangla-{version}-aur.tar.gz", "w:gz") as tar:
                    for name in ("PKGBUILD", ".SRCINFO"):
                        tar.add(recipe / name, arcname=f"jong-bangla/{name}")
        if len(packages) != 1:
            raise ValueError(f"expected exactly one {kind} package, found {packages}")
        shutil.copyfile(packages[0], destination / packages[0].name)
        # Reuse the real synthetic addon harness against package-manager paths.
        # Its two null registrations are the only test data copied to runtime.
        flags = capture(["pkg-config", "--cflags", "--libs", "Fcitx5Core"]).split()
        run(["c++", "-std=c++20", '-DJONG_HARNESS_DATA="/opt/jong-package-test/harness-data"',
             root / "adapters/fcitx5/tests/harness.cpp", *flags, "-o", destination / "harness"])
        data = destination / "harness-data/fcitx5"
        for src, target in (("null-addon.conf", "addon/jong-harness-null.conf"),
                            ("null-inputmethod.conf", "inputmethod/keyboard-us.conf")):
            path = data / target
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / "adapters/fcitx5/tests" / src, path)
        manager = {"deb": ["dpkg-query", "-W"], "rpm": ["rpm", "-qa"], "arch": ["pacman", "-Q"]}[kind]
        info = {"format": kind, "version": version, "revision": revision,
                "source_sha256": values["SHA256"], "source_date_epoch": epoch,
                "package": packages[0].name, "os_release": Path("/etc/os-release").read_text(),
                "packages": capture(manager).splitlines(), "rustc": capture(["rustc", "-vV"]),
                "cxx": capture(["c++", "--version"])}
        if kind == "arch" and revision == 1:
            info["maintained_recipe_verified"] = True
            info["recipe_sha256"] = hashlib.sha256((destination / f"jong-bangla-{version}-aur.tar.gz").read_bytes()).hexdigest()
        (destination / "build.json").write_text(json.dumps(info, indent=2, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("format", choices=("deb", "rpm", "arch"))
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--revision", type=int, default=1)
    args = parser.parse_args()
    try:
        build(args.format, args.source.resolve(), args.output.resolve(), args.revision)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError, tarfile.TarError) as error:
        sys.exit(f"FAIL: {error}")


if __name__ == "__main__":
    main()
