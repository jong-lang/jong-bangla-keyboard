#!/usr/bin/env python3
"""Stage an experimental install; check discovery and removal without a daemon."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

from icon_payload import icon_files


def run(args, *, env=None, expect_success=True):
    result = subprocess.run(
        [str(arg) for arg in args], env=env, capture_output=True, text=True,
        timeout=120, check=False,
    )
    if (result.returncode == 0) != expect_success:
        sys.stderr.write(result.stdout + result.stderr)
        sys.exit(f"FAIL: unexpected exit {result.returncode}: {args[0]}")
    return result


def require(condition, message):
    if not condition:
        sys.exit(f"FAIL: {message}")


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python3 tools/check-install.py BUILD_DIRECTORY")
    build = Path(sys.argv[1]).resolve()
    destinations = (build / "install-layout.txt").read_text().splitlines()
    require(len(destinations) == 3, "expected addon, package-data and data destinations")
    for destination in destinations:
        path = Path(destination)
        require(path.is_absolute() and ".." not in path.parts,
                "installation destinations must be absolute without '..'")

    with tempfile.TemporaryDirectory(prefix="jong-install-check-") as directory:
        stage = Path(directory)
        addon_dir, data_dir, shared_data = [
            stage / Path(path).relative_to("/") for path in destinations
        ]
        library = addon_dir / "libjong-bangla.so"
        metadata = data_dir / "addon/jong-bangla.conf"
        input_method = data_dir / "inputmethod/jong-bangla.conf"
        expected = {library, metadata, input_method} | icon_files(shared_data)
        env = dict(os.environ, DESTDIR=str(stage))
        run(["cmake", "--install", build], env=env)
        actual = {path for path in stage.rglob("*") if not path.is_dir() or path.is_symlink()}
        require(actual == expected and all(path.is_file() and not path.is_symlink()
                                          for path in actual),
                f"expected exactly twelve regular installation files; found {sorted(actual)}")
        require("Library=libjong-bangla\n" in metadata.read_text(),
                "installed metadata must use the relocatable library name")
        require(str(build) not in metadata.read_text(),
                "installed metadata must not contain the build path")
        require("Addon=jong-bangla\n" in input_method.read_text(),
                "input-method registration must match the addon identifier")
        require("Icon=jong-bangla\n" in input_method.read_text(),
                "input-method registration must reference the installed app icon")
        print("PASS: exactly twelve staged files; metadata has no build path", flush=True)

        # The distro owns index.theme, not Jong. Supply its directory definitions
        # inside the temporary stage without exposing any system icon assets.
        index = shared_data / "icons/hicolor/index.theme"
        shutil.copyfile("/usr/share/icons/hicolor/index.theme", index)
        icons = [build / "jong-fcitx5-harness", "--icons", shared_data]
        result = run(icons)
        print(f"PASS: staged icon lookup: {result.stdout.strip()}", flush=True)
        symbolic = shared_data / "icons/hicolor/scalable/status/jong-symbolic.svg"
        tree = ET.parse(symbolic)
        namespace = {"s": "http://www.w3.org/2000/svg"}
        style = tree.find(".//s:style", namespace)
        require(style is not None and style.get("id") == "current-color-scheme"
                and ".ColorScheme-Text{color:#24282b}" in (style.text or ""),
                "symbolic SVG must provide the KDE palette stylesheet and fallback")
        shapes = tree.findall(".//s:path", namespace)
        original = ET.parse(shared_data /
                            "icons/hicolor/scalable/status/fcitx-jong-bangla-light.svg")
        require([node.get("d") for node in shapes] ==
                [node.get("d") for node in original.findall(".//s:path", namespace)]
                and shapes and all(node.get("class") == "ColorScheme-Text"
                                   and node.get("fill") == "currentColor" for node in shapes),
                "symbolic SVG must preserve the artwork and use palette-aware fills")
        hidden_icon = symbolic.with_suffix(".hidden")
        symbolic.rename(hidden_icon)
        try:
            result = run(icons, expect_success=False)
            require("resolve exact installed icon: scalable/status/jong-symbolic.svg"
                    in result.stderr, "missing-icon control failed for another reason")
        finally:
            hidden_icon.rename(symbolic)
            index.unlink()
        print("PASS: missing status icon rejected; no host/prefix fallback", flush=True)

        harness = [build / "jong-fcitx5-harness", "--installed", data_dir, addon_dir]
        result = run(harness)
        print(f"PASS: staged loading: {result.stdout.strip()}", flush=True)
        # An absent staged library must fail, even while the build-local copy
        # still exists. This detects fallback to a developer/system installation.
        hidden = library.with_suffix(".so.hidden")
        library.rename(hidden)
        try:
            result = run(harness, expect_success=False)
            require("Fcitx5 harness failed: load Jong addon from configured library path"
                    in result.stderr,
                    f"missing-library control failed for another reason: {result.stderr}")
        finally:
            hidden.rename(library)
        print("PASS: missing staged library rejected; no build/system fallback", flush=True)

        sentinel = addon_dir / "unrelated-addon.keep"
        sentinel.write_text("unrelated file must remain\n")
        icon_sentinel = shared_data / "icons/hicolor/scalable/status/unrelated.keep"
        icon_sentinel.write_text("unrelated icon must remain\n")
        for path in expected:
            path.unlink()
        remaining = {path for path in stage.rglob("*") if path.is_file()}
        require(remaining == {sentinel, icon_sentinel}, "removal must retain unrelated files")
        print("PASS: removed only Jong's twelve files; unrelated sentinels retained", flush=True)


if __name__ == "__main__":
    main()
