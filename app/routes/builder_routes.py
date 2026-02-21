"""
Builder Routes
Handles all builder-related API endpoints
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import (
    User, BuilderProfile, BuilderSkill, BuilderPortfolio, 
    BuilderApplication, SavedStartup, Startup, ApplicationStatus
)
from datetime import datetime
from sqlalchemy import and_, or_

# Create blueprint
builder_bp = Blueprint('builder', __name__)


def get_current_builder_profile():
    """Get current user's builder profile"""
    user_id = get_jwt_identity()
    profile = BuilderProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        # Create new profile if doesn't exist
        profile = BuilderProfile(user_id=user_id)
        db.session.add(profile)
        db.session.commit()
    return profile, user_id


# ==================== PROFILE ENDPOINTS ====================

@builder_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get builder's profile"""
    profile, _ = get_current_builder_profile()
    return jsonify({
        'success': True,
        'data': profile.to_dict(include_relations=True)
    }), 200


@builder_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update builder's profile"""
    profile, _ = get_current_builder_profile()
    data = request.get_json()
    
    try:
        # Update fields
        if 'title' in data:
            profile.title = data['title']
        if 'bio' in data:
            profile.bio = data['bio']
        if 'hourly_rate' in data:
            profile.hourly_rate = data['hourly_rate']
        if 'preferred_work_type' in data:
            profile.preferred_work_type = data['preferred_work_type']
        if 'industries_interested' in data:
            profile.industries_interested = data['industries_interested']
        
        profile.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'data': profile.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# ==================== SKILLS ENDPOINTS ====================

@builder_bp.route('/skills', methods=['POST'])
@jwt_required()
def add_skill():
    """Add a skill to builder's profile"""
    profile, _ = get_current_builder_profile()
    data = request.get_json()
    
    try:
        skill = BuilderSkill(
            profile_id=profile.id,
            name=data.get('name'),
            level=data.get('level'),
            years_of_experience=data.get('years_of_experience')
        )
        db.session.add(skill)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Skill added successfully',
            'data': skill.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@builder_bp.route('/skills/<int:skill_id>', methods=['DELETE'])
@jwt_required()
def remove_skill(skill_id):
    """Remove a skill from builder's profile"""
    profile, _ = get_current_builder_profile()
    
    skill = BuilderSkill.query.filter_by(
        id=skill_id,
        profile_id=profile.id
    ).first()
    
    if not skill:
        return jsonify({
            'success': False,
            'error': 'Skill not found'
        }), 404
    
    try:
        db.session.delete(skill)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Skill removed successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# ==================== PORTFOLIO ENDPOINTS ====================

@builder_bp.route('/portfolio', methods=['GET'])
@jwt_required()
def get_portfolio():
    """Get builder's portfolio items"""
    profile, _ = get_current_builder_profile()
    
    items = BuilderPortfolio.query.filter_by(profile_id=profile.id).all()
    
    return jsonify({
        'success': True,
        'data': [item.to_dict() for item in items]
    }), 200


