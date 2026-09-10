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
    "demand_engine.py",
    "value_engine.py",
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
        "demand_engine",
        "value_engine",
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


def test_demand_engine():
    try:
        from demand_engine import (
            get_demand,
            get_demand_level,
            get_exchange_potential,
        )

        # 正常なカテゴリ
        camera = get_demand(
            {
                "name": "中古カメラ",
                "value": 5000,
                "category": "camera",
            }
        )

        camera_valid = (
            isinstance(camera, dict)
            and camera.get("asset") == "中古カメラ"
            and camera.get("category") == "camera"
            and camera.get("demand_score") == 0.80
            and camera.get("demand_level") == "high"
            and camera.get("freshness_score") == 0.75
            and camera.get("exchange_score") == 0.70
        )

        check(
            camera_valid,
            "demand_engine:camera",
            "OK" if camera_valid else str(camera),
        )

        # 未知カテゴリ
        unknown = get_demand(
            {
                "name": "未知の商品",
                "category": "unknown",
            }
        )

        unknown_valid = (
            isinstance(unknown, dict)
            and unknown.get("demand_level") == "medium"
            and unknown.get("demand_score") == 0.50
        )

        check(
            unknown_valid,
            "demand_engine:unknown_category",
            "OK" if unknown_valid else str(unknown),
        )

        # 不正入力
        invalid = get_demand(None)

        invalid_valid = isinstance(invalid, dict)

        check(
            invalid_valid,
            "demand_engine:invalid_input",
            "OK" if invalid_valid else str(invalid),
        )

        # 需要レベル判定
        level_valid = (
            get_demand_level(0.80) == "high"
            and get_demand_level(0.50) == "medium"
            and get_demand_level(0.20) == "low"
        )

        check(
            level_valid,
            "demand_engine:demand_level",
            "OK" if level_valid else "invalid",
        )

        # 交換可能性
        exchange = get_exchange_potential(
            {
                "name": "中古カメラ",
                "category": "camera",
            }
        )

        exchange_valid = exchange == 0.70

        check(
            exchange_valid,
            "demand_engine:exchange_potential",
            "OK" if exchange_valid else str(exchange),
        )

    except Exception:
        check(
            False,
            "demand_engine",
            traceback.format_exc(),
        )


def test_value_engine():
    try:
        from value_engine import (
            get_value_transformation,
            get_value_growth_score,
            get_next_value,
            get_exchange_potential,
        )

        # 正常なカテゴリ
        camera = get_value_transformation(
            {
                "name": "中古カメラ",
                "value": 5000,
                "category": "camera",
            }
        )

        camera_valid = (
            isinstance(camera, dict)
            and camera.get("asset") == "中古カメラ"
            and camera.get("category") == "camera"
            and camera.get("current_value") == 5000.0
            and camera.get("next_value") == 7500.0
            and camera.get("value_growth_score") == 0.72
            and camera.get("exchange_potential") == 0.68
            and camera.get("route") == "collector"
        )

        check(
            camera_valid,
            "value_engine:camera",
            "OK" if camera_valid else str(camera),
        )

        # 価値上昇スコア
        growth_score = get_value_growth_score(
            {
                "name": "中古カメラ",
                "value": 5000,
                "category": "camera",
            }
        )

        growth_valid = growth_score == 0.72

        check(
            growth_valid,
            "value_engine:growth_score",
            "OK" if growth_valid else str(growth_score),
        )

        # 次の価値
        next_value = get_next_value(
            {
                "name": "中古カメラ",
                "value": 5000,
                "category": "camera",
            }
        )

        next_value_valid = next_value == 7500.0

        check(
            next_value_valid,
            "value_engine:next_value",
            "OK" if next_value_valid else str(next_value),
        )

        # 交換可能性
        exchange = get_exchange_potential(
            {
                "name": "中古カメラ",
                "value": 5000,
                "category": "camera",
            }
        )

        exchange_valid = exchange == 0.68

        check(
            exchange_valid,
            "value_engine:exchange_potential",
            "OK" if exchange_valid else str(exchange),
        )

        # 未知カテゴリ
        unknown = get_value_transformation(
            {
                "name": "未知の商品",
                "value": 1000,
                "category": "unknown",
            }
        )

        unknown_valid = (
            isinstance(unknown, dict)
            and unknown.get("next_value") == 1200.0
            and unknown.get("value_growth_score") == 0.50
            and unknown.get("exchange_potential") == 0.50
            and unknown.get("route") == "general"
        )

        check(
            unknown_valid,
            "value_engine:unknown_category",
            "OK" if unknown_valid else str(unknown),
        )

        # 不正入力
        invalid = get_value_transformation(None)

        invalid_valid = (
            isinstance(invalid, dict)
            and invalid.get("current_value") == 0
            and invalid.get("next_value") == 0
        )

        check(
            invalid_valid,
            "value_engine:invalid_input",
            "OK" if invalid_valid else str(invalid),
        )

    except Exception:
        check(
            False,
            "value_engine",
            traceback.format_exc(),
        )


