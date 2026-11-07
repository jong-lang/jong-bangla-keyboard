"""Release package names and evidence checks shared by assembly and draft gates."""

import hashlib
import json
import re


def package_names(version):
    base, _, pre = version.partition("-")
    return {
        "deb": f"jong-bangla_{version.replace('-', '~')}-1_amd64.deb",
        "rpm": f"jong-bangla-{base}-{'0.1.' + pre if pre else '1'}.x86_64.rpm",
        "arch": f"jong-bangla-{base + pre}-1-x86_64.pkg.tar.zst",
    }


def package_assets(version):
    return set(package_names(version).values()) | {
        f"jong-bangla-{version}-aur.tar.gz", *(f"package-check-{kind}.json" for kind in ("deb", "rpm", "arch"))}


def verify_packages(directory, version):
    source_hash = hashlib.sha256((directory / f"jong-bangla-{version}.tar.gz").read_bytes()).hexdigest()
    native = json.loads((directory / "build-info.json").read_text())
    for kind, name in package_names(version).items():
        info = json.loads((directory / f"package-check-{kind}.json").read_text())
        builds, runtime = info["builds"], info["runtime"]
        if (len(builds) != 2 or [b["revision"] for b in builds] != [1, 2]
                or any(b["source_sha256"] != source_hash or b["version"] != version
                       or b["format"] != kind or b["source_date_epoch"] != native["source_date_epoch"] for b in builds)
                or builds[0]["package"] != name or runtime["format"] != kind
                or any(runtime[key] is not True for key in (
                    "install_upgrade_remove", "missing_library_rejected", "unrelated_files_preserved"))
                or len(runtime["installed_versions"]) != 2
                or runtime["installed_versions"][0] == runtime["installed_versions"][1]
                or not re.fullmatch(r"[A-Za-z0-9./_-]+@sha256:[0-9a-f]{64}", info["image"])):
            raise ValueError(f"incomplete or mismatched package evidence: {kind}")
        digest = hashlib.sha256((directory / name).read_bytes()).hexdigest()
        if runtime["artifacts"][name] != digest:
            raise ValueError(f"package differs from the tested artifact: {name}")
        if kind == "arch":
            if (builds[0]["maintained_recipe_verified"] is not True
                    or builds[0]["recipe_sha256"] != hashlib.sha256(
                        (directory / f"jong-bangla-{version}-aur.tar.gz").read_bytes()).hexdigest()):
                raise ValueError("AUR recipe differs from the tested recipe or maintained recipe was not verified")
