import json
import shlex
from typing import Dict, Any
from fastapi import HTTPException

def parse_curl_command(curl_command: str) -> Dict[str, Any]:
    """Parse curl command and extract URL, headers, and body"""
    try:
        # Remove 'curl' from the beginning
        curl_command = curl_command.strip()
        if curl_command.startswith('curl '):
            curl_command = curl_command[5:]
        
        # Split command into parts
        parts = shlex.split(curl_command)
        
        url = ""
        headers = {}
        body = {}
        method = "GET"
        
        i = 0
        while i < len(parts):
            part = parts[i]
            
            # Extract URL (first non-flag argument)
            if not part.startswith('-') and not url:
                url = part
            
            # Extract headers
            elif part == '-H' or part == '--header':
                if i + 1 < len(parts):
                    header_line = parts[i + 1]
                    if ':' in header_line:
                        key, value = header_line.split(':', 1)
                        headers[key.strip()] = value.strip()
                    i += 1
            
            # Extract method
            elif part == '-X' or part == '--request':
                if i + 1 < len(parts):
                    method = parts[i + 1]
                    i += 1
            
            # Extract body data
            elif part == '-d' or part == '--data':
                if i + 1 < len(parts):
                    try:
                        body = json.loads(parts[i + 1])
                    except json.JSONDecodeError:
                        body = {"data": parts[i + 1]}
                    i += 1
            
            i += 1
        
        # Create request body template with variables
        request_body_template = body.copy() if body else {}
        
        # Replace common prompt fields with variables
        if "prompt" in request_body_template:
            request_body_template["prompt"] = "{prompt}"
        if "message" in request_body_template:
            request_body_template["message"] = "{prompt}"
        if "input" in request_body_template:
            request_body_template["input"] = "{prompt}"
        if "text" in request_body_template:
            request_body_template["text"] = "{prompt}"
        
        # Add common parameters
        if "max_tokens" not in request_body_template:
            request_body_template["max_tokens"] = "{max_tokens}"
        if "temperature" not in request_body_template:
            request_body_template["temperature"] = "{temperature}"
        if "model" not in request_body_template:
            request_body_template["model"] = "{model}"
        
        return {
            "base_url": url,
            "headers": headers,
            "request_body_template": request_body_template,
            "response_parser": {
                "content_path": "choices.0.message.content"  # Default parser
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse curl command: {str(e)}")