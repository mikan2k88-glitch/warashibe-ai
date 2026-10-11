from __future__ import annotations

import json

from dropship.startup_preflight import build_startup_preflight


def main():
    result = build_startup_preflight()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if result["live_execution_allowed"]:
        raise SystemExit("live execution must remain disabled")


if __name__ == "__main__":
    main()
