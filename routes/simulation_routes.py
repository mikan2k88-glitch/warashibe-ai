from flask import Blueprint, jsonify, request

from market_engine import MARKET
from policy_engine import POLICY_VERSION, START_CAPITAL
from simulation_engine import (
    run_cycle,
    summarize_campaigns
)


simulation_bp = Blueprint(
    "simulation",
    __name__
)


TARGET = 1_000_000
MAX_CAMPAIGN_CYCLES = 10


# ============================================================
# 共通関数
# ============================================================

def get_strategy():

    strategy = request.args.get(
        "strategy",
        "random"
    ).lower()

    if strategy not in {
        "random",
        "safe",
        "aggressive"
    }:
        return None

    return strategy


def get_bounded_int(
    name,
    default,
    minimum,
    maximum
):

    value = request.args.get(name)

    if value is None:
        return default

    try:
        value = int(value)

    except (
        ValueError,
        TypeError
    ):
        return None

    if minimum <= value <= maximum:
        return value

    return None


# ============================================================
# /journey
# ============================================================

@simulation_bp.route("/journey")
def journey():

    strategy = get_strategy()

    if strategy is None:

        return jsonify({
            "error":
            "strategy が不正です。"
        }), 400

    result = run_cycle(
        strategy
    )

    return jsonify({

        "version": "1.0",

        "policy_version":
            POLICY_VERSION,

        "strategy":
            strategy,

        "start_capital":
            START_CAPITAL,

        "target":
            TARGET,

        **result
    })


# ============================================================
# /simulate
# ============================================================

@simulation_bp.route("/simulate")
def simulate():

    strategy = get_strategy()

    simulations = get_bounded_int(
        "simulations",
        10_000,
        1,
        100_000
    )

    if strategy is None:

        return jsonify({
            "error":
            "strategy が不正です。"
        }), 400

    if simulations is None:

        return jsonify({
            "error":
            "simulations は1〜100000の整数です。"
        }), 400

    goal_reached = 0

    item_stats = {

        item["name"]: {
            "attempts": 0,
            "successes": 0,
            "failures": 0
        }

        for item in MARKET
    }

    for _ in range(simulations):

        result = run_cycle(
            strategy
        )

        for trade in result["history"]:

            stats = item_stats[
                trade["selected_item"]
            ]

            stats["attempts"] += 1

            if trade["success"]:

                stats["successes"] += 1

            else:

                stats["failures"] += 1

        if result["status"] == "goal_reached":

            goal_reached += 1

    for stats in item_stats.values():

        attempts = stats["attempts"]

        if attempts:

            stats[
                "success_rate_percent"
            ] = round(
                stats["successes"]
                / attempts
                * 100,
                2
            )

        else:

            stats[
                "success_rate_percent"
            ] = 0

    return jsonify({

        "version": "1.0",

        "policy_version":
            POLICY_VERSION,

        "strategy":
            strategy,

        "simulations":
            simulations,

        "goal_reached":
            goal_reached,

        "goal_rate_percent":
            round(
                goal_reached
                / simulations
                * 100,
                2
            ),

        "item_stats":
            item_stats
    })


# ============================================================
# /campaign/simulate
# ============================================================

@simulation_bp.route(
    "/campaign/simulate"
)
def campaign_simulate():

    strategy = get_strategy()

    campaigns = get_bounded_int(
        "campaigns",
        1_000,
        1,
        10_000
    )

    max_cycles = get_bounded_int(
        "max_cycles",
        MAX_CAMPAIGN_CYCLES,
        1,
        100
    )

    if strategy is None:

        return jsonify({
            "error":
            "strategy が不正です。"
        }), 400

    if (
        campaigns is None
        or max_cycles is None
    ):

        return jsonify({
            "error":
            "campaigns は1〜10000、"
            "max_cycles は1〜100で指定してください。"
        }), 400

    summary = summarize_campaigns(
        strategy,
        campaigns,
        max_cycles
    )

    return jsonify({

        "version": "1.0",

        "policy_version":
            POLICY_VERSION,

        "start_capital":
            START_CAPITAL,

        "target":
            TARGET,

        **summary
    })
