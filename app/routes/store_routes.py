"""
Store Routes - SF Collab Virtual Product Store API
Handles products, purchases, and inventory management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.UserWallet import UserWallet
from app.models.WalletTransaction import WalletTransaction
from app.models.virtual_product import VirtualProduct
from app.models.product_purchase import ProductPurchase
from app.models.user_inventory import UserInventory
from app.models.user import User
from datetime import datetime, timedelta
from sqlalchemy import desc

store_bp = Blueprint('store', __name__)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_or_create_wallet(user_id):
    """Get user's wallet or create one if it doesn't exist"""
    wallet = UserWallet.query.filter_by(user_id=user_id).first()
    
    if not wallet:
        wallet = UserWallet(
            user_id=user_id,
            sf_coins=100,
            premium_gems=0,
            event_tokens=0,
            total_coins_earned=100,
            daily_earning_limit=1000
        )
        db.session.add(wallet)
        db.session.commit()
    
    return wallet


# ============================================================================
# PRODUCT ENDPOINTS
# ============================================================================

@store_bp.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    """Get all available products"""
    try:
        category = request.args.get('category')
        product_type = request.args.get('product_type')
        currency_type = request.args.get('currency_type')
        is_featured = request.args.get('is_featured')
        
        query = VirtualProduct.query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category=category)
        if product_type:
            query = query.filter_by(product_type=product_type)
        if currency_type:
            query = query.filter_by(currency_type=currency_type)
        if is_featured:
            query = query.filter_by(is_featured=True)
        
        products = query.order_by(desc(VirtualProduct.is_featured), VirtualProduct.name).all()
        
        return jsonify({
            'success': True,
            'products': [p.to_dict() for p in products]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@store_bp.route('/products/featured', methods=['GET'])
@jwt_required()
def get_featured_products():
    """Get featured products"""
    try:
        products = VirtualProduct.find_featured_products()
        
        return jsonify({
            'success': True,
            'products': [p.to_dict() for p in products]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@store_bp.route('/products/<product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    """Get single product details"""
    try:
        user_id = get_jwt_identity()
        product = VirtualProduct.find_by_id(product_id)
        
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        # Check if user owns this product
        owned = UserInventory.find_user_product(user_id, product_id) is not None
        
        return jsonify({
            'success': True,
            'product': product.to_dict(),
            'owned': owned
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@store_bp.route('/products/<product_id>/purchase', methods=['POST'])
@jwt_required()
def purchase_product(product_id):
    """Purchase a product"""
    try:
        user_id = get_jwt_identity()
        
        product = VirtualProduct.find_by_id(product_id)
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        # Check if product is available
        if not product.is_available():
            return jsonify({'success': False, 'error': 'Product is not available'}), 400
        
        # Check purchase limits
        if product.max_purchases:
            existing_purchases = ProductPurchase.count_user_purchases(user_id, product_id)
            if existing_purchases >= product.max_purchases:
                return jsonify({'success': False, 'error': 'Purchase limit reached'}), 400
        
        # Check stock
        if product.stock_quantity is not None and product.stock_quantity <= 0:
            return jsonify({'success': False, 'error': 'Out of stock'}), 400
        
        wallet = get_or_create_wallet(user_id)
        
        # Check balance based on currency type
        if product.currency_type == 'sf_coins':
            if wallet.sf_coins < product.price:
                return jsonify({
                    'success': False,
                    'error': 'Insufficient SF Coins',
                    'balance': wallet.sf_coins,
                    'required': product.price
                }), 400
            balance_before = wallet.sf_coins
            wallet.sf_coins -= product.price
            wallet.total_coins_spent += product.price
            balance_after = wallet.sf_coins
            
        elif product.currency_type == 'premium_gems':
            if wallet.premium_gems < product.price:
                return jsonify({
                    'success': False,
                    'error': 'Insufficient SF Crystals',
                    'balance': wallet.premium_gems,
                    'required': product.price
                }), 400
            balance_before = wallet.premium_gems
            wallet.premium_gems -= product.price
            balance_after = wallet.premium_gems
            
        else:  # event_tokens
            if wallet.event_tokens < product.price:
                return jsonify({
                    'success': False,
                    'error': 'Insufficient Event Tokens',
                    'balance': wallet.event_tokens,
                    'required': product.price
                }), 400
            balance_before = wallet.event_tokens
            wallet.event_tokens -= product.price
            balance_after = wallet.event_tokens
        
        # Calculate expiration date if applicable
        expires_at = None
        if product.duration_days:
            expires_at = datetime.utcnow() + timedelta(days=product.duration_days)
        
        # Create purchase record
        purchase = ProductPurchase(
            user_id=user_id,
            product_id=product_id,
            currency_type=product.currency_type,
            amount_paid=product.price,
            status='completed',
            expires_at=expires_at
        )
        db.session.add(purchase)
        
        # Add to inventory
        inventory_item = UserInventory(
            user_id=user_id,
            product_id=product_id,
            purchase_id=purchase.id,
            quantity=1,
            remaining_uses=1 if product.consumable else None,
            expires_at=expires_at
        )
        db.session.add(inventory_item)
        
        # Update stock if limited
        if product.stock_quantity is not None:
            product.stock_quantity -= 1
        
        # Record transaction
        WalletTransaction.record_transaction(
            wallet_id=wallet.id,
            user_id=user_id,
            transaction_type='purchase',
            currency_type=product.currency_type,
            amount=product.price,
            balance_before=balance_before,
            balance_after=balance_after,
            reference_type='product',
            reference_id=str(product_id),
            description=f'Purchased: {product.name}'
        )
        db.session.commit()
        
        return jsonify({
            'success': True,
            'purchase': purchase.to_dict(),
            'inventory_item': inventory_item.to_dict(),
            'wallet': wallet.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# INVENTORY ENDPOINTS
# ============================================================================

@store_bp.route('/inventory', methods=['GET'])
@jwt_required()
def get_inventory():
    """Get user's inventory"""
    try:
        user_id = get_jwt_identity()
        
        product_type = request.args.get('product_type')
        is_equipped = request.args.get('is_equipped')
        include_expired = request.args.get('include_expired', 'false').lower() == 'true'
        
        query = UserInventory.query.filter_by(user_id=user_id)
        
        if not include_expired:
            query = query.filter_by(expired=False, is_consumed=False)
        
        if is_equipped:
            query = query.filter_by(is_equipped=True)
        
        items = query.all()
        
        # Filter by product type if specified
        if product_type:
            items = [item for item in items if item.product and item.product.product_type == product_type]
        
        return jsonify({
            'success': True,
            'inventory': [item.to_dict() for item in items]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@store_bp.route('/inventory/<item_id>/equip', methods=['POST'])
@jwt_required()
def equip_item(item_id):
    """Equip an inventory item"""
    try:
        user_id = get_jwt_identity()
        
        item = UserInventory.find_by_id(item_id)
        
        if not item or str(item.user_id) != str(user_id):
            return jsonify({'success': False, 'error': 'Item not found'}), 404
        
        if not item.is_valid():
            return jsonify({'success': False, 'error': 'Item is expired or consumed'}), 400
        
        # Unequip other items of same type
        if item.product:
            other_items = UserInventory.query.filter(
                UserInventory.user_id == user_id,
                UserInventory.is_equipped == True,
                UserInventory.id != item_id
            ).join(VirtualProduct).filter(
                VirtualProduct.product_type == item.product.product_type
            ).all()
            
            for other in other_items:
                other.is_equipped = False
        
        item.is_equipped = not item.is_equipped  # Toggle
        db.session.commit()
        
        return jsonify({
            'success': True,
            'item': item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@store_bp.route('/inventory/<item_id>/use', methods=['POST'])
@jwt_required()
def use_item(item_id):
    """Use a consumable item"""
    try:
        user_id = get_jwt_identity()
        
        item = UserInventory.find_by_id(item_id)
        
        if not item or str(item.user_id) != str(user_id):
            return jsonify({'success': False, 'error': 'Item not found'}), 404
        
        if not item.is_valid():
            return jsonify({'success': False, 'error': 'Item is expired or consumed'}), 400
        
        if not item.product or not item.product.consumable:
            return jsonify({'success': False, 'error': 'Item is not consumable'}), 400
        
        remaining = item.use_consumable()
        
        return jsonify({
            'success': True,
            'item': item.to_dict(),
            'remaining_uses': remaining
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# PURCHASE HISTORY
# ============================================================================

@store_bp.route('/purchases', methods=['GET'])
@jwt_required()
def get_purchases():
    """Get user's purchase history"""
    try:
        user_id = get_jwt_identity()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        query = ProductPurchase.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(desc(ProductPurchase.purchased_at))
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'purchases': [p.to_dict() for p in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@store_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get available product categories"""
    try:
        categories = db.session.query(VirtualProduct.category).filter(
            VirtualProduct.is_active == True,
            VirtualProduct.category != None
        ).distinct().all()
        
        return jsonify({
            'success': True,
            'categories': [c[0] for c in categories if c[0]]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@store_bp.route('/admin/products', methods=['POST'])
@jwt_required()
def create_product():
    """Create a new product (admin only)"""
    try:
        admin_id = get_jwt_identity()
        
        admin_user = User.query.get(admin_id)
        if not admin_user or not getattr(admin_user, 'is_admin', False):
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        data = request.get_json()
        
        product = VirtualProduct(
            name=data.get('name'),
            description=data.get('description'),
            product_type=data.get('product_type'),
            currency_type=data.get('currency_type'),
            price=data.get('price'),
            original_price=data.get('original_price'),
            discount_percent=data.get('discount_percent'),
            duration_days=data.get('duration_days'),
            consumable=data.get('consumable', False),
            max_purchases=data.get('max_purchases'),
            stock_quantity=data.get('stock_quantity'),
            is_featured=data.get('is_featured', False),
            badge_text=data.get('badge_text'),
            category=data.get('category'),
            tags=data.get('tags'),
            benefits=data.get('benefits'),
            icon_url=data.get('icon_url'),
            preview_url=data.get('preview_url')
        )
        
        product.save()
        
        return jsonify({
            'success': True,
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@store_bp.route('/admin/products/<product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Update a product (admin only)"""
    try:
        admin_id = get_jwt_identity()
        
        admin_user = User.query.get(admin_id)
        if not admin_user or not getattr(admin_user, 'is_admin', False):
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        product = VirtualProduct.find_by_id(product_id)
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        for field in ['name', 'description', 'product_type', 'currency_type', 'price',
                      'original_price', 'discount_percent', 'duration_days', 'consumable',
                      'max_purchases', 'stock_quantity', 'is_featured', 'badge_text',
                      'category', 'tags', 'benefits', 'is_active', 'icon_url', 'preview_url']:
            if field in data:
                setattr(product, field, data[field])
        
        product.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500