"""Eagle Interpreter - the core AI engine for Eagle."""

import os
import json
from typing import Dict, Any, Optional
from openai import OpenAI
import anthropic
import google.generativeai as genai

from .config import get_default_config
from .tools.base import tool_registry
from .providers import get_provider_config


class EagleInterpreter:
    """The core Eagle interpreter that handles AI provider interactions."""
    
    def __init__(self, provider: str = None, model_name: str = None, rules: list = None, config: dict = None, verbose: bool = None, additional_context: list = None):
        self.default_config = get_default_config()
        self.config = config or self.default_config
        self.provider = provider or self.config.get("provider", self.default_config["provider"])
        self.model_name = model_name or self.config.get("model", self.default_config["model"])
        self.rules = rules or self.config.get("rules", self.default_config["rules"])
        self.verbose = verbose if verbose is not None else self.config.get("verbose", self.default_config.get("verbose", False))
        self.additional_context = additional_context or []
        
        # Initialize tools first
        self.tools_enabled = self.config.get("tools")
        self.available_tools = self._get_available_tools()
        
        # Provide interpreter reference to tool registry
        tool_registry.set_interpreter(self)
        
        # Build system prompt with rules and dynamic tool documentation
        self.system_prompt = self._build_system_prompt()
        self.assistant_name = "Eagle Assistant"
        
        self.client = self._initialize_client()
        tools_info = f" with {len(self.available_tools)} tools" if self.available_tools else ""
        if self.verbose:
            print(f"🔧 Eagle initialized with {self.assistant_name} using {self.provider}:{self.model_name}{tools_info}")
            if self.available_tools:
                print(f"📋 Available tools: {', '.join(self.available_tools)}")
        else:
            print(f"Eagle initialized with {self.assistant_name} using {self.provider}:{self.model_name}{tools_info}")
    
    
    def _load_rules(self) -> str:
        """Load rules from markdown files."""
        if not self.rules:
            # Fallback if no rules specified
            print("No rules specified. Using default system prompt.")
            return "You are Eagle, a helpful, high-level AI programming assistant. You interpret plain English instructions from .caw files and generate the best possible direct response or action. Do not ask clarifying questions unless absolutely necessary for safety or critical clarification. Focus on fulfilling the user's high-level intent."
        
        combined_rules = []
        
        for rules_file in self.rules:
            # Try to find the rules file in .eagle folders
            rules_paths = [
                # Direct path if provided
                rules_file,
                # In project .eagle directory
                os.path.join(os.getcwd(), ".eagle", rules_file),
                # In user home .eagle directory
                os.path.expanduser(f"~/.eagle/{rules_file}")
            ]
            
            rules_content = None
            for rules_path in rules_paths:
                if os.path.exists(rules_path):
                    try:
                        with open(rules_path, "r", encoding="utf-8") as f:
                            rules_content = f.read()
                        break
                    except Exception as e:
                        print(f"Error reading rules file {rules_path}: {e}")
                        continue
            
            if rules_content:
                combined_rules.append(rules_content)
            else:
                print(f"Rules file '{rules_file}' not found, skipping.")
        
        if not combined_rules:
            # Fallback if no rules files could be loaded
            print("No rules files could be loaded. Using default system prompt.")
            return "You are Eagle, a helpful, high-level AI programming assistant. You interpret plain English instructions from .caw files and generate the best possible direct response or action. Do not ask clarifying questions unless absolutely necessary for safety or critical clarification. Focus on fulfilling the user's high-level intent."
        
        # Combine all rules with separators
        return "\n\n---\n\n".join(combined_rules)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with rules and dynamic tool documentation."""
        base_rules = self._load_rules()
        
        # Generate dynamic tool documentation
        tool_docs = self._generate_tool_documentation()
        
        # Generate dynamic tool patterns from available tools
        tool_patterns = tool_registry.get_tool_patterns(self.available_tools)
        
        return f"""{base_rules}

## Available Tools

You have access to the following tools:

{tool_docs}

## Tool Usage Guidelines
- Tools in the "🔓 Allowed" category can be used freely without user permission
- Tools in the "🔐 Requires Permission" category will prompt the user for approval before execution
- Always use the most appropriate tool for the task at hand
- Combine multiple tools when needed for complex workflows
- Handle tool errors gracefully and suggest alternatives
- Focus on accomplishing real work through tool usage, not just providing information

## Usage Patterns