def test_candidate_engine():
    try:
        from candidate_engine import create_candidate

        candidate = create_candidate(
            name="中古カメラ",
            purchase_price=5000,
            expected_sale_price=7500,
            source="test",
            category="camera",
            confidence=0.90,
        )

        demand = candidate.get("demand", {})
        value = candidate.get("value_transformation", {})

        valid = (
            isinstance(candidate, dict)
            and candidate.get("candidate_version") == "1.1"
            and candidate.get("name") == "中古カメラ"
            and candidate.get("category") == "camera"
            and candidate.get("source") == "test"
            and candidate.get("purchase_price") == 5000
            and candidate.get("expected_sale_price") == 7500
            and candidate.get("expected_profit") == 2500
            and candidate.get("expected_profit_rate") == 0.5
            and candidate.get("confidence") == 0.90
            and isinstance(demand, dict)
            and demand.get("demand_score") == 0.80
            and demand.get("demand_level") == "high"
            and demand.get("freshness_score") == 0.75
            and demand.get("exchange_score") == 0.70
            and isinstance(value, dict)
            and value.get("current_value") == 7500.0
            and value.get("next_value") == 11250.0
            and value.get("value_growth_score") == 0.72
            and value.get("exchange_potential") == 0.68
            and value.get("route") == "collector"
        )

        check(
            valid,
            "candidate_engine:integration",
            "OK" if valid else str(candidate),
        )

        # metadata が維持されること
        metadata = {
            "market": "test",
            "source_id": "TEST001",
        }

        candidate_with_metadata = create_candidate(
            name="中古カメラ",
            purchase_price=5000,
            expected_sale_price=7500,
            source="test",
            category="camera",
            confidence=0.90,
            metadata=metadata,
        )

        metadata_valid = (
            candidate_with_metadata.get("metadata") == metadata
        )

        check(
            metadata_valid,
            "candidate_engine:metadata",
            "OK" if metadata_valid else str(
                candidate_with_metadata.get("metadata")
            ),
        )

    except Exception:
        check(
            False,
            "candidate_engine",
            traceback.format_exc(),
        )


def test_ranking_engine():
    try:
        from ranking_engine import (
            calculate_score,
            rank_candidates,
        )

        # Demand / Value 評価を持つ候補
        strong_candidate = {
            "name": "高評価カメラ",
            "expected_profit_rate": 0.50,
            "expected_profit": 2500,
            "confidence": 0.90,
            "demand": {
                "demand_score": 0.80,
                "freshness_score": 0.75,
                "exchange_score": 0.70,
            },
            "value_transformation": {
                "value_growth_score": 0.72,
                "exchange_potential": 0.68,
            },
        }

        score = calculate_score(strong_candidate)

        score_valid = (
            isinstance(score, float)
            and score > 0
        )

        check(
            score_valid,
            "ranking_engine:calculate_score",
            str(score),
        )

        # 既存候補との比較
        weak_candidate = {
            "name": "低評価商品",
            "expected_profit_rate": 0.10,
            "expected_profit": 500,
            "confidence": 0.50,
            "demand": {
                "demand_score": 0.40,
                "freshness_score": 0.50,
                "exchange_score": 0.35,
            },
            "value_transformation": {
                "value_growth_score": 0.40,
                "exchange_potential": 0.35,
            },
        }

        ranked = rank_candidates(
            [
                weak_candidate,
                strong_candidate,
            ]
        )

        ranking_valid = (
            isinstance(ranked, list)
            and len(ranked) == 2
            and ranked[0].get("name") == "高評価カメラ"
            and ranked[0].get("rank") == 1
            and ranked[1].get("rank") == 2
            and ranked[0].get("score")
            > ranked[1].get("score")
        )

        check(
            ranking_valid,
            "ranking_engine:rank_candidates",
            "OK" if ranking_valid else str(ranked),
        )

        # Demand / Value がない候補でも動作すること
        basic_candidate = {
            "name": "基本候補",
            "expected_profit_rate": 0.20,
            "expected_profit": 1000,
            "confidence": 0.60,
        }

        basic_score = calculate_score(basic_candidate)

        basic_valid = (
            isinstance(basic_score, float)
            and basic_score > 0
        )

        check(
            basic_valid,
            "ranking_engine:backward_compatibility",
            str(basic_score),
        )

    except Exception:
        check(
            False,
            "ranking_engine",
            traceback.format_exc(),
        )



