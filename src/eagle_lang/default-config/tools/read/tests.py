"""Tests for read tool."""

import unittest
import tempfile
import os
from . import ReadTool


class TestReadTool(unittest.TestCase):
    """Test cases for the read tool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = ReadTool()
        
        # Create a temporary test file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        self.temp_file.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")
        self.temp_file.close()
        
        # Get relative path for sandboxing
        self.test_file_path = os.path.relpath(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_tool_properties(self):
        """Test that tool has required properties."""
        self.assertEqual(self.tool.name, "read")
        self.assertIsNotNone(self.tool.description)
        self.assertIsNotNone(self.tool.parameters)
    
    def test_basic_file_read(self):
        """Test basic file reading."""
        result = self.tool.execute(file_path=self.test_file_path)
        self.assertIsInstance(result, str)
        self.assertIn("Line 1", result)
        self.assertIn("Line 5", result)
    
    def test_line_range_reading(self):
        """Test reading specific line ranges."""
        result = self.tool.execute(file_path=self.test_file_path, start_line=2, end_line=4)
        self.assertIn("Line 2", result)
        self.assertIn("Line 3", result)
        self.assertNotIn("Line 1", result)
        self.assertNotIn("Line 5", result)
    
    def test_max_lines_limit(self):
        """Test max lines limitation."""
        result = self.tool.execute(file_path=self.test_file_path, max_lines=2)
        lines_in_result = result.count("Line")
        self.assertLessEqual(lines_in_result, 2)
    
    def test_nonexistent_file(self):
        """Test behavior with nonexistent file."""
        result = self.tool.execute(file_path="nonexistent_file.txt")
        self.assertIn("File not found", result)
    
    def test_sandboxing(self):
        """Test that sandboxing prevents access outside current directory."""
        result = self.tool.execute(file_path="/etc/passwd")
        self.assertIn("Access denied", result)
    
    def test_usage_patterns(self):
        """Test usage patterns are properly defined."""
        patterns = self.tool.usage_patterns
        self.assertEqual(patterns["category"], "file_operations")
        self.assertIsInstance(patterns["patterns"], list)
        self.assertGreater(len(patterns["patterns"]), 0)


if __name__ == '__main__':
    unittest.main()