#!/usr/bin/env python3
"""Block newly committed or pushed sensitive data without printing secret values."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import PurePosixPath


MAX_BLOB_BYTES = 2 * 1024 * 1024
ZERO_SHA = "0" * 40

BLOCKED_NAMES = {
    "credentials.json",
    "secrets.json",
    "settings.local.json",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "id_rsa",
}
BLOCKED_SUFFIXES = {
    ".7z",
    ".backup",
    ".bak",
    ".bmp",
    ".db",
    ".doc",
    ".docx",
    ".dump",
    ".gif",
    ".gz",
    ".jpeg",
    ".jpg",
    ".jks",
    ".kdbx",
    ".key",
    ".keystore",
    ".p12",
    ".pdf",
    ".pem",
    ".pfx",
    ".png",
    ".ppt",
    ".pptx",
    ".rar",
    ".sqlite",
    ".sqlite3",
    ".tar",
    ".tgz",
    ".webp",
    ".xls",
    ".xlsx",
    ".zip",
}

TOKEN_PATTERNS = (
    (
        "private key",
        re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----"),
    ),
    (
        "AWS access key",
        re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    ),
    (
        "GitHub token",
        re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b"),
    ),
    (
        "Google API key",
        re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    ),
    (
        "Slack token",
        re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b"),
    ),
    (
        "live payment key",
        re.compile(r"\b(?:sk|rk)_live_[0-9A-Za-z]{16,}\b"),
    ),
    (
        "JWT",
        re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    ),
    (
        "credential in URL",
        re.compile(
            r"(?i)\b(?:https?|mariadb|mysql|postgres(?:ql)?|redis)://"
            r"[^/\s:@]+:[^@\s/]{4,}@"
        ),
    ),
)

SENSITIVE_KEY = (
    r"[A-Za-z0-9_.-]*(?:password|passwd|pwd|token|api[_-]?key|secret|"
    r"client[_-]?secret|access[_-]?key|private[_-]?key)[A-Za-z0-9_.-]*"
)
QUOTED_ASSIGNMENT = re.compile(
    rf"""(?ix)
    \b{SENSITIVE_KEY}\b
    \s*(?:=|:)\s*
    (?P<quote>["'])
    (?P<value>[^"'\r\n]{{8,}})
    (?P=quote)
    """
)
UNQUOTED_ASSIGNMENT = re.compile(
    rf"""(?ix)
    \b{SENSITIVE_KEY}\b
    \s*(?:=|:)\s*
    (?P<value>[A-Za-z0-9_./+@#$%(){{}}$:-]{{8,}})
    """
)

PLACEHOLDER_WORDS = {
    "changeme",
    "dummy",
    "example",
    "masked",
    "none",
    "not_set",
    "null",
    "placeholder",
    "redacted",
    "sample",
}
SAFE_VALUE_PREFIXES = (
    "${",
    "{{",
    "<",
    "args.",
    "config.",
    "env[",
    "getenv(",
    "os.environ",
    "os.getenv",
    "process.env",
    "system.getenv",
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    kind: str


class GuardError(RuntimeError):
    """Raised when Git cannot provide the content that must be inspected."""


def _git_bytes(args: list[str]) -> bytes:
    result = subprocess.run(
        ["git", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise GuardError(detail or f"git {' '.join(args)} failed")
    return result.stdout


def _git_text(args: list[str]) -> str:
    return _git_bytes(args).decode("utf-8", errors="replace")


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").lstrip('"')


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _is_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in PLACEHOLDER_WORDS:
        return True
    if normalized.startswith(SAFE_VALUE_PREFIXES):
        return True
    return any(word in normalized for word in ("placeholder", "redacted", "example"))


def scan_blob(path: str, data: bytes) -> list[Finding]:
    """Return metadata-only findings; never include a detected value."""
    normalized_path = _normalize_path(path)
    pure_path = PurePosixPath(normalized_path)
    name = pure_path.name.lower()
    suffix = pure_path.suffix.lower()
    findings: list[Finding] = []

    if name == ".env" or (
        name.startswith(".env.") and name not in {".env.example", ".env.sample"}
    ):
        findings.append(Finding(normalized_path, 0, "environment file"))
    if name in BLOCKED_NAMES or name.startswith(("credentials.", "secrets.")):
        findings.append(Finding(normalized_path, 0, "credential file name"))
    if suffix in BLOCKED_SUFFIXES:
        findings.append(Finding(normalized_path, 0, "binary, backup, or key file"))
    if len(data) > MAX_BLOB_BYTES:
        findings.append(Finding(normalized_path, 0, "file exceeds the scan size limit"))

    if findings:
        return findings
    if b"\0" in data:
        return [Finding(normalized_path, 0, "unreviewable binary content")]

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return [Finding(normalized_path, 0, "non-UTF-8 content")]

    for kind, pattern in TOKEN_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                Finding(normalized_path, _line_number(text, match.start()), kind)
            )

    assignment_offsets: set[int] = set()
    for pattern in (QUOTED_ASSIGNMENT, UNQUOTED_ASSIGNMENT):
        for match in pattern.finditer(text):
            if match.start() in assignment_offsets:
                continue
            if _is_placeholder(match.group("value")):
                continue
            assignment_offsets.add(match.start())
            findings.append(
                Finding(
                    normalized_path,
                    _line_number(text, match.start()),
                    "hard-coded credential assignment",
                )
            )

    return findings


def _staged_entries() -> list[tuple[str, bytes]]:
    raw_paths = _git_bytes(
        ["diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"]
    )
    entries: list[tuple[str, bytes]] = []
    for raw_path in raw_paths.split(b"\0"):
        if not raw_path:
            continue
        path = raw_path.decode("utf-8", errors="surrogateescape")
        entries.append((path, _git_bytes(["cat-file", "blob", f":{path}"])))
    return entries


def _new_commit_shas(updates: str) -> list[str]:
    commits: set[str] = set()
    for line in updates.splitlines():
        fields = line.split()
        if len(fields) != 4:
            continue
        _local_ref, local_sha, _remote_ref, remote_sha = fields
        if local_sha == ZERO_SHA:
            continue
        if remote_sha != ZERO_SHA:
            revision_args = ["rev-list", f"{remote_sha}..{local_sha}"]
        else:
            revision_args = ["rev-list", local_sha, "--not", "--remotes"]
        commits.update(_git_text(revision_args).splitlines())
    return sorted(commits)


def _commit_entries(commit_shas: list[str]) -> list[tuple[str, bytes]]:
    entries: list[tuple[str, bytes]] = []
    seen: set[tuple[str, str]] = set()
    for commit_sha in commit_shas:
        raw_paths = _git_bytes(
            [
                "diff-tree",
                "--root",
                "--no-commit-id",
                "--name-only",
                "--diff-filter=ACMR",
                "-r",
                "-m",
                "-z",
                commit_sha,
            ]
        )
        for raw_path in raw_paths.split(b"\0"):
            if not raw_path:
                continue
            path = raw_path.decode("utf-8", errors="surrogateescape")
            identity = (commit_sha, path)
            if identity in seen:
                continue
            seen.add(identity)
            entries.append(
                (path, _git_bytes(["cat-file", "blob", f"{commit_sha}:{path}"]))
            )
    return entries


def scan_entries(entries: list[tuple[str, bytes]]) -> list[Finding]:
    findings: list[Finding] = []
    for path, data in entries:
        findings.extend(scan_blob(path, data))
    return findings


def report(findings: list[Finding]) -> int:
    if not findings:
        return 0

    print("민감정보 보호 훅이 커밋 또는 푸시를 차단했습니다.", file=sys.stderr)
    for finding in findings[:20]:
        location = f"{finding.path}:{finding.line}" if finding.line else finding.path
        print(f"- {location} [{finding.kind}]", file=sys.stderr)
    if len(findings) > 20:
        print(f"- 그 밖의 탐지 {len(findings) - 20}건", file=sys.stderr)
    print(
        "민감값은 출력하지 않았습니다. 환경변수·보안 저장소로 옮기거나 "
        "공개 가능한 정제 텍스트로 교체한 뒤 다시 시도하세요.",
        file=sys.stderr,
    )
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--staged", action="store_true")
    mode.add_argument("--pre-push", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.staged:
            entries = _staged_entries()
        else:
            entries = _commit_entries(_new_commit_shas(sys.stdin.read()))
        return report(scan_entries(entries))
    except GuardError as exc:
        print(f"민감정보 검사를 완료하지 못해 작업을 차단합니다: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
