"""Tests for Eagle configuration system."""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, mock_open, MagicMock

# Mock dotenv before importing config
with patch.dict('sys.modules', {'dotenv': MagicMock()}):
    from eagle_lang.config import load_config, get_default_config


class TestConfig(unittest.TestCase):
    """Test cases for configuration loading and management."""
    
    def test_get_default_config(self):
        """Test that default config is properly loaded."""
        default_config = get_default_config()
        
        # Check required keys exist
        required_keys = ["provider", "model", "rules", "tools", "max_tokens"]
        for key in required_keys:
            self.assertIn(key, default_config)
        
        # Check default values
        self.assertIsInstance(default_config["provider"], str)
        self.assertIsInstance(default_config["model"], str)
        self.assertIsInstance(default_config["rules"], list)
        self.assertIsInstance(default_config["tools"], dict)
        self.assertIsInstance(default_config["max_tokens"], int)
    
    def test_load_config_default_fallback(self):
        """Test that load_config falls back to default when no config files exist."""
        with patch('os.path.exists', return_value=False):
            config = load_config()
            default_config = get_default_config()
            self.assertEqual(config, default_config)
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_load_config_project_file(self, mock_exists, mock_file):
        """Test loading config from project directory."""
        # Mock project config exists
        def exists_side_effect(path):
            return path.endswith('.eagle/eagle_config.json')
        
        mock_exists.side_effect = exists_side_effect
        
        # Mock config content
        test_config = {
            "provider": "claude",
            "model": "claude-3-sonnet",
            "rules": ["custom_rules.md"],
            "tools": {"allowed": ["print", "read"], "require_permission": ["write"]},
            "max_tokens": 8000
        }
        mock_file.return_value.read.return_value = json.dumps(test_config)
        
        config = load_config()
        
        # Verify loaded config matches test config
        self.assertEqual(config["provider"], "claude")
        self.assertEqual(config["model"], "claude-3-sonnet")
        self.assertEqual(config["max_tokens"], 8000)
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_load_config_user_home_fallback(self, mock_exists, mock_file):
        """Test loading config from user home directory when project config doesn't exist."""
        # Mock only home config exists
        def exists_side_effect(path):
            return '~/.eagle/eagle_config.json' in path
        
        mock_exists.side_effect = exists_side_effect
        
        # Mock config content
        test_config = {
            "provider": "openai",
            "model": "gpt-4",
            "rules": ["global_rules.md"],
            "tools": {"allowed": ["print"], "require_permission": ["write", "shell"]},
            "max_tokens": 4000
        }
        mock_file.return_value.read.return_value = json.dumps(test_config)
        
        with patch('os.path.expanduser', return_value='/mock/home/.eagle/eagle_config.json'):
            config = load_config()
        
        # Verify loaded config matches test config
        self.assertEqual(config["provider"], "openai")
        self.assertEqual(config["model"], "gpt-4")
        self.assertEqual(config["max_tokens"], 4000)
    
    
    def test_tools_config_structure(self):
        """Test that tools config has correct structure."""
        config = get_default_config()
        tools = config["tools"]
        
        # Should have both allowed and require_permission
        self.assertIn("allowed", tools)
        self.assertIn("require_permission", tools)
        
        # Both should be lists
        self.assertIsInstance(tools["allowed"], list)
        self.assertIsInstance(tools["require_permission"], list)
        
        # Should have some default tools
        self.assertGreater(len(tools["allowed"]), 0)
        self.assertGreater(len(tools["require_permission"]), 0)


if __name__ == '__main__':
    unittest.main()