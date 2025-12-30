from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app.models.storyView import StoryView
from app.models.story import Story

from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

story_views_bp = Blueprint('story_views', __name__)

@story_views_bp.route('', methods=['GET'])
def get_story_views():
    """Get all story views with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    story_id = request.args.get('story_id', type=int)
    user_id = request.args.get('user_id', type=int)
    recent_only = request.args.get('recent_only', 'false').lower() == 'true'
    
    query = StoryView.query
    
    if story_id:
        query = query.filter(StoryView.story_id == story_id)
    if user_id:
        query = query.filter(StoryView.user_id == user_id)
    if recent_only:
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        query = query.filter(StoryView.viewed_at >= hour_ago)
    
    result = paginate(query.order_by(StoryView.viewed_at.desc()), page, per_page)
    
    return success_response({
        'views': [view.to_dict() for view in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@story_views_bp.route('/<int:view_id>', methods=['GET'])
def get_story_view(view_id):
    """Get single story view by ID"""
    view = StoryView.query.get(view_id)
    if not view:
        return error_response('Story view not found', 404)
    
    return success_response({'view': view.to_dict()})

@story_views_bp.route('/story/<int:story_id>/count', methods=['GET'])
def get_story_view_count(story_id):
    """Get view count for a story"""
    count = StoryView.query.filter_by(story_id=story_id).count()
    
    return success_response({
        'story_id': story_id,
        'view_count': count
    })

@story_views_bp.route('/user/<int:user_id>/story/<int:story_id>', methods=['GET'])
def check_user_viewed_story(user_id, story_id):
    """Check if user has viewed a story"""
    view = StoryView.query.filter_by(
        user_id=user_id,
        story_id=story_id
    ).first()
    
    return success_response({
        'has_viewed': view is not None,
        'view': view.to_dict() if view else None
    })

@story_views_bp.route('/analytics/popular', methods=['GET'])
def get_popular_stories():
    """Get most popular stories by views"""
    limit = request.args.get('limit', 10, type=int)
    hours = request.args.get('hours', 24, type=int)
    
    from sqlalchemy import func
    
    # Calculate date cutoff
    cutoff_date = datetime.utcnow() - timedelta(hours=hours)
    
    # Get popular stories
    popular_stories = db.session.query(
        StoryView.story_id,
        func.count(StoryView.id).label('view_count')
    ).filter(
        StoryView.viewed_at >= cutoff_date
    ).group_by(
        StoryView.story_id
    ).order_by(
        func.count(StoryView.id).desc()
    ).limit(limit).all()
    
    # Get story details
    result = []
    for story_id, view_count in popular_stories:
        story = Story.query.get(story_id)
        if story and not story.is_expired():
            result.append({
                'story': story.to_dict(),
                'view_count': view_count
            })
    
    return success_response({
        'popular_stories': result,
        'period_hours': hours
    })

@story_views_bp.route('/<int:view_id>', methods=['DELETE'])
def delete_story_view(view_id):
    """Delete story view"""
    view = StoryView.query.get(view_id)
    if not view:
        return error_response('Story view not found', 404)
    
    try:
        # Decrement story view count
        story = Story.query.get(view.story_id)
        if story and story.views > 0:
            story.views -= 1
            db.session.commit()
        
        db.session.delete(view)
        db.session.commit()
        
        return success_response(message='Story view deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete story view: {str(e)}', 500)