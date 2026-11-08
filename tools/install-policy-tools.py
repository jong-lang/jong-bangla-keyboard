#!/usr/bin/env python3
"""Install pinned CI policy binaries, with a checksummed official API fallback."""

import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile


# Asset IDs identify the same upstream files as the browser URLs. Neither API
# metadata nor an HTTP success may replace these independently reviewed hashes.
TOOLS = (
    ("cargo-deny", "EmbarkStudios/cargo-deny", "0.20.2",
     "cargo-deny-0.20.2-x86_64-unknown-linux-musl.tar.gz", 471598214,
     "9f12ed4c49936e09b48bf862b595cde2fe64fcbd9d74dfacac6131ca824c8d5f",
     "cargo-deny-0.20.2-x86_64-unknown-linux-musl/cargo-deny"),
    ("cargo-audit", "rustsec/rustsec", "cargo-audit/v0.22.2",
     "cargo-audit-x86_64-unknown-linux-musl-v0.22.2.tgz", 439292222,
     "7fb9497f8594b389e5fce5ef9b92db08432996895b2e0c5a0167a69ed445c428",
     "cargo-audit-x86_64-unknown-linux-musl-v0.22.2/cargo-audit"),
)


def download(repository, tag, filename, asset_id, destination):
    urls = (
        (f"https://github.com/{repository}/releases/download/{tag}/{filename}", []),
        (f"https://api.github.com/repos/{repository}/releases/assets/{asset_id}",
         ["--header", "Accept: application/octet-stream"]),
    )
    for index, (url, headers) in enumerate(urls):
        try:
            subprocess.run([
                "curl", "--fail", "--location", "--silent", "--show-error",
                "--proto", "=https", "--proto-redir", "=https",
                "--connect-timeout", "15", "--max-time", "45",
                "--retry", "2", "--retry-delay", "5",
                *headers, "--output", str(destination), url,
            ], check=True)
            return
        except subprocess.CalledProcessError:
            destination.unlink(missing_ok=True)
            if index == len(urls) - 1:
                raise
            print(f"Browser download failed for {filename}; trying official asset API", flush=True)


def install(output):
    if output.exists() or output.is_symlink():
        raise ValueError("output must not exist")
    binaries = {}
    with tempfile.TemporaryDirectory(prefix="jong-policy-") as temporary:
        for name, repository, tag, filename, asset_id, digest, member_name in TOOLS:
            archive_path = Path(temporary) / filename
            download(repository, tag, filename, asset_id, archive_path)
            if hashlib.sha256(archive_path.read_bytes()).hexdigest() != digest:
                # Unexpected bytes are not a transport error. Never fall back
                # or extract anything after a checksum failure.
                raise ValueError(f"SHA-256 mismatch: {filename}")
            with tarfile.open(archive_path) as archive:
                members = [member for member in archive if member.name == member_name]
                if len(members) != 1 or not members[0].isfile():
                    raise ValueError(f"expected one regular binary: {member_name}")
                binaries[name] = archive.extractfile(members[0]).read()
                if not binaries[name]:
                    raise ValueError(f"empty binary: {member_name}")
            print(f"PASS: pinned SHA-256 verified for {filename}", flush=True)
    # Install only after both archives pass. Archive paths, links, ownership and
    # modes are ignored; only the selected regular binaries' bytes are written.
    output.mkdir(parents=True)
    for name, content in binaries.items():
        path = output / name
        path.write_bytes(content)
        path.chmod(0o755)
    print(f"PASS: pinned policy tools installed in {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        install(args.output)
    except (OSError, ValueError, tarfile.TarError, subprocess.CalledProcessError) as error:
        sys.exit(f"FAIL: {error}")


if __name__ == "__main__":
    main()
