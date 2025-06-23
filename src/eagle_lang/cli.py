# src/eagle_lang/cli.py
import argparse
import os
import sys
from dotenv import load_dotenv

from .tools.base import tool_registry
from .config import load_config
from .interpreter import EagleInterpreter
from .init import eagle_init

# Load environment variables from .env files in .eagle folders
load_dotenv(os.path.join(os.getcwd(), ".eagle", ".env"))
load_dotenv(os.path.expanduser("~/.eagle/.env"))


# Initialize tools
def _initialize_tools():
    """Initialize and register all available tools."""
    # Load built-in tools from default-config/tools
    default_tools_dir = os.path.join(os.path.dirname(__file__), "default-config", "tools")
    tool_registry.load_tools_from_directory(default_tools_dir)
    
    # Load custom tools from .eagle/tools/ folders
    project_tools_dir = os.path.join(os.getcwd(), ".eagle", "tools")
    user_tools_dir = os.path.expanduser("~/.eagle/tools")
    
    # Load project-specific tools (can override defaults)
    tool_registry.load_tools_from_directory(project_tools_dir)
    
    # Load user-global tools (can override project and defaults)
    tool_registry.load_tools_from_directory(user_tools_dir)


_initialize_tools()


def start_interactive_mode():
    """Start Eagle's interactive REPL mode."""
    print("🦅 Eagle Interactive Mode")
    print("Type your instructions in plain English and press Enter.")
    print("Commands: .exit (quit), .help (show help), .config (show config)")
    print("=" * 60)
    
    try:
        # Load configuration
        config = load_config()
        provider = config.get("provider")
        model = config.get("model")
        rules = config.get("rules")
        
        # Initialize interpreter
        interpreter = EagleInterpreter(
            provider=provider, model_name=model, rules=rules, config=config
        )
        
        print(f"Ready! Using {provider}:{model}")
        print()
        
        while True:
            try:
                # Get user input
                user_input = input("eagle> ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input == ".exit" or user_input == ".quit":
                    print("Goodbye! 🦅")
                    break
                elif user_input == ".help":
                    print("Available commands:")
                    print("  .exit/.quit  - Exit Eagle")
                    print("  .help        - Show this help")
                    print("  .config      - Show current configuration")
                    print("  .capabilities - Show available tools and workflows")
                    print("  Or just type any instruction in plain English!")
                    continue
                elif user_input == ".config":
                    print(f"Provider: {provider}")
                    print(f"Model: {model}")
                    print(f"Rules: {rules}")
                    tools_config = config.get("tools", {})
                    if isinstance(tools_config, dict):
                        allowed = tools_config.get("allowed", [])
                        permission = tools_config.get("require_permission", [])
                        print(f"Allowed tools: {', '.join(allowed) if allowed else 'None'}")
                        print(f"Permission tools: {', '.join(permission) if permission else 'None'}")
                    continue
                elif user_input == ".capabilities":
                    tools_config = config.get("tools", {})
                    if isinstance(tools_config, dict):
                        allowed_tools = tools_config.get("allowed", [])
                        permission_tools = tools_config.get("require_permission", [])
                        available_tools = allowed_tools + permission_tools
                    else:
                        available_tools = tools_config if tools_config else []
                    
                    # Filter to only tools that actually exist
                    available_tools = [tool for tool in available_tools if tool in tool_registry.list_tools()]
                    summary = tool_registry.get_user_capabilities_summary(available_tools)
                    print(summary)
                    continue
                
                # Execute the instruction
                print("\n--- Eagle is thinking... ---")
                try:
                    response = interpreter._get_llm_response(user_input)
                    print(f"\n{response}")
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                
                print()  # Add spacing
                
            except KeyboardInterrupt:
                print("\n\nUse .exit to quit Eagle")
                continue
            except EOFError:
                print("\nGoodbye! 🦅")
                break
                
    except Exception as e:
        print(f"❌ Failed to start interactive mode: {e}")
        print("Try running 'eagle init' to set up your configuration.")


def main():
    """
    Entry point for the eagle command-line tool.
    """
    parser = argparse.ArgumentParser(
        prog="eagle",  # Set the program name for help messages
        description="Eagle: An Agentic Language Platform operating at a higher level than Python.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Eagle subcommands")

    # Default/run command (no subcommand)
    parser_run = subparsers.add_parser("run", help="Run a .caw file (default)")
    parser_run.add_argument(
        "caw_file",
        help="Path to the .caw file containing plain English instructions for Eagle.",
    )
    parser_run.add_argument(
        "--model",
        default=None,
        help="Specify the LLM model to use (overrides config/default).",
    )
    parser_run.add_argument(
        "--provider",
        default=None,
        choices=["openai", "claude", "gemini", "openrouter"],
        help="Specify the AI provider to use (openai, claude, gemini, openrouter).",
    )
    parser_run.add_argument(
        "--rules",
        nargs="+",
        default=None,
        help="Specify the rules files to use (space-separated list).",
    )

    # Init subcommand
    parser_init = subparsers.add_parser("init", help="Interactive Eagle configuration setup")
    parser_init.add_argument(
        "-g", "--global",
        action="store_true",
        dest="global_install",
        help="Install configuration globally in home directory instead of current directory"
    )
    
    # Capabilities subcommand
    parser_capabilities = subparsers.add_parser("capabilities", help="Show current Eagle capabilities and workflows")
    parser_capabilities.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed information including potential workflows"
    )

    # Handle no arguments - start interactive mode
    if len(sys.argv) == 1:
        start_interactive_mode()
        return

    # If no subcommand, treat as run (for backward compatibility)
    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "init", "capabilities"):
        # Check if first arg is a .caw file or other run argument
        # Insert 'run' as the default subcommand
        sys.argv.insert(1, "run")

    args = parser.parse_args()

    if args.command == "init":
        eagle_init(global_install=getattr(args, 'global_install', False))
        return
    
    if args.command == "capabilities":
        # Load config to get available tools
        try:
            config = load_config()
            tools_config = config.get("tools", {})
            
            if isinstance(tools_config, dict):
                allowed_tools = tools_config.get("allowed", [])
                permission_tools = tools_config.get("require_permission", [])
                available_tools = allowed_tools + permission_tools
            else:
                available_tools = tools_config if tools_config else []
            
            # Filter to only tools that actually exist
            available_tools = [tool for tool in available_tools if tool in tool_registry.list_tools()]
            
            # Show capabilities
            summary = tool_registry.get_user_capabilities_summary(available_tools)
            print(summary)
            
            if getattr(args, 'detailed', False):
                print("\n" + "="*50)
                print("DETAILED TOOL INFORMATION")
                print("="*50)
                detailed_info = tool_registry.get_tool_patterns(available_tools)
                print(detailed_info)
                
        except SystemExit:
            print("❌ No Eagle configuration found. Run 'eagle init' first.")
        return

    # Load config for run
    config = load_config()
    provider = args.provider or config.get("provider")
    model = args.model or config.get("model")
    rules = args.rules or config.get("rules")

    interpreter = EagleInterpreter(
        provider=provider, model_name=model, rules=rules, config=config
    )
    interpreter.execute_caw_file(args.caw_file)


if __name__ == "__main__":
    main()
