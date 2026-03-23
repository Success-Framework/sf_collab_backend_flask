from datetime import datetime
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db
from sqlalchemy import JSON


class UserInventory(db.Model):
    __tablename__ = "user_inventory"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('virtual_products.id'), nullable=False)
    purchase_id = db.Column(db.Integer, db.ForeignKey('product_purchases.id'))
    quantity = db.Column(db.Integer, default=1)
    remaining_uses = db.Column(db.Integer)  # For consumables
    acquired_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_equipped = db.Column(db.Boolean, default=False)  # For cosmetics
    is_active = db.Column(db.Boolean, default=True)  # For features
    is_consumed = db.Column(db.Boolean, default=False)
    expired = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = relationship('User', back_populates='inventory')
    product = relationship('VirtualProduct', back_populates='inventory_items')
    purchase = relationship('ProductPurchase', back_populates='inventory_items')

    def __repr__(self):
        return f"<UserInventory {self.id} - User:{self.user_id} Product:{self.product_id}>"

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'product_id': str(self.product_id),
            'product': self.product.to_dict() if self.product else None,
            'purchase_id': str(self.purchase_id) if self.purchase_id else None,
            'quantity': self.quantity,
            'remaining_uses': self.remaining_uses,
            'acquired_at': self.acquired_at.isoformat() if self.acquired_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_equipped': self.is_equipped,
            'is_active': self.is_active,
            'is_consumed': self.is_consumed,
            'is_valid': self.is_valid()
        }

    # Save inventory item to database
    def save(self):
        db.session.add(self)
        db.session.commit()

    # Delete inventory item from database
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    # Find inventory item by ID
    @classmethod
    def find_by_id(cls, inventory_id):
        return cls.query.filter_by(id=inventory_id).first()

    # Find user inventory
    @classmethod
    def find_by_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()

    # Find specific user product
    @classmethod
    def find_user_product(cls, user_id, product_id):
        return cls.query.filter_by(user_id=user_id, product_id=product_id).first()

    # Find active items
    @classmethod
    def find_active_items(cls, user_id):
        return cls.query.filter_by(
            user_id=user_id,
            is_active=True,
            is_consumed=False,
            expired=False
        ).all()

    # Find equipped items
    @classmethod
    def find_equipped_items(cls, user_id):
        return cls.query.filter_by(user_id=user_id, is_equipped=True).all()

    # Equip item
    def equip(self):
        self.is_equipped = True
        self.save()

    # Unequip item
    def unequip(self):
        self.is_equipped = False
        self.save()

    # Use consumable
    def use_consumable(self, amount: int = 1):
        if self.remaining_uses is not None:
            self.remaining_uses -= amount
            if self.remaining_uses <= 0:
                self.is_consumed = True
                self.is_active = False
        elif self.quantity > 0:
            self.quantity -= amount
            if self.quantity <= 0:
                self.is_consumed = True
                self.is_active = False
        self.save()
        return self.remaining_uses if self.remaining_uses is not None else self.quantity

    # Check if item is valid
    def is_valid(self) -> bool:
        if self.is_consumed or self.expired:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            self.expired = True
            self.is_active = False
            db.session.commit()
            return False
        return True