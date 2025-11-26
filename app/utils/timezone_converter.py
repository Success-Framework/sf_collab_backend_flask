from datetime import datetime, timedelta
import pytz
from typing import Optional, Dict, Any
import re

class TimezoneConverter:
    # Common timezone mappings for countries
    COUNTRY_TIMEZONES = {
        'US': 'America/New_York',
        'UK': 'Europe/London',
        'GB': 'Europe/London',
        'CA': 'America/Toronto',
        'AU': 'Australia/Sydney',
        'DE': 'Europe/Berlin',
        'FR': 'Europe/Paris',
        'IT': 'Europe/Rome',
        'ES': 'Europe/Madrid',
        'JP': 'Asia/Tokyo',
        'CN': 'Asia/Shanghai',
        'IN': 'Asia/Kolkata',
        'BR': 'America/Sao_Paulo',
        'RU': 'Europe/Moscow',
        'ZA': 'Africa/Johannesburg',
        'EG': 'Africa/Cairo',
        'NG': 'Africa/Lagos',
        'KE': 'Africa/Nairobi',
        'SA': 'Asia/Riyadh',
        'AE': 'Asia/Dubai',
        'SG': 'Asia/Singapore',
        'KR': 'Asia/Seoul',
        'MX': 'America/Mexico_City',
        'AR': 'America/Argentina/Buenos_Aires',
    }
    
    # Timezone placeholder pattern
    TIME_PLACEHOLDER_PATTERN = r'\[(\d{1,2}:\d{2})\]'
    
    @staticmethod
    def get_user_timezone(user_country: str, user_timezone: str = None) -> str:
        """Get timezone string based on user country or custom timezone"""
        if user_timezone:
            return user_timezone
        return TimezoneConverter.COUNTRY_TIMEZONES.get(user_country, 'UTC')
    
    @staticmethod
    def convert_datetime_to_user_tz(utc_dt: datetime, user_tz: str) -> datetime:
        """Convert UTC datetime to user's timezone"""
        try:
            utc_dt = utc_dt.replace(tzinfo=pytz.UTC)
            user_timezone = pytz.timezone(user_tz)
            return utc_dt.astimezone(user_timezone)
        except Exception:
            return utc_dt
    
    @staticmethod
    def format_time_for_display(dt: datetime, format_type: str = 'short') -> str:
        """Format datetime for display based on type"""
        if format_type == 'short':
            return dt.strftime('%H:%M')
        elif format_type == 'medium':
            return dt.strftime('%I:%M %p')
        elif format_type == 'long':
            return dt.strftime('%b %d, %I:%M %p')
        else:
            return dt.strftime('%H:%M')
    
    @staticmethod
    def create_time_placeholder(utc_dt: datetime, sender_tz: str) -> str:
        """Create time placeholder in sender's timezone"""
        sender_dt = TimezoneConverter.convert_datetime_to_user_tz(utc_dt, sender_tz)
        time_str = TimezoneConverter.format_time_for_display(sender_dt, 'short')
        return f'[{time_str}]'
    
    @staticmethod
    def parse_time_placeholder(message: str) -> Optional[datetime]:
        """Extract original UTC time from message with placeholder"""
        match = re.search(TimezoneConverter.TIME_PLACEHOLDER_PATTERN, message)
        if match:
            # We'll store the original UTC timestamp in a separate field
            # This is handled in the message model
            return None
        return None
    
    @staticmethod
    def replace_time_placeholder_for_user(message: str, original_utc_dt: datetime, 
                                        user_tz: str, original_sender_tz: str) -> str:
        """Replace time placeholder with user's local time"""
        # Convert to user's timezone
        user_dt = TimezoneConverter.convert_datetime_to_user_tz(original_utc_dt, user_tz)
        user_time_str = TimezoneConverter.format_time_for_display(user_dt, 'short')
        
        # Create new placeholder with user's time
        new_placeholder = f'[{user_time_str}]'
        
        # Replace the placeholder in the message
        pattern = TimezoneConverter.TIME_PLACEHOLDER_PATTERN
        return re.sub(pattern, new_placeholder, message)
    
    @staticmethod
    def get_time_display_info(utc_dt: datetime, user_tz: str) -> Dict[str, Any]:
        """Get comprehensive time display information for a user"""
        user_dt = TimezoneConverter.convert_datetime_to_user_tz(utc_dt, user_tz)
        
        return {
            'time_short': TimezoneConverter.format_time_for_display(user_dt, 'short'),
            'time_medium': TimezoneConverter.format_time_for_display(user_dt, 'medium'),
            'time_long': TimezoneConverter.format_time_for_display(user_dt, 'long'),
            'timezone': user_tz,
            'is_today': user_dt.date() == datetime.now().date(),
            'is_yesterday': user_dt.date() == (datetime.now() - timedelta(days=1)).date(),
            'date': user_dt.strftime('%Y-%m-%d'),
            'day_name': user_dt.strftime('%A'),
        }
    
    @staticmethod
    def batch_convert_messages(messages: list, user_tz: str) -> list:
        """Batch convert multiple messages for a user"""
        converted_messages = []
        
        for message in messages:
            if hasattr(message, 'content') and hasattr(message, 'created_at'):
                converted_content = TimezoneConverter.replace_time_placeholder_for_user(
                    message.content,
                    message.created_at,
                    user_tz,
                    getattr(message, 'sender_timezone', 'UTC')
                )
                
                # Create converted message copy
                converted_msg = {
                    'id': message.id,
                    'content': converted_content,
                    'original_content': message.content,
                    'created_at': message.created_at,
                    'display_time': TimezoneConverter.get_time_display_info(
                        message.created_at, user_tz
                    ),
                    'sender_id': message.sender_id,
                    'conversation_id': message.conversation_id
                }
                converted_messages.append(converted_msg)
        
        return converted_messages

# Helper function to get user's timezone from user object
def get_user_timezone(user) -> str:
    """Extract timezone from user object"""
    if hasattr(user, 'pref_timezone') and user.pref_timezone:
        return user.pref_timezone
    elif hasattr(user, 'profile_country') and user.profile_country:
        return TimezoneConverter.get_user_timezone(user.profile_country)
    else:
        return 'UTC'