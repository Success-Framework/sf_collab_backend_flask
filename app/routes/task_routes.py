from flask import Blueprint, request, jsonify
from datetime import datetime
from app.models.task import Task
from app.services.achievement_service import AchievementService
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

@tasks_bp.route('', methods=['GET'])
def get_tasks():
    """Get all tasks with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    startup_id = request.args.get('startup_id', type=int)
    status = request.args.get('status', type=str)
    priority = request.args.get('priority', type=str)
    assigned_to = request.args.get('assigned_to', type=int)
    
    query = Task.query
    
    if user_id:
        query = query.filter(Task.user_id == user_id)
    if startup_id:
        query = query.filter(Task.startup_id == startup_id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)
    
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

@tasks_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get single task by ID"""
    task = Task.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)
    
    return success_response({'task': task.to_dict()})

@tasks_bp.route('', methods=['POST'])
def create_task():
    """Create new task"""
    data = request.get_json()
    
    required_fields = ['title', 'user_id', 'created_by']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: title, user_id, created_by')
    
    try:
        task = Task(
            title=data['title'],
            user_id=data['user_id'],
            startup_id=data.get('startup_id'),
            description=data.get('description'),
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'today'),
            tags=data.get('tags', []),
            labels=data.get('labels', []),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            estimated_hours=data.get('estimated_hours'),
            assigned_to=data.get('assigned_to'),
            created_by=data['created_by']
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
def update_task(task_id):
    """Update task"""
    task = Task.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)
    
    data = request.get_json()
    
    try:
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'priority' in data:
            task.priority = data['priority']
        if 'due_date' in data:
            task.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
        if 'estimated_hours' in data:
            task.estimated_hours = data['estimated_hours']
        if 'tags' in data:
            task.tags = data['tags']
        if 'labels' in data:
            task.labels = data['labels']
        
        db.session.commit()
        
        return success_response({
            'task': task.to_dict()
        }, 'Task updated successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update task: {str(e)}', 500)

@tasks_bp.route('/<int:task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    """Update task status"""
    task = Task.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)
    
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
def update_task_progress(task_id):
    """Update task progress"""
    task = Task.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)
    
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
def assign_task(task_id):
    """Assign task to user"""
    task = Task.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)
    
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
def log_task_time(task_id):
    """Log time spent on task"""
    task = Task.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)
    
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
def delete_task(task_id):
    """Delete task"""
    task = Task.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)
    
    try:
        db.session.delete(task)
        db.session.commit()
        return success_response(message='Task deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete task: {str(e)}', 500)