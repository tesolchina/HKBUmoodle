"""
Main Entry Point

Command-line interface for the Moodle AI Processor
"""

import click
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.processor import MoodleAIProcessor


@click.command()
@click.option('--course-id', '-c', type=int, required=True, 
              help='Moodle course ID')
@click.option('--forum-id', '-f', type=int, 
              help='Specific forum ID (optional)')
@click.option('--auto-reply/--no-auto-reply', default=False,
              help='Automatically reply to posts with AI responses')
@click.option('--limit', '-l', type=int, default=10,
              help='Maximum number of posts to process')
@click.option('--config', '-cfg', default='config/config.json',
              help='Path to configuration file')
@click.option('--output', '-o', 
              help='Output file for results (JSON format)')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose logging')
def main(course_id, forum_id, auto_reply, limit, config, output, verbose):
    """
    Process students' posts in Moodle using AI
    
    This tool reads students' posts from Moodle forums, processes them
    with AI to generate feedback and replies, and optionally posts
    the replies back to Moodle.
    """
    try:
        # Initialize processor
        processor = MoodleAIProcessor(config)
        
        click.echo(f"Processing posts from course {course_id}")
        if forum_id:
            click.echo(f"Targeting specific forum: {forum_id}")
        if auto_reply:
            click.echo("Auto-reply is ENABLED - AI responses will be posted to Moodle")
        else:
            click.echo("Auto-reply is DISABLED - results will only be displayed/saved")
        
        # Process posts
        results = processor.process_forum_posts(
            course_id=course_id,
            forum_id=forum_id,
            auto_reply=auto_reply,
            limit=limit
        )
        
        # Display results
        if results:
            click.echo(f"\nProcessed {len(results)} posts:")
            for i, result in enumerate(results, 1):
                if 'error' in result:
                    click.echo(f"{i}. Post {result.get('post_id')} - ERROR: {result['error']}")
                else:
                    status = "✓ Replied" if result.get('auto_replied') else "✓ Analyzed"
                    click.echo(f"{i}. {result['post_subject']} - {status}")
                    
                    if verbose:
                        click.echo(f"   Original: {result['original_content'][:100]}...")
                        click.echo(f"   AI Reply: {result['ai_reply'][:100]}...")
                        click.echo()
        else:
            click.echo("No posts found to process.")
        
        # Save results to file if specified
        if output:
            with open(output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            click.echo(f"\nResults saved to {output}")
        
        # Generate and display summary
        summary = processor.generate_summary_report(results)
        click.echo(summary)
        
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("Make sure you have created config/config.json with your API credentials")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.option('--course-id', '-c', type=int, required=True)
def list_forums(course_id):
    """List all forums in a course"""
    try:
        processor = MoodleAIProcessor()
        forums = processor.get_course_forums(course_id)
        
        if forums:
            click.echo(f"Forums in course {course_id}:")
            for forum in forums:
                click.echo(f"ID: {forum.get('id')} - {forum.get('name')}")
        else:
            click.echo(f"No forums found in course {course_id}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command()  
@click.option('--course-id', '-c', type=int, required=True)
def course_info(course_id):
    """Get course information"""
    try:
        processor = MoodleAIProcessor()
        course = processor.moodle_client.get_course_details(course_id)
        
        if course:
            click.echo(f"Course ID: {course.get('id')}")
            click.echo(f"Name: {course.get('fullname')}")
            click.echo(f"Short Name: {course.get('shortname')}")
            click.echo(f"Category ID: {course.get('categoryid')}")
        else:
            click.echo(f"Course {course_id} not found")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.group()
def cli():
    """Moodle AI Processor - Process student posts with AI"""
    pass


# Add commands to the CLI group
cli.add_command(main, name='process')
cli.add_command(list_forums, name='forums') 
cli.add_command(course_info, name='info')


if __name__ == '__main__':
    cli()
