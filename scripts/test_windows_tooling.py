import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import native_job
import sqlite_query
import text_eol


def test_native_job_preserves_quotes_and_working_directory(tmp_path, capfd):
    working = tmp_path / "working directory"
    working.mkdir()
    probe = tmp_path / "probe.py"
    probe.write_text(
        "import json, os, sys\nprint(json.dumps({'arg': sys.argv[1], 'cwd': os.getcwd()}))\n",
        encoding="utf-8",
    )
    expected = "({single: 'value', double: \"quoted value\"})"
    job = tmp_path / "job.json"
    job.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "cwd": str(working),
                "argv": [sys.executable, str(probe), expected],
            }
        ),
        encoding="utf-8",
    )

    assert native_job.run_job(job) == 0
    output = json.loads(capfd.readouterr().out)
    assert output["arg"] == expected
    assert Path(output["cwd"]) == working


def test_native_job_passes_stdin_without_shell_parsing(tmp_path):
    source = tmp_path / "source.js"
    source.write_text("const value = 'single \\\"double\\\"';\n", encoding="utf-8")
    output = tmp_path / "output.bin"
    copier = tmp_path / "copier.py"
    copier.write_text(
        "import pathlib, sys\npathlib.Path(sys.argv[1]).write_bytes(sys.stdin.buffer.read())\n",
        encoding="utf-8",
    )
    job = tmp_path / "job.json"
    job.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "argv": [sys.executable, str(copier), str(output)],
                "stdin_path": str(source),
            }
        ),
        encoding="utf-8",
    )

    assert native_job.run_job(job) == 0
    assert output.read_bytes() == source.read_bytes()


def test_sqlite_query_is_parameterized_and_read_only(tmp_path):
    database = tmp_path / "history.sqlite"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE downloads (target_path TEXT, tab_url TEXT)")
        connection.execute("INSERT INTO downloads VALUES (?, ?)", ("p'081.jpg", "KAN-48"))
    sql = tmp_path / "query.sql"
    sql.write_text(
        "SELECT target_path, tab_url FROM downloads WHERE target_path = :filename",
        encoding="utf-8",
    )

    rows = sqlite_query.query(database, sql, {"filename": "p'081.jpg"})
    assert rows == [{"target_path": "p'081.jpg", "tab_url": "KAN-48"}]


def test_sqlite_query_snapshots_a_locked_database(tmp_path, monkeypatch):
    database = tmp_path / "locked.sqlite"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE sample (value TEXT)")
        connection.execute("INSERT INTO sample VALUES ('quoted')")
    sql = tmp_path / "query.sql"
    sql.write_text("SELECT value FROM sample", encoding="utf-8")
    original_execute = sqlite_query._execute
    calls = {"count": 0}

    def locked_once(path, statement, parameters):
        calls["count"] += 1
        if calls["count"] == 1:
            raise sqlite3.OperationalError("database is locked")
        return original_execute(path, statement, parameters)

    monkeypatch.setattr(sqlite_query, "_execute", locked_once)
    assert sqlite_query.query(database, sql, {}) == [{"value": "quoted"}]
    assert calls["count"] == 2


def test_eol_normalization_preserves_bom_and_eof():
    original = b"\xef\xbb\xbffirst\r\nsecond\nlast"
    fixed = text_eol.normalize(original, "crlf")
    assert fixed == b"\xef\xbb\xbffirst\r\nsecond\r\nlast"
    assert text_eol.classify(fixed) == "crlf"


def test_eol_attribute_overrides_autocrlf(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "core.autocrlf", "true"], cwd=tmp_path, check=True)
    (tmp_path / ".gitattributes").write_text("*.py text eol=lf\n", encoding="utf-8")
    target = tmp_path / "sample.py"
    target.write_bytes(b"first\r\nsecond\n")

    assert text_eol.expected_eol(tmp_path, "sample.py", target.read_bytes()) == "lf"
    assert text_eol.process(tmp_path, ["sample.py"], fix=True) == 0
    assert target.read_bytes() == b"first\nsecond\n"


def test_eol_defaults_to_current_majority_when_autocrlf_is_false(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=tmp_path, check=True)
    target = tmp_path / "sample.txt"
    target.write_bytes(b"first\r\nsecond\r\nthird\n")

    assert text_eol.expected_eol(tmp_path, "sample.txt", target.read_bytes()) == "crlf"
