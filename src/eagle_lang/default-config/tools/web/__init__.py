"""Web tool for Eagle - fetches web content and makes HTTP requests."""

import urllib.request
import urllib.parse
import json
import re
from typing import Dict, Any, List, Optional
from eagle_lang.tools.base import EagleTool, tool_registry

try:
    from html.parser import HTMLParser
    import html
    HTML_AVAILABLE = True
except ImportError:
    HTML_AVAILABLE = False


class SimpleHTMLParser(HTMLParser):
    """Simple HTML parser to extract useful content."""
    
    def __init__(self):
        super().__init__()
        self.text_content = []
        self.links = []
        self.titles = []
        self.current_tag = None
        self.in_script = False
        self.in_style = False
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        if tag in ['script', 'style']:
            self.in_script = True
            self.in_style = True
        elif tag == 'a':
            # Extract href from links
            for attr_name, attr_value in attrs:
                if attr_name == 'href' and attr_value:
                    self.links.append(attr_value)
        elif tag in ['h1', 'h2', 'h3', 'title']:
            self.current_tag = f"{tag}_start"
    
    def handle_endtag(self, tag):
        if tag in ['script', 'style']:
            self.in_script = False
            self.in_style = False
        self.current_tag = None
    
    def handle_data(self, data):
        if self.in_script or self.in_style:
            return
            
        text = data.strip()
        if text:
            if self.current_tag and self.current_tag.endswith('_start'):
                self.titles.append(text)
            else:
                self.text_content.append(text)
    
    def get_clean_text(self) -> str:
        """Get clean text content."""
        return '\n'.join(self.text_content)
    
    def get_titles(self) -> List[str]:
        """Get all titles/headings."""
        return self.titles
    
    def get_links(self) -> List[str]:
        """Get all links."""
        return self.links


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
                "purpose": {
                    "type": "string",
                    "description": "What you want to extract/find from the webpage (e.g., 'trending topics', 'product prices', 'contact information')"
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
                },
                "raw": {
                    "type": "boolean",
                    "description": "Return raw content without AI processing (default: false)",
                    "default": False
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
    
    def execute(self, url: str, purpose: str = None, method: str = "GET", headers: Dict[str, str] = None, 
                data: str = None, timeout: int = 30, max_content_length: int = 1048576, raw: bool = False) -> str:
        """Execute the web tool."""
        raw_content = self._make_request(url, method, headers, data, timeout, max_content_length)
        
        # If raw requested or no purpose given, return raw content
        if raw or not purpose:
            return raw_content
        
        # Try to parse and extract relevant information
        return self._process_content(raw_content, purpose, url)
    
    def _process_content(self, raw_content: str, purpose: str, url: str) -> str:
        """Process HTML content to extract relevant information."""
        if not HTML_AVAILABLE:
            return raw_content
        
        try:
            # Extract the actual HTML content from the raw response
            html_content = self._extract_html_from_response(raw_content)
            if not html_content:
                return raw_content
            
            # Parse HTML
            parser = SimpleHTMLParser()
            parser.feed(html_content)
            
            # Get structured data
            clean_text = parser.get_clean_text()
            titles = parser.get_titles()
            links = parser.get_links()
            
            # Apply intelligent filtering based on purpose
            filtered_content = self._filter_content_by_purpose(clean_text, titles, links, purpose)
            
            # Format results
            result = f"🌐 Web Content from {url}\n"
            result += f"📋 Purpose: {purpose}\n"
            result += "=" * 50 + "\n"
            result += filtered_content
            
            return result
            
        except Exception as e:
            # Fallback to raw content if parsing fails
            return f"⚠️ Could not parse content: {str(e)}\n\n{raw_content}"
    
    def _extract_html_from_response(self, raw_response: str) -> Optional[str]:
        """Extract HTML content from the raw HTTP response."""
        # Look for the content after the headers
        separator = "\n" + "=" * 50 + "\n"
        if separator in raw_response:
            return raw_response.split(separator, 1)[1]
        return None
    
    def _filter_content_by_purpose(self, text: str, titles: List[str], links: List[str], purpose: str) -> str:
        """Filter content based on the stated purpose."""
        purpose_lower = purpose.lower()
        lines = text.split('\n')
        
        # Trending/trending topics
        if 'trend' in purpose_lower:
            relevant_lines = self._find_trending_content(lines, titles)
            return self._format_trending_results(relevant_lines, titles)
        
        # Prices/pricing
        elif 'price' in purpose_lower or 'cost' in purpose_lower:
            relevant_lines = self._find_price_content(lines)
            return '\n'.join(relevant_lines[:20])  # Limit to 20 lines
        
        # Contact information
        elif 'contact' in purpose_lower:
            relevant_lines = self._find_contact_content(lines)
            return '\n'.join(relevant_lines[:15])
        
        # News/articles
        elif 'news' in purpose_lower or 'article' in purpose_lower:
            return self._format_news_content(lines, titles)
        
        # Default: return cleaned text with reasonable limits
        else:
            # Limit to most relevant content (first 30 lines of meaningful text)
            filtered_lines = [line for line in lines if len(line.strip()) > 10][:30]
            result = '\n'.join(filtered_lines)
            
            # Add titles if available
            if titles:
                result = "📰 Headlines/Titles:\n" + '\n'.join(f"• {title}" for title in titles[:10]) + "\n\n" + result
            
            return result
    
    def _find_trending_content(self, lines: List[str], titles: List[str]) -> List[str]:
        """Find content related to trends."""
        trend_keywords = ['trend', 'trending', 'popular', 'viral', 'hot', '#', '@', 'hashtag']
        relevant_lines = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in trend_keywords):
                relevant_lines.append(line)
            elif re.search(r'#\w+', line):  # Hashtags
                relevant_lines.append(line)
        
        return relevant_lines[:25]  # Limit results
    
    def _format_trending_results(self, content_lines: List[str], titles: List[str]) -> str:
        """Format trending content nicely."""
        result = ""
        
        if titles:
            result += "🔥 Trending Headlines:\n"
            for title in titles[:8]:
                result += f"• {title}\n"
            result += "\n"
        
        if content_lines:
            result += "📈 Trending Content:\n"
            # Look for hashtags and clean formatting
            hashtags = set(re.findall(r'#\w+', '\n'.join(content_lines)))
            if hashtags:
                result += f"🏷️ Hashtags: {', '.join(sorted(hashtags)[:10])}\n\n"
            
            for line in content_lines[:15]:
                if line.strip():
                    result += f"• {line.strip()}\n"
        
        return result if result else "No trending content found"
    
    def _find_price_content(self, lines: List[str]) -> List[str]:
        """Find content related to prices."""
        price_patterns = [r'\$\d+', r'€\d+', r'£\d+', r'\d+\.\d+', r'price', r'cost', r'fee']
        relevant_lines = []
        
        for line in lines:
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in price_patterns):
                relevant_lines.append(line)
        
        return relevant_lines
    
    def _find_contact_content(self, lines: List[str]) -> List[str]:
        """Find content related to contact information."""
        contact_keywords = ['email', 'phone', 'contact', 'address', '@', 'tel:', 'mailto:']
        relevant_lines = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in contact_keywords):
                relevant_lines.append(line)
        
        return relevant_lines
    
    def _format_news_content(self, lines: List[str], titles: List[str]) -> str:
        """Format news/article content."""
        result = ""
        
        if titles:
            result += "📰 Headlines:\n"
            for title in titles[:5]:
                result += f"• {title}\n"
            result += "\n"
        
        # Get first few paragraphs of meaningful content
        paragraphs = []
        current_para = []
        
        for line in lines:
            line = line.strip()
            if len(line) > 20:  # Meaningful content
                current_para.append(line)
            elif current_para:
                paragraphs.append(' '.join(current_para))
                current_para = []
        
        if current_para:
            paragraphs.append(' '.join(current_para))
        
        result += "📄 Content:\n"
        for para in paragraphs[:3]:  # First 3 paragraphs
            result += f"{para}\n\n"
        
        return result
    
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