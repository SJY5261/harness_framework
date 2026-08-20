#!/usr/bin/env python3
"""Check or normalize changed text files to Git's declared worktree EOL."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def _git_config(repo: Path, name: str) -> str:
    result = subprocess.run(
        ["git", "config", "--get", name],
        cwd=repo,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode not in {0, 1}:
        raise RuntimeError(result.stderr.strip() or f"git config --get {name} failed")
    return result.stdout.strip()


def _changed_paths(repo: Path) -> list[str]:
    paths: set[str] = set()
    for args in (
        ("diff", "--name-only", "--diff-filter=ACMRTUXB"),
        ("diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB"),
        ("ls-files", "--others", "--exclude-standard"),
    ):
        paths.update(line for line in _git(repo, *args).splitlines() if line)
    return sorted(paths)


def _attribute(repo: Path, name: str, path: str) -> str | None:
    output = _git(repo, "check-attr", name, "--", path).rstrip("\n")
    value = output.rsplit(": ", 1)[-1]
    return None if value in {"unspecified", "unset"} else value


def expected_eol(repo: Path, path: str, data: bytes) -> str:
    declared = _attribute(repo, "eol", path)
    if declared in {"lf", "crlf"}:
        return declared

    autocrlf = _git_config(repo, "core.autocrlf").lower()
    if autocrlf == "true":
        return "crlf"
    if autocrlf == "input":
        return "lf"

    crlf = data.count(b"\r\n")
    lone_lf = data.count(b"\n") - crlf
    return "crlf" if crlf > lone_lf else "lf"


def classify(data: bytes) -> str:
    if b"\0" in data:
        return "binary"
    crlf = data.count(b"\r\n")
    lone_lf = data.count(b"\n") - crlf
    lone_cr = data.count(b"\r") - crlf
    kinds = sum(count > 0 for count in (crlf, lone_lf, lone_cr))
    if kinds == 0:
        return "none"
    if kinds > 1 or lone_cr:
        return "mixed"
    return "crlf" if crlf else "lf"


def normalize(data: bytes, eol: str) -> bytes:
    separator = b"\r\n" if eol == "crlf" else b"\n"
    logical = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return logical.replace(b"\n", separator)


def process(repo: Path, paths: list[str], fix: bool) -> int:
    failures = 0
    changed = 0
    root = repo.resolve()
    for relative in paths:
        path = (root / relative).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            print(f"outside repository: {relative}", file=sys.stderr)
            failures += 1
            continue
        if not path.is_file():
            continue
        data = path.read_bytes()
        actual = classify(data)
        if actual in {"binary", "none"}:
            continue
        expected = expected_eol(root, relative, data)
        if actual == expected:
            continue
        if fix:
            path.write_bytes(normalize(data, expected))
            print(f"fixed {relative}: {actual} -> {expected}")
            changed += 1
        else:
            print(f"invalid {relative}: {actual}, expected {expected}")
            failures += 1
    if fix:
        print(f"EOL fixed: {changed} file(s)")
    elif failures == 0:
        print("EOL check passed")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("check", "fix"))
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--changed", action="store_true")
    group.add_argument("--paths", nargs="+")
    args = parser.parse_args()
    try:
        repo = args.repo.resolve()
        paths = _changed_paths(repo) if args.changed else args.paths
        return process(repo, paths, fix=args.mode == "fix")
    except (OSError, RuntimeError) as exc:
        print(f"EOL operation failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
