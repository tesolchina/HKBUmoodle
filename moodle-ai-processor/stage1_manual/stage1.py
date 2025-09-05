#!/usr/bin/env python3
"""
Stage 1 CLI: Manual File Processing

Process HTML and Word documents uploaded manually from Moodle
"""

import click
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from stage1_manual.file_processor import FileProcessor


@click.group()
def cli():
    """Stage 1: Manual File Processing for Moodle content"""
    pass


@click.command()
@click.option('--type', '-t', 
              type=click.Choice(['feedback', 'summary', 'grading']), 
              default='feedback',
              help='Type of AI processing to perform')
@click.option('--file', '-f', 
              help='Process specific file instead of entire upload directory')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose output')
def process(type, file, verbose):
    """
    Process uploaded files with AI
    
    Files should be placed in stage1_manual/uploads/
    Results will be saved to stage1_manual/processed/
    """
    try:
        processor = FileProcessor()
        
        if file:
            # Process single file
            if Path(file).is_absolute():
                file_path = Path(file)
            elif Path(f"uploads/{file}").exists():
                file_path = Path(f"uploads/{file}")
            elif Path(f"stage1_manual/uploads/{file}").exists():
                file_path = Path(f"stage1_manual/uploads/{file}")
            else:
                click.echo(f"Error: File not found: {file}")
                return
            
            click.echo(f"Processing file: {file_path.name}")
            result = processor.process_file(file_path, type)
            
            if verbose:
                click.echo("\nProcessing Result:")
                click.echo(json.dumps(result, indent=2, default=str))
            else:
                if 'error' in result:
                    click.echo(f"❌ Error: {result['error']}")
                else:
                    click.echo(f"✅ Successfully processed {file_path.name}")
                    if 'processed_posts' in result:
                        click.echo(f"   Found {len(result['processed_posts'])} posts")
        else:
            # Process entire upload directory
            click.echo(f"Processing all files in uploads/ directory with '{type}' analysis...")
            result = processor.process_upload_directory(type)
            
            click.echo(f"\n📊 Processing Summary:")
            click.echo(f"   Files processed: {result['total_files']}")
            
            success_count = len([r for r in result['results'] if 'error' not in r])
            error_count = result['total_files'] - success_count
            
            click.echo(f"   ✅ Successful: {success_count}")
            if error_count > 0:
                click.echo(f"   ❌ Errors: {error_count}")
            
            if verbose or error_count > 0:
                for r in result['results']:
                    status = "❌" if 'error' in r else "✅"
                    click.echo(f"   {status} {r['file_name']}")
                    if 'error' in r:
                        click.echo(f"      Error: {r['error']}")
            
            click.echo(f"\n📁 Results saved to: stage1_manual/processed/")
            click.echo(f"   Combined results: combined_{type}_results.json")
    
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


@click.command()
def list_files():
    """List files in the upload directory"""
    upload_dir = Path("uploads") if Path("uploads").exists() else Path("stage1_manual/uploads")
    
    if not upload_dir.exists():
        click.echo("Upload directory doesn't exist. Creating it now...")
        upload_dir.mkdir(parents=True)
        click.echo(f"Created: {upload_dir}")
        return
    
    files = list(upload_dir.iterdir())
    
    if not files:
        click.echo("No files found in uploads directory.")
        click.echo(f"Please add HTML or Word documents to: {upload_dir}")
        return
    
    click.echo(f"Files in {upload_dir}:")
    
    supported = ['.html', '.htm', '.docx', '.doc', '.txt', '.json']
    
    for file in sorted(files):
        if file.is_file():
            icon = "📄" if file.suffix.lower() in supported else "❓"
            size = file.stat().st_size
            size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
            click.echo(f"  {icon} {file.name} ({size_str})")


@click.command()
def setup():
    """Setup directories and show instructions"""
    upload_dir = Path("stage1_manual/uploads")
    processed_dir = Path("stage1_manual/processed")
    
    upload_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    click.echo("📁 Stage 1 directories created:")
    click.echo(f"   📥 Upload: {upload_dir}")
    click.echo(f"   📤 Processed: {processed_dir}")
    
    click.echo("\n📋 Instructions:")
    click.echo("1. Save Moodle forum pages as HTML files")
    click.echo("2. Download Word documents from Moodle assignments")
    click.echo("3. Place files in the uploads/ directory")
    click.echo("4. Run processing commands")
    
    click.echo("\n💡 Examples:")
    click.echo("   python stage1.py process --type feedback")
    click.echo("   python stage1.py process --type grading --file assignment.docx")
    click.echo("   python stage1.py list-files")


