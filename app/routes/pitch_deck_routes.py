"""
pitch_deck_routes.py
All pitch deck API endpoints.

Endpoints:
    POST   /api/pitch-deck/generate        — generate a new deck
    GET    /api/pitch-deck/my-decks        — list the current user's decks
    GET    /api/pitch-deck/download/<id>   — download a specific deck file
    DELETE /api/pitch-deck/delete/<id>     — delete a deck record + file
"""

import os
import logging
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.pitch_deck import PitchDeck
from app.services.pitch_deck import build_pitch_deck

logger = logging.getLogger(__name__)

pitch_deck_bp = Blueprint("pitch_deck", __name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ok(data=None, message="success", code=200):
    return jsonify({"success": True, "message": message, "data": data}), code


def _err(message="error", code=400):
    return jsonify({"success": False, "error": message}), code


# ── POST /generate ────────────────────────────────────────────────────────────

@pitch_deck_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_deck():
    """
    Generate a pitch deck from form data.

    Expected JSON body:
    {
        "template":            "general | saas | fintech | consumer",
        "company_name":        "string (required)",
        "tagline":             "string",
        "founder_name":        "string",
        "problem":             "string (required)",
        "solution":            "string (required)",
        "market_size":         "string",
        "product_description": "string",
        "key_features":        ["string", ...],
        "traction":            "string",
        "team_members":        [{"name": "string", "role": "string"}, ...],
        "funding_ask":         "string",
        "use_of_funds":        "string"
    }
    """
    user_id   = get_jwt_identity()
    form_data = request.get_json(silent=True)

    if not form_data:
        return _err("Request body must be JSON.", 400)

    # ── Build the deck ────────────────────────────────────────────────────────
    try:
        result = build_pitch_deck(form_data)
    except ValueError as e:
        logger.warning(f"[PitchDeck] Validation/AI error for user {user_id}: {e}")
        return _err(str(e), 400)
    except Exception as e:
        logger.exception(f"[PitchDeck] Unexpected error for user {user_id}")
        return _err("Failed to generate pitch deck. Please try again.", 500)

    # ── Save DB record ────────────────────────────────────────────────────────
    try:
        deck = PitchDeck(
            user_id           = user_id,
            company_name      = form_data.get("company_name", "").strip(),
            tagline           = form_data.get("tagline", ""),
            template          = result["template"],
            sector            = form_data.get("sector", ""),
            form_data         = form_data,
            generated_content = result["generated_content"],
            file_path         = result["file_path"],
            file_name         = result["file_name"],
            status            = "generated",
        )
        db.session.add(deck)
        db.session.commit()
    except Exception as e:
        logger.exception("[PitchDeck] DB save failed")
        # File was generated; still return download info but warn
        return jsonify({
            "success": True,
            "message": "Deck generated but could not be saved to database.",
            "data": {
                "file_name": result["file_name"],
                "template":  result["template"],
            }
        }), 207

    return _ok({
        "deck_id":   deck.id,
        "file_name": deck.file_name,
        "template":  deck.template,
        "download_url": f"/api/pitch-deck/download/{deck.id}",
    }, "Pitch deck generated successfully.", 201)


# ── GET /my-decks ─────────────────────────────────────────────────────────────

@pitch_deck_bp.route("/my-decks", methods=["GET"])
@jwt_required()
def my_decks():
    """Return a list of all pitch decks created by the current user."""
    user_id = get_jwt_identity()

    decks = (
        PitchDeck.query
        .filter_by(user_id=user_id)
        .order_by(PitchDeck.created_at.desc())
        .all()
    )

    return _ok([d.to_list_dict() for d in decks])


# ── GET /download/<id> ────────────────────────────────────────────────────────

@pitch_deck_bp.route("/download/<int:deck_id>", methods=["GET"])
@jwt_required()
def download_deck(deck_id):
    """Download the PPTX file for a specific deck (must belong to requesting user)."""
    user_id = get_jwt_identity()

    deck = PitchDeck.query.filter_by(id=deck_id, user_id=user_id).first()
    if not deck:
        return _err("Pitch deck not found.", 404)

    if not deck.file_path or not os.path.exists(deck.file_path):
        return _err("Pitch deck file is no longer available.", 404)

    return send_file(
        deck.file_path,
        as_attachment=True,
        download_name=deck.file_name,
        mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )


# ── DELETE /delete/<id> ───────────────────────────────────────────────────────

@pitch_deck_bp.route("/delete/<int:deck_id>", methods=["DELETE"])
@jwt_required()
def delete_deck(deck_id):
    """Delete a pitch deck record and its associated file."""
    user_id = get_jwt_identity()

    deck = PitchDeck.query.filter_by(id=deck_id, user_id=user_id).first()
    if not deck:
        return _err("Pitch deck not found.", 404)

    # Delete file from disk
    if deck.file_path and os.path.exists(deck.file_path):
        try:
            os.remove(deck.file_path)
        except OSError as e:
            logger.warning(f"[PitchDeck] Could not delete file {deck.file_path}: {e}")

    db.session.delete(deck)
    db.session.commit()

    return _ok(message="Pitch deck deleted successfully.")