#!/usr/bin/env python3
"""
Setup Script for Moodle AI Processor

This script helps set up the environment and configuration
"""

import json
import os
import sys
from pathlib import Path


def create_config():
    """Create configuration file with user input"""
    config_path = Path("config/config.json")
    template_path = Path("config/config.template.json")
    
    if config_path.exists():
        response = input("Configuration file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    # Load template
    with open(template_path, 'r') as f:
        config = json.load(f)
    
    print("\nMoodle AI Processor Setup")
    print("=" * 30)
    
    # Moodle configuration
    print("\n1. Moodle Configuration:")
    config['moodle']['base_url'] = input(f"Moodle base URL [{config['moodle']['base_url']}]: ").strip() or config['moodle']['base_url']
    config['moodle']['token'] = input(f"Moodle API token [{config['moodle']['token']}]: ").strip() or config['moodle']['token']
    config['moodle']['username'] = input(f"Username [{config['moodle']['username']}]: ").strip() or config['moodle']['username']
    
    # OpenRouter configuration
    print("\n2. OpenRouter AI Configuration:")
    print("   Get your API key from: https://openrouter.ai/keys")
    config['openrouter']['api_key'] = input("OpenRouter API key: ").strip() or config['openrouter']['api_key']
    
    # Model selection
    print("\n3. AI Model Selection:")
    models = [
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4",
        "openai/gpt-3.5-turbo",
        "meta-llama/llama-2-70b-chat",
        "google/gemma-7b-it"
    ]
    
    print("Available models:")
    for i, model in enumerate(models, 1):
        print(f"   {i}. {model}")
    
    choice = input(f"Select model (1-{len(models)}) [{models[0]}]: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(models):
        config['openrouter']['model'] = models[int(choice) - 1]
    
    # AI settings
    print("\n4. AI Settings:")
    temp_input = input(f"Temperature (0.0-1.0) [{config['ai_settings']['temperature']}]: ").strip()
    if temp_input:
        try:
            config['ai_settings']['temperature'] = float(temp_input)
        except ValueError:
            print("Invalid temperature, using default")
    
    tokens_input = input(f"Max tokens [{config['ai_settings']['max_tokens']}]: ").strip()
    if tokens_input:
        try:
            config['ai_settings']['max_tokens'] = int(tokens_input)
        except ValueError:
            print("Invalid token count, using default")
    
    # System prompt
    print(f"\nCurrent system prompt: {config['ai_settings']['system_prompt']}")
    new_prompt = input("New system prompt (press Enter to keep current): ").strip()
    if new_prompt:
        config['ai_settings']['system_prompt'] = new_prompt
    
    # Save configuration
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nConfiguration saved to {config_path}")
    print("Setup complete!")


def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import requests
        import click
        import openai
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False


def run_tests():
    """Run basic tests"""
    print("\nRunning basic tests...")
    
    # Test configuration loading
    try:
        with open("config/config.json", 'r') as f:
            config = json.load(f)
        print("✓ Configuration file loads correctly")
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False
    
    # Test imports
    try:
        sys.path.insert(0, 'src')
        from src.moodle_client import MoodleAPIClient
        from src.ai_client import OpenRouterClient
        from src.processor import MoodleAIProcessor
        print("✓ All modules import correctly")
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False
    
    return True


def main():
    """Main setup function"""
    print("Moodle AI Processor - Setup Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Create directories
    Path("config").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    print("✓ Created necessary directories")
    
    # Check dependencies
    if not check_dependencies():
        response = input("Install dependencies now? (y/N): ")
        if response.lower() == 'y':
            os.system("pip install -r requirements.txt")
        else:
            print("Please install dependencies manually and run setup again")
            sys.exit(1)
    
    # Create configuration
    create_config()
    
    # Run tests
    if run_tests():
        print("\n✓ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Test connection: python example.py")
        print("2. List forums: python main.py forums --course-id <YOUR_COURSE_ID>")
        print("3. Process posts: python main.py process --course-id <YOUR_COURSE_ID>")
    else:
        print("\n✗ Setup completed with errors. Please check the configuration.")


if __name__ == '__main__':
    main()
