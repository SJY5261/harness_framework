import json
import os
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "pc_profile.ps1"
POWERSHELL = shutil.which("powershell.exe") or shutil.which("powershell")


def run_profile(marker: Path, desktop: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    assert POWERSHELL, "Windows PowerShell is required"
    command = [
        POWERSHELL,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(SCRIPT),
        "-MarkerPath",
        str(marker),
        "-DesktopPath",
        str(desktop),
        *arguments,
        "-Json",
    ]
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def parse_output(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    return json.loads(result.stdout.lstrip("\ufeff").strip())


def same_path(left: str, right: Path) -> bool:
    return os.path.normcase(os.path.normpath(left)) == os.path.normcase(os.path.normpath(str(right)))


def test_missing_marker_is_unknown_and_has_no_artifact_root(tmp_path: Path) -> None:
    marker = tmp_path / "missing" / "pc-profile.json"
    result = run_profile(marker, tmp_path / "Desktop")

    assert result.returncode == 2, result.stderr
    output = parse_output(result)
    assert output["profile"] == "unknown"
    assert output["configured"] is False
    assert output["reason"] == "marker_missing"
    assert output["artifact_root"] is None


def test_set_work_writes_minimal_bomless_marker_and_work_path(tmp_path: Path) -> None:
    marker = tmp_path / "profile" / "pc-profile.json"
    desktop = tmp_path / "Desktop"
    result = run_profile(marker, desktop, "-SetProfile", "work")

    assert result.returncode == 0, result.stderr
    output = parse_output(result)
    assert output["profile"] == "work"
    assert output["configured"] is True
    assert output["reason"] == "configured"
    assert same_path(str(output["artifact_root"]), desktop / "PR")

    marker_bytes = marker.read_bytes()
    assert not marker_bytes.startswith(b"\xef\xbb\xbf")
    assert json.loads(marker_bytes.decode("utf-8")) == {
        "schema_version": 1,
        "profile": "work",
    }


def test_set_personal_returns_personal_artifact_path(tmp_path: Path) -> None:
    marker = tmp_path / "profile" / "pc-profile.json"
    desktop = tmp_path / "Desktop"
    result = run_profile(marker, desktop, "-SetProfile", "personal")

    assert result.returncode == 0, result.stderr
    output = parse_output(result)
    assert output["profile"] == "personal"
    assert same_path(str(output["artifact_root"]), desktop / "Tomes" / "PR")


def test_invalid_marker_fails_closed(tmp_path: Path) -> None:
    marker = tmp_path / "profile" / "pc-profile.json"
    marker.parent.mkdir(parents=True)
    marker.write_text('{"schema_version":1,"profile":"office"}', encoding="utf-8")

    result = run_profile(marker, tmp_path / "Desktop")

    assert result.returncode == 2, result.stderr
    output = parse_output(result)
    assert output["profile"] == "unknown"
    assert output["reason"] == "marker_invalid"
    assert output["artifact_root"] is None
