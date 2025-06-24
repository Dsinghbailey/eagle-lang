"""Eagle initialization and setup functionality."""

import os
import shutil
import json
import time
from .config import get_default_config, save_config
from .interpreter import EagleInterpreter
from .providers import PROVIDERS, get_provider_models, get_provider_api_key_env


def eagle_init(global_install: bool = False):
    """
    Interactive setup for Eagle config including provider, model, and API key configuration.
    
    Args:
        global_install: If True, install config in user home directory. If False, install in current directory.
    """
    print("\n🦅 Welcome to Eagle Setup! 🦅")
    
    # Check for existing .eagle directory
    project_eagle_dir = os.path.join(os.getcwd(), ".eagle")
    user_eagle_dir = os.path.expanduser("~/.eagle")
    
    existing_config = None
    if not global_install and os.path.exists(project_eagle_dir):
        print(f"📁 Found existing .eagle directory: {project_eagle_dir}")
        action = input("What would you like to do? (fresh/cancel): ").strip().lower()
        if action == "cancel":
            print("Setup cancelled.")
            return
        elif action == "fresh":
            import shutil
            backup_dir = f"{project_eagle_dir}_backup_{int(time.time())}"
            shutil.move(project_eagle_dir, backup_dir)
            print(f"📦 Backed up existing config to: {backup_dir}")
            print("🆕 Starting fresh installation")
        else:
            print("Invalid option. Use 'eagle update-tools' to update tools only.")
            return
    elif global_install and os.path.exists(user_eagle_dir):
        print(f"📁 Found existing global .eagle directory: {user_eagle_dir}")
        action = input("What would you like to do? (fresh/cancel): ").strip().lower()
        if action == "cancel":
            print("Setup cancelled.")
            return
        elif action == "fresh":
            import shutil
            backup_dir = f"{user_eagle_dir}_backup_{int(time.time())}"
            shutil.move(user_eagle_dir, backup_dir)
            print(f"📦 Backed up existing config to: {backup_dir}")
            print("🆕 Starting fresh installation")
        else:
            print("Invalid option. Use 'eagle update-tools' to update tools only.")
            return
    
    print("Let's configure your AI assistant...\n")
    
    # Load default config for fallback values
    fallback_config = get_default_config()
    
    # Use existing config as defaults if available
    current_provider = existing_config.get("provider") if existing_config else fallback_config["provider"]
    current_model = existing_config.get("model") if existing_config else fallback_config["model"]
    current_rules = existing_config.get("rules") if existing_config else fallback_config["rules"]
    current_tools = existing_config.get("tools") if existing_config else fallback_config["tools"]
    
    # Step 1: Choose Provider
    print("Step 1: Choose your AI provider")
    print("Available providers:")
    for i, (provider_id, provider_config) in enumerate(PROVIDERS.items(), 1):
        models_preview = ", ".join(provider_config["models"][:3])
        if len(provider_config["models"]) > 3:
            models_preview += "..."
        current_marker = " (current)" if provider_id == current_provider else ""
        print(f"  {i}. {provider_config['name']} ({models_preview}){current_marker}")
    
    provider_input = input(f"\nEnter your choice (1-{len(PROVIDERS)}) or provider name (current: {current_provider}): ").strip()
    
    # Use current provider if input is empty
    if not provider_input:
        default_provider = current_provider
    else:
        # Build provider map dynamically
        provider_map = {}
        for i, provider_id in enumerate(PROVIDERS.keys(), 1):
            provider_map[str(i)] = provider_id
            provider_map[provider_id] = provider_id
            # Add alternative names
            if provider_id == "claude":
                provider_map["anthropic"] = provider_id
            elif provider_id == "gemini":
                provider_map["google"] = provider_id
        
        default_provider = provider_map.get(provider_input.lower(), current_provider)
    
    print(f"Selected provider: {default_provider}")
    
    # Step 2: Configure API Key
    print(f"\nStep 2: Configure API key for {default_provider}")
    api_key_env = get_provider_api_key_env(default_provider)
    
    current_key = os.getenv(api_key_env)
    if current_key:
        print(f"✅ {api_key_env} is already set")
        update_key = input("Do you want to update it? (y/N): ").strip().lower()
        if update_key not in ['y', 'yes']:
            print("Keeping existing API key")
        else:
            current_key = None
    
    if not current_key:
        print(f"Please set your {api_key_env}")
        print("You can:")
        print(f"  1. Set environment variable: export {api_key_env}='your-key'")
        print(f"  2. Add to .env file: {api_key_env}=your-key")
        
        set_now = input("Do you want to set it now? (y/N): ").strip().lower()
        if set_now in ['y', 'yes']:
            api_key = input(f"Enter your {default_provider} API key: ").strip()
            if api_key:
                # Store API key for later use in .eagle folder
                api_key_for_env = api_key
                
                # Set for current session
                os.environ[api_key_env] = api_key
            else:
                print("⚠️  No API key entered. You'll need to set it manually later.")
    
    # Step 3: Choose Model
    print(f"\nStep 3: Choose model for {default_provider}")
    available_models = get_provider_models(default_provider)
    print("Available models:")
    for i, model in enumerate(available_models, 1):
        current_marker = " (current)" if model == current_model else ""
        print(f"  {i}. {model}{current_marker}")
    
    model_input = input(f"\nEnter choice (1-{len(available_models)}) or model name (current: {current_model}): ").strip()
    
    try:
        if model_choice.isdigit():
            model_idx = int(model_choice) - 1
            if 0 <= model_idx < len(available_models):
                default_model = available_models[model_idx]
            else:
                default_model = available_models[0]
        else:
            # Check if it's a valid model name
            if model_choice in available_models:
                default_model = model_choice
            else:
                default_model = available_models[0]
    except:
        default_model = available_models[0]
    
    print(f"Selected model: {default_model}")
    
    # Step 4: Additional Options
    print(f"\nStep 4: Additional options")
    
    # Rules
    rules_input = input("Rules files (comma-separated, or Enter for default): ").strip()
    if rules_input:
        rules_list = [r.strip() for r in rules_input.split(",") if r.strip()]
    else:
        rules_list = fallback_config["rules"]
    
    # Tools
    tools_input = input("Tools to enable (comma-separated, or Enter for default): ").strip()
    if tools_input:
        tools_list = [t.strip() for t in tools_input.split(",") if t.strip()]
    else:
        tools_list = fallback_config["tools"]
    
    # Step 5: Save Configuration
    print(f"\nStep 5: Save configuration")
    
    # Determine where to save
    if global_install:
        to_project = False
        print("Installing globally (to home directory)")
    else:
        save_scope = input("Save config for this project only, or for all projects? (project/global): ").strip().lower()
        to_project = save_scope != "global"
    
    # Create config
    config = {
        "provider": default_provider,
        "model": default_model,
        "rules": rules_list,
        "tools": tools_list
    }
    
    # Save config file
    save_config(config, to_project=to_project)
    
    # Copy default files to .eagle folder
    default_config_dir = os.path.join(os.path.dirname(__file__), "default_config")
    default_rules_path = os.path.join(default_config_dir, "eagle_rules.md")
    default_tools_dir = os.path.join(default_config_dir, "tools")
    
    # Determine target directory
    if to_project:
        target_dir = os.path.join(os.getcwd(), ".eagle")
    else:
        target_dir = os.path.expanduser("~/.eagle")
    
    # Create .eagle directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    target_rules_path = os.path.join(target_dir, "eagle_rules.md")
    target_env_path = os.path.join(target_dir, ".env")
    target_tools_dir = os.path.join(target_dir, "tools")
    
    # Copy rules file if it doesn't exist
    if os.path.exists(default_rules_path) and not os.path.exists(target_rules_path):
        try:
            shutil.copy2(default_rules_path, target_rules_path)
            print(f"📋 Copied default rules to: {target_rules_path}")
        except Exception as e:
            print(f"⚠️  Could not copy rules file: {e}")
    elif os.path.exists(target_rules_path):
        print(f"📋 Rules file already exists: {target_rules_path}")
    
    # Copy tools directory if it doesn't exist
    if os.path.exists(default_tools_dir) and not os.path.exists(target_tools_dir):
        try:
            shutil.copytree(default_tools_dir, target_tools_dir)
            print(f"🔧 Copied default tools to: {target_tools_dir}")
        except Exception as e:
            print(f"⚠️  Could not copy tools directory: {e}")
    elif os.path.exists(target_tools_dir):
        print(f"🔧 Tools directory already exists: {target_tools_dir}")
    
    # Create or update .env file in .eagle folder
    if 'api_key_for_env' in locals() and api_key_for_env:
        env_content = ""
        if os.path.exists(target_env_path):
            with open(target_env_path, "r") as f:
                env_content = f.read()
        
        # Check if key already exists in .env
        if f"{api_key_env}=" in env_content:
            # Update existing key
            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith(f"{api_key_env}="):
                    lines[i] = f"{api_key_env}={api_key_for_env}"
                    break
            env_content = '\n'.join(lines)
        else:
            # Add new key
            if env_content and not env_content.endswith('\n'):
                env_content += '\n'
            env_content += f"{api_key_env}={api_key_for_env}\n"
        
        with open(target_env_path, "w") as f:
            f.write(env_content)
        print(f"✅ API key saved to {target_env_path}")
    
    print("\n🎉 Eagle configuration complete!")
    print(f"Provider: {default_provider}")
    print(f"Model: {default_model}")
    print(f"Rules: {', '.join(rules_list) if rules_list else 'None'}")
    print(f"Tools: {', '.join(tools_list) if tools_list else 'None'}")
    print(f"Config saved: {'Project' if to_project else 'Global'}")
    print("\nYou can now run: eagle run your_file.caw\n")


