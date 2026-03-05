import logging
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import desc, asc

from app.extensions import db
from app.models.aiNews import AINewsArticle
from app.services.ai_news.scraper import run_scraper
from app.services.ai_news.sources import get_active_sources, SOURCES

logger = logging.getLogger(__name__)

ai_news_bp = Blueprint("ai_news", __name__)


# ── Standard response helper (matches your existing pattern) ──────────────────

def standard_response(success=True, data=None, error=None, code=200):
    return jsonify({"success": success, "data": data, "error": error}), code


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/news
# Paginated article feed with optional filters
# Query params:
#   page         (int, default 1)
#   per_page     (int, default 20, max 50)
#   category     (str) e.g. "AI Research"
#   source       (str) e.g. "openai"
#   sort         (str) "latest" | "oldest" | "impact"  — default "latest"
#   search       (str) search in title
# ─────────────────────────────────────────────────────────────────────────────

@ai_news_bp.route("/ainews", methods=["GET"])
@jwt_required()
def get_news():
    try:
        # ── Pagination ────────────────────────────────────────────
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 50)

        # ── Filters ───────────────────────────────────────────────
        category = request.args.get("category", "").strip()
        source = request.args.get("source", "").strip()
        search = request.args.get("search", "").strip()
        sort = request.args.get("sort", "latest").strip().lower()

        # ── Build query ───────────────────────────────────────────
        query = AINewsArticle.query.filter_by(is_active=True)

        if category:
            query = query.filter(AINewsArticle.category.ilike(f"%{category}%"))

        if source:
            query = query.filter(AINewsArticle.source == source)

        if search:
            query = query.filter(AINewsArticle.title.ilike(f"%{search}%"))

        # ── Sorting ───────────────────────────────────────────────
        if sort == "oldest":
            query = query.order_by(asc(AINewsArticle.published_at))
        elif sort == "impact":
            query = query.order_by(desc(AINewsArticle.impact_score), desc(AINewsArticle.published_at))
        else:  # default: latest
            query = query.order_by(desc(AINewsArticle.published_at))

        # ── Paginate ──────────────────────────────────────────────
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return standard_response(True, {
            "articles": [a.to_dict() for a in paginated.items],
            "pagination": {
                "page": paginated.page,
                "per_page": per_page,
                "total": paginated.total,
                "total_pages": paginated.pages,
                "has_next": paginated.has_next,
                "has_prev": paginated.has_prev,
            }
        })

    except Exception as e:
        logger.error(f"[GET /news] Error: {e}")
        return standard_response(False, None, str(e), 500)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/news/categories
# Returns all unique categories present in the DB
# ─────────────────────────────────────────────────────────────────────────────

@ai_news_bp.route("/ainews/categories", methods=["GET"])
@jwt_required()
def get_categories():
    try:
        rows = (
            db.session.query(AINewsArticle.category)
            .filter(AINewsArticle.is_active == True, AINewsArticle.category != None)
            .distinct()
            .all()
        )
        categories = sorted([r[0] for r in rows if r[0]])
        return standard_response(True, {"categories": categories})

    except Exception as e:
        logger.error(f"[GET /news/categories] Error: {e}")
        return standard_response(False, None, str(e), 500)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/news/sources
# Returns all configured sources with their status info
# ─────────────────────────────────────────────────────────────────────────────

@ai_news_bp.route("/ainews/sources", methods=["GET"])
@jwt_required()
def get_sources():
    try:
        # Count articles per source from DB
        from sqlalchemy import func
        counts = (
            db.session.query(AINewsArticle.source, func.count(AINewsArticle.id))
            .filter_by(is_active=True)
            .group_by(AINewsArticle.source)
            .all()
        )
        count_map = {source: count for source, count in counts}

        sources_data = []
        for s in SOURCES:
            sources_data.append({
                "key": s["key"],
                "label": s["label"],
                "category": s["category"],
                "impact": s["impact"],
                "active": s["active"],
                "article_count": count_map.get(s["key"], 0),
            })

        return standard_response(True, {"sources": sources_data})

    except Exception as e:
        logger.error(f"[GET /news/sources] Error: {e}")
        return standard_response(False, None, str(e), 500)


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/news/<int:article_id>
# Returns a single article by ID
# ─────────────────────────────────────────────────────────────────────────────

@ai_news_bp.route("/ainews/<int:article_id>", methods=["GET"])
@jwt_required()
def get_article(article_id):
    try:
        article = AINewsArticle.query.filter_by(id=article_id, is_active=True).first()
        if not article:
            return standard_response(False, None, "Article not found", 404)

        return standard_response(True, {"article": article.to_dict()})

    except Exception as e:
        logger.error(f"[GET /news/{article_id}] Error: {e}")
        return standard_response(False, None, str(e), 500)


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/news/scrape
# Manually trigger a scrape run
# Body (optional): { "sources": ["openai", "anthropic"] }
#   — omit to scrape all active sources
# ─────────────────────────────────────────────────────────────────────────────

@ai_news_bp.route("/ainews/scrape", methods=["POST"])
@jwt_required()
def trigger_scrape():
    try:
        data = request.get_json(silent=True) or {}
        source_keys = data.get("sources", None)  # None = scrape all

        logger.info(f"Manual scrape triggered — sources: {source_keys or 'ALL'}")

        results = run_scraper(source_keys=source_keys)

        return standard_response(True, {
            "message": "Scrape completed",
            "results": results,
            "triggered_at": datetime.utcnow().isoformat(),
        })

    except Exception as e:
        logger.error(f"[POST /news/scrape] Error: {e}")
        return standard_response(False, None, str(e), 500)