from app.services.business_plan_gen.industry_benchmarks import get_industry_benchmark


def calculate_health_score(base_analysis, scenario_comparison, industry):
    """
    Investor-grade financial health score (0–100)
    """

    score = 100
    reasons = []

    summary = base_analysis.get("summary", {})
    margin = summary.get("gross_margin_percent", 0)
    break_even = summary.get("break_even_year")
    avg_profit = summary.get("avg_profit", 0)

    risk_level = scenario_comparison.get("risk_level", "LOW")

    benchmark = get_industry_benchmark(industry)

    # ----------------------------
    # Gross Margin Impact (30 pts)
    # ----------------------------
    if benchmark:
        target_margin = benchmark["gross_margin"] * 100
        if margin < target_margin * 0.7:
            score -= 25
            reasons.append(
                f"Gross margin ({margin}%) is far below industry benchmark ({target_margin}%)."
            )
        elif margin < target_margin:
            score -= 15
            reasons.append(
                f"Gross margin ({margin}%) is below industry benchmark ({target_margin}%)."
            )
    else:
        if margin < 30:
            score -= 15
            reasons.append("Gross margin is low for venture-backed businesses.")

    # ----------------------------
    # Break-even Impact (25 pts)
    # ----------------------------
    if break_even is None:
        score -= 25
        reasons.append("Business does not break even within projection window.")
    elif benchmark and break_even > benchmark["break_even_year"]:
        score -= 15
        reasons.append(
            f"Break-even year ({break_even}) exceeds industry expectation."
        )
    elif break_even > 3:
        score -= 8

    # ----------------------------
    # Profitability Impact (15 pts)
    # ----------------------------
    if avg_profit < 0:
        score -= 15
        reasons.append("Average profitability is negative.")
    elif avg_profit < 50000:
        score -= 8
        reasons.append("Profitability is low relative to operational risk.")

    # ----------------------------
    # Scenario Risk Impact (30 pts)
    # ----------------------------
    if risk_level == "HIGH":
        score -= 25
        reasons.append("High downside risk under worst-case scenario.")
    elif risk_level == "MEDIUM":
        score -= 12
        reasons.append("Moderate sensitivity to assumptions.")

    # ----------------------------
    # Normalize
    # ----------------------------
    score = max(0, min(100, score))

    # ----------------------------
    # Grade
    # ----------------------------
    if score >= 80:
        grade = "EXCELLENT"
    elif score >= 65:
        grade = "GOOD"
    elif score >= 50:
        grade = "FAIR"
    else:
        grade = "WEAK"

    return {
        "score": score,
        "grade": grade,
        "reasons": reasons
    }
