# ============================================================
# Warashibe AI
# route_engine.py
#
# Route Engine v1.1
#
# 目的：
#
# Candidate単体ではなく、
#
# 「この候補を選択した場合、
#   最終TARGETへ到達できる確率」
#
# を評価して次の商品を選択する。
#
# v1.1では、従来のRoute選択ロジックを変更せず、
# 将来のMulti-Objective Route研究に使用する
# Route Metricsを追加する。
#
# failure時は現在のSimulationと同じく
# capital = 0 とする。
#
# Monte Carloではなく、
# 再帰計算 / 動的計画法を使用する。
# ============================================================

from candidate_strategy_adapter import (
    filter_by_price_band,
)


ROUTE_ENGINE_VERSION = "1.1"


# ============================================================
# Candidate基本値
# ============================================================

def get_confidence(candidate):
    return float(
        candidate.get(
            "confidence",
            0,
        )
    )


def get_next_capital(candidate):
    return int(
        candidate.get(
            "expected_sale_price",
            0,
        )
    )


def get_candidate_score(candidate):
    score = candidate.get(
        "score"
    )

    if score is None:
        return 0.0

    return float(score)


def get_purchase_price(candidate):
    return float(
        candidate.get(
            "purchase_price",
            0,
        )
    )


# ============================================================
# Demand Metrics
# ============================================================

def get_demand_score(candidate):
    demand = candidate.get(
        "demand",
        {},
    )

    if not isinstance(
        demand,
        dict,
    ):
        return 0.0

    return float(
        demand.get(
            "demand_score",
            0,
        )
    )


def get_exchange_score(candidate):
    demand = candidate.get(
        "demand",
        {},
    )

    if not isinstance(
        demand,
        dict,
    ):
        return 0.0

    return float(
        demand.get(
            "exchange_score",
            0,
        )
    )


# ============================================================
# Value Metrics
# ============================================================

def get_value_growth_score(candidate):
    value = candidate.get(
        "value_transformation",
        {},
    )

    if not isinstance(
        value,
        dict,
    ):
        return 0.0

    return float(
        value.get(
            "value_growth_score",
            0,
        )
    )


def get_value_exchange_potential(candidate):
    value = candidate.get(
        "value_transformation",
        {},
    )

    if not isinstance(
        value,
        dict,
    ):
        return 0.0

    return float(
        value.get(
            "exchange_potential",
            0,
        )
    )


# ============================================================
# Risk Metrics
# ============================================================

def get_risk_level(candidate):
    risk_level = candidate.get(
        "risk_level"
    )

    if risk_level is None:
        return "unknown"

    return str(
        risk_level
    )


# ============================================================
# Capital Metrics
# ============================================================

def calculate_capital_multiplier(
    capital,
    candidate,
):
    """
    現在資本に対して、
    成功時に資本が何倍になるか。
    """

    if capital <= 0:
        return 0.0

    next_capital = get_next_capital(
        candidate
    )

    return (
        next_capital
        / float(capital)
    )


def calculate_expected_capital(
    candidate,
):
    """
    failure時 capital=0 という
    現在のSimulationモデルに合わせた
    1回の取引後の期待資本。

        confidence
        ×
        expected_sale_price
    """

    confidence = get_confidence(
        candidate
    )

    next_capital = get_next_capital(
        candidate
    )

    return (
        confidence
        * next_capital
    )


# ============================================================
# Candidate取得
# ============================================================

def get_route_candidates(
    capital,
    candidate_provider,
):
    """
    candidate_provider(capital) から
    Candidate Pipeline の結果を取得する。

    Route Rankingではscore付きの
    ranked_candidatesを使用する。

    その後、Warashibeルールに従い、
    現在資本で購入可能な最高価格帯だけ残す。
    """

    result = candidate_provider(
        capital
    )

    candidates = result.get(
        "ranked_candidates",
        [],
    )

    if not candidates:
        return []

    return filter_by_price_band(
        candidates,
        capital,
    )


# ============================================================
# 到達確率計算
# ============================================================

