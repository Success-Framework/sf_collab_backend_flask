from flask import Blueprint, request
from app.models.userRole import UserRole
from app.extensions import db
from app.utils.helper import success_response, error_response
from flask_jwt_extended import jwt_required, get_jwt_identity

user_roles_bp = Blueprint('user_roles', __name__)

#! GET ALL USER ROLES
@user_roles_bp.route('', methods=['GET'])
@jwt_required()
def get_all_user_roles():
  try:
    roles = UserRole.query.all()
    return success_response([{'id': role.id, 'user_id': role.user_id, 'role': role.role} for role in roles])
  except Exception as e:
    return error_response(f"Error fetching roles: {str(e)}", 500)

#! GET SINGLE USER ROLE BY ID
@user_roles_bp.route('/<int:role_id>', methods=['GET'])
@jwt_required()
def get_user_role(role_id):
  try:
    role = UserRole.query.get_or_404(role_id)
    return success_response({'id': role.id, 'user_id': role.user_id, 'role': role.role})
  except Exception as e:
    return error_response("Role not found", 404)

#! CREATE NEW USER ROLE
@user_roles_bp.route('', methods=['POST'])
@jwt_required()
def create_user_role():
  try:
    data = request.json
    new_role = UserRole(user_id=data['user_id'], role=data['role'])
    db.session.add(new_role)
    db.session.commit()
    return success_response({'id': new_role.id, 'user_id': new_role.user_id, 'role': new_role.role}, "User role created successfully", 201)
  except KeyError:
    return error_response("Missing required fields", 400)
  except Exception as e:
    return error_response(f"Error creating role: {str(e)}", 500)

#! UPDATE USER ROLE
@user_roles_bp.route('/<int:role_id>', methods=['PUT'])
@jwt_required()
def update_user_role(role_id):
  try:
    role = UserRole.query.get_or_404(role_id)
    data = request.json
    role.role = data.get('role', role.role)
    db.session.commit()
    return success_response({'id': role.id, 'user_id': role.user_id, 'role': role.role}, "User role updated successfully")
  except Exception as e:
    return error_response("Role not found", 404)

#! DELETE USER ROLE
@user_roles_bp.route('/<int:role_id>', methods=['DELETE'])
@jwt_required()
def delete_user_role(role_id):
  try:
    role = UserRole.query.get_or_404(role_id)
    db.session.delete(role)
    db.session.commit()
    return success_response(message="User role deleted successfully", status=204)
  except Exception as e:
    return error_response("Role not found", 404)

@user_roles_bp.route('/my-roles', methods=['GET'])
@jwt_required()
def get_my_roles():
  try:
    user_id = get_jwt_identity()
    roles = UserRole.query.filter_by(user_id=user_id).all()
    return success_response([{'id': role.id, 'role': role.role} for role in roles])
  except Exception as e:
    return error_response(f"Error fetching user roles: {str(e)}", 500)