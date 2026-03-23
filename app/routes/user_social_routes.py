from flask import Blueprint, request, jsonify
from app.models.userSocial import UserSocial, UserFollowers
from app.models.user import User
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate
from flask_jwt_extended import jwt_required, get_jwt_identity
from operator import or_

user_social_bp = Blueprint('user_social', __name__)

# ============= FOLLOWER ROUTES =============

@user_social_bp.route('/<int:user_id>/follow', methods=['POST'])
@jwt_required()
def follow_user(user_id):
  """Follow a user"""
  current_user_id = get_jwt_identity()
  
  if current_user_id == user_id:
    return error_response('Cannot follow yourself', 400)
  
  target_user = User.query.get(user_id)
  if not target_user:
    return error_response('User not found', 404)
  
  try:
    current_social = UserSocial.query.filter_by(user_id=current_user_id).first()
    target_social = UserSocial.query.filter_by(user_id=user_id).first()
    
    if not current_social or not target_social:
      return error_response('Social profile not found', 404)
    
    current_social.follow_user(user_id)
    target_social.add_follower(current_user_id)
    
    return success_response({'following': True}, 'User followed successfully')
  except Exception as e:
    db.session.rollback()
    return error_response(f'Failed to follow user: {str(e)}', 500)

@user_social_bp.route('/<int:user_id>/unfollow', methods=['POST'])
@jwt_required()
def unfollow_user(user_id):
  """Unfollow a user"""
  current_user_id = get_jwt_identity()
  
  try:
    current_social = UserSocial.query.filter_by(user_id=current_user_id).first()
    target_social = UserSocial.query.filter_by(user_id=user_id).first()
    
    if not current_social or not target_social:
      return error_response('Social profile not found', 404)
    
    current_social.unfollow_user(user_id)
    target_social.remove_follower(current_user_id)
    
    return success_response({'following': False}, 'User unfollowed successfully')
  except Exception as e:
    db.session.rollback()
    return error_response(f'Failed to unfollow user: {str(e)}', 500)

@user_social_bp.route('/<int:user_id>/followers', methods=['GET'])
@jwt_required()
def get_followers(user_id):
  """Get user's followers with pagination"""
  page = request.args.get('page', 1, type=int)
  per_page = request.args.get('per_page', 10, type=int)
  
  social = UserSocial.query.filter_by(user_id=user_id).first()
  if not social:
    return error_response('Social profile not found', 404)
  
  followers_query = User.query.filter(User.id.in_(social.follower_ids or []))
  result = paginate(followers_query, page, per_page)
  
  return success_response({
    'followers': [user.to_dict() for user in result['items']],
    'pagination': {
      'page': result['page'],
      'per_page': result['per_page'],
      'total': result['total'],
      'pages': result['pages']
    }
  })

@user_social_bp.route('/<int:user_id>/following', methods=['GET'])
@jwt_required()
def get_following(user_id):
  """Get users that a user is following with pagination"""
  page = request.args.get('page', 1, type=int)
  per_page = request.args.get('per_page', 10, type=int)
  
  social = UserSocial.query.filter_by(user_id=user_id).first()
  if not social:
    return error_response('Social profile not found', 404)
  
  following_query = User.query.filter(User.id.in_(social.following_ids or []))
  result = paginate(following_query, page, per_page)
  
  return success_response({
    'following': [user.to_dict() for user in result['items']],
    'pagination': {
      'page': result['page'],
      'per_page': result['per_page'],
      'total': result['total'],
      'pages': result['pages']
    }
  })

# ============= ENGAGEMENT ROUTES =============

@user_social_bp.route('/<int:user_id>/like-post', methods=['POST'])
@jwt_required()
def like_post(user_id):
  """Like a post"""
  data = request.get_json()
  post_id = data.get('post_id')
  
  if not post_id:
    return error_response('post_id is required', 400)
  
  try:
    social = UserSocial.query.filter_by(user_id=user_id).first()
    if not social:
      return error_response('Social profile not found', 404)
    
    social.like_post(post_id)
    return success_response({'liked': True}, 'Post liked successfully')
  except Exception as e:
    db.session.rollback()
    return error_response(f'Failed to like post: {str(e)}', 500)

