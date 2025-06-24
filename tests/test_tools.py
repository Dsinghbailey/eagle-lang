"""Tests for Eagle tool system."""

import unittest
import os
from unittest.mock import patch, MagicMock
from eagle_lang.tools.base import EagleTool, tool_registry


class MockTool(EagleTool):
    """Mock tool for testing."""
    
    @property
    def name(self) -> str:
        return "mock_tool"
    
    @property
    def description(self) -> str:
        return "A mock tool for testing"
    
    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "Test input"
                }
            },
            "required": ["input"]
        }
    
    @property
    def usage_patterns(self) -> dict:
        return {
            "category": "test",
            "patterns": ["Test pattern"],
            "workflows": {"Test Workflow": ["mock_tool"]}
        }
    
    def execute(self, input: str) -> str:
        return f"Mock execution: {input}"


class TestEagleTool(unittest.TestCase):
    """Test cases for EagleTool base class."""
    
    def test_tool_properties(self):
        """Test that tool has required properties."""
        tool = MockTool()
        
        self.assertEqual(tool.name, "mock_tool")
        self.assertEqual(tool.description, "A mock tool for testing")
        self.assertIsInstance(tool.parameters, dict)
        self.assertIsInstance(tool.usage_patterns, dict)
    
    def test_tool_execution(self):
        """Test tool execution."""
        tool = MockTool()
        result = tool.execute(input="test")
        
        self.assertEqual(result, "Mock execution: test")
    
    def test_parameters_structure(self):
        """Test parameters follow JSON schema structure."""
        tool = MockTool()
        params = tool.parameters
        
        self.assertEqual(params["type"], "object")
        self.assertIn("properties", params)
        self.assertIn("required", params)
        
        # Check that required input property exists
        self.assertIn("input", params["properties"])
        self.assertIn("input", params["required"])
    
    def test_usage_patterns_structure(self):
        """Test usage patterns have required structure."""
        tool = MockTool()
        patterns = tool.usage_patterns
        
        self.assertIn("category", patterns)
        self.assertIn("patterns", patterns)
        self.assertIn("workflows", patterns)
        
        self.assertIsInstance(patterns["patterns"], list)
        self.assertIsInstance(patterns["workflows"], dict)


