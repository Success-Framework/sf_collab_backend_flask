from app.extensions import db
from sqlalchemy import JSON

class TeamMember(db.Model):
    __tablename__ = 'team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255))
    position = db.Column(db.String(255))
    skills = db.Column(JSON, default={})
    
    # Relationships
    parent_idea = db.relationship('Idea', back_populates='team_members')
    
    # HELPER FUNCTIONS
    
    def update_skills(self, new_skills):
        """Update team member skills"""
        self.skills = new_skills
        db.session.commit()
    
    def add_skill(self, skill_name, proficiency='intermediate'):
        """Add a skill to team member"""
        if not self.skills:
            self.skills = {}
        self.skills[skill_name] = proficiency
        db.session.commit()
    
    def remove_skill(self, skill_name):
        """Remove a skill from team member"""
        if self.skills and skill_name in self.skills:
            del self.skills[skill_name]
            db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'idea_id': self.idea_id,
            'name': self.name,
            'position': self.position,
            'skills': self.skills or {}
        }