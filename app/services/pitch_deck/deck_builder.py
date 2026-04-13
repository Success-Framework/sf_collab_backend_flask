"""
deck_builder.py
Orchestrates the full pitch deck generation pipeline:
  1. Validate form data
  2. Call content_generator → AI-generated slide content
  3. Route to correct template builder
  4. Save PPTX to uploads/pitch_decks/
  5. Return file path + metadata
"""

import os
import uuid
import logging
from pathlib import Path
from datetime import datetime

from .content_generator import generate_slide_content
from .ppt_templates import (
    build_general_deck,
    build_saas_deck,
    build_fintech_deck,
    build_consumer_deck,
)

logger = logging.getLogger(__name__)

# ── Output folder ─────────────────────────────────────────────────────────────
BASE_DIR    = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
OUTPUT_DIR  = os.path.join(BASE_DIR, "uploads", "pitch_decks")
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ── Template router ───────────────────────────────────────────────────────────
TEMPLATE_BUILDERS = {
    "general":  build_general_deck,
    "saas":     build_saas_deck,
    "fintech":  build_fintech_deck,
    "consumer": build_consumer_deck,
}

VALID_TEMPLATES = set(TEMPLATE_BUILDERS.keys())


# ── Validation ────────────────────────────────────────────────────────────────

REQUIRED_FIELDS = ["company_name", "problem", "solution"]

def validate_form_data(form_data: dict) -> list:
    """
    Returns a list of error strings.
    Empty list means the form data is valid.
    """
    errors = []

    for field in REQUIRED_FIELDS:
        if not form_data.get(field, "").strip():
            errors.append(f"'{field}' is required.")

    template = form_data.get("template", "general").lower()
    if template not in VALID_TEMPLATES:
        errors.append(f"Invalid template '{template}'. Must be one of: {', '.join(VALID_TEMPLATES)}")

    return errors


# ── File naming ───────────────────────────────────────────────────────────────

def _make_filename(company_name: str) -> str:
    """Generate a safe, unique filename for the deck."""
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in company_name)
    safe_name = safe_name[:40].strip("_")
    uid = uuid.uuid4().hex[:8]
    return f"{safe_name}_{uid}.pptx"


# ── Main entry point ──────────────────────────────────────────────────────────

def build_pitch_deck(form_data: dict) -> dict:
    """
    Full pipeline: validate → generate content → build deck → save file.

    Args:
        form_data: dict from the API request body

    Returns:
        dict with keys:
            - file_path (str): absolute path to saved .pptx
            - file_name (str): filename only
            - generated_content (dict): AI slide content
            - template (str): template used

    Raises:
        ValueError: on validation errors or AI parse failure
        Exception: on unexpected errors
    """
    # 1. Normalise template
    form_data["template"] = form_data.get("template", "general").lower().strip()

    # 2. Validate
    errors = validate_form_data(form_data)
    if errors:
        raise ValueError(f"Validation failed: {'; '.join(errors)}")

    company_name = form_data["company_name"].strip()
    template     = form_data["template"]

    logger.info(f"[DeckBuilder] Starting build for '{company_name}' | template={template}")

    # 3. Generate AI slide content
    generated_content = generate_slide_content(form_data)

    # 4. Route to template builder
    builder = TEMPLATE_BUILDERS[template]
    prs = builder(generated_content)

    # 5. Save to disk
    file_name = _make_filename(company_name)
    file_path = os.path.join(OUTPUT_DIR, file_name)
    prs.save(file_path)

    logger.info(f"[DeckBuilder] Saved deck → {file_path}")

    return {
        "file_path":          file_path,
        "file_name":          file_name,
        "generated_content":  generated_content,
        "template":           template,
    }