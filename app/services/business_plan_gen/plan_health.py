def calculate_plan_health(financial_analysis, scenario_results):
    score = 0
    flags = []
    badges = []

    # --- Financial realism ---
    if not financial_analysis["concerns"]:
        score += 40
    else:
        score += max(10, 40 - len(financial_analysis["concerns"]) * 10)
        flags.append("financial_risks")

    # --- Break-even ---
    break_even = financial_analysis.get("break_even_year")
    if break_even and break_even <= 2:
        score += 20
    elif break_even:
        score += 10
        flags.append("late_break_even")
    else:
        flags.append("no_break_even")

    # --- Margin quality ---
    for s in financial_analysis.get("strengths", []):
        if "margin" in s.lower():
            score += 20
            break

    # --- Scenario resilience ---
    worst_case = scenario_results.get("worst", {})
    if worst_case.get("profit", -1) >= 0:
        score += 20
    else:
        score += 10
        flags.append("scenario_risk")

    # --- Readiness badge ---
    if score >= 80:
        badges.append("Investor Ready")
    elif score >= 60:
        badges.append("Founder Ready")
    else:
        badges.append("Needs Work")

    return {
        "score": min(score, 100),
        "badges": badges,
        "flags": flags,
        "status": readiness_label(score)
    }


def readiness_label(score):
    if score >= 80:
        return "INVESTOR_READY"
    if score >= 60:
        return "STRONG"
    if score >= 40:
        return "EARLY"
    return "NOT_READY"


def evaluate_plan_health(scenarios):
    score = 100
    warnings = []
    insights = []

    likely = scenarios.get("likely")
    best = scenarios.get("best")
    worst = scenarios.get("worst")

    # -------------------------------
    # 1. Profitability / Break-even
    # -------------------------------
    break_even = likely.get("break_even_year")

    if not break_even:
        score -= 25
        warnings.append("Plan does not reach break-even within projected period.")
    elif break_even > 3:
        score -= 15
        warnings.append("Late break-even may concern investors.")
    else:
        insights.append(f"Break-even achieved in year {break_even}.")

    # -------------------------------
    # 2. Revenue Growth Realism
    # -------------------------------
    projections = likely.get("projections", [])
    if len(projections) >= 2:
        rev_y1 = projections[0]["revenue"]
        rev_y3 = projections[-1]["revenue"]

        if rev_y3 > rev_y1 * 6:
            score -= 15
            warnings.append("Revenue growth appears overly aggressive.")
        elif rev_y3 < rev_y1 * 1.5:
            score -= 10
            warnings.append("Revenue growth may be too conservative.")
        else:
            insights.append("Revenue growth aligns with early-stage SaaS norms.")

    # -------------------------------
    # 3. Cost Structure Sanity
    # -------------------------------
    for year in projections:
        if year["expenses"] > year["revenue"] * 1.2:
            score -= 10
            warnings.append("Cost structure too heavy relative to revenue.")
            break

    # -------------------------------
    # 4. Scenario Resilience
    # -------------------------------
    worst_profit_years = [
        p["profit"] for p in worst.get("projections", [])
    ]

    if all(p < 0 for p in worst_profit_years):
        score -= 15
        warnings.append("Worst-case scenario shows sustained losses.")
    else:
        insights.append("Plan shows resilience under downside scenario.")

    # -------------------------------
    # 5. Best-case Validation
    # -------------------------------
    best_profit = max(p["profit"] for p in best.get("projections", []))
    if best_profit < 0:
        score -= 10
        warnings.append("Even best-case scenario fails to reach profitability.")

    # -------------------------------
    # Clamp Score
    # -------------------------------
    score = max(0, min(score, 100))

    return {
        "score": score,
        "grade": health_grade(score),
        "warnings": warnings,
        "insights": insights
    }


def health_grade(score):
    if score >= 85:
        return "Investor-Ready"
    elif score >= 70:
        return "Strong but Needs Refinement"
    elif score >= 55:
        return "High Risk – Major Revisions Needed"
    return "Not Investor Ready"
