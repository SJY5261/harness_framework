#!/usr/bin/env python3
"""Run one parameterized query against a SQLite database in read-only mode."""

from __future__ import annotations

import argparse
import contextlib
import json
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path


def _parameters(values: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"parameter must use name=value: {value}")
        name, raw = value.split("=", 1)
        if not name:
            raise ValueError("parameter name must not be empty")
        result[name] = raw
    return result


def _execute(database: Path, sql: str, parameters: dict[str, str]) -> list[dict]:
    uri = f"{database.as_uri()}?mode=ro"
    with contextlib.closing(sqlite3.connect(uri, uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        rows = connection.execute(sql, parameters).fetchall()
        return [dict(row) for row in rows]


def _snapshot(database: Path, destination: Path) -> Path:
    copied = destination / database.name
    shutil.copy2(database, copied)
    for suffix in ("-wal", "-shm", "-journal"):
        sidecar = database.with_name(database.name + suffix)
        if sidecar.is_file():
            shutil.copy2(sidecar, destination / (database.name + suffix))
    return copied


def query(database: Path, query_file: Path, parameters: dict[str, str]) -> list[dict]:
    database = database.resolve()
    sql = query_file.read_text(encoding="utf-8")
    try:
        return _execute(database, sql, parameters)
    except sqlite3.OperationalError as exc:
        if "locked" not in str(exc).lower():
            raise
        with tempfile.TemporaryDirectory(prefix="sqlite-readonly-") as temp_dir:
            copied = _snapshot(database, Path(temp_dir))
            return _execute(copied, sql, parameters)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--query-file", required=True, type=Path)
    parser.add_argument("--param", action="append", default=[], metavar="NAME=VALUE")
    args = parser.parse_args()
    try:
        rows = query(args.database, args.query_file, _parameters(args.param))
        print(json.dumps(rows, ensure_ascii=False, default=str))
        return 0
    except (OSError, ValueError, sqlite3.Error) as exc:
        print(f"SQLite query failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
