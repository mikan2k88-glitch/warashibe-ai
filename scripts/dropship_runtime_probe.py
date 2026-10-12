from __future__ import annotations

import json

from dropship.runtime_probe import run_runtime_probe


def main():
    result = run_runtime_probe()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if result["live_execution_allowed"]:
        raise SystemExit("live execution must remain disabled")
    if result["status"] != "runtime_probe_ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
