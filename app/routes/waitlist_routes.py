from flask import Blueprint, request, jsonify
from app.models.waitlist import Waitlist
from app.extensions import db
from app.utils.helper import error_response, success_response
import re

waitlist_bp = Blueprint('waitlist', __name__)

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@waitlist_bp.route('/join', methods=['POST'])
def join_waitlist():
    """Add email to waitlist"""
    data = request.get_json()
    
    if not data:
        return error_response('No data provided', 400)
    
    email = data.get('email', '').strip().lower()
    source = data.get('source', 'web')
    
    if not email:
        return error_response('Email is required', 400)
    
    if not is_valid_email(email):
        return error_response('Invalid email format', 400)
    
    try:
        # Check if email already exists
        existing = Waitlist.query.filter_by(email=email).first()
        if existing:
            return error_response('Email already registered on waitlist', 409)
        
        # Create new waitlist entry
        waitlist_entry = Waitlist(
            email=email,
            source=source
        )
        
        db.session.add(waitlist_entry)
        db.session.commit()
        
        return success_response(
            {'waitlist': waitlist_entry.to_dict()},
            'Successfully joined the waitlist!',
            201
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to join waitlist: {str(e)}', 500)

@waitlist_bp.route('', methods=['GET'])
def get_waitlist():
    """Get all waitlist entries (admin only in production)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    status_filter = request.args.get('status', type=str)
    
    query = Waitlist.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    # Order by creation date (newest first)
    query = query.order_by(Waitlist.created_at.desc())
    
    # Paginate results
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return success_response({
        'waitlist': [entry.to_dict() for entry in paginated.items],
        'pagination': {
            'page': paginated.page,
            'per_page': paginated.per_page,
            'total': paginated.total,
            'pages': paginated.pages
        }
    })

@waitlist_bp.route('/<int:waitlist_id>', methods=['PATCH'])
def update_waitlist_status(waitlist_id):
    """Update waitlist entry status (admin only in production)"""
    data = request.get_json()
    
    if not data:
        return error_response('No data provided', 400)
    
    waitlist_entry = Waitlist.query.get(waitlist_id)
    if not waitlist_entry:
        return error_response('Waitlist entry not found', 404)
    
    status = data.get('status')
    if status and status in ['pending', 'approved', 'rejected']:
        try:
            waitlist_entry.status = status
            db.session.commit()
            
            return success_response(
                {'waitlist': waitlist_entry.to_dict()},
                'Waitlist entry updated successfully'
            )
        except Exception as e:
            db.session.rollback()
            return error_response(f'Failed to update waitlist entry: {str(e)}', 500)
    else:
        return error_response('Invalid status. Must be pending, approved, or rejected', 400)

@waitlist_bp.route('/<int:waitlist_id>', methods=['DELETE'])
def delete_waitlist_entry(waitlist_id):
    """Delete waitlist entry (admin only in production)"""
    waitlist_entry = Waitlist.query.get(waitlist_id)
    if not waitlist_entry:
        return error_response('Waitlist entry not found', 404)
    
    try:
        db.session.delete(waitlist_entry)
        db.session.commit()
        
        return success_response(
            message='Waitlist entry deleted successfully'
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete waitlist entry: {str(e)}', 500)
