"""
Payment Routes with Notification Triggers
SF Collab Notification System - Section 4.7 Rewards & Payments
"""
import stripe
from flask import Blueprint, request, jsonify, current_app, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin
from app.models.transaction import Transaction
from app.extensions import db
from app.models.plan import Plan
from app.subscription_plans import PLANS
from app.models.user import User
from app.utils.helper import success_response, error_response

# Import notification helpers
from app.notifications.helpers import (
    notify_payment_sent,
    notify_payment_received,
    notify_points_earned,
    notify_contribution_verified
)

payment_bp = Blueprint("payments", __name__, url_prefix="/payments")


def get_user_full_name(user_id):
    """Helper to get user's full name"""
    user = User.query.get(user_id)
    if user:
        return f"{user.first_name or ''} {user.last_name or ''}".strip() or "Someone"
    return "Someone"


def format_amount(amount_cents, currency='usd'):
    """Format amount from cents to readable string"""
    amount = amount_cents / 100
    if currency.upper() == 'USD':
        return f"${amount:.2f}"
    return f"{amount:.2f} {currency.upper()}"


@payment_bp.route("/plans", methods=["GET"])
@cross_origin()
def get_plans():
    plans = PLANS

    type = request.args.get("type")
    if type:
        plans = list(filter(lambda p: p.get('category') == type, PLANS))
    return jsonify([{
            "title": plan['category'],
            "currency": plan.get('currency', 'usd'),
            "description": plan.get('description', ''),
            "roles": plan.get('roles', []),
        } for plan in plans])


@payment_bp.route("/plans/<plan_id>", methods=["GET"])
def get_plan_by_id(plan_id):
    # Loop over all categories
    for category in PLANS:
        # 1️⃣ Check roles -> tiers (crowdfunding, standard)
        if 'roles' in category:
            for role in category['roles']:
                for tier in role.get('tiers', []):
                    if tier.get('id') == plan_id:
                        result = tier.copy()
                        result['category'] = category.get('category')
                        result['role'] = role.get('role')
                        return jsonify(result)

        # 2️⃣ Check ai-tools -> tools
        if 'tools' in category:
            for tool in category['tools']:
                if tool.get('id') == plan_id:
                    result = tool.copy()
                    result['category'] = category.get('category')
                    return jsonify(result)

        # 3️⃣ Check extras -> extras -> items
        if 'extras' in category:
            for extra_group in category['extras']:
                for item in extra_group.get('items', []):
                    if item.get('id') == plan_id:
                        result = item.copy()
                        result['category'] = category.get('category')
                        result['extra_group'] = extra_group.get('title')
                        return jsonify(result)

        # 4️⃣ Check credits -> credit_packs
        if 'credit_packs' in category:
            for pack in category['credit_packs']:
                if pack.get('id') == plan_id:
                    result = pack.copy()
                    result['category'] = category.get('category')
                    return jsonify(result)

        # 5️⃣ Check credits -> topups
        if 'topups' in category:
            for topup in category['topups']:
                if topup.get('id') == plan_id:
                    result = topup.copy()
                    result['category'] = category.get('category')
                    return jsonify(result)

    # Not found
    return jsonify({"error": "Plan not found"}), 404


@payment_bp.route("create-payment-intent", methods=["POST"])
@jwt_required()
def create_payment_intent():
    data = request.get_json()
    price_id = data.get("priceId")

    plan = next((plan for plan in PLANS if plan['stripe_price_id'] == price_id), None)
    if not plan:
        return jsonify({"error": "Invalid price ID"}), 400

    intent = stripe.PaymentIntent.create(
        amount=plan['price'],
        currency=plan['currency'],
        metadata={
            "integration_check": "accept_a_payment",
            "user_id": get_jwt_identity(),
            "plan_id": plan['id']
            },
        return_url=current_app.config['FRONTEND_URL'] + '/checkout/success',
        confirm=True
    )

    return jsonify({
        "clientSecret": intent.client_secret
    }), 200


