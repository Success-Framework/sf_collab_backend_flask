from app.services.business_plan_gen.industry_benchmarks import get_industry_benchmark
from app.services.business_plan_gen.financial_calculator import calculate_financials


def analyze_financials(
    plan,
    revenue_inputs,
    expense_inputs,
    scenario="base"
):
    """
    Returns:
    - projections
    - break-even
    - benchmark comparison
    - warnings
    """

    projections_data = calculate_financials(
        revenue_inputs,
        expense_inputs,
        years=3
    )

    benchmark = get_industry_benchmark(plan.industry)
    warnings = []
    comparisons = {}

    if benchmark:
        total_revenue = sum(p["revenue"] for p in projections_data["projections"])
        total_expense = sum(p["expenses"] for p in projections_data["projections"])

        gross_margin = (
            (total_revenue - total_expense) / total_revenue
            if total_revenue > 0 else 0
        )

        comparisons["gross_margin"] = {
            "value": round(gross_margin, 2),
            "industry_avg": benchmark["gross_margin"],
            "status": "good" if gross_margin >= benchmark["gross_margin"] else "low"
        }

        if gross_margin < benchmark["gross_margin"]:
            warnings.append(
                "Gross margin is below industry average. Consider reducing costs or increasing pricing."
            )

        if projections_data["break_even_year"]:
            if projections_data["break_even_year"] > benchmark["break_even_year"]:
                warnings.append(
                    "Break-even occurs later than industry norm."
                )
        else:
            warnings.append("Business does not reach break-even within 3 years.")

    return {
        "scenario": scenario,
        "projections": projections_data["projections"],
        "break_even_year": projections_data["break_even_year"],
        "benchmarks": comparisons,
        "warnings": warnings
    }
