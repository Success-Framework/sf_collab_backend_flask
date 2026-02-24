"""
Calendar Event Routes with Notification Triggers
SF Collab Notification System - Section 4.12 Events & Reminders
"""
from flask import Blueprint, request, jsonify, send_file, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app.models.calendarEvent import CalendarEvent
from app.models.user import User
from app.models.startUpMember import StartupMember
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

# Import notification helpers
from app.notifications.helpers import (
    notify_event_created,
    notify_event_reminder,
    notify_event_starting_soon,
    notify_event_canceled,
    notify_meeting_scheduled,
    notify_meeting_updated,
    notify_meeting_canceled,
    notify_deadline_reminder
)

calendar_events_bp = Blueprint('calendar_events', __name__)


def get_user_full_name(user_id):
    """Helper to get user's full name"""
    user = User.query.get(user_id)
    if user:
        return f"{user.first_name or ''} {user.last_name or ''}".strip() or "Someone"
    return "Someone"

def has_calendar_event_visibility_access(user_id, event):
    """Check if user has visibility access to task based on visibility settings"""
    # Admin always has access
    if event.parent_startup is not None and event.parent_startup.creator_id == int(user_id):
        return True
    # Owner always has access

    if int(event.user_id) == int(user_id):
        return True
    
    # Check visibility settings
    if event.visible_by == 'private':
        return False
    
    if event.visible_by == 'team' and event.startup_id:
        # Check if user is part of the startup team
        return is_user_on_startup_team(user_id, event.startup_id)
    
    if event.visible_by == 'all' or event.visible_by == 'public':
        return True
    
    return False
def is_user_on_startup_team(user_id, startup_id):
    """Check if user is a member of the startup team"""
    
    membership = StartupMember.query.filter_by(
        user_id=user_id,
        startup_id=startup_id
    ).first()
    return membership is not None
def get_startup_member_ids(startup_id):
    """Get list of user IDs who are members of a startup"""
    members = StartupMember.query.filter_by(startup_id=startup_id).all()
    return [m.user_id for m in members if m.user_id]


def format_event_date(event):
    """Format event date for notification"""
    if event.all_day:
        return event.start_date.strftime("%A, %B %d, %Y")
    return event.start_date.strftime("%A, %B %d at %I:%M %p")


