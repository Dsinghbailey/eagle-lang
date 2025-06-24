"""Read tool for Eagle - reads file contents."""

import os
from typing import Dict, Any, List
from eagle_lang.tools.base import EagleTool


class ReadTool(EagleTool):
    """Tool for reading file contents."""
    
    @property
    def name(self) -> str:
        return "read"
    
    @property
    def description(self) -> str:
        return "Read contents of one or more files, with optional line range support"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read (or comma-separated paths for multiple files)"
                },
                "start_line": {
                    "type": "integer",
                    "description": "Starting line number (1-based, optional)",
                    "minimum": 1
                },
                "end_line": {
                    "type": "integer",
                    "description": "Ending line number (1-based, optional)",
                    "minimum": 1
                },
                "max_lines": {
                    "type": "integer",
                    "description": "Maximum number of lines to read (default: 1000)",
                    "default": 1000,
                    "maximum": 5000
                },
                "encoding": {
                    "type": "string",
                    "description": "File encoding (default: utf-8)",
                    "default": "utf-8"
                }
            },
            "required": ["file_path"]
        }
    
    @property
    def usage_patterns(self) -> Dict[str, Any]:
        return {
            "category": "file_operations", 
            "patterns": [
                "Read and analyze existing files",
                "Load configuration or data files", 
                "Examine source code before modifications",
                "Read multiple files for comparison or compilation"
            ],
            "workflows": {
                "Code Analysis": ["read", "print"],
                "File Processing": ["read", "shell", "write"],
                "Documentation Review": ["search", "read", "write"],
                "Data Loading": ["read", "web", "write"]
            }
        }
    
    def execute(self, file_path: str, start_line: int = None, end_line: int = None, 
                max_lines: int = 1000, encoding: str = "utf-8") -> str:
        """Execute the read tool."""
        # Handle multiple files
        file_paths = [path.strip() for path in file_path.split(",")]
        
        if len(file_paths) == 1:
            return self._read_single_file(file_paths[0], start_line, end_line, max_lines, encoding)
        else:
            return self._read_multiple_files(file_paths, max_lines, encoding)
    
    def _read_single_file(self, file_path: str, start_line: int, end_line: int, 
                          max_lines: int, encoding: str) -> str:
        """Read a single file with sandboxing."""
        try:
            # Sandboxing: Only allow reads from current directory or lower
            abs_path = os.path.abspath(file_path)
            cwd = os.path.abspath(os.getcwd())
            
            if not abs_path.startswith(cwd):
                return f"Access denied: Can only read from current directory or subdirectories. Path: {abs_path}"
            
            if not os.path.exists(file_path):
                return f"File not found: {file_path}"
            
            if not os.path.isfile(file_path):
                return f"Path is not a file: {file_path}"
            
            with open(file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            
            # Handle line range
            if start_line is not None:
                start_idx = max(0, start_line - 1)  # Convert to 0-based
            else:
                start_idx = 0
            
            if end_line is not None:
                end_idx = min(total_lines, end_line)  # Convert to 0-based + 1
            else:
                end_idx = min(total_lines, start_idx + max_lines)
            
            # Limit to max_lines
            if end_idx - start_idx > max_lines:
                end_idx = start_idx + max_lines
                truncated = True
            else:
                truncated = False
            
            selected_lines = lines[start_idx:end_idx]
            content = ''.join(selected_lines)
            
            # Build result
            result = f"File: {file_path}\n"
            result += f"Lines: {start_idx + 1}-{end_idx} (of {total_lines} total)\n"
            if truncated:
                result += f"(Output truncated to {max_lines} lines)\n"
            result += f"{'=' * 50}\n"
            result += content
            
            if not content.endswith('\n'):
                result += '\n'
            
            return result
            
        except UnicodeDecodeError:
            return f"Unable to decode file with {encoding} encoding: {file_path}"
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"
    
    def _read_multiple_files(self, file_paths: List[str], max_lines: int, encoding: str) -> str:
        """Read multiple files."""
        results = []
        lines_per_file = max_lines // len(file_paths)
        
        for file_path in file_paths:
            result = self._read_single_file(file_path, None, None, lines_per_file, encoding)
            results.append(result)
        
        return "\n\n".join(results)