def calculate_goal_probability(
    capital,
    target,
    candidate_provider,
    memo=None,
    visiting=None,
):
    """
    capital から target へ到達する
    理論上の最大確率を計算する。

    各候補について、

        confidence
        ×
        次資本からの最適到達確率

    を計算し、その最大値を採用する。

    v1.1でもv1.0の計算方式を維持する。
    """

    if capital >= target:
        return 1.0

    if capital <= 0:
        return 0.0

    if memo is None:
        memo = {}

    if visiting is None:
        visiting = set()

    if capital in memo:
        return memo[capital]

    # --------------------------------------------------------
    # 循環防止
    # --------------------------------------------------------

    if capital in visiting:
        return 0.0

    visiting.add(
        capital
    )

    candidates = get_route_candidates(
        capital,
        candidate_provider,
    )

    best_probability = 0.0

    for candidate in candidates:

        confidence = get_confidence(
            candidate
        )

        next_capital = get_next_capital(
            candidate
        )

        # ----------------------------------------------------
        # 資本が増えない候補は除外
        # ----------------------------------------------------

        if next_capital <= capital:
            continue

        # ----------------------------------------------------
        # 直接ゴール
        # ----------------------------------------------------

        if next_capital >= target:
            future_probability = 1.0

        # ----------------------------------------------------
        # 再帰計算
        # ----------------------------------------------------

        else:
            future_probability = (
                calculate_goal_probability(
                    next_capital,
                    target,
                    candidate_provider,
                    memo,
                    visiting,
                )
            )

        route_probability = (
            confidence
            * future_probability
        )

        if (
            route_probability
            > best_probability
        ):
            best_probability = (
                route_probability
            )

    visiting.remove(
        capital
    )

    memo[capital] = (
        best_probability
    )

    return best_probability


# ============================================================
# 最適Routeの残りStep数
# ============================================================

def calculate_route_steps_to_target(
    capital,
    target,
    candidate_provider,
    probability_memo=None,
    steps_memo=None,
    visiting=None,
):
    """
    Route Engineが選択する
    「最終到達確率最大Route」を辿った場合の
    TARGETまでの残り成功Step数を返す。

    TARGET到達済み：
        0

    TARGETへ到達できるRouteがない：
        None

    tie-breakはRoute Candidate選択と同じく、

        1. route_goal_probability
        2. confidence
        3. candidate score

    の順で評価する。
    """

    if capital >= target:
        return 0

    if capital <= 0:
        return None

    if probability_memo is None:
        probability_memo = {}

    if steps_memo is None:
        steps_memo = {}

    if visiting is None:
        visiting = set()

    if capital in steps_memo:
        return steps_memo[capital]

    if capital in visiting:
        return None

    visiting.add(
        capital
    )

    candidates = get_route_candidates(
        capital,
        candidate_provider,
    )

    evaluated = []

    for candidate in candidates:

        confidence = get_confidence(
            candidate
        )

        next_capital = get_next_capital(
            candidate
        )

        if next_capital <= capital:
            continue

        if next_capital >= target:
            future_probability = 1.0

        else:
            future_probability = (
                calculate_goal_probability(
                    next_capital,
                    target,
                    candidate_provider,
                    probability_memo,
                    set(),
                )
            )

        goal_probability = (
            confidence
            * future_probability
        )

        evaluated.append(
            (
                goal_probability,
                confidence,
                get_candidate_score(
                    candidate
                ),
                next_capital,
            )
        )

    if not evaluated:
        visiting.remove(
            capital
        )

        steps_memo[capital] = None

        return None

    evaluated.sort(
        key=lambda item: (
            item[0],
            item[1],
            item[2],
        ),
        reverse=True,
    )

    (
        best_probability,
        _,
        _,
        best_next_capital,
    ) = evaluated[0]

    if best_probability <= 0:
        visiting.remove(
            capital
        )

        steps_memo[capital] = None

        return None

    if best_next_capital >= target:
        steps = 1

    else:
        future_steps = (
            calculate_route_steps_to_target(
                best_next_capital,
                target,
                candidate_provider,
                probability_memo,
                steps_memo,
                visiting,
            )
        )

        if future_steps is None:
            steps = None
        else:
            steps = (
                1
                + future_steps
            )

    visiting.remove(
        capital
    )

    steps_memo[capital] = steps

    return steps


# ============================================================
# Candidate Route評価
# ============================================================

