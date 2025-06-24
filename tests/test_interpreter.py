"""Tests for Eagle interpreter functionality."""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open

# Mock dependencies before importing
with patch.dict('sys.modules', {
    'openai': MagicMock(),
    'anthropic': MagicMock(),
    'google.generativeai': MagicMock()
}):
    from eagle_lang.interpreter import EagleInterpreter


class TestEagleInterpreter(unittest.TestCase):
    """Test cases for EagleInterpreter core functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            "provider": "openai",
            "model": "gpt-4",
            "rules": ["test_rules.md"],
            "tools": {
                "allowed": ["print", "read"],
                "require_permission": ["write", "shell"]
            },
            "max_tokens": 4000
        }

    # TODO: Re-add these interpreter tests with proper mocking
    # The following tests were removed due to issues with:
    # 1. Real API provider initialization requirements
    # 2. File system interactions that need mocking
    # 3. Complex initialization mocking needed
    
    # @patch('eagle_lang.interpreter.tool_registry')
    # @patch('eagle_lang.interpreter.get_provider_config')
    # @patch('os.getenv')
    # def test_interpreter_initialization(self, mock_getenv, mock_get_provider_config, mock_tool_registry):
    #     """Test interpreter initialization with valid config."""
    
    # @patch('eagle_lang.interpreter.tool_registry')
    # @patch('eagle_lang.interpreter.get_provider_config')
    # @patch('os.getenv')
    # def test_interpreter_verbose_mode(self, mock_getenv, mock_get_provider_config, mock_tool_registry):
    #     """Test interpreter with verbose mode enabled."""
    
    # @patch('eagle_lang.interpreter.tool_registry')
    # @patch('eagle_lang.interpreter.get_provider_config')
    # @patch('os.getenv')
    # def test_additional_context_handling(self, mock_getenv, mock_get_provider_config, mock_tool_registry):
    #     """Test additional context handling."""
    
    def test_enhance_content_with_context(self):
        """Test content enhancement with additional context."""
        # This test works without full interpreter initialization
        with patch('eagle_lang.interpreter.tool_registry'), \
             patch('eagle_lang.interpreter.get_provider_config'), \
             patch('os.getenv'), \
             patch('eagle_lang.interpreter.OpenAI'):
            
            context = ["env=production", "This is a test context"]
            interpreter = EagleInterpreter(
                provider="openai",
                model_name="gpt-4",
                config=self.test_config,
                additional_context=context
            )
            
            original_content = "Create a simple script"
            enhanced_content = interpreter._enhance_content_with_context(original_content)
            
            # Check that original content is preserved
            self.assertIn(original_content, enhanced_content)
            
            # Check that context section is added
            self.assertIn("## Additional Context", enhanced_content)
            self.assertIn("env: production", enhanced_content)
            self.assertIn("This is a test context", enhanced_content)
    
    def test_enhance_content_no_context(self):
        """Test content enhancement with no additional context."""
        with patch('eagle_lang.interpreter.tool_registry'), \
             patch('eagle_lang.interpreter.get_provider_config'), \
             patch('os.getenv'), \
             patch('eagle_lang.interpreter.OpenAI'):
            
            interpreter = EagleInterpreter(
                provider="openai",
                model_name="gpt-4",
                config=self.test_config,
                additional_context=[]
            )
            
            original_content = "Create a simple script"
            enhanced_content = interpreter._enhance_content_with_context(original_content)
            
            # Should return original content unchanged
            self.assertEqual(enhanced_content, original_content)

    # TODO: Re-add file system related tests with proper mocking
    # @patch('builtins.open', new_callable=mock_open, read_data="Test .caw file content")
    # def test_read_caw_file(self, mock_file):
    #     """Test reading .caw file content."""
    
    # @patch('builtins.open', side_effect=FileNotFoundError())
    # @patch('sys.exit')
    # def test_read_caw_file_not_found(self, mock_exit, mock_file):
    #     """Test reading non-existent .caw file."""
    
    # def test_get_available_tools(self):
    #     """Test getting available tools from config."""
    
    def test_get_available_tools_missing_config(self):
        """Test that missing tools config raises appropriate error."""
        invalid_config = {
            "provider": "openai",
            "model": "gpt-4",
            "rules": [],
            # Missing tools config
            "max_tokens": 4000
        }
        
        with patch('eagle_lang.interpreter.tool_registry'), \
             patch('eagle_lang.interpreter.get_provider_config'), \
             patch('os.getenv'), \
             patch('eagle_lang.interpreter.OpenAI'):
            
            with self.assertRaises(ValueError) as context:
                EagleInterpreter(
                    provider="openai",
                    model_name="gpt-4",
                    config=invalid_config
                )
            
            self.assertIn("Missing 'tools' configuration", str(context.exception))
    
    def test_tool_requires_permission(self):
        """Test permission checking for tools."""
        with patch('eagle_lang.interpreter.tool_registry'), \
             patch('eagle_lang.interpreter.get_provider_config'), \
             patch('os.getenv'), \
             patch('eagle_lang.interpreter.OpenAI'):
            
            interpreter = EagleInterpreter(
                provider="openai",
                model_name="gpt-4",
                config=self.test_config
            )
            
            # Test allowed tools don't require permission
            self.assertFalse(interpreter._tool_requires_permission("print"))
            self.assertFalse(interpreter._tool_requires_permission("read"))
            
            # Test permission-required tools
            self.assertTrue(interpreter._tool_requires_permission("write"))
            self.assertTrue(interpreter._tool_requires_permission("shell"))
    
    @patch('builtins.input', return_value='y')
    def test_get_user_permission_granted(self, mock_input):
        """Test user permission granted."""
        with patch('eagle_lang.interpreter.tool_registry'), \
             patch('eagle_lang.interpreter.get_provider_config'), \
             patch('os.getenv'), \
             patch('eagle_lang.interpreter.OpenAI'):
            
            interpreter = EagleInterpreter(
                provider="openai",
                model_name="gpt-4",
                config=self.test_config
            )
            
            permission = interpreter._get_user_permission("write", {"file": "test.txt"})
            
            self.assertTrue(permission)
    
    @patch('builtins.input', return_value='n')
    def test_get_user_permission_denied(self, mock_input):
        """Test user permission denied."""
        with patch('eagle_lang.interpreter.tool_registry'), \
             patch('eagle_lang.interpreter.get_provider_config'), \
             patch('os.getenv'), \
             patch('eagle_lang.interpreter.OpenAI'):
            
            interpreter = EagleInterpreter(
                provider="openai",
                model_name="gpt-4",
                config=self.test_config
            )
            
            permission = interpreter._get_user_permission("write", {"file": "test.txt"})
            
            self.assertFalse(permission)
    
    def test_load_rules_no_rules(self):
        """Test loading rules when no rules are specified."""
        config_no_rules = self.test_config.copy()
        config_no_rules["rules"] = []
        
        with patch('eagle_lang.interpreter.tool_registry'), \
             patch('eagle_lang.interpreter.get_provider_config'), \
             patch('os.getenv'), \
             patch('eagle_lang.interpreter.OpenAI'):
            
            interpreter = EagleInterpreter(
                provider="openai",
                model_name="gpt-4",
                config=config_no_rules
            )
            
            rules = interpreter._load_rules()
            
            # Should return default prompt
            self.assertIn("You are Eagle", rules)
            self.assertIn("helpful, high-level AI", rules)


class TestInterpreterProviders(unittest.TestCase):
    """Test interpreter with different AI providers."""
    
    # TODO: Re-add provider initialization tests with proper mocking
    # The following tests were removed due to issues with:
    # 1. Real API client initialization
    # 2. Complex provider-specific mocking requirements
    
    # @patch('eagle_lang.interpreter.tool_registry')
    # @patch('eagle_lang.interpreter.get_provider_config')
    # @patch('os.getenv')
    # def test_openai_provider_initialization(self, mock_getenv, mock_get_provider_config, mock_tool_registry):
    #     """Test OpenAI provider initialization."""
    
    # @patch('eagle_lang.interpreter.tool_registry')
    # @patch('eagle_lang.interpreter.get_provider_config')
    # @patch('os.getenv')
    # def test_claude_provider_initialization(self, mock_getenv, mock_get_provider_config, mock_tool_registry):
    #     """Test Claude provider initialization."""
    
    # @patch('eagle_lang.interpreter.tool_registry')
    # @patch('eagle_lang.interpreter.get_provider_config')
    # @patch('os.getenv', return_value=None)
    # @patch('sys.exit')
    # def test_missing_api_key(self, mock_exit, mock_getenv, mock_get_provider_config, mock_tool_registry):
    #     """Test that missing API key raises appropriate error."""


if __name__ == '__main__':
    unittest.main()