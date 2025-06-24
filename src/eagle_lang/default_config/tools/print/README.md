# Print Tool

Print content to the terminal/console with optional formatting

## Category
Communication

## Parameters

- **content** (string) (required): The content to print to the console
- **style** (string) (optional): Style of output - plain (default), header, info, success, warning, or error
- **newline** (boolean) (optional): Whether to add a newline after the content

## Usage Patterns

- Display results and status updates
- Show formatted output with styling
- Provide user feedback during operations
- Present analysis results and summaries

## Example Usage

```python
from eagle_lang.tools.base import tool_registry

# Get the tool
tool = tool_registry.get("print")

# Basic printing
result = tool.execute(content="Hello, World!")

# Styled output
result = tool.execute(content="Success!", style="success")

# Without newline
result = tool.execute(content="Loading... ", newline=False)
```

## Styling Options

- **plain**: Normal text output (default)
- **header**: Formatted as a section header with borders
- **info**: Prefixed with ℹ️ emoji
- **success**: Prefixed with ✅ emoji
- **warning**: Prefixed with ⚠️ emoji
- **error**: Prefixed with ❌ emoji

## Testing

Run the tests using:

```bash
python -m unittest print.tests
```