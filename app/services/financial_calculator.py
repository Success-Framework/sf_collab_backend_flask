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
