#!/usr/bin/env python3
"""
Test script to debug startup deletion authorization
"""
import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.models.user import User
from app.models.startup import Startup
from app.models.startUpMember import StartupMember
from app.utils.startup_permissions import get_current_user_startup_role, can_manage_members

def test_delete_authorization():
    """Test the delete authorization logic"""
    app = create_app('development')

    with app.app_context():
        # Get the test user (ID 2)
        user = User.query.get(2)
        print(f"Test User: {user}")
        print(f"User ID: {user.id}")
        print(f"User Email: {user.email}")
        print(f"User Role: {user.role}")

        # Get the test startup (ID 1)
        startup = Startup.query.get(1)
        print(f"\nTest Startup: {startup}")
        print(f"Startup ID: {startup.id}")
        print(f"Startup Name: {startup.name}")
        print(f"Startup Creator ID: {startup.creator_id}")

        # Check membership
        membership = StartupMember.query.filter_by(
            user_id=user.id,
            startup_id=startup.id,
            is_active=True
        ).first()
        print(f"\nMembership: {membership}")
        if membership:
            print(f"Membership Role: {membership.role}")
            print(f"Membership Role Type: {type(membership.role)}")

        # Test the permission functions
        print("\n=== Testing Permission Functions ===")
        try:
            role = get_current_user_startup_role(startup.id, user.id)
            print(f"get_current_user_startup_role({startup.id}, {user.id}): {role}")
        except Exception as e:
            print(f"Error in get_current_user_startup_role: {e}")

        try:
            can_manage = can_manage_members(startup.id, user.id)
            print(f"can_manage_members({startup.id}, {user.id}): {can_manage}")
        except Exception as e:
            print(f"Error in can_manage_members: {e}")

if __name__ == "__main__":
    test_delete_authorization()