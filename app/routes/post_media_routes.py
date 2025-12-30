from flask import Blueprint, request, jsonify
from app.models.postMedia import PostMedia
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

post_media_bp = Blueprint('post_media', __name__)

@post_media_bp.route('', methods=['GET'])
def get_post_media():
    """Get all post media with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    post_id = request.args.get('post_id', type=int)
    media_type = request.args.get('media_type', type=str)
    
    query = PostMedia.query
    
    if post_id:
        query = query.filter(PostMedia.post_id == post_id)
    if media_type:
        if media_type == 'image':
            query = query.filter(PostMedia.content_type.startswith('image/'))
        elif media_type == 'video':
            query = query.filter(PostMedia.content_type.startswith('video/'))
        elif media_type == 'document':
            query = query.filter(
                PostMedia.content_type.startswith('application/') |
                PostMedia.content_type.in_(['text/plain', 'text/html'])
            )
    
    result = paginate(query.order_by(PostMedia.created_at.desc()), page, per_page)
    
    return success_response({
        'media': [media.to_dict() for media in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@post_media_bp.route('/<int:media_id>', methods=['GET'])
def get_post_media_item(media_id):
    """Get single post media by ID"""
    media = PostMedia.query.get(media_id)
    if not media:
        return error_response('Post media not found', 404)
    
    return success_response({'media': media.to_dict()})

@post_media_bp.route('', methods=['POST'])
def create_post_media():
    """Create new post media"""
    # This would typically handle file uploads
    data = request.get_json()
    
    required_fields = ['post_id', 'file_name', 'content_type', 'file_size']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields')
    
    try:
        media = PostMedia(
            post_id=data['post_id'],
            file_name=data['file_name'],
            content_type=data['content_type'],
            file_size=data['file_size'],
            caption=data.get('caption')
            # data field would be set from file upload
        )
        
        db.session.add(media)
        db.session.commit()
        
        return success_response({
            'media': media.to_dict()
        }, 'Media created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create media: {str(e)}', 500)

@post_media_bp.route('/<int:media_id>/caption', methods=['PUT'])
def update_media_caption(media_id):
    """Update media caption"""
    media = PostMedia.query.get(media_id)
    if not media:
        return error_response('Post media not found', 404)
    
    data = request.get_json()
    caption = data.get('caption')
    
    try:
        media.update_caption(caption)
        return success_response({
            'media': media.to_dict()
        }, 'Caption updated successfully')
    except Exception as e:
        return error_response(f'Failed to update caption: {str(e)}', 500)

@post_media_bp.route('/<int:media_id>', methods=['DELETE'])
def delete_post_media(media_id):
    """Delete post media"""
    media = PostMedia.query.get(media_id)
    if not media:
        return error_response('Post media not found', 404)
    
    try:
        db.session.delete(media)
        db.session.commit()
        return success_response(message='Media deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete media: {str(e)}', 500)