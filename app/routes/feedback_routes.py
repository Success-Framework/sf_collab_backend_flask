from flask import Blueprint, request
from app.extensions import db
from app.models.feedback import Feedback
from app.utils.helper import success_response, error_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

friend_requests_bp = Blueprint('friend_requests', __name__)
@friend_requests_bp.route('', methods=['OPTIONS'])
def friend_requests_options():
    return "", 200


feedback_bp = Blueprint('feedback', __name__)
@feedback_bp.route('', methods=['OPTIONS'])
def feedback_options():
    return "", 200



@feedback_bp.route('', methods=['POST'])
def create_feedback():
  data = request.get_json()
  print(data)
  feedback = Feedback(
    user_id=data.get('userId'),
    content=data.get('content')
  )
  print(feedback)
  db.session.add(feedback)
  db.session.commit()
  
  return success_response(feedback.to_dict(), "Feedback created successfully", 201)

@feedback_bp.route('', methods=['GET'])
@jwt_required()
def get_all_feedback():
  feedbacks = Feedback.query.all()
  user_id = get_jwt_identity()
  
  if not User.query.get(user_id).is_admin():
    return error_response('Unauthorized', 403)
  
  return success_response([f.to_dict() for f in feedbacks], "Feedbacks retrieved successfully")

@feedback_bp.route('/<int:feedback_id>', methods=['GET'])
def get_feedback(feedback_id):
  feedback = Feedback.query.get(feedback_id)
  if not feedback:
    return error_response('Feedback not found', 404)
  return success_response(feedback.to_dict(), "Feedback retrieved successfully")

@feedback_bp.route('/<int:feedback_id>', methods=['PUT'])
def update_feedback(feedback_id):
  feedback = Feedback.query.get(feedback_id)
  if not feedback:
    return error_response('Feedback not found', 404)
  
  data = request.get_json()
  feedback.content = data.get('content', feedback.content)
  
  db.session.commit()
  return success_response(feedback.to_dict(), "Feedback updated successfully")

@feedback_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_feedback(user_id):

  admin_id = get_jwt_identity()
  feedback = Feedback.query.filter_by(user_id=user_id).first()
  if not feedback:
    return error_response('Feedback not found', 404)
  if not User.query.get(admin_id).is_admin():
    return error_response('Unauthorized', 403)
  db.session.delete(feedback)
  db.session.commit()
  return success_response(message="Feedback deleted successfully")
