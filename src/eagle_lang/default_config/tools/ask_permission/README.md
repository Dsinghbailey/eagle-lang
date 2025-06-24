# Ask Permission Tool

The `ask_permission` tool enables interactive communication with users by requesting input, confirmation, or feedback during Eagle workflow execution.

## Overview

This tool pauses execution and waits for user input, making it essential for:
- Getting user confirmation before destructive operations
- Collecting user preferences or choices
- Creating interactive workflows
- Implementing user-guided processes

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | "Press Enter to continue..." | The message or question to display to the user |
| `expect_response` | boolean | No | `true` | Whether to expect a text response or just wait for Enter |
| `timeout` | integer | No | None | Optional timeout in seconds (minimum 1) |

## Usage Examples

### Basic Confirmation
```python
# Simple yes/no confirmation
result = ask_permission(
    prompt="Do you want to delete this file? (y/n)",
    expect_response=True
)
```

### Acknowledgment Only
```python
# Just wait for user to press Enter
result = ask_permission(
    prompt="Review the output above. Press Enter when ready to continue.",
    expect_response=False
)
```

### With Timeout
```python
# Wait with timeout (simplified implementation)
result = ask_permission(
    prompt="Enter your choice (or wait 30 seconds for default):",
    expect_response=True,
    timeout=30
)
```

## Return Values

The tool returns different messages based on the interaction:

- **User Response**: `"User responded: {user_input}"` - When user provides text input
- **Empty Response**: `"User provided no response (empty input)"` - When user presses Enter without text
- **Acknowledgment**: `"User acknowledged (pressed Enter)"` - When `expect_response=False`
- **Interrupted**: `"User interrupted the wait (Ctrl+C)"` - When user cancels with Ctrl+C
- **Error**: `"Error during wait: {error_message}"` - When an error occurs

## Usage Patterns

### Confirmation Flow
```
ask_permission → shell
```
Get user confirmation before executing shell commands.

### Interactive Setup
```
ask_permission → write → ask_permission
```
Collect user input, write configuration, then confirm settings.

### User Input Collection
```
ask_permission → write
```
Gather user data and save it to files.

## Best Practices

1. **Clear Prompts**: Write clear, specific prompts that tell users exactly what you need
2. **Appropriate Expectations**: Set `expect_response=False` for simple acknowledgments
3. **Error Handling**: Always handle the possibility of user interruption
4. **Context**: Provide enough context in the prompt for users to make informed decisions

## Technical Notes

- The tool handles keyboard interrupts (Ctrl+C) gracefully
- Timeout implementation is simplified and may need enhancement for production use
- Input is automatically stripped of leading/trailing whitespace
- Empty responses are differentiated from no-response scenarios

## Security Considerations

- User input is not validated or sanitized - implement validation in calling code if needed
- Sensitive information in prompts will be visible in logs and terminal output
- Consider the security implications of any user input that will be used in subsequent operations