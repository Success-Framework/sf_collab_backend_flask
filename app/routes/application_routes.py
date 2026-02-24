from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.application import ApplicationJob
from app.models.user import User
from app.utils.helper import success_response, error_response, paginate

# Import notification helpers
from app.notifications.helpers import (
    notify_application_submitted,
    notify_application_approved,
    notify_application_rejected,
    notify_info
)

applications_bp = Blueprint('applications', __name__)


def get_user_full_name(user_id):
    """Helper to get user's full name"""
    user = User.query.get(user_id)
    if user:
        return f"{user.first_name or ''} {user.last_name or ''}".strip() or "Someone"
    return "Someone"


# ========================== GET ALL APPLICATIONS ==========================
@applications_bp.route('', methods=['GET'])
@jwt_required()
def get_all_applications():
    """Get all applications with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    app_type = request.args.get('type', type=str)
    search = request.args.get('search', type=str)
    
    query = ApplicationJob.query
    
    # Apply filters
    if app_type:
        query = query.filter(ApplicationJob.application_type == app_type)
    if search:
        query = query.filter(
            (ApplicationJob.name.ilike(f'%{search}%')) |
            (ApplicationJob.email.ilike(f'%{search}%'))
        )
    
    result = paginate(query, page, per_page)
    
    return success_response({
        'applications': [application.to_dict() for application in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })


# ========================== GET JOB APPLICATIONS ==========================
@applications_bp.route('/jobs', methods=['GET'])
@jwt_required()
def get_job_applications():
    """Get all job applications with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', type=str)
    
    query = ApplicationJob.query.filter_by(application_type='job')
    
    if search:
        query = query.filter(
            (ApplicationJob.name.ilike(f'%{search}%')) |
            (ApplicationJob.email.ilike(f'%{search}%'))
        )
    
    result = paginate(query, page, per_page)
    
    return success_response({
        'job_applications': [application.to_dict() for application in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })


# ========================== GET INFLUENCER APPLICATIONS ==========================
@applications_bp.route('/influencers', methods=['GET'])
@jwt_required()
def get_influencer_applications():
    """Get all influencer applications with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', type=str)
    
    query = ApplicationJob.query.filter_by(application_type='influencer')
    
    if search:
        query = query.filter(
            (ApplicationJob.name.ilike(f'%{search}%')) |
            (ApplicationJob.email.ilike(f'%{search}%'))
        )
    
    result = paginate(query, page, per_page)
    
    return success_response({
        'influencer_applications': [app.to_dict() for app in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })


# ========================== GET SINGLE APPLICATION ==========================
@applications_bp.route('/<int:application_id>', methods=['GET'])
@jwt_required()
def get_application(application_id):
    """Get single application by ID"""
    application = ApplicationJob.query.get(application_id)
    if not application:
        return error_response('Application not found', 404)
    
    return success_response({'application': application.to_dict()})


# ========================== CREATE JOB APPLICATION ==========================
@applications_bp.route('/jobs', methods=['POST'])
def create_job_application():
    """Create a new job application"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email']
        if not all(field in data for field in required_fields):
            return error_response('Missing required fields: name, email', 400)
        
        application = ApplicationJob(
            name=data.get('name'),
            email=data.get('email'),
            country=data.get('country'),
            application_type='job',
            data=data.get('data')
        )
        
        db.session.add(application)
        db.session.commit()
        
        # ════════════════════════════════════════════════════════════
        # ✨ NOTIFICATION: Application Submitted (4.13)
        # ════════════════════════════════════════════════════════════
        # If user_id is provided (logged in user), notify them
        user_id = data.get('user_id')
        if user_id:
            try:
                position = data.get('data', {}).get('position', 'Job Position')
                notify_application_submitted(
                    user_id=user_id,
                    position=position,
                    application_id=application.id
                )
            except Exception as e:
                print(f"⚠️ Job application notification failed: {e}")
        
        return success_response(
            {'application': application.to_dict()},
            'Job application created successfully',
            201
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create job application: {str(e)}', 500)


# ========================== CREATE INFLUENCER APPLICATION ==========================
@applications_bp.route('/influencers', methods=['POST'])
def create_influencer_application():
    """Create a new influencer application"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email']
        if not all(field in data for field in required_fields):
            return error_response('Missing required fields: name, email', 400)
        
        application = ApplicationJob(
            user_id=data.get('user_id'),
            name=data.get('name'),
            email=data.get('email'),
            country=data.get('country'),
            application_type='influencer',
            data=data.get('data')
        )
        
        db.session.add(application)
        db.session.commit()
        
        # ════════════════════════════════════════════════════════════
        # ✨ NOTIFICATION: Influencer Application Submitted (4.13)
        # ════════════════════════════════════════════════════════════
        user_id = data.get('user_id')
        if user_id:
            try:
                notify_application_submitted(
                    user_id=user_id,
                    position="Influencer Program",
                    application_id=application.id
                )
            except Exception as e:
                print(f"⚠️ Influencer application notification failed: {e}")
        
        return success_response(
            {'application': application.to_dict()},
            'Influencer application created successfully',
            201
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create influencer application: {str(e)}', 500)


# ========================== UPDATE APPLICATION STATUS ==========================
@applications_bp.route('/<int:application_id>/status', methods=['PUT'])
@jwt_required()
def update_application_status(application_id):
    """Update application status (approve/reject)"""
    try:
        application = ApplicationJob.query.get(application_id)
        if not application:
            return error_response('Application not found', 404)
        
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['pending', 'approved', 'rejected', 'reviewing']:
            return error_response('Invalid status. Must be: pending, approved, rejected, or reviewing', 400)
        
        old_status = application.status if hasattr(application, 'status') else 'pending'
        
        # Update status
        if hasattr(application, 'status'):
            application.status = new_status
        
        db.session.commit()
        
        # ════════════════════════════════════════════════════════════
        # ✨ NOTIFICATION: Application Status Changed (4.13)
        # ════════════════════════════════════════════════════════════
        if application.user_id and old_status != new_status:
            try:
                position = "Influencer Program" if application.application_type == 'influencer' else "Job Position"
                
                if new_status == 'approved':
                    notify_application_approved(
                        user_id=application.user_id,
                        position=position,
                        application_id=application.id
                    )
                elif new_status == 'rejected':
                    notify_application_rejected(
                        user_id=application.user_id,
                        position=position,
                        application_id=application.id
                    )
                elif new_status == 'reviewing':
                    notify_info(
                        user_id=application.user_id,
                        message=f"Your application for {position} is now being reviewed."
                    )
            except Exception as e:
                print(f"⚠️ Application status notification failed: {e}")
        
        return success_response(
            {'application': application.to_dict()},
            f'Application status updated to {new_status}'
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update application status: {str(e)}', 500)


# ========================== DELETE APPLICATION ==========================
@applications_bp.route('/<int:application_id>', methods=['DELETE'])
@jwt_required()
def delete_application(application_id):
    """Delete an application"""
    try:
        application = ApplicationJob.query.get(application_id)
        if not application:
            return error_response('Application not found', 404)
        
        db.session.delete(application)
        db.session.commit()
        
        return success_response(message='Application deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete application: {str(e)}', 500)