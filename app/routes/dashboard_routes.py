from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from app.extensions import db
from app.models.user import User
from app.models.startup import Startup
from app.models.startUpMember import StartupMember
from app.models.joinRequest import JoinRequest
from app.models.task import Task
from app.models.transaction import Transaction
from app.models.idea import Idea
from app.models.knowledge import Knowledge
from app.models.post import Post
from app.models.userSocial import UserSocial
from app.models.friendRequest import FriendRequest
from app.models.Enums import UserRoles, JoinRequestStatus
from app.utils.helper import success_response, error_response

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")

@dashboard_bp.route("/founder", methods=["GET"])
@jwt_required()
def founder_dashboard():
  user_id = get_jwt_identity()

  startups = Startup.query.filter_by(creator_id=user_id).all()

  response = []

  for startup in startups:
    pending_requests = JoinRequest.query.filter_by(
      startup_id=startup.id,
      status=JoinRequestStatus.pending
    ).count()

    active_members = StartupMember.query.filter_by(
      startup_id=startup.id,
      is_active=True
    ).count()

    tasks = Task.query.filter_by(startup_id=startup.id).count()

    transactions_sum = db.session.query(
      func.coalesce(func.sum(Transaction.amount), 0)
    ).join(
      Startup, Startup.creator_id == Transaction.user_id
    ).filter(
      Startup.id == startup.id
    ).scalar()

    response.append({
      "startup": startup.to_dict(),
      "stats": {
        "members": active_members,
        "pendingJoinRequests": pending_requests,
        "tasks": tasks,
        "views": startup.views,
        "revenue": startup.revenue,
        "burnRate": startup.burn_rate,
        "runwayMonths": startup.runway_months,
        "totalDonations": transactions_sum
      }
    })

  return success_response({"role": "founder", "startups": response})

@dashboard_bp.route("/builder", methods=["GET"])
@jwt_required()
def builder_dashboard():
  user_id = get_jwt_identity()

  memberships = StartupMember.query.filter_by(
    user_id=user_id,
    is_active=True
  ).all()

  startups_data = []

  for membership in memberships:
    startup = membership.member_startup

    assigned_tasks = Task.query.filter_by(
      startup_id=startup.id,
      assigned_to=user_id
    ).all()

    startups_data.append({
      "startup": startup.to_dict(),
      "role": membership.role.value if hasattr(membership.role, "value") else membership.role,
      "tasks": {
        "total": len(assigned_tasks),
        "completed": len([t for t in assigned_tasks if t.status == "completed"]),
        "pending": len([t for t in assigned_tasks if t.status != "completed"]),
        "items": [t.to_dict() for t in assigned_tasks]
      }
    })
  print("Builder Dashboard Data:", startups_data)  # Debug print
  return success_response({"role": "builder", "startups": startups_data})

@dashboard_bp.route("/overview", methods=["GET"])
@jwt_required()
def dashboard_overview():
  user_id = get_jwt_identity()

  founded = Startup.query.filter_by(creator_id=user_id).count()
  member_of = StartupMember.query.filter_by(
    user_id=user_id,
    is_active=True
  ).count()

  tasks_assigned = Task.query.filter_by(assigned_to=user_id).count()

  return success_response({
    "foundedStartups": founded,
    "memberStartups": member_of,
    "assignedTasks": tasks_assigned
  })

@dashboard_bp.route("/profile/<int:user_id>", methods=["GET"])
@jwt_required()
def user_profile(user_id):
  current_user_id = get_jwt_identity()
  is_own_profile = int(current_user_id) == user_id

  user = User.query.get(user_id)
  if not user:
    return error_response("User not found", 404)

  # Core user info — sensitive fields only for own profile
  profile = user.to_dict(
    public=not is_own_profile,
    include_statistics=True,
  )

  # Social profile
  social = UserSocial.query.filter_by(user_id=user_id).first()
  if social:
    social_data = social.to_dict()
    if not is_own_profile:
      # Strip private social fields for other viewers
      for key in [
        "blockedUserIds", "mutedUserIds", "blockedKeywords",
        "savedPostIds", "savedIdeaIds", "savedStartupIds",
        "likedPostIds", "likedIdeaIds", "likedStartupIds", "likedCommentIds",
      ]:
        social_data.pop(key, None)
    profile["social"] = social_data

  # Startups founded
  founded_startups = Startup.query.filter_by(creator_id=user_id).all()
  profile["foundedStartups"] = [s.to_dict() for s in founded_startups]

  # Startup memberships
  memberships = StartupMember.query.filter_by(user_id=user_id, is_active=True).all()
  profile["startupMemberships"] = [m.to_dict() for m in memberships]

  # Ideas
  ideas = Idea.query.filter_by(creator_id=user_id).order_by(Idea.created_at.desc()).all()
  profile["ideas"] = [idea.to_dict() for idea in ideas]

  # Knowledge posts
  knowledge = Knowledge.query.filter_by(author_id=user_id).order_by(Knowledge.created_at.desc()).all()
  profile["knowledgePosts"] = [k.to_dict() for k in knowledge]

  # Posts
  posts = Post.query.filter_by(author_id=user_id).order_by(Post.created_at.desc()).all()
  profile["posts"] = [p.to_dict() for p in posts]

  # Achievements
  achievements = [
    ua.to_dict()
    for ua in user.user_achievements.filter_by(is_completed=True).all()
  ]
  profile["achievements"] = achievements

  # Sensitive-only sections
  if is_own_profile:
    # Tasks assigned to me
    assigned_tasks = Task.query.filter_by(assigned_to=user_id).all()
    profile["assignedTasks"] = {
      "total": len(assigned_tasks),
      "completed": len([t for t in assigned_tasks if t.status == "completed"]),
      "pending": len([t for t in assigned_tasks if t.status != "completed"]),
    }

    # Transactions
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.created_at.desc()).all()
    profile["transactions"] = [t.to_dict() for t in transactions]

    # Pending friend requests received
    pending_friend_requests = FriendRequest.query.filter_by(
      receiver_id=user_id, status="pending"
    ).all()
    profile["pendingFriendRequests"] = [
      fr.to_dict(include_user_info=True) for fr in pending_friend_requests
    ]

    # Friends count (accepted)
    friends_count = FriendRequest.query.filter(
      ((FriendRequest.sender_id == user_id) | (FriendRequest.receiver_id == user_id))
      & (FriendRequest.status == "accepted")
    ).count()
    profile["friendsCount"] = friends_count
  else:
    # For public viewers — show friendship status with current user
    friendship = FriendRequest.query.filter(
      (
        ((FriendRequest.sender_id == current_user_id) & (FriendRequest.receiver_id == user_id))
        | ((FriendRequest.sender_id == user_id) & (FriendRequest.receiver_id == current_user_id))
      )
    ).first()
    profile["friendshipStatus"] = friendship.status if friendship else None

    # Public friends count
    friends_count = FriendRequest.query.filter(
      ((FriendRequest.sender_id == user_id) | (FriendRequest.receiver_id == user_id))
      & (FriendRequest.status == "accepted")
    ).count()
    profile["friendsCount"] = friends_count

  return success_response(profile)
