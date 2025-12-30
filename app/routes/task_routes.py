from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app.models.task import Task
from app.models.user import User
from app.models.startUpMember import StartupMember
from app.services.achievement_service import AchievementService
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get all tasks with filtering"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    user_id = request.args.get('user_id', type=int)
    startup_id = request.args.get('startup_id', type=int)
    status = request.args.get('status', type=str)
    priority = request.args.get('priority', type=str)
    assigned_to = request.args.get('assigned_to', type=int)
    show_overdue_only = request.args.get('show_overdue_only', 'false').lower() == 'true'
    
    # Default to current user's tasks if no user_id specified
    if not user_id:
        user_id = current_user_id
    
    # Check if user is authorized to view other users' tasks
    if user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user:
            # Check if they're in the same startup
            if startup_id:
                if not has_startup_access(current_user_id, startup_id):
                    return error_response('Unauthorized to access tasks', 403)
            else:
                return error_response('Unauthorized to view other users tasks', 403)
    
    query = Task.query.filter(Task.user_id == user_id)
    
    if startup_id and startup_id != 'all':
        query = query.filter(Task.startup_id == startup_id)
    if status and status != 'all':
        query = query.filter(Task.status == status)
    if priority and priority != 'all':
        query = query.filter(Task.priority == priority)
    if assigned_to and assigned_to != 'all':
        query = query.filter(Task.assigned_to == assigned_to)
    if show_overdue_only:
        # Filter for overdue tasks
        query = query.filter(Task.due_date < datetime.utcnow(), Task.status != 'completed')
    
    result = paginate(query.order_by(Task.created_at.desc()), page, per_page)
    
    return success_response({
        'tasks': [task.to_dict() for task in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@tasks_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_task_stats():
    """Get task statistics for dashboard"""
    current_user_id = get_jwt_identity()
    
    user_id = request.args.get('user_id', type=int)
    startup_id = request.args.get('startup_id', type=int)
    time_range = request.args.get('time_range', '30d')
    
    # Default to current user if no user_id specified
    if not user_id:
        user_id = current_user_id
    
    # Check authorization
    if user_id != current_user_id:
        return error_response('Unauthorized to view other users stats', 403)
    
    # Calculate time range
    now = datetime.utcnow()
    if time_range == '7d':
        start_date = now - timedelta(days=7)
    elif time_range == '90d':
        start_date = now - timedelta(days=90)
    elif time_range == 'month':
        start_date = datetime(now.year, now.month, 1)
    else:  # 30d default
        start_date = now - timedelta(days=30)
    
    query = Task.query.filter(
        Task.user_id == user_id,
        Task.created_at >= start_date
    )
    
    if startup_id and startup_id != 'all':
        query = query.filter(Task.startup_id == startup_id)
    
    tasks = query.all()
    
    # Calculate statistics
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == 'completed'])
    in_progress_tasks = len([t for t in tasks if t.status == 'in_progress'])
    overdue_tasks = len([t for t in tasks if t.is_overdue()])
    today_tasks = len([t for t in tasks if t.status == 'today'])
    
    # Calculate completion rate
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Calculate on-time completion rate
    completed_on_time = len([t for t in tasks if t.status == 'completed' and t.is_on_time])
    on_time_rate = (completed_on_time / completed_tasks * 100) if completed_tasks > 0 else 0
    
    # Priority distribution
    priority_counts = {
        'high': len([t for t in tasks if t.priority == 'high']),
        'medium': len([t for t in tasks if t.priority == 'medium']),
        'low': len([t for t in tasks if t.priority == 'low'])
    }
    
    # Daily completion data for charts
    daily_data = []
    current_date = start_date
    while current_date <= now:
        date_str = current_date.strftime('%Y-%m-%d')
        day_tasks = [t for t in tasks if t.created_at.date() == current_date.date()]
        
        daily_data.append({
            'date': date_str,
            'display_date': current_date.strftime('%b %d'),
            'completed': len([t for t in day_tasks if t.status == 'completed']),
            'in_progress': len([t for t in day_tasks if t.status == 'in_progress']),
            'overdue': len([t for t in day_tasks if t.is_overdue()]),
            'total': len(day_tasks)
        })
        
        current_date += timedelta(days=1)
    
    return success_response({
        'stats': {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'overdue_tasks': overdue_tasks,
            'today_tasks': today_tasks,
            'completion_rate': round(completion_rate, 1),
            'on_time_rate': round(on_time_rate, 1),
            'completed_on_time': completed_on_time,
            'priority_distribution': priority_counts
        },
        'daily_data': daily_data
    })

@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get single task by ID"""
    current_user_id = get_jwt_identity()
    
    task = Task.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)
    
    # Check if user is authorized to view this task
    if task.user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user :
            # Check if they're in the same startup
            if task.startup_id:
                if not has_startup_access(current_user_id, task.startup_id):
                    return error_response('Unauthorized to view this task', 403)
            else:
                return error_response('Unauthorized to view this task', 403)
    
    return success_response({'task': task.to_dict()})

@tasks_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    """Create new task"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['title']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: title')
    
    # Users can only create tasks for themselves unless they're admin
    user_id = data.get('user_id', current_user_id)
    if user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user :
            return error_response('Unauthorized to create tasks for other users', 403)
    
    # Check startup access if startup_id is provided
    startup_id = data.get('startup_id')
    if startup_id and not has_startup_access(current_user_id, startup_id):
        return error_response('Unauthorized to create tasks for this startup', 403)
    
    try:
        # Handle datetime parsing with timezone
        due_date = None
        if data.get('due_date'):
            due_date_str = data['due_date'].replace('Z', '+00:00')
            due_date = datetime.fromisoformat(due_date_str)
        
        task = Task(
            user_id=user_id,
            startup_id=startup_id,
            title=data['title'],
            description=data.get('description'),
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'today'),
            tags=data.get('tags', []),
            labels=data.get('labels', []),
            due_date=due_date,
            estimated_hours=data.get('estimated_hours'),
            assigned_to=data.get('assigned_to'),
            created_by=current_user_id,
            progress_percentage=data.get('progress_percentage', 0)
        )
        
        db.session.add(task)
        db.session.commit()
        
        return success_response({
            'task': task.to_dict()
        }, 'Task created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create task: {str(e)}', 500)