@user_social_bp.route('/<int:user_id>/unlike-post', methods=['POST'])
@jwt_required()
def unlike_post(user_id):
  """Unlike a post"""
  data = request.get_json()
  post_id = data.get('post_id')
  
  if not post_id:
    return error_response('post_id is required', 400)
  
  try:
    social = UserSocial.query.filter_by(user_id=user_id).first()
    if not social:
      return error_response('Social profile not found', 404)
    
    social.unlike_post(post_id)
    return success_response({'liked': False}, 'Post unliked successfully')
  except Exception as e:
    db.session.rollback()
    return error_response(f'Failed to unlike post: {str(e)}', 500)

# ============= SAVE/BOOKMARK ROUTES =============

@user_social_bp.route('/<int:user_id>/save-post', methods=['POST'])
@jwt_required()
def save_post(user_id):
  """Save a post"""
  data = request.get_json()
  post_id = data.get('post_id')
  
  if not post_id:
    return error_response('post_id is required', 400)
  
  try:
    social = UserSocial.query.filter_by(user_id=user_id).first()
    if not social:
      return error_response('Social profile not found', 404)
    
    social.save_post(post_id)
    return success_response({'saved': True}, 'Post saved successfully')
  except Exception as e:
    db.session.rollback()
    return error_response(f'Failed to save post: {str(e)}', 500)

@user_social_bp.route('/<int:user_id>/unsave-post', methods=['POST'])
@jwt_required()
def unsave_post(user_id):
  """Unsave a post"""
  data = request.get_json()
  post_id = data.get('post_id')
  
  if not post_id:
    return error_response('post_id is required', 400)
  
  try:
    social = UserSocial.query.filter_by(user_id=user_id).first()
    if not social:
      return error_response('Social profile not found', 404)
    
    social.unsave_post(post_id)
    return success_response({'saved': False}, 'Post unsaved successfully')
  except Exception as e:
    db.session.rollback()
    return error_response(f'Failed to unsave post: {str(e)}', 500)

# ============= BLOCK/MUTE ROUTES =============

@user_social_bp.route('/<int:user_id>/block/<int:blocked_user_id>', methods=['POST'])
@jwt_required()
def block_user(user_id, blocked_user_id):
  """Block a user"""
  current_user_id = get_jwt_identity()
  
  if int(user_id) != int(current_user_id):
    return error_response('Unauthorized', 403)
  
  if user_id == blocked_user_id:
    return error_response('Cannot block yourself', 400)
  
  try:
    social = UserSocial.query.filter_by(user_id=user_id).first()
    if not social:
      return error_response('Social profile not found', 404)
    
    social.block_user(blocked_user_id)
    return success_response({'blocked': True}, 'User blocked successfully')
  except Exception as e:
    db.session.rollback()
    return error_response(f'Failed to block user: {str(e)}', 500)

@user_social_bp.route('/<int:user_id>/unblock/<int:blocked_user_id>', methods=['POST'])
@jwt_required()
def unblock_user(user_id, blocked_user_id):
  """Unblock a user"""
  current_user_id = get_jwt_identity()
  
  if int(user_id) != int(current_user_id):
    return error_response('Unauthorized', 403)
  
  try:
    social = UserSocial.query.filter_by(user_id=user_id).first()
    if not social:
      return error_response('Social profile not found', 404)
    
    social.unblock_user(blocked_user_id)
    return success_response({'blocked': False}, 'User unblocked successfully')
  except Exception as e:
    db.session.rollback()
    return error_response(f'Failed to unblock user: {str(e)}', 500)

@user_social_bp.route('/<int:user_id>/mute/<int:muted_user_id>', methods=['POST'])
@jwt_required()
def mute_user(user_id, muted_user_id):
  """Mute a user"""
  current_user_id = get_jwt_identity()
  
  if int(user_id) != int(current_user_id):
    return error_response('Unauthorized', 403)
  
  try:
    social = UserSocial.query.filter_by(user_id=user_id).first()
    if not social:
      return error_response('Social profile not found', 404)
    
    social.mute_user(muted_user_id)
    return success_response({'muted': True}, 'User muted successfully')
  except Exception as e:
    db.session.rollback()
    return error_response(f'Failed to mute user: {str(e)}', 500)

