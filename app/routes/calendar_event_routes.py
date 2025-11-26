from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app.models.calendarEvent import CalendarEvent
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

calendar_events_bp = Blueprint('calendar_events', __name__, url_prefix='/api/calendar-events')

@calendar_events_bp.route('', methods=['GET'])
def get_calendar_events():
    """Get all calendar events with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    user_id = request.args.get('user_id', type=int)
    startup_id = request.args.get('startup_id', type=int)
    category = request.args.get('category', type=str)
    start_date = request.args.get('start_date', type=str)
    end_date = request.args.get('end_date', type=str)
    upcoming_only = request.args.get('upcoming_only', 'false').lower() == 'true'
    
    query = CalendarEvent.query
    
    if user_id:
        query = query.filter(CalendarEvent.user_id == user_id)
    if startup_id:
        query = query.filter(CalendarEvent.startup_id == startup_id)
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

@calendar_events_bp.route('/<int:event_id>', methods=['GET'])
def get_calendar_event(event_id):
    """Get single calendar event by ID"""
    event = CalendarEvent.query.get(event_id)
    if not event:
        return error_response('Calendar event not found', 404)
    
    return success_response({'event': event.to_dict()})

@calendar_events_bp.route('', methods=['POST'])
def create_calendar_event():
    """Create new calendar event"""
    data = request.get_json()
    
    required_fields = ['user_id', 'title', 'start_date']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: user_id, title, start_date')
    
    try:
        event = CalendarEvent(
            user_id=data['user_id'],
            startup_id=data.get('startup_id'),
            title=data['title'],
            description=data.get('description'),
            start_date=datetime.fromisoformat(data['start_date'].replace('Z', '+00:00')),
            end_date=datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')) if data.get('end_date') else None,
            all_day=data.get('all_day', False),
            category=data.get('category', 'event'),
            color=data.get('color'),
            location=data.get('location'),
            is_recurring=data.get('is_recurring', False),
            recurrence_rule=data.get('recurrence_rule'),
            reminder_minutes=data.get('reminder_minutes', 30)
        )
        
        db.session.add(event)
        db.session.commit()
        
        return success_response({
            'event': event.to_dict()
        }, 'Calendar event created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create calendar event: {str(e)}', 500)

@calendar_events_bp.route('/<int:event_id>', methods=['PUT'])
def update_calendar_event(event_id):
    """Update calendar event"""
    event = CalendarEvent.query.get(event_id)
    if not event:
        return error_response('Calendar event not found', 404)
    
    data = request.get_json()
    
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
        
        return success_response({
            'event': event.to_dict()
        }, 'Calendar event updated successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update calendar event: {str(e)}', 500)

@calendar_events_bp.route('/<int:event_id>/dates', methods=['PUT'])
def update_event_dates(event_id):
    """Update event dates"""
    event = CalendarEvent.query.get(event_id)
    if not event:
        return error_response('Calendar event not found', 404)
    
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
def get_upcoming_events():
    """Get upcoming events that need reminders"""
    user_id = request.args.get('user_id', type=int)
    hours_ahead = request.args.get('hours_ahead', 24, type=int)
    
    now = datetime.utcnow()
    reminder_cutoff = now + timedelta(hours=hours_ahead)
    
    query = CalendarEvent.query.filter(
        CalendarEvent.start_date <= reminder_cutoff,
        CalendarEvent.start_date >= now,
        CalendarEvent.reminder_minutes > 0
    )
    
    if user_id:
        query = query.filter(CalendarEvent.user_id == user_id)
    
    events = query.order_by(CalendarEvent.start_date.asc()).all()
    
    # Filter events that should remind now
    events_to_remind = [event for event in events if event.should_remind()]
    
    return success_response({
        'upcoming_events': [event.to_dict() for event in events],
        'events_to_remind': [event.to_dict() for event in events_to_remind],
        'total_upcoming': len(events),
        'total_to_remind': len(events_to_remind)
    })

@calendar_events_bp.route('/<int:event_id>', methods=['DELETE'])
def delete_calendar_event(event_id):
    """Delete calendar event"""
    event = CalendarEvent.query.get(event_id)
    if not event:
        return error_response('Calendar event not found', 404)
    
    try:
        db.session.delete(event)
        db.session.commit()
        return success_response(message='Calendar event deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete calendar event: {str(e)}', 500)