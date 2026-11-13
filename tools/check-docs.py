#!/usr/bin/env python3
"""Check repository Markdown links, anchors, fences and shell example syntax."""

from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit


def without_fences(content):
    return re.sub(r"^```[^\n]*\n.*?^```[^\n]*$", "", content, flags=re.M | re.S)


def anchors(content):
    counts = {}
    result = set()
    for heading in re.finditer(r"^#{1,6} (.+)$", without_fences(content), re.M):
        label = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", heading[1])
        slug = re.sub(r"[^\w -]", "", label.lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        result.add(f"{slug}-{count}" if count else slug)
        counts[slug] = count + 1
    return result


def main():
    names = subprocess.check_output([
        "git", "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", "*.md",
    ]).decode().split("\0")
    links = shells = files = 0
    for name in filter(None, names):
        source = Path(name)
        content = source.read_text(encoding="utf-8")
        budget = {"AGENTS.md": 120, "README.md": 80}.get(name)
        if budget and len(content.splitlines()) > budget:
            sys.exit(f"FAIL: {name}: exceeds {budget}-line budget")
        if name == "CLAUDE.md" and (len(content.splitlines()) != 1
                                   or re.findall(r"\[[^\]]+\]\(([^)]+)\)", content) != ["AGENTS.md"]):
            sys.exit("FAIL: CLAUDE.md must contain only a link to AGENTS.md")
        if len(re.findall(r"^```", content, re.M)) % 2:
            sys.exit(f"FAIL: {name}: unbalanced code fences")
        files += 1
        for match in re.finditer(r"!?\[[^\]]+\]\(([^\s)]+)\)", without_fences(content)):
            link = match[1]
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc:
                continue
            target = source.parent / unquote(parsed.path) if parsed.path else source
            if not target.exists():
                sys.exit(f"FAIL: {name}: missing link target: {link}")
            if parsed.fragment and target.suffix == ".md":
                if unquote(parsed.fragment) not in anchors(target.read_text(encoding="utf-8")):
                    sys.exit(f"FAIL: {name}: missing heading anchor: {link}")
            links += 1
        for block in re.findall(r"^```(?:sh|bash)\n(.*?)^```", content, re.M | re.S):
            result = subprocess.run(["bash", "-n"], input=block, text=True, capture_output=True)
            if result.returncode:
                sys.exit(f"FAIL: {name}: shell example syntax: {result.stderr.strip()}")
            shells += 1
    print(f"PASS: {files} Markdown files, {links} local links/anchors, fences and {shells} shell examples")
    print("External URLs and shell example execution are not checked.")


if __name__ == "__main__":
    main()
