from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.utils.helper import success_response, error_response, paginate
from app.models.error import Error
from app.models.user import User
from datetime import datetime
main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    endpoints = {}

    for rule in current_app.url_map.iter_rules():
        if rule.endpoint == "static":
            continue

        blueprint = rule.endpoint.split(".")[0]
        endpoints.setdefault(blueprint, set()).add(str(rule))

    return {
        "message": "Flask API is running",
        "version": "1.0.0",
        "endpoints": {
            bp: sorted(paths)
            for bp, paths in endpoints.items()
        }
    }

@main_bp.route("/api/log-client-error", methods=["POST"])
def log_client_error():
    """Endpoint to receive client-side error logs"""
    data = request.get_json() or {}
    error_message = data.get('errorMessage', 'Unknown error')
    error_from_backend = data.get('errorFromBackend')
    stack = data.get('stack')
    page = data.get('page')
    component = data.get('component', 'Unknown Component')
    user_agent = request.headers.get('User-Agent', 'Unknown')
    url = page or 'Unknown URL'
    # Check if error already exists by checking message, stack, and URL
    existing_error = Error.query.filter_by(
        error_message=error_message,
        error_from_backend=error_from_backend,
        page=url
    ).first()
    if existing_error:
        current_app.logger.warning(f"Error already exists: {error_message}")
        return  success_response({"message": "Error already logged"}, "Duplicate error", 200)

    error = Error(
        error_message=error_message[:500] if error_message else None,
        error_from_backend=error_from_backend[:255] if error_from_backend else None,
        stack=stack,
        page=url,
        component=component,
    )
    current_app.logger.error(f"Client error: {error_message} | URL: {url} | User-Agent: {user_agent}")
    db.session.add(error)
    db.session.commit()

    return success_response({"message": "Error logged successfully"}, "Error logged", 201)

@main_bp.route("/api/errors", methods=["GET"])
@jwt_required()
def get_errors():
    """Get all logged errors (admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return error_response("Unauthorized", 403)
    
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 10)
    
    query = Error.query.order_by(Error.created_at.desc())
    paginated = paginate(query, page, per_page)
    
    return success_response({
        "errors": [e.to_dict() for e in paginated['items']],
        "pagination": {
            "page": paginated['page'],
            "per_page": paginated['per_page'],
            "total": paginated['total'],
            "pages": paginated['pages']
        }
    })
@main_bp.route('/api/errors/<int:error_id>', methods=["DELETE"])
@jwt_required()
def delete_error(error_id):
    """Delete a specific error log (admin only)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return error_response("Unauthorized", 403)
    error = Error.query.get(error_id)
    if not error:
        return error_response("Error not found", 404)
    db.session.delete(error)
    db.session.commit()
    return success_response({"message": "Error deleted successfully"})