"""
Custom Validators
"""

from typing import Any


def validate_notification_type(notification_type: str) -> bool:
    """
    Validate notification type
    """
    valid_types = ["email", "push", "sms"]
    return notification_type in valid_types


def validate_priority(priority: int) -> bool:
    """
    Validate priority value
    """
    return 1 <= priority <= 10


def sanitize_template_variables(variables: dict) -> dict:
    """
    Sanitize template variables
    """
    # Remove potentially dangerous content
    sanitized = {}
    for key, value in variables.items():
        if isinstance(value, str):
            # Basic XSS prevention
            sanitized[key] = value.replace("<", "&lt;").replace(">", "&gt;")
        else:
            sanitized[key] = value
    return sanitized
