import stripe
from flask import Blueprint, request, jsonify, current_app, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.transaction import Transaction
from app.extensions import db
from app.models.plan import Plan
from app.subscription_plans import PLANS
from app.models.user import User
payment_bp = Blueprint("payments", __name__, url_prefix="/payments")




@payment_bp.route("/plans", methods=["GET"])
def get_plans():
    plans = PLANS


    return jsonify([{
            "id": plan['id'],
            "title": plan['title'],
            "price": plan['price'] / 100,
            "interval": plan.get('interval'),
            "features": plan['features']
        } for plan in plans])
    # return jsonify([
    #     {
    #         "id": plan.id,
    #         "name": plan.name,
    #         "price": plan.price_cents / 100,
    #         "interval": plan.interval,
    #         "features": plan.features
    #     }
    #     for plan in plans
    # ]), 200

@payment_bp.route("/plans/<plan_id>", methods=["GET"])
def get_plan_by_id(plan_id):
    print(plan_id)
    for plan in PLANS:
        if plan['id'] == plan_id:
            return plan
    return None
@payment_bp.route("create-payment-intent", methods=["POST"] )
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
        confirm=True # Optional: automatically confirm the payment intent
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
            ui_mode="custom",
            metadata={
                "user_id": user_id,
                "plan_id": tier_id

            },
            
            # The URL of your payment completion page
            return_url=f"{current_app.config['FRONTEND_URL']}/checkout/return?session_id={{CHECKOUT_SESSION_ID}}",
        )
        return jsonify({
            'checkoutSessionClientSecret': session['client_secret']
        })
    except Exception as e:
        return jsonify(error=str(e)), 403
@payment_bp.route("/checkout-session/<session_id>", methods=["GET"])
@jwt_required()
def get_checkout_session(session_id):
    print("Retrieving session:", session_id)
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
        db.session.commit()
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

    # PaymentIntent succeeded
    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        user_id = intent["metadata"].get("user_id")
        plan_id = intent["metadata"].get("plan_id")

        # Save transaction
        from app.models.transaction import Transaction
        tx = Transaction(
            user_id=user_id,
            plan_id=plan_id,
            stripe_payment_intent_id=intent["id"],
            amount=intent["amount"],
            currency=intent["currency"],
            status=intent["status"]
        )
        db.session.add(tx)
        db.session.commit()

    return "", 200
