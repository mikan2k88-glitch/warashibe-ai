from capital_filter import evaluate_capital_fit


def main():
    exact = evaluate_capital_fit(
        10_000,
        {"purchase_price": 10_000},
    )
    assert exact["allowed"] is True

    under = evaluate_capital_fit(
        10_000,
        {"purchase_price": 8_000},
    )
    assert under["allowed"] is False
    assert under["capital_usage_rate"] == 0.8
    assert under["reasons"]

    over = evaluate_capital_fit(
        10_000,
        {"purchase_price": 12_000},
    )
    assert over["allowed"] is False

    zero = evaluate_capital_fit(
        10_000,
        {"purchase_price": 0},
    )
    assert zero["allowed"] is False


if __name__ == "__main__":
    main()
