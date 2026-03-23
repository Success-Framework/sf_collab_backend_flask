"""
Migration: Add SF Economy Tables
=================================
Adds the following new tables (does NOT modify any existing tables):

  balances               — real-money wallet per user
  balance_transactions   — immutable audit log for Balance movements
  escrow_transactions    — milestone payment escrow
  crystal_wallets        — crystal balance per user
  crystal_transactions   — audit log for crystal movements
  visibility_boosts      — active/expired visibility boost records

Run with:
  flask db upgrade

Rollback with:
  flask db downgrade
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# Alembic revision identifiers
revision = '001_sf_economy'
down_revision = ('9198f8997faf', 'ee78359866cc')  # merges all existing heads
branch_labels = None
depends_on = None


def upgrade():
    # ----------------------------------------------------------------
    # 1. balances — real-money wallet (one per user)
    # ----------------------------------------------------------------
    op.create_table(
        'balances',
        sa.Column('id',               sa.Integer,     primary_key=True),
        sa.Column('user_id',          sa.Integer,     sa.ForeignKey('users.id'), unique=True, nullable=False),
        sa.Column('available',        sa.Integer,     default=0, nullable=False),
        sa.Column('pending',          sa.Integer,     default=0, nullable=False),
        sa.Column('escrow_locked',    sa.Integer,     default=0, nullable=False),
        sa.Column('total_deposited',  sa.Integer,     default=0, nullable=False),
        sa.Column('total_withdrawn',  sa.Integer,     default=0, nullable=False),
        sa.Column('total_paid_out',   sa.Integer,     default=0, nullable=False),
        sa.Column('currency',         sa.String(3),   default='USD', nullable=False),
        sa.Column('created_at',       sa.DateTime,    default=datetime.utcnow),
        sa.Column('updated_at',       sa.DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow),
    )
    op.create_index('ix_balances_user_id', 'balances', ['user_id'])

    # ----------------------------------------------------------------
    # 2. balance_transactions — immutable audit log
    # ----------------------------------------------------------------
    op.create_table(
        'balance_transactions',
        sa.Column('id',                 sa.Integer,     primary_key=True),
        sa.Column('balance_id',         sa.Integer,     sa.ForeignKey('balances.id'), nullable=False),
        sa.Column('user_id',            sa.Integer,     sa.ForeignKey('users.id'), nullable=False),
        sa.Column('tx_type',            sa.String(30),  nullable=False),
        sa.Column('amount',             sa.Integer,     nullable=False),
        sa.Column('balance_before',     sa.Integer,     nullable=False),
        sa.Column('balance_after',      sa.Integer,     nullable=False),
        sa.Column('status',             sa.String(20),  default='completed'),
        sa.Column('reference_type',     sa.String(50),  nullable=True),
        sa.Column('reference_id',       sa.String(255), nullable=True),
        sa.Column('description',        sa.Text,        nullable=True),
        sa.Column('stripe_payment_id',  sa.String(255), nullable=True),
        sa.Column('created_at',         sa.DateTime,    default=datetime.utcnow),
    )
    op.create_index('ix_balance_transactions_balance_id', 'balance_transactions', ['balance_id'])
    op.create_index('ix_balance_transactions_user_id',    'balance_transactions', ['user_id'])

    # ----------------------------------------------------------------
    # 3. escrow_transactions — milestone payment escrow
    # ----------------------------------------------------------------
    op.create_table(
        'escrow_transactions',
        sa.Column('id',                 sa.Integer,     primary_key=True),
        sa.Column('payer_id',           sa.Integer,     sa.ForeignKey('users.id'), nullable=False),
        sa.Column('payee_id',           sa.Integer,     sa.ForeignKey('users.id'), nullable=False),
        sa.Column('payer_balance_id',   sa.Integer,     sa.ForeignKey('balances.id'), nullable=False),
        sa.Column('payee_balance_id',   sa.Integer,     sa.ForeignKey('balances.id'), nullable=True),
        sa.Column('amount_cents',       sa.Integer,     nullable=False),
        sa.Column('currency',           sa.String(3),   default='USD', nullable=False),
        sa.Column('reference_type',     sa.String(50),  nullable=True),
        sa.Column('reference_id',       sa.String(255), nullable=True),
        sa.Column('title',              sa.String(255), nullable=True),
        sa.Column('description',        sa.Text,        nullable=True),
        sa.Column('status',             sa.String(30),  default='created', nullable=False),
        sa.Column('due_date',           sa.DateTime,    nullable=True),
        sa.Column('funded_at',          sa.DateTime,    nullable=True),
        sa.Column('completed_at',       sa.DateTime,    nullable=True),
        sa.Column('approved_at',        sa.DateTime,    nullable=True),
        sa.Column('released_at',        sa.DateTime,    nullable=True),
        sa.Column('disputed_at',        sa.DateTime,    nullable=True),
        sa.Column('cancelled_at',       sa.DateTime,    nullable=True),
        sa.Column('resolution_note',    sa.Text,        nullable=True),
        sa.Column('resolved_by',        sa.Integer,     sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at',         sa.DateTime,    default=datetime.utcnow),
        sa.Column('updated_at',         sa.DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow),
    )
    op.create_index('ix_escrow_payer_id',  'escrow_transactions', ['payer_id'])
    op.create_index('ix_escrow_payee_id',  'escrow_transactions', ['payee_id'])
    op.create_index('ix_escrow_status',    'escrow_transactions', ['status'])

    # ----------------------------------------------------------------
    # 4. crystal_wallets — one per user
    # ----------------------------------------------------------------
    op.create_table(
        'crystal_wallets',
        sa.Column('id',           sa.Integer,  primary_key=True),
        sa.Column('user_id',      sa.Integer,  sa.ForeignKey('users.id'), unique=True, nullable=False),
        sa.Column('balance',      sa.Integer,  default=0, nullable=False),
        sa.Column('total_earned', sa.Integer,  default=0, nullable=False),
        sa.Column('total_spent',  sa.Integer,  default=0, nullable=False),
        sa.Column('created_at',   sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at',   sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    )
    op.create_index('ix_crystal_wallets_user_id', 'crystal_wallets', ['user_id'])

    # ----------------------------------------------------------------
    # 5. crystal_transactions — immutable audit log
    # ----------------------------------------------------------------
    op.create_table(
        'crystal_transactions',
        sa.Column('id',                 sa.Integer,     primary_key=True),
        sa.Column('crystal_wallet_id',  sa.Integer,     sa.ForeignKey('crystal_wallets.id'), nullable=False),
        sa.Column('user_id',            sa.Integer,     sa.ForeignKey('users.id'), nullable=False),
        sa.Column('direction',          sa.String(6),   nullable=False),
        sa.Column('usage_type',         sa.String(30),  nullable=False),
        sa.Column('amount',             sa.Integer,     nullable=False),
        sa.Column('balance_before',     sa.Integer,     nullable=False),
        sa.Column('balance_after',      sa.Integer,     nullable=False),
        sa.Column('reference_id',       sa.String(255), nullable=True),
        sa.Column('description',        sa.Text,        nullable=True),
        sa.Column('created_at',         sa.DateTime,    default=datetime.utcnow),
    )
    op.create_index('ix_crystal_transactions_wallet_id', 'crystal_transactions', ['crystal_wallet_id'])
    op.create_index('ix_crystal_transactions_user_id',   'crystal_transactions', ['user_id'])

    # ----------------------------------------------------------------
    # 6. visibility_boosts — active/expired boost records
    # ----------------------------------------------------------------
    op.create_table(
        'visibility_boosts',
        sa.Column('id',                 sa.Integer,     primary_key=True),
        sa.Column('user_id',            sa.Integer,     sa.ForeignKey('users.id'), nullable=False),
        sa.Column('crystal_wallet_id',  sa.Integer,     sa.ForeignKey('crystal_wallets.id'), nullable=False),
        sa.Column('boost_type',         sa.String(30),  nullable=False),
        sa.Column('crystals_spent',     sa.Integer,     nullable=False),
        sa.Column('target_type',        sa.String(50),  nullable=True),
        sa.Column('target_id',          sa.String(255), nullable=True),
        sa.Column('duration_hours',     sa.Integer,     default=24, nullable=False),
        sa.Column('started_at',         sa.DateTime,    default=datetime.utcnow),
        sa.Column('expires_at',         sa.DateTime,    nullable=False),
        sa.Column('is_active',          sa.Boolean,     default=True),
        sa.Column('created_at',         sa.DateTime,    default=datetime.utcnow),
    )
    op.create_index('ix_visibility_boosts_user_id',    'visibility_boosts', ['user_id'])
    op.create_index('ix_visibility_boosts_is_active',  'visibility_boosts', ['is_active'])
    op.create_index('ix_visibility_boosts_expires_at', 'visibility_boosts', ['expires_at'])


def downgrade():
    # Drop in reverse dependency order
    op.drop_table('visibility_boosts')
    op.drop_table('crystal_transactions')
    op.drop_table('crystal_wallets')
    op.drop_table('escrow_transactions')
    op.drop_table('balance_transactions')
    op.drop_table('balances')