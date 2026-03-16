"""
SF Collab — Readiness, Lifecycle & Execution Routes
Week 1 of the 2-week dev plan

Endpoints:
  GET  /api/ideas/<id>/readiness              — compute + return readiness score
  POST /api/ideas/<id>/vision-state           — set vision state manually
  GET  /api/startups/<id>/execution-score     — compute + return execution score
  POST /api/startups/<id>/lifecycle-state     — set lifecycle state manually
  POST /api/startups/<id>/record-activity     — record meaningful activity
  GET  /api/startups/<id>/crowdfunding-eligibility  — check unlock conditions
  POST /api/startups/<id>/unlock-crowdfunding — unlock crowdfunding if eligible
  POST /api/startups/<id>/complete-milestone  — record a completed milestone
  GET  /api/discovery/feed                    — filtered discovery feed
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.idea import Idea, VISION_STATES
from app.models.startup import Startup, STARTUP_LIFECYCLE_STATES
from app.models.user import User
from app.utils.helper import error_response, success_response, paginate
from sqlalchemy import desc, or_

readiness_bp = Blueprint('readiness', __name__)


# ============================================================================
# VISION READINESS
# ============================================================================

@readiness_bp.route('/ideas/<int:idea_id>/readiness', methods=['GET'])
@jwt_required()
def get_idea_readiness(idea_id):
    """
    Compute and return the Vision Readiness Score for an idea.
    Always recomputes from current state so it stays fresh.
    """
    try:
        idea = Idea.query.get(idea_id)
        if not idea:
            return error_response('Idea not found', 404)

        score = idea.compute_readiness_score()

        return success_response({
            'idea_id': idea_id,
            'readiness_score': score,
            'readiness_breakdown': idea.readiness_breakdown,
            'readiness_needs': idea.get_readiness_needs(),
            'vision_state': idea.vision_state,
            'team_size': idea.get_team_size(),
            'required_roles': idea.required_roles or [],
        })
    except Exception as e:
        return error_response(str(e), 500)


@readiness_bp.route('/ideas/<int:idea_id>/vision-state', methods=['POST'])
@jwt_required()
def set_vision_state(idea_id):
    """
    Manually set vision state (creator only).
    Use this to archive a vision or push it to team_forming.
    """
    try:
        current_user_id = int(get_jwt_identity())
        idea = Idea.query.get(idea_id)
        if not idea:
            return error_response('Idea not found', 404)

        if idea.creator_id != current_user_id:
            return error_response('Only the idea creator can change vision state', 403)

        data = request.get_json()
        new_state = data.get('vision_state')

        if not new_state:
            return error_response('vision_state is required', 400)

        if new_state not in VISION_STATES:
            return error_response(
                f'Invalid state. Must be one of: {", ".join(VISION_STATES)}', 400
            )

        old_state = idea.vision_state
        idea.set_vision_state(new_state)

        # Notify team members when vision becomes ready for activation
        if new_state == 'ready_for_activation' and old_state != new_state:
            try:
                from app.notifications.helpers import notify_info
                for member in idea.team_members.all():
                    notify_info(
                        user_id=idea.creator_id,
                        message=f"Your vision '{idea.title}' is now ready for startup activation! 🚀"
                    )
            except Exception:
                pass

        return success_response({
            'idea_id': idea_id,
            'vision_state': idea.vision_state,
            'readiness_score': idea.readiness_score,
        }, f'Vision state updated to {new_state}')

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@readiness_bp.route('/ideas/<int:idea_id>/vision-fields', methods=['PUT'])
@jwt_required()
def update_vision_fields(idea_id):
    """
    Update structured vision fields (problem_statement, outcome_goal,
    required_roles, roadmap_items, risk_level).
    These feed directly into the readiness score.
    """
    try:
        current_user_id = int(get_jwt_identity())
        idea = Idea.query.get(idea_id)
        if not idea:
            return error_response('Idea not found', 404)

        if idea.creator_id != current_user_id:
            return error_response('Only the idea creator can update vision fields', 403)

        data = request.get_json()

        if 'problem_statement' in data:
            idea.problem_statement = data['problem_statement']
        if 'outcome_goal' in data:
            idea.outcome_goal = data['outcome_goal']
        if 'risk_level' in data:
            if data['risk_level'] not in ('low', 'medium', 'high'):
                return error_response('risk_level must be low, medium, or high', 400)
            idea.risk_level = data['risk_level']
        if 'required_roles' in data:
            if not isinstance(data['required_roles'], list):
                return error_response('required_roles must be a list', 400)
            idea.required_roles = data['required_roles']
        if 'roadmap_items' in data:
            if not isinstance(data['roadmap_items'], list):
                return error_response('roadmap_items must be a list', 400)
            idea.roadmap_items = data['roadmap_items']

        db.session.commit()

        # Recompute readiness after fields change
        score = idea.compute_readiness_score()

        return success_response({
            'idea': idea.to_dict(user_id=current_user_id),
            'readiness_score': score,
            'readiness_needs': idea.get_readiness_needs(),
        }, 'Vision fields updated')

    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


# ============================================================================
# STARTUP EXECUTION SCORE & LIFECYCLE
# ============================================================================

@readiness_bp.route('/startups/<int:startup_id>/execution-score', methods=['GET'])
@jwt_required()
def get_execution_score(startup_id):
    """
    Compute and return the Execution Score for a startup.
    """
    try:
        startup = Startup.query.get(startup_id)
        if not startup:
            return error_response('Startup not found', 404)

        score = startup.compute_execution_score()
        active_members = startup.startup_members.filter_by(is_active=True).count()

        completion_rate = 0
        if startup.milestones_total and startup.milestones_total > 0:
            completion_rate = round(
                (startup.milestones_completed / startup.milestones_total) * 100, 1
            )

        return success_response({
            'startup_id': startup_id,
            'execution_score': score,
            'lifecycle_state': startup.lifecycle_state,
            'milestones_completed': startup.milestones_completed,
            'milestones_total': startup.milestones_total,
            'milestone_completion_rate': completion_rate,
            'active_builders': active_members,
            'last_activity_at': startup.last_activity_at.isoformat() if startup.last_activity_at else None,
        })
    except Exception as e:
        return error_response(str(e), 500)


@readiness_bp.route('/startups/<int:startup_id>/lifecycle-state', methods=['POST'])
@jwt_required()
def set_lifecycle_state(startup_id):
    """
    Manually set startup lifecycle state (creator only).
    For example: mark as 'launched' or 'archived'.
    """
    try:
        current_user_id = int(get_jwt_identity())
        startup = Startup.query.get(startup_id)
        if not startup:
            return error_response('Startup not found', 404)

        if startup.creator_id != current_user_id:
            return error_response('Only the startup creator can change lifecycle state', 403)

        data = request.get_json()
        new_state = data.get('lifecycle_state')

        if not new_state:
            return error_response('lifecycle_state is required', 400)

        if new_state not in STARTUP_LIFECYCLE_STATES:
            return error_response(
                f'Invalid state. Must be one of: {", ".join(STARTUP_LIFECYCLE_STATES)}', 400
            )

        old_state = startup.lifecycle_state
        startup.lifecycle_state = new_state
        db.session.commit()

        # Notify team members on key transitions
        if new_state == 'launched':
            try:
                from app.notifications.helpers import notify_startup_milestone
                member_ids = [m.user_id for m in startup.startup_members.filter_by(is_active=True).all()]
                for uid in member_ids:
                    notify_startup_milestone(
                        user_id=uid,
                        actor_id=current_user_id,
                        startup_name=startup.name,
                        startup_id=startup.id,
                        milestone_title='Startup Launched! 🚀'
                    )
            except Exception:
                pass

        return success_response({
            'startup_id': startup_id,
            'lifecycle_state': startup.lifecycle_state,
            'old_state': old_state,
        }, f'Lifecycle state updated to {new_state}')

    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@readiness_bp.route('/startups/<int:startup_id>/record-activity', methods=['POST'])
@jwt_required()
def record_startup_activity(startup_id):
    """
    Record a meaningful activity event on a startup.
    Prevents the startup from drifting into 'slowing' or 'dormant'.
    Called automatically by milestone completion, member join, etc.
    Can also be called explicitly by team members.
    """
    try:
        current_user_id = int(get_jwt_identity())
        startup = Startup.query.get(startup_id)
        if not startup:
            return error_response('Startup not found', 404)

        # Only team members can record activity
        from app.models.startUpMember import StartupMember
        is_member = StartupMember.query.filter_by(
            startup_id=startup_id, user_id=current_user_id, is_active=True
        ).first() or startup.creator_id == current_user_id

        if not is_member:
            return error_response('Only startup team members can record activity', 403)

        startup.record_activity()
        score = startup.compute_execution_score()

        return success_response({
            'startup_id': startup_id,
            'lifecycle_state': startup.lifecycle_state,
            'execution_score': score,
            'last_activity_at': startup.last_activity_at.isoformat(),
        }, 'Activity recorded')

    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@readiness_bp.route('/startups/<int:startup_id>/complete-milestone', methods=['POST'])
@jwt_required()
def complete_milestone(startup_id):
    """
    Record a completed milestone for a startup.
    This is the most important activity signal — it updates execution score,
    lifecycle state, activity timestamp, and optionally notifies team members.
    
    Body:
      { "milestone_title": "...", "total_milestones": 5 }  (total_milestones optional)
    """
    try:
        current_user_id = int(get_jwt_identity())
        startup = Startup.query.get(startup_id)
        if not startup:
            return error_response('Startup not found', 404)

        from app.models.startUpMember import StartupMember
        is_member = StartupMember.query.filter_by(
            startup_id=startup_id, user_id=current_user_id, is_active=True
        ).first() or startup.creator_id == current_user_id

        if not is_member:
            return error_response('Only team members can complete milestones', 403)

        data = request.get_json() or {}
        milestone_title = data.get('milestone_title', 'Milestone')
        new_total = data.get('total_milestones')

        # Update milestone counters
        startup.milestones_completed += 1
        if new_total is not None:
            startup.milestones_total = int(new_total)
        elif startup.milestones_total < startup.milestones_completed:
            startup.milestones_total = startup.milestones_completed

        startup.record_activity()
        score = startup.compute_execution_score()

        # Check if crowdfunding is now eligible
        crowdfunding_check = startup.check_crowdfunding_eligibility()

        # Auto-unlock crowdfunding if newly eligible
        if crowdfunding_check['eligible'] and not startup.crowdfunding_unlocked:
            try:
                startup.unlock_crowdfunding()
            except Exception:
                pass

        db.session.commit()

        # Notify all team members of milestone completion
        try:
            from app.notifications.helpers import notify_startup_milestone
            member_ids = [m.user_id for m in startup.startup_members.filter_by(is_active=True).all()]
            for uid in member_ids:
                if uid != current_user_id:
                    notify_startup_milestone(
                        user_id=uid,
                        actor_id=current_user_id,
                        startup_name=startup.name,
                        startup_id=startup.id,
                        milestone_title=milestone_title
                    )
        except Exception:
            pass

        return success_response({
            'startup_id': startup_id,
            'milestones_completed': startup.milestones_completed,
            'milestones_total': startup.milestones_total,
            'execution_score': score,
            'lifecycle_state': startup.lifecycle_state,
            'crowdfunding_unlocked': startup.crowdfunding_unlocked,
            'crowdfunding_newly_eligible': crowdfunding_check['eligible'],
        }, f'Milestone "{milestone_title}" completed!')

    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@readiness_bp.route('/startups/<int:startup_id>/crowdfunding-eligibility', methods=['GET'])
@jwt_required()
def get_crowdfunding_eligibility(startup_id):
    """Check whether this startup qualifies to unlock crowdfunding."""
    try:
        startup = Startup.query.get(startup_id)
        if not startup:
            return error_response('Startup not found', 404)

        check = startup.check_crowdfunding_eligibility()

        return success_response({
            'startup_id': startup_id,
            'eligible': check['eligible'],
            'reasons': check['reasons'],
            'already_unlocked': startup.crowdfunding_unlocked,
            'milestones_completed': startup.milestones_completed,
            'milestones_needed': max(0, 3 - startup.milestones_completed),
            'active_members': startup.startup_members.filter_by(is_active=True).count(),
            'days_active': (
                (db.session.execute(db.text('NOW()')).scalar() - startup.created_at).days
                if startup.created_at else 0
            ),
        })
    except Exception as e:
        return error_response(str(e), 500)


@readiness_bp.route('/startups/<int:startup_id>/unlock-crowdfunding', methods=['POST'])
@jwt_required()
def unlock_crowdfunding(startup_id):
    """Attempt to unlock crowdfunding for a startup (creator only)."""
    try:
        current_user_id = int(get_jwt_identity())
        startup = Startup.query.get(startup_id)
        if not startup:
            return error_response('Startup not found', 404)

        if startup.creator_id != current_user_id:
            return error_response('Only the startup creator can unlock crowdfunding', 403)

        if startup.crowdfunding_unlocked:
            return success_response({
                'startup_id': startup_id,
                'crowdfunding_unlocked': True,
                'unlocked_at': startup.crowdfunding_unlocked_at.isoformat() if startup.crowdfunding_unlocked_at else None,
            }, 'Crowdfunding already unlocked')

        startup.unlock_crowdfunding()

        # Notify team
        try:
            from app.notifications.helpers import notify_info
            member_ids = [m.user_id for m in startup.startup_members.filter_by(is_active=True).all()]
            for uid in member_ids:
                notify_info(
                    user_id=uid,
                    message=f"🎉 '{startup.name}' has unlocked crowdfunding! Your execution milestones paid off."
                )
        except Exception:
            pass

        return success_response({
            'startup_id': startup_id,
            'crowdfunding_unlocked': True,
            'unlocked_at': startup.crowdfunding_unlocked_at.isoformat(),
        }, 'Crowdfunding unlocked!')

    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


# ============================================================================
# DISCOVERY FEED (Week 2 Task 7)
# ============================================================================

@readiness_bp.route('/discovery/feed', methods=['GET'])
@jwt_required()
def get_discovery_feed(  ):
    """
    Opportunity discovery feed — shows:
      - Visions needing collaborators (team_forming, with open required_roles)
      - Startups actively recruiting
      - Startups with recent milestone completions
      - Fast-growing / high execution score startups

    Excludes:
      - founder_only drafts
      - dormant startups
      - archived visions
    
    Query params:
      - sector / industry (string)
      - type: 'visions' | 'startups' | 'all' (default: all)
      - page, per_page
    """
    try:
        current_user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        feed_type = request.args.get('type', 'all')
        industry = request.args.get('industry') or request.args.get('sector')

        feed = []

        # ── Visions needing collaborators ──────────────────────
        if feed_type in ('visions', 'all'):
            vision_query = Idea.query.filter(
                Idea.vision_state.in_(['public', 'team_forming', 'ready_for_activation']),
                Idea.status == 'active'
            )
            if industry:
                vision_query = vision_query.filter(Idea.industry.ilike(f'%{industry}%'))

            # Order by readiness score desc — highest traction first
            vision_query = vision_query.order_by(desc(Idea.readiness_score), desc(Idea.updated_at))

            visions = vision_query.limit(per_page // 2 if feed_type == 'all' else per_page).all()

            for idea in visions:
                item = idea.to_dict(user_id=current_user_id)
                item['feed_type'] = 'vision'
                item['feed_reason'] = _get_vision_feed_reason(idea)
                feed.append(item)

        # ── Startups ───────────────────────────────────────────
        if feed_type in ('startups', 'all'):
            startup_query = Startup.query.filter(
                Startup.lifecycle_state.in_(['active', 'recruiting']),
                Startup.status != 'deleted'
            )
            if industry:
                startup_query = startup_query.filter(Startup.industry.ilike(f'%{industry}%'))

            startup_query = startup_query.order_by(
                desc(Startup.execution_score),
                desc(Startup.last_activity_at)
            )

            startups = startup_query.limit(per_page // 2 if feed_type == 'all' else per_page).all()

            for startup in startups:
                item = startup.to_dict()
                item['feed_type'] = 'startup'
                item['feed_reason'] = _get_startup_feed_reason(startup)
                feed.append(item)

        # Sort combined feed: recruiting/high readiness first
        if feed_type == 'all':
            feed.sort(key=lambda x: (
                1 if x.get('lifecycleState') == 'recruiting' or x.get('visionState') == 'ready_for_activation' else 0,
                x.get('executionScore', 0) + x.get('readinessScore', 0) / 10
            ), reverse=True)

        return success_response({
            'feed': feed,
            'count': len(feed),
            'filters': {
                'type': feed_type,
                'industry': industry,
            }
        })

    except Exception as e:
        return error_response(str(e), 500)


def _get_vision_feed_reason(idea: Idea) -> str:
    """Human-readable reason this vision appears in the feed."""
    if idea.vision_state == 'ready_for_activation':
        return 'Ready for activation'
    if idea.required_roles:
        missing = idea.required_roles[:2]
        roles_str = ', '.join(r.replace('_', ' ') for r in missing)
        return f'Looking for: {roles_str}'
    if idea.readiness_score >= 60:
        return f'High readiness ({idea.readiness_score:.0f}%)'
    return 'Seeking collaborators'


def _get_startup_feed_reason(startup: Startup) -> str:
    """Human-readable reason this startup appears in the feed."""
    if startup.lifecycle_state == 'recruiting':
        return 'Actively recruiting'
    if startup.milestones_completed > 0:
        return f'{startup.milestones_completed} milestone{"s" if startup.milestones_completed > 1 else ""} completed'
    if startup.execution_score >= 7:
        return f'Execution score: {startup.execution_score}'
    return 'Active startup'