@calendar_events_bp.route('', methods=['GET'])
@jwt_required()
def get_calendar_events():
    """Get all calendar events with filtering"""
    current_user_id = get_jwt_identity()
    print(f"🔍 [get_calendar_events] Starting - current_user_id: {current_user_id}")
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    user_id = request.args.get('user_id', type=int)
    startup_id = request.args.get('startup_id', type=int)
    category = request.args.get('category', type=str)
    start_date = request.args.get('start_date', type=str)
    end_date = request.args.get('end_date', type=str)
    upcoming_only = request.args.get('upcoming_only', 'false').lower() == 'true'
    
    print(f"📋 [get_calendar_events] Query params - page: {page}, per_page: {per_page}, user_id: {user_id}, startup_id: {startup_id}, category: {category}, upcoming_only: {upcoming_only}")
    
    # Default to current user's events if no user_id specified
    query = CalendarEvent.query
    if not user_id and not startup_id:
        user_id = current_user_id
        query = query.filter(CalendarEvent.user_id == user_id)
    print(f"🔎 [get_calendar_events] Initial query filter applied for user_id: {user_id}, items count: {query.count()}")
    
    if startup_id:
        # Check if user has access to this startup
        query = query.filter(CalendarEvent.startup_id == startup_id)
        print(f"🏢 [get_calendar_events] Startup filter applied - startup_id: {startup_id}, items count: {query.count()}")
    
    if category:
        query = query.filter(CalendarEvent.category == category)
        print(f"🏷️ [get_calendar_events] Category filter applied - category: {category}, items count: {query.count()}")
    
    if start_date:
        start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        query = query.filter(CalendarEvent.start_date >= start_datetime)
        print(f"📅 [get_calendar_events] Start date filter applied - start_date: {start_datetime}, items count: {query.count()}")
    
    if end_date:
        end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        query = query.filter(CalendarEvent.start_date <= end_datetime)
        print(f"📅 [get_calendar_events] End date filter applied - end_date: {end_datetime}, items count: {query.count()}")
    
    if upcoming_only:
        now = datetime.utcnow()
        query = query.filter(CalendarEvent.start_date >= now)
        print(f"⏰ [get_calendar_events] Upcoming only filter applied - current time: {now}, items count: {query.count()}")
    
    result = paginate(query.order_by(CalendarEvent.start_date.asc()), page, per_page)
    print(f"📊 [get_calendar_events] Paginated result - total: {result['total']}, items in page: {len(result['items'])}")
    print(f"📦 [get_calendar_events] Events data: {[event.to_dict() for event in result['items']]}")
    
    filtered_events = []
    print(f"🔐 [get_calendar_events] Starting visibility check for {len(result['items'])} events")
    
    for idx, event in enumerate(result['items']):
        has_access = has_calendar_event_visibility_access(current_user_id, event)
        print(f"  ✓ Event {idx} (id: {event.id}, title: '{event.title}') - visibility: {event.visible_by}, user has access: {has_access}")
        
        if has_access:
            filtered_events.append(event)
            print(f"    ✅ Event added to filtered list")
        else:
            print(f"    ❌ Event filtered out - insufficient access")
    
    print(f"✨ [get_calendar_events] Final result - filtered_events: {len(filtered_events)} / {len(result['items'])}")
    
    return success_response({
        'events': [event.to_dict() for event in filtered_events],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })


@calendar_events_bp.route('/<int:event_id>', methods=['GET'])
@jwt_required()
def get_calendar_event(event_id):
    """Get single calendar event by ID"""
    current_user_id = get_jwt_identity()
    
    event = CalendarEvent.query.get(event_id)
    if not event:
        return error_response('Calendar event not found', 404)
    
    # Check if user is authorized to view this event
    if event.user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user:
            return error_response('Unauthorized to view this calendar event', 403)
    
    return success_response({'event': event.to_dict()})


