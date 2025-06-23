"""Base tool class for Eagle tools."""

import os
import sys
import importlib.util
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class EagleTool(ABC):
    """Base class for all Eagle tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the tool."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of what the tool does."""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """Return the parameters schema for the tool."""
        pass
    
    @property
    def usage_patterns(self) -> Dict[str, Any]:
        """Return usage patterns and workflow examples for this tool."""
        return {
            "category": "general",
            "patterns": [],
            "workflows": {}
        }
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool with the given parameters."""
        pass
    
    def to_openai_function(self) -> Dict[str, Any]:
        """Convert tool to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    def to_anthropic_tool(self) -> Dict[str, Any]:
        """Convert tool to Anthropic tool format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters
        }


class ToolRegistry:
    """Registry for managing Eagle tools."""
    
    def __init__(self):
        self._tools: Dict[str, EagleTool] = {}
        self._interpreter = None  # Reference to current Eagle interpreter
    
    def register(self, tool: EagleTool):
        """Register a tool."""
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> EagleTool:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def set_interpreter(self, interpreter):
        """Set the current Eagle interpreter reference."""
        self._interpreter = interpreter
    
    def get_interpreter(self):
        """Get the current Eagle interpreter reference."""
        return self._interpreter
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())
    
    def get_openai_functions(self) -> List[Dict[str, Any]]:
        """Get all tools in OpenAI function calling format."""
        return [tool.to_openai_function() for tool in self._tools.values()]
    
    def get_anthropic_tools(self) -> List[Dict[str, Any]]:
        """Get all tools in Anthropic tool format."""
        return [tool.to_anthropic_tool() for tool in self._tools.values()]
    
    def get_tool_patterns(self, available_tools: List[str]) -> str:
        """Generate usage patterns from available tools."""
        if not available_tools:
            return "No tools available - operating in text-only mode."
        
        categories = {}
        all_workflows = {}
        
        for tool_name in available_tools:
            tool = self.get(tool_name)
            if tool and hasattr(tool, 'usage_patterns'):
                patterns = tool.usage_patterns
                
                # Group by category
                category = patterns.get("category", "general")
                if category not in categories:
                    categories[category] = []
                categories[category].extend(patterns.get("patterns", []))
                
                # Collect workflows
                all_workflows.update(patterns.get("workflows", {}))
        
        return self._format_patterns_for_ai(categories, all_workflows, available_tools)
    
    def _format_patterns_for_ai(self, categories: Dict[str, List[str]], workflows: Dict[str, List[str]], available_tools: List[str]) -> str:
        """Format patterns and workflows for AI system prompt."""
        sections = []
        
        # Add category-based patterns
        for category, patterns in categories.items():
            if patterns:
                category_title = category.replace("_", " ").title()
                section = f"### {category_title} Patterns\n"
                for pattern in patterns:
                    section += f"- {pattern}\n"
                sections.append(section)
        
        # Analyze workflows for availability
        available_workflows, potential_workflows = self._analyze_workflows(workflows, available_tools)
        
        # Add available workflows
        if available_workflows:
            workflow_section = "### Available Workflows\n"
            for workflow_name, steps in available_workflows.items():
                steps_str = " → ".join(steps)
                workflow_section += f"- **{workflow_name}**: {steps_str} ✅\n"
            sections.append(workflow_section)
        
        # Add potential workflows
        if potential_workflows:
            potential_section = "### Potential Workflows\n"
            for workflow_name, info in potential_workflows.items():
                steps_str = " → ".join(info['steps'])
                missing_str = ", ".join(info['missing'])
                potential_section += f"- **{workflow_name}**: {steps_str} (missing: {missing_str})\n"
            sections.append(potential_section)
            
            # Add guidance for AI
            sections.append("""
