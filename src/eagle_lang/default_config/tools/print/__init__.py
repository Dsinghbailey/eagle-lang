"""Print tool for Eagle - outputs content to terminal/console."""

from typing import Dict, Any
from eagle_lang.tools.base import EagleTool


class PrintTool(EagleTool):
    """Tool for printing content to terminal/console."""
    
    @property
    def name(self) -> str:
        return "print"
    
    @property
    def description(self) -> str:
        return "Print content to the terminal/console with optional formatting"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The content to print to the console"
                },
                "style": {
                    "type": "string",
                    "enum": ["plain", "header", "info", "success", "warning", "error"],
                    "description": "Style of output - plain (default), header, info, success, warning, or error",
                    "default": "plain"
                },
                "newline": {
                    "type": "boolean",
                    "description": "Whether to add a newline after the content",
                    "default": True
                }
            },
            "required": ["content"]
        }
    
    @property
    def usage_patterns(self) -> Dict[str, Any]:
        return {
            "category": "communication",
            "patterns": [
                "Display results and status updates",
                "Show formatted output with styling",
                "Provide user feedback during operations",
                "Present analysis results and summaries"
            ],
            "workflows": {
                "Status Updates": ["print"],
                "Results Display": ["read", "print"],
                "Progress Reporting": ["shell", "print", "shell"]
            }
        }
    
    def execute(self, content: str, style: str = "plain", newline: bool = True) -> str:
        """Execute the print tool."""
        return self._print_to_console(content, style, newline)
    
    def _print_to_console(self, content: str, style: str, newline: bool) -> str:
        """Print content to console with formatting."""
        try:
            # Apply styling
            if style == "header":
                formatted_content = f"\n=== {content} ==="
            elif style == "info":
                formatted_content = f"ℹ️  {content}"
            elif style == "success":
                formatted_content = f"✅ {content}"
            elif style == "warning":
                formatted_content = f"⚠️  {content}"
            elif style == "error":
                formatted_content = f"❌ {content}"
            else:  # plain
                formatted_content = content
            
            # Print with or without newline
            if newline:
                print(formatted_content)
            else:
                print(formatted_content, end="")
            
            return f"Content printed to console ({style} style)"
            
        except Exception as e:
            return f"Error printing to console: {str(e)}"