@calendar_events_bp.route('', methods=['POST'])
@jwt_required()
def create_calendar_event():
    """Create new calendar event"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['title', 'start_date']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: title, start_date')
    
    # Users can only create events for themselves unless they're admin
    user_id = data.get('user_id', current_user_id)
    if user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user:
            return error_response('Unauthorized to create events for other users', 403)
    
    # Check startup access if startup_id is provided
    startup_id = data.get('startup_id')
    if startup_id and not has_startup_access(current_user_id, startup_id):
        return error_response('Unauthorized to create events for this startup', 403)
    try:
        event = CalendarEvent(
            user_id=user_id,
            startup_id=startup_id,
            title=data['title'],
            description=data.get('description'),
            start_date=datetime.fromisoformat(data['start_date'].replace('Z', '+00:00')),
            end_date=datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')) if data.get('end_date') else None,
            all_day=data.get('all_day', False),
            link=data.get('link', None),
            category=data.get('category', 'event'),
            color=data.get('color'),
            location=data.get('location'),
            is_recurring=data.get('is_recurring', False),
            recurrence_rule=data.get('recurrence_rule'),
            reminder_minutes=data.get('reminder_minutes', 30),
            visible_by=data.get('visible_by', 'team')
        )
        
        db.session.add(event)
        db.session.commit()
        
        # ════════════════════════════════════════════════════════════
        # ✨ NOTIFICATION: Event/Meeting Created (4.12)
        # ════════════════════════════════════════════════════════════
        try:
            event_date_str = format_event_date(event)
            category = data.get('category', 'event')
            
            # If it's a startup event, notify all startup members
            if startup_id:
                member_ids = get_startup_member_ids(startup_id)
                # Exclude the creator from notifications
                member_ids = [m_id for m_id in member_ids if m_id != current_user_id]
                
                if member_ids:
                    if category == 'meeting':
                        notify_meeting_scheduled(
                            user_ids=member_ids,
                            meeting_title=event.title,
                            meeting_id=event.id,
                            date=event_date_str
                        )
                    else:
                        notify_event_created(
                            user_ids=member_ids,
                            event_title=event.title,
                            event_id=event.id,
                            date=event_date_str
                        )
            
            # Notify the user who created the event as confirmation
            if category == 'meeting':
                notify_meeting_scheduled(
                    user_ids=[user_id],
                    meeting_title=event.title,
                    meeting_id=event.id,
                    date=event_date_str
                )
            else:
                notify_event_created(
                    user_ids=[user_id],
                    event_title=event.title,
                    event_id=event.id,
                    date=event_date_str
                )
        except Exception as e:
            print(f"⚠️ Event creation notification failed: {e}")
        
        return success_response({
            'event': event.to_dict()
        }, 'Calendar event created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create calendar event: {str(e)}', 500)


@calendar_events_bp.route('/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_calendar_event(event_id):
    """Update calendar event"""
    current_user_id = get_jwt_identity()
    
    event = CalendarEvent.query.get(event_id)
    if not event:
        return error_response('Calendar event not found', 404)
    
    # Check if user is authorized to update this event
    if int(event.user_id) != int(current_user_id):
        return error_response('Unauthorized to update this calendar event', 403)
    
    data = request.get_json()
    old_title = event.title
    old_start_date = event.start_date
    
    try:
        if 'title' in data:
            event.title = data['title']
        if 'description' in data:
            event.description = data['description']
        if 'start_date' in data:
            event.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        if 'end_date' in data:
            event.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')) if data['end_date'] else None
        if 'all_day' in data:
            event.all_day = data['all_day']
        if 'category' in data:
            event.category = data['category']
        if 'color' in data:
            event.color = data['color']
        if 'location' in data:
            event.location = data['location']
        if 'reminder_minutes' in data:
            event.reminder_minutes = data['reminder_minutes']
        
        db.session.commit()
        
        # ════════════════════════════════════════════════════════════
        # ✨ NOTIFICATION: Event/Meeting Updated (4.12)
        # ════════════════════════════════════════════════════════════
        # Notify if significant changes (title or date changed)
        if event.startup_id and (old_title != event.title or old_start_date != event.start_date):
            try:
                member_ids = get_startup_member_ids(event.startup_id)
                member_ids = [m_id for m_id in member_ids if m_id != current_user_id]
                
                if member_ids:
                    if event.category == 'meeting':
                        notify_meeting_updated(
                            user_ids=member_ids,
                            meeting_title=event.title,
                            meeting_id=event.id
                        )
                    # For other events, could add notify_event_updated if needed
            except Exception as e:
                print(f"⚠️ Event update notification failed: {e}")
        
        return success_response({
            'event': event.to_dict()
        }, 'Calendar event updated successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update calendar event: {str(e)}', 500)


@calendar_events_bp.route('/<int:event_id>/dates', methods=['PUT'])
@jwt_required()
def update_event_dates(event_id):
    """Update event dates"""
    current_user_id = get_jwt_identity()
    
    event = CalendarEvent.query.get(event_id)
    if not event:
        return error_response('Calendar event not found', 404)
    
    # Check if user is authorized to update this event
    if event.user_id != current_user_id:
        return error_response('Unauthorized to update this calendar event', 403)
    
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    all_day = data.get('all_day', event.all_day)
    
    if not start_date:
        return error_response('Start date is required', 400)
    
    try:
        event.update_dates(
            start_date=datetime.fromisoformat(start_date.replace('Z', '+00:00')),
            end_date=datetime.fromisoformat(end_date.replace('Z', '+00:00')) if end_date else None,
            all_day=all_day
        )
        return success_response({
            'event': event.to_dict()
        }, 'Event dates updated successfully')
    except Exception as e:
        return error_response(f'Failed to update event dates: {str(e)}', 500)


@calendar_events_bp.route('/upcoming', methods=['GET'])
@jwt_required()
def get_upcoming_events():
    """Get upcoming events that need reminders"""
    current_user_id = get_jwt_identity()
    
    user_id = request.args.get('user_id', type=int)
    hours_ahead = request.args.get('hours_ahead', 24, type=int)
    
    # Default to current user if no user_id specified
    if not user_id:
        user_id = current_user_id
    
    # Check if user is authorized to view other users' upcoming events
    if user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user:
            return error_response('Unauthorized to view other users upcoming events', 403)
    
    now = datetime.utcnow()
    reminder_cutoff = now + timedelta(hours=hours_ahead)
    
    query = CalendarEvent.query.filter(
        CalendarEvent.user_id == user_id,
        CalendarEvent.start_date <= reminder_cutoff,
        CalendarEvent.start_date >= now,
        CalendarEvent.reminder_minutes > 0
    )
    
    events = query.order_by(CalendarEvent.start_date.asc()).all()
    
    # Filter events that should remind now
    events_to_remind = [event for event in events if event.should_remind()]
    
    return success_response({
        'upcoming_events': [event.to_dict() for event in events],
        'events_to_remind': [event.to_dict() for event in events_to_remind],
        'total_upcoming': len(events),
        'total_to_remind': len(events_to_remind)
    })


@calendar_events_bp.route('/send-reminders', methods=['POST'])
@jwt_required()
def send_event_reminders():
    """Send reminders for upcoming events (typically called by a scheduled job)"""
    current_user_id = get_jwt_identity()
    
    # This endpoint should be protected (admin only in production)
    now = datetime.utcnow()
    
    # Get events starting in the next hour that haven't had reminders sent
    upcoming_events = CalendarEvent.query.filter(
        CalendarEvent.start_date >= now,
        CalendarEvent.start_date <= now + timedelta(hours=1),
        CalendarEvent.reminder_minutes > 0
    ).all()
    
    reminders_sent = 0
    
    for event in upcoming_events:
        time_until = event.start_date - now
        minutes_until = int(time_until.total_seconds() / 60)
        
        # Send reminder if within the reminder window
        if minutes_until <= event.reminder_minutes:
            try:
                # ════════════════════════════════════════════════════════════
                # ✨ NOTIFICATION: Event Reminder (4.12)
                # ════════════════════════════════════════════════════════════
                time_until_str = f"{minutes_until} minutes" if minutes_until > 0 else "now"
                
                if minutes_until <= 15:
                    notify_event_starting_soon(
                        user_id=event.user_id,
                        event_title=event.title,
                        event_id=event.id,
                        minutes=minutes_until
                    )
                else:
                    notify_event_reminder(
                        user_id=event.user_id,
                        event_title=event.title,
                        event_id=event.id,
                        time_until=time_until_str
                    )
                
                reminders_sent += 1
            except Exception as e:
                print(f"⚠️ Event reminder notification failed for event {event.id}: {e}")
    
    return success_response({
        'reminders_sent': reminders_sent,
        'events_checked': len(upcoming_events)
    }, f'Sent {reminders_sent} reminders')


@calendar_events_bp.route('/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_calendar_event(event_id):
    """Delete calendar event"""
    current_user_id = get_jwt_identity()
    
    event = CalendarEvent.query.get(event_id)
    if not event:
        return error_response('Calendar event not found', 404)
    
    # Check if user is authorized to delete this event
    if int(event.user_id) != int(current_user_id):
        return error_response('Unauthorized to delete this calendar event', 403)
    
    # Store event info before deletion for notifications
    event_title = event.title
    event_date = format_event_date(event)
    startup_id = event.startup_id
    category = event.category
    event_id_copy = event.id
    
    try:
        db.session.delete(event)
        db.session.commit()
        
        # ════════════════════════════════════════════════════════════
        # ✨ NOTIFICATION: Event/Meeting Canceled (4.12)
        # ════════════════════════════════════════════════════════════
        if startup_id:
            try:
                member_ids = get_startup_member_ids(startup_id)
                member_ids = [m_id for m_id in member_ids if m_id != current_user_id]
                
                if member_ids:
                    if category == 'meeting':
                        notify_meeting_canceled(
                            user_ids=member_ids,
                            meeting_title=event_title,
                            meeting_id=event_id_copy,
                            date=event_date
                        )
                    else:
                        notify_event_canceled(
                            user_ids=member_ids,
                            event_title=event_title,
                            event_id=event_id_copy,
                            date=event_date
                        )
            except Exception as e:
                print(f"⚠️ Event cancellation notification failed: {e}")
        
        return success_response(message='Calendar event deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete calendar event: {str(e)}', 500)


@calendar_events_bp.route('/my-events', methods=['GET'])
@jwt_required()
def get_my_calendar_events():
    """Get current user's calendar events (convenience endpoint)"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    category = request.args.get('category', type=str)
    start_date = request.args.get('start_date', type=str)
    end_date = request.args.get('end_date', type=str)
    upcoming_only = request.args.get('upcoming_only', 'false').lower() == 'true'
    
    query = CalendarEvent.query.filter(CalendarEvent.user_id == current_user_id)
    
    if category:
        query = query.filter(CalendarEvent.category == category)
    if start_date:
        start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        query = query.filter(CalendarEvent.start_date >= start_datetime)
    if end_date:
        end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        query = query.filter(CalendarEvent.start_date <= end_datetime)
    if upcoming_only:
        now = datetime.utcnow()
        query = query.filter(CalendarEvent.start_date >= now)
    
    result = paginate(query.order_by(CalendarEvent.start_date.asc()), page, per_page)
    
    return success_response({
        'events': [event.to_dict() for event in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })


# Helper functions for authorization
def has_startup_access(user_id, startup_id):
    """Check if user has access to startup data"""
    # Admin users can access all startups
    current_user = User.query.get(user_id)
    if current_user:
        return True
    
    # Check if user is a member of the startup
    membership = StartupMember.query.filter_by(
        user_id=user_id, 
        startup_id=startup_id
    ).first()
    
    return membership is not None


@calendar_events_bp.route('/bulk', methods=['POST'])
@jwt_required()
def create_bulk_events():
    """Create multiple calendar events at once"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'events' not in data:
        return error_response('Events array is required', 400)
    
    events = data.get('events', [])
    if not isinstance(events, list) or len(events) > 50:
        return error_response('Events must be an array with max 50 items', 400)
    
    created_events = []
    errors = []
    
    for idx, event_data in enumerate(events):
        try:
            required_fields = ['title', 'start_date']
            if not all(field in event_data for field in required_fields):
                errors.append(f'Event {idx}: Missing required fields')
                continue
            
            # Users can only create events for themselves unless they're admin
            user_id = event_data.get('user_id', current_user_id)
            if user_id != current_user_id:
                current_user = User.query.get(current_user_id)
                if not current_user:
                    errors.append(f'Event {idx}: Unauthorized to create events for other users')
                    continue
            
            # Check startup access if startup_id is provided
            startup_id = event_data.get('startup_id')
            if startup_id and not has_startup_access(current_user_id, startup_id):
                errors.append(f'Event {idx}: Unauthorized to create events for this startup')
                continue
            
            event = CalendarEvent(
                user_id=user_id,
                startup_id=startup_id,
                title=event_data['title'],
                description=event_data.get('description'),
                start_date=datetime.fromisoformat(event_data['start_date'].replace('Z', '+00:00')),
                end_date=datetime.fromisoformat(event_data['end_date'].replace('Z', '+00:00')) if event_data.get('end_date') else None,
                all_day=event_data.get('all_day', False),
                category=event_data.get('category', 'event'),
                color=event_data.get('color'),
                location=event_data.get('location'),
                is_recurring=event_data.get('is_recurring', False),
                recurrence_rule=event_data.get('recurrence_rule'),
                reminder_minutes=event_data.get('reminder_minutes', 30)
            )
            
            db.session.add(event)
            created_events.append(event)
            
        except Exception as e:
            errors.append(f'Event {idx}: {str(e)}')
    
    try:
        if created_events:
            db.session.commit()
            
            # ════════════════════════════════════════════════════════════
            # ✨ NOTIFICATION: Bulk Events Created (4.12)
            # ════════════════════════════════════════════════════════════
            try:
                # Notify user about bulk creation
                from app.notifications.helpers import notify_info
                notify_info(
                    user_id=current_user_id,
                    message=f"Successfully created {len(created_events)} calendar events."
                )
            except Exception as e:
                print(f"⚠️ Bulk event notification failed: {e}")
            
            return success_response({
                'created_count': len(created_events),
                'events': [event.to_dict() for event in created_events],
                'errors': errors if errors else None
            }, f'Created {len(created_events)} events successfully')
        else:
            db.session.rollback()
            return error_response('No events were created', 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create events: {str(e)}', 500)


@calendar_events_bp.route('/sync', methods=['POST'])
@jwt_required()
def sync_external_calendar():
    """Sync events from external calendar services"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    provider = data.get('provider')
    access_token = data.get('access_token')
    
    if not provider or not access_token:
        return error_response('Provider and access token are required', 400)
    
    try:
        return success_response({
            'synced': True,
            'provider': provider,
            'message': 'Calendar sync initiated'
        })
    except Exception as e:
        return error_response(f'Failed to sync calendar: {str(e)}', 500)


@calendar_events_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_calendar_stats():
    """Get calendar statistics"""
    current_user_id = get_jwt_identity()
    
    user_id = request.args.get('user_id', type=int)
    startup_id = request.args.get('startup_id', type=int)
    start_date = request.args.get('start_date', type=str)
    end_date = request.args.get('end_date', type=str)
    
    # Default to current user if no user_id specified
    if not user_id:
        user_id = current_user_id
    
    # Check if user is authorized to view other users' stats
    if user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user:
            return error_response('Unauthorized to view other users stats', 403)
    
    query = CalendarEvent.query.filter(CalendarEvent.user_id == user_id)
    
    if startup_id:
        query = query.filter(CalendarEvent.startup_id == startup_id)
    if start_date:
        start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        query = query.filter(CalendarEvent.start_date >= start_datetime)
    if end_date:
        end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        query = query.filter(CalendarEvent.start_date <= end_datetime)
    
    events = query.all()
    
    # Calculate statistics
    total_events = len(events)
    upcoming_events = len([e for e in events if not e.is_past()])
    ongoing_events = len([e for e in events if e.is_ongoing()])
    
    # Events by category
    category_counts = {}
    for event in events:
        category = event.category
        category_counts[category] = category_counts.get(category, 0) + 1
    
    # Events by startup
    startup_counts = {}
    for event in events:
        if event.startup_id:
            startup_name = event.parent_startup.name if event.parent_startup else 'Unknown'
            startup_counts[startup_name] = startup_counts.get(startup_name, 0) + 1
    
    # Busiest day
    day_counts = {}
    for event in events:
        day_name = event.start_date.strftime('%A')
        day_counts[day_name] = day_counts.get(day_name, 0) + 1
    
    busiest_day = max(day_counts, key=day_counts.get) if day_counts else None
    
    return success_response({
        'stats': {
            'total_events': total_events,
            'upcoming_events': upcoming_events,
            'ongoing_events': ongoing_events,
            'category_distribution': category_counts,
            'startup_distribution': startup_counts,
            'busiest_day': busiest_day,
            'average_events_per_week': total_events / 52 if total_events > 0 else 0
        }
    })


@calendar_events_bp.route('/export', methods=['GET'])
@jwt_required()
def export_calendar():
    """Export calendar events in various formats"""
    current_user_id = get_jwt_identity()
    
    format_type = request.args.get('format', 'json')
    user_id = request.args.get('user_id', type=int)
    
    # Default to current user if no user_id specified
    if not user_id:
        user_id = current_user_id
    
    # Check if user is authorized to export other users' events
    if user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user:
            return error_response('Unauthorized to export other users calendar', 403)
    
    query = CalendarEvent.query.filter(CalendarEvent.user_id == user_id)
    events = query.order_by(CalendarEvent.start_date.asc()).all()
    
    if format_type == 'json':
        return jsonify({
            'success': True,
            'data': {
                'events': [event.to_dict() for event in events],
                'exported_at': datetime.utcnow().isoformat(),
                'total_events': len(events)
            }
        })
    
    elif format_type == 'csv':
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Title', 'Description', 'Start Date', 'End Date', 'Category',
            'Location', 'All Day', 'Reminder Minutes', 'Startup', 'Created At'
        ])
        
        # Write data
        for event in events:
            writer.writerow([
                event.title,
                event.description or '',
                event.start_date.isoformat(),
                event.end_date.isoformat() if event.end_date else '',
                event.category,
                event.location or '',
                'Yes' if event.all_day else 'No',
                event.reminder_minutes,
                event.parent_startup.name if event.parent_startup else '',
                event.created_at.isoformat()
            ])
        
        output.seek(0)
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'calendar_export_{datetime.utcnow().strftime("%Y%m%d")}.csv'
        )
    
    elif format_type == 'ical':
        # Generate iCal format
        from icalendar import Calendar, Event as ICalEvent
        
        cal = Calendar()
        cal.add('prodid', '-//SF Collab//Calendar Export//EN')
        cal.add('version', '2.0')
        
        for event in events:
            ical_event = ICalEvent()
            ical_event.add('summary', event.title)
            if event.description:
                ical_event.add('description', event.description)
            ical_event.add('dtstart', event.start_date)
            if event.end_date:
                ical_event.add('dtend', event.end_date)
            if event.location:
                ical_event.add('location', event.location)
            ical_event.add('uid', f'event-{event.id}@sfcollab.com')
            ical_event.add('dtstamp', datetime.utcnow())
            
            cal.add_component(ical_event)
        
        response = make_response(cal.to_ical())
        response.headers['Content-Type'] = 'text/calendar'
        response.headers['Content-Disposition'] = f'attachment; filename=calendar_export_{datetime.utcnow().strftime("%Y%m%d")}.ics'
        return response
    
    else:
        return error_response('Unsupported export format', 400)


@calendar_events_bp.route('/shared', methods=['GET'])
@jwt_required()
def get_shared_events():
    """Get events shared with the current user"""
    current_user_id = get_jwt_identity()
    
    # This would require a shared_events table
    # For now, we'll return events from startups the user is a member of
    memberships = StartupMember.query.filter_by(user_id=current_user_id).all()
    startup_ids = [m.startup_id for m in memberships]
    
    if not startup_ids:
        return success_response({'events': [], 'pagination': {'total': 0, 'pages': 0}})
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    query = CalendarEvent.query.filter(
        CalendarEvent.startup_id.in_(startup_ids),
        CalendarEvent.user_id != current_user_id  # Exclude own events
    )
    
    result = paginate(query.order_by(CalendarEvent.start_date.asc()), page, per_page)
    
    return success_response({
        'events': [event.to_dict() for event in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })