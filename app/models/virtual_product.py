from datetime import datetime
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db
from sqlalchemy import JSON


currency_type = db.Column(db.String(20), nullable=False)
product_type = db.Column(db.String(50), nullable=False)




class VirtualProduct(db.Model):
    __tablename__ = "virtual_products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    product_type = db.Column(db.String(50), nullable=False) # feature_unlock, cosmetic, booster, subscription, etc.
    currency_type = db.Column(db.String(20), nullable=False)  # sf_coins, premium_gems, event_tokens
    price = db.Column(db.Integer, nullable=False)
    original_price = db.Column(db.Integer, nullable=True)  # For showing discounts
    discount_percent = db.Column(db.Integer, nullable=True)
    duration_days = db.Column(db.Integer)  # For time-based items
    consumable = db.Column(db.Boolean, default=False)
    max_purchases = db.Column(db.Integer)  # Purchase limit per user
    stock_quantity = db.Column(db.Integer)  # Available stock (null = unlimited)
    
    # Display
    is_featured = db.Column(db.Boolean, default=False)
    badge_text = db.Column(db.String(50))  # e.g., "NEW", "HOT", "LIMITED"
    category = db.Column(db.String(100))
    tags = db.Column(JSON, default=list)
    benefits = db.Column(JSON, default=list)
    
    # Requirements
    min_user_level = db.Column(db.Integer, default=1)
    required_achievements = db.Column(JSON, default=list)
    
    # Visibility
    is_active = db.Column(db.Boolean, default=True)
    available_from = db.Column(db.DateTime)
    available_to = db.Column(db.DateTime)
    
    # Media
    icon_url = db.Column(db.Text)
    preview_url = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    purchases = db.relationship('ProductPurchase', back_populates='product', cascade="all, delete-orphan")
    inventory_items = db.relationship('UserInventory', back_populates='product', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<VirtualProduct {self.name}>"

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'product_type': self.product_type,
            'currency_type': self.currency_type,
            'price': self.price,
            'original_price': self.original_price,
            'discount_percent': self.discount_percent,
            'duration_days': self.duration_days,
            'consumable': self.consumable,
            'max_purchases': self.max_purchases,
            'stock_quantity': self.stock_quantity,
            'is_featured': self.is_featured,
            'badge_text': self.badge_text,
            'category': self.category,
            'tags': self.tags,
            'benefits': self.benefits,
            'min_user_level': self.min_user_level,
            'is_active': self.is_active,
            'is_available': self.is_available(),
            'icon_url': self.icon_url,
            'preview_url': self.preview_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    # Save product to database
    def save(self):
        db.session.add(self)
        db.session.commit()

    # Delete product from database
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    # Find product by ID
    @classmethod
    def find_by_id(cls, product_id):
        return cls.query.filter_by(id=product_id).first()

    # Find active products
    @classmethod
    def find_active_products(cls):
        now = datetime.utcnow()
        return cls.query.filter(
            cls.is_active == True,
            (cls.available_from == None) | (cls.available_from <= now),
            (cls.available_to == None) | (cls.available_to >= now)
        ).all()

    # Find featured products
    @classmethod
    def find_featured_products(cls):
        return cls.query.filter_by(is_featured=True, is_active=True).all()

    # Find products by type
    @classmethod
    def find_by_type(cls, product_type: str):
        return cls.query.filter_by(product_type=product_type, is_active=True).all()

    # Check if product is available
    def is_available(self) -> bool:
        if not self.is_active:
            return False
        
        now = datetime.utcnow()
        if self.available_from and self.available_from > now:
            return False
        if self.available_to and self.available_to < now:
            return False
        
        if self.stock_quantity is not None and self.stock_quantity <= 0:
            return False
        
        return True

    # Check if user meets requirements
    def user_meets_requirements(self, user_level: int, user_achievements: list = None) -> bool:
        if user_level < self.min_user_level:
            return False
        
        if self.required_achievements and user_achievements:
            required_set = set(self.required_achievements)
            user_set = set(user_achievements)
            if not required_set.issubset(user_set):
                return False
        
        return True