from app.models.plan import Plan
from app.extensions import db  # your SQLAlchemy instance
PLANS = [
    {
        "id": "early",
        "title": "Early Pioneer",
        "description": "For early believers",
        "price": 3900,
        "currency": "usd",
        "note": "One-time",

        "stripe_price_id": "price_early_xxx",

        "accent": "indigo",
        "highlight": False,
        "crown": False,
        "cta": "Claim Early Access",

        "features": [
            "Lifetime Pro access",
            "Beta access",
            "Pioneer badge",
            "Priority support",
        ],

        "limit": 100,
    },
    {
        "id": "builder",
        "title": "Professional Builder",
        "description": "Most popular",
        "price": 9900,
        "currency": "usd",
        "note": "One-time",

        "stripe_price_id": "price_builder_xxx",

        "accent": "violet",
        "highlight": True,
        "crown": False,
        "cta": "Upgrade to Pro",

        "features": [
            "2 years Pro access",
            "Advanced analytics",
            "Custom domain (1 year)",
            "Priority support",
        ],
    },
    {
        "id": "agency",
        "title": "Agency Partner",
        "description": "Teams & studios",
        "price": 29900,
        "currency": "usd",
        "note": "One-time",

        "stripe_price_id": "price_agency_xxx",

        "accent": "slate",
        "highlight": False,
        "crown": False,
        "cta": "Scale with SFCollab",

        "features": [
            "3 years Pro access",
            "5 team seats",
            "White-label options",
            "Dev team access",
        ],
    },
    {
        "id": "founder",
        "title": "Founding Member",
        "description": "Shape the platform",
        "price": 99900,
        "currency": "usd",
        "note": "Lifetime",

        "stripe_price_id": "price_founder_xxx",

        "accent": "gold",
        "highlight": False,
        "crown": True,
        "cta": "Become a Member",

        "features": [
            "Lifetime access (10 users)",
            "Monthly founder calls",
            "Feature priority",
            "All future products",
        ],

        "limit": 50,
    },
]
def insert_default_plans():
    for plan_data in PLANS:
        # check if plan already exists to avoid duplicates
        existing = Plan.query.get(plan_data['id'])
        if existing:
            continue
        
        plan = Plan(
            id=plan_data['id'],
            title=plan_data['title'],
            description=plan_data['description'],
            price=plan_data['price'],
            currency=plan_data['currency'],
            note=plan_data.get('note'),
            stripe_price_id=plan_data['stripe_price_id'],
            accent=plan_data.get('accent'),
            highlight=plan_data.get('highlight', False),
            crown=plan_data.get('crown', False),
            cta=plan_data.get('cta'),
            features=plan_data.get('features', []),
            limit=plan_data.get('limit')
        )
        db.session.add(plan)
    db.session.commit()
    print("Default plans inserted!")
