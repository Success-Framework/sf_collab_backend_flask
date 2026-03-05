def generate_financial_advice(base_analysis, scenario_comparison, health_score):
    advice = {
        "strengths": [],
        "concerns": [],
        "recommendations": [],
        "investor_summary": ""
    }

    summary = base_analysis["summary"]
    margin = summary["gross_margin_percent"]
    break_even = summary["break_even_year"]
    avg_profit = summary["avg_profit"]
    risk_level = scenario_comparison["risk_level"]
    score = health_score["score"]

    # ----------------------------
    # Strengths
    # ----------------------------
    if margin >= 40:
        advice["strengths"].append(
            "Strong gross margins align well with investor expectations."
        )

    if break_even and break_even <= 2:
        advice["strengths"].append(
            "Early break-even improves capital efficiency."
        )

    if avg_profit > 100000:
        advice["strengths"].append(
            "Profitability outlook indicates scalable unit economics."
        )

    # ----------------------------
    # Concerns
    # ----------------------------
    if margin < 30:
        advice["concerns"].append(
            "Gross margin is below typical SaaS benchmarks (40–60%)."
        )

    if break_even is None or break_even > 3:
        advice["concerns"].append(
            "Late or missing break-even increases funding dependency."
        )

    if risk_level == "HIGH":
        advice["concerns"].append(
            "Financial outcomes are highly sensitive to assumptions."
        )

    # ----------------------------
    # Recommendations
    # ----------------------------
    if margin < 40:
        advice["recommendations"].append(
            "Review pricing strategy or reduce variable costs to improve margins."
        )

    if break_even and break_even > 2:
        advice["recommendations"].append(
            "Delay hiring or phase operational expenses to accelerate break-even."
        )

    if risk_level != "LOW":
        advice["recommendations"].append(
            "Run conservative forecasts and present downside mitigation strategies to investors."
        )

    # ----------------------------
    # Investor Summary
    # ----------------------------
    if score >= 80:
        summary_text = (
            "This business demonstrates strong financial fundamentals "
            "and would be attractive to early-stage investors."
        )
    elif score >= 65:
        summary_text = (
            "The business shows promise but requires refinement "
            "before being investor-ready."
        )
    elif score >= 50:
        summary_text = (
            "Investors may perceive moderate risk due to financial assumptions."
        )
    else:
        summary_text = (
            "The current financial structure may deter investors "
            "without significant revisions."
        )

    advice["investor_summary"] = summary_text

    return advice
