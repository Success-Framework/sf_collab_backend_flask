# app/services/pitch_deck/templates.py

TEMPLATES = {

    "saas": [
        "cover",
        "problem",
        "solution",
        "market",
        "product",
        "business_model",
        "traction",
        "competition",
        "competitive_advantage",
        "go_to_market",
        "financials",
        "team",
        "roadmap",
        "fundraising_ask",
        "closing"
    ],

    "fintech": [
        "cover",
        "problem",
        "solution",
        "market",
        "product",
        "compliance",
        "business_model",
        "traction",
        "competition",
        "risk_analysis",
        "financials",
        "team",
        "roadmap",
        "fundraising_ask",
        "closing"
    ],

    "consumer": [
        "cover",
        "problem",
        "solution",
        "market",
        "product",
        "traction",
        "brand_positioning",
        "competition",
        "go_to_market",
        "financials",
        "team",
        "roadmap",
        "fundraising_ask",
        "closing"
    ],

    "ai_startup": [
        "cover",
        "problem",
        "solution",
        "technology",
        "market",
        "product",
        "business_model",
        "traction",
        "competition",
        "moat",
        "financials",
        "team",
        "roadmap",
        "fundraising_ask",
        "closing"
    ]
}


def get_template(template_type: str):
    """
    Returns slide structure list for a given template.
    Defaults to SaaS if invalid.
    """
    return TEMPLATES.get(template_type, TEMPLATES["saas"])
