from __future__ import annotations

import json

from dropship.provider_handshake import run_provider_handshake


def main():
    result = run_provider_handshake()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if result["live_execution_allowed"]:
        raise SystemExit("live execution must remain disabled")
    if result["configured_provider_count"] > 0 and result["successful_provider_count"] == 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
