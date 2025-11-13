import re
from typing import List, Dict

def parse_variables(template: str) -> List[str]:
    """Extract variable names from template"""
    pattern = r'\{\{(\w+)\}\}'
    matches = re.findall(pattern, template)
    return list(set(matches))

def validate_template(template: str, variables: Dict[str, str]) -> bool:
    """Validate that template has all required variables"""
    required_vars = parse_variables(template)
    return all(var in variables for var in required_vars)

def get_template_info(template: str) -> Dict:
    """Get information about template"""
    variables = parse_variables(template)
    return {
        "variables": variables,
        "variable_count": len(variables),
        "has_subject": "{{subject}}" in template or "{{SUBJECT}}" in template
    }
