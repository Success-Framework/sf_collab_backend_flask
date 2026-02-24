from datetime import datetime
from app.extensions import db

class IdeaComment(db.Model):
    __tablename__ = 'idea_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author_first_name = db.Column(db.String(100))
    author_last_name = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    suggestion = db.Column(db.Boolean, default=False)
    #! Relationships
    comment_author = db.relationship('User', back_populates='idea_comments', foreign_keys=[author_id])
    parent_idea = db.relationship('Idea', back_populates='idea_comments', foreign_keys=[idea_id])
    idea_comment_likes = db.relationship('IdeaCommentLike', back_populates='liked_comment', lazy='dynamic', cascade='all, delete-orphan')
    #! HELPER FUNCTIONS
    
    def update_content(self, new_content):
        """Update comment content"""
        self.content = new_content
        db.session.commit()
    def toggle_like(self, user_id):
        """Like or unlike the comment"""
        existing_like = IdeaCommentLike.query.filter_by(user_id=user_id, comment_id=self.id).first()
        if existing_like:
            db.session.delete(existing_like)
        else:
            new_like = IdeaCommentLike(user_id=user_id, comment_id=self.id)
            db.session.add(new_like)
        db.session.commit()

    def get_author_name(self):
        """Get author's full name"""
        return f"{self.author_first_name} {self.author_last_name}"
    
    def to_dict(self, user_id=None):
        user_liked = False
        if user_id:
            print(f"Checking if user {user_id} liked comment {self.id}")
            user_liked = self.idea_comment_likes.filter_by(user_id=user_id).first() is not None
        return {
            'id': self.id,
            'ideaId': self.idea_id,
            'content': self.content,
            'likes': self.idea_comment_likes.count(),
            'userLiked': user_liked,
            'author': {
                'id': self.author_id,
                'firstName': self.author_first_name,
                'lastName': self.author_last_name,
                'fullName': self.get_author_name()
            },
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
            'suggestion': self.suggestion
        }
        
class IdeaCommentLike(db.Model):
    __tablename__ = 'idea_comment_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('idea_comments.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    liker = db.relationship('User', back_populates='idea_comment_likes', foreign_keys=[user_id])
    liked_comment = db.relationship('IdeaComment', back_populates='idea_comment_likes', foreign_keys=[comment_id])
    
    def count(self):
        return IdeaCommentLike.query.filter_by(comment_id=self.comment_id).count()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'comment_id': self.comment_id,
            'created_at': self.created_at.isoformat(),
            'user': {
                'id': self.liker.id,
                'firstName': self.liker.first_name,
                'lastName': self.liker.last_name
            } if self.liker else None
        }