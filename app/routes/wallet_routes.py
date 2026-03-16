"""
Wallet Routes - Manage virtual currency

Endpoints:
- GET  /api/wallet/balance              - Get wallet info
- GET  /api/wallet/balance/<user_id>    - Get specific user's wallet (admin/self)
- GET  /api/wallet/history              - Get transaction history
- POST /api/wallet/earn                 - Earn SF Coins
- POST /api/wallet/spend                - Spend SF Coins
- POST /api/wallet/crystals/add         - Add Premium Gems
- POST /api/wallet/crystals/spend       - Spend Premium Gems
- POST /api/wallet/event-tokens/add     - Add Event Tokens
- POST /api/wallet/transfer             - Transfer coins to another user
- POST /api/wallet/bonus                - Admin: award bonus
- GET  /api/wallet/leaderboard          - Top earners (supports ?period=all|weekly|monthly)
- GET  /api/wallet/stats                - Detailed stats
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.UserWallet import UserWallet
from app.models.WalletTransaction import WalletTransaction
from app.models.user import User
from datetime import datetime, timedelta
from sqlalchemy import desc, func

wallet_bp = Blueprint('wallet', __name__)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_or_create_wallet(user_id):
    """Get user's wallet or create one if it doesn't exist"""
    # Always cast to int — JWT identity comes back as a string
    user_id = int(user_id)
    wallet = UserWallet.query.filter_by(user_id=user_id).first()

    if not wallet:
        wallet = UserWallet(
            user_id=user_id,
            sf_coins=100,  # Welcome bonus
            premium_gems=0,
            event_tokens=0,
            total_coins_earned=100,
            daily_earning_limit=1000
        )
        db.session.add(wallet)
        db.session.flush()  # get wallet.id without committing

        # Record welcome bonus transaction
        WalletTransaction.record_transaction(
            wallet_id=wallet.id,
            user_id=user_id,
            transaction_type='bonus',
            currency_type='sf_coins',
            amount=100,
            balance_before=0,
            balance_after=100,
            description='Welcome bonus'
        )
        db.session.commit()

    return wallet


# ============================================================================
# WALLET ENDPOINTS
# ============================================================================

@wallet_bp.route('/balance', methods=['GET'])
@jwt_required()
def get_balance():
    """Get current user's wallet balance"""
    try:
        user_id = int(get_jwt_identity())
        wallet = get_or_create_wallet(user_id)

        return jsonify({
            'success': True,
            'wallet': wallet.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@wallet_bp.route('/balance/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_balance(user_id):
    """Get specific user's wallet balance (admin or self)"""
    try:
        current_user_id = int(get_jwt_identity())

        # Only allow self or admin
        if current_user_id != user_id:
            current_user = User.query.get(current_user_id)
            if not current_user or not getattr(current_user, 'is_admin', False):
                return jsonify({'success': False, 'error': 'Unauthorized'}), 403

        wallet = get_or_create_wallet(user_id)

        return jsonify({
            'success': True,
            'wallet': wallet.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@wallet_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """Get transaction history for current user"""
    try:
        user_id = int(get_jwt_identity())
        wallet = get_or_create_wallet(user_id)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        currency_type = request.args.get('currency_type')
        transaction_type = request.args.get('transaction_type')

        query = WalletTransaction.query.filter_by(wallet_id=wallet.id)

        if currency_type:
            query = query.filter_by(currency_type=currency_type)
        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)

        query = query.order_by(desc(WalletTransaction.created_at))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'success': True,
            'transactions': [tx.to_dict() for tx in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@wallet_bp.route('/earn', methods=['POST'])
@jwt_required()
def earn_coins():
    """Earn SF Coins (subject to daily limit)"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        amount = data.get('amount', 0)
        description = data.get('description', 'Earned SF Coins')
        reference_type = data.get('reference_type')
        reference_id = data.get('reference_id')

        if amount <= 0:
            return jsonify({'success': False, 'error': 'Amount must be positive'}), 400

        wallet = get_or_create_wallet(user_id)
        wallet.check_and_reset_daily()

        # Check daily limit
        if wallet.daily_earnings + amount > wallet.daily_earning_limit:
            remaining = wallet.daily_earning_limit - wallet.daily_earnings
            return jsonify({
                'success': False,
                'error': f'Daily earning limit exceeded. You can earn {remaining} more coins today.',
                'remaining': remaining
            }), 400

        balance_before = wallet.sf_coins
        wallet.sf_coins += amount
        wallet.total_coins_earned += amount
        wallet.daily_earnings += amount

        WalletTransaction.record_transaction(
            wallet_id=wallet.id,
            user_id=user_id,
            transaction_type='earn',
            currency_type='sf_coins',
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.sf_coins,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description
        )
        db.session.commit()

        return jsonify({
            'success': True,
            'wallet': wallet.to_dict(),
            'earned': amount
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@wallet_bp.route('/spend', methods=['POST'])
@jwt_required()
def spend_coins():
    """Spend SF Coins"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        amount = data.get('amount', 0)
        description = data.get('description', 'Spent SF Coins')
        reference_type = data.get('reference_type')
        reference_id = data.get('reference_id')

        if amount <= 0:
            return jsonify({'success': False, 'error': 'Amount must be positive'}), 400

        wallet = get_or_create_wallet(user_id)

        if wallet.sf_coins < amount:
            return jsonify({
                'success': False,
                'error': 'Insufficient SF Coins',
                'balance': wallet.sf_coins,
                'required': amount
            }), 400

        balance_before = wallet.sf_coins
        wallet.sf_coins -= amount
        wallet.total_coins_spent += amount

        WalletTransaction.record_transaction(
            wallet_id=wallet.id,
            user_id=user_id,
            transaction_type='spend',
            currency_type='sf_coins',
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.sf_coins,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description
        )
        db.session.commit()

        return jsonify({
            'success': True,
            'wallet': wallet.to_dict(),
            'spent': amount
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@wallet_bp.route('/crystals/add', methods=['POST'])
@jwt_required()
def add_crystals():
    """Add SF Crystals (Premium Gems) — from purchase"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        amount = data.get('amount', 0)
        description = data.get('description', 'Added SF Crystals')
        payment_reference = data.get('payment_reference')

        if amount <= 0:
            return jsonify({'success': False, 'error': 'Amount must be positive'}), 400

        wallet = get_or_create_wallet(user_id)

        balance_before = wallet.premium_gems
        wallet.premium_gems += amount

        WalletTransaction.record_transaction(
            wallet_id=wallet.id,
            user_id=user_id,
            transaction_type='earn',
            currency_type='premium_gems',
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.premium_gems,
            reference_type='payment',
            reference_id=payment_reference,
            description=description
        )
        db.session.commit()

        return jsonify({
            'success': True,
            'wallet': wallet.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@wallet_bp.route('/crystals/spend', methods=['POST'])
@jwt_required()
def spend_crystals():
    """Spend SF Crystals (Premium Gems)"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        amount = data.get('amount', 0)
        description = data.get('description', 'Spent SF Crystals')
        reference_type = data.get('reference_type')
        reference_id = data.get('reference_id')

        if amount <= 0:
            return jsonify({'success': False, 'error': 'Amount must be positive'}), 400

        wallet = get_or_create_wallet(user_id)

        if wallet.premium_gems < amount:
            return jsonify({
                'success': False,
                'error': 'Insufficient SF Crystals',
                'balance': wallet.premium_gems,
                'required': amount
            }), 400

        balance_before = wallet.premium_gems
        wallet.premium_gems -= amount

        WalletTransaction.record_transaction(
            wallet_id=wallet.id,
            user_id=user_id,
            transaction_type='spend',
            currency_type='premium_gems',
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.premium_gems,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description
        )
        db.session.commit()

        return jsonify({
            'success': True,
            'wallet': wallet.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@wallet_bp.route('/event-tokens/add', methods=['POST'])
@jwt_required()
def add_event_tokens():
    """Add Event Tokens"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        amount = data.get('amount', 0)
        description = data.get('description', 'Added Event Tokens')
        event_id = data.get('event_id')

        if amount <= 0:
            return jsonify({'success': False, 'error': 'Amount must be positive'}), 400

        wallet = get_or_create_wallet(user_id)

        balance_before = wallet.event_tokens
        wallet.event_tokens += amount

        WalletTransaction.record_transaction(
            wallet_id=wallet.id,
            user_id=user_id,
            transaction_type='earn',
            currency_type='event_tokens',
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.event_tokens,
            reference_type='event',
            reference_id=event_id,
            description=description
        )
        db.session.commit()

        return jsonify({
            'success': True,
            'wallet': wallet.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@wallet_bp.route('/transfer', methods=['POST'])
@jwt_required()
def transfer_coins():
    """Transfer SF Coins to another user"""
    try:
        sender_id = int(get_jwt_identity())
        data = request.get_json()

        recipient_id = data.get('recipient_id')
        amount = data.get('amount', 0)
        message = data.get('message', '')

        if not recipient_id:
            return jsonify({'success': False, 'error': 'Recipient ID required'}), 400

        recipient_id = int(recipient_id)

        if sender_id == recipient_id:
            return jsonify({'success': False, 'error': 'Cannot transfer to yourself'}), 400

        if amount <= 0:
            return jsonify({'success': False, 'error': 'Amount must be positive'}), 400

        # Verify recipient exists
        recipient_user = User.query.get(recipient_id)
        if not recipient_user:
            return jsonify({'success': False, 'error': 'Recipient not found'}), 404

        sender_wallet = get_or_create_wallet(sender_id)
        recipient_wallet = get_or_create_wallet(recipient_id)

        if sender_wallet.sf_coins < amount:
            return jsonify({
                'success': False,
                'error': 'Insufficient SF Coins',
                'balance': sender_wallet.sf_coins
            }), 400

        sender_before = sender_wallet.sf_coins
        recipient_before = recipient_wallet.sf_coins

        sender_wallet.sf_coins -= amount
        sender_wallet.total_coins_spent += amount
        recipient_wallet.sf_coins += amount
        recipient_wallet.total_coins_earned += amount

        WalletTransaction.record_transaction(
            wallet_id=sender_wallet.id,
            user_id=sender_id,
            transaction_type='transfer',
            currency_type='sf_coins',
            amount=amount,
            balance_before=sender_before,
            balance_after=sender_wallet.sf_coins,
            reference_type='transfer_out',
            reference_id=str(recipient_id),
            description=f'Transfer to user: {message}' if message else 'Transfer to user'
        )

        WalletTransaction.record_transaction(
            wallet_id=recipient_wallet.id,
            user_id=recipient_id,
            transaction_type='transfer',
            currency_type='sf_coins',
            amount=amount,
            balance_before=recipient_before,
            balance_after=recipient_wallet.sf_coins,
            reference_type='transfer_in',
            reference_id=str(sender_id),
            description=f'Transfer from user: {message}' if message else 'Transfer from user'
        )
        db.session.commit()

        return jsonify({
            'success': True,
            'sender_wallet': sender_wallet.to_dict(),
            'transferred': amount
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@wallet_bp.route('/bonus', methods=['POST'])
@jwt_required()
def award_bonus():
    """Award bonus to user (admin only, bypasses daily limit)"""
    try:
        admin_id = int(get_jwt_identity())

        admin_user = User.query.get(admin_id)
        if not admin_user or not getattr(admin_user, 'is_admin', False):
            return jsonify({'success': False, 'error': 'Admin access required'}), 403

        data = request.get_json()

        user_id = data.get('user_id')
        amount = data.get('amount', 0)
        currency_type = data.get('currency_type', 'sf_coins')
        description = data.get('description', 'Bonus awarded')

        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400

        user_id = int(user_id)

        if amount <= 0:
            return jsonify({'success': False, 'error': 'Amount must be positive'}), 400

        if currency_type not in ['sf_coins', 'premium_gems', 'event_tokens']:
            return jsonify({'success': False, 'error': 'Invalid currency type'}), 400

        wallet = get_or_create_wallet(user_id)

        if currency_type == 'sf_coins':
            balance_before = wallet.sf_coins
            wallet.sf_coins += amount
            wallet.total_coins_earned += amount
            balance_after = wallet.sf_coins
        elif currency_type == 'premium_gems':
            balance_before = wallet.premium_gems
            wallet.premium_gems += amount
            balance_after = wallet.premium_gems
        else:  # event_tokens
            balance_before = wallet.event_tokens
            wallet.event_tokens += amount
            balance_after = wallet.event_tokens

        WalletTransaction.record_transaction(
            wallet_id=wallet.id,
            user_id=user_id,
            transaction_type='bonus',
            currency_type=currency_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            reference_type='admin_bonus',
            reference_id=str(admin_id),
            description=description
        )
        db.session.commit()

        return jsonify({
            'success': True,
            'wallet': wallet.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@wallet_bp.route('/leaderboard', methods=['GET'])
@jwt_required()
def get_leaderboard():
    """
    Get top earners leaderboard.

    Query params:
      - limit  (int, default 10, max 100)
      - period (str: all | weekly | monthly)
    """
    try:
        limit = min(request.args.get('limit', 10, type=int), 100)
        period = request.args.get('period', 'all')  # all, weekly, monthly

        # For period filtering we look at transaction sums rather than the
        # static total_coins_earned field, which only reflects all-time data.
        if period in ('weekly', 'monthly'):
            if period == 'weekly':
                since = datetime.utcnow() - timedelta(weeks=1)
            else:  # monthly
                since = datetime.utcnow() - timedelta(days=30)

            # Sum earn/bonus transactions per user within the window
            period_earnings = (
                db.session.query(
                    WalletTransaction.user_id,
                    func.sum(WalletTransaction.amount).label('period_earned')
                )
                .filter(
                    WalletTransaction.transaction_type.in_(['earn', 'bonus']),
                    WalletTransaction.currency_type == 'sf_coins',
                    WalletTransaction.created_at >= since
                )
                .group_by(WalletTransaction.user_id)
                .subquery()
            )

            rows = (
                db.session.query(
                    User.id.label('user_id'),
                    User.first_name,
                    User.last_name,
                    User.profile_picture,
                    UserWallet.sf_coins,
                    period_earnings.c.period_earned.label('total_earned')
                )
                .join(UserWallet, UserWallet.user_id == User.id)
                .join(period_earnings, period_earnings.c.user_id == User.id)
                .order_by(desc('total_earned'))
                .limit(limit)
                .all()
            )
        else:
            # All-time: use the cached total_coins_earned column (fast)
            rows = (
                db.session.query(
                    UserWallet.user_id,
                    UserWallet.total_coins_earned,
                    UserWallet.sf_coins,
                    User.first_name,
                    User.last_name,
                    User.profile_picture
                )
                .join(User, UserWallet.user_id == User.id)
                .order_by(desc(UserWallet.total_coins_earned))
                .limit(limit)
                .all()
            )

        leaderboard = []
        for i, row in enumerate(rows, 1):
            leaderboard.append({
                'rank': i,
                'user_id': str(row.user_id),
                'username': f"{row.first_name} {row.last_name}",
                'profile_picture': row.profile_picture,
                'total_earned': row.total_earned if period in ('weekly', 'monthly') else row.total_coins_earned,
                'current_balance': row.sf_coins
            })

        return jsonify({
            'success': True,
            'leaderboard': leaderboard,
            'period': period
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@wallet_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get detailed wallet statistics"""
    try:
        user_id = int(get_jwt_identity())
        wallet = get_or_create_wallet(user_id)
        wallet.check_and_reset_daily()

        # Earnings breakdown by source
        earnings = (
            db.session.query(
                WalletTransaction.reference_type,
                func.sum(WalletTransaction.amount).label('total')
            )
            .filter(
                WalletTransaction.wallet_id == wallet.id,
                WalletTransaction.transaction_type == 'earn'
            )
            .group_by(WalletTransaction.reference_type)
            .all()
        )
        earnings_breakdown = {e.reference_type or 'other': e.total for e in earnings}

        # Spending breakdown by source
        spending = (
            db.session.query(
                WalletTransaction.reference_type,
                func.sum(WalletTransaction.amount).label('total')
            )
            .filter(
                WalletTransaction.wallet_id == wallet.id,
                WalletTransaction.transaction_type == 'spend'
            )
            .group_by(WalletTransaction.reference_type)
            .all()
        )
        spending_breakdown = {s.reference_type or 'other': s.total for s in spending}

        return jsonify({
            'success': True,
            'wallet': wallet.to_dict(),
            'stats': {
                'daily_progress': {
                    'earned': wallet.daily_earnings,
                    'limit': wallet.daily_earning_limit,
                    'remaining': wallet.daily_earning_limit - wallet.daily_earnings,
                    'percentage': round(
                        (wallet.daily_earnings / wallet.daily_earning_limit) * 100, 1
                    ) if wallet.daily_earning_limit else 0
                },
                'earnings_breakdown': earnings_breakdown,
                'spending_breakdown': spending_breakdown,
                'net_balance': wallet.total_coins_earned - wallet.total_coins_spent
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500