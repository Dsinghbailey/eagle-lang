# Write Tool

Create or write content to a file

## Category
File Operations

## Parameters

- **content** (string) (required): The content to write to the file
- **file_path** (string) (required): Path to the file to write to
- **mode** (string) (optional): File write mode - 'write' (default) overwrites file, 'append' adds to existing file

## Usage Patterns

- Create new files with generated content
- Save analysis results to files
- Generate code files and documentation
- Append to log files or ongoing documents

## Example Usage

```python
from eagle_lang.tools.base import tool_registry

# Get the tool
tool = tool_registry.get("write")

# Write new file
result = tool.execute(content="Hello, World!", file_path="greeting.txt")

# Append to existing file
result = tool.execute(content="\nNew line", file_path="log.txt", mode="append")
```

## Security Features

- **Sandboxing**: Can only write to current directory or subdirectories
- **Auto-directory creation**: Creates parent directories if they don't exist
- **Safe file handling**: Proper error handling for permission issues

## Testing

Run the tests using:

```bash
python -m unittest write.tests
```