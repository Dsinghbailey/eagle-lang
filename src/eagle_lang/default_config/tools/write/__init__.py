"""Write tool for Eagle - handles file creation and writing."""

import os
from typing import Dict, Any
from eagle_lang.tools.base import EagleTool


class WriteTool(EagleTool):
    """Tool for creating and writing to files."""
    
    @property
    def name(self) -> str:
        return "write"
    
    @property
    def description(self) -> str:
        return "Create or write content to a file"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The content to write to the file"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to write to"
                },
                "mode": {
                    "type": "string",
                    "enum": ["write", "append"],
                    "description": "File write mode - 'write' (default) overwrites file, 'append' adds to existing file",
                    "default": "write"
                }
            },
            "required": ["content", "file_path"]
        }
    
    @property
    def usage_patterns(self) -> Dict[str, Any]:
        return {
            "category": "file_operations",
            "patterns": [
                "Create new files with generated content",
                "Save analysis results to files",
                "Generate code files and documentation",
                "Append to log files or ongoing documents"
            ],
            "workflows": {
                "Content Generation": ["read", "write"],
                "Data Processing": ["read", "shell", "write"],
                "Documentation": ["search", "read", "write"],
                "Code Generation": ["read", "write", "shell"]
            }
        }
    
    def execute(self, content: str, file_path: str, mode: str = "write") -> str:
        """Execute the write tool."""
        return self._write_to_file(content, file_path, mode)
    
    def _write_to_file(self, content: str, file_path: str, mode: str) -> str:
        """Write content to a file with sandboxing."""
        try:
            # Sandboxing: Only allow writes to current directory or lower
            abs_path = os.path.abspath(file_path)
            cwd = os.path.abspath(os.getcwd())
            
            if not abs_path.startswith(cwd):
                return f"Access denied: Can only write to current directory or subdirectories. Path: {abs_path}"
            
            # Ensure directory exists
            directory = os.path.dirname(abs_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Write or append to file
            file_mode = "a" if mode == "append" else "w"
            with open(abs_path, file_mode, encoding="utf-8") as f:
                f.write(content)
            
            action = "appended to" if mode == "append" else "written to"
            return f"Content successfully {action} file: {file_path}"
            
        except PermissionError:
            return f"Permission denied: Cannot write to {file_path}"
        except Exception as e:
            return f"Error writing to file {file_path}: {str(e)}"