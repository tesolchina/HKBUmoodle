#!/usr/bin/env python3
"""
Moodle AI Processor - Main Entry Point

Two-stage processing system:
Stage 1: Manual file processing (HTML/Word documents)  
Stage 2: Automated API processing (direct Moodle integration)
"""

import click
import subprocess
import sys
from pathlib import Path
import json


@click.group()
def cli():
    """
    🎓 Moodle AI Processor
    
    Two-stage system for processing student work with AI:
    
    Stage 1: Manual file processing (HTML/Word documents)
    Stage 2: Automated API processing (direct Moodle integration)
    """
    pass


@click.group()
def stage1():
    """📁 Stage 1: Manual File Processing Commands"""
    pass


@click.group() 
def stage2():
    """🔗 Stage 2: Automated API Processing Commands"""
    pass


# Stage 1 Commands
@stage1.command()
def setup():
    """Setup Stage 1 directories"""
    subprocess.run([sys.executable, "stage1_manual/stage1.py", "setup"])


@stage1.command()
@click.option('--type', '-t', type=click.Choice(['feedback', 'summary', 'grading']), default='feedback')
@click.option('--file', '-f', help='Process specific file')
@click.option('--verbose', '-v', is_flag=True)
def process(type, file, verbose):
    """Process uploaded files with AI"""
    cmd = [sys.executable, "stage1_manual/stage1.py", "process", "--type", type]
    if file:
        cmd.extend(["--file", file])
    if verbose:
        cmd.append("--verbose")
    subprocess.run(cmd)


@stage1.command(name='list-files')
def list_files():
    """List files ready for processing"""
    subprocess.run([sys.executable, "stage1_manual/stage1.py", "list-files"])


@stage1.command(name='view-results')
@click.option('--results-file', '-f', help='Specific results file to view')
def view_results(results_file):
    """View processing results"""
    cmd = [sys.executable, "stage1_manual/stage1.py", "view-results"]
    if results_file:
        cmd.extend(["--results-file", results_file])
    subprocess.run(cmd)


# Stage 2 Commands
@stage2.command()
@click.option('--course-id', '-c', type=int, required=True)
@click.option('--forum-id', '-f', type=int)
@click.option('--auto-reply/--no-auto-reply', default=False)
@click.option('--limit', '-l', type=int, default=10)
@click.option('--output', '-o')
@click.option('--verbose', '-v', is_flag=True)
def process(course_id, forum_id, auto_reply, limit, output, verbose):
    """Process posts via Moodle API"""
    cmd = [sys.executable, "stage2_automated/automated_processor.py", "process", 
           "--course-id", str(course_id), "--limit", str(limit)]
    if forum_id:
        cmd.extend(["--forum-id", str(forum_id)])
    if auto_reply:
        cmd.append("--auto-reply")
    if output:
        cmd.extend(["--output", output])
    if verbose:
        cmd.append("--verbose")
    subprocess.run(cmd)


@stage2.command()
@click.option('--course-id', '-c', type=int, required=True)
def forums(course_id):
    """List forums in a course"""
    subprocess.run([sys.executable, "stage2_automated/automated_processor.py", "forums", 
                   "--course-id", str(course_id)])


@stage2.command()
@click.option('--course-id', '-c', type=int, required=True)
def info(course_id):
    """Get course information"""
    subprocess.run([sys.executable, "stage2_automated/automated_processor.py", "info", 
                   "--course-id", str(course_id)])


@stage2.command()
def test():
    """Test API connections"""
    subprocess.run([sys.executable, "stage2_automated/automated_processor.py", "test"])


@click.command()
def setup():
    """Initial project setup"""
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
    
    click.echo("\n📋 Two-Stage System:")
    click.echo("├── 📁 Stage 1: Manual File Processing")
    click.echo("│   ├── Upload HTML/Word files to stage1_manual/uploads/")
    click.echo("│   └── AI processes files locally")
    click.echo("└── 🔗 Stage 2: Automated API Processing")
    click.echo("    ├── Direct Moodle API integration")
    click.echo("    └── Automatic reading and posting")
    
    click.echo("\n💡 Quick Start:")
    click.echo("Stage 1: python main.py stage1 process --type feedback")
    click.echo("Stage 2: python main.py stage2 test")


@click.command()
def status():
    """Check system status"""
    click.echo("🔍 System Status")
    click.echo("=" * 20)
    
    # Check configuration
    config_path = Path("config/config.json")
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        api_key = config.get('openrouter', {}).get('api_key', '')
        if api_key and api_key.startswith('sk-'):
            click.echo("✅ OpenRouter API configured")
        else:
            click.echo("❌ OpenRouter API key missing")
            
        moodle_token = config.get('moodle', {}).get('token', '')
        if moodle_token and len(moodle_token) > 20:
            click.echo("✅ Moodle API configured")
        else:
            click.echo("❌ Moodle token missing")
    else:
        click.echo("❌ Configuration missing")
    
    # Check Stage 1 files
    upload_dir = Path("stage1_manual/uploads")
    if upload_dir.exists():
        files = list(upload_dir.glob("*"))
        click.echo(f"📁 Stage 1: {len(files)} files ready")
    else:
        click.echo("📁 Stage 1: No upload directory")
    
    # Check Stage 1 results
    processed_dir = Path("stage1_manual/processed")
    if processed_dir.exists():
        results = list(processed_dir.glob("*.json"))
        click.echo(f"📊 Stage 1: {len(results)} result files")
    else:
        click.echo("📊 Stage 1: No results yet")


# Add subcommands to main CLI
cli.add_command(stage1)
cli.add_command(stage2)
cli.add_command(setup)
cli.add_command(status)

if __name__ == '__main__':
    cli()
