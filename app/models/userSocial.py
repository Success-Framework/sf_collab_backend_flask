from datetime import datetime
from sqlalchemy import Enum, JSON
from app.extensions import db
from app.models.Enums import Privacy

class UserSocial(db.Model):
  __tablename__ = 'user_social'
  
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False, index=True)
  
  # Follower System
  followers_count = db.Column(db.Integer, default=0)
  following_count = db.Column(db.Integer, default=0)
  follower_ids = db.Column(JSON, default=[])  # Array of user IDs
  following_ids = db.Column(JSON, default=[])  # Array of user IDs
  
  # Engagement Metrics
  total_likes_given = db.Column(db.Integer, default=0)
  total_likes_received = db.Column(db.Integer, default=0)
  total_shares = db.Column(db.Integer, default=0)
  total_views = db.Column(db.Integer, default=0)
  
  # Saved/Bookmarked Content
  saved_post_ids = db.Column(JSON, default=[])  # Array of post IDs
  saved_idea_ids = db.Column(JSON, default=[])  # Array of idea IDs
  saved_startup_ids = db.Column(JSON, default=[])  # Array of startup IDs
  
  # Liked Content
  liked_post_ids = db.Column(JSON, default=[])  # Array of post IDs
  liked_idea_ids = db.Column(JSON, default=[])  # Array of idea IDs
  liked_startup_ids = db.Column(JSON, default=[])  # Array of startup IDs
  liked_comment_ids = db.Column(JSON, default=[])  # Array of comment IDs
  
  # Stories
  stories_count = db.Column(db.Integer, default=0)
  archived_story_ids = db.Column(JSON, default=[])  # Array of archived story IDs
  story_highlights = db.Column(JSON, default={})  # Dict: {highlight_name: [story_ids]}
  
  # Posts
  posts_count = db.Column(db.Integer, default=0)
  pinned_post_ids = db.Column(JSON, default=[])  # Array of pinned post IDs
  
  # Auto-Suggestions Preferences
  pref_suggested_accounts = db.Column(db.Boolean, default=True)
  pref_suggested_content = db.Column(db.Boolean, default=True)
  pref_suggested_hashtags = db.Column(db.Boolean, default=True)
  
  # Content Preferences for Suggestions (interests/tags)
  interest_tags = db.Column(JSON, default=[])  # Array: ["tech", "startups", "finance"]
  preferred_content_types = db.Column(JSON, default=[])  # Array: ["posts", "stories", "ideas"]
  blocked_keywords = db.Column(JSON, default=[])  # Array of keywords to exclude from suggestions
  
  # Matching & Discovery
  match_preferences = db.Column(JSON, default={})  # Dict for matching algorithm
  # Example: {'skills': ['python', 'ui/ux'], 'industry': 'tech', 'location': 'US', 'looking_for': ['co-founder', 'investor']}
  
  # Block & Mute
  blocked_user_ids = db.Column(JSON, default=[])  # Array of user IDs
  muted_user_ids = db.Column(JSON, default=[])  # Array of user IDs (still follow but don't see content)
  
  # Privacy Settings
  profile_visibility = db.Column(Enum(Privacy), default=Privacy.public)
  allow_messages_from = db.Column(db.String(50), default='everyone')  # everyone, followers, nobody
  allow_collaboration_requests = db.Column(db.Boolean, default=True)
  
  # Social Stats
  engagement_rate = db.Column(db.Float, default=0.0)  # Calculated metric
  reputation_score = db.Column(db.Float, default=0.0)  # Overall social score
  
  # Timestamps
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  
  # ========== RELATIONSHIPS ==========
  
  user = db.relationship('User', backref='social_profile', foreign_keys=[user_id])
  
  followers = db.relationship(
    'User',
    secondary='user_followers',
    primaryjoin='UserSocial.user_id == user_followers.c.following_id',
    secondaryjoin='user_followers.c.follower_id == User.id',
    backref='followed_by',
    lazy='dynamic'
  )
  
  following = db.relationship(
    'User',
    secondary='user_followers',
    primaryjoin='UserSocial.user_id == user_followers.c.follower_id',
    secondaryjoin='user_followers.c.following_id == User.id',
    backref='followers_of',
    lazy='dynamic'
  )
  
  # ========== HELPER FUNCTIONS ==========
  
  def add_follower(self, follower_user_id: int):
    """Add a follower"""
    if follower_user_id not in self.follower_ids:
      self.follower_ids.append(follower_user_id)
      self.followers_count += 1
      db.session.commit()
  
  def remove_follower(self, follower_user_id: int):
    """Remove a follower"""
    if follower_user_id in self.follower_ids:
      self.follower_ids.remove(follower_user_id)
      self.followers_count = max(0, self.followers_count - 1)
      db.session.commit()
  
  def follow_user(self, user_to_follow_id: int):
    """Follow a user"""
    if user_to_follow_id not in self.following_ids:
      self.following_ids.append(user_to_follow_id)
      self.following_count += 1
      db.session.commit()
  
  def unfollow_user(self, user_to_unfollow_id: int):
    """Unfollow a user"""
    if user_to_unfollow_id in self.following_ids:
      self.following_ids.remove(user_to_unfollow_id)
      self.following_count = max(0, self.following_count - 1)
      db.session.commit()
  
  def is_following(self, user_id: int) -> bool:
    """Check if user is following another user"""
    return user_id in self.following_ids
  
  def is_follower(self, user_id: int) -> bool:
    """Check if user is a follower"""
    return user_id in self.follower_ids
  
  def save_post(self, post_id: int):
    """Save a post"""
    if post_id not in self.saved_post_ids:
      self.saved_post_ids.append(post_id)
      db.session.commit()
  
  def unsave_post(self, post_id: int):
    """Unsave a post"""
    if post_id in self.saved_post_ids:
      self.saved_post_ids.remove(post_id)
      db.session.commit()
  
  def like_post(self, post_id: int):
    """Like a post"""
    if post_id not in self.liked_post_ids:
      self.liked_post_ids.append(post_id)
      self.total_likes_given += 1
      db.session.commit()
  
  def unlike_post(self, post_id: int):
    """Unlike a post"""
    if post_id in self.liked_post_ids:
      self.liked_post_ids.remove(post_id)
      self.total_likes_given = max(0, self.total_likes_given - 1)
      db.session.commit()
  
  def block_user(self, user_id: int):
    """Block a user"""
    if user_id not in self.blocked_user_ids:
      self.blocked_user_ids.append(user_id)
      db.session.commit()
  
  def unblock_user(self, user_id: int):
    """Unblock a user"""
    if user_id in self.blocked_user_ids:
      self.blocked_user_ids.remove(user_id)
      db.session.commit()
  
  def is_blocked(self, user_id: int) -> bool:
    """Check if user is blocked"""
    return user_id in self.blocked_user_ids
  
  def mute_user(self, user_id: int):
    """Mute a user"""
    if user_id not in self.muted_user_ids:
      self.muted_user_ids.append(user_id)
      db.session.commit()
  
  def unmute_user(self, user_id: int):
    """Unmute a user"""
    if user_id in self.muted_user_ids:
      self.muted_user_ids.remove(user_id)
      db.session.commit()
  
  def is_muted(self, user_id: int) -> bool:
    """Check if user is muted"""
    return user_id in self.muted_user_ids
  
  def add_story_highlight(self, highlight_name: str, story_ids: list):
    """Add a story highlight collection"""
    self.story_highlights[highlight_name] = story_ids
    db.session.commit()
  
  def update_match_preferences(self, preferences: dict):
    """Update matching preferences for discovery"""
    self.match_preferences = preferences
    db.session.commit()
  
  def update_interest_tags(self, tags: list):
    """Update interest tags for content suggestions"""
    self.interest_tags = tags
    db.session.commit()
  
  def calculate_engagement_rate(self) -> float:
    """Calculate engagement rate"""
    if self.posts_count == 0:
      return 0.0
    engagement = (self.total_likes_received + self.total_shares + self.total_views) / (self.posts_count * 100)
    self.engagement_rate = min(engagement, 100.0)
    db.session.commit()
    return self.engagement_rate
  
  def to_dict(self):
    return {
      'id': self.id,
      'userId': self.user_id,
      'followersCount': self.followers_count,
      'followingCount': self.following_count,
      'followerIds': self.follower_ids,
      'followingIds': self.following_ids,
      'totalLikesGiven': self.total_likes_given,
      'totalLikesReceived': self.total_likes_received,
      'totalShares': self.total_shares,
      'totalViews': self.total_views,
      'savedPostIds': self.saved_post_ids,
      'savedIdeaIds': self.saved_idea_ids,
      'savedStartupIds': self.saved_startup_ids,
      'likedPostIds': self.liked_post_ids,
      'likedIdeaIds': self.liked_idea_ids,
      'likedStartupIds': self.liked_startup_ids,
      'likedCommentIds': self.liked_comment_ids,
      'storiesCount': self.stories_count,
      'archivedStoryIds': self.archived_story_ids,
      'storyHighlights': self.story_highlights,
      'postsCount': self.posts_count,
      'pinnedPostIds': self.pinned_post_ids,
      'preferences': {
        'suggestedAccounts': self.pref_suggested_accounts,
        'suggestedContent': self.pref_suggested_content,
        'suggestedHashtags': self.pref_suggested_hashtags
      },
      'interestTags': self.interest_tags,
      'preferredContentTypes': self.preferred_content_types,
      'blockedKeywords': self.blocked_keywords,
      'matchPreferences': self.match_preferences,
      'blockedUserIds': self.blocked_user_ids,
      'mutedUserIds': self.muted_user_ids,
      'profileVisibility': self.profile_visibility.value,
      'allowMessagesFrom': self.allow_messages_from,
      'allowCollaborationRequests': self.allow_collaboration_requests,
      'engagementRate': self.engagement_rate,
      'reputationScore': self.reputation_score,
      'createdAt': self.created_at.isoformat(),
      'updatedAt': self.updated_at.isoformat()
    }


# Association table for followers
class UserFollowers(db.Model):
  __tablename__ = 'user_followers'
  
  follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
  following_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
  followed_at = db.Column(db.DateTime, default=datetime.utcnow)