def test_candidate_pipeline():
    try:
        from candidate_engine import create_candidate
        from candidate_pipeline import evaluate_candidates

        candidates = [
            create_candidate(
                name="中古カメラ",
                purchase_price=5000,
                expected_sale_price=8000,
                source="test",
                category="camera",
                confidence=0.90,
            ),
            create_candidate(
                name="中古CD",
                purchase_price=5000,
                expected_sale_price=5500,
                source="test",
                category="cd",
                confidence=0.90,
            ),
        ]

        result = evaluate_candidates(candidates, current_capital=10000)

        valid = (
            isinstance(result, dict)
            and result.get("version") == "1.1"
            and result.get("current_capital") == 10000
            and result.get("total_candidates") == 2
            and isinstance(result.get("danger_blocked"), list)
            and isinstance(result.get("capital_blocked"), list)
            and isinstance(result.get("ranked_candidates"), list)
            and result.get("best_candidate") is not None
        )

        check(valid, "candidate_pipeline:basic", "OK" if valid else str(result))

        best = result.get("best_candidate")
        ranked = result.get("ranked_candidates", [])

        ranking_valid = (
            isinstance(best, dict)
            and best.get("name") == "中古カメラ"
            and len(ranked) >= 1
            and ranked[0].get("name") == "中古カメラ"
            and ranked[0].get("rank") == 1
        )

        check(ranking_valid, "candidate_pipeline:best_candidate", "OK" if ranking_valid else str(result))

        integration_valid = (
            isinstance(best.get("demand"), dict)
            and isinstance(best.get("value_transformation"), dict)
            and isinstance(best.get("capital_fit"), dict)
            and best["capital_fit"].get("allowed") is True
            and isinstance(best.get("score"), (int, float))
        )

        check(integration_valid, "candidate_pipeline:integration", "OK" if integration_valid else str(best))

    except Exception:
        check(False, "candidate_pipeline", traceback.format_exc())

def test_strategy_single_cycle():
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



def test_candidate_evaluate_api():
    try:
        from app import app

        client = app.test_client()

        payload = {
            "name": "中古カメラ",
            "purchase_price": 5000,
            "expected_sale_price": 8000,
            "source": "test",
            "category": "camera",
            "confidence": 0.90,
            "current_capital": 10000,
        }

        response = client.post(
            "/candidates/evaluate",
            json=payload,
        )

        data = response.get_json()

        valid = (
            response.status_code == 200
            and isinstance(data, dict)
            and data.get("status") == "allowed"
            and data.get("candidate", {}).get("name") == "中古カメラ"
            and "demand" in data.get("candidate", {})
            and "value_transformation"
            in data.get("candidate", {})
            and "capital_fit"
            in data.get("candidate", {})
            and isinstance(
                data.get("candidate", {}).get("score"),
                (int, float),
            )
        )

        check(
            valid,
            "api:candidates_evaluate",
            "OK"
            if valid
            else (
                f"status={response.status_code} "
                f"body={str(data)[:1000]}"
            ),
        )

        results["api"]["candidates_evaluate"] = {
            "passed": valid,
            "status_code": response.status_code,
        }

    except Exception:
        check(
            False,
            "api:candidates_evaluate",
            traceback.format_exc(),
        )

        results["api"]["candidates_evaluate"] = {
            "passed": False,
            "error": traceback.format_exc(),
        }


def main():
    print("=" * 60)
    print("Warashibe AI 現行構成 一括テスト")
    print("=" * 60)

    test_syntax()
    test_imports()
    test_strategy_engine()
    test_demand_engine()
    test_value_engine()
    test_candidate_engine()
    test_ranking_engine()
    test_candidate_pipeline()
    test_strategy_single_cycle()
    test_campaign_engine()
    test_strategy_api()
    test_candidate_api()
    test_flask_api()
    test_candidate_evaluate_api()

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