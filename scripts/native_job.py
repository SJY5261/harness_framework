#!/usr/bin/env python3
"""Run a native command from a JSON job without shell re-parsing.

The job file is the argument boundary. Complex JavaScript, SQL, JSON, and
regular expressions belong in a separate file referenced by ``stdin_path``.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _resolve(base: Path, raw: str) -> Path:
    path = Path(raw)
    return path.resolve() if path.is_absolute() else (base / path).resolve()


def run_job(job_path: Path) -> int:
    job_path = job_path.resolve()
    job = json.loads(job_path.read_text(encoding="utf-8"))
    if job.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")

    argv = job.get("argv")
    if not isinstance(argv, list) or not argv or not all(isinstance(arg, str) for arg in argv):
        raise ValueError("argv must be a non-empty string array")

    base = job_path.parent
    cwd = _resolve(base, job.get("cwd", "."))
    if not cwd.is_dir():
        raise FileNotFoundError(f"working directory does not exist: {cwd}")

    stdin_handle = None
    try:
        if raw_stdin := job.get("stdin_path"):
            stdin_path = _resolve(base, raw_stdin)
            stdin_handle = stdin_path.open("rb")

        timeout = job.get("timeout_seconds")
        if timeout is not None and (not isinstance(timeout, (int, float)) or timeout <= 0):
            raise ValueError("timeout_seconds must be a positive number")

        completed = subprocess.run(
            argv,
            cwd=cwd,
            stdin=stdin_handle,
            check=False,
            shell=False,
            timeout=timeout,
        )
        return completed.returncode
    finally:
        if stdin_handle is not None:
            stdin_handle.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job", type=Path, help="UTF-8 JSON job file")
    args = parser.parse_args()
    try:
        return run_job(args.job)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        print(f"native job failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
