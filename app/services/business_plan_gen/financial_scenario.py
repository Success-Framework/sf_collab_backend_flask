from app.services.business_plan_gen.financial_calculator import calculate_financials_with_scenario

from app.services.business_plan_gen.financial_calculator import calculate_financials

def generate_financial_scenarios(financials):
    """
    Generate Base / Best / Worst case financial scenarios
    """

    revenue_inputs = financials.revenue_inputs
    expense_inputs = financials.expense_inputs
    years = financials.assumptions.get("projection_years", 3)

    scenarios = {}

    # ---------------- BASE ----------------
    scenarios["base"] = calculate_financials(
        revenue_inputs,
        expense_inputs,
        years
    )

    # ---------------- BEST ----------------
    best_revenue = revenue_inputs.copy()
    best_expenses = expense_inputs.copy()

    best_revenue["growth_rate"] = revenue_inputs.get("growth_rate", 0) + 0.10
    best_expenses["monthly_fixed"] = expense_inputs.get("monthly_fixed", 0) * 0.9

    scenarios["best"] = calculate_financials(
        best_revenue,
        best_expenses,
        years
    )

    # ---------------- WORST ----------------
    worst_revenue = revenue_inputs.copy()
    worst_expenses = expense_inputs.copy()

    worst_revenue["growth_rate"] = max(
        revenue_inputs.get("growth_rate", 0) - 0.15,
        0
    )
    worst_expenses["monthly_fixed"] = expense_inputs.get("monthly_fixed", 0) * 1.15

    scenarios["worst"] = calculate_financials(
        worst_revenue,
        worst_expenses,
        years
    )

    return scenarios