**Workflow Guidance:**
- Suggest available workflows for multi-step tasks
- Mention potential workflows when relevant to user's request  
- Offer to help user enable missing tools when it would significantly improve capabilities
- Focus on what's currently possible while being helpful about expansion options""")
        
        return "\n".join(sections) if sections else "No specific patterns defined for current tools."
    
    def _analyze_workflows(self, workflows: Dict[str, List[str]], available_tools: List[str]) -> tuple:
        """Analyze workflows into available and potential categories."""
        available_workflows = {}
        potential_workflows = {}
        
        for workflow_name, steps in workflows.items():
            missing_tools = [tool for tool in steps if tool not in available_tools]
            
            if not missing_tools:
                # All tools available
                available_workflows[workflow_name] = steps
            else:
                # Some tools missing
                potential_workflows[workflow_name] = {
                    'steps': steps,
                    'missing': missing_tools
                }
        
        return available_workflows, potential_workflows
    
    def get_user_capabilities_summary(self, available_tools: List[str]) -> str:
        """Generate user-friendly capabilities summary."""
        if not available_tools:
            return "🔧 No tools currently enabled. Run 'eagle init' to configure tools."
        
        # Collect workflows from tools
        all_workflows = {}
        for tool_name in available_tools:
            tool = self.get(tool_name)
            if tool and hasattr(tool, 'usage_patterns'):
                all_workflows.update(tool.usage_patterns.get("workflows", {}))
        
        available_workflows, potential_workflows = self._analyze_workflows(all_workflows, available_tools)
        
        summary = []
        
        if available_workflows:
            summary.append("🚀 Available Workflows:")
            for name in available_workflows.keys():
                summary.append(f"   • {name}")
        
        if potential_workflows:
            summary.append("\n💡 Unlock More Workflows:")
            for name, info in potential_workflows.items():
                tools_needed = len(info['missing'])
                summary.append(f"   • {name} (add {tools_needed} more tool{'s' if tools_needed > 1 else ''})")
            summary.append("\nRun 'eagle init' to configure additional tools.")
        
        return "\n".join(summary)
    
    def load_tools_from_directory(self, tools_dir: str) -> None:
        """Load tools from a directory containing Python tool files or tool folders."""
        if not os.path.exists(tools_dir):
            return
        
        for item in os.listdir(tools_dir):
            item_path = os.path.join(tools_dir, item)
            
            if os.path.isfile(item_path):
                # Legacy: single Python file tools
                if item.endswith('.py') and item != '__init__.py' and item != 'base.py':
                    self._load_tool_from_file(item_path)
            
            elif os.path.isdir(item_path):
                # New: tool folders with __init__.py
                init_path = os.path.join(item_path, '__init__.py')
                if os.path.exists(init_path):
                    self._load_tool_from_file(init_path)
    
    def _load_tool_from_file(self, file_path: str) -> None:
        """Load a tool from a Python file."""
        try:
            # Get module name from filename
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Add parent directory to sys.path temporarily for relative imports
            parent_dir = os.path.dirname(file_path)
            original_path = sys.path[:]
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            try:
                # Load the module
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec is None or spec.loader is None:
                    return
                
                module = importlib.util.module_from_spec(spec)
                
                # Make base module available for imports
                if 'base' not in sys.modules:
                    base_module_path = os.path.join(parent_dir, 'base.py')
                    if os.path.exists(base_module_path):
                        base_spec = importlib.util.spec_from_file_location('base', base_module_path)
                        if base_spec and base_spec.loader:
                            base_module = importlib.util.module_from_spec(base_spec)
                            sys.modules['base'] = base_module
                            base_spec.loader.exec_module(base_module)
                
                spec.loader.exec_module(module)
                
                # Find EagleTool subclasses in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, EagleTool) and 
                        attr != EagleTool):
                        # Instantiate and register the tool
                        tool_instance = attr()
                        self.register(tool_instance)
                        # print(f"Loaded custom tool: {tool_instance.name}")
                        
            finally:
                # Restore original sys.path
                sys.path[:] = original_path
                    
        except Exception as e:
            # Silently ignore tool loading errors for now
            pass


# Global tool registry
tool_registry = ToolRegistry()