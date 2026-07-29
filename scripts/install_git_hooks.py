#!/usr/bin/env python3
"""Activate the repository-owned Git hooks for the current clone."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


HOOKS_PATH = ".codex/git-hooks"


def _run_git(args: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def install(cwd: Path | None = None) -> Path:
    root = Path(_run_git(["rev-parse", "--show-toplevel"], cwd=cwd))
    hooks_dir = root / HOOKS_PATH
    required = (hooks_dir / "pre-commit", hooks_dir / "pre-push")
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"missing hook files: {', '.join(missing)}")

    _run_git(["config", "--local", "core.hooksPath", HOOKS_PATH], cwd=root)
    configured = _run_git(["config", "--local", "--get", "core.hooksPath"], cwd=root)
    if configured != HOOKS_PATH:
        raise RuntimeError(f"unexpected core.hooksPath: {configured}")
    return root


def main() -> int:
    try:
        root = install()
    except RuntimeError as exc:
        print(f"Git 훅 설치 실패: {exc}", file=sys.stderr)
        return 1
    print(f"Git 민감정보 보호 훅 활성화: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
