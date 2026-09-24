"""Offline tests for secret-safe Supabase keep-alive observability."""

import logging

import research_lab.supabase_keepalive_scheduler as scheduler


def main():
    old_interval = scheduler._INTERVAL
    old_last = scheduler._last_attempt
    try:
        scheduler._INTERVAL = 10
        scheduler._last_attempt = 0.0

        assert scheduler.maybe_run_keepalive(
            now=20, check=lambda: {"read_ok": True}
        ) is True
        assert scheduler.maybe_run_keepalive(
            now=25, check=lambda: {"read_ok": True}
        ) is False
        assert scheduler.maybe_run_keepalive(
            now=31, check=lambda: {"read_ok": False, "reason": "secret-detail"}
        ) is True
    finally:
        scheduler._INTERVAL = old_interval
        scheduler._last_attempt = old_last

    print("Supabase keep-alive scheduler tests passed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()
