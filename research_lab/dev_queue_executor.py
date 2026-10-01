from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

QUEUE_URL = "https://bittxuhjejaokfgmymkw.supabase.co/functions/v1/warashibe-dev-queue"
OIDC_AUDIENCE = "warashibe-supabase"
MAX_CONTENT_BYTES = 100_000

_ALLOWED = (
    re.compile(r"^[A-Za-z0-9_]+\.py$"),
    re.compile(r"^routes/[A-Za-z0-9_]+\.py$"),
    re.compile(r"^research_lab/[A-Za-z0-9_]+\.py$"),
)


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=check)


def current_head() -> str:
    return run("git", "rev-parse", "HEAD").stdout.strip()


def get_oidc_token() -> str:
    request_url = os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"]
    request_token = os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]
    separator = "&" if "?" in request_url else "?"
    url = f"{request_url}{separator}audience={OIDC_AUDIENCE}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {request_token}"})
    with urllib.request.urlopen(req, timeout=20) as response:
        payload = json.load(response)
    return payload["value"]


def queue_call(token: str, payload: dict) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        QUEUE_URL,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def allowed_path(raw: str) -> Path:
    if not raw or raw.startswith("/") or ".." in Path(raw).parts:
        raise ValueError("unsafe_path")
    if not any(pattern.fullmatch(raw) for pattern in _ALLOWED):
        raise ValueError("path_not_allowlisted")
    return Path(raw)


def fixed_tests(target: Path) -> tuple[bool, str]:
    checks = [
        [sys.executable, "-m", "py_compile", str(target)],
        [sys.executable, "-m", "research_lab.runner"],
    ]
    logs: list[str] = []
    for command in checks:
        proc = subprocess.run(command, text=True, capture_output=True)
        logs.append("$ " + " ".join(command))
        logs.append(proc.stdout[-2500:])
        logs.append(proc.stderr[-2500:])
        if proc.returncode != 0:
            return False, "\n".join(logs)[-4000:]
    diff_check = run("git", "diff", "--check", check=False)
    logs.append(diff_check.stdout[-1000:])
    logs.append(diff_check.stderr[-1000:])
    return diff_check.returncode == 0, "\n".join(logs)[-4000:]


def restore(path: Path, existed: bool) -> None:
    if existed:
        run("git", "checkout", "--", str(path), check=False)
    else:
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def main() -> int:
    token = get_oidc_token()
    result = queue_call(token, {"action": "next"})
    task = result.get("task")
    if not task:
        queue_call(token, {"action": "cleanup"})
        print("No pending queue item.")
        return 0

    task_id = str(task.get("task_id") or "")
    path: Path | None = None
    existed = False

    try:
        if task.get("base_sha") != current_head():
            queue_call(token, {
                "action": "reject",
                "task_id": task_id,
                "error_message": "base_sha_mismatch",
            })
            return 0

        operation = str(task.get("operation") or "")
        if operation not in {"create", "create_file", "replace", "replace_file", "update_file"}:
            raise ValueError("unsupported_operation")

        path = allowed_path(str(task.get("target_path") or ""))
        content = task.get("content")
        if not isinstance(content, str):
            raise ValueError("content_required")
        if len(content.encode()) > MAX_CONTENT_BYTES:
            raise ValueError("content_too_large")

        existed = path.exists()
        if operation in {"create", "create_file"} and existed:
            raise ValueError("create_target_exists")
        if operation in {"replace", "replace_file", "update_file"} and not existed:
            raise ValueError("replace_target_missing")

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

        ok, test_log = fixed_tests(path)
        if not ok:
            restore(path, existed)
            queue_call(token, {
                "action": "fail",
                "task_id": task_id,
                "test_result": test_log,
                "error_message": "fixed_tests_failed",
            })
            return 1

        changed = run("git", "status", "--porcelain", "--", str(path)).stdout.strip()
        if not changed:
            restore(path, existed)
            queue_call(token, {
                "action": "reject",
                "task_id": task_id,
                "error_message": "no_change",
            })
            return 0

        run("git", "config", "user.name", "warashibe-queue-bot")
        run("git", "config", "user.email", "actions@users.noreply.github.com")
        run("git", "add", "--", str(path))
        run("git", "commit", "-m", f"queue: {task_id}")
        commit_sha = current_head()
        run("git", "push", "origin", "HEAD:research-lab")

        queue_call(token, {
            "action": "complete",
            "task_id": task_id,
            "commit_sha": commit_sha,
            "test_result": test_log,
        })
        queue_call(token, {"action": "cleanup"})
        print(f"Committed {task_id} as {commit_sha}")
        return 0

    except Exception as exc:
        if path is not None:
            restore(path, existed)
        try:
            queue_call(token, {
                "action": "reject",
                "task_id": task_id,
                "error_message": str(exc),
            })
        except Exception:
            pass
        raise


if __name__ == "__main__":
    raise SystemExit(main())
