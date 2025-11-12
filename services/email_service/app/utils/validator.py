import re
from typing import Dict

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_variables(variables: Dict[str, str]) -> bool:
    """Validate that variables are strings and not empty"""
    if not isinstance(variables, dict):
        return False
    return all(isinstance(v, str) and v.strip() for v in variables.values())
