"""Tests for print tool."""

import unittest
from . import PrintTool


class TestPrintTool(unittest.TestCase):
    """Test cases for the print tool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = PrintTool()
    
    def test_tool_properties(self):
        """Test that tool has required properties."""
        self.assertEqual(self.tool.name, "print")
        self.assertIsNotNone(self.tool.description)
        self.assertIsNotNone(self.tool.parameters)
    
    def test_basic_execution(self):
        """Test basic tool execution."""
        result = self.tool.execute(content="test message")
        self.assertIsInstance(result, str)
        self.assertIn("printed to console", result)
    
    def test_style_formatting(self):
        """Test different style options."""
        styles = ["plain", "header", "info", "success", "warning", "error"]
        for style in styles:
            result = self.tool.execute(content="test", style=style)
            self.assertIn("printed to console", result)
            self.assertIn(f"({style} style)", result)
    
    def test_newline_parameter(self):
        """Test newline parameter behavior."""
        result_with_newline = self.tool.execute(content="test", newline=True)
        result_without_newline = self.tool.execute(content="test", newline=False)
        
        self.assertIsInstance(result_with_newline, str)
        self.assertIsInstance(result_without_newline, str)
    
    def test_usage_patterns(self):
        """Test usage patterns are properly defined."""
        patterns = self.tool.usage_patterns
        self.assertEqual(patterns["category"], "communication")
        self.assertIsInstance(patterns["patterns"], list)
        self.assertGreater(len(patterns["patterns"]), 0)


if __name__ == '__main__':
    unittest.main()