@user_social_bp.route('/<int:user_id>/unmute/<int:muted_user_id>', methods=['POST'])
@jwt_required()
def unmute_user(user_id, muted_user_id):
  """Unmute a user"""
  current_user_id = get_jwt_identity()
  
  if int(user_id) != int(current_user_id):
    return error_response('Unauthorized', 403)
  
  try:
    social = UserSocial.query.filter_by(user_id=user_id).first()
    if not social:
      return error_response('Social profile not found', 404)
    
    social.unmute_user(muted_user_id)
    return success_response({'muted': False}, 'User unmuted successfully')
  except Exception as e:
    db.session.rollback()
    return error_response(f'Failed to unmute user: {str(e)}', 500)

# ============= PREFERENCES & SETTINGS ROUTES =============

@user_social_bp.route('/<int:user_id>/preferences', methods=['PUT'])
@jwt_required()
def update_preferences(user_id):
  """Update suggestion preferences"""
  current_user_id = get_jwt_identity()
  
  if int(user_id) != int(current_user_id):
    return error_response('Unauthorized', 403)
  
  data = request.get_json()
  
  try:
    social = UserSocial.query.filter_by(user_id=user_id).first()
    if not social:
      return error_response('Social profile not found', 404)
    
    if 'suggestedAccounts' in data:
      social.pref_suggested_accounts = data['suggestedAccounts']
    if 'suggestedContent' in data:
      social.pref_suggested_content = data['suggestedContent']
    if 'suggestedHashtags' in data:
      social.pref_suggested_hashtags = data['suggestedHashtags']
    
    db.session.commit()
    return success_response({'social': social.to_dict()}, 'Preferences updated successfully')
  except Exception as e:
    db.session.rollback()
    return error_response(f'Failed to update preferences: {str(e)}', 500)

@user_social_bp.route('/<int:user_id>/interest-tags', methods=['PUT'])
@jwt_required()
def update_interest_tags(user_id):
  """Update interest tags"""
  current_user_id = get_jwt_identity()
  
  if int(user_id) != int(current_user_id):
    return error_response('Unauthorized', 403)
  
  data = request.get_json()
  tags = data.get('tags', [])
  
  if not isinstance(tags, list):
    return error_response('tags must be an array', 400)
  
  try:
    social = UserSocial.query.filter_by(user_id=user_id).first()
    if not social:
      return error_response('Social profile not found', 404)
    
    social.update_interest_tags(tags)
    return success_response({'social': social.to_dict()}, 'Interest tags updated successfully')
  except Exception as e:
    db.session.rollback()
    return error_response(f'Failed to update interest tags: {str(e)}', 500)

@user_social_bp.route('/<int:user_id>/match-preferences', methods=['PUT'])
@jwt_required()
def update_match_preferences(user_id):
  """Update match preferences"""
  current_user_id = get_jwt_identity()
  
  if int(user_id) != int(current_user_id):
    return error_response('Unauthorized', 403)
  
  data = request.get_json()
  preferences = data.get('preferences', {})
  
  if not isinstance(preferences, dict):
    return error_response('preferences must be an object', 400)
  
  try:
    social = UserSocial.query.filter_by(user_id=user_id).first()
    if not social:
      return error_response('Social profile not found', 404)
    
    social.update_match_preferences(preferences)
    return success_response({'social': social.to_dict()}, 'Match preferences updated successfully')
  except Exception as e:
    db.session.rollback()
    return error_response(f'Failed to update match preferences: {str(e)}', 500)

