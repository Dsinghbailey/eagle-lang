"""Make Tool - creates new custom tools and makes them available to Eagle."""

import os
import json
from typing import Dict, Any
from eagle_lang.tools.base import EagleTool


class MakeToolTool(EagleTool):
    """Tool for creating new custom tools."""
    
    @property
    def name(self) -> str:
        return "make_tool"
    
    @property
    def description(self) -> str:
        return "Create a new custom tool and make it immediately available to Eagle"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "tool_name": {
                    "type": "string",
                    "description": "Name of the new tool (lowercase, no spaces)"
                },
                "description": {
                    "type": "string", 
                    "description": "Description of what the tool does"
                },
                "category": {
                    "type": "string",
                    "enum": ["file_operations", "system_operations", "external_data", "communication", "analysis", "general"],
                    "description": "Category for the tool",
                    "default": "general"
                },
                "parameters_schema": {
                    "type": "object",
                    "description": "JSON schema for the tool's parameters (optional - will be auto-generated if not provided)"
                },
                "implementation": {
                    "type": "string",
                    "description": "Python implementation code for the execute method (optional - will be auto-generated if not provided)"
                },
                "examples": {
                    "type": "array",
                    "description": "Example usage scenarios to help generate the implementation",
                    "items": {"type": "string"}
                },
                "usage_patterns": {
                    "type": "array",
                    "description": "List of usage patterns for this tool",
                    "items": {"type": "string"}
                },
                "workflows": {
                    "type": "object", 
                    "description": "Workflow examples that use this tool",
                    "additionalProperties": {"type": "array", "items": {"type": "string"}}
                }
            },
            "required": ["tool_name", "description"]
        }
    
    @property
    def usage_patterns(self) -> Dict[str, Any]:
        return {
            "category": "meta_operations",
            "patterns": [
                "Create specialized tools for specific tasks",
                "Extend Eagle's capabilities dynamically", 
                "Generate tools based on user requirements",
                "Build custom integrations and workflows"
            ],
            "workflows": {
                "Tool Development": ["make_tool", "shell", "call_eagle"],
                "Custom Integration": ["make_tool", "write", "read"]
            }
        }
    
    def execute(self, tool_name: str, description: str, parameters_schema: dict = None, 
                implementation: str = None, category: str = "general", 
                usage_patterns: list = None, workflows: dict = None, examples: list = None) -> str:
        """Execute the make_tool tool."""
        try:
            # Validate tool name
            if not self._is_valid_tool_name(tool_name):
                return f"Invalid tool name: {tool_name}. Use lowercase letters, numbers, and underscores only."
            
            # Auto-generate missing components if needed
            if implementation is None or parameters_schema is None:
                if not self._can_auto_generate():
                    return f"❌ Auto-generation requires AI access. Please provide 'implementation' and 'parameters_schema' parameters manually."
                
                # Generate missing components using AI
                generation_result = self._generate_with_ai(tool_name, description, examples or [], parameters_schema, implementation)
                if "error" in generation_result:
                    return f"❌ Failed to auto-generate tool: {generation_result['error']}"
                
                parameters_schema = generation_result.get("parameters_schema", parameters_schema)
                implementation = generation_result.get("implementation", implementation)
            
            # Create .eagle/tools directory if it doesn't exist
            tools_dir = os.path.join(".eagle", "tools")
            os.makedirs(tools_dir, exist_ok=True)
            
            # Create tool folder
            tool_folder = os.path.join(tools_dir, tool_name)
            os.makedirs(tool_folder, exist_ok=True)
            
            # Generate tool code
            tool_code = self._generate_tool_code(
                tool_name, description, category, parameters_schema, 
                implementation, usage_patterns or [], workflows or {}
            )
            
            # Generate test code
            test_code = self._generate_test_code(tool_name, description, parameters_schema)
            
            # Generate README
            readme_content = self._generate_readme(tool_name, description, category, parameters_schema, usage_patterns or [])
            
            # Write files
            tool_path = os.path.join(tool_folder, "__init__.py")
            test_path = os.path.join(tool_folder, "tests.py")
            readme_path = os.path.join(tool_folder, "README.md")
            
            with open(tool_path, 'w', encoding='utf-8') as f:
                f.write(tool_code)
            
            with open(test_path, 'w', encoding='utf-8') as f:
                f.write(test_code)
                
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            # Ask user about adding to config
            config_result = self._prompt_config_update(tool_name)
            
            # Try to reload tools dynamically
            reload_result = self._reload_tools()
            
            return f"""✅ Created custom tool '{tool_name}' successfully!

📁 Location: {tool_folder}/
   ├── __init__.py     (tool implementation)
   ├── tests.py        (test cases)
   └── README.md       (documentation)

📋 Description: {description}
🔧 Category: {category}

{config_result}
{reload_result}

The tool is now available for use in Eagle workflows."""
            
        except Exception as e:
            return f"❌ Error creating tool '{tool_name}': {str(e)}"
    
    def _is_valid_tool_name(self, name: str) -> bool:
        """Validate tool name format."""
        import re
        return bool(re.match(r'^[a-z][a-z0-9_]*$', name))
    
    def _generate_tool_code(self, tool_name: str, description: str, category: str,
                           parameters_schema: dict, implementation: str, 
                           usage_patterns: list, workflows: dict) -> str:
        """Generate the Python code for the new tool."""
        
        class_name = ''.join(word.capitalize() for word in tool_name.split('_')) + 'Tool'
        
        # Format implementation with proper indentation
        implementation_lines = implementation.strip().split('\n')
        indented_implementation = '\n        '.join(implementation_lines)
        
        # Format parameters schema
        schema_str = json.dumps(parameters_schema, indent=12)[:-1] + '    }'
        
        # Format usage patterns
        patterns_str = json.dumps(usage_patterns, indent=12)
        workflows_str = json.dumps(workflows, indent=12)
        
        tool_code = f'''"""Custom tool: {tool_name} - {description}"""

import os
import json
import requests
from typing import Dict, Any

# Import EagleTool from the main package
import sys
import importlib.util

def _import_eagle_tool():
    """Import EagleTool from the main eagle_lang package."""
    try:
        from eagle_lang.tools.base import EagleTool
        return EagleTool
    except ImportError:
        # Fallback to local base if main package not available
        from eagle_lang.tools.base import EagleTool
        return EagleTool

EagleTool = _import_eagle_tool()


class {class_name}(EagleTool):
    """Custom tool: {description}"""
    
    @property
    def name(self) -> str:
        return "{tool_name}"
    
    @property
    def description(self) -> str:
        return "{description}"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {schema_str}
    
    @property
    def usage_patterns(self) -> Dict[str, Any]:
        return {{
            "category": "{category}",
            "patterns": {patterns_str},
            "workflows": {workflows_str}
        }}
    
    def execute(self, **kwargs) -> str:
        """Execute the {tool_name} tool."""
        try:
            {indented_implementation}
        except Exception as e:
            return f"Error in {tool_name} tool: {{str(e)}}"
'''
        
        return tool_code
    
    def _generate_test_code(self, tool_name: str, description: str, parameters_schema: dict) -> str:
        """Generate test code for the new tool."""
        class_name = ''.join(word.capitalize() for word in tool_name.split('_')) + 'Tool'
        
        # Extract parameter names for test examples
        properties = parameters_schema.get('properties', {})
        required_params = parameters_schema.get('required', [])
        
        # Generate test parameters
        test_params = {}
        for param_name, param_info in properties.items():
            param_type = param_info.get('type', 'string')
            if param_type == 'string':
                test_params[param_name] = f"'test_{param_name}'"
            elif param_type == 'integer':
                test_params[param_name] = '42'
            elif param_type == 'boolean':
                test_params[param_name] = 'True'
            else:
                test_params[param_name] = f"'test_value'"
        
        params_str = ', '.join([f"{k}={v}" for k, v in test_params.items()])
        
        test_code = f'''"""Tests for {tool_name} tool."""

import unittest
from . import {class_name}


class Test{class_name}(unittest.TestCase):
    """Test cases for the {tool_name} tool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = {class_name}()
    
    def test_tool_properties(self):
        """Test that tool has required properties."""
        self.assertEqual(self.tool.name, "{tool_name}")
        self.assertIsNotNone(self.tool.description)
        self.assertIsNotNone(self.tool.parameters)
    
    def test_basic_execution(self):
        """Test basic tool execution."""
        result = self.tool.execute({params_str})
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_invalid_parameters(self):
        """Test tool behavior with invalid parameters."""
        # Test with missing required parameters
        result = self.tool.execute()
        self.assertIn("Error", result)
    
    def test_parameter_validation(self):
        """Test parameter validation."""
        # Add specific parameter validation tests here
        pass


if __name__ == '__main__':
    unittest.main()
'''
        return test_code
    
    def _generate_readme(self, tool_name: str, description: str, category: str, 
                        parameters_schema: dict, usage_patterns: list) -> str:
        """Generate README documentation for the new tool."""
        
        # Format parameters for documentation
        properties = parameters_schema.get('properties', {})
        required_params = parameters_schema.get('required', [])
        
        params_doc = []
        for param_name, param_info in properties.items():
            param_type = param_info.get('type', 'string')
            param_desc = param_info.get('description', 'No description provided')
            required_marker = ' (required)' if param_name in required_params else ' (optional)'
            params_doc.append(f"- **{param_name}** ({param_type}){required_marker}: {param_desc}")
        
        params_section = '\n'.join(params_doc) if params_doc else "No parameters required."
        
        # Format usage patterns
        patterns_section = '\n'.join([f"- {pattern}" for pattern in usage_patterns]) if usage_patterns else "No specific usage patterns defined."
        
        readme_content = f'''# {tool_name.replace('_', ' ').title()} Tool

{description}

## Category
{category.replace('_', ' ').title()}

## Parameters

{params_section}

## Usage Patterns

{patterns_section}

## Example Usage

```python
from eagle_lang.tools.base import tool_registry

# Get the tool
tool = tool_registry.get("{tool_name}")

# Execute the tool
result = tool.execute(
    # Add your parameters here
)

print(result)
```

## Testing

Run the tests using:

```bash
python -m unittest {tool_name}.tests
```

## Development

This tool was generated using Eagle's `make_tool` functionality. To modify:

1. Edit the `__init__.py` file for the main implementation
2. Update `tests.py` to add more test cases
3. Update this README with any changes

## Dependencies

- Standard Python libraries only (modify if you add external dependencies)
'''
        return readme_content
    
    def _can_auto_generate(self) -> bool:
        """Check if auto-generation is possible (Eagle interpreter available)."""
        from eagle_lang.tools.base import tool_registry
        return tool_registry.get_interpreter() is not None
    
    def _generate_with_ai(self, tool_name: str, description: str, examples: list, 
                         existing_schema: dict = None, existing_impl: str = None) -> dict:
        """Generate tool components using direct AI generation."""
        try:
            from eagle_lang.tools.base import tool_registry
            interpreter = tool_registry.get_interpreter()
            
            if not interpreter:
                return {"error": "No Eagle interpreter available for AI generation"}
            
            # Build prompt for AI generation
            prompt = self._build_generation_prompt(tool_name, description, examples, existing_schema, existing_impl)
            
            # Generate using current AI session
            result = interpreter.generate_with_ai(prompt)
            
            # Parse the result to extract schema and implementation
            return self._parse_generation_result(result)
            
        except Exception as e:
            return {"error": str(e)}
    
    def _build_generation_prompt(self, tool_name: str, description: str, examples: list,
                                existing_schema: dict = None, existing_impl: str = None) -> str:
        """Build prompt for AI to generate tool components."""
        
        prompt = f"""Create an Eagle tool with the following specifications:

**Tool Name**: {tool_name}
**Description**: {description}

**Requirements**:
1. Generate a JSON schema for the tool's parameters
2. Generate Python implementation for the execute method
3. Follow Eagle tool patterns and best practices
4. Include proper error handling
5. Return results as strings

"""
        
        if examples:
            prompt += "**Usage Examples**:\n"
            for i, example in enumerate(examples, 1):
                prompt += f"{i}. {example}\n"
            prompt += "\n"
        
        if existing_schema:
            prompt += f"**Use this parameter schema**: {json.dumps(existing_schema, indent=2)}\n\n"
        else:
            prompt += "**Generate parameter schema** based on the description and examples.\n\n"
            
        if existing_impl:
            prompt += f"**Use this implementation**: {existing_impl}\n\n"
        else:
            prompt += "**Generate implementation** for the execute method.\n\n"
        
        prompt += """**Output Format**:
Return a JSON object with this exact structure:
```json
{
    "parameters_schema": {
        "type": "object",
        "properties": {...},
        "required": [...]
    },
    "implementation": "def execute(self, **kwargs):\\n    # implementation here\\n    return 'result'"
}
```

Make sure the implementation is a single string with proper Python indentation using \\n for newlines."""
        
        return prompt
    
    def _parse_generation_result(self, result: str) -> dict:
        """Parse the AI generation result to extract schema and implementation."""
        try:
            # Look for JSON in the result
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', result, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)
            
            # Fallback: try to parse the entire result as JSON
            return json.loads(result)
            
        except json.JSONDecodeError:
            return {"error": f"Failed to parse AI response as JSON: {result}"}
    
    def _prompt_config_update(self, tool_name: str) -> str:
        """Prompt user to add tool to config and update automatically."""
        try:
            print(f"\n🔧 Tool '{tool_name}' created! Where should it be added to your Eagle config?")
            print("1. Allowed tools (can be used freely)")
            print("2. Permission-required tools (requires user approval)")
            print("3. Skip (don't add to config now)")
            
            while True:
                choice = input("Enter choice (1/2/3): ").strip()
                
                if choice == "1":
                    return self._update_config(tool_name, "allowed")
                elif choice == "2":
                    return self._update_config(tool_name, "require_permission")
                elif choice == "3":
                    return "⚠️  Tool not added to config. Add manually to use."
                else:
                    print("Please enter 1, 2, or 3")
                    
        except Exception as e:
            return f"⚠️  Config update failed: {str(e)}. Add tool to config manually."
    
    def _update_config(self, tool_name: str, category: str) -> str:
        """Update Eagle config to include the new tool."""
        try:
            import os
            import json
            
            # Find config file (project first, then user)
            project_config = os.path.join(".eagle", "eagle_config.json")
            user_config = os.path.expanduser("~/.eagle/eagle_config.json")
            
            config_path = None
            if os.path.exists(project_config):
                config_path = project_config
            elif os.path.exists(user_config):
                config_path = user_config
            else:
                # No config file exists, create project config
                os.makedirs(".eagle", exist_ok=True)
                config_path = project_config
                # Create basic config structure
                config = {
                    "provider": "openai",
                    "model": "gpt-4",
                    "rules": ["eagle_rules.md"],
                    "tools": {
                        "allowed": [],
                        "require_permission": []
                    },
                    "max_tokens": 4000
                }
            
            # Load existing config
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            # Ensure tools structure exists
            if "tools" not in config:
                config["tools"] = {"allowed": [], "require_permission": []}
            if "allowed" not in config["tools"]:
                config["tools"]["allowed"] = []
            if "require_permission" not in config["tools"]:
                config["tools"]["require_permission"] = []
            
            # Add tool to requested category (avoid duplicates)
            target_list = config["tools"][category]
            if tool_name not in target_list:
                target_list.append(tool_name)
            
            # Remove from other category if present
            other_category = "require_permission" if category == "allowed" else "allowed"
            other_list = config["tools"][other_category]
            if tool_name in other_list:
                other_list.remove(tool_name)
            
            # Save updated config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            category_name = "allowed tools" if category == "allowed" else "permission-required tools"
            return f"✅ Added '{tool_name}' to {category_name} in {config_path}"
            
        except Exception as e:
            return f"❌ Failed to update config: {str(e)}"
    
    def _reload_tools(self) -> str:
        """Attempt to reload tools dynamically."""
        try:
            from .base import tool_registry
            
            # Load tools from .eagle/tools directory
            tools_dir = os.path.join(".eagle", "tools")
            if os.path.exists(tools_dir):
                tool_registry.load_tools_from_directory(tools_dir)
                return "🔄 Tools reloaded successfully. New tool is immediately available!"
            else:
                return "⚠️  Tool created but requires Eagle restart to become available."
                
        except Exception as e:
            return f"⚠️  Tool created but reload failed: {str(e)}. Restart Eagle to use the new tool."