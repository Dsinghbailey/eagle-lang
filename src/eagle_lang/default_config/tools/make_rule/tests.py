import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from . import MakeRuleTool


class TestMakeRuleTool(unittest.TestCase):
    def setUp(self):
        self.tool = MakeRuleTool()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_tool_properties(self):
        """Test basic tool properties."""
        self.assertEqual(self.tool.name, "make_rule")
        self.assertIn("Create custom rule files", self.tool.description)
        self.assertIn("meta-programming", self.tool.usage_patterns["category"])

    def test_generate_rule_filename(self):
        """Test rule filename generation."""
        # Test basic filename generation
        filename = self.tool._generate_rule_filename("create debugging rules for error handling")
        self.assertTrue(filename.endswith("_rules.md"))
        self.assertIn("create", filename)
        
        # Test filename cleaning
        filename = self.tool._generate_rule_filename("test@#$%^&*()rules")
        self.assertTrue(filename.replace("_rules.md", "").replace("_", "").isalnum())

    @patch('os.getcwd')
    def test_get_eagle_directory_project(self, mock_getcwd):
        """Test getting project-specific .eagle directory."""
        mock_getcwd.return_value = self.temp_dir
        eagle_dir = os.path.join(self.temp_dir, ".eagle")
        os.makedirs(eagle_dir)
        
        result = self.tool._get_eagle_directory()
        self.assertEqual(result, eagle_dir)

    @patch('os.getcwd')
    @patch('os.path.expanduser')
    def test_get_eagle_directory_user(self, mock_expanduser, mock_getcwd):
        """Test falling back to user .eagle directory."""
        mock_getcwd.return_value = self.temp_dir
        user_eagle = os.path.join(self.temp_dir, "user_eagle")
        mock_expanduser.return_value = user_eagle
        
        result = self.tool._get_eagle_directory()
        self.assertEqual(result, user_eagle)
        self.assertTrue(os.path.exists(user_eagle))

    def test_update_config_with_rule(self):
        """Test updating configuration with new rule."""
        # Setup test config
        config_path = os.path.join(self.temp_dir, "eagle_config.json")
        initial_config = {"rules": ["existing_rule.md"]}
        
        with open(config_path, 'w') as f:
            json.dump(initial_config, f)
        
        # Mock the directory
        with patch.object(self.tool, '_get_eagle_directory', return_value=self.temp_dir):
            self.tool._update_config_with_rule("new_rule.md")
        
        # Check config was updated
        with open(config_path, 'r') as f:
            updated_config = json.load(f)
        
        self.assertIn("new_rule.md", updated_config["rules"])
        self.assertIn("existing_rule.md", updated_config["rules"])

    def test_empty_input(self):
        """Test handling of empty input."""
        result = self.tool.execute("")
        self.assertIn("Please provide a description", result)
        self.assertIn("❌", result)

    @patch('eagle_lang.tools.base.tool_registry.get_interpreter')
    def test_execute_success(self, mock_get_interpreter):
        """Test successful rule creation."""
        # Mock interpreter
        mock_interpreter = MagicMock()
        mock_interpreter.generate_with_ai.return_value = "# Test Rule\n\nThis is a test rule."
        mock_get_interpreter.return_value = mock_interpreter
        
        # Mock directory methods
        with patch.object(self.tool, '_get_eagle_directory', return_value=self.temp_dir):
            with patch.object(self.tool, '_update_config_with_rule'):
                result = self.tool.execute("Create rules for testing")
        
        self.assertIn("✅", result)
        self.assertIn("Created rule file", result)
        
        # Check file was created
        rule_files = [f for f in os.listdir(self.temp_dir) if f.endswith('_rules.md')]
        self.assertTrue(len(rule_files) > 0)


if __name__ == '__main__':
    unittest.main()