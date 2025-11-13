import re
from typing import Dict

def parse_template_variables(template: str) -> list:
    """Extract variable names from template"""
    pattern = r'\{\{(\w+)\}\}'
    matches = re.findall(pattern, template)
    return list(set(matches))

def validate_variables(template: str, variables: Dict[str, str]) -> bool:
    """Check if all required variables are provided"""
    required_vars = parse_template_variables(template)
    return all(var in variables for var in required_vars)
