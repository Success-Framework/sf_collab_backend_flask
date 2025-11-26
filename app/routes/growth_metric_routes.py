from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app.models.growthMetric import GrowthMetric
from app.extensions import db
from app.utils.helper import error_response, success_response, paginate

growth_metrics_bp = Blueprint('growth_metrics', __name__, url_prefix='/api/growth-metrics')

@growth_metrics_bp.route('', methods=['GET'])
def get_growth_metrics():
    """Get all growth metrics with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    startup_id = request.args.get('startup_id', type=int)
    user_id = request.args.get('user_id', type=int)
    metric_type = request.args.get('metric_type', type=str)
    current_only = request.args.get('current_only', 'false').lower() == 'true'
    
    query = GrowthMetric.query
    
    if startup_id:
        query = query.filter(GrowthMetric.startup_id == startup_id)
    if user_id:
        query = query.filter(GrowthMetric.user_id == user_id)
    if metric_type:
        query = query.filter(GrowthMetric.metric_type == metric_type)
    if current_only:
        now = datetime.utcnow()
        query = query.filter(
            GrowthMetric.period_start <= now,
            GrowthMetric.period_end >= now
        )
    
    result = paginate(query.order_by(GrowthMetric.period_start.desc()), page, per_page)
    
    return success_response({
        'growth_metrics': [metric.to_dict() for metric in result['items']],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    })

@growth_metrics_bp.route('/<int:metric_id>', methods=['GET'])
def get_growth_metric(metric_id):
    """Get single growth metric by ID"""
    metric = GrowthMetric.query.get(metric_id)
    if not metric:
        return error_response('Growth metric not found', 404)
    
    return success_response({'growth_metric': metric.to_dict()})

@growth_metrics_bp.route('', methods=['POST'])
def create_growth_metric():
    """Create new growth metric"""
    data = request.get_json()
    
    required_fields = ['metric_type', 'period_start', 'period_end']
    if not all(field in data for field in required_fields):
        return error_response('Missing required fields: metric_type, period_start, period_end')
    
    # Validate that either startup_id or user_id is provided
    if not data.get('startup_id') and not data.get('user_id'):
        return error_response('Either startup_id or user_id must be provided', 400)
    
    try:
        metric = GrowthMetric(
            startup_id=data.get('startup_id'),
            user_id=data.get('user_id'),
            metric_type=data['metric_type'],
            current_value=data.get('current_value', 0),
            previous_value=data.get('previous_value', 0),
            period_start=datetime.fromisoformat(data['period_start'].replace('Z', '+00:00')),
            period_end=datetime.fromisoformat(data['period_end'].replace('Z', '+00:00'))
        )
        
        # Calculate growth percentage
        metric.growth_percentage = metric.calculate_growth_percentage()
        
        db.session.add(metric)
        db.session.commit()
        
        return success_response({
            'growth_metric': metric.to_dict()
        }, 'Growth metric created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create growth metric: {str(e)}', 500)

@growth_metrics_bp.route('/<int:metric_id>', methods=['PUT'])
def update_growth_metric(metric_id):
    """Update growth metric"""
    metric = GrowthMetric.query.get(metric_id)
    if not metric:
        return error_response('Growth metric not found', 404)
    
    data = request.get_json()
    
    try:
        if 'current_value' in data:
            current_value = data['current_value']
            previous_value = data.get('previous_value', metric.previous_value)
            metric.update_values(current_value, previous_value)
        
        if 'period_start' in data:
            metric.period_start = datetime.fromisoformat(data['period_start'].replace('Z', '+00:00'))
        if 'period_end' in data:
            metric.period_end = datetime.fromisoformat(data['period_end'].replace('Z', '+00:00'))
        
        db.session.commit()
        
        return success_response({
            'growth_metric': metric.to_dict()
        }, 'Growth metric updated successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update growth metric: {str(e)}', 500)

@growth_metrics_bp.route('/<int:metric_id>/values', methods=['PUT'])
def update_metric_values(metric_id):
    """Update metric values and recalculate growth"""
    metric = GrowthMetric.query.get(metric_id)
    if not metric:
        return error_response('Growth metric not found', 404)
    
    data = request.get_json()
    current_value = data.get('current_value')
    previous_value = data.get('previous_value')
    
    if current_value is None:
        return error_response('Current value is required', 400)
    
    try:
        metric.update_values(current_value, previous_value)
        return success_response({
            'growth_metric': metric.to_dict()
        }, 'Metric values updated successfully')
    except Exception as e:
        return error_response(f'Failed to update metric values: {str(e)}', 500)

@growth_metrics_bp.route('/summary', methods=['GET'])
def get_growth_summary():
    """Get growth metrics summary"""
    startup_id = request.args.get('startup_id', type=int)
    user_id = request.args.get('user_id', type=int)
    
    # Get current period metrics
    now = datetime.utcnow()
    current_metrics = GrowthMetric.query.filter(
        GrowthMetric.period_start <= now,
        GrowthMetric.period_end >= now
    )
    
    if startup_id:
        current_metrics = current_metrics.filter(GrowthMetric.startup_id == startup_id)
    if user_id:
        current_metrics = current_metrics.filter(GrowthMetric.user_id == user_id)
    
    current_metrics = current_metrics.all()
    
    summary = {
        'total_metrics': len(current_metrics),
        'positive_growth': len([m for m in current_metrics if m.growth_percentage > 0]),
        'negative_growth': len([m for m in current_metrics if m.growth_percentage < 0]),
        'average_growth': sum(m.growth_percentage for m in current_metrics) / len(current_metrics) if current_metrics else 0,
        'metrics_by_type': {}
    }
    
    # Group by metric type
    for metric in current_metrics:
        if metric.metric_type not in summary['metrics_by_type']:
            summary['metrics_by_type'][metric.metric_type] = []
        summary['metrics_by_type'][metric.metric_type].append(metric.to_dict())
    
    return success_response({'summary': summary})

@growth_metrics_bp.route('/<int:metric_id>', methods=['DELETE'])
def delete_growth_metric(metric_id):
    """Delete growth metric"""
    metric = GrowthMetric.query.get(metric_id)
    if not metric:
        return error_response('Growth metric not found', 404)
    
    try:
        db.session.delete(metric)
        db.session.commit()
        return success_response(message='Growth metric deleted successfully')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete growth metric: {str(e)}', 500)