@builder_bp.route('/portfolio', methods=['POST'])
@jwt_required()
def add_portfolio_item():
    """Add a portfolio item"""
    profile, _ = get_current_builder_profile()
    data = request.get_json()
    
    try:
        item = BuilderPortfolio(
            profile_id=profile.id,
            title=data.get('title'),
            description=data.get('description'),
            url=data.get('url'),
            image_url=data.get('image_url'),
            project_type=data.get('project_type'),
            skills_used=data.get('skills_used', [])
        )
        db.session.add(item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Portfolio item added successfully',
            'data': item.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@builder_bp.route('/portfolio/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_portfolio_item(item_id):
    """Delete a portfolio item"""
    profile, _ = get_current_builder_profile()
    
    item = BuilderPortfolio.query.filter_by(
        id=item_id,
        profile_id=profile.id
    ).first()
    
    if not item:
        return jsonify({
            'success': False,
            'error': 'Portfolio item not found'
        }), 404
    
    try:
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Portfolio item deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# ==================== APPLICATIONS ENDPOINTS ====================

@builder_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    """Get all builder's applications"""
    profile, _ = get_current_builder_profile()
    
    # Get query parameters for filtering
    status = request.args.get('status')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    query = BuilderApplication.query.filter_by(profile_id=profile.id)
    
    # Apply status filter if provided
    if status:
        query = query.filter_by(status=ApplicationStatus[status])
    
    # Order by most recent
    query = query.order_by(BuilderApplication.applied_date.desc())
    
    total = query.count()
    applications = query.limit(limit).offset(offset).all()
    
    return jsonify({
        'success': True,
        'data': [app.to_dict(include_startup=True) for app in applications],
        'total': total,
        'limit': limit,
        'offset': offset
    }), 200


@builder_bp.route('/applications/<int:app_id>', methods=['GET'])
@jwt_required()
def get_application(app_id):
    """Get single application details"""
    profile, _ = get_current_builder_profile()
    
    app = BuilderApplication.query.filter_by(
        id=app_id,
        profile_id=profile.id
    ).first()
    
    if not app:
        return jsonify({
            'success': False,
            'error': 'Application not found'
        }), 404
    
    return jsonify({
        'success': True,
        'data': app.to_dict(include_startup=True)
    }), 200


@builder_bp.route('/applications', methods=['POST'])
@jwt_required()
def apply_to_startup():
    """Submit application to a startup"""
    profile, _ = get_current_builder_profile()
    data = request.get_json()
    
    startup_id = data.get('startup_id')
    if not startup_id:
        return jsonify({
            'success': False,
            'error': 'startup_id is required'
        }), 400
    
    # Check if startup exists
    startup = Startup.query.get(startup_id)
    if not startup:
        return jsonify({
            'success': False,
            'error': 'Startup not found'
        }), 404
    
    # Check if already applied
    existing_app = BuilderApplication.query.filter_by(
        profile_id=profile.id,
        startup_id=startup_id
    ).first()
    
    if existing_app and existing_app.status != ApplicationStatus.withdrawn:
        return jsonify({
            'success': False,
            'error': 'You have already applied to this startup'
        }), 400
    
    try:
        application = BuilderApplication(
            profile_id=profile.id,
            startup_id=startup_id,
            role_applied_for=data.get('role_applied_for'),
            cover_letter=data.get('cover_letter'),
            expected_commitment=data.get('expected_commitment'),
            proposed_rate=data.get('proposed_rate')
        )
        db.session.add(application)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Application submitted successfully',
            'data': application.to_dict(include_startup=True)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@builder_bp.route('/applications/<int:app_id>', methods=['DELETE'])
@jwt_required()
def withdraw_application(app_id):
    """Withdraw an application"""
    profile, _ = get_current_builder_profile()
    
    app = BuilderApplication.query.filter_by(
        id=app_id,
        profile_id=profile.id
    ).first()
    
    if not app:
        return jsonify({
            'success': False,
            'error': 'Application not found'
        }), 404
    
    if app.status == ApplicationStatus.withdrawn:
        return jsonify({
            'success': False,
            'error': 'Application already withdrawn'
        }), 400
    
    try:
        app.status = ApplicationStatus.withdrawn
        app.withdrawn_date = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Application withdrawn successfully',
            'data': app.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


# ==================== SAVED STARTUPS ENDPOINTS ====================

@builder_bp.route('/saved-startups', methods=['GET'])
@jwt_required()
def get_saved_startups():
    """Get all saved startups"""
    profile, _ = get_current_builder_profile()
    
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    industry = request.args.get('industry')
    stage = request.args.get('stage')
    
    query = SavedStartup.query.filter_by(profile_id=profile.id)
    
    # Apply filters
    if industry or stage:
        query = query.join(Startup)
        if industry:
            query = query.filter(Startup.industry == industry)
        if stage:
            query = query.filter(Startup.stage == stage)
    
    # Order by most recent
    query = query.order_by(SavedStartup.saved_date.desc())
    
    total = query.count()
    saved = query.limit(limit).offset(offset).all()
    
    return jsonify({
        'success': True,
        'data': [s.to_dict(include_startup=True) for s in saved],
        'total': total,
        'limit': limit,
        'offset': offset
    }), 200


@builder_bp.route('/saved-startups', methods=['POST'])
@jwt_required()
def save_startup():
    """Save a startup"""
    profile, _ = get_current_builder_profile()
    data = request.get_json()
    
    startup_id = data.get('startup_id')
    if not startup_id:
        return jsonify({
            'success': False,
            'error': 'startup_id is required'
        }), 400
    
    # Check if startup exists
    startup = Startup.query.get(startup_id)
    if not startup:
        return jsonify({
            'success': False,
            'error': 'Startup not found'
        }), 404
    
    # Check if already saved
    existing = SavedStartup.query.filter_by(
        profile_id=profile.id,
        startup_id=startup_id
    ).first()
    
    if existing:
        return jsonify({
            'success': False,
            'error': 'Startup already saved'
        }), 400
    
    try:
        saved = SavedStartup(
            profile_id=profile.id,
            startup_id=startup_id,
            notes=data.get('notes')
        )
        db.session.add(saved)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Startup saved successfully',
            'data': saved.to_dict(include_startup=True)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@builder_bp.route('/saved-startups/<int:startup_id>', methods=['DELETE'])
@jwt_required()
def unsave_startup(startup_id):
    """Remove saved startup"""
    profile, _ = get_current_builder_profile()
    
    saved = SavedStartup.query.filter_by(
        profile_id=profile.id,
        startup_id=startup_id
    ).first()
    
    if not saved:
        return jsonify({
            'success': False,
            'error': 'Saved startup not found'
        }), 404
    
    try:
        db.session.delete(saved)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Startup removed from saved'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@builder_bp.route('/saved-startups/<int:startup_id>/check', methods=['GET'])
@jwt_required()
def check_saved_startup(startup_id):
    """Check if a startup is saved"""
    profile, _ = get_current_builder_profile()
    
    saved = SavedStartup.query.filter_by(
        profile_id=profile.id,
        startup_id=startup_id
    ).first()
    
    return jsonify({
        'success': True,
        'is_saved': saved is not None,
        'data': saved.to_dict() if saved else None
    }), 200


# ==================== DISCOVERY ENDPOINTS ====================

@builder_bp.route('/recommended-startups', methods=['GET'])
@jwt_required()
def get_recommended_startups():
    """Get recommended startups based on builder profile"""
    profile, _ = get_current_builder_profile()
    
    limit = request.args.get('limit', 10, type=int)
    
    # Get startups that builder hasn't already saved or applied to
    saved_startup_ids = SavedStartup.query.filter_by(
        profile_id=profile.id
    ).with_entities(SavedStartup.startup_id).all()
    saved_ids = [s[0] for s in saved_startup_ids]
    
    applied_startup_ids = BuilderApplication.query.filter_by(
        profile_id=profile.id
    ).filter(
        BuilderApplication.status != ApplicationStatus.rejected
    ).with_entities(BuilderApplication.startup_id).all()
    applied_ids = [a[0] for a in applied_startup_ids]
    
    exclude_ids = list(set(saved_ids + applied_ids))
    
    # Query startups
    query = Startup.query.filter(~Startup.id.in_(exclude_ids))
    
    # Filter by builder's interested industries if set
    if profile.industries_interested:
        query = query.filter(
            Startup.industry.in_(profile.industries_interested)
        )
    
    # Order by recently created or featured
    startups = query.order_by(
        Startup.created_at.desc()
    ).limit(limit).all()
    
    return jsonify({
        'success': True,
        'data': [{
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'logo': s.logo,
            'stage': s.stage,
            'industry': s.industry,
        } for s in startups]
    }), 200


@builder_bp.route('/startups/search', methods=['GET'])
@jwt_required()
def search_startups():
    """Search startups with filters"""
    query_str = request.args.get('q', '')
    industry = request.args.get('industry')
    stage = request.args.get('stage')
    location = request.args.get('location')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    query = Startup.query
    
    # Search by name or description
    if query_str:
        search_term = f"%{query_str}%"
        query = query.filter(
            or_(
                Startup.name.ilike(search_term),
                Startup.description.ilike(search_term)
            )
        )
    
    # Apply filters
    if industry:
        query = query.filter_by(industry=industry)
    if stage:
        query = query.filter_by(stage=stage)
    if location:
        query = query.filter(Startup.location.ilike(f"%{location}%"))
    
    total = query.count()
    startups = query.limit(limit).offset(offset).all()
    
    return jsonify({
        'success': True,
        'data': [{
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'logo': s.logo,
            'stage': s.stage,
            'industry': s.industry,
            'location': s.location,
        } for s in startups],
        'total': total,
        'limit': limit,
        'offset': offset
    }), 200


# ==================== REWARDS ENDPOINTS ====================

@builder_bp.route('/rewards', methods=['GET'])
@jwt_required()
def get_rewards_summary():
    """Get rewards summary"""
    profile, _ = get_current_builder_profile()
    
    return jsonify({
        'success': True,
        'data': {
            'paid_earnings': profile.total_earnings,
            'pending_payouts': 0,  # TODO: Calculate from transactions
            'equity_promises': profile.total_equity_earned,
            'reputation_points': int(profile.rating * 100),  # Convert rating to points
        }
    }), 200


# ==================== STATS ENDPOINTS ====================

@builder_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_builder_stats():
    """Get builder's statistics"""
    profile, _ = get_current_builder_profile()
    
    # Calculate stats
    total_applications = BuilderApplication.query.filter_by(
        profile_id=profile.id
    ).count()
    
    accepted_applications = BuilderApplication.query.filter_by(
        profile_id=profile.id,
        status=ApplicationStatus.accepted
    ).count()
    
    saved_startups_count = SavedStartup.query.filter_by(
        profile_id=profile.id
    ).count()
    
    return jsonify({
        'success': True,
        'data': {
            'total_applications': total_applications,
            'accepted_applications': accepted_applications,
            'saved_startups': saved_startups_count,
            'completed_projects': profile.completed_projects,
            'rating': profile.rating,
            'review_count': profile.review_count,
            'on_time_delivery_rate': profile.on_time_delivery_rate,
            'total_earnings': profile.total_earnings,
        }
    }), 200