@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update task"""
    current_user_id = get_jwt_identity()
    
    task = Task.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)
    
    # Check if user is authorized to update this task
    if task.user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user :
            return error_response('Unauthorized to update this task', 403)
    
    data = request.get_json()
    
    try:
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'priority' in data:
            task.priority = data['priority']
        if 'status' in data:
            task.update_status(data['status'])
        if 'due_date' in data:
            if data['due_date']:
                due_date_str = data['due_date'].replace('Z', '+00:00')
                task.due_date = datetime.fromisoformat(due_date_str)
            else:
                task.due_date = None
        if 'estimated_hours' in data:
            task.estimated_hours = data['estimated_hours']
        if 'actual_hours' in data:
            task.actual_hours = data['actual_hours']
        if 'tags' in data:
            task.tags = data['tags']
        if 'labels' in data:
            task.labels = data['labels']
        if 'progress_percentage' in data:
            task.update_progress(data['progress_percentage'])
        
        db.session.commit()
        
        return success_response({
            'task': task.to_dict()
        }, 'Task updated successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update task: {str(e)}', 500)

@tasks_bp.route('/<int:task_id>/status', methods=['PUT'])
@jwt_required()
def update_task_status(task_id):
    """Update task status"""
    current_user_id = get_jwt_identity()
    
    task = Task.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)
    
    # Check if user is authorized to update this task
    if task.user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user :
            return error_response('Unauthorized to update this task', 403)
    
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return error_response('Status is required', 400)
    
    try:
        task.update_status(new_status)
        
        # Check achievements for task completion
        if new_status == 'completed':
            AchievementService.check_achievements(task.user_id, 'tasks_completed')
        
        return success_response({
            'task': task.to_dict()
        }, 'Task status updated successfully')
    except Exception as e:
        return error_response(f'Failed to update task status: {str(e)}', 500)

@tasks_bp.route('/<int:task_id>/progress', methods=['PUT'])
@jwt_required()
def update_task_progress(task_id):
    """Update task progress"""
    current_user_id = get_jwt_identity()
    
    task = Task.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)
    
    # Check if user is authorized to update this task
    if task.user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user :
            return error_response('Unauthorized to update this task', 403)
    
    data = request.get_json()
    progress = data.get('progress_percentage')
    
    if progress is None:
        return error_response('Progress percentage is required', 400)
    
    try:
        task.update_progress(progress)
        return success_response({
            'task': task.to_dict()
        }, 'Task progress updated successfully')
    except Exception as e:
        return error_response(f'Failed to update task progress: {str(e)}', 500)

@tasks_bp.route('/<int:task_id>/assign', methods=['PUT'])
@jwt_required()
def assign_task(task_id):
    """Assign task to user"""
    current_user_id = get_jwt_identity()
    
    task = Task.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)
    
    # Check if user is authorized to update this task
    if task.user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user :
            return error_response('Unauthorized to update this task', 403)
    
    data = request.get_json()
    user_id = data.get('assigned_to')
    
    if not user_id:
        return error_response('User ID is required', 400)
    
    try:
        task.assign_to_user(user_id)
        return success_response({
            'task': task.to_dict()
        }, 'Task assigned successfully')
    except Exception as e:
        return error_response(f'Failed to assign task: {str(e)}', 500)

@tasks_bp.route('/<int:task_id>/log-time', methods=['POST'])
@jwt_required()
def log_task_time(task_id):
    """Log time spent on task"""
    current_user_id = get_jwt_identity()
    
    task = Task.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)
    
    # Check if user is authorized to update this task
    if task.user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user :
            return error_response('Unauthorized to update this task', 403)
    
    data = request.get_json()
    hours = data.get('hours')
    
    if not hours or hours <= 0:
        return error_response('Valid hours value is required', 400)
    
    try:
        task.log_time(hours)
        return success_response({
            'task': task.to_dict()
        }, 'Time logged successfully')
    except Exception as e:
        return error_response(f'Failed to log time: {str(e)}', 500)

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete task"""
    current_user_id = get_jwt_identity()
    
    task = Task.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)
    
    # Check if user is authorized to delete this task
    if task.user_id != current_user_id:
        current_user = User.query.get(current_user_id)
        if not current_user :
            return error_response('Unauthorized to delete this task', 403)
    
    try:
        db.session.delete(task)
        db.session.commit()
        return success_response(message='Task deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete task: {str(e)}', 500)

