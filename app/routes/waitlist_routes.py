from flask import Blueprint, request
from app.extensions import db
from app.models.waitlist import Waitlist
from app.utils.helper import success_response, error_response
from flask_jwt_extended import jwt_required

waitlist_bp = Blueprint("waitlist", __name__)

# -------------------------------------------------
# Register to waitlist
# POST /waitlist/register
# -------------------------------------------------
@waitlist_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    email = data.get("email")
    name = data.get("name")
    id = data.get("id")
    if not email:
        return error_response("email is required", 400)
    
    success, message, payload = Waitlist.register(email, name, id)

    if not success:
        return error_response(message, 400)

    return success_response(
        {
            "email": email,
            "name": name,
            **payload
        },
        message,
        201
    )

# -------------------------------------------------
# Check if email is on waitlist
# POST /waitlist/check
# -------------------------------------------------
@waitlist_bp.route("/check", methods=["POST"])
def check_waitlist():
    data = request.get_json() or {}
    email = data.get("email")

    if not email:
        return error_response("email is required", 400)

    result = Waitlist.is_on_waitlist(email)

    return success_response({
        "is_on_waitlist": result["on_waitlist"],
        "position": result["position"]
    })

# -------------------------------------------------
# Get total waitlist count
# GET /waitlist/count
# -------------------------------------------------
@waitlist_bp.route("/count", methods=["GET"])
def total_count():
    count = Waitlist.query.count()
    max_allowed = Waitlist.get_max_allowed()

    return success_response({
        "total": count,
        "max_allowed": max_allowed,
        "full": count >= max_allowed
    })

# -------------------------------------------------
# Get my waitlist info + points
# Protected (email from token or client)
# GET /waitlist/me/<id>
# -------------------------------------------------
@waitlist_bp.route("/me/<int:user_id>", methods=["GET"])
@jwt_required()
def my_waitlist(user_id):
    user = Waitlist.query.get(user_id)
    if not user:
        return error_response("User not found on waitlist", 404)

    return success_response(user.to_dict())

# -------------------------------------------------
# Leaderboard (points-based)
# GET /waitlist/leaderboard
# -------------------------------------------------
@waitlist_bp.route("/leaderboard", methods=["GET"])
def leaderboard():
    limit = request.args.get("limit", 10, type=int)

    users = Waitlist.leaderboard(limit)

    return success_response([
        {
            **user.to_dict(),
            "rank": index + 1
        }
        for index, user in enumerate(users)
    ])

# -------------------------------------------------
# Add points (ADMIN / SYSTEM ONLY)
# POST /waitlist/add-points
# -------------------------------------------------
@waitlist_bp.route("/add-points", methods=["POST"])
@jwt_required()
def add_points():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    category = data.get("category")

    if not all([user_id, category]):
        return error_response(
            "user_id and category are required",
            400
        )

    user = Waitlist.query.get(user_id)
    if not user:
        return error_response("User not found on waitlist", 404)

    try:
        points = {
            'referral': Waitlist.POINTS_PER_REFERRAL,
            'contribution': Waitlist.POINTS_PER_CONTRIBUTION,
            'activity': Waitlist.POINTS_PER_ACTIVITY
        }.get(category)
        user.add_points(int(points), category)
    except ValueError as e:
        return error_response(str(e), 400)

    return success_response(
        user.to_dict(),
        "Points added successfully"
    )
@waitlist_bp.route("/heartbeat/<int:user_id>", methods=["GET"])
@jwt_required()
def heartbeat(user_id):

    print("Heartbeat received for user_id:", user_id)
    user = Waitlist.query.filter_by(id=user_id).first()

    if not user:
        return {"error": "User not found"}, 404

    points_added = user.register_activity()
    db.session.commit()

    return {
        "success": True,
        "pointsAdded": points_added,
        "totalActivityPoints": user.activity_points
    }, 200
