# ============================================================
# AI News Sources Configuration
# Each source has:
#   key        - unique machine identifier
#   label      - display name for frontend
#   url        - RSS feed or scrape URL
#   type       - "rss" or "html"
#   category   - default category tag
#   impact     - default impact score (1-10)
#   active     - enable/disable without deleting
# ============================================================


SOURCES = [

    # ── Official AI Lab Blogs (RSS) ──────────────────────────────
    {
        "key": "openai",
        "label": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml",
        "type": "rss",
        "category": "AI Research",
        "impact": 10,
        "active": True,
        "max_articles": 20,
    },
    {
        "key": "anthropic",
        "label": "Anthropic News",
        "url": "https://www.anthropic.com/news/rss",  # fixed
        "type": "rss",
        "category": "AI Research",
        "impact": 10,
        "active": True,
        "max_articles": 20,
    },
    {
        "key": "deepmind",
        "label": "Google DeepMind Blog",
        "url": "https://deepmind.google/blog/rss.xml",
        "type": "rss",
        "category": "AI Research",
        "impact": 10,
        "active": True,
        "max_articles": 20,
    },
    {
        "key": "googleblog",
        "label": "Google AI Blog",
        "url": "https://blog.google/technology/ai/rss/",
        "type": "rss",
        "category": "AI Research",
        "impact": 9,
        "active": True,
        "max_articles": 20,
    },
    {
        "key": "metaai",
        "label": "Meta AI Blog",
        "url": "https://engineering.fb.com/feed/",  # fixed — Meta AI blog has no public RSS, FB Engineering does
        "type": "rss",
        "category": "AI Research",
        "impact": 9,
        "active": True,
        "max_articles": 20,
    },
    {
        "key": "huggingface",
        "label": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "type": "rss",
        "category": "AI Tools",
        "impact": 8,
        "active": True,
        "max_articles": 30,  # HF posts frequently, allow a bit more
    },
    {
        "key": "microsoft_ai",
        "label": "Microsoft AI Blog",
        "url": "https://blogs.microsoft.com/ai/feed/",
        "type": "rss",
        "category": "AI Research",
        "impact": 8,
        "active": True,
        "max_articles": 20,
    },
    {
        "key": "nvidia",
        "label": "NVIDIA AI Blog",
        "url": "https://blogs.nvidia.com/blog/category/deep-learning/feed/",
        "type": "rss",
        "category": "AI Hardware",
        "impact": 8,
        "active": True,
        "max_articles": 20,
    },

    # ── Tech News (RSS) ──────────────────────────────────────────
    {
        "key": "techcrunch",
        "label": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "type": "rss",
        "category": "Tech News",
        "impact": 7,
        "active": True,
        "max_articles": 20,
    },
    {
        "key": "venturebeat",
        "label": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "type": "rss",
        "category": "Tech News",
        "impact": 7,
        "active": True,
        "max_articles": 20,
    },
    {
        "key": "theverge",
        "label": "The Verge AI",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",  # fixed
        "type": "rss",
        "category": "Tech News",
        "impact": 7,
        "active": True,
        "max_articles": 20,
    },
    {
        "key": "wired",
        "label": "Wired AI",
        "url": "https://www.wired.com/feed/category/artificial-intelligence/latest/rss",  # fixed
        "type": "rss",
        "category": "Tech News",
        "impact": 7,
        "active": True,
        "max_articles": 20,
    },
    {
        "key": "mit_review",
        "label": "MIT Technology Review",
        "url": "https://www.technologyreview.com/feed/",  # fixed — topic-specific feed was broken
        "type": "rss",
        "category": "AI Research",
        "impact": 8,
        "active": True,
        "max_articles": 20,
    },
    {
        "key": "ainews",
        "label": "AI News",
        "url": "https://www.artificialintelligence-news.com/feed/",
        "type": "rss",
        "category": "Tech News",
        "impact": 6,
        "active": True,
        "max_articles": 20,
    },

    # ── Research & Community (RSS) ───────────────────────────────
    {
        "key": "arxiv",
        "label": "ArXiv CS.AI",
        "url": "https://rss.arxiv.org/rss/cs.AI",  # correct, may be rate-limiting us
        "type": "rss",
        "category": "AI Research",
        "impact": 8,
        "active": True,
        "max_articles": 30,
    },
    {
        "key": "paperswithcode",
        "label": "Papers With Code",
        "url": "https://paperswithcode.com/latest.rss",  # fixed
        "type": "rss",
        "category": "AI Research",
        "impact": 7,
        "active": True,
        "max_articles": 20,
    },
    {
        "key": "deeplearningai",
        "label": "DeepLearning.AI — The Batch",
        "url": "https://www.deeplearning.ai/the-batch/feed/",  # fixed
        "type": "rss",
        "category": "AI Education",
        "impact": 7,
        "active": True,
        "max_articles": 10,
    },
    {
        "key": "importai",
        "label": "Import AI (Jack Clark)",
        "url": "https://importai.substack.com/feed",
        "type": "rss",
        "category": "AI Research",
        "impact": 8,
        "active": True,
        "max_articles": 10,
    },
]


def get_active_sources():
    """Return only active sources."""
    return [s for s in SOURCES if s.get("active", True)]


def get_source_by_key(key):
    """Return a source config by its key."""
    return next((s for s in SOURCES if s["key"] == key), None)


def get_sources_by_category(category):
    """Return all active sources for a given category."""
    return [s for s in SOURCES if s.get("category") == category and s.get("active", True)]