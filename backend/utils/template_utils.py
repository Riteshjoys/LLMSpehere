import json
from typing import Dict, Any

def substitute_variables(template: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
    """Substitute variables in request template"""
    template_str = json.dumps(template)
    for key, value in variables.items():
        template_str = template_str.replace(f"{{{key}}}", str(value))
    return json.loads(template_str)

def extract_response_content(response_data: Dict[str, Any], parser_config: Dict[str, str]) -> str:
    """Extract content from API response using parser configuration"""
    try:
        # Simple JSONPath-like extraction
        content_path = parser_config.get("content_path", "choices.0.message.content")
        
        current = response_data
        for key in content_path.split('.'):
            if key.isdigit():
                current = current[int(key)]
            else:
                current = current[key]
        
        return str(current)
    except (KeyError, IndexError, TypeError):
        # Fallback to raw response
        return str(response_data)