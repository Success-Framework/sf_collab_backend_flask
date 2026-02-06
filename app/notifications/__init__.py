"""
SF Collab Notifications Package
Centralized notification system for the SF Collab platform
"""

# Import templates first (no dependencies)
from app.notifications.templates import (
    NOTIFICATION_TEMPLATES,
    PRIORITY_LEVELS,
    NOTIFICATION_CATEGORIES
)

# Import service (depends on templates)
from app.notifications.service import notification_service, NotificationService

# Import helpers last (depends on service)
# Using relative import to avoid circular issues
from . import helpers

__all__ = [
    'notification_service',
    'NotificationService',
    'NOTIFICATION_TEMPLATES',
    'PRIORITY_LEVELS',
    'NOTIFICATION_CATEGORIES',
    'helpers'
]