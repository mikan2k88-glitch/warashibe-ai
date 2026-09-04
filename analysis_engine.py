
# ============================================================
# Warashibe AI v0.6
# analysis_engine.py
#
# 役割：
# ・商品別統計
# ・失敗ステップ分析
# ・資本帯分析
#
# シミュレーション処理は simulation_engine.py に置く
# ============================================================


# ============================================================
# 資本帯定義
# ============================================================

CAPITAL_BANDS = [
    ("100-999", 100, 999),
    ("1,000-9,999", 1_000, 9_999),
    ("10,000-99,999", 10_000, 99_999),
    ("100,000-999,999", 100_000, 999_999),
    ("1,000,000+", 1_000_000, float("inf")),
]


# ============================================================
# 商品統計
# ============================================================

def create_item_stats():
    """
    商品統計を空の状態で作成する。
    """

    return {}


def update_item_stats(
    item_stats,
    item_name,
    success
):
    """
    商品1回分の取引結果を統計へ反映する。
    """

    if item_name not in item_stats:
        item_stats[item_name] = {
            "attempts": 0,
            "failures": 0,
            "successes": 0,
            "success_rate_percent": 0.0,
        }

    stats = item_stats[item_name]

    stats["attempts"] += 1

    if success:
        stats["successes"] += 1
    else:
        stats["failures"] += 1

    attempts = stats["attempts"]

    if attempts > 0:
        stats["success_rate_percent"] = round(
            stats["successes"]
            / attempts
            * 100,
            2
        )


def merge_item_stats(
    total_stats,
    cycle_stats
):
    """
    複数サイクルの商品統計を合算する。
    """

    for item_name, stats in cycle_stats.items():

        if item_name not in total_stats:
            total_stats[item_name] = {
                "attempts": 0,
                "failures": 0,
                "successes": 0,
                "success_rate_percent": 0.0,
            }

        total = total_stats[item_name]

        total["attempts"] += int(
            stats.get("attempts", 0)
        )

        total["failures"] += int(
            stats.get("failures", 0)
        )

        total["successes"] += int(
            stats.get("successes", 0)
        )

    recalculate_item_stats(total_stats)


def recalculate_item_stats(item_stats):
    """
    商品統計の成功率を再計算する。
    """

    for stats in item_stats.values():

        attempts = (
            int(stats.get("successes", 0))
            + int(stats.get("failures", 0))
        )

        stats["attempts"] = attempts

        if attempts > 0:
            stats["success_rate_percent"] = round(
                int(stats.get("successes", 0))
                / attempts
                * 100,
                2
            )
        else:
            stats["success_rate_percent"] = 0.0


# ============================================================
# 失敗ステップ分析
# ============================================================

def create_failure_step_stats():
    """
    失敗ステップ統計を作成する。
    """

    return {}


def update_failure_step_stats(
    failure_step_stats,
    history,
    success,
    failure_reason=None
):
    """
    1回の挑戦結果から失敗ステップを記録する。

    成功した場合は何もしない。
    失敗した場合は、その失敗が発生したstepを記録する。
    """

    if success:
        return

    if not history:
        return

    failed_trade = history[-1]

    step = failed_trade.get("step")

    if step is None:
        return

    step_key = str(step)

    if step_key not in failure_step_stats:
        failure_step_stats[step_key] = {
            "failures": 0,
            "failure_rate_percent": 0.0,
        }

    failure_step_stats[step_key]["failures"] += 1


def recalculate_failure_step_stats(
    failure_step_stats,
    total_failures
):
    """
    失敗ステップごとの割合を再計算する。
    """

    if total_failures <= 0:
        for stats in failure_step_stats.values():
            stats["failure_rate_percent"] = 0.0
        return

    for stats in failure_step_stats.values():

        stats["failure_rate_percent"] = round(
            stats["failures"]
            / total_failures
            * 100,
            2
        )


# ============================================================
# 資本帯分析
# ============================================================

def create_capital_band_stats():
    """
    資本帯統計を作成する。
    """

    stats = {}

    for name, _, _ in CAPITAL_BANDS:
        stats[name] = {
            "attempts": 0,
            "failures": 0,
            "successes": 0,
            "success_rate_percent": 0.0,
        }

    return stats


def get_capital_band(capital):
    """
    現在資本がどの資本帯に属するかを返す。
    """

    try:
        capital = float(capital)
    except (TypeError, ValueError):
        return "unknown"

    for name, minimum, maximum in CAPITAL_BANDS:

        if minimum <= capital <= maximum:
            return name

    return "unknown"