@tasks_bp.route('/my-tasks', methods=['GET'])
@jwt_required()
def get_my_tasks():
    """Get current user's tasks (convenience endpoint)"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    startup_id = request.args.get('startup_id', type=int)
    status = request.args.get('status', type=str)
    priority = request.args.get('priority', type=str)
    
    query = Task.query.filter(Task.user_id == current_user_id)
    
    if startup_id:
        query = query.filter(Task.startup_id == startup_id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    
    result = paginate(query.order_by(Task.created_at.desc()), page, per_page)
    
    return success_response({
        'tasks': [task.to_dict() for task in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@tasks_bp.route('/overdue', methods=['GET'])
@jwt_required()
def get_overdue_tasks():
    """Get current user's overdue tasks"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    startup_id = request.args.get('startup_id', type=int)
    
    query = Task.query.filter(
        Task.user_id == current_user_id,
        Task.due_date < datetime.utcnow(),
        Task.status != 'completed'
    )
    
    if startup_id:
        query = query.filter(Task.startup_id == startup_id)
    
    result = paginate(query.order_by(Task.due_date.asc()), page, per_page)
    
    return success_response({
        'tasks': [task.to_dict() for task in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@tasks_bp.route('/upcoming', methods=['GET'])
@jwt_required()
def get_upcoming_tasks():
    """Get current user's upcoming tasks (due in next 7 days)"""
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    startup_id = request.args.get('startup_id', type=int)
    
    now = datetime.utcnow()
    next_week = now + timedelta(days=7)
    
    query = Task.query.filter(
        Task.user_id == current_user_id,
        Task.due_date.between(now, next_week),
        Task.status != 'completed'
    )
    
    if startup_id:
        query = query.filter(Task.startup_id == startup_id)
    
    result = paginate(query.order_by(Task.due_date.asc()), page, per_page)
    
    return success_response({
        'tasks': [task.to_dict() for task in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

# Helper functions
def has_startup_access(user_id, startup_id):
    """Check if user has access to startup data"""
    # Admin users can access all startups
    current_user = User.query.get(user_id)
    if current_user :
        return True
    
    # Check if user is a member of the startup
    membership = StartupMember.query.filter_by(
        user_id=user_id, 
        startup_id=startup_id
    ).first()
    
    return membership is not None