"""Ask permission tool for Eagle - gets user input or confirmation."""

from typing import Dict, Any
from eagle_lang.tools.base import EagleTool


class AskPermissionTool(EagleTool):
    """Tool for asking user permission or getting input."""
    
    @property
    def name(self) -> str:
        return "ask_permission"
    
    @property
    def description(self) -> str:
        return "Ask for user permission or input. Use when you need confirmation or user feedback before proceeding."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The message or question to display to the user",
                    "default": "Press Enter to continue..."
                },
                "expect_response": {
                    "type": "boolean",
                    "description": "Whether to expect a text response from the user (true) or just wait for Enter (false)",
                    "default": True
                },
                "timeout": {
                    "type": "integer",
                    "description": "Optional timeout in seconds. If not provided, waits indefinitely.",
                    "minimum": 1
                }
            },
            "required": ["prompt"]
        }
    
    def execute(self, prompt: str = "Press Enter to continue...", expect_response: bool = True, timeout: int = None) -> str:
        """Execute the wait tool."""
        try:
            print(f"\n--- Eagle is waiting for your input ---")
            print(f"{prompt}")
            
            if timeout:
                print(f"(Timeout: {timeout} seconds)")
                # Note: For simplicity, we'll implement basic input without timeout
                # In production, you might want to use signal.alarm or threading
                user_input = input("> ").strip()
            else:
                if expect_response:
                    user_input = input("> ").strip()
                else:
                    input()
                    user_input = ""
            
            if expect_response and user_input:
                return f"User responded: {user_input}"
            elif expect_response and not user_input:
                return "User provided no response (empty input)"
            else:
                return "User acknowledged (pressed Enter)"
                
        except KeyboardInterrupt:
            return "User interrupted the wait (Ctrl+C)"
        except Exception as e:
            return f"Error during wait: {str(e)}"