@payment_bp.route('/create-checkout-session', methods=['POST'])
def checkout():
    try:
        data = request.get_json()
        currency = data.get('currency', 'usd')
        tier_id = data.get('id')
        user_id = data.get('user_id')
        product = data.get('title')
        amount = data.get('price')  # amount in cents
        description = data.get('description', '')
        option = data.get('option', None)
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                    "currency": currency,
                    "product_data": {"name": product},
                    "unit_amount": amount,
                },
                "quantity": 1,
                },
            ],
            mode="payment",
            ui_mode="hosted",
            metadata={
                "user_id": user_id,
                "plan_id": tier_id,
                "option": str(option) if option else "",
            },
            # The URL of your payment completion page
            success_url=f"{current_app.config['FRONTEND_URL']}/checkout/return?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{current_app.config['FRONTEND_URL']}/checkout/cancel",
        )
        return jsonify({
            'checkoutSessionClientSecret': session['client_secret'],
            'url': session['url'],
            'success': True
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@payment_bp.route("/checkout-session/<session_id>", methods=["GET"])
def get_checkout_session(session_id):
    session = stripe.checkout.Session.retrieve(session_id)
    return jsonify(session)


@payment_bp.route("/record-transaction", methods=["POST"])
@jwt_required()
def record_transaction():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        plan_id = data.get("plan_id")
        amount = data.get("amount")
        currency = data.get("currency")
        type = data.get("type", "subscription")

        if type not in ["subscription", "donation"]:
            return jsonify({"error": "Invalid transaction type"}), 400
        
        if type == "subscription":
            stripe_payment_intent_id = data.get("stripe_payment_intent_id")
            if not all([user_id, plan_id, amount, currency, stripe_payment_intent_id]):
                return jsonify({"error": "Missing required fields"}), 400
            existing_tx = Transaction.query.filter_by(stripe_payment_intent_id=stripe_payment_intent_id).first()
            if existing_tx:
                return jsonify({"error": "Transaction already recorded"}), 400
            transaction = Transaction(
                user_id=user_id,
                plan_id=plan_id,
                amount=amount,
                currency=currency,
                stripe_payment_intent_id=stripe_payment_intent_id,
                status="completed"
            )

            # Update user's plan here if needed
            user = User.query.get(user_id)
            if user:
                user.plan_id = plan_id
            db.session.add(transaction)
            
        elif type == "donation":
            stripe_checkout_session_id = data.get("stripe_checkout_session_id")
            if not all([user_id, amount, currency, stripe_checkout_session_id]):
                return jsonify({"error": "Missing required fields for donation"}), 400
            existing_tx = Transaction.query.filter_by(stripe_checkout_session_id=stripe_checkout_session_id).first()
            if existing_tx:
                return jsonify({"error": "Donation transaction already recorded"}), 400
            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                currency=currency,
                stripe_checkout_session_id=stripe_checkout_session_id,
                status="completed",
                type="donation"
            )
            db.session.add(transaction)
        
        db.session.commit()
        
        # ════════════════════════════════════════════════════════════
        # ✨ NOTIFICATION: Payment Sent/Received (4.7)
        # ════════════════════════════════════════════════════════════
        try:
            amount_str = format_amount(amount, currency)
            
            # Notify user their payment was processed
            notify_payment_sent(
                user_id=user_id,
                amount=amount_str,
                recipient="SF Collab",
                payment_id=transaction.id
            )
            
            # If donation, also notify as contribution
            if type == "donation":
                notify_contribution_verified(
                    user_id=user_id,
                    project="SF Collab Platform",
                    contribution_id=transaction.id
                )
        except Exception as e:
            print(f"⚠️ Payment notification failed: {e}")
        
        return jsonify({
            "success": True,
            "message": "Transaction recorded successfully",
            "transaction_id": transaction.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@payment_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = current_app.config["STRIPE_WEBHOOK_SECRET"]

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception:
        return "", 400

    # ✅ Stripe Checkout completed
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        user_id = session["metadata"].get("user_id")
        tx_type = session["metadata"].get("type", "subscription")

        # Idempotency check
        existing = Transaction.query.filter_by(
            stripe_checkout_session_id=session["id"]
        ).first()
        if existing:
            return "", 200

        tx = Transaction(
            user_id=user_id,
            plan_id=session["metadata"].get("plan_id"),
            amount=session["amount_total"],
            currency=session["currency"],
            stripe_checkout_session_id=session["id"],
            status="completed",
            type=tx_type,
        )

        db.session.add(tx)

        # Update plan if subscription
        if tx_type == "subscription":
            user = User.query.get(user_id)
            if user:
                user.plan_id = session["metadata"].get("plan_id")

        db.session.commit()
        
        # ════════════════════════════════════════════════════════════
        # ✨ NOTIFICATION: Payment via Webhook (4.7)
        # ════════════════════════════════════════════════════════════
        try:
            if user_id:
                amount_str = format_amount(session["amount_total"], session["currency"])
                
                notify_payment_sent(
                    user_id=int(user_id),
                    amount=amount_str,
                    recipient="SF Collab",
                    payment_id=tx.id
                )
                
                # Award points for payments
                if tx_type == "donation":
                    notify_points_earned(
                        user_id=int(user_id),
                        points=100,
                        reason="Donation to SF Collab"
                    )
                elif tx_type == "crowdfunding":
                    notify_points_earned(
                        user_id=int(user_id),
                        points=250,
                        reason="Crowdfunding contribution"
                    )
        except Exception as e:
            print(f"⚠️ Webhook payment notification failed: {e}")

    return "", 200


@payment_bp.route("/create-donation-session", methods=["POST", "OPTIONS"])
@jwt_required()
def create_donation_session():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    data = request.get_json()
    amount = data.get("amount")
    user_id = get_jwt_identity()
    email = data.get("email")
    name = data.get("name")
    message = data.get("message")
    if not all([amount, user_id, email]):
        return jsonify({"error": "Missing required fields"}), 400
    
    session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                    "currency": 'usd',
                    "product_data": {"name": 'Donation'},
                    "unit_amount": amount,
                },
                "quantity": 1,
                },
            ],
            mode="payment",
            ui_mode="hosted",
            metadata={
                "user_id": user_id,
                "message": message,
                "name": name,
                "type": "donation"
            },
            success_url=f"{current_app.config['FRONTEND_URL']}/checkout/return?session_id={{CHECKOUT_SESSION_ID}}?donation=true",
            cancel_url=f"{current_app.config['FRONTEND_URL']}/donate",
        )
    return jsonify({
        'checkoutSessionClientSecret': session['client_secret'],
        'url': session['url'],
        'success': True
    })


