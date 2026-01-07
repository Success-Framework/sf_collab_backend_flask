from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.contributionPolls import ContributionPoll
from app.utils.helper import success_response, error_response
from app.models.user import User
from app.models.userRole import UserRole
from datetime import datetime, timedelta
from app.models.Enums import UserRoles
poll_bp = Blueprint('contribution_polls', __name__)

# ========================== CREATE POLL ==========================
@poll_bp.route('', methods=['POST'])
@jwt_required()
def create_poll():
  """Create a new contribution poll"""
  data = request.get_json()
  user_id = int(get_jwt_identity())
  user = User.query.get(user_id)
  print(user, user.role)
  if not user or not user.is_admin():
    return error_response('Unauthorized', status=403)
  
  
  required_fields = ['title', 'description', 'options', 'points', 'ends_in_days']
  
  if not all(field in data for field in required_fields):
    return error_response('Missing required fields', status=400)

  poll = ContributionPoll(
    title=data['title'],
    description=data['description'],
    options=data['options'],
    points=data['points'],
    ends_in_days=data['ends_in_days']
  )
  
  db.session.add(poll)
  db.session.commit()
  
  return success_response(poll.to_dict(), message='Poll created successfully', status=201)

# ========================== GET ALL POLLS ==========================
@poll_bp.route('', methods=['GET'])
def get_polls():
  """Get all contribution polls"""
  ContributionPoll.autodelete_polls()
  polls = ContributionPoll.query.all()
  
  return success_response({
    
    'polls': [poll.to_dict() for poll in polls]
    
    })

# ========================== GET POLL BY ID ==========================
@poll_bp.route('/<int:poll_id>', methods=['GET'])
def get_poll(poll_id):
  """Get a specific contribution poll"""
  poll = ContributionPoll.query.get(poll_id)
  if not poll:
    return error_response('Poll not found', status=404)
  
  return success_response(poll.to_dict())

# ========================== UPDATE POLL ==========================
@poll_bp.route('/<int:poll_id>', methods=['PUT'])
@jwt_required()
def update_poll(poll_id):
  """Update a contribution poll"""
  poll = ContributionPoll.query.get(poll_id)
  if not poll:
    return error_response('Poll not found', status=404)

  data = request.get_json()
  for key, value in data.items():
    setattr(poll, key, value)

  db.session.commit()
  return success_response(poll.to_dict(), message='Poll updated successfully')


@poll_bp.route('/<int:poll_id>/vote', methods=['POST'])
@jwt_required()
def vote_poll(poll_id):
    poll = ContributionPoll.query.get(poll_id)
    if not poll:
        return error_response('Poll not found', status=404)

    if poll.created_at + timedelta(days=poll.ends_in_days) < datetime.utcnow():
        return error_response('Poll has ended', status=400)

    data = request.get_json()
    option = data.get('option_index')

    if option is None or option < 0 or option >= len(poll.options):
        return error_response('Invalid option', status=400)

    user_id = int(get_jwt_identity())
    print(user_id)
    users_voted = poll.users_voted or []

    if user_id in users_voted:
        return error_response('User already voted', status=400)

    votes = poll.votes or {}
    key = str(option)
    votes[key] = votes.get(key, 0) + 1
    print(votes)
    users_voted.append(user_id)

    poll.votes = votes
    poll.users_voted = users_voted
    print(poll.to_dict())
    db.session.commit()
    return success_response(poll.to_dict(), message='Vote recorded successfully')


# ========================== DELETE POLL ==========================
@poll_bp.route('/<int:poll_id>', methods=['DELETE'])
@jwt_required()
def delete_poll(poll_id):
  """Delete a contribution poll"""
  poll = ContributionPoll.query.get(poll_id)
  if not poll:
    return error_response('Poll not found', status=404)

  db.session.delete(poll)
  db.session.commit()
  return success_response(message='Poll deleted successfully')

# ========================== AUTO DELETE EXPIRED POLLS ==========================
@poll_bp.route('/auto-delete', methods=['POST'])
def auto_delete_polls():
  """Automatically delete expired polls"""
  ContributionPoll.autodelete_polls()
  return success_response(message='Expired polls deleted successfully')