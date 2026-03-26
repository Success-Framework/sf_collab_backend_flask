from datetime import datetime
from app.extensions import db
from sqlalchemy import Enum, JSON
from .Enums import ResourceStatus, Privacy
from .ideaComment import IdeaComment
from app.models.teamMember import TeamMember

# ─────────────────────────────────────────────────────────────
# VISION STATES (per product doc)
# draft → public → team_forming → ready_for_activation → archived
# ─────────────────────────────────────────────────────────────
VISION_STATES = [
    'draft',
    'public',
    'team_forming',
    'ready_for_activation',
    'archived'
]

class Idea(db.Model):
    __tablename__ = 'ideas'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    project_details = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    industry = db.Column(db.String(100), nullable=False)
    stage = db.Column(db.String(100), nullable=False)
    tags = db.Column(JSON, default=[])
    privacy = db.Column(Enum(Privacy), default=Privacy.public)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    creator_first_name = db.Column(db.String(100))
    creator_last_name = db.Column(db.String(100))
    
    status = db.Column(Enum(ResourceStatus), default=ResourceStatus.active)
    likes = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)

    # ── Week 1: Vision System fields ──────────────────────────
    # Vision lifecycle state
    vision_state = db.Column(db.String(50), default='public')

    # Readiness score (0–100), computed by compute_readiness_score()
    readiness_score = db.Column(db.Float, default=0.0)

    # Breakdown of what contributes to readiness (stored for display)
    readiness_breakdown = db.Column(JSON, default=dict)

    # Structured fields from the vision system spec
    problem_statement = db.Column(db.Text, nullable=True)
    outcome_goal = db.Column(db.Text, nullable=True)
    risk_level = db.Column(db.String(20), default='medium')  # low, medium, high

    # Roles the vision needs (list of strings e.g. ["backend_engineer", "designer"])
    required_roles = db.Column(JSON, default=list)

    # High-level roadmap items (public-facing summary, not sensitive details)
    roadmap_items = db.Column(JSON, default=list)
    # ── End Vision System fields ───────────────────────────────
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    #! Relationships
    idea_creator = db.relationship(
        'User',
        back_populates='ideas',
        foreign_keys=[creator_id]
    )

    team_members = db.relationship('TeamMember', 
        back_populates='parent_idea', 
        lazy='dynamic', 
        cascade='all, delete-orphan',
        foreign_keys='TeamMember.idea_id')
    
    idea_comments = db.relationship('IdeaComment', 
        back_populates='parent_idea', 
        lazy='dynamic', 
        cascade='all, delete-orphan',
        foreign_keys='IdeaComment.idea_id')
    
    suggestions = db.relationship('Suggestion', 
        back_populates='parent_idea', 
        lazy='dynamic', 
        cascade='all, delete-orphan',
        foreign_keys='Suggestion.idea_id')
    
    idea_bookmarks = db.relationship('IdeaBookmark',
        back_populates='bookmarked_idea',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='IdeaBookmark.idea_id')

    idea_likes = db.relationship('IdeaLike',
        back_populates='liked_idea',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='IdeaLike.idea_id')

    # ── HELPER FUNCTIONS ──────────────────────────────────────

    def increment_views(self):
        self.views += 1
        db.session.commit()
    
    def increment_likes(self):
        self.likes += 1
        db.session.commit()
    
    def decrement_likes(self):
        if self.likes > 0:
            self.likes -= 1
        db.session.commit()
    
    def add_team_member(self, name, position, skills=None):
        member = TeamMember(
            idea_id=self.id,
            name=name,
            position=position,
            skills=skills or {}
        )
        db.session.add(member)
        db.session.commit()
        return member
    
    def add_tag(self, tag):
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
        db.session.commit()
    
    def remove_tag(self, tag):
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
        db.session.commit()
    
    def update_stage(self, new_stage):
        self.stage = new_stage
        db.session.commit()
    
    def get_comments_count(self):
        return self.idea_comments.count()
    
    def get_team_size(self):
        return self.team_members.count()

    def save_image(self, image_url):
        self.image_url = image_url
        db.session.commit()

    # ── Week 1: Vision State Machine ──────────────────────────

    def set_vision_state(self, new_state: str):
        """Transition vision to a new state. Validates allowed transitions."""
        if new_state not in VISION_STATES:
            raise ValueError(f"Invalid vision state: {new_state}. Must be one of {VISION_STATES}")
        self.vision_state = new_state
        db.session.commit()

    # ── Week 1: Readiness Score Engine ────────────────────────

    def compute_readiness_score(self) -> float:
        """
        Compute and persist a 0–100 readiness score for this vision.

        Scoring breakdown (total 100 points):
          - Roadmap defined           →  20 pts  (roadmap_items has ≥1 items)
          - Problem statement filled  →  15 pts
          - Outcome goal filled       →  15 pts
          - Required roles defined    →  10 pts
          - Has collaborators         →  20 pts  (team_members ≥ 1, excl. creator)
          - Collaborator interest     →  10 pts  (collab requests pending/approved)
          - Activity / recency        →  10 pts  (updated_at within 14 days)

        The breakdown dict is stored on the model so the frontend can display
        "Needs: 1 backend developer, mentor review" etc.
        """
        breakdown = {
            'roadmap': 0,
            'problem_statement': 0,
            'outcome_goal': 0,
            'required_roles': 0,
            'collaborators': 0,
            'collaborator_interest': 0,
            'activity': 0,
        }

        # Roadmap (20)
        if self.roadmap_items and len(self.roadmap_items) >= 1:
            breakdown['roadmap'] = 20

        # Problem statement (15)
        if self.problem_statement and len(self.problem_statement.strip()) >= 20:
            breakdown['problem_statement'] = 15

        # Outcome goal (15)
        if self.outcome_goal and len(self.outcome_goal.strip()) >= 20:
            breakdown['outcome_goal'] = 15

        # Required roles defined (10)
        if self.required_roles and len(self.required_roles) >= 1:
            breakdown['required_roles'] = 10

        # Collaborators joined (20) — team members excluding the creator
        team_size = self.get_team_size()
        if team_size >= 2:
            breakdown['collaborators'] = 20
        elif team_size == 1:
            breakdown['collaborators'] = 10

        # Collaborator interest via collab requests (10)
        try:
            from app.models.ideaCollabRequest import IdeaCollabRequest
            from app.models.Enums import JoinRequestStatus
            pending_count = IdeaCollabRequest.query.filter(
                IdeaCollabRequest.idea_id == self.id,
                IdeaCollabRequest.status.in_([JoinRequestStatus.pending, JoinRequestStatus.approved])
            ).count()
            if pending_count >= 3:
                breakdown['collaborator_interest'] = 10
            elif pending_count >= 1:
                breakdown['collaborator_interest'] = 5
        except Exception:
            pass

        # Activity recency (10) — updated within last 14 days
        days_since_update = (datetime.utcnow() - self.updated_at).days
        if days_since_update <= 3:
            breakdown['activity'] = 10
        elif days_since_update <= 14:
            breakdown['activity'] = 5

        score = float(sum(breakdown.values()))

        # Persist
        self.readiness_score = score
        self.readiness_breakdown = breakdown

        # Auto-advance state based on score
        if score >= 70 and self.vision_state in ('public', 'team_forming'):
            self.vision_state = 'ready_for_activation'
        elif team_size >= 1 and self.vision_state == 'public':
            self.vision_state = 'team_forming'

        db.session.commit()
        return score

    def get_readiness_needs(self) -> list:
        """
        Returns a human-readable list of what the vision still needs,
        e.g. ["1 backend engineer", "outcome goal description", "mentor review"]
        """
        needs = []
        breakdown = self.readiness_breakdown or {}

        if breakdown.get('roadmap', 0) == 0:
            needs.append("Define a roadmap (at least one milestone)")
        if breakdown.get('problem_statement', 0) == 0:
            needs.append("Add a problem statement")
        if breakdown.get('outcome_goal', 0) == 0:
            needs.append("Define an outcome goal")
        if breakdown.get('required_roles', 0) == 0:
            needs.append("List required roles")
        if breakdown.get('collaborators', 0) < 20:
            missing = 2 - self.get_team_size()
            if missing > 0:
                needs.append(f"{missing} more collaborator{'s' if missing > 1 else ''}")

        # Suggest specific missing roles
        if self.required_roles:
            team_positions = {m.position.lower() for m in self.team_members.all()}
            for role in self.required_roles:
                if role.lower() not in team_positions:
                    needs.append(f"1 {role.replace('_', ' ')}")

        if len(needs) == 0 and self.readiness_score < 70:
            needs.append("Increase engagement to reach activation threshold")

        return needs[:4]  # cap at 4 items for clean display

    # ──────────────────────────────────────────────────────────

    def _enum_to_value(self, value):
        return value.value if hasattr(value, "value") else value

    def to_dict(self, user_id=None, include_comments=False, include_team=True):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'projectDetails': self.project_details,
            'industry': self.industry,
            'stage': self.stage,
            'privacy': self._enum_to_value(self.privacy),
            'tags': self.tags or [],
            'creator': {
                'id': self.creator_id,
                'firstName': self.creator_first_name,
                'lastName': self.creator_last_name, 
                'profilePicture': self.idea_creator.profile_picture
            },
            'status': self.status.value,
            'likes': self.likes,
            'bookmarks': self.idea_bookmarks.count(),
            'views': self.views,
            'commentsCount': self.get_comments_count(),
            'teamSize': self.get_team_size(),
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
            'imageUrl': self.image_url,

            # ── Vision System fields ──
            'visionState': self.vision_state or 'public',
            'readinessScore': self.readiness_score or 0.0,
            'readinessBreakdown': self.readiness_breakdown or {},
            'readinessNeeds': self.get_readiness_needs(),
            'problemStatement': self.problem_statement,
            'outcomeGoal': self.outcome_goal,
            'riskLevel': self.risk_level or 'medium',
            'requiredRoles': self.required_roles or [],
            'roadmapItems': self.roadmap_items or [],
        }

        if include_team:
            data['teamMembers'] = [
                {'name': tm.name, 'position': tm.position, 'skills': tm.skills} 
                for tm in self.team_members.all()
            ]
        if user_id:
            data['hasLiked'] = self.idea_likes.filter_by(user_id=user_id).count() > 0
            data['hasBookmarked'] = self.idea_bookmarks.filter_by(user_id=user_id).count() > 0
        if include_comments:
            data['comments'] = [
                comment.to_dict() 
                for comment in self.idea_comments.order_by(IdeaComment.created_at.desc()).all()
            ]
            data['commentsCount'] = self.idea_comments.count()
            data['collaborators'] = self.get_team_size()
            
        return data