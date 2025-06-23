"""Eagle initialization and setup functionality."""

import os
import shutil
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
    print("Let's configure your AI assistant...\n")
    
    # Load default config for fallback values
    fallback_config = get_default_config()
    
    # Step 1: Choose Provider
    print("Step 1: Choose your AI provider")
    print("Available providers:")
    for i, (provider_id, provider_config) in enumerate(PROVIDERS.items(), 1):
        models_preview = ", ".join(provider_config["models"][:3])
        if len(provider_config["models"]) > 3:
            models_preview += "..."
        print(f"  {i}. {provider_config['name']} ({models_preview})")
    
    provider_choice = input(f"\nEnter your choice (1-{len(PROVIDERS)}) or provider name: ").strip().lower()
    
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
    
    default_provider = provider_map.get(provider_choice, fallback_config["provider"])
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
        print(f"  {i}. {model}")
    
    model_choice = input(f"\nEnter choice (1-{len(available_models)}) or model name: ").strip()
    
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
    
    # Step 4: Test Configuration
    print(f"\nStep 4: Test configuration")
    test_config = input("Do you want to test the configuration? (Y/n): ").strip().lower()
    
    if test_config not in ['n', 'no']:
        try:
            print("Testing connection...")
            test_interpreter = EagleInterpreter(
                provider=default_provider,
                model_name=default_model,
                config=fallback_config
            )
            print("✅ Configuration test successful!")
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            print("Please check your API key and try again.")
    
    # Step 5: Additional Options
    print(f"\nStep 5: Additional options")
    
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
    
    # Step 6: Save Configuration
    print(f"\nStep 6: Save configuration")
    
    # Determine where to save
    if global_install:
        to_project = False
        print("Installing globally (to home directory)")
    else:
        save_scope = input("Save config for this project only, or for all projects? (project/all): ").strip().lower()
        to_project = save_scope != "all"
    
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
    default_config_dir = os.path.join(os.path.dirname(__file__), "default-config")
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