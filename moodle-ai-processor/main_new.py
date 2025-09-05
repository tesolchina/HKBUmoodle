#!/usr/bin/env python3
"""
Moodle AI Processor - Main Entry Point

Two-stage processing system:
1. Manual file processing (HTML/Word documents)
2. Automated API processing (direct Moodle integration)
"""

import click
import sys
from pathlib import Path


@click.group()
def cli():
    """
    🎓 Moodle AI Processor
    
    A two-stage system for processing student work with AI:
    
    Stage 1: Manual file processing (HTML/Word documents)
    Stage 2: Automated API processing (direct Moodle integration)
    """
    pass


@click.command()
def stage1():
    """Launch Stage 1: Manual file processing"""
    import subprocess
    script_path = Path("stage1_manual/stage1.py")
    subprocess.run([sys.executable, str(script_path)] + sys.argv[2:])


@click.command()
def stage2():
    """Launch Stage 2: Automated API processing"""
    import subprocess
    script_path = Path("stage2_automated/automated_processor.py")
    subprocess.run([sys.executable, str(script_path)] + sys.argv[2:])


@click.command()
def setup():
    """Initial setup for both stages"""
    click.echo("🚀 Moodle AI Processor Setup")
    click.echo("=" * 40)
    
    # Create directories
    dirs_to_create = [
        "stage1_manual/uploads",
        "stage1_manual/processed", 
        "stage2_automated/results",
        "logs"
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        click.echo(f"✅ Created: {dir_path}")
    
    click.echo("\n📋 Project Structure:")
    click.echo("├── 📁 stage1_manual/")
    click.echo("│   ├── 📁 uploads/          # Place HTML/Word files here")
    click.echo("│   └── 📁 processed/        # AI processing results")
    click.echo("├── 📁 stage2_automated/")
    click.echo("│   └── 📁 results/          # API processing results")
    click.echo("└── 📁 logs/                 # Application logs")
    
    click.echo("\n🔧 Next Steps:")
    click.echo("1. Place your OpenRouter API key in config/APIkey.txt ✅")
    click.echo("2. For Stage 1: python main.py stage1 --help")
    click.echo("3. For Stage 2: python main.py stage2 --help")
    
    click.echo("\n📚 Usage Examples:")
    click.echo("Stage 1 (Manual files):")
    click.echo("  python main.py stage1 setup")
    click.echo("  python main.py stage1 process --type feedback")
    click.echo("")
    click.echo("Stage 2 (API automation):")
    click.echo("  python main.py stage2 test")
    click.echo("  python main.py stage2 process --course-id 99")


@click.command()
def status():
    """Check system status and configuration"""
    click.echo("🔍 System Status Check")
    click.echo("=" * 30)
    
    # Check config
    config_path = Path("config/config.json")
    if config_path.exists():
        click.echo("✅ Configuration file exists")
        
        import json
        with open(config_path) as f:
            config = json.load(f)
        
        # Check API key
        api_key = config.get('openrouter', {}).get('api_key', '')
        if api_key and api_key != 'your_openrouter_api_key_here':
            click.echo("✅ OpenRouter API key configured")
        else:
            click.echo("❌ OpenRouter API key not configured")
        
        # Check Moodle config
        moodle_token = config.get('moodle', {}).get('token', '')
        if moodle_token and moodle_token != 'your_moodle_token_here':
            click.echo("✅ Moodle API token configured")
        else:
            click.echo("❌ Moodle API token not configured")
    else:
        click.echo("❌ Configuration file not found")
    
    # Check directories
    directories = [
        "stage1_manual/uploads",
        "stage1_manual/processed",
        "stage2_automated",
        "logs"
    ]
    
    click.echo("\n📁 Directory Status:")
    for dir_path in directories:
        if Path(dir_path).exists():
            file_count = len(list(Path(dir_path).glob("*")))
            click.echo(f"   ✅ {dir_path} ({file_count} files)")
        else:
            click.echo(f"   ❌ {dir_path} (missing)")
    
    # Check Stage 1 uploads
    upload_dir = Path("stage1_manual/uploads")
    if upload_dir.exists():
        files = list(upload_dir.glob("*"))
        if files:
            click.echo(f"\n📄 Files ready for Stage 1 processing: {len(files)}")
            for file in files[:5]:  # Show first 5
                click.echo(f"   📄 {file.name}")
            if len(files) > 5:
                click.echo(f"   ... and {len(files) - 5} more")
        else:
            click.echo("\n📄 No files in uploads directory")
    
    click.echo(f"\n💡 Quick Actions:")
    click.echo("   Setup:        python main.py setup")
    click.echo("   Stage 1 help: python main.py stage1 --help")
    click.echo("   Stage 2 help: python main.py stage2 --help")


# Add commands to CLI
cli.add_command(stage1)
cli.add_command(stage2) 
cli.add_command(setup)
cli.add_command(status)


if __name__ == '__main__':
    cli()
