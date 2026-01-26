from app.services.business_plan_gen.financial_calculator import calculate_financials_with_scenario

def generate_financial_scenarios(financials):
    assumptions = financials.assumptions or {}
    scenarios = assumptions.get("scenarios", {})
    years = assumptions.get("years", 3)

    results = {}

    for name, config in scenarios.items():
        results[name] = calculate_financials_with_scenario(
            revenue_inputs=financials.revenue_inputs,
            expense_inputs=financials.expense_inputs,
            years=years,
            growth_multiplier=config.get("growth_multiplier", 1.0),
            expense_multiplier=config.get("expense_multiplier", 1.0)
        )

    return results