@payment_bp.route("/total-donations", methods=["GET"])
@jwt_required()
def get_total_donations():
    total = db.session.query(db.func.sum(Transaction.amount)).filter_by(type="donation", status="completed").scalar()
    return success_response({"total_donations": total or 0})


@payment_bp.route("/donations", methods=["GET"])
@jwt_required()
def get_donations():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Transaction.query.filter_by(type="donation", status="completed")
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    result = []
    for donation in paginated.items:
        user = User.query.get(donation.user_id)
        result.append({
            "id": donation.id,
            "user": {
                "id": user.id,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "email": user.email
            } if user else None,
            "message": donation.donation_message,
            "amount": donation.amount,
            "currency": donation.currency,
            "createdAt": donation.created_at.isoformat()
        })
    
    return success_response({
        "donations": result,
        "pagination": {
            "page": paginated.page,
            "per_page": paginated.per_page,
            "total": paginated.total,
            "pages": paginated.pages
        }
    })


@payment_bp.route("/total-crowdfunding", methods=["GET"])
@jwt_required()
def get_total_crowdfunding():
    total = db.session.query(db.func.sum(Transaction.amount)).filter_by(type="crowdfunding", status="completed").scalar()
    return success_response({"total_crowdfunding": total or 0})


@payment_bp.route("/crowdfunding", methods=["GET"])
@jwt_required()
def get_crowdfunding_transactions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Transaction.query.filter_by(type="crowdfunding", status="completed")
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    result = []
    for tx in paginated.items:
        user = User.query.get(tx.user_id)
        result.append({
            "id": tx.id,
            "user": {
                "id": user.id,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "email": user.email
            } if user else None,
            "amount": tx.amount,
            "planId": tx.plan_id,
            "currency": tx.currency,
            "createdAt": tx.created_at.isoformat()
        })
    return success_response({
        "crowdfunding_transactions": result,
        "pagination": {
            "page": paginated.page,
            "per_page": paginated.per_page,
            "total": paginated.total,
            "pages": paginated.pages
        }
    })


@payment_bp.route("/credits", methods=["GET"])
@jwt_required()
def get_credits():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return error_response("User not found", 404)
    return success_response({"credits": user.credits})