from __future__ import annotations

from statistics import mean, pstdev


def assess_price_stability(values: list[float]) -> dict:
    numbers = [float(value) for value in values if float(value) > 0]
    if not numbers:
        return {
            "status": "blocked",
            "reason": "no_prices",
            "stable": False,
        }
    avg = mean(numbers)
    deviation = pstdev(numbers) if len(numbers) > 1 else 0.0
    cv = deviation / avg if avg > 0 else 1.0
    return {
        "status": "ok",
        "count": len(numbers),
        "mean": round(avg, 4),
        "stdev": round(deviation, 4),
        "coefficient_of_variation": round(cv, 6),
        "stable": cv <= 0.25,
    }
