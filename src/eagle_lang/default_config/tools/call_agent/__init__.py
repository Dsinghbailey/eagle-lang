"""Call Agent tool - allows delegating subtasks to specialized agents."""

import os
import tempfile
import subprocess
from typing import Dict, Any
from eagle_lang.tools.base import EagleTool


class CallAgentTool(EagleTool):
    """Tool for delegating subtasks to specialized agents."""
    
    @property
    def name(self) -> str:
        return "call_agent"
    
    @property
    def description(self) -> str:
        return "Delegate subtasks to specialized agents. Use this to break down complex tasks or leverage different agent capabilities."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "instructions": {
                    "type": "string",
                    "description": "The instructions/task to give to the agent"
                },
                "agent": {
                    "type": "string",
                    "description": "Optional: Name of the specific agent to use for this task"
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
    
    def execute(self, instructions: str, agent: str = None, provider: str = None, model: str = None, 
                rules: str = None, save_output: bool = False) -> str:
        """Execute the call_agent tool."""
        try:
            # Create temporary .caw file with instructions
            with tempfile.NamedTemporaryFile(mode='w', suffix='.caw', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(instructions)
                temp_caw_path = temp_file.name
            
            # Build Eagle command
            cmd = ['eagle', 'run', temp_caw_path]
            
            # Add optional parameters
            if agent:
                cmd.extend(['--agent', agent])
            if provider:
                cmd.extend(['--provider', provider])
            if model:
                cmd.extend(['--model', model])
            if rules:
                cmd.extend(['--rules', rules])
            
            # Execute Eagle command with interactive stdin for permission prompts
            try:
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=None,  # Inherit stdin to allow interactive prompts
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
                    agent_name = agent if agent else "default agent"
                    response = f"Agent call to {agent_name} completed successfully:\n\n{output}"
                    
                    if save_output:
                        # Save output to a file
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as output_file:
                            output_file.write(output)
                            response += f"\n\nOutput saved to: {output_file.name}"
                    
                    return response
                else:
                    # Error
                    agent_name = agent if agent else "default agent"
                    return f"Agent call to {agent_name} failed (exit code {result.returncode}):\n\nStdout:\n{output}\n\nStderr:\n{error}"
                    
            except subprocess.TimeoutExpired:
                return "Agent call timed out after 5 minutes"
            except FileNotFoundError:
                return "Error: 'eagle' command not found. Make sure Eagle is installed and in your PATH."
            
        except Exception as e:
            # Clean up temporary file if it exists
            try:
                if 'temp_caw_path' in locals():
                    os.unlink(temp_caw_path)
            except:
                pass
            
            return f"Error executing agent call: {str(e)}"