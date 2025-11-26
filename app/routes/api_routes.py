from flask import Blueprint, request, jsonify
from app.services.llm_service import handle_llm

api_bp = Blueprint("api", __name__)

@api_bp.route("/llm", methods=["POST"])
def llm():
    data = request.get_json()
    return jsonify(handle_llm(data))