def update_tools():
    """Update default tools while preserving custom tools."""
    print("\n🔧 Eagle Tools Update")
    
    # Find .eagle directories
    project_eagle_dir = os.path.join(os.getcwd(), ".eagle")
    user_eagle_dir = os.path.expanduser("~/.eagle")
    
    # Determine which directory to update
    target_dirs = []
    if os.path.exists(project_eagle_dir):
        target_dirs.append(("Project", project_eagle_dir))
    if os.path.exists(user_eagle_dir):
        target_dirs.append(("Global", user_eagle_dir))
    
    if not target_dirs:
        print("❌ No .eagle directories found. Run 'eagle init' first.")
        return
    
    print("Found Eagle installations:")
    for i, (scope, path) in enumerate(target_dirs, 1):
        print(f"  {i}. {scope}: {path}")
    
    if len(target_dirs) == 1:
        selected_dir = target_dirs[0][1]
        scope = target_dirs[0][0]
        print(f"Updating {scope.lower()} tools...")
    else:
        choice = input(f"\nSelect installation to update (1-{len(target_dirs)}) or 'all': ").strip().lower()
        if choice == "all":
            selected_dirs = [path for _, path in target_dirs]
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(target_dirs):
                    selected_dirs = [target_dirs[idx][1]]
                    scope = target_dirs[idx][0]
                else:
                    print("❌ Invalid selection")
                    return
            except ValueError:
                print("❌ Invalid selection")
                return
        
        if choice != "all":
            selected_dir = selected_dirs[0]
            print(f"Updating {scope.lower()} tools...")
        else:
            print("Updating all Eagle installations...")
    
    # Get default tools directory
    default_tools_dir = os.path.join(os.path.dirname(__file__), "default_config", "tools")
    if not os.path.exists(default_tools_dir):
        print("❌ Default tools directory not found")
        return
    
    # Update tools for selected directories
    dirs_to_update = selected_dirs if 'selected_dirs' in locals() else [selected_dir]
    
    for target_dir in dirs_to_update:
        target_tools_dir = os.path.join(target_dir, "tools")
        
        if not os.path.exists(target_tools_dir):
            print(f"⚠️  No tools directory found in {target_dir}")
            continue
        
        # Get list of default tool names
        default_tool_names = set()
        if os.path.exists(default_tools_dir):
            default_tool_names = {item for item in os.listdir(default_tools_dir) 
                                 if os.path.isdir(os.path.join(default_tools_dir, item))}
        
        # Update only default tools, preserve custom ones
        updated_count = 0
        for tool_name in default_tool_names:
            default_tool_path = os.path.join(default_tools_dir, tool_name)
            target_tool_path = os.path.join(target_tools_dir, tool_name)
            
            try:
                if os.path.exists(target_tool_path):
                    shutil.rmtree(target_tool_path)
                shutil.copytree(default_tool_path, target_tool_path)
                updated_count += 1
            except Exception as e:
                print(f"⚠️  Could not update {tool_name}: {e}")
        
        print(f"✅ Updated {updated_count} default tools in {target_dir}")
    
    print("\n🎉 Tools update complete!")
    print("Updated tools will be available on next Eagle run.")