def evaluate_route_candidates(
    capital,
    target,
    candidate_provider,
):
    """
    現在資本の各Candidateについて
    最終TARGET到達確率を計算する。

    v1.1では同時にRoute Metricsも付加する。

    Candidate選択順位そのものは
    v1.0から変更しない。
    """

    candidates = get_route_candidates(
        capital,
        candidate_provider,
    )

    if not candidates:
        return []

    probability_memo = {}
    steps_memo = {}

    results = []

    for candidate in candidates:

        confidence = get_confidence(
            candidate
        )

        next_capital = get_next_capital(
            candidate
        )

        candidate_score = (
            get_candidate_score(
                candidate
            )
        )

        # ----------------------------------------------------
        # Goal Probability
        # ----------------------------------------------------

        if next_capital <= capital:

            future_probability = 0.0
            goal_probability = 0.0
            route_steps_to_target = None

        elif next_capital >= target:

            future_probability = 1.0

            goal_probability = (
                confidence
            )

            route_steps_to_target = 1

        else:

            future_probability = (
                calculate_goal_probability(
                    next_capital,
                    target,
                    candidate_provider,
                    probability_memo,
                    set(),
                )
            )

            goal_probability = (
                confidence
                * future_probability
            )

            future_steps = (
                calculate_route_steps_to_target(
                    next_capital,
                    target,
                    candidate_provider,
                    probability_memo,
                    steps_memo,
                    set(),
                )
            )

            if future_steps is None:
                route_steps_to_target = None

            else:
                route_steps_to_target = (
                    1
                    + future_steps
                )

        # ----------------------------------------------------
        # Route Metrics
        # ----------------------------------------------------

        capital_multiplier = (
            calculate_capital_multiplier(
                capital,
                candidate,
            )
        )

        expected_capital = (
            calculate_expected_capital(
                candidate
            )
        )

        demand_score = (
            get_demand_score(
                candidate
            )
        )

        exchange_score = (
            get_exchange_score(
                candidate
            )
        )

        value_growth_score = (
            get_value_growth_score(
                candidate
            )
        )

        value_exchange_potential = (
            get_value_exchange_potential(
                candidate
            )
        )

        risk_level = (
            get_risk_level(
                candidate
            )
        )

        # ----------------------------------------------------
        # Candidateコピー
        # ----------------------------------------------------

        item = dict(
            candidate
        )

        # ----------------------------------------------------
        # v1.0 Route Metrics
        # ----------------------------------------------------

        item[
            "route_future_probability"
        ] = future_probability

        item[
            "route_goal_probability"
        ] = goal_probability

        # ----------------------------------------------------
        # v1.1 Route Metrics
        # ----------------------------------------------------

        item[
            "route_steps_to_target"
        ] = route_steps_to_target

        item[
            "route_capital_multiplier"
        ] = capital_multiplier

        item[
            "route_expected_capital"
        ] = expected_capital

        item[
            "route_demand_score"
        ] = demand_score

        item[
            "route_exchange_score"
        ] = exchange_score

        item[
            "route_value_growth_score"
        ] = value_growth_score

        item[
            "route_value_exchange_potential"
        ] = value_exchange_potential

        item[
            "route_risk_level"
        ] = risk_level

        item[
            "route_engine_version"
        ] = ROUTE_ENGINE_VERSION

        results.append(
            item
        )

    # ========================================================
    # IMPORTANT
    #
    # v1.1では順位付けを変更しない。
    #
    # 1. 最終TARGET到達確率
    # 2. confidence
    # 3. Candidate score
    #
    # Route Metricsは観測用であり、
    # まだ順位には使用しない。
    # ========================================================

    results.sort(
        key=lambda candidate: (
            float(
                candidate.get(
                    "route_goal_probability",
                    0,
                )
            ),
            get_confidence(
                candidate
            ),
            get_candidate_score(
                candidate
            ),
        ),
        reverse=True,
    )

    return results


# ============================================================
# Route最適Candidate選択
# ============================================================

def select_route_candidate(
    capital,
    target,
    candidate_provider,
):
    """
    最終TARGET到達確率が最大になる
    Candidateを1件返す。

    v1.1でも選択ロジックは
    v1.0と同一。
    """

    candidates = (
        evaluate_route_candidates(
            capital,
            target,
            candidate_provider,
        )
    )

    if not candidates:
        return None

    best = dict(
        candidates[0]
    )

    best[
        "route_rank"
    ] = 1

    return best