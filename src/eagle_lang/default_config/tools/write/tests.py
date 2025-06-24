"""Tests for write tool."""

import unittest
import tempfile
import os
from . import WriteTool


class TestWriteTool(unittest.TestCase):
    """Test cases for the write tool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = WriteTool()
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.txt")
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_file):
            os.unlink(self.test_file)
        os.rmdir(self.temp_dir)
    
    def test_tool_properties(self):
        """Test that tool has required properties."""
        self.assertEqual(self.tool.name, "write")
        self.assertIsNotNone(self.tool.description)
        self.assertIsNotNone(self.tool.parameters)
    
    def test_basic_write(self):
        """Test basic file writing."""
        content = "Test content"
        result = self.tool.execute(content=content, file_path=self.test_file)
        self.assertIn("successfully written", result)
        
        # Verify file was created and contains correct content
        with open(self.test_file, 'r') as f:
            written_content = f.read()
        self.assertEqual(written_content, content)
    
    def test_append_mode(self):
        """Test append mode."""
        # Write initial content
        self.tool.execute(content="First line\n", file_path=self.test_file)
        
        # Append more content
        result = self.tool.execute(content="Second line\n", file_path=self.test_file, mode="append")
        self.assertIn("appended to", result)
        
        # Verify both lines are present
        with open(self.test_file, 'r') as f:
            content = f.read()
        self.assertIn("First line", content)
        self.assertIn("Second line", content)
    
    def test_directory_creation(self):
        """Test that directories are created if they don't exist."""
        nested_file = os.path.join(self.temp_dir, "subdir", "nested.txt")
        result = self.tool.execute(content="nested content", file_path=nested_file)
        self.assertIn("successfully written", result)
        self.assertTrue(os.path.exists(nested_file))


if __name__ == '__main__':
    unittest.main()