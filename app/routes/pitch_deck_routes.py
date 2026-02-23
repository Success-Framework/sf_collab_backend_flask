from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.pitch_deck import PitchDeck
from app.models.user import User
from app.extensions import db
from datetime import datetime
import uuid
from app.services.pitch_deck.generator import PitchDeckGenerator
from app.services.pitch_deck.ppt_builder import PitchDeckPPTBuilder
import os
from flask import send_file


pitch_decks_bp = Blueprint("pitch_decks", __name__)


def standard_response(success=True, data=None, error=None, code=200):
    return jsonify({
        "success": success,
        "data": data,
        "error": error
    }), code


@pitch_decks_bp.route("/", methods=["POST"])
@jwt_required()
def create_pitch_deck():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return standard_response(False, None, "Unauthorized", 401)

    data = request.get_json()

    title = data.get("title", "Untitled Deck")
    template_type = data.get("template_type", "saas")
    theme_type = data.get("theme_type", "minimal_light")

    # Temporary empty slides
    slides_json = {
        "deck_title": title,
        "slides": []
    }

    deck = PitchDeck(
        user_id=user_id,
        title=title,
        template_type=template_type,
        theme_type=theme_type,
        slides_json=slides_json,
        credits_used=0
    )

    db.session.add(deck)
    db.session.commit()

    return standard_response(True, deck.to_dict(), None, 201)


@pitch_decks_bp.route("/<deck_id>", methods=["GET"])
@jwt_required()
def get_pitch_deck(deck_id):
    user_id = get_jwt_identity()

    deck = PitchDeck.query.filter_by(id=deck_id, user_id=user_id).first()

    if not deck:
        return standard_response(False, None, "Deck not found", 404)

    return standard_response(True, deck.to_dict())


@pitch_decks_bp.route("/<deck_id>", methods=["PUT"])
@jwt_required()
def update_pitch_deck(deck_id):
    user_id = get_jwt_identity()

    deck = PitchDeck.query.filter_by(id=deck_id, user_id=user_id).first()

    if not deck:
        return standard_response(False, None, "Deck not found", 404)

    data = request.get_json()

    if "slides_json" in data:
        deck.slides_json = data["slides_json"]

    if "title" in data:
        deck.title = data["title"]

    deck.updated_at = datetime.utcnow()

    db.session.commit()

    return standard_response(True, deck.to_dict())


@pitch_decks_bp.route("/<deck_id>", methods=["DELETE"])
@jwt_required()
def delete_pitch_deck(deck_id):
    user_id = get_jwt_identity()

    deck = PitchDeck.query.filter_by(id=deck_id, user_id=user_id).first()

    if not deck:
        return standard_response(False, None, "Deck not found", 404)

    db.session.delete(deck)
    db.session.commit()

    return standard_response(True, {"message": "Deck deleted"})


@pitch_decks_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_pitch_deck():

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return standard_response(False, None, "Unauthorized", 401)

    data = request.get_json()

    title = data.get("title")
    template_type = data.get("template_type", "saas")
    theme_type = data.get("theme_type", "minimal_light")
    startup_data = data.get("startup_data")

    if not title or not startup_data:
        return standard_response(False, None, "Missing required fields", 400)

    # Credit Check
    COST = 20

    if user.credits < COST:
        return standard_response(False, None, "Not enough credits", 402)

    try:
        generator = PitchDeckGenerator()
        deck_json = generator.generate_deck(title, template_type, startup_data)

        # Deduct credits
        user.credits -= COST

        # Create deck record
        deck = PitchDeck(
            user_id=user_id,
            title=title,
            template_type=template_type,
            theme_type=theme_type,
            slides_json=deck_json,
            credits_used=COST,
            status="draft"
        )

        db.session.add(deck)
        db.session.commit()

        return standard_response(True, deck.to_dict(), None, 201)

    except Exception as e:
        db.session.rollback()
        return standard_response(False, None, str(e), 500)


@pitch_decks_bp.route("/<deck_id>/export", methods=["POST"])
@jwt_required()
def export_pitch_deck(deck_id):

    user_id = get_jwt_identity()

    deck = PitchDeck.query.filter_by(id=deck_id, user_id=user_id).first()

    if not deck:
        return standard_response(False, None, "Deck not found", 404)

    try:
        builder = PitchDeckPPTBuilder(
            deck_json=deck.slides_json,
            theme_type=deck.theme_type,
            deck_id=deck.id
        )

        filepath = builder.build()

        deck.status = "exported"
        db.session.commit()

        return standard_response(True, {
            "message": "PPT generated successfully",
            "download_url": f"/api/pitch-decks/download/{deck.id}.pptx"
        })

    except Exception as e:
        db.session.rollback()
        return standard_response(False, None, str(e), 500)


@pitch_decks_bp.route("/download/<filename>", methods=["GET"])
@jwt_required()
def download_pitch_deck(filename):

    base_upload_folder = current_app.config.get("UPLOAD_FOLDER")
    file_path = os.path.join(base_upload_folder, "pitch_decks", filename)

    if not os.path.exists(file_path):
        return standard_response(False, None, "File not found", 404)

    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )


