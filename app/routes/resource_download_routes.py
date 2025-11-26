from flask import Blueprint, request, jsonify
from app.models.ResourceDownload import ResourceDownload
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate
from datetime import datetime, timedelta

resource_downloads_bp = Blueprint('resource_downloads', __name__, url_prefix='/api/resource-downloads')

@resource_downloads_bp.route('', methods=['GET'])
def get_resource_downloads():
    """Get all resource downloads with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    resource_id = request.args.get('resource_id', type=int)
    user_id = request.args.get('user_id', type=int)
    recent_only = request.args.get('recent_only', 'false').lower() == 'true'
    
    query = ResourceDownload.query
    
    if resource_id:
        query = query.filter(ResourceDownload.resource_id == resource_id)
    if user_id:
        query = query.filter(ResourceDownload.user_id == user_id)
    if recent_only:
        from datetime import datetime, timedelta
        day_ago = datetime.utcnow() - timedelta(days=1)
        query = query.filter(ResourceDownload.downloaded_at >= day_ago)
    
    result = paginate(query.order_by(ResourceDownload.downloaded_at.desc()), page, per_page)
    
    return success_response({
        'downloads': [download.to_dict() for download in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@resource_downloads_bp.route('/<int:download_id>', methods=['GET'])
def get_resource_download(download_id):
    """Get single resource download by ID"""
    download = ResourceDownload.query.get(download_id)
    if not download:
        return error_response('Resource download not found', 404)
    
    return success_response({'download': download.to_dict()})

@resource_downloads_bp.route('', methods=['POST'])
def create_resource_download():
    """Create new resource download"""
    data = request.get_json()
    
    required_fields = ['resource_id', 'user_id']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: resource_id, user_id')
    
    # Check if download already exists (optional - you might want to allow multiple downloads)
    existing = ResourceDownload.query.filter_by(
        resource_id=data['resource_id'],
        user_id=data['user_id']
    ).first()
    
    if existing:
        # Update the existing download timestamp
        existing.downloaded_at = datetime.utcnow()
        db.session.commit()
        return success_response({
            'download': existing.to_dict()
        }, 'Download timestamp updated')
    
    try:
        download = ResourceDownload(
            resource_id=data['resource_id'],
            user_id=data['user_id']
        )
        
        db.session.add(download)
        
        # Increment resource download count
        from models.knowledge import Knowledge
        resource = Knowledge.query.get(data['resource_id'])
        if resource:
            resource.increment_downloads()
        
        db.session.commit()
        
        return success_response({
            'download': download.to_dict()
        }, 'Resource download recorded successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to record download: {str(e)}', 500)

@resource_downloads_bp.route('/resource/<int:resource_id>/count', methods=['GET'])
def get_resource_download_count(resource_id):
    """Get download count for a resource"""
    count = ResourceDownload.query.filter_by(resource_id=resource_id).count()
    
    return success_response({
        'resource_id': resource_id,
        'download_count': count
    })

@resource_downloads_bp.route('/user/<int:user_id>/resource/<int:resource_id>', methods=['GET'])
def check_user_downloaded_resource(user_id, resource_id):
    """Check if user has downloaded a resource"""
    download = ResourceDownload.query.filter_by(
        user_id=user_id,
        resource_id=resource_id
    ).first()
    
    return success_response({
        'has_downloaded': download is not None,
        'download': download.to_dict() if download else None
    })

@resource_downloads_bp.route('/<int:download_id>', methods=['DELETE'])
def delete_resource_download(download_id):
    """Delete resource download"""
    download = ResourceDownload.query.get(download_id)
    if not download:
        return error_response('Resource download not found', 404)
    
    try:
        # Decrement resource download count
        from models.knowledge import Knowledge
        resource = Knowledge.query.get(download.resource_id)
        if resource and resource.downloads > 0:
            resource.downloads -= 1
            db.session.commit()
        
        db.session.delete(download)
        db.session.commit()
        
        return success_response(message='Download record deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete download record: {str(e)}', 500)