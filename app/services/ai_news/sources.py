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
    },
    {
        "key": "anthropic",
        "label": "Anthropic News",
        "url": "https://www.anthropic.com/rss.xml",
        "type": "rss",
        "category": "AI Research",
        "impact": 10,
        "active": True,
    },
    {
        "key": "deepmind",
        "label": "Google DeepMind Blog",
        "url": "https://deepmind.google/blog/rss.xml",
        "type": "rss",
        "category": "AI Research",
        "impact": 10,
        "active": True,
    },
    {
        "key": "googleblog",
        "label": "Google AI Blog",
        "url": "https://blog.google/technology/ai/rss/",
        "type": "rss",
        "category": "AI Research",
        "impact": 9,
        "active": True,
    },
    {
        "key": "metaai",
        "label": "Meta AI Blog",
        "url": "https://ai.meta.com/blog/rss/",
        "type": "rss",
        "category": "AI Research",
        "impact": 9,
        "active": True,
    },
    {
        "key": "huggingface",
        "label": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "type": "rss",
        "category": "AI Tools",
        "impact": 8,
        "active": True,
    },
    {
        "key": "microsoft_ai",
        "label": "Microsoft AI Blog",
        "url": "https://blogs.microsoft.com/ai/feed/",
        "type": "rss",
        "category": "AI Research",
        "impact": 8,
        "active": True,
    },
    {
        "key": "nvidia",
        "label": "NVIDIA AI Blog",
        "url": "https://blogs.nvidia.com/blog/category/deep-learning/feed/",
        "type": "rss",
        "category": "AI Hardware",
        "impact": 8,
        "active": True,
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
    },
    {
        "key": "venturebeat",
        "label": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "type": "rss",
        "category": "Tech News",
        "impact": 7,
        "active": True,
    },
    {
        "key": "theverge",
        "label": "The Verge AI",
        "url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
        "type": "rss",
        "category": "Tech News",
        "impact": 7,
        "active": True,
    },
    {
        "key": "wired",
        "label": "Wired AI",
        "url": "https://www.wired.com/feed/tag/artificial-intelligence/latest/rss",
        "type": "rss",
        "category": "Tech News",
        "impact": 7,
        "active": True,
    },
    {
        "key": "mit_review",
        "label": "MIT Technology Review",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "type": "rss",
        "category": "AI Research",
        "impact": 8,
        "active": True,
    },
    {
        "key": "ainews",
        "label": "AI News",
        "url": "https://www.artificialintelligence-news.com/feed/",
        "type": "rss",
        "category": "Tech News",
        "impact": 6,
        "active": True,
    },

    # ── Research & Community (RSS) ───────────────────────────────
    {
        "key": "arxiv",
        "label": "ArXiv CS.AI",
        "url": "https://rss.arxiv.org/rss/cs.AI",
        "type": "rss",
        "category": "AI Research",
        "impact": 8,
        "active": True,
    },
    {
        "key": "paperswithcode",
        "label": "Papers With Code",
        "url": "https://paperswithcode.com/rss.xml",
        "type": "rss",
        "category": "AI Research",
        "impact": 7,
        "active": True,
    },
    {
        "key": "deeplearningai",
        "label": "DeepLearning.AI — The Batch",
        "url": "https://www.deeplearning.ai/the-batch/rss/",
        "type": "rss",
        "category": "AI Education",
        "impact": 7,
        "active": True,
    },
    {
        "key": "importai",
        "label": "Import AI (Jack Clark)",
        "url": "https://importai.substack.com/feed",
        "type": "rss",
        "category": "AI Research",
        "impact": 8,
        "active": True,
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