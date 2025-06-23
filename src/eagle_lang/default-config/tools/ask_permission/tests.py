"""Tests for the ask_permission tool."""

import pytest
from unittest.mock import patch, MagicMock
from . import AskPermissionTool


class TestAskPermissionTool:
    """Test cases for AskPermissionTool."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tool = AskPermissionTool()
    
    def test_tool_properties(self):
        """Test that tool properties are correctly defined."""
        assert self.tool.name == "ask_permission"
        assert "permission" in self.tool.description.lower()
        assert "prompt" in self.tool.parameters["properties"]
        assert self.tool.parameters["required"] == ["prompt"]
    
    def test_usage_patterns(self):
        """Test that usage patterns are properly defined."""
        patterns = self.tool.usage_patterns
        assert patterns["category"] == "interaction"
        assert len(patterns["patterns"]) > 0
        assert "workflows" in patterns
    
    @patch('builtins.input', return_value="yes")
    @patch('builtins.print')
    def test_execute_with_response(self, mock_print, mock_input):
        """Test executing with user response."""
        result = self.tool.execute(prompt="Do you want to continue?", expect_response=True)
        
        assert "User responded: yes" in result
        mock_input.assert_called_once_with("> ")
    
    @patch('builtins.input', return_value="")
    @patch('builtins.print')
    def test_execute_with_empty_response(self, mock_print, mock_input):
        """Test executing with empty user response."""
        result = self.tool.execute(prompt="Continue?", expect_response=True)
        
        assert "User provided no response" in result
        mock_input.assert_called_once_with("> ")
    
    @patch('builtins.input', return_value="")
    @patch('builtins.print')
    def test_execute_no_response_expected(self, mock_print, mock_input):
        """Test executing when no response is expected."""
        result = self.tool.execute(prompt="Press Enter to continue", expect_response=False)
        
        assert "User acknowledged" in result
        mock_input.assert_called_once_with()
    
    @patch('builtins.input', side_effect=KeyboardInterrupt())
    @patch('builtins.print')
    def test_execute_keyboard_interrupt(self, mock_print, mock_input):
        """Test handling keyboard interrupt."""
        result = self.tool.execute(prompt="Continue?")
        
        assert "User interrupted" in result
        assert "Ctrl+C" in result
    
    @patch('builtins.input', side_effect=Exception("Test error"))
    @patch('builtins.print')
    def test_execute_error_handling(self, mock_print, mock_input):
        """Test error handling during execution."""
        result = self.tool.execute(prompt="Continue?")
        
        assert "Error during wait" in result
        assert "Test error" in result
    
    def test_parameter_schema(self):
        """Test parameter schema validation."""
        params = self.tool.parameters
        
        # Check required fields
        assert "prompt" in params["required"]
        
        # Check property types
        props = params["properties"]
        assert props["prompt"]["type"] == "string"
        assert props["expect_response"]["type"] == "boolean"
        assert props["timeout"]["type"] == "integer"
        
        # Check defaults
        assert props["expect_response"]["default"] is True
        assert props["timeout"]["minimum"] == 1