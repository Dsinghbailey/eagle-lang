# Eagle - AI Programming Language

**Write software in plain English.**

Eagle is an AI programming language where you write instructions in natural language instead of code. Write `.caw` files with plain English, and Eagle's AI interprets and executes them using a comprehensive and customizable set of tools. Rather than generating code for you to run, Eagle directly executes your intent. Eagle can edit itself.

## What Makes Eagle Different

- **🗣️ Natural Language Programming**: Write instructions in plain English instead of learning syntax
- **🚀 Multi-Provider AI**: Works with OpenAI, Claude, Gemini, or OpenRouter
- **🔄 Self-Modifying Architecture**: Eagle can create tools for itself, modify its own configuration, and generate new behavior rules
- **⚙️ Zero-Config Tool Sharing**: Tools are self-contained folders that work across projects and teams
- **🔗 Workflow Composition**: Eagle understands how tools work together and suggests intelligent multi-step workflows
- **🔄 Recursive Intelligence**: Eagle can call itself to break down complex tasks, delegate subtasks, and coordinate multi-step solutions
- **💬 Interactive REPL**: Type commands directly in natural language for immediate execution and feedback
- **⚡ Smooth Setup**: Guided configuration with automatic .env creation and API key help

## Installation

```bash
pip install eagle-lang
```

## Quick Start

### Option 1: Interactive Mode (Recommended)

```bash
# Install and initialize
pip install eagle-lang
eagle init

# Start interactive mode
eagle
```

Then type commands directly:
```
eagle> create a python script that sorts a list of numbers
eagle> test it with the numbers [3, 1, 4, 1, 5, 9]
eagle> save the script as sort_demo.py
```

### Option 2: Script Files

1. **Initialize Eagle** in your project:
```bash
eagle init
```

2. **Create a `.caw` file** with your instructions:
```
# my_task.caw
Help me write 3 tweets about the launch of a new AI programming language called Eagle.
Focus on its ability to use plain English and be higher-level than Python.
```

3. **Run Eagle**:
```bash
eagle my_task.caw
```

Eagle will interpret your instructions and execute them using available tools.

## Configuration

### Interactive Setup

Run `eagle init` for guided setup, or use `eagle init -g` for global configuration.

### Manual Configuration

Eagle looks for configuration in this order:

1. Project: `.eagle/eagle_config.json`
2. User home: `~/.eagle/eagle_config.json`

Example configuration:

```json
{
  "provider": "openai",
  "model": "gpt-4o",
  "rules": ["eagle_rules.md"],
  "tools": {
    "allowed": ["print", "read", "search", "ask_permission"],
    "require_permission": [
      "write",
      "shell",
      "web",
      "git",
      "make_tool",
      "edit_config"
    ]
  },
  "max_tokens": 4000
}
```

> **🔄 Auto-Updates**: When you create tools with `make_tool`, Eagle automatically updates this config

### API Keys

Set your API key in `.eagle/.env`:

```
OPENAI_API_KEY=your-api-key-here
ANTHROPIC_API_KEY=your-claude-key-here
GOOGLE_API_KEY=your-gemini-key-here
OPENROUTER_API_KEY=your-openrouter-key-here
```

## Usage

### Basic Commands

```bash
# Interactive mode
eagle                         # Start interactive REPL

# Initialize configuration
eagle init                    # Project configuration
eagle init -g                 # Global configuration

# Run .caw files
eagle my_task.caw             # Simple syntax (recommended)
eagle run my_task.caw         # Explicit syntax
eagle task.caw --provider claude --model claude-3-sonnet
eagle task.caw --rules custom_rules.md

# Explore capabilities
eagle capabilities            # Show current workflows and tools
eagle capabilities --detailed # Show technical tool information
```

### Interactive Mode

Eagle includes a powerful REPL (Read-Eval-Print Loop) for immediate interaction:

```bash
$ eagle
🦅 Eagle Interactive Mode
Type your instructions in plain English and press Enter.
Commands: .exit (quit), .help (show help), .config (show config)
============================================================
Ready! Using openai:gpt-4o

eagle> create a simple hello world python script
--- Eagle is thinking... ---
[Eagle creates the script using available tools]

eagle> run the script
--- Eagle is thinking... ---
[Eagle executes the script and shows output]

eagle> .exit
Goodbye! 🦅
```

**Interactive Commands:**
- `.exit` / `.quit` - Exit Eagle
- `.help` - Show available commands
- `.config` - Show current configuration  
- `.capabilities` - Show available tools and workflows

### Command Options

- `--provider`: AI provider (openai, claude, gemini, openrouter)
- `--model`: Specific model to use
- `--rules`: Custom rules files (space-separated)

## Built-in Tools

Eagle comes with a comprehensive toolkit for software development:

### File Operations

- **`write`**: Create/modify files with intelligent directory creation
- **`read`**: Read files with line ranges and multi-file support
- **`search`**: Search files by name patterns or content with regex

### System Operations

- **`shell`**: Execute shell commands with safety guardrails
- **`git`**: Full git workflow (status, commit, push, branch management)

### Communication & I/O

