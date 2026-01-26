from flask import Blueprint, request, jsonify
from app.models.startupBookmark import StartupBookmark
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate
from flask_jwt_extended import jwt_required
from app.models.startup import Startup
bookmarks_bp = Blueprint('startup_bookmarks', __name__)

@bookmarks_bp.route('', methods=['GET'])
def get_bookmarks():
    """Get all bookmarks with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    user_id = request.args.get('user_id', type=int)
    
    query = StartupBookmark.query
    
    if user_id:
        query = query.filter(StartupBookmark.user_id == user_id)
    
    result = paginate(query, page, per_page)
    
    return success_response({
        'bookmarks': [bookmark.to_dict() for bookmark in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })
@bookmarks_bp.route('/startups', methods=['GET'])
@jwt_required()
def get_bookmarked_startups():
    """Get all bookmarked startups for a user"""
    user_id = request.args.get('user_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    industry = request.args.get('industry', type=str)
    stage = request.args.get('stage', type=str)
    search = request.args.get('search', type=str)
    if not user_id:
        return error_response('user_id is required', 400)

    query = StartupBookmark.query.filter(StartupBookmark.user_id == user_id)
    if search:
        query = query.filter(
            StartupBookmark.startup.has(
                (Startup.name.ilike(f"%{search}%")) |
                (Startup.description.ilike(f"%{search}%"))
            )
        )
    print("Search:", search)
    print("Query:", query)
    if industry:
        query = query.filter(StartupBookmark.startup.has(industry=industry))
    if stage:
        query = query.filter(StartupBookmark.startup.has(stage=stage))
    result = paginate(query, page, per_page)

    startups = [bookmark.startup.to_dict() for bookmark in result['items']]

    return success_response({
        'startups': startups,
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@bookmarks_bp.route('/<int:bookmark_id>', methods=['GET'])
def get_bookmark(bookmark_id):
    """Get single bookmark by ID"""
    bookmark = StartupBookmark.query.get(bookmark_id)
    if not bookmark:
        return error_response('Bookmark not found', 404)
    
    return success_response({'bookmark': bookmark.to_dict()})
@bookmarks_bp.route('/user/<int:user_id>/startup/<int:startup_id>', methods=['GET'])
def get_bookmark_by_user_startup(user_id, startup_id):
    """Get bookmark by user ID and startup ID"""
    bookmark = StartupBookmark.query.filter_by(user_id=user_id, startup_id=startup_id).first()
    if not bookmark:
        return error_response('Bookmark not found', 404)
    
    return success_response({'bookmark': bookmark.to_dict()})

@bookmarks_bp.route('/toggle', methods=['POST'])
@jwt_required()
def toggle_bookmark():
    data = request.get_json()

    user_id = data.get('user_id')
    startup_id = data.get('startup_id')

    if not user_id or not startup_id:
        return error_response('user_id and startup_id are required', 400)

    bookmark = StartupBookmark.query.filter_by(
        user_id=user_id,
        startup_id=startup_id
    ).first()

    try:
        if bookmark:
            db.session.delete(bookmark)
            db.session.commit()
            return success_response(
                {'bookmarked': False},
                'Bookmark removed'
            )
        else:
            bookmark = StartupBookmark(
                user_id=user_id,
                startup_id=startup_id
            )
            db.session.add(bookmark)
            db.session.commit()
            return success_response(
                {'bookmarked': True},
                'Bookmark added'
            )
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to toggle bookmark: {str(e)}', 500)


@bookmarks_bp.route('/status', methods=['GET'])
def bookmark_status():
    user_id = request.args.get('user_id', type=int)
    startup_id = request.args.get('startup_id', type=int)

    if not user_id or not startup_id:
        return error_response('user_id and startup_id are required', 400)

    exists = StartupBookmark.query.filter_by(
        user_id=user_id,
        startup_id=startup_id
    ).first() is not None

    return success_response({'bookmarked': exists})
