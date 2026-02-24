def compare_scenarios(base, best, worst):
    """
    Compare financial scenarios and generate investor-grade insights.
    Input = analyzed financial outputs (NOT raw inputs)
    """

    insights = []

    def delta(a, b):
        if a == 0:
            return None
        return round(((b - a) / a) * 100, 2)

    # Revenue comparison
    revenue_base = base["summary"]["total_revenue"]
    revenue_best = best["summary"]["total_revenue"]
    revenue_worst = worst["summary"]["total_revenue"]

    revenue_upside = delta(revenue_base, revenue_best)
    revenue_downside = delta(revenue_base, revenue_worst)

    # Margin comparison
    margin_base = base["summary"]["gross_margin_percent"]
    margin_best = best["summary"]["gross_margin_percent"]
    margin_worst = worst["summary"]["gross_margin_percent"]

    # Break-even comparison
    break_even_base = base["summary"]["break_even_year"]
    break_even_best = best["summary"]["break_even_year"]
    break_even_worst = worst["summary"]["break_even_year"]

    # -------------------------------
    # INSIGHTS
    # -------------------------------
    if revenue_upside and revenue_upside > 40:
        insights.append(
            "Best-case scenario shows strong upside leverage with significant revenue acceleration."
        )

    if revenue_downside and revenue_downside < -30:
        insights.append(
            "Worst-case scenario indicates high sensitivity to revenue assumptions."
        )

    if break_even_worst is None:
        insights.append(
            "Business fails to break even in the worst-case scenario, indicating financial fragility."
        )

    if margin_worst < 30:
        insights.append(
            "Margins deteriorate sharply under downside conditions."
        )

    # Risk classification
    risk_level = "LOW"
    if revenue_downside and revenue_downside < -40:
        risk_level = "HIGH"
    elif revenue_downside and revenue_downside < -20:
        risk_level = "MEDIUM"

    return {
        "comparison": {
            "revenue": {
                "base": revenue_base,
                "best": revenue_best,
                "worst": revenue_worst,
                "upside_percent": revenue_upside,
                "downside_percent": revenue_downside,
            },
            "gross_margin": {
                "base": margin_base,
                "best": margin_best,
                "worst": margin_worst,
            },
            "break_even_year": {
                "base": break_even_base,
                "best": break_even_best,
                "worst": break_even_worst,
            },
        },
        "risk_level": risk_level,
        "insights": insights
    }