@user_social_bp.route('/suggestions', methods=['GET'])
@jwt_required()
def get_user_suggestions():
  """Get user suggestions based on match preferences"""
  limit = request.args.get('limit', 5, type=int)
  current_user_id = get_jwt_identity()
  
  if not current_user_id:
    return error_response('User not found', 404)
  
  try:
    social = UserSocial.query.filter_by(user_id=current_user_id).first()
    if not social:
      return error_response('Social profile not found', 404)
    
    if not social.pref_suggested_accounts:
      return success_response({'suggestions': []}, 'No suggestions available')

    exclude_ids = set(social.following_ids or []).union(social.blocked_ids or []).union([current_user_id])
    users = User.query.filter(~User.id.in_(exclude_ids)).all()

    preferences = social.match_preferences or {}
    filters = []

    if 'location' in preferences:
      filters.append(User.profile_city == preferences['location'] or User.profile_country == preferences['location'])
    if 'looking_for' in preferences:
      filters.append(User.role.in_(preferences['looking_for']))
    # Add more filters based on other preferences as needed - e.g. industry, skills, etc.
    
    if filters:
      users = users.filter(or_(*filters))
      
    candidates = users.limit(200).all()

    scored_users = []
    for candidate in candidates:
      score = 0
      if 'location' in preferences and (candidate.profile_city == preferences['location'] or candidate.profile_country == preferences['location']):
        score += 10
      if 'looking_for' in preferences and candidate.role in preferences.get('looking_for', []):
        score += 5
      if score > 0:
        scored_users.append((candidate, score))

    sorted_users = sorted(scored_users, key=lambda x: x[1], reverse=True)
    top_users = [user.to_dict() for user, _ in sorted_users[:limit]]
    # Add additional users if we don't have enough suggestions based on preferences
    if len (top_users) < limit:
      additional_needed = limit - len(top_users)
      additional_users = users.filter(~User.id.in_([u['id'] for u in top_users])).order_by(User.created_at.desc()).limit(additional_needed).all()
      
    top_users.extend([user.to_dict() for user in additional_users])
    return success_response({'suggestions': top_users}, 'Suggestions retrieved successfully')
  except Exception as e:
    return error_response(f'Failed to get user suggestions based on match preferences: {str(e)}', 500)


# ============= SOCIAL PROFILE ROUTES =============

@user_social_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_social_profile(user_id):
  """Get user's social profile"""
  social = UserSocial.query.filter_by(user_id=user_id).first()
  if not social:
    return error_response('Social profile not found', 404)
  
  return success_response({'social': social.to_dict()})

@user_social_bp.route('/<int:user_id>', methods=['POST'])
@jwt_required()
def create_social_profile(user_id):
  """Create user's social profile"""
  print("Creating social profile for user_id:", user_id)

  user_social = UserSocial(
    user_id=user_id
    )
  try:
    db.session.add(user_social)
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    return error_response(f'Failed to create social profile: {str(e)}', 500)
  
  return success_response({'social': user_social.to_dict()})

@user_social_bp.route('/<int:user_id>/privacy', methods=['PUT'])
@jwt_required()
def update_privacy_settings(user_id):
  """Update privacy settings"""
  current_user_id = get_jwt_identity()
  
  if int(user_id) != int(current_user_id):
    return error_response('Unauthorized', 403)
  
  data = request.get_json()
  
  try:
    social = UserSocial.query.filter_by(user_id=user_id).first()
    if not social:
      return error_response('Social profile not found', 404)
    
    if 'profileVisibility' in data:
      social.profile_visibility = data['profileVisibility']
    if 'allowMessagesFrom' in data:
      social.allow_messages_from = data['allowMessagesFrom']
    if 'allowCollaborationRequests' in data:
      social.allow_collaboration_requests = data['allowCollaborationRequests']
    
    db.session.commit()
    return success_response({'social': social.to_dict()}, 'Privacy settings updated successfully')
  except Exception as e:
    db.session.rollback()
    return error_response(f'Failed to update privacy settings: {str(e)}', 500)

@user_social_bp.route('/<int:user_id>/engagement-rate', methods=['GET'])
@jwt_required()
def get_engagement_rate(user_id):
  """Calculate and get engagement rate"""
  social = UserSocial.query.filter_by(user_id=user_id).first()
  if not social:
    return error_response('Social profile not found', 404)
  
  engagement_rate = social.calculate_engagement_rate()
  return success_response({'engagementRate': engagement_rate})
