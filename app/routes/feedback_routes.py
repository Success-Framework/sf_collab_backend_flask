from flask import Blueprint, request
from app.extensions import db
from app.models.feedback import Feedback
from app.utils.helper import success_response, error_response, paginate
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.notifications.helpers import notify_info, notify_success, notify_error

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('', methods=['OPTIONS'])
def feedback_options():
  return "", 200

@feedback_bp.route('', methods=['POST'])
def create_feedback():
  data = request.get_json()
  user_id = data.get('userId')
  
  feedback = Feedback(
  user_id=user_id,
  content=data.get('content')
  )
  db.session.add(feedback)
  db.session.commit()
  
  notify_success(user_id, "Your feedback has been submitted successfully")
  
  return success_response(feedback.to_dict(), "Feedback created successfully", 201)

@feedback_bp.route('', methods=['GET'])
@jwt_required()
def get_all_feedback():
  user_id = get_jwt_identity()
  user = User.query.get(user_id)
  
  if not user.is_admin():
    notify_error(user_id, "Unauthorized access attempt")
    return error_response('Unauthorized', 403)
  
  page = request.args.get('page', 1, type=int)
  per_page = request.args.get('per_page', 10, type=int)
  
  result = paginate(Feedback.query, page, per_page)
  
  return success_response({
    "feedback": [f.to_dict() for f in result['items']],
    "pagination": {
      "page": result['page'],
      "per_page": result['per_page'],
      "total": result['total'],
      "pages": result['pages']
    }
  }, "Feedbacks retrieved successfully")


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
  
  notify_success(feedback.user_id, "Your feedback has been updated")
  
  return success_response(feedback.to_dict(), "Feedback updated successfully")

@feedback_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_feedback(user_id):
  admin_id = get_jwt_identity()
  admin = User.query.get(admin_id)
  
  if not admin.is_admin():
    notify_error(admin_id, "Unauthorized deletion attempt")
    return error_response('Unauthorized', 403)
  
  feedback = Feedback.query.filter_by(user_id=user_id).first()
  if not feedback:
    return error_response('Feedback not found', 404)
  
  db.session.delete(feedback)
  db.session.commit()
  
  return success_response(message="Feedback deleted successfully")