def update_capital_band_stats(
    capital_band_stats,
    capital,
    success
):
    """
    取引結果を資本帯統計へ反映する。
    """

    band = get_capital_band(capital)

    if band == "unknown":
        return

    stats = capital_band_stats[band]

    stats["attempts"] += 1

    if success:
        stats["successes"] += 1
    else:
        stats["failures"] += 1

    attempts = stats["attempts"]

    if attempts > 0:
        stats["success_rate_percent"] = round(
            stats["successes"]
            / attempts
            * 100,
            2
        )


def merge_capital_band_stats(
    total_stats,
    cycle_stats
):
    """
    複数サイクルの資本帯統計を合算する。
    """

    for band, stats in cycle_stats.items():

        if band not in total_stats:
            total_stats[band] = {
                "attempts": 0,
                "failures": 0,
                "successes": 0,
                "success_rate_percent": 0.0,
            }

        total = total_stats[band]

        total["attempts"] += int(
            stats.get("attempts", 0)
        )

        total["failures"] += int(
            stats.get("failures", 0)
        )

        total["successes"] += int(
            stats.get("successes", 0)
        )

    recalculate_capital_band_stats(total_stats)


def recalculate_capital_band_stats(
    capital_band_stats
):
    """
    資本帯ごとの成功率を再計算する。
    """

    for stats in capital_band_stats.values():

        attempts = (
            int(stats.get("successes", 0))
            + int(stats.get("failures", 0))
        )

        stats["attempts"] = attempts

        if attempts > 0:
            stats["success_rate_percent"] = round(
                int(stats.get("successes", 0))
                / attempts
                * 100,
                2
            )
        else:
            stats["success_rate_percent"] = 0.0


# ============================================================
# 成功ルート分析
# ============================================================

def build_successful_route(history):
    """
    成功したhistoryから商品名だけのルートを作成する。

    例：
        商品A → 商品B → 商品C
    """

    if not history:
        return ""

    return " → ".join(
        trade.get(
            "selected_item",
            "unknown"
        )
        for trade in history
    )


def build_detailed_successful_route(history):
    """
    成功したhistoryから、
    商品名と資本推移を含む詳細ルートを作成する。

    例：
        100円
        ↓
        商品A
        ↓
        500円
        ↓
        商品B
    """

    if not history:
        return ""

    parts = []

    first_capital = history[0].get(
        "capital_before",
        0
    )

    parts.append(
        f"{first_capital:g}円"
    )

    for trade in history:

        item_name = trade.get(
            "selected_item",
            "unknown"
        )

        capital_after = trade.get(
            "capital_after",
            0
        )

        parts.append(item_name)
        parts.append(
            f"{capital_after:g}円"
        )

    return " → ".join(parts)


# ============================================================
# 分析結果作成
# ============================================================

def create_analysis_stats():
    """
    分析用統計をまとめて初期化する。
    """

    return {
        "item_stats": create_item_stats(),
        "failure_step_stats": create_failure_step_stats(),
        "capital_band_stats": create_capital_band_stats(),
    }


# ============================================================
# 1回分の分析更新
# ============================================================

def update_analysis_stats(
    analysis_stats,
    history,
    success
):
    """
    1回の挑戦結果を分析統計へ反映する。
    """

    item_stats = analysis_stats[
        "item_stats"
    ]

    capital_band_stats = analysis_stats[
        "capital_band_stats"
    ]

    failure_step_stats = analysis_stats[
        "failure_step_stats"
    ]

    for trade in history:

        item_name = trade.get(
            "selected_item",
            "unknown"
        )

        trade_success = bool(
            trade.get("success", False)
        )

        capital_before = trade.get(
            "capital_before",
            0
        )

        update_item_stats(
            item_stats,
            item_name,
            trade_success
        )

        update_capital_band_stats(
            capital_band_stats,
            capital_before,
            trade_success
        )

    update_failure_step_stats(
        failure_step_stats,
        history,
        success
    )


# ============================================================
# 分析結果の再計算
# ============================================================

def finalize_analysis_stats(
    analysis_stats
):
    """
    分析統計の割合を最終計算する。
    """

    item_stats = analysis_stats[
        "item_stats"
    ]

    failure_step_stats = analysis_stats[
        "failure_step_stats"
    ]

    capital_band_stats = analysis_stats[
        "capital_band_stats"
    ]

    recalculate_item_stats(
        item_stats
    )

    total_failures = sum(
        stats.get("failures", 0)
        for stats in failure_step_stats.values()
    )

    recalculate_failure_step_stats(
        failure_step_stats,
        total_failures
    )

    recalculate_capital_band_stats(
        capital_band_stats
    )

    return analysis_stats

