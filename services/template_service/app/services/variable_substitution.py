import re
from typing import Dict, Any

class VariableSubstitutionService:
    def __init__(self):
        self.pattern = re.compile(r'\{\{(\w+)\}\}')

    def substitute(self, template: str, variables: Dict[str, Any]) -> str:
        """Substitute variables in template"""
        def replace_var(match):
            var_name = match.group(1)
            return str(variables.get(var_name, match.group(0)))

        return self.pattern.sub(replace_var, template)
