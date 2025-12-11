from app import create_app
from app.extensions import db
from app.models.knowledge import Knowledge

app = create_app()

def update(id, title, title_description, content_preview, category, tags):
    with app.app_context():
        item = Knowledge.query.get(id)
        if not item:
            print(f"[ERROR] Knowledge ID {id} not found.")
            return
        
        item.title = title
        item.title_description = title_description
        item.content_preview = content_preview
        item.category = category
        item.tags = tags

        db.session.commit()
        print(f"[UPDATED] Knowledge {id} updated successfully.")

update(
    1,
    "Startup Funding Basics: Seed to Series A",
    "A clear explanation of early-stage startup funding models in India...",
    "This resource explains valuation, dilution, SAFE notes, investor expectations...",
    "Startup",
    ["funding", "investment", "venture capital"]
)

update(
    2,
    "MVP Development for Early-Stage Startups",
    "How to validate ideas quickly without wasting time or money...",
    "This guide covers MVP building strategies used by Swiggy, Ola, Flipkart...",
    "Product Development",
    ["MVP", "lean", "product"]
)

update(
    3,
    "Pitch Decks That Actually Get Funding",
    "A proven structure for creating VC-ready pitch decks...",
    "Covers 12 essential pitch slides, traction, TAM-SAM-SOM, competition analysis...",
    "Startup",
    ["pitch", "fundraising", "deck"]
)

update(
    4,
    "Branding & Growth Strategy for Startups",
    "How to position your brand and scale using growth frameworks...",
    "Includes SEO, CAC vs LTV, community building, and digital strategy models...",
    "Marketing",
    ["branding", "growth", "marketing"]
)

update(
    5,
    "Legal Essentials for Indian Founders",
    "Important legal steps for early startups...",
    "Explains company registration, founder agreements, ESOP, IP rules...",
    "Legal",
    ["legal", "compliance", "india"]
)

update(
    6,
    "Building a High-Performance Startup Team",
    "Hiring and managing early-stage startup teams...",
    "Covers culture, compensation, work style, leadership, and sprint planning...",
    "Human Resources",
    ["team", "leadership", "hr"]
)