- **`print`**: Styled terminal output with formatting options
- **`ask_permission`**: Interactive user input and confirmations
- **`web`**: HTTP requests, API calls, and web scraping

### Meta-Programming Tools

- **`make_tool`**: Describe a tool in English, Eagle generates the code automatically
- **`make_rule`**: Generate custom behavior rules for Eagle
- **`edit_config`**: Modify Eagle configuration programmatically
- **`call_eagle`**: Recursive Eagle calls for complex task delegation

> **Tip**: Use `eagle capabilities` to see what's possible with your current setup

## Examples

### File Management

```
# organize.caw
Look through all the Python files in this directory and organize them by creating
subdirectories based on their purpose (models, views, utilities, etc.).
Move the files to appropriate directories and create an index.md file
explaining the new structure.
```

### Development Workflow

```
# deploy.caw
Check the git status, run the tests, and if they pass, commit all changes
with an appropriate message and push to the main branch. If tests fail,
show me what failed and ask for permission before proceeding.
```

### Data Analysis

```
# analyze.caw
Read the sales_data.csv file, analyze the trends, and create a summary report
in markdown format. Include charts if possible and save the report as
sales_analysis.md.
```

### Web Research

```
# research.caw
Research the latest developments in AI coding assistants by checking
relevant websites and summarize the key findings. Focus on new features
and capabilities announced in 2024.
```

### Meta-Programming

```
# extend_eagle.caw
I need a tool that can automatically optimize images - compress them,
resize them, and convert formats. It should work with JPG, PNG, and WebP files.
Create this tool and then use it to optimize all images in my /assets folder.
```

Eagle will:

1. Generate a complete `image_optimizer` tool with AI
2. Add it to your Eagle configuration automatically
3. Use the new tool to optimize your images
4. Complete the entire workflow automatically

## Custom Tools

### Option 1: AI-Generated Tools (Recommended)

Let Eagle write the tool for you:

```
# In any .caw file
Create a "weather" tool that fetches weather data for any city using a weather API.
It should take a city name and return current temperature, conditions, and forecast.
```

Eagle generates:

```
.eagle/tools/weather/
├── __init__.py     (full implementation)
├── tests.py        (unit tests)
└── README.md       (documentation)
```

### Option 2: Manual Tool Development

For advanced users who want full control:

```python
# .eagle/tools/my_tool/__init__.py
from eagle_lang.tools.base import EagleTool

class MyCustomTool(EagleTool):
    @property
    def name(self) -> str:
        return "my_tool"

    @property
    def description(self) -> str:
        return "Description of what my tool does"

    @property
    def usage_patterns(self) -> dict:
        return {
            "category": "custom",
            "patterns": ["Pattern 1", "Pattern 2"],
            "workflows": {"My Workflow": ["my_tool", "print"]}
        }

    def execute(self, input: str) -> str:
        return f"Processed: {input}"
```

> **💡 Note**: Tools automatically update Eagle's capabilities and workflows. No restart needed!

## Permission System

Tools are categorized by permission level:

- **Allowed**: Execute without prompts (`print`, `read`, `search`, `call_eagle`)
- **Require Permission**: Prompt user before execution (`write`, `shell`, `web`, `git`, `ask_permission`)

When a restricted tool is called, Eagle will show:

```
🔐 Permission Required
Tool: write
Arguments: {"file_path": "output.txt", "content": "Hello World"}
Allow this tool execution? (y/n/details):
```

## Security & Sandboxing

Eagle includes built-in security measures:

- **File Operations**: Restricted to current directory and subdirectories
- **Shell Commands**: Blocks dangerous operations (rm -rf /, shutdown, etc.)
- **Web Requests**: Blocks localhost and private networks
- **Git Operations**: Prevents force pushes and hard resets

## License

MIT License - see LICENSE file for details.

## Roadmap

Building the Eagle ecosystem:

### ✅ Core Platform
- Interactive REPL and .caw file execution
- Self-modifying architecture with AI-generated tools
- Multi-provider AI support and project-aware configuration

### 🚧 Next Steps
- **Eagle Website** - Official documentation and community hub
- **Downloadable Releases** - Standalone installers for all platforms
- **Package Manager** - `eagle install <tool/config/rule>` for sharing components
- **VS Code Extension** - Syntax highlighting and Eagle integration
- **Community Registry** - Discover and share tools, configs, and rules

### 💭 Future
- Cloud execution and team collaboration features
- Advanced debugging and workflow visualization
- Integration with popular development tools

## Contributing

Eagle is in active development. Contributions, feedback, and bug reports are welcome!

## The Vision

Eagle represents a new approach to programming where natural language becomes the primary interface for software development. Instead of learning syntax and frameworks, you describe what you want to accomplish.

**Eagle enables:**

- **Faster iteration** - Express ideas directly without translation to code syntax
- **Lower barriers** - Programming accessible to anyone who can clearly explain a problem
- **Direct execution** - Your intent becomes reality without intermediate code generation
- **True AI collaboration** - Not autocomplete or suggestions, but AI that understands and acts

This is a step toward a future where the gap between human intent and computer execution continues to shrink.

---

**Get started in 30 seconds:**

```bash
pip install eagle-lang && eagle init && eagle
```

Then just start typing what you want to build.
