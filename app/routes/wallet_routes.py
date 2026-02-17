"""
Wallet Routes - Manage virtual currency

Endpoints:
- POST /api/wallet/add     - Add funds (earning)
- POST /api/wallet/deduct  - Deduct funds (spending)
- GET  /api/wallet         - Get wallet info
- GET  /api/wallet/transactions - Get transaction history
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.wallet_service import WalletService, DailyLimitExceeded
from app.utils.helper import error_response, success_response

wallet_bp = Blueprint('wallet', __name__)


@wallet_bp.route('/', methods=['GET'])
@jwt_required()
def get_wallet():
    """Get current user's wallet"""
    try:
        user_id = get_jwt_identity()
        wallet = WalletService.get_wallet(user_id)
        return success_response(wallet.to_dict(), 'Wallet retrieved', 200)
    except Exception as e:
        return error_response(f'Failed to get wallet: {str(e)}', 500)


@wallet_bp.route('/add', methods=['POST'])
@jwt_required()
def add_funds():
    """
    Add funds to wallet
    
    Body: { "amount": 100, "currency": "sf_coins", "reason": "daily_login" }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return error_response('Request body required', 400)
        
        amount = data.get('amount')
        currency = data.get('currency', 'sf_coins')
        reason = data.get('reason', 'manual')
        
        if not amount or amount <= 0:
            return error_response('Amount must be a positive integer', 400)
        
        valid_currencies = ['sf_coins', 'premium_gems', 'event_tokens']
        if currency not in valid_currencies:
            return error_response(f'Invalid currency. Use: {valid_currencies}', 400)
        
        wallet = WalletService.add_funds(
            user_id=user_id,
            amount=amount,
            currency_type=currency,
            transaction_type='reward',
            reference_type=reason,
            description=f"Earned {amount} {currency} via {reason}"
        )
        
        return success_response(wallet.to_dict(), f'Added {amount} {currency}', 200)
        
    except DailyLimitExceeded as e:
        return error_response(str(e), 429)
    except Exception as e:
        return error_response(f'Failed to add funds: {str(e)}', 500)


@wallet_bp.route('/deduct', methods=['POST'])
@jwt_required()
def deduct_funds():
    """
    Deduct funds from wallet
    
    Body: { "amount": 50, "currency": "sf_coins", "reason": "purchase" }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return error_response('Request body required', 400)
        
        amount = data.get('amount')
        currency = data.get('currency', 'sf_coins')
        reason = data.get('reason', 'purchase')
        
        if not amount or amount <= 0:
            return error_response('Amount must be a positive integer', 400)
        
        wallet = WalletService.deduct_funds(
            user_id=user_id,
            amount=amount,
            currency_type=currency,
            transaction_type='purchase',
            reference_type=reason,
            description=f"Spent {amount} {currency} on {reason}"
        )
        
        return success_response(wallet.to_dict(), f'Deducted {amount} {currency}', 200)
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Failed to deduct funds: {str(e)}', 500)


@wallet_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    """Get wallet transaction history with pagination"""
    try:
        user_id = get_jwt_identity()
        wallet = WalletService.get_wallet(user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        from app.models.wallet import WalletTransaction
        transactions = wallet.transactions.order_by(
            WalletTransaction.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return success_response({
            'transactions': [t.to_dict() for t in transactions.items],
            'total': transactions.total,
            'page': page,
            'pages': transactions.pages
        }, 'Transactions retrieved', 200)
        
    except Exception as e:
        return error_response(f'Failed to get transactions: {str(e)}', 500)
