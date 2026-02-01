from datetime import datetime
from app.extensions import db
from sqlalchemy import Enum, JSON
from .Enums import StartupStage
import os
from sqlalchemy.ext.mutable import MutableDict, MutableList

class Startup(db.Model):
    __tablename__ = 'startups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255))
    description = db.Column(db.Text)
    stage = db.Column(Enum(StartupStage), default=StartupStage.idea)
    
    # Financial Foundation Fields
    revenue = db.Column(db.Float, default=0.0)  # Annual revenue in USD
    funding_amount = db.Column(db.Float, default=0.0)  # Total funding raised
    funding_round = db.Column(db.String(50), default='pre-seed')  # pre-seed, seed, series-a, etc.
    burn_rate = db.Column(db.Float, default=0.0)  # Monthly burn rate in USD
    runway_months = db.Column(db.Integer, default=0)  # Months until out of cash
    valuation = db.Column(db.Float, default=0.0)  # Company valuation in USD
    financial_notes = db.Column(db.Text)  # Additional financial context
    
    # File paths instead of binary data
    logo_path = db.Column(db.String(500))
    logo_content_type = db.Column(db.String(100))
    banner_path = db.Column(db.String(500))
    banner_content_type = db.Column(db.String(100))
    
    # Add URL fields for frontend
    logo_url = db.Column(db.String(500))
    banner_url = db.Column(db.String(500))
    
    roles = db.Column(MutableDict.as_mutable(JSON), default=dict)
    tech_stack = db.Column(MutableList.as_mutable(JSON), default=list)
    
    positions = db.Column(db.Integer, default=0)
    
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    creator_first_name = db.Column(db.String(100))
    creator_last_name = db.Column(db.String(100))
    
    status = db.Column(db.String(50), default='active')
    member_count = db.Column(db.Integer, default=1)
    views = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    startup_creator = db.relationship(
        "User",
        back_populates="startups",
        foreign_keys=[creator_id]
    )
    
    startup_members = db.relationship('StartupMember', 
        back_populates='member_startup', 
        lazy='dynamic', 
        cascade='all, delete-orphan',
        foreign_keys='StartupMember.startup_id')
    
    join_requests = db.relationship('JoinRequest', 
        back_populates='target_startup', 
        lazy='dynamic', 
        cascade='all, delete-orphan',
        foreign_keys='JoinRequest.startup_id')
    
    startup_bookmarks = db.relationship('StartupBookmark',
        back_populates='startup',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='StartupBookmark.startup_id')
    
    startup_tasks = db.relationship('Task',
        back_populates='parent_startup',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='Task.startup_id')
    
    project_goals = db.relationship('ProjectGoal',
        back_populates='parent_startup',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='ProjectGoal.startup_id')
    
    team_performance_records = db.relationship('TeamPerformance',
        back_populates='parent_startup',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='TeamPerformance.startup_id')
    
    growth_metrics_startup = db.relationship('GrowthMetric',
        back_populates='parent_startup',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='GrowthMetric.startup_id')
    
    calendar_events = db.relationship('CalendarEvent',
        back_populates='parent_startup',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='CalendarEvent.startup_id')
        
    startup_documents = db.relationship('StartupDocument',
        back_populates='parent_startup',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='StartupDocument.startup_id')
    # HELPER FUNCTIONS
    def increment_views(self):
        """Increment view count"""
        self.views += 1
        db.session.commit()
    
    def update_member_count(self):
        """Update member count based on active members"""
        active_members = self.startup_members.filter_by(is_active=True).count()
        self.member_count = active_members
        db.session.commit()
    
    def add_member(self, user_id, first_name, last_name, role='member'):
        """Add a new member to the startup"""
        from app.models.startUpMember import StartupMember
        member = StartupMember(
            startup_id=self.id,
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        db.session.add(member)
        self.update_member_count()
        db.session.commit()
        return member
    
    def remove_member(self, user_id):
        """Remove a member from the startup"""
        member = self.startup_members.filter_by(user_id=user_id, is_active=True).first()
        if member:
            member.is_active = False
            self.update_member_count()
    def remove_member_by_id(self, member_id):
        member = self.startup_members.filter_by(
            id=member_id,
            is_active=True
        ).first()

        if not member:
            return False

        db.session.delete(member)
        self.update_member_count()
        db.session.commit()
        return True

    def update_stage(self, new_stage):
        """Update startup stage"""
        self.stage = StartupStage(new_stage)
        db.session.commit()
    
    def add_position(self, role_name, count=1):
        """Add available positions"""
        if not self.roles:
            self.roles = {}
        
        # Handle both old and new roles structure
        if role_name not in self.roles:
            # Initialize with new structure
            self.roles[role_name] = {
                "roleType": "Full Time",  # Default role type
                "positionsNumber": count
            }
        else:
            # Update existing role
            role_data = self.roles[role_name]
            if isinstance(role_data, dict):
                # New structure: increment positionsNumber
                current_positions = role_data.get('positionsNumber', 0)
                role_data['positionsNumber'] = current_positions + count
            else:
                # Old structure: convert to new structure
                self.roles[role_name] = {
                    "roleType": role_data,  # Preserve the old role type
                    "positionsNumber": count
                }
        
        self.positions += count
        db.session.commit()
    
    def fill_position(self, role_name):
        """Fill an available position"""
        if self.roles and role_name in self.roles:
            role_data = self.roles[role_name]
            
            if isinstance(role_data, dict):
                # New structure: check and decrement positionsNumber
                current_positions = role_data.get('positionsNumber', 0)
                if current_positions > 0:
                    role_data['positionsNumber'] = current_positions - 1
                    self.positions -= 1
                    db.session.commit()
            else:
                # Old structure: treat as 1 position per role
                # Remove the role entirely since old structure didn't track multiple positions
                del self.roles[role_name]
                self.positions -= 1
                db.session.commit()
    
    def get_active_members(self):
        """Get list of active members"""
        return self.startup_members.filter_by(is_active=True).all()
    
    def add_document(self, filename, file_path, content_type, document_type='general', file_url=None):
        """Add a document to the startup"""
        from app.models.startup_document import StartupDocument
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        # Generate file_url if not provided
        if not file_url:
            unique_filename = os.path.basename(file_path)
            file_url = f"/startups/uploads/{self.id}/{unique_filename}"
        
        document = StartupDocument(
            startup_id=self.id,
            filename=filename,
            file_path=file_path,
            file_url=file_url,
            content_type=content_type,
            document_type=document_type,
            file_size=file_size
        )
        db.session.add(document)
        db.session.commit()
        return document
        

    def get_documents(self, document_type=None):
        """Get startup documents, optionally filtered by type"""
        query = self.startup_documents
        if document_type:
            query = query.filter_by(document_type=document_type)
        return query.all()
    
    def _enum_to_value(self, value):
        return value.value if hasattr(value, "value") else value
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'industry': self.industry,
            'location': self.location,
            'description': self.description,
            'stage': self._enum_to_value(self.stage),
            'positions': self.positions,
            'roles': self.roles or {},
            
            'tech_stack': self.tech_stack or [],
            
            'revenue': self.revenue,
            'funding_amount': self.funding_amount,
            'funding_round': self.funding_round,
            'burn_rate': self.burn_rate,
            'runway_months': self.runway_months,
            'valuation': self.valuation,
            'financial_notes': self.financial_notes,
            'logo_url': self.logo_url or (f'/startups/{self.id}/logo' if self.logo_path else None),
            'banner_url': self.banner_url or (f'/startups/{self.id}/banner' if self.banner_path else None),
            'creator': {
                'id': self.creator_id,
                'firstName': self.creator_first_name,
                'lastName': self.creator_last_name
            },
            'status': self.status,
            'memberCount': self.member_count,
            'views': self.views,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }