# Read Tool

Read contents of one or more files, with optional line range support

## Category
File Operations

## Parameters

- **file_path** (string) (required): Path to the file to read (or comma-separated paths for multiple files)
- **start_line** (integer) (optional): Starting line number (1-based, optional)
- **end_line** (integer) (optional): Ending line number (1-based, optional)
- **max_lines** (integer) (optional): Maximum number of lines to read (default: 1000)
- **encoding** (string) (optional): File encoding (default: utf-8)

## Usage Patterns

- Read and analyze existing files
- Load configuration or data files
- Examine source code before modifications
- Read multiple files for comparison or compilation

## Example Usage

```python
from eagle_lang.tools.base import tool_registry

# Get the tool
tool = tool_registry.get("read")

# Basic file reading
result = tool.execute(file_path="config.json")

# Read specific line range
result = tool.execute(file_path="large_file.txt", start_line=10, end_line=50)

# Read multiple files
result = tool.execute(file_path="file1.txt,file2.txt,file3.txt")

# Limit output lines
result = tool.execute(file_path="big_file.log", max_lines=100)
```

## Security Features

- **Sandboxing**: Can only read files from current directory or subdirectories
- **Size limits**: Maximum 5000 lines per file to prevent memory issues
- **Encoding safety**: Handles encoding errors gracefully

## Testing

Run the tests using:

```bash
python -m unittest read.tests
```