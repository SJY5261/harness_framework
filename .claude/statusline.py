#!/usr/bin/env python3
"""Claude Code status line: elapsed time, real task progress, and recent activity."""

import json
import sys
from pathlib import Path


for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


TOOL_LABELS = {
    "Bash": "명령 실행",
    "Read": "파일 확인",
    "Edit": "파일 수정",
    "Write": "파일 작성",
    "Glob": "파일 탐색",
    "Grep": "코드 검색",
    "WebFetch": "웹 문서 확인",
    "WebSearch": "웹 검색",
    "Task": "보조 작업",
    "TaskCreate": "계획 등록",
    "TaskUpdate": "계획 갱신",
}


def _one_line(value, limit=54):
    text = " ".join(str(value or "").split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _tool_detail(name, tool_input):
    tool_input = tool_input if isinstance(tool_input, dict) else {}
    label = TOOL_LABELS.get(name, name or "도구 사용")
    detail = (
        tool_input.get("description")
        or tool_input.get("command")
        or tool_input.get("file_path")
        or tool_input.get("path")
        or tool_input.get("pattern")
        or tool_input.get("query")
        or tool_input.get("subject")
        or ""
    )
    return f"{label}: {_one_line(detail)}" if detail else label


def read_transcript(path):
    """Return the latest visible activity and task counts from a JSONL transcript."""
    latest = ""
    created_tasks = 0
    updated_task_ids = set()
    completed_task_ids = set()
    if not path:
        return latest, None

    transcript = Path(path)
    if not transcript.is_file():
        return latest, None

    try:
        with transcript.open("rb") as stream:
            stream.seek(0, 2)
            size = stream.tell()
            stream.seek(max(0, size - 262_144))
            if size > 262_144:
                stream.readline()
            lines = stream.read().decode("utf-8", errors="replace").splitlines()
    except OSError:
        return latest, None

    for raw in lines[-400:]:
        try:
            event = json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            continue

        message = event.get("message", event)
        if message.get("role") != "assistant":
            continue
        content = message.get("content", [])
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        if not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict):
                continue
            block_type = block.get("type")
            if block_type == "text" and block.get("text"):
                latest = _one_line(block["text"])
            elif block_type == "tool_use":
                name = block.get("name", "")
                tool_input = block.get("input", {})
                latest = _tool_detail(name, tool_input)
                if name == "TaskCreate":
                    created_tasks += 1
                elif name == "TaskUpdate":
                    task_id = tool_input.get("taskId")
                    if task_id:
                        updated_task_ids.add(task_id)
                        if tool_input.get("status") == "completed":
                            completed_task_ids.add(task_id)
                        else:
                            completed_task_ids.discard(task_id)

    total_tasks = max(created_tasks, len(updated_task_ids))
    if total_tasks:
        return latest, (min(len(completed_task_ids), total_tasks), total_tasks)
    return latest, None


def format_duration(milliseconds):
    seconds = max(0, int((milliseconds or 0) / 1000))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"


def build_status(data):
    cost = data.get("cost", {})
    context = data.get("context_window", {})
    elapsed = format_duration(cost.get("total_duration_ms", 0))
    used = int(context.get("used_percentage", 0) or 0)
    latest, task_progress = read_transcript(data.get("transcript_path"))

    parts = [f"[작업 {elapsed}]"]
    if task_progress:
        parts.append(f"계획 {task_progress[0]}/{task_progress[1]}")
    if latest:
        parts.append(f"현재: {latest}")
    else:
        parts.append("현재: 응답 준비")
    parts.append(f"context {used}%")

    total_cost = cost.get("total_cost_usd")
    if isinstance(total_cost, (int, float)):
        parts.append(f"${total_cost:.2f}")
    return " | ".join(parts)


def main():
    try:
        data = json.load(sys.stdin)
        print(build_status(data))
    except Exception as exc:
        print(f"[상태 확인 불가] {type(exc).__name__}")


if __name__ == "__main__":
    main()