{tool_patterns}"""
    
    def _generate_tool_documentation(self) -> str:
        """Generate documentation for currently available tools."""
        if not self.available_tools:
            return "No tools are currently available."
        
        docs = []
        
        for tool_name in self.available_tools:
            tool = tool_registry.get(tool_name)
            if tool:
                permission_status = "🔓 Allowed" if self._tool_is_allowed(tool_name) else "🔐 Requires Permission"
                
                docs.append(f"""### {tool_name} {permission_status}
**Description**: {tool.description}
**Parameters**: {self._format_parameters(tool.parameters)}""")
        
        return "\n\n".join(docs)
    
    def _tool_is_allowed(self, tool_name: str) -> bool:
        """Check if tool is in allowed category."""
        if isinstance(self.tools_enabled, dict):
            return tool_name in self.tools_enabled.get("allowed", [])
        return True  # Legacy format - assume allowed
    
    def _format_parameters(self, parameters: dict) -> str:
        """Format tool parameters for prompt."""
        if not parameters or "properties" not in parameters:
            return "No parameters required"
        
        props = []
        required = parameters.get("required", [])
        properties = parameters.get("properties", {})
        
        for prop, details in properties.items():
            req_marker = " (required)" if prop in required else " (optional)"
            prop_type = details.get("type", "unknown")
            description = details.get("description", "No description")
            
            # Add enum options if available
            if "enum" in details:
                enum_options = ", ".join(details["enum"])
                description += f" Options: {enum_options}"
            
            props.append(f"  - **{prop}** ({prop_type}){req_marker}: {description}")
        
        return "\n" + "\n".join(props) if props else "No parameters required"
    
    def _get_available_tools(self) -> list:
        """Get list of available tools based on config."""
        # Validate that tools config exists
        if self.tools_enabled is None:
            raise ValueError("Missing 'tools' configuration. Please run 'eagle init' to create a valid configuration.")
        
        # Handle new config structure with allowed/require_permission
        if isinstance(self.tools_enabled, dict):
            # Validate required keys
            if "allowed" not in self.tools_enabled or "require_permission" not in self.tools_enabled:
                raise ValueError("Invalid tools configuration. Expected 'allowed' and 'require_permission' arrays.")
            
            allowed_tools = self.tools_enabled.get("allowed", [])
            permission_tools = self.tools_enabled.get("require_permission", [])
            all_configured_tools = allowed_tools + permission_tools
            
            # Return exactly what's configured (empty means no tools)
            return [tool for tool in all_configured_tools if tool in tool_registry.list_tools()]
        elif isinstance(self.tools_enabled, list):
            # Legacy list format
            return [tool for tool in self.tools_enabled if tool in tool_registry.list_tools()]
        else:
            raise ValueError(f"Invalid tools configuration format. Expected dict or list, got {type(self.tools_enabled)}.")
    
    def _initialize_client(self):
        """Initialize the appropriate client based on provider."""
        try:
            provider_config = get_provider_config(self.provider)
        except ValueError as e:
            print(f"Error: {e}")
            exit(1)
            
        api_key_env = provider_config["api_key_env"]
        api_key = os.getenv(api_key_env)
        
        if not api_key:
            self._prompt_env_setup(api_key_env, self.provider)
            raise ValueError(f"{api_key_env} environment variable not set. Please set it or ensure your .env file is loaded.")
        
        try:
            if self.provider == "openai":
                return OpenAI(api_key=api_key)
            elif self.provider == "claude":
                return anthropic.Anthropic(api_key=api_key)
            elif self.provider == "gemini":
                genai.configure(api_key=api_key)
                return genai.GenerativeModel(self.model_name)
            elif self.provider == "openrouter":
                base_url = provider_config.get("base_url", "https://openrouter.ai/api/v1")
                return OpenAI(api_key=api_key, base_url=base_url)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            if "authentication" in str(e).lower() or "api key" in str(e).lower():
                print(f"Authentication error: Please check your {api_key_env} in the .env file or environment variables.")
            else:
                print(f"Error initializing {self.provider} client: {e}")
            exit(1)

    def _read_caw_file(self, file_path: str) -> str:
        """Reads the content of a .caw file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"Successfully read .caw file: {file_path}")
            return content
        except FileNotFoundError:
            print(f"Error: .caw file not found at {file_path}")
            exit(1)
        except Exception as e:
            print(f"Error reading .caw file {file_path}: {e}")
            exit(1)

    def _enhance_content_with_context(self, content: str) -> str:
        """Enhance the .caw file content with additional context."""
        if not self.additional_context:
            return content
            
        enhanced_parts = [content]
        
        # Add additional context section
        context_section = "\n\n## Additional Context\n"
        for context_item in self.additional_context:
            if '=' in context_item:
                # Key-value format
                key, value = context_item.split('=', 1)
                context_section += f"- {key.strip()}: {value.strip()}\n"
            else:
                # Plain text context
                context_section += f"- {context_item}\n"
        enhanced_parts.append(context_section)
        
        return "".join(enhanced_parts)

    def execute_caw_file(self, caw_file_path: str) -> None:
        """Execute a .caw file by sending its content to the LLM."""
        caw_content = self._read_caw_file(caw_file_path)

        if not caw_content.strip():
            print("The .caw file is empty or contains only whitespace. No instructions for Eagle.")
            return

        # Inject additional context and variables
        enhanced_content = self._enhance_content_with_context(caw_content)

        if self.verbose:
            print("🧠 Processing your request...")
            print(f"📝 Content length: {len(enhanced_content)} characters")
            if self.additional_context:
                print("📋 Additional context injected")
        else:
            print("\n--- Eagle is thinking... ---\n")

        try:
            llm_response = self._get_llm_response(enhanced_content)
            if self.verbose:
                print("✅ Response received from AI")
            print(f"\n--- {self.assistant_name}'s Response ---\n")
            print(llm_response)
            print("\n" + "-" * (len(self.assistant_name) + 15) + "\n")
        except Exception as e:
            print(f"An unexpected error occurred during LLM communication: {e}")
            exit(1)
    
    def _get_llm_response(self, content: str, session_history: list = None) -> str:
        """Get response from the configured LLM provider."""
        max_tokens = self.config.get("max_tokens", self.default_config["max_tokens"])
        
        if self.verbose:
            print(f"🌐 Sending request to {self.provider}...")
        
        if self.provider in ["openai", "openrouter"]:
            return self._get_openai_response(content, max_tokens, session_history)
        elif self.provider == "claude":
            return self._get_claude_response(content, max_tokens, session_history)
        elif self.provider == "gemini":
            return self._get_gemini_response(content, max_tokens, session_history)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _get_openai_response(self, content: str, max_tokens: int, session_history: list = None) -> str:
        """Get response from OpenAI/OpenRouter with tool support."""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add session history if available
        if session_history:
            # Add recent history (excluding current user input to avoid duplication)
            messages.extend(session_history[:-1])
        
        # Add current user message
        messages.append({"role": "user", "content": content})
        
        # Add tools if available
        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        
        if self.available_tools:
            kwargs["tools"] = tool_registry.get_openai_functions()
            kwargs["tool_choice"] = "auto"
        
        if self.verbose:
            print("⏳ Awaiting response from AI...")
        
        response = self.client.chat.completions.create(**kwargs)
        message = response.choices[0].message
        
        # Handle tool calls
        if message.tool_calls:
            if self.verbose:
                print(f"🔧 AI requested {len(message.tool_calls)} tool execution(s)")
            return self._handle_tool_calls(message.tool_calls, messages)
        
        return message.content
    
    def _get_claude_response(self, content: str, max_tokens: int, session_history: list = None) -> str:
        """Get response from Claude with tool support."""
        messages = []
        
        # Add session history if available
        if session_history:
            # Add recent history (excluding current user input to avoid duplication)
            messages.extend(session_history[:-1])
        
        # Add current user message
        messages.append({"role": "user", "content": content})
        kwargs = {
            "model": self.model_name,
            "max_tokens": max_tokens,
            "system": self.system_prompt,
            "messages": messages
        }
        
        if self.available_tools:
            kwargs["tools"] = tool_registry.get_anthropic_tools()
        
        if self.verbose:
            print("⏳ Awaiting response from AI...")
        
        response = self.client.messages.create(**kwargs)
        
        # Handle tool calls
        if hasattr(response, 'content') and len(response.content) > 0:
            for content_block in response.content:
                if content_block.type == "tool_use":
                    if self.verbose:
                        print("🔧 AI requested tool execution")
                    # Add assistant's response to messages first
                    messages.append({"role": "assistant", "content": response.content})
                    return self._handle_anthropic_tool_calls([content_block], messages)
                elif content_block.type == "text":
                    return content_block.text
        
        return response.content[0].text if response.content else ""
    
    def _get_gemini_response(self, content: str, max_tokens: int, session_history: list = None) -> str:
        """Get response from Gemini (basic implementation without tool support for now)."""
        # Build full prompt with session history
        full_prompt = self.system_prompt
        
        if session_history:
            full_prompt += "\n\nConversation History:\n"
            for msg in session_history[:-1]:  # Exclude current user input
                role = "User" if msg["role"] == "user" else "Assistant"
                full_prompt += f"{role}: {msg['content']}\n"
        
        full_prompt += f"\n\nUser: {content}"
        response = self.client.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(max_output_tokens=max_tokens)
        )
        return response.text
    
    def _handle_tool_calls(self, tool_calls, messages) -> str:
        """Handle OpenAI/OpenRouter tool calls with multi-turn support."""
        # Add the assistant's tool call message to the conversation
        messages.append({
            "role": "assistant",
            "tool_calls": [{
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            } for tc in tool_calls]
        })
        
        # Execute tools and add results to conversation
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            if self.verbose:
                print(f"🔧 Executing tool: {tool_name}")
                print(f"📋 Arguments: {tool_args}")
            
            tool = tool_registry.get(tool_name)
            if tool:
                try:
                    # Check if tool requires permission
                    if self._tool_requires_permission(tool_name):
                        if not self._get_user_permission(tool_name, tool_args):
                            result = f"Tool '{tool_name}' execution denied by user"
                            if self.verbose:
                                print(f"❌ Tool execution denied: {tool_name}")
                        else:
                            result = tool.execute(**tool_args)
                            if self.verbose:
                                print(f"✅ Tool completed: {tool_name}")
                    else:
                        result = tool.execute(**tool_args)
                        if self.verbose:
                            print(f"✅ Tool completed: {tool_name}")
                except Exception as e:
                    result = f"Tool '{tool_name}' failed: {str(e)}"
                    if self.verbose:
                        print(f"❌ Tool failed: {tool_name} - {str(e)}")
            else:
                result = f"Unknown tool: {tool_name}"
                if self.verbose:
                    print(f"❓ Unknown tool requested: {tool_name}")
            
            # Add tool result to conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })
        
        # Continue conversation with tool results
        if self.verbose:
            print("🧠 Processing tool results...")
            
        max_tokens = self.config.get("max_tokens", self.default_config["max_tokens"])
        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        
        if self.available_tools:
            kwargs["tools"] = tool_registry.get_openai_functions()
            kwargs["tool_choice"] = "auto"
        
        response = self.client.chat.completions.create(**kwargs)
        message = response.choices[0].message
        
        # Handle potential additional tool calls
        if message.tool_calls:
            return self._handle_tool_calls(message.tool_calls, messages)
        
        return message.content
    
    def _handle_anthropic_tool_calls(self, tool_calls, messages) -> str:
        """Handle Anthropic tool calls with multi-turn support."""
        tool_results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.name
            tool_args = tool_call.input
            
            if self.verbose:
                print(f"🔧 Executing tool: {tool_name}")
                print(f"📋 Arguments: {tool_args}")
            
            tool = tool_registry.get(tool_name)
            if tool:
                try:
                    # Check if tool requires permission
                    if self._tool_requires_permission(tool_name):
                        if not self._get_user_permission(tool_name, tool_args):
                            result = f"Tool '{tool_name}' execution denied by user"
                            if self.verbose:
                                print(f"❌ Tool execution denied: {tool_name}")
                        else:
                            result = tool.execute(**tool_args)
                            if self.verbose:
                                print(f"✅ Tool completed: {tool_name}")
                    else:
                        result = tool.execute(**tool_args)
                        if self.verbose:
                            print(f"✅ Tool completed: {tool_name}")
                except Exception as e:
                    result = f"Tool '{tool_name}' failed: {str(e)}"
                    if self.verbose:
                        print(f"❌ Tool failed: {tool_name} - {str(e)}")
            else:
                result = f"Unknown tool: {tool_name}"
                if self.verbose:
                    print(f"❓ Unknown tool requested: {tool_name}")
            
            # Prepare tool result for Claude format
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_call.id,
                "content": str(result)
            })
        
        # Add tool results to messages and continue conversation
        messages.append({
            "role": "user",
            "content": tool_results
        })
        
        # Continue conversation with tool results
        if self.verbose:
            print("🧠 Processing tool results...")
            
        max_tokens = self.config.get("max_tokens", self.default_config["max_tokens"])
        kwargs = {
            "model": self.model_name,
            "max_tokens": max_tokens,
            "system": self.system_prompt,
            "messages": messages
        }
        
        if self.available_tools:
            kwargs["tools"] = tool_registry.get_anthropic_tools()
        
        response = self.client.messages.create(**kwargs)
        
        # Handle potential additional tool calls
        if hasattr(response, 'content') and len(response.content) > 0:
            for content_block in response.content:
                if content_block.type == "tool_use":
                    return self._handle_anthropic_tool_calls([content_block], messages)
                elif content_block.type == "text":
                    return content_block.text
        
        return response.content[0].text if response.content else ""
    
    def _tool_requires_permission(self, tool_name: str) -> bool:
        """Check if a tool requires user permission before execution."""
        if isinstance(self.tools_enabled, dict):
            require_permission = self.tools_enabled.get("require_permission", [])
            return tool_name in require_permission
        return False
    
    def _get_user_permission(self, tool_name: str, tool_args: dict) -> bool:
        """Get user permission for tool execution."""
        print(f"\n🔐 Permission Required")
        print(f"Tool: {tool_name}")
        print(f"Arguments: {tool_args}")
        
        while True:
            response = input("Allow this tool execution? (y/n/details): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            elif response in ['d', 'details']:
                tool = tool_registry.get(tool_name)
                if tool:
                    print(f"Tool description: {tool.description}")
                else:
                    print("Tool details not available")
            else:
                print("Please enter 'y' (yes), 'n' (no), or 'd' (details)")
    
    def generate_with_ai(self, prompt: str, max_tokens: int = None) -> str:
        """Generate content using the current AI session (for use by tools)."""
        if not max_tokens:
            max_tokens = min(4000, self.config.get("max_tokens", self.default_config["max_tokens"]))
        
        try:
            if self.provider in ["openai", "openrouter"]:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            elif self.provider == "claude":
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            elif self.provider == "gemini":
                response = self.client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(max_output_tokens=max_tokens)
                )
                return response.text
            
            else:
                return f"Error: Unsupported provider for AI generation: {self.provider}"
                
        except Exception as e:
            return f"Error generating with AI: {str(e)}"
    
    def _prompt_env_setup(self, api_key_env: str, provider: str) -> None:
        """Prompt user to set up .env file with API key."""
        print(f"\n🔑 API Key Missing for {provider}")
        print(f"Eagle needs your {api_key_env} to work with {provider}.")
        print("\n📝 To fix this:")
        
        # Check for existing .env files
        project_env = os.path.join(".eagle", ".env")
        user_env = os.path.expanduser("~/.eagle/.env")
        
        env_file = None
        if os.path.exists(project_env):
            env_file = project_env
        elif os.path.exists(user_env):
            env_file = user_env
        else:
            # Suggest creating project .env
            env_file = project_env
            print(f"1. Create .env file: mkdir -p .eagle && touch {env_file}")
        
        print(f"2. Add your API key to {env_file}:")
        print(f"   {api_key_env}=your_api_key_here")
        print(f"3. Restart Eagle")
        
        # Provider-specific guidance
        if provider == "openai":
            print(f"\n💡 Get your OpenAI API key from: https://platform.openai.com/api-keys")
        elif provider == "claude":
            print(f"\n💡 Get your Anthropic API key from: https://console.anthropic.com/")
        elif provider == "gemini":
            print(f"\n💡 Get your Google AI API key from: https://makersuite.google.com/app/apikey")
        elif provider == "openrouter":
            print(f"\n💡 Get your OpenRouter API key from: https://openrouter.ai/keys")
        
        print(f"\n⚠️  Keep your API key secure - never share it or commit it to version control!")
        
        # Offer to create/edit .env file
        try:
            choice = input(f"\nWould you like Eagle to help create/edit {env_file}? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                self._create_env_file(env_file, api_key_env)
        except KeyboardInterrupt:
            print("\n")
    
    def _create_env_file(self, env_file: str, api_key_env: str) -> None:
        """Help user create or edit .env file."""
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(env_file), exist_ok=True)
            
            # Check if file exists and has the key
            existing_content = ""
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    existing_content = f.read()
            
            # Check if key already exists
            if f"{api_key_env}=" in existing_content:
                print(f"✅ {api_key_env} already exists in {env_file}")
                print("Please update the value with your actual API key.")
                return
            
            # Add the key
            with open(env_file, 'a') as f:
                if existing_content and not existing_content.endswith('\n'):
                    f.write('\n')
                f.write(f"{api_key_env}=your_api_key_here\n")
            
            print(f"✅ Added {api_key_env} to {env_file}")
            print(f"📝 Please edit {env_file} and replace 'your_api_key_here' with your actual API key.")
            
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            print(f"Please manually create {env_file} with: {api_key_env}=your_api_key_here")