class TestToolRegistry(unittest.TestCase):
    """Test cases for tool registry functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear registry for clean tests
        tool_registry._tools.clear()
        tool_registry.interpreter = None
    
    def tearDown(self):
        """Clean up after tests."""
        # Clear registry after tests
        tool_registry._tools.clear()
        tool_registry.interpreter = None
    
    def test_register_tool(self):
        """Test registering a tool."""
        tool = MockTool()
        tool_registry.register(tool)
        
        self.assertIn("mock_tool", tool_registry._tools)
        self.assertEqual(tool_registry._tools["mock_tool"], tool)
    
    def test_get_tool(self):
        """Test getting a registered tool."""
        tool = MockTool()
        tool_registry.register(tool)
        
        retrieved_tool = tool_registry.get("mock_tool")
        self.assertEqual(retrieved_tool, tool)
    
    def test_get_nonexistent_tool(self):
        """Test getting a non-existent tool returns None."""
        result = tool_registry.get("nonexistent_tool")
        self.assertIsNone(result)
    
    def test_list_tools(self):
        """Test listing registered tools."""
        tool1 = MockTool()
        
        # Create second mock tool with different name
        class MockTool2(MockTool):
            @property
            def name(self) -> str:
                return "mock_tool_2"
        
        tool2 = MockTool2()
        
        tool_registry.register(tool1)
        tool_registry.register(tool2)
        
        tools = tool_registry.list_tools()
        self.assertIn("mock_tool", tools)
        self.assertIn("mock_tool_2", tools)
    
    def test_get_openai_functions(self):
        """Test getting OpenAI function definitions."""
        tool = MockTool()
        tool_registry.register(tool)
        
        functions = tool_registry.get_openai_functions()
        
        self.assertIsInstance(functions, list)
        self.assertEqual(len(functions), 1)
        
        function_def = functions[0]
        self.assertEqual(function_def["type"], "function")
        self.assertEqual(function_def["function"]["name"], "mock_tool")
        self.assertEqual(function_def["function"]["description"], "A mock tool for testing")
        self.assertEqual(function_def["function"]["parameters"], tool.parameters)
    
    def test_get_anthropic_tools(self):
        """Test getting Anthropic tool definitions."""
        tool = MockTool()
        tool_registry.register(tool)
        
        tools = tool_registry.get_anthropic_tools()
        
        self.assertIsInstance(tools, list)
        self.assertEqual(len(tools), 1)
        
        tool_def = tools[0]
        self.assertEqual(tool_def["name"], "mock_tool")
        self.assertEqual(tool_def["description"], "A mock tool for testing")
        self.assertEqual(tool_def["input_schema"], tool.parameters)
    
    def test_get_user_capabilities_summary(self):
        """Test getting user capabilities summary."""
        tool = MockTool()
        tool_registry.register(tool)
        
        summary = tool_registry.get_user_capabilities_summary(["mock_tool"])
        
        self.assertIsInstance(summary, str)
        # The summary format may vary, just check it's not empty
        self.assertGreater(len(summary), 0)
    
    def test_get_tool_patterns(self):
        """Test getting tool patterns."""
        tool = MockTool()
        tool_registry.register(tool)
        
        patterns = tool_registry.get_tool_patterns(["mock_tool"])
        
        self.assertIsInstance(patterns, str)
        self.assertIn("Test pattern", patterns)
    
    def test_set_interpreter(self):
        """Test setting interpreter reference."""
        mock_interpreter = MagicMock()
        tool_registry.set_interpreter(mock_interpreter)
        
        self.assertEqual(tool_registry.get_interpreter(), mock_interpreter)
    
    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('importlib.util.spec_from_file_location')
    @patch('importlib.util.module_from_spec')
    def test_load_tools_from_directory(self, mock_module_from_spec, mock_spec_from_file, mock_listdir, mock_exists):
        """Test loading tools from directory."""
        # Mock directory exists and contains tool directories
        mock_exists.return_value = True
        mock_listdir.return_value = ["test_tool"]
        
        # Mock module loading
        mock_spec = MagicMock()
        mock_spec_from_file.return_value = mock_spec
        
        mock_module = MagicMock()
        mock_module_from_spec.return_value = mock_module
        
        # Mock the tool class in the module
        mock_tool_class = MagicMock()
        mock_tool_instance = MockTool()
        mock_tool_class.return_value = mock_tool_instance
        
        # Set up module attributes
        mock_module.__dict__ = {"TestTool": mock_tool_class}
        
        with patch('os.path.isdir', return_value=True):
            tool_registry.load_tools_from_directory("/mock/tools")
        
        # Verify module loading was attempted
        mock_spec_from_file.assert_called()
    
    def test_load_tools_from_nonexistent_directory(self):
        """Test loading tools from non-existent directory."""
        with patch('os.path.exists', return_value=False):
            # Should not raise exception
            tool_registry.load_tools_from_directory("/nonexistent/path")
        
        # Registry should remain empty
        self.assertEqual(len(tool_registry._tools), 0)


class TestBuiltinTools(unittest.TestCase):
    """Test cases for built-in tools."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Import built-in tools with correct path
        try:
            from eagle_lang.default_config.tools.print import PrintTool
            self.print_tool = PrintTool()
        except ImportError:
            self.print_tool = None
    
    def test_print_tool_basic_functionality(self):
        """Test print tool basic functionality."""
        if self.print_tool is None:
            self.skipTest("Print tool not available - missing dependencies")
        
        result = self.print_tool.execute(content="Hello World")
        
        self.assertIsInstance(result, str)
        self.assertIn("printed to console", result)
    
    def test_print_tool_properties(self):
        """Test print tool properties."""
        if self.print_tool is None:
            self.skipTest("Print tool not available - missing dependencies")
            
        self.assertEqual(self.print_tool.name, "print")
        self.assertIsNotNone(self.print_tool.description)
        self.assertIsInstance(self.print_tool.parameters, dict)
        self.assertIsInstance(self.print_tool.usage_patterns, dict)
    
    def test_print_tool_parameters(self):
        """Test print tool parameters structure."""
        if self.print_tool is None:
            self.skipTest("Print tool not available - missing dependencies")
            
        params = self.print_tool.parameters
        
        self.assertEqual(params["type"], "object")
        self.assertIn("content", params["properties"])
        self.assertIn("content", params["required"])
        
        # Check optional parameters
        self.assertIn("style", params["properties"])
        self.assertIn("newline", params["properties"])
    
    def test_print_tool_style_options(self):
        """Test print tool style options."""
        if self.print_tool is None:
            self.skipTest("Print tool not available - missing dependencies")
            
        params = self.print_tool.parameters
        style_prop = params["properties"]["style"]
        
        self.assertIn("enum", style_prop)
        expected_styles = ["plain", "header", "info", "success", "warning", "error"]
        self.assertEqual(style_prop["enum"], expected_styles)


class TestToolValidation(unittest.TestCase):
    """Test cases for tool validation."""
    
    def test_invalid_tool_missing_method(self):
        """Test that tools with missing required methods can't be instantiated properly."""
        
        class InvalidTool(EagleTool):
            # Missing required abstract methods
            pass
        
        # Should not be able to instantiate without implementing abstract methods
        with self.assertRaises(TypeError):
            InvalidTool()
    
    def test_tool_execute_error_handling(self):
        """Test tool execution error handling."""
        
        class ErrorTool(EagleTool):
            @property
            def name(self) -> str:
                return "error_tool"
            
            @property
            def description(self) -> str:
                return "Tool that raises errors"
            
            @property
            def parameters(self) -> dict:
                return {"type": "object", "properties": {}, "required": []}
            
            @property
            def usage_patterns(self) -> dict:
                return {"category": "test", "patterns": [], "workflows": {}}
            
            def execute(self, **kwargs) -> str:
                raise ValueError("Test error")
        
        tool = ErrorTool()
        
        # Error should propagate (not caught by base class)
        with self.assertRaises(ValueError):
            tool.execute()


if __name__ == '__main__':
    unittest.main()