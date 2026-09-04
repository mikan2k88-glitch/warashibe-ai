```python
# ============================================================
# Warashibe AI
# test_runner.py
#
# 開発用一括テスト
#
# 使い方：
#     python test_runner.py
#
# 出力された結果を、そのままChatGPTへコピペする。
# ============================================================

import json
import py_compile
import traceback
from pathlib import Path


ROOT = Path(__file__).resolve().parent

REQUIRED_FILES = [
    "app.py",
    "simulation_engine.py",
    "market_engine.py",
    "policy_engine.py",
    "analysis_engine.py",
]

OPTIONAL_FILES = [
    "strategy_engine.py",
]

STRATEGIES = [
    "random",
    "safe",
    "balanced",
    "aggressive",
]


results = {
    "status": "PASSED",
    "checks": {},
    "simulation": {},
    "strategy_tests": {},
    "errors": [],
}


def check(condition, name, detail=""):
    results["checks"][name] = {
        "passed": bool(condition),
        "detail": detail,
    }

    if not condition:
        results["status"] = "FAILED"
        results["errors"].append(
            f"{name}: {detail}"
        )


def test_syntax():
    for filename in REQUIRED_FILES + OPTIONAL_FILES:
        path = ROOT / filename

        if not path.exists():
            if filename in OPTIONAL_FILES:
                continue

            check(
                False,
                f"file:{filename}",
                "ファイルが存在しません",
            )
            continue

        try:
            py_compile.compile(
                str(path),
                doraise=True,
            )

            check(
                True,
                f"syntax:{filename}",
                "OK",
            )

        except Exception as exc:
            check(
                False,
                f"syntax:{filename}",
                str(exc),
            )


def test_imports():
    try:
        import simulation_engine

        check(
            True,
            "import:simulation_engine",
            "OK",
        )

    except Exception:
        check(
            False,
            "import:simulation_engine",
            traceback.format_exc(),
        )
        return

    try:
        import market_engine

        check(
            True,
            "import:market_engine",
            "OK",
        )

    except Exception:
        check(
            False,
            "import:market_engine",
            traceback.format_exc(),
        )

    try:
        import policy_engine

        check(
            True,
            "import:policy_engine",
            "OK",
        )

    except Exception:
        check(
            False,
            "import:policy_engine",
            traceback.format_exc(),
        )

    try:
        import analysis_engine

        check(
            True,
            "import:analysis_engine",
            "OK",
        )

    except Exception:
        check(
            False,
            "import:analysis_engine",
            traceback.format_exc(),
        )

    strategy_path = ROOT / "strategy_engine.py"

    if strategy_path.exists():
        try:
            import strategy_engine

            check(
                True,
                "import:strategy_engine",
                "OK",
            )

        except Exception:
            check(
                False,
                "import:strategy_engine",
                traceback.format_exc(),
            )


def test_single_cycle():
    try:
        from simulation_engine import run_cycle

        result = run_cycle("random")

        valid_statuses = {
            "goal_reached",
            "failed",
            "policy_blocked",
            "no_item",
            "max_steps_reached",
        }

        valid = (
            isinstance(result, dict)
            and result.get("status") in valid_statuses
            and isinstance(result.get("history"), list)
        )

        check(
            valid,
            "single_cycle",
            result.get("status", "invalid")
            if isinstance(result, dict)
            else "invalid result",
        )

        results["simulation"]["single_cycle"] = {
            "status": result.get("status"),
            "final_capital": result.get(
                "final_capital"
            ),
            "steps": result.get("steps"),
            "history_length": len(
                result.get("history", [])
            ),
        }

    except Exception:
        check(
            False,
            "single_cycle",
            traceback.format_exc(),
        )


def test_all_strategies():
    try:
        from simulation_engine import run_cycle

        for strategy in STRATEGIES:
            try:
                result = run_cycle(strategy)

                valid = (
                    isinstance(result, dict)
                    and "status" in result
                    and "history" in result
                )

                results["strategy_tests"][strategy] = {
                    "passed": valid,
                    "status": result.get("status"),
                    "final_capital": result.get(
                        "final_capital"
                    ),
                    "steps": result.get("steps"),
                }

                check(
                    valid,
                    f"strategy:{strategy}",
                    result.get(
                        "status",
                        "invalid",
                    ),
                )

            except Exception:
                results["strategy_tests"][strategy] = {
                    "passed": False,
                    "error": traceback.format_exc(),
                }

                check(
                    False,
                    f"strategy:{strategy}",
                    traceback.format_exc(),
                )

    except Exception:
        check(
            False,
            "strategy_tests",
            traceback.format_exc(),
        )


def test_summary():
    try:
        from simulation_engine import (
            summarize_campaigns,
        )

        for strategy in STRATEGIES:
            try:
                summary = summarize_campaigns(
                    strategy,
                    campaigns=10,
                )

                valid = (
                    isinstance(summary, dict)
                    and "error" not in summary
                )

                if valid:
                    results["strategy_tests"][
                        f"summary_{strategy}"
                    ] = {
                        "passed": True,
                        "campaigns": summary.get(
                            "campaigns"
                        ),
                        "goal_reached": summary.get(
                            "goal_reached"
                        ),
                        "goal_rate_percent": summary.get(
                            "goal_rate_percent"
                        ),
                    }

                check(
                    valid,
                    f"summary:{strategy}",
                    "OK"
                    if valid
                    else str(summary),
                )

            except Exception:
                check(
                    False,
                    f"summary:{strategy}",
                    traceback.format_exc(),
                )

    except Exception:
        check(
            False,
            "summary_tests",
            traceback.format_exc(),
        )


def test_analysis():
    try:
        import analysis_engine

        required_functions = [
            "create_analysis_stats",
            "update_analysis_stats",
            "finalize_analysis_stats",
        ]

        missing = [
            name
            for name in required_functions
            if not hasattr(
                analysis_engine,
                name,
            )
        ]

        check(
            not missing,
            "analysis_functions",
            "OK"
            if not missing
            else f"不足: {missing}",
        )

    except Exception:
        check(
            False,
            "analysis_functions",
            traceback.format_exc(),
        )


def main():
    print("=" * 60)
    print("Warashibe AI 一括テスト")
    print("=" * 60)

    test_syntax()
    test_imports()
    test_single_cycle()
    test_all_strategies()
    test_summary()
    test_analysis()

    print()
    print("=" * 60)
    print("TEST RESULT")
    print("=" * 60)

    print(
        json.dumps(
            results,
            ensure_ascii=False,
            indent=2,
        )
    )

    print()
    print("=" * 60)
    print(
        f"FINAL STATUS: {results['status']}"
    )
    print("=" * 60)

    if results["status"] != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
```
