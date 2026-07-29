"""Regression tests for the public-fork sensitive-data guard."""

import importlib.util
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "secret_guard.py"
INSTALLER = ROOT / "scripts" / "install_git_hooks.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


guard = _load("secret_guard", SCRIPT)
installer = _load("install_git_hooks", INSTALLER)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return result.stdout.strip()


def _init_repo(path: Path) -> None:
    _git(path, "init", "-q")
    _git(path, "config", "user.name", "Secret Guard Test")
    _git(path, "config", "user.email", "secret-guard@example.invalid")


def _sensitive_payload() -> tuple[str, str]:
    sample_value = "".join(("N0t", "-a-real-", "credential"))
    key_name = "DB_" + "PASSWORD"
    return f'{key_name} = "{sample_value}"\n', sample_value


def test_detects_hardcoded_assignment_without_printing_value(capsys):
    payload, sample_value = _sensitive_payload()
    findings = guard.scan_blob("config.py", payload.encode("utf-8"))

    assert any(item.kind == "hard-coded credential assignment" for item in findings)
    assert guard.report(findings) == 1
    output = capsys.readouterr().err
    assert "config.py:1" in output
    assert sample_value not in output


def test_allows_environment_lookup_and_documented_placeholder():
    content = (
        'DB_PASSWORD = os.environ.get("DB_PASSWORD")\n'
        'api_key: "placeholder"\n'
    )

    assert guard.scan_blob("config.py", content.encode("utf-8")) == []


def test_blocks_env_and_binary_files():
    assert guard.scan_blob(".env.local", b"SAFE=1")
    assert guard.scan_blob("logs/screenshot.png", b"\x89PNG\r\n\x1a\n")


def test_staged_cli_blocks_secret_and_hides_value(tmp_path):
    _init_repo(tmp_path)
    safe = tmp_path / "safe.txt"
    safe.write_text("safe\n", encoding="utf-8")
    _git(tmp_path, "add", "safe.txt")
    _git(tmp_path, "commit", "-qm", "initial")

    payload, sample_value = _sensitive_payload()
    config = tmp_path / "config.py"
    config.write_text(payload, encoding="utf-8")
    _git(tmp_path, "add", "config.py")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--staged"],
        cwd=tmp_path,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 1
    assert "config.py:1" in result.stderr
    assert sample_value not in result.stderr


def test_pre_push_cli_scans_each_new_commit(tmp_path):
    _init_repo(tmp_path)
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("safe\n", encoding="utf-8")
    _git(tmp_path, "add", "tracked.txt")
    _git(tmp_path, "commit", "-qm", "initial")
    remote_sha = _git(tmp_path, "rev-parse", "HEAD")

    payload, sample_value = _sensitive_payload()
    tracked.write_text(payload, encoding="utf-8")
    _git(tmp_path, "add", "tracked.txt")
    _git(tmp_path, "commit", "-qm", "unsafe")
    local_sha = _git(tmp_path, "rev-parse", "HEAD")
    update = (
        f"refs/heads/main {local_sha} refs/heads/main {remote_sha}\n"
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--pre-push"],
        cwd=tmp_path,
        input=update,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 1
    assert "tracked.txt:1" in result.stderr
    assert sample_value not in result.stderr


def test_installer_activates_repository_hooks(tmp_path):
    _init_repo(tmp_path)
    hooks = tmp_path / ".codex" / "git-hooks"
    hooks.mkdir(parents=True)
    (hooks / "pre-commit").write_text("#!/bin/sh\n", encoding="utf-8")
    (hooks / "pre-push").write_text("#!/bin/sh\n", encoding="utf-8")

    assert installer.install(tmp_path) == tmp_path
    assert _git(tmp_path, "config", "--local", "--get", "core.hooksPath") == (
        ".codex/git-hooks"
    )


def test_tracked_hooks_call_both_guard_modes():
    assert "--staged" in (ROOT / ".codex/git-hooks/pre-commit").read_text(
        encoding="utf-8"
    )
    assert "--pre-push" in (ROOT / ".codex/git-hooks/pre-push").read_text(
        encoding="utf-8"
    )
