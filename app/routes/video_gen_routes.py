from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from app.services.video_generation.limit_service import (
    can_generate_video,
    increment_video_usage,
    remaining_videos
)
from app.services.video_generation.video_service import generate_video
from app.services.video_generation.prompt_service import enhance_video_prompt
from app.services.video_generation.file_validator import validate_files



video_bp = Blueprint("video", __name__)

def standard_response(success=True, data=None, error=None, code=200):
    return jsonify({
        "success": success,
        "data": data,
        "error": error
    }), code


@video_bp.route("/generate", methods=["POST", "OPTIONS"])
@jwt_required()
def generate_video_route():
    # ----------------------------
    # CORS preflight
    # ----------------------------
    if request.method == "OPTIONS":
        return standard_response(True, {}, code=200)

    # ----------------------------
    # Auth
    # ----------------------------
    user_id = get_jwt_identity()

    # ----------------------------
    # Basic inputs
    # ----------------------------
    mode = request.form.get("mode")
    raw_prompt = request.form.get("prompt")
    style = request.form.get("style", "cinematic")

    try:
        duration = int(request.form.get("duration", 10))
    except ValueError:
        return standard_response(False, None, "Invalid duration", 400)

    # ----------------------------
    # Validation
    # ----------------------------
    if not mode or not raw_prompt:
        return standard_response(False, None, "mode and prompt are required", 400)

    if mode not in ["text", "image", "video"]:
        return standard_response(False, None, "Invalid mode", 400)

    if duration < 5 or duration > 30:
        return standard_response(
            False,
            None,
            "Duration must be between 5 and 30 seconds",
            400
        )

    # ----------------------------
    # Daily limit check
    # ----------------------------
    if not can_generate_video(user_id):
        return standard_response(
            False,
            {
                "remaining_today": 0
            },
            "Daily video generation limit reached",
            429
        )

    # ----------------------------
    # Prompt enhancement (Groq-first)
    # ----------------------------
    enhanced_prompt = enhance_video_prompt(
        mode=mode,
        user_prompt=raw_prompt,
        duration=duration,
        style=style
    )

    # ----------------------------
    # Video generation (provider-based)
    # ----------------------------
    # ----------------------------
    # File validation & preparation
    # ----------------------------
    try:
        prepared_inputs = validate_files(mode, request.files)
    except ValueError as e:
        return standard_response(False, None, str(e), 400)

    # ----------------------------
    # Video generation
    # ---------------------------- 
    
    try:
        result = generate_video(
        mode=mode,
        prompt=enhanced_prompt,
        duration=duration,
        input_files=prepared_inputs
    )  
    except Exception as e:
        return standard_response(
            False,
            None,
            f"Video generation failed: {str(e)}",
            500
        )

    # ----------------------------
    # Increment usage AFTER success
    # ----------------------------
    increment_video_usage(user_id)

    # ----------------------------
    # Final response
    # ----------------------------
    return standard_response(True, {
        "video_url": f"/api/video/download/{result['filename']}",
        "mode": mode,
        "duration": duration,
        "remaining_today": remaining_videos(user_id),
        "generated_at": datetime.utcnow().isoformat()
    })
    
    
# Full Flow Summary:
# Request
#  → JWT user_id
#  → Validate inputs
#  → Check daily limit
#  → Enhance prompt (Groq)
#  → Generate video (provider)
#  → Save output
#  → Increment usage
#  → Return final URL

@video_bp.route("/download/<filename>", methods=["GET"])
@jwt_required()
def download_video(filename):
    user_id = get_jwt_identity()
    video_path = os.path.join(current_app.config["VIDEO_OUTPUT_DIR"], secure_filename(filename))

    if not os.path.exists(video_path):
        return standard_response(False, None, "File not found", 404)

    return send_file(video_path, as_attachment=True)