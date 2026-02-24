def calculate_financials(revenue_inputs, expense_inputs, years=3):
    projections = []

    revenue = revenue_inputs.get("year1", 0)
    growth = revenue_inputs.get("growth_rate", 0)

    monthly_fixed = expense_inputs.get("monthly_fixed", 0)
    yearly_variable = expense_inputs.get("yearly_variable", 0)

    break_even_year = None

    for year in range(1, years + 1):
        yearly_revenue = round(revenue, 2)
        yearly_expense = (monthly_fixed * 12) + yearly_variable
        profit = yearly_revenue - yearly_expense

        if profit >= 0 and break_even_year is None:
            break_even_year = year

        projections.append({
            "year": year,
            "revenue": yearly_revenue,
            "expenses": yearly_expense,
            "profit": profit
        })

        revenue = revenue * (1 + growth)

    return {
        "projections": projections,
        "break_even_year": break_even_year
    }

def calculate_financials_with_scenario(
    revenue_inputs,
    expense_inputs,
    years=3,
    growth_multiplier=1.0,
    expense_multiplier=1.0
):
    projections = []

    revenue = revenue_inputs.get("year1", 0)
    growth = revenue_inputs.get("growth_rate", 0) * growth_multiplier

    monthly_fixed = expense_inputs.get("monthly_fixed", 0) * expense_multiplier
    yearly_variable = expense_inputs.get("yearly_variable", 0) * expense_multiplier

    break_even_year = None

    for year in range(1, years + 1):
        yearly_revenue = round(revenue, 2)
        yearly_expense = round((monthly_fixed * 12) + yearly_variable, 2)
        profit = round(yearly_revenue - yearly_expense, 2)

        if profit >= 0 and break_even_year is None:
            break_even_year = year

        projections.append({
            "year": year,
            "revenue": yearly_revenue,
            "expenses": yearly_expense,
            "profit": profit
        })

        revenue = revenue * (1 + growth)

    return {
        "projections": projections,
        "break_even_year": break_even_year
    }
