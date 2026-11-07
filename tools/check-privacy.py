#!/usr/bin/env python3
"""Conservative source tripwires, not a parser, dataflow analysis or sandbox.

Scan first-party Rust/native runtime sources, including future adapter folders.
Comments and strings are deliberately scanned too. Also scan a comment-stripped
view to catch split tokens. Diagnostics never echo source or typed text.
"""

from pathlib import Path
import re
import sys


SOURCE_SUFFIXES = {".rs", ".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}
TEST_ONLY_FILES = {Path("adapters/fcitx5/ffi/src/panic_tests.rs")}
PATH_SEP = r"\s*::\s*"


def alternatives(names):
    return r"(?:" + "|".join(re.escape(name) for name in names.split()) + r")"


# Ban both imports and qualified paths, including common grouped Rust imports.
RUST_MODULES = alternatives("net fs io process env")
RULES = {
    "rust-io": rf"\bstd{PATH_SEP}(?:\{{[^;]*?\b)?{RUST_MODULES}\b",
    "network-crate": rf"\b{alternatives('reqwest hyper hyper_util ureq curl curl_sys attohttpc isahc surf tokio async_std smol mio socket2 quinn tungstenite hickory_resolver trust_dns_resolver')}{PATH_SEP}",
    "telemetry": rf"\b{alternatives('sentry sentry_core opentelemetry opentelemetry_sdk opentelemetry_otlp')}{PATH_SEP}",
    "rust-diagnostics": rf"\b{alternatives('print println eprint eprintln dbg')}\s*!",
    "rust-logging": rf"\b{alternatives('log tracing')}{PATH_SEP}",
    "native-network-header": r"#\s*include\s*[<\"](?:sys/socket\.h|netinet/[^>\"]+|arpa/[^>\"]+|netdb\.h|curl/[^>\"]+|boost/asio[^>\"]*|asio[^>\"]*|winsock[^>\"]*|winhttp\.h|wininet\.h|QtNetwork/[^>\"]+)[>\"]",
    "network-call": rf"\b{alternatives('socket socketpair connect bind listen accept accept4 send sendto sendmsg recv recvfrom recvmsg getaddrinfo gethostbyname curl_easy_init curl_easy_perform curl_multi_perform WinHttpOpen WinHttpSendRequest InternetOpen InternetOpenA InternetOpenW URLDownloadToFile QNetworkAccessManager QTcpSocket QUdpSocket')}\s*\(",
    "native-persistence": rf"\b{alternatives('fopen fopen64 freopen open open64 openat creat fwrite fprintf fputs fputc write pwrite CreateFile CreateFileA CreateFileW WriteFile RegSetValueExA RegSetValueExW')}\s*\(",
    "native-streams": r"\b(?:std\s*::\s*)?(?:ofstream|fstream|cout|cerr|clog|wcout|wcerr|wclog)\b",
    "native-diagnostics": rf"\b{alternatives('printf puts putchar perror syslog vsyslog OutputDebugStringA OutputDebugStringW qDebug qInfo qWarning qCritical')}\s*\(|\bFCITX_(?:DEBUG|INFO|WARN|WARNING|ERROR|FATAL|LOG)\b|\bspdlog\s*::",
    "process-call": rf"\b{alternatives('system popen execve execl execlp execv execvp posix_spawn ShellExecuteA ShellExecuteW CreateProcessA CreateProcessW')}\s*\(",
}
CORE_RULES = {
    "core-global": r"\bstatic\s+(?:mut\s+)?\w+\s*:|\bthread_local\s*!",
    "core-shared-state": rf"\b{alternatives('Mutex RwLock OnceLock LazyLock AtomicBool AtomicUsize AtomicU64')}\b",
    "core-platform": r"\bextern\s*(?:\"[^\"]*\")?\s*\{|\b(?:libc|windows|winapi|fcitx|nix)\s*::",
}


def violations(relative, content):
    # This is intentionally conservative. It does not interpret literals, nested
    # comments, macros, conditional compilation or language name resolution.
    stripped = re.sub(r"/\*.*?\*/|//[^\n]*", lambda match: " " + "\n" * match[0].count("\n"), content, flags=re.S)
    rules = RULES | (CORE_RULES if relative.parts[0] == "src" else {})
    findings = []
    for rule, pattern in rules.items():
        for view in (content, stripped):
            match = re.search(pattern, view)
            if match:
                line = view.count("\n", 0, match.start()) + 1
                findings.append((line, rule))
                break
    return findings


def source_paths(root):
    for directory in (root / "src", root / "adapters"):
        if not directory.is_dir():
            raise ValueError(f"missing source directory: {directory.name}")
        for path in sorted(directory.rglob("*")):
            relative = path.relative_to(root)
            # Native test harnesses intentionally use synthetic diagnostics/I/O.
            # Inline Rust tests remain scanned; no in-source suppression exists.
            if ("tests" not in relative.parts and relative not in TEST_ONLY_FILES
                    and path.suffix.lower() in SOURCE_SUFFIXES):
                yield path


def main():
    root = Path.cwd()
    failed = False
    count = 0
    try:
        for path in source_paths(root):
            count += 1
            relative = path.relative_to(root)
            for line, rule in violations(relative, path.read_text(encoding="utf-8")):
                print(f"FAIL: {relative}:{line}: {rule}", file=sys.stderr)
                failed = True
        if count == 0:
            raise ValueError("no runtime sources found")
    except (OSError, UnicodeError, ValueError) as error:
        print(f"FAIL: privacy scan could not complete: {error}", file=sys.stderr)
        return 1
    if failed:
        return 1
    print(f"PASS: privacy tripwires checked {count} Rust/native source files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
