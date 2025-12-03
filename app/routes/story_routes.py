from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app.models.story import Story
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

stories_bp = Blueprint('stories', __name__, url_prefix='/api/stories')

@stories_bp.route('', methods=['GET'])
def get_stories():
    """Get all stories with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    author_id = request.args.get('author_id', type=int)
    story_type = request.args.get('type', type=str)
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    include_viewers = request.args.get('include_viewers', 'false').lower() == 'true'
    
    query = Story.query
    
    if user_id:
        query = query.filter(Story.user_id == user_id)
    if author_id:
        query = query.filter(Story.author_id == author_id)
    if story_type:
        from app.models.Enums import StoryType
        query = query.filter(Story.type == StoryType(story_type))
    if active_only:
        query = query.filter(Story.expires_at > datetime.utcnow())
    
    result = paginate(query.order_by(Story.created_at.desc()), page, per_page)
    
    current_user_id = request.args.get('current_user_id', type=int)
    
    return success_response({
        'stories': [story.to_dict(
            include_viewers=include_viewers,
            user_id=current_user_id
        ) for story in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@stories_bp.route('/<int:story_id>', methods=['GET'])
def get_story(story_id):
    """Get single story by ID"""
    story = Story.query.get(story_id)
    if not story:
        return error_response('Story not found', 404)
    
    include_viewers = request.args.get('include_viewers', 'false').lower() == 'true'
    current_user_id = request.args.get('current_user_id', type=int)
    
    return success_response({
        'story': story.to_dict(
            include_viewers=include_viewers,
            user_id=current_user_id
        )
    })

@stories_bp.route('', methods=['POST'])
def create_story():
    """Create new story"""
    data = request.get_json()
    
    required_fields = ['user_id', 'author_id', 'author_first_name', 'author_last_name', 'media_url', 'expires_at']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields')
    
    try:
        # Set expiry to 24 hours from now if not provided
        expires_at = data.get('expires_at')
        if not expires_at:
            expires_at = (datetime.utcnow() + timedelta(hours=24)).isoformat()
        
        story = Story(
            user_id=data['user_id'],
            author_id=data['author_id'],
            author_first_name=data['author_first_name'],
            author_last_name=data['author_last_name'],
            media_url=data['media_url'],
            caption=data.get('caption'),
            type=data.get('type', 'image'),
            expires_at=datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        )
        
        db.session.add(story)
        db.session.commit()
        
        return success_response({
            'story': story.to_dict()
        }, 'Story created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create story: {str(e)}', 500)

@stories_bp.route('/<int:story_id>', methods=['PUT'])
def update_story(story_id):
    """Update story"""
    story = Story.query.get(story_id)
    if not story:
        return error_response('Story not found', 404)
    
    data = request.get_json()
    
    try:
        if 'caption' in data:
            story.caption = data['caption']
        if 'media_url' in data:
            story.media_url = data['media_url']
        if 'expires_at' in data:
            story.expires_at = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00'))
        
        db.session.commit()
        
        return success_response({
            'story': story.to_dict()
        }, 'Story updated successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update story: {str(e)}', 500)

@stories_bp.route('/<int:story_id>/view', methods=['POST'])
def view_story(story_id):
    """Record story view"""
    story = Story.query.get(story_id)
    if not story:
        return error_response('Story not found', 404)
    
    if story.is_expired():
        return error_response('Story has expired', 410)  # 410 Gone
    
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return error_response('User ID is required', 400)
    
    # Check if user already viewed this story
    from models.storyView import StoryView
    existing_view = StoryView.query.filter_by(story_id=story_id, user_id=user_id).first()
    
    if existing_view:
        # Update the existing view timestamp
        existing_view.viewed_at = datetime.utcnow()
        db.session.commit()
        return success_response({
            'story': story.to_dict(user_id=user_id),
            'view': existing_view.to_dict()
        }, 'Story view updated')
    
    try:
        # Create view record
        view = StoryView(story_id=story_id, user_id=user_id)
        db.session.add(view)
        
        # Increment story view count
        story.increment_views()
        
        db.session.commit()
        
        return success_response({
            'story': story.to_dict(user_id=user_id),
            'view': view.to_dict()
        }, 'Story viewed successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to record story view: {str(e)}', 500)

@stories_bp.route('/active', methods=['GET'])
def get_active_stories():
    """Get active stories for users"""
    user_ids = request.args.getlist('user_ids', type=int)
    
    if not user_ids:
        return error_response('User IDs are required', 400)
    
    # Get active stories from specified users
    active_stories = Story.query.filter(
        Story.user_id.in_(user_ids),
        Story.expires_at > datetime.utcnow()
    ).order_by(Story.created_at.desc()).all()
    
    current_user_id = request.args.get('current_user_id', type=int)
    
    # Group stories by user
    stories_by_user = {}
    for story in active_stories:
        if story.user_id not in stories_by_user:
            stories_by_user[story.user_id] = []
        stories_by_user[story.user_id].append(story.to_dict(user_id=current_user_id))
    
    return success_response({
        'stories_by_user': stories_by_user,
        'total_active_stories': len(active_stories)
    })

@stories_bp.route('/<int:story_id>', methods=['DELETE'])
def delete_story(story_id):
    """Delete story"""
    story = Story.query.get(story_id)
    if not story:
        return error_response('Story not found', 404)
    
    try:
        db.session.delete(story)
        db.session.commit()
        return success_response(message='Story deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete story: {str(e)}', 500)