from flask import Blueprint, jsonify, request

from simulation_engine import (
    run_cycle,
    summarize_campaigns,
    MAX_CAMPAIGN_CYCLES
)

from strategy_engine import create_recommendation


strategy_bp = Blueprint("strategy", __name__)


@strategy_bp.route("/journey")
def journey():

    strategy = request.args.get(
        "strategy",
        "random"
    )

    result = run_cycle(strategy)

    return jsonify(result)


@strategy_bp.route("/simulate")
def simulate():

    strategy = request.args.get(
        "strategy",
        "random"
    )

    simulations = request.args.get(
        "simulations",
        10000,
        type=int
    )

    results = summarize_campaigns(
        strategy=strategy,
        campaigns=simulations,
        max_cycles=1
    )

    return jsonify(results)


@strategy_bp.route("/campaign/simulate")
def campaign_simulate():

    strategy = request.args.get(
        "strategy",
        "random"
    )

    campaigns = request.args.get(
        "campaigns",
        5000,
        type=int
    )

    max_cycles = request.args.get(
        "max_cycles",
        MAX_CAMPAIGN_CYCLES,
        type=int
    )

    result = summarize_campaigns(
        strategy=strategy,
        campaigns=campaigns,
        max_cycles=max_cycles
    )

    return jsonify(result)


@strategy_bp.route("/strategy/recommendation")
def strategy_recommendation():

    campaigns = request.args.get(
        "campaigns",
        5000,
        type=int
    )

    max_cycles = request.args.get(
        "max_cycles",
        MAX_CAMPAIGN_CYCLES,
        type=int
    )

    strategies = [
        "random",
        "safe",
        "aggressive"
    ]

    strategy_results = []

    for strategy in strategies:

        result = summarize_campaigns(
            strategy=strategy,
            campaigns=campaigns,
            max_cycles=max_cycles
        )

        strategy_results.append(result)

    recommendation = create_recommendation(
        strategy_results
    )

    return jsonify({
        "recommendation": recommendation,
        "strategy_results": strategy_results
    })
