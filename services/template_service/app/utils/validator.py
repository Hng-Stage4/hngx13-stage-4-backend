import re
from typing import Dict

def validate_template_id(template_id: str) -> bool:
    """Validate template ID format"""
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, template_id))

def validate_language_code(code: str) -> bool:
    """Validate language code format"""
    pattern = r'^[a-z]{2}(-[A-Z]{2})?$'
    return bool(re.match(pattern, code))

def validate_variables(variables: Dict[str, str]) -> bool:
    """Validate variables dict"""
    if not isinstance(variables, dict):
        return False
    return all(isinstance(k, str) and isinstance(v, str) for k, v in variables.items())
