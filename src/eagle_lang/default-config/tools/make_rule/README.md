# Make Rule Tool

The `make_rule` tool allows you to create custom rule files for Eagle based on natural language descriptions. Rules define how Eagle should behave in specific situations and guide its decision-making process.

## What it does

- **AI-Generated Rules**: Describe what rules you want, and Eagle generates the complete rule file
- **Auto-Configuration**: Automatically adds new rules to your Eagle configuration
- **Smart Naming**: Generates appropriate filenames based on rule descriptions
- **Project Integration**: Rules are saved to your project's `.eagle` folder or global config

## Usage Patterns

### Basic Rule Creation
```
Create a rule for handling database connections safely
Make a rule that prioritizes user confirmation for file deletions
Generate rules for API rate limiting behavior
```

### Specific Behavioral Rules
```
Create rules for debugging workflow - always show intermediate steps
Make a rule that requires permission before modifying configuration files
Add a rule to handle error recovery gracefully
```

### Domain-Specific Rules
```
Create rules for web scraping ethics and rate limiting
Make rules for secure handling of sensitive data
Generate rules for code review and quality checks
```

## How it works

1. **Description Analysis**: Parses your natural language description
2. **AI Generation**: Uses the current AI session to generate appropriate rule content
3. **File Creation**: Saves the rule as a markdown file in your `.eagle` folder
4. **Config Update**: Automatically adds the new rule to your Eagle configuration
5. **Immediate Activation**: Rules become active for the next Eagle session

## File Structure

Created rules follow this structure:
```
.eagle/
├── your_custom_rules.md     # Generated rule file
└── eagle_config.json       # Updated with new rule reference
```

## Rule Format

Generated rules are structured markdown files containing:
- Clear behavioral guidelines
- Specific execution instructions
- Context-aware recommendations
- Integration with existing Eagle principles

## Examples

### Input
```
Create rules for secure file operations
```

### Generated Output
```markdown
# Secure File Operations Rules

## File Access Guidelines
- Always verify file paths are within allowed directories
- Request permission before modifying system files
- Validate file permissions before operations
- Log all file operations for audit trail

## Security Practices
- Never expose sensitive file contents
- Use secure temporary files when needed
- Clean up temporary files after use
- Respect user privacy and data protection
```

## Integration

The tool integrates seamlessly with Eagle's existing rule system:
- New rules combine with existing `eagle_rules.md`
- Rules are loaded in the order specified in configuration
- Custom rules can override or extend default behaviors
- No restart required - changes take effect on next session

## Best Practices

1. **Be Specific**: Describe exactly what behavior you want
2. **Consider Context**: Think about when and how the rules should apply
3. **Test Rules**: Create test scenarios to verify rule behavior
4. **Document Purpose**: Include the reasoning behind rule creation
5. **Review Generated Content**: Always review AI-generated rules before use

## Security Considerations

- Rules are stored as plain text markdown files
- Generated rules follow Eagle's security principles
- Custom rules cannot override core security restrictions
- Rules are scoped to the configuration they're added to