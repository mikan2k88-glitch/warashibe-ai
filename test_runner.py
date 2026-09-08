# ============================================================
# Warashibe AI
# test_runner.py
#
# 現在のモジュール分割構成に対応した一括テスト
#
# 実行：
#     python test_runner.py
#
# 結果をそのままChatGPTへ貼り付けてください。
# ============================================================

import json
import py_compile
import traceback
from pathlib import Path


ROOT = Path(__file__).resolve().parent

REQUIRED_FILES = [
    "app.py",
    "simulation_engine.py",
    "campaign_engine.py",
    "market_engine.py",
    "policy_engine.py",
    "analysis_engine.py",
    "strategy_engine.py",
    "strategy_api.py",
    "candidate_api.py",
    "candidate_engine.py",
    "danger_filter.py",
    "capital_filter.py",
    "ranking_engine.py",
    "candidate_pipeline.py",
]

STRATEGIES = [
    "random",
    "safe",
    "balanced",
    "aggressive",
]

API_TESTS = [
    ("/", "home"),
    ("/docs", "docs"),
    ("/journey?strategy=balanced", "journey"),
    ("/simulate?strategy=balanced&simulations=3", "simulate"),
    (
        "/campaign/simulate?strategy=balanced&campaigns=100&max_cycles=2",
        "campaign_simulate",
    ),
    (
        "/strategy/recommendation?campaigns=100&max_cycles=2",
        "strategy_recommendation",
    ),
    (
        "/strategy/report?campaigns=100&max_cycles=2",
        "strategy_report",
    ),
    ("/candidates/test", "candidates_test"),
    ("/capital-filter/test", "capital_filter_test"),
    ("/candidates/pipeline-test", "pipeline_test"),
    ("/candidate-form", "candidate_form"),
]


results = {
    "status": "PASSED",
    "checks": {},
    "simulation": {},
    "campaign": {},
    "api": {},
    "errors": [],
}


def check(condition, name, detail=""):
    passed = bool(condition)

    results["checks"][name] = {
        "passed": passed,
        "detail": detail,
    }

    if not passed:
        results["status"] = "FAILED"
        results["errors"].append(
            f"{name}: {detail}"
        )


def test_syntax():
    for filename in REQUIRED_FILES:
        path = ROOT / filename

        if not path.exists():
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
    modules = [
        "market_engine",
        "policy_engine",
        "analysis_engine",
        "strategy_engine",
        "simulation_engine",
        "campaign_engine",
        "candidate_engine",
        "danger_filter",
        "capital_filter",
        "ranking_engine",
        "candidate_pipeline",
        "strategy_api",
        "candidate_api",
        "app",
    ]

    for module_name in modules:
        try:
            __import__(module_name)

            check(
                True,
                f"import:{module_name}",
                "OK",
            )

        except Exception:
            check(
                False,
                f"import:{module_name}",
                traceback.format_exc(),
            )


def test_strategy_engine():
    try:
        from strategy_engine import normalize_strategy

        for strategy in STRATEGIES:
            normalized = normalize_strategy(strategy)

            check(
                normalized == strategy,
                f"normalize_strategy:{strategy}",
                str(normalized),
            )

    except Exception:
        check(
            False,
            "strategy_engine",
            traceback.format_exc(),
        )


def test_single_cycle():
    try:
        from simulation_engine import run_cycle

        valid_statuses = {
            "goal_reached",
            "failed",
            "policy_blocked",
            "no_item",
            "max_steps_reached",
        }

        for strategy in STRATEGIES:
            result = run_cycle(strategy)

            valid = (
                isinstance(result, dict)
                and result.get("status") in valid_statuses
                and isinstance(result.get("history"), list)
            )

            check(
                valid,
                f"run_cycle:{strategy}",
                result.get(
                    "status",
                    "invalid",
                )
                if isinstance(result, dict)
                else "invalid result",
            )

            results["simulation"][strategy] = {
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
            "run_cycle_tests",
            traceback.format_exc(),
        )


