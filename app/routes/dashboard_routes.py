from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from app.extensions import db
from app.models.startup import Startup
from app.models.startUpMember import StartupMember
from app.models.joinRequest import JoinRequest
from app.models.task import Task
from app.models.transaction import Transaction
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
