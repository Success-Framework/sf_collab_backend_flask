INDUSTRY_BENCHMARKS = {
    "saas": {
        "gross_margin": 0.70,
        "revenue_growth": 0.35,
        "marketing_ratio": 0.25,
        "engineering_ratio": 0.30,
        "break_even_year": 3
    },
    "ecommerce": {
        "gross_margin": 0.45,
        "revenue_growth": 0.25,
        "marketing_ratio": 0.30,
        "engineering_ratio": 0.15,
        "break_even_year": 2
    },
    "fintech": {
        "gross_margin": 0.65,
        "revenue_growth": 0.30,
        "marketing_ratio": 0.20,
        "engineering_ratio": 0.35,
        "break_even_year": 3
    }
}

def get_industry_benchmark(industry: str):
    if not industry:
        return None

    key = industry.lower().strip()
    return INDUSTRY_BENCHMARKS.get(key)
