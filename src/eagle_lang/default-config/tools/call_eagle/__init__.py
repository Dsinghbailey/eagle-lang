"""Call Eagle tool - allows Eagle to recursively call itself with new instructions."""

import os
import tempfile
import subprocess
from typing import Dict, Any
from eagle_lang.tools.base import EagleTool


class CallEagleTool(EagleTool):
    """Tool for making recursive calls to Eagle with new instructions."""
    
    @property
    def name(self) -> str:
        return "call_eagle"
    
    @property
    def description(self) -> str:
        return "Call Eagle recursively with new instructions. Use this to break down complex tasks or delegate subtasks."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "instructions": {
                    "type": "string",
                    "description": "The instructions/task to give to the new Eagle instance"
                },
                "provider": {
                    "type": "string",
                    "description": "Optional: Override the AI provider for this call",
                    "enum": ["openai", "claude", "gemini", "openrouter"]
                },
                "model": {
                    "type": "string",
                    "description": "Optional: Override the model for this call"
                },
                "rules": {
                    "type": "string",
                    "description": "Optional: Override the rules file for this call"
                },
                "save_output": {
                    "type": "boolean",
                    "description": "Whether to save the output to a temporary file for later reference",
                    "default": False
                }
            },
            "required": ["instructions"]
        }
    
    def execute(self, instructions: str, provider: str = None, model: str = None, 
                rules: str = None, save_output: bool = False) -> str:
        """Execute the call_eagle tool."""
        try:
            # Create temporary .caw file with instructions
            with tempfile.NamedTemporaryFile(mode='w', suffix='.caw', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(instructions)
                temp_caw_path = temp_file.name
            
            # Build Eagle command
            cmd = ['eagle', 'run', temp_caw_path]
            
            # Add optional parameters
            if provider:
                cmd.extend(['--provider', provider])
            if model:
                cmd.extend(['--model', model])
            if rules:
                cmd.extend(['--rules', rules])
            
            # Execute Eagle command
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                    encoding='utf-8'
                )
                
                output = result.stdout
                error = result.stderr
                
                # Clean up temporary file
                try:
                    os.unlink(temp_caw_path)
                except:
                    pass
                
                if result.returncode == 0:
                    # Success
                    response = f"Eagle call completed successfully:\n\n{output}"
                    
                    if save_output:
                        # Save output to a file
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as output_file:
                            output_file.write(output)
                            response += f"\n\nOutput saved to: {output_file.name}"
                    
                    return response
                else:
                    # Error
                    return f"Eagle call failed (exit code {result.returncode}):\n\nStdout:\n{output}\n\nStderr:\n{error}"
                    
            except subprocess.TimeoutExpired:
                return "Eagle call timed out after 5 minutes"
            except FileNotFoundError:
                return "Error: 'eagle' command not found. Make sure Eagle is installed and in your PATH."
            
        except Exception as e:
            # Clean up temporary file if it exists
            try:
                if 'temp_caw_path' in locals():
                    os.unlink(temp_caw_path)
            except:
                pass
            
            return f"Error executing Eagle call: {str(e)}"