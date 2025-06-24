"""Search tool for Eagle - searches files and directories."""

import os
import re
import glob
from typing import Dict, Any, List
from eagle_lang.tools.base import EagleTool


class SearchTool(EagleTool):
    """Tool for searching files and directories."""
    
    @property
    def name(self) -> str:
        return "search"
    
    @property
    def description(self) -> str:
        return "Search for files by name/pattern or search for text content within files"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query - file pattern (*.py) or text to search for"
                },
                "search_type": {
                    "type": "string",
                    "enum": ["files", "content"],
                    "description": "Type of search - 'files' to find files by name/pattern, 'content' to search text within files",
                    "default": "content"
                },
                "directory": {
                    "type": "string",
                    "description": "Directory to search in (default: current directory)",
                    "default": "."
                },
                "file_pattern": {
                    "type": "string",
                    "description": "File pattern to limit search (e.g., '*.py', '*.js') - only used with content search",
                    "default": "*"
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Whether to search recursively in subdirectories",
                    "default": True
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "Whether search should be case sensitive (content search only)",
                    "default": False
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 50,
                    "maximum": 200
                }
            },
            "required": ["query"]
        }
    
    @property
    def usage_patterns(self) -> Dict[str, Any]:
        return {
            "category": "file_operations",
            "patterns": [
                "Find files by name or pattern",
                "Search for specific content within files",
                "Locate code patterns or functions",
                "Discover project structure and organization"
            ],
            "workflows": {
                "Code Discovery": ["search", "read", "print"],
                "Project Analysis": ["search", "read", "write"],
                "Refactoring": ["search", "read", "write", "shell"]
            }
        }
    
    def execute(self, query: str, search_type: str = "content", directory: str = ".", 
                file_pattern: str = "*", recursive: bool = True, case_sensitive: bool = False, 
                max_results: int = 50) -> str:
        """Execute the search tool."""
        if search_type == "files":
            return self._search_files(query, directory, recursive, max_results)
        else:
            return self._search_content(query, directory, file_pattern, recursive, case_sensitive, max_results)
    
    def _search_files(self, pattern: str, directory: str, recursive: bool, max_results: int) -> str:
        """Search for files by name/pattern."""
        try:
            if not os.path.exists(directory):
                return f"Directory not found: {directory}"
            
            matches = []
            
            if recursive:
                # Use glob for recursive search
                search_pattern = os.path.join(directory, "**", pattern)
                matches = glob.glob(search_pattern, recursive=True)
            else:
                # Search only in specified directory
                search_pattern = os.path.join(directory, pattern)
                matches = glob.glob(search_pattern)
            
            # Filter to only files (not directories)
            file_matches = [f for f in matches if os.path.isfile(f)]
            
            # Limit results
            file_matches = file_matches[:max_results]
            
            if not file_matches:
                return f"No files found matching pattern: {pattern}"
            
            result = f"Found {len(file_matches)} file(s) matching '{pattern}' in {directory}:\n\n"
            for i, file_path in enumerate(file_matches, 1):
                # Make path relative to current directory for cleaner output
                rel_path = os.path.relpath(file_path)
                result += f"{i:3d}. {rel_path}\n"
            
            if len(matches) > max_results:
                result += f"\n(Showing first {max_results} results, {len(matches) - max_results} more found)"
            
            return result
            
        except Exception as e:
            return f"Error searching for files: {str(e)}"
    
    def _search_content(self, query: str, directory: str, file_pattern: str, 
                       recursive: bool, case_sensitive: bool, max_results: int) -> str:
        """Search for text content within files."""
        try:
            if not os.path.exists(directory):
                return f"Directory not found: {directory}"
            
            # Compile regex pattern
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                pattern = re.compile(query, flags)
            except re.error as e:
                return f"Invalid regex pattern: {query}. Error: {str(e)}"
            
            matches = []
            files_searched = 0
            
            # Get files to search
            if recursive:
                search_glob = os.path.join(directory, "**", file_pattern)
                files = glob.glob(search_glob, recursive=True)
            else:
                search_glob = os.path.join(directory, file_pattern)
                files = glob.glob(search_glob)
            
            # Filter to only files
            files = [f for f in files if os.path.isfile(f)]
            
            for file_path in files:
                try:
                    files_searched += 1
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if pattern.search(line):
                                rel_path = os.path.relpath(file_path)
                                matches.append({
                                    'file': rel_path,
                                    'line': line_num,
                                    'content': line.strip()
                                })
                                
                                if len(matches) >= max_results:
                                    break
                    
                    if len(matches) >= max_results:
                        break
                        
                except (UnicodeDecodeError, PermissionError):
                    # Skip files that can't be read
                    continue
            
            if not matches:
                return f"No matches found for '{query}' in {files_searched} files searched"
            
            result = f"Found {len(matches)} match(es) for '{query}' in {files_searched} files:\n\n"
            
            for i, match in enumerate(matches, 1):
                result += f"{i:3d}. {match['file']}:{match['line']}\n"
                result += f"     {match['content']}\n\n"
            
            if len(matches) >= max_results:
                result += f"(Showing first {max_results} results)"
            
            return result
            
        except Exception as e:
            return f"Error searching content: {str(e)}"