def test_campaign_engine():
    try:
        from campaign_engine import (
            run_campaign,
            summarize_campaigns,
            evaluate_strategies,
        )

        for strategy in STRATEGIES:
            result = run_campaign(
                strategy,
                max_cycles=2,
            )

            valid = (
                isinstance(result, dict)
                and result.get("status") in {
                    "goal_reached",
                    "policy_blocked",
                    "max_cycles_reached",
                }
                and "cycles_used" in result
                and "analysis_stats" in result
            )

            check(
                valid,
                f"run_campaign:{strategy}",
                result.get(
                    "status",
                    "invalid",
                )
                if isinstance(result, dict)
                else "invalid result",
            )

        summary = summarize_campaigns(
            "balanced",
            campaigns=3,
            max_cycles=2,
        )

        summary_valid = (
            isinstance(summary, dict)
            and "error" not in summary
            and summary.get("strategy") == "balanced"
            and summary.get("campaigns") == 3
        )

        check(
            summary_valid,
            "summarize_campaigns:balanced",
            "OK" if summary_valid else str(summary),
        )

        strategy_results, ranked_results = evaluate_strategies(
            campaigns=3,
            max_cycles=2,
        )

        evaluate_valid = (
            isinstance(strategy_results, list)
            and len(strategy_results) == 4
            and isinstance(ranked_results, list)
            and len(ranked_results) == 4
        )

        check(
            evaluate_valid,
            "evaluate_strategies",
            "4 strategies"
            if evaluate_valid
            else "invalid result",
        )

        results["campaign"] = {
            "summary_balanced": {
                "campaigns": summary.get("campaigns"),
                "goal_reached": summary.get(
                    "campaign_goal_reached"
                ),
                "goal_rate_percent": summary.get(
                    "campaign_goal_rate_percent"
                ),
                "average_cycles_used": summary.get(
                    "average_cycles_used"
                ),
                "average_restarts": summary.get(
                    "average_restarts"
                ),
            },
            "evaluate_strategies_count": len(
                strategy_results
            ),
            "ranked_strategies_count": len(
                ranked_results
            ),
        }

    except Exception:
        check(
            False,
            "campaign_engine_tests",
            traceback.format_exc(),
        )


def test_strategy_api():
    try:
        from strategy_api import (
            strategy_bp,
            STRATEGIES as API_STRATEGIES,
        )

        valid = (
            strategy_bp is not None
            and tuple(API_STRATEGIES)
            == tuple(STRATEGIES)
        )

        check(
            valid,
            "strategy_api",
            "OK"
            if valid
            else "strategy list mismatch",
        )

    except Exception:
        check(
            False,
            "strategy_api",
            traceback.format_exc(),
        )


def test_candidate_api():
    try:
        from candidate_api import candidate_bp

        check(
            candidate_bp is not None,
            "candidate_api",
            "OK",
        )

    except Exception:
        check(
            False,
            "candidate_api",
            traceback.format_exc(),
        )


def test_flask_api():
    try:
        from app import app

        client = app.test_client()

        for path, name in API_TESTS:
            try:
                response = client.get(path)

                valid = response.status_code == 200

                detail = (
                    f"status={response.status_code}"
                )

                if not valid:
                    detail += (
                        " body="
                        + response.get_data(
                            as_text=True
                        )[:500]
                    )

                check(
                    valid,
                    f"api:{name}",
                    detail,
                )

                results["api"][name] = {
                    "passed": valid,
                    "status_code": response.status_code,
                }

            except Exception:
                check(
                    False,
                    f"api:{name}",
                    traceback.format_exc(),
                )

                results["api"][name] = {
                    "passed": False,
                    "error": traceback.format_exc(),
                }

    except Exception:
        check(
            False,
            "flask_api_tests",
            traceback.format_exc(),
        )


def main():
    print("=" * 60)
    print("Warashibe AI 現行構成 一括テスト")
    print("=" * 60)

    test_syntax()
    test_imports()
    test_strategy_engine()
    test_single_cycle()
    test_campaign_engine()
    test_strategy_api()
    test_candidate_api()
    test_flask_api()

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