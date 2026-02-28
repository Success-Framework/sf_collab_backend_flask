from datetime import datetime
from app.extensions import db


class AINewsArticle(db.Model):
    __tablename__ = 'ai_news_articles'

    id = db.Column(db.Integer, primary_key=True)

    # Core content
    title = db.Column(db.String(500), nullable=False)
    url = db.Column(db.String(1000), nullable=False, unique=True)  # unique prevents duplicates
    summary = db.Column(db.Text, nullable=True)
    author = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(1000), nullable=True)

    # Categorization
    source = db.Column(db.String(100), nullable=False)        # e.g. "openai", "techcrunch"
    source_label = db.Column(db.String(100), nullable=True)   # e.g. "OpenAI Blog", "TechCrunch"
    category = db.Column(db.String(100), nullable=True)       # e.g. "AI Research", "Funding", "Tools"
    tags = db.Column(db.Text, nullable=True)                  # comma-separated tags e.g. "llm,gpt,openai"

    # Scoring
    impact_score = db.Column(db.Integer, default=5)           # 1-10, auto-assigned by source tier

    # Timestamps
    published_at = db.Column(db.DateTime, nullable=True)      # from the article/feed itself
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Control
    is_active = db.Column(db.Boolean, default=True)           # soft delete / hide article

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'summary': self.summary,
            'author': self.author,
            'image_url': self.image_url,
            'source': self.source,
            'source_label': self.source_label,
            'category': self.category,
            'tags': self.tags.split(',') if self.tags else [],
            'impact_score': self.impact_score,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
        }