@click.command()
@click.option('--results-file', '-f', 
              help='Specific results file to view')
def view_results(results_file):
    """View processing results"""
    processed_dir = Path("stage1_manual/processed")
    
    if results_file:
        file_path = processed_dir / results_file
        if not file_path.exists():
            click.echo(f"Results file not found: {file_path}")
            return
        
        with open(file_path, 'r') as f:
            result = json.load(f)
        
        click.echo(f"📄 Results from: {results_file}")
        click.echo("=" * 50)
        
        if 'results' in result:  # Combined results
            for r in result['results']:
                click.echo(f"\n📁 {r['file_name']}")
                if 'processed_posts' in r:
                    for i, post in enumerate(r['processed_posts'], 1):
                        click.echo(f"   Post {i} by {post['original']['author']}:")
                        if 'ai_response' in post and 'feedback' in post['ai_response']:
                            click.echo(f"   💬 AI Feedback: {post['ai_response']['feedback'][:200]}...")
        else:  # Single file result
            if 'ai_response' in result:
                click.echo(f"🤖 AI Response: {result['ai_response']}")
    
    else:
        # List all results files
        results_files = list(processed_dir.glob("*.json"))
        
        if not results_files:
            click.echo("No results files found.")
            click.echo("Run 'python stage1.py process' first.")
            return
        
        click.echo("📊 Available results files:")
        for file in sorted(results_files):
            click.echo(f"   📄 {file.name}")
        
        click.echo(f"\nUse --results-file to view specific results")


# Add commands to CLI
cli.add_command(process)
cli.add_command(list_files, name='list-files')
cli.add_command(setup)
cli.add_command(view_results, name='view-results')


@click.command()
@click.option('--format', '-f',
              type=click.Choice(['markdown', 'forum-post', 'both']),
              default='both',
              help='Export format: markdown report, forum post, or both')
@click.option('--results-file', '-r',
              help='Specific results file to export (default: latest combined results)')
def export(format, results_file):
    """
    Export processed results in different formats for delivery to Moodle
    
    Available formats:
    - markdown: Detailed report with clearly divided sections
    - forum-post: Single consolidated post ready for Moodle forum
    - both: Generate both formats
    """
    try:
        processor = FileProcessor()
        processed_dir = Path("stage1_manual/processed")
        
        # Find results file to export
        if results_file:
            results_path = processed_dir / results_file
        else:
            # Find latest combined results file
            combined_files = list(processed_dir.glob("combined_*_results.json"))
            if not combined_files:
                click.echo("❌ No combined results files found. Run processing first.")
                return
            results_path = max(combined_files, key=lambda f: f.stat().st_mtime)
        
        if not results_path.exists():
            click.echo(f"❌ Results file not found: {results_path}")
            return
        
        # Load results data
        with open(results_path, 'r', encoding='utf-8') as f:
            results_data = json.load(f)
        
        click.echo(f"📊 Exporting from: {results_path.name}")
        click.echo(f"🔢 Total files: {results_data.get('total_files', 0)}")
        
        exported_files = []
        
        if format in ['markdown', 'both']:
            click.echo("\n📄 Generating markdown report...")
            markdown_file = processor.export_markdown_feedback(results_data)
            exported_files.append(markdown_file)
            click.echo(f"✅ Markdown report: {Path(markdown_file).name}")
        
        if format in ['forum-post', 'both']:
            click.echo("\n📤 Generating forum post...")
            forum_file = processor.export_consolidated_forum_post(results_data)
            exported_files.append(forum_file)
            click.echo(f"✅ Forum post: {Path(forum_file).name}")
        
        click.echo(f"\n🎉 Export complete! {len(exported_files)} files generated")
        click.echo(f"📁 Location: {processed_dir}")
        
        if format in ['forum-post', 'both']:
            click.echo("\n💡 Next steps:")
            click.echo("   1. Open the forum post HTML file")
            click.echo("   2. Copy the contents")
            click.echo("   3. Paste into your Moodle forum as a new post")
        
        if format in ['markdown', 'both']:
            click.echo("\n📋 Markdown report features:")
            click.echo("   • Complete feedback with expandable sections")
            click.echo("   • Individual student sections for separate delivery")  
            click.echo("   • Copy specific sections as needed")
    
    except Exception as e:
        click.echo(f"❌ Export failed: {e}")


# Add export command to CLI
cli.add_command(export)


if __name__ == '__main__':
    cli()
