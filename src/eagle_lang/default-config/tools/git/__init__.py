"""Git tool for Eagle - performs git operations."""

import subprocess
import os
from typing import Dict, Any
from eagle_lang.tools.base import EagleTool


class GitTool(EagleTool):
    """Tool for git operations."""
    
    @property
    def name(self) -> str:
        return "git"
    
    @property
    def description(self) -> str:
        return "Perform git operations like status, diff, add, commit, push, pull, etc."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["status", "diff", "add", "commit", "push", "pull", "log", "branch", "checkout", "stash", "reset"],
                    "description": "Git operation to perform"
                },
                "args": {
                    "type": "string",
                    "description": "Additional arguments for the git command (e.g., file paths, commit message, branch name)"
                },
                "directory": {
                    "type": "string",
                    "description": "Directory to run git command in (default: current directory)",
                    "default": "."
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 60)",
                    "default": 60,
                    "maximum": 300
                }
            },
            "required": ["operation"]
        }
    
    @property
    def usage_patterns(self) -> Dict[str, Any]:
        return {
            "category": "version_control",
            "patterns": [
                "Check repository status and changes",
                "Commit and push code changes",
                "Manage branches and git workflow",
                "View commit history and diffs"
            ],
            "workflows": {
                "Development Workflow": ["git", "shell", "git", "git"],
                "Code Review": ["git", "read", "print"],
                "Release Process": ["git", "shell", "git", "ask_permission"]
            }
        }
    
    def execute(self, operation: str, args: str = "", directory: str = ".", timeout: int = 60) -> str:
        """Execute the git tool."""
        # Check if directory is a git repository
        if not self._is_git_repo(directory):
            return f"Not a git repository: {directory}"
        
        return self._run_git_command(operation, args, directory, timeout)
    
    def _is_git_repo(self, directory: str) -> bool:
        """Check if directory is a git repository."""
        git_dir = os.path.join(directory, ".git")
        return os.path.exists(git_dir) or self._has_git_repo_parent(directory)
    
    def _has_git_repo_parent(self, directory: str) -> bool:
        """Check if any parent directory contains a .git folder."""
        current = os.path.abspath(directory)
        while current != os.path.dirname(current):  # Not at root
            if os.path.exists(os.path.join(current, ".git")):
                return True
            current = os.path.dirname(current)
        return False
    
    def _run_git_command(self, operation: str, args: str, directory: str, timeout: int) -> str:
        """Run git command with sandboxing."""
        try:
            # Sandboxing: Check for dangerous git operations
            if not self._is_safe_git_operation(operation, args):
                return f"Git operation blocked for safety: git {operation} {args}"
            
            # Build git command
            cmd_parts = ["git", operation]
            
            # Add arguments based on operation
            if operation == "commit":
                # Handle commit with message
                if args:
                    if not args.startswith("-m"):
                        cmd_parts.extend(["-m", args])
                    else:
                        cmd_parts.extend(args.split(" ", 1))
                else:
                    return "Commit operation requires a message in args parameter"
            
            elif operation == "add":
                # Handle add with file paths
                if args:
                    cmd_parts.extend(args.split())
                else:
                    cmd_parts.append(".")  # Add all files if no args
            
            elif operation == "checkout":
                # Handle checkout with branch/file
                if args:
                    cmd_parts.extend(args.split())
                else:
                    return "Checkout operation requires branch name or file path in args parameter"
            
            elif operation == "branch":
                # Handle branch operations
                if args:
                    cmd_parts.extend(args.split())
            
            elif operation == "log":
                # Handle log with options
                if args:
                    cmd_parts.extend(args.split())
                else:
                    cmd_parts.extend(["--oneline", "-10"])  # Default: show last 10 commits
            
            elif operation == "diff":
                # Handle diff with options
                if args:
                    cmd_parts.extend(args.split())
            
            elif operation == "stash":
                # Handle stash operations
                if args:
                    cmd_parts.extend(args.split())
                else:
                    cmd_parts.append("list")  # Default: list stashes
            
            elif operation == "reset":
                # Handle reset operations
                if args:
                    cmd_parts.extend(args.split())
                else:
                    return "Reset operation requires arguments (e.g., 'HEAD~1', '--hard HEAD')"
            
            elif args:
                # For other operations, just add args
                cmd_parts.extend(args.split())
            
            # Execute command
            result = subprocess.run(
                cmd_parts,
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Format output
            output_parts = []
            
            if result.stdout:
                output_parts.append(f"Output:\n{result.stdout}")
            
            if result.stderr:
                output_parts.append(f"Error/Warning:\n{result.stderr}")
            
            if result.returncode == 0:
                status = f"Git {operation} completed successfully"
            else:
                status = f"Git {operation} failed (exit code: {result.returncode})"
            
            output_parts.append(f"Status: {status}")
            
            return "\n\n".join(output_parts)
            
        except subprocess.TimeoutExpired:
            return f"Git {operation} timed out after {timeout} seconds"
        except FileNotFoundError:
            return "Git command not found. Make sure git is installed and in your PATH."
        except Exception as e:
            return f"Error running git {operation}: {str(e)}"
    
    def _is_safe_git_operation(self, operation: str, args: str) -> bool:
        """Check if git operation is safe with common sense protection."""
        # Basic dangerous git operations - common sense protection only
        
        # Don't allow hard resets that could lose work
        if operation == "reset" and "--hard" in args:
            return False
        
        # Don't allow force pushes that could overwrite remote history
        if operation == "push" and ("--force" in args or "-f" in args):
            return False
        
        # Don't allow cleaning that could delete untracked files
        if operation == "clean" and ("-f" in args or "-d" in args):
            return False
        
        return True