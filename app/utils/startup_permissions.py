# app/utils/startup_permissions.py
from flask_jwt_extended import get_jwt_identity
from app.models.startup import Startup
from app.models.startUpMember import StartupMember
from app.models.user import User
from app.models.Enums import UserRoles


def get_current_user_startup_role(startup_id: int) -> str:
    """
    Returns one of: 'owner', 'founder', 'member', 'none'
    """
    user_id = get_jwt_identity()
    if not user_id:
        return 'none'

    user = User.query.get(user_id)
    if not user:
        return 'none'

    # Global admin has owner-level access everywhere
    if user.role == UserRoles.admin:
        return 'owner'

    startup = Startup.query.get(startup_id)
    if not startup:
        return 'none'

    # Creator always has owner rights
    if startup.creator_id == user_id:
        print(f"User {user_id} is creator of startup {startup_id}")
        return 'owner'

    membership = (
        StartupMember.query.filter_by(
            user_id=user_id,
            startup_id=startup_id,
            is_active=True
        )
        .first()
    )

    if not membership:
        return 'none'

    if membership.admin:
        return 'admin'
    # Special elevated member role - handle both enum and string
    role_value = membership.role.value if hasattr(membership.role, 'value') else membership.role
    if role_value == 'founder':
        print(f"User {user_id} is founder of startup {startup_id}")
        return 'founder'

    # Default member access
    print(f"User {user_id} is regular member of startup {startup_id}")
    return 'member'


# ----------------------------------------------------
# Permission checks - use these in routes
# ----------------------------------------------------

def can_view_basic_info() -> bool:
    """Any logged-in user can see basic public info"""
    return get_jwt_identity() is not None


def can_view_full_details(startup_id: int) -> bool:
    """Members, founders, owners"""
    role = get_current_user_startup_role(startup_id)
    return role in {'owner', 'founder', 'member'}


def can_manage_documents(startup_id: int) -> bool:
    """Only owner + founder"""
    role = get_current_user_startup_role(startup_id)
    return role in {'owner', 'founder'}


def can_manage_members(startup_id: int) -> bool:
    """Only owner + founder"""
    role = get_current_user_startup_role(startup_id)
    print(f"can_manage_members for startup {startup_id}: role = {role}")
    return role in {'owner', 'founder'}


def can_edit_startup_core_info(startup_id: int) -> bool:
    """Only real owner (creator) or global admin"""
    return get_current_user_startup_role(startup_id) == 'owner'


def can_manage_positions_and_roles(startup_id: int) -> bool:
    """Only real owner (creator) or global admin"""
    return get_current_user_startup_role(startup_id) == 'owner'