from flask import Blueprint, request, jsonify
from app.models.suggestion import Suggestion
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

suggestions_bp = Blueprint('suggestions', __name__)

@suggestions_bp.route('', methods=['GET'])
def get_suggestions():
    """Get all suggestions with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    idea_id = request.args.get('idea_id', type=int)
    author_id = request.args.get('author_id', type=int)
    status = request.args.get('status', type=str)
    
    query = Suggestion.query
    
    if idea_id:
        query = query.filter(Suggestion.idea_id == idea_id)
    if author_id:
        query = query.filter(Suggestion.author_id == author_id)
    if status:
        from app.models.Enums import SuggestionStatus
        query = query.filter(Suggestion.status == SuggestionStatus(status))
    
    result = paginate(query.order_by(Suggestion.created_at.desc()), page, per_page)
    
    return success_response({
        'suggestions': [suggestion.to_dict() for suggestion in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@suggestions_bp.route('/<int:suggestion_id>', methods=['GET'])
def get_suggestion(suggestion_id):
    """Get single suggestion by ID"""
    suggestion = Suggestion.query.get(suggestion_id)
    if not suggestion:
        return error_response('Suggestion not found', 404)
    
    return success_response({'suggestion': suggestion.to_dict()})

@suggestions_bp.route('', methods=['POST'])
def create_suggestion():
    """Create new suggestion"""
    data = request.get_json()
    
    required_fields = ['idea_id', 'content', 'author_id', 'author_first_name', 'author_last_name']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields')
    
    try:
        suggestion = Suggestion(
            idea_id=data['idea_id'],
            content=data['content'],
            author_id=data['author_id'],
            author_first_name=data['author_first_name'],
            author_last_name=data['author_last_name']
        )
        
        db.session.add(suggestion)
        db.session.commit()
        
        return success_response({
            'suggestion': suggestion.to_dict()
        }, 'Suggestion created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create suggestion: {str(e)}', 500)

@suggestions_bp.route('/<int:suggestion_id>/approve', methods=['POST'])
def approve_suggestion(suggestion_id):
    """Approve suggestion"""
    suggestion = Suggestion.query.get(suggestion_id)
    if not suggestion:
        return error_response('Suggestion not found', 404)
    
    if suggestion.is_approved():
        return error_response('Suggestion is already approved', 400)
    
    try:
        suggestion.approve()
        return success_response({
            'suggestion': suggestion.to_dict()
        }, 'Suggestion approved successfully')
    except Exception as e:
        return error_response(f'Failed to approve suggestion: {str(e)}', 500)

@suggestions_bp.route('/<int:suggestion_id>/reject', methods=['POST'])
def reject_suggestion(suggestion_id):
    """Reject suggestion"""
    suggestion = Suggestion.query.get(suggestion_id)
    if not suggestion:
        return error_response('Suggestion not found', 404)
    
    if suggestion.is_rejected():
        return error_response('Suggestion is already rejected', 400)
    
    try:
        suggestion.reject()
        return success_response({
            'suggestion': suggestion.to_dict()
        }, 'Suggestion rejected successfully')
    except Exception as e:
        return error_response(f'Failed to reject suggestion: {str(e)}', 500)

@suggestions_bp.route('/<int:suggestion_id>/status', methods=['PUT'])
def update_suggestion_status(suggestion_id):
    """Update suggestion status"""
    suggestion = Suggestion.query.get(suggestion_id)
    if not suggestion:
        return error_response('Suggestion not found', 404)
    
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return error_response('Status is required', 400)
    
    try:
        suggestion.update_status(new_status)
        return success_response({
            'suggestion': suggestion.to_dict()
        }, 'Suggestion status updated successfully')
    except Exception as e:
        return error_response(f'Failed to update suggestion status: {str(e)}', 500)

@suggestions_bp.route('/idea/<int:idea_id>/pending-count', methods=['GET'])
def get_pending_suggestions_count(idea_id):
    """Get count of pending suggestions for an idea"""
    count = Suggestion.query.filter_by(idea_id=idea_id, status='pending').count()
    
    return success_response({
        'idea_id': idea_id,
        'pending_suggestions_count': count
    })

@suggestions_bp.route('/<int:suggestion_id>', methods=['DELETE'])
def delete_suggestion(suggestion_id):
    """Delete suggestion"""
    suggestion = Suggestion.query.get(suggestion_id)
    if not suggestion:
        return error_response('Suggestion not found', 404)
    
    try:
        db.session.delete(suggestion)
        db.session.commit()
        return success_response(message='Suggestion deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete suggestion: {str(e)}', 500)