from eagle_lang.tools.base import EagleTool, tool_registry
import os
import json


class MakeRuleTool(EagleTool):
    @property
    def name(self) -> str:
        return "make_rule"

    @property
    def description(self) -> str:
        return "Create custom rule files for Eagle based on user description"

    @property
    def usage_patterns(self) -> dict:
        return {
            "category": "meta-programming",
            "patterns": [
                "Create a rule for [specific behavior]",
                "Make a rule that [describes behavior]",
                "Generate rules for [use case]",
                "Add a rule to [handle situation]"
            ],
            "workflows": {
                "Custom Rule Creation": ["make_rule", "edit_config"],
                "Rule Management": ["make_rule", "read", "edit_config"]
            }
        }

    def execute(self, input: str) -> str:
        """Generate a custom rule file based on user description."""
        try:
            # Parse the input to extract rule description
            rule_description = input.strip()
            
            if not rule_description:
                return "❌ Please provide a description for the rule you want to create"
            
            # Generate rule content using AI
            rule_content = self._generate_rule_content(rule_description)
            
            # Determine filename
            rule_name = self._generate_rule_filename(rule_description)
            
            # Save to .eagle folder
            eagle_dir = self._get_eagle_directory()
            rule_path = os.path.join(eagle_dir, rule_name)
            
            with open(rule_path, 'w') as f:
                f.write(rule_content)
            
            # Update config to include the new rule
            self._update_config_with_rule(rule_name)
            
            return f"✅ Created rule file: {rule_path}\n📝 Rule automatically added to Eagle configuration"
            
        except Exception as e:
            return f"❌ Error creating rule: {str(e)}"

    def _generate_rule_content(self, description: str) -> str:
        """Generate rule content using AI."""
        interpreter = tool_registry.get_interpreter()
        
        prompt = f"""Generate a markdown rule file for Eagle AI assistant based on this description:

"{description}"

The rule file should:
1. Be written in clear, actionable markdown
2. Follow the format of existing Eagle rules
3. Include specific behavioral guidelines
4. Be concise but comprehensive
5. Focus on practical execution guidelines

Format as a complete markdown file with appropriate headers and structure.
Do not include any code blocks or technical implementation details.
Focus on behavioral rules and guidelines for the AI assistant.

Generate only the markdown content, no additional text or explanations."""

        return interpreter.generate_with_ai(prompt, max_tokens=2000)

    def _generate_rule_filename(self, description: str) -> str:
        """Generate an appropriate filename for the rule."""
        # Extract key words and create filename
        words = description.lower().split()
        # Filter out common words
        filtered_words = [w for w in words if w not in ['a', 'an', 'the', 'for', 'to', 'that', 'and', 'or', 'but', 'in', 'on', 'at', 'by']]
        # Take first few meaningful words
        key_words = filtered_words[:3]
        filename = "_".join(key_words) + "_rules.md"
        
        # Clean filename
        filename = "".join(c for c in filename if c.isalnum() or c in ['_', '-', '.'])
        
        return filename

    def _get_eagle_directory(self) -> str:
        """Get the appropriate .eagle directory."""
        # Check for project-specific .eagle directory first
        project_eagle = os.path.join(os.getcwd(), ".eagle")
        if os.path.exists(project_eagle):
            return project_eagle
        
        # Fall back to user global .eagle directory
        user_eagle = os.path.expanduser("~/.eagle")
        os.makedirs(user_eagle, exist_ok=True)
        return user_eagle

    def _update_config_with_rule(self, rule_filename: str) -> None:
        """Update Eagle configuration to include the new rule."""
        eagle_dir = self._get_eagle_directory()
        config_path = os.path.join(eagle_dir, "eagle_config.json")
        
        # Load existing config
        config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        
        # Add rule to rules list
        rules = config.get("rules", [])
        if rule_filename not in rules:
            rules.append(rule_filename)
            config["rules"] = rules
            
            # Save updated config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)