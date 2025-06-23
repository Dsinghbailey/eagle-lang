"""Web tool for Eagle - fetches web content and makes HTTP requests."""

import urllib.request
import urllib.parse
import json
from typing import Dict, Any
from eagle_lang.tools.base import EagleTool


class WebTool(EagleTool):
    """Tool for fetching web content and making HTTP requests."""
    
    @property
    def name(self) -> str:
        return "web"
    
    @property
    def description(self) -> str:
        return "Fetch content from web URLs, make HTTP requests, or call REST APIs"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to fetch or make request to"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE"],
                    "description": "HTTP method to use (default: GET)",
                    "default": "GET"
                },
                "headers": {
                    "type": "object",
                    "description": "Optional HTTP headers as key-value pairs",
                    "additionalProperties": {"type": "string"}
                },
                "data": {
                    "type": "string",
                    "description": "Data to send with POST/PUT requests (JSON string or form data)"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 30, max: 120)",
                    "default": 30,
                    "maximum": 120
                },
                "max_content_length": {
                    "type": "integer",
                    "description": "Maximum content length to retrieve in bytes (default: 1MB)",
                    "default": 1048576,
                    "maximum": 10485760
                }
            },
            "required": ["url"]
        }
    
    @property
    def usage_patterns(self) -> Dict[str, Any]:
        return {
            "category": "external_data",
            "patterns": [
                "Fetch data from APIs and web services",
                "Download content and resources",
                "Make HTTP requests for integration",
                "Retrieve external information for analysis"
            ],
            "workflows": {
                "API Integration": ["web", "write", "read"],
                "Data Collection": ["web", "write", "shell"],
                "Content Fetching": ["web", "print", "write"]
            }
        }
    
    def execute(self, url: str, method: str = "GET", headers: Dict[str, str] = None, 
                data: str = None, timeout: int = 30, max_content_length: int = 1048576) -> str:
        """Execute the web tool."""
        return self._make_request(url, method, headers, data, timeout, max_content_length)
    
    def _make_request(self, url: str, method: str, headers: Dict[str, str], 
                     data: str, timeout: int, max_content_length: int) -> str:
        """Make HTTP request with sandboxing."""
        try:
            # Sandboxing: Validate URL
            if not url.startswith(('http://', 'https://')):
                return f"Invalid URL: {url}. Must start with http:// or https://"
            
            # Sandboxing: Check for dangerous/restricted URLs
            if not self._is_safe_url(url):
                return f"Access denied: URL blocked for security: {url}"
            
            # Sandboxing: Validate content length limits
            max_content_length = min(max_content_length, 10 * 1024 * 1024)  # Cap at 10MB
            
            # Prepare request
            if data and method in ['POST', 'PUT']:
                # Convert data to bytes
                if isinstance(data, str):
                    data_bytes = data.encode('utf-8')
                else:
                    data_bytes = data
            else:
                data_bytes = None
            
            # Create request
            req = urllib.request.Request(url, data=data_bytes, method=method)
            
            # Add headers
            if headers:
                for key, value in headers.items():
                    req.add_header(key, value)
            
            # Add default User-Agent if not provided
            if not headers or 'User-Agent' not in headers:
                req.add_header('User-Agent', 'Eagle-WebTool/1.0')
            
            # Add Content-Type for POST/PUT if data is provided and no Content-Type set
            if data_bytes and method in ['POST', 'PUT']:
                if not headers or 'Content-Type' not in headers:
                    # Try to detect if data is JSON
                    try:
                        json.loads(data)
                        req.add_header('Content-Type', 'application/json')
                    except (json.JSONDecodeError, TypeError):
                        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            # Make request
            with urllib.request.urlopen(req, timeout=timeout) as response:
                # Check content length
                content_length = response.headers.get('Content-Length')
                if content_length and int(content_length) > max_content_length:
                    return f"Content too large: {content_length} bytes (max: {max_content_length})"
                
                # Read response
                content = response.read()
                
                # Limit content size
                if len(content) > max_content_length:
                    content = content[:max_content_length]
                    truncated = True
                else:
                    truncated = False
                
                # Try to decode as text
                try:
                    text_content = content.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        text_content = content.decode('latin-1')
                    except UnicodeDecodeError:
                        return f"Binary content received ({len(content)} bytes). Cannot display as text."
                
                # Build result
                result = f"HTTP {response.status} {response.reason}\n"
                result += f"URL: {response.url}\n"
                result += f"Content-Type: {response.headers.get('Content-Type', 'unknown')}\n"
                result += f"Content-Length: {len(content)} bytes\n"
                
                if truncated:
                    result += f"(Content truncated to {max_content_length} bytes)\n"
                
                result += "\n" + "=" * 50 + "\n"
                result += text_content
                
                return result
                
        except urllib.error.HTTPError as e:
            return f"HTTP Error {e.code}: {e.reason}\nURL: {url}"
        except urllib.error.URLError as e:
            return f"URL Error: {e.reason}\nURL: {url}"
        except TimeoutError:
            return f"Request timed out after {timeout} seconds\nURL: {url}"
        except Exception as e:
            return f"Error making request: {str(e)}\nURL: {url}"
    
    def _is_safe_url(self, url: str) -> bool:
        """Check if URL is safe to access with common sense protection."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            
            # Block file:// and other dangerous schemes
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Block localhost/loopback - common sense protection
            hostname = parsed.hostname
            if hostname and hostname.lower() in ['localhost', '127.0.0.1', '0.0.0.0', '::1']:
                return False
            
            return True
            
        except Exception:
            return False