import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger



logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(daemon=True)


def _scrape_job():
    """
    Wrapper that runs the scraper inside the Flask app context.
    APScheduler runs in a separate thread — app context is required
    for DB access.
    """
    from app.services.ai_news.scraper import run_scraper
    try:
        logger.info("[Scheduler] Starting scheduled scrape...")
        results = run_scraper()
        logger.info(
            f"[Scheduler] Scrape done — "
            f"saved: {results['total_saved']}, "
            f"skipped: {results['total_skipped']}"
        )
    except Exception as e:
        logger.error(f"[Scheduler] Scrape job failed: {e}")


def start_scheduler(app):
    """
    Start the background scheduler with the Flask app context.
    Call this once from create_app().

    Schedule: every 12 hours — scrapes all active sources, skips duplicates.

    To change frequency, update IntervalTrigger(hours=12) below.
    """

    # ── Gunicorn multi-worker fix ─────────────────────────────────────────────
    # Gunicorn spawns multiple worker processes. Without this guard,
    # each worker starts its own scheduler = duplicate scrapes.
    # We only start the scheduler in the FIRST worker process.
    #
    # How it works:
    #   - Gunicorn sets a unique ID per worker via environment variable
    #   - We only proceed if this is worker #1 (or we're in dev mode)
    #   - In dev (Flask's built-in server), this env var won't be set,
    #     so the scheduler always starts normally in local.

    worker_id = os.environ.get("GUNICORN_WORKER_ID", "0")
    if worker_id not in ("0", "1"):
        logger.info(f"[Scheduler] Skipping start on Gunicorn worker {worker_id}")
        return

    if scheduler.running:
        logger.info("[Scheduler] Already running, skipping start.")
        return

    # Wrap job so it always runs inside the Flask app context
    def job_with_context():
        with app.app_context():
            _scrape_job()

    # ── Every 12 hours ────────────────────────────────────────────────────────
    scheduler.add_job(
        func=job_with_context,
        trigger=IntervalTrigger(hours=12),
        id="ai_news_scraper",
        name="AI News Scraper",
        replace_existing=True,
        max_instances=1,        # prevents overlap if a run takes long
        misfire_grace_time=300, # if missed by <5 min, still run it
    )

    # ── Startup run ───────────────────────────────────────────────────────────
    # Run once immediately when the app starts so the DB isn't empty
    # on first launch. Comment this out after your first successful deploy.
    scheduler.add_job(
        func=job_with_context,
        trigger="date",         # run once, right now
        id="ai_news_scraper_startup",
        name="AI News Scraper — Startup",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("[Scheduler] AI News scraper started — runs every 12 hours.")


def stop_scheduler():
    """Gracefully stop the scheduler (on app teardown)."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Stopped.")