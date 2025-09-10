"""
Stage 2: Automated API Processing

Command-line interface for automated Moodle API processing
"""

import click
import json
import sys
from pathlib import Path

# Add parent src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

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
@click.option('--config', '-cfg', default='../config/config.json',
              help='Path to configuration file')
@click.option('--output', '-o', 
              help='Output file for results (JSON format)')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose logging')
def process(course_id, forum_id, auto_reply, limit, config, output, verbose):
    """
    Process students' posts in Moodle using API and AI
    
    This tool automatically reads students' posts from Moodle forums via API,
    processes them with AI to generate feedback and replies, and optionally 
    posts the replies back to Moodle.
    """
    try:
        # Initialize processor
        processor = MoodleAIProcessor(config)
        
        click.echo(f"🔗 Stage 2: Automated API Processing")
        click.echo(f"Processing posts from course {course_id}")
        if forum_id:
            click.echo(f"Targeting specific forum: {forum_id}")
        if auto_reply:
            click.echo("⚠️  Auto-reply is ENABLED - AI responses will be posted to Moodle")
        else:
            click.echo("ℹ️  Auto-reply is DISABLED - results will only be displayed/saved")
        
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
                    click.echo(f"{i}. Post {result.get('post_id')} - ❌ ERROR: {result['error']}")
                else:
                    status = "✅ Replied" if result.get('auto_replied') else "✅ Analyzed"
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
            click.echo(f"\n📁 Results saved to {output}")
        
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
@click.option('--config', '-cfg', default='../config/config.json')
def forums(course_id, config):
    """List all forums in a course"""
    try:
        processor = MoodleAIProcessor(config)
        forums = processor.get_course_forums(course_id)
        
        if forums:
            click.echo(f"📋 Forums in course {course_id}:")
            for forum in forums:
                click.echo(f"   ID: {forum.get('id')} - {forum.get('name')}")
        else:
            click.echo(f"No forums found in course {course_id}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command()  
@click.option('--course-id', '-c', type=int, required=True)
@click.option('--config', '-cfg', default='../config/config.json')
def info(course_id, config):
    """Get course information"""
    try:
        processor = MoodleAIProcessor(config)
        course = processor.moodle_client.get_course_details(course_id)
        
        if course:
            click.echo(f"📚 Course Information:")
            click.echo(f"   ID: {course.get('id')}")
            click.echo(f"   Name: {course.get('fullname')}")
            click.echo(f"   Short Name: {course.get('shortname')}")
            click.echo(f"   Category ID: {course.get('categoryid')}")
        else:
            click.echo(f"Course {course_id} not found")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.option('--config', '-cfg', default='../config/config.json')
def test_connection(config):
    """Test Moodle API connection"""
    try:
        processor = MoodleAIProcessor(config)
        
        click.echo("🔍 Testing Moodle API connection...")
        
        # Test with course 99 from your sandbox
        course = processor.moodle_client.get_course_details(99)
        if course:
            click.echo("✅ Moodle API connection successful!")
            click.echo(f"   Test course: {course.get('fullname', 'Unknown')}")
        else:
            click.echo("⚠️  Connected but no course found with ID 99")
        
        click.echo("\n🤖 Testing AI connection...")
        test_response = processor.ai_client.generate_response(
            "Hello, this is a test message.",
            max_tokens=50
        )
        click.echo("✅ AI API connection successful!")
        click.echo(f"   Test response: {test_response[:100]}...")
        
    except Exception as e:
        click.echo(f"❌ Connection test failed: {e}")
        sys.exit(1)


@click.group()
def cli():
    """Stage 2: Automated Moodle API Processing with AI"""
    pass


# Add commands to the CLI group
cli.add_command(process)
cli.add_command(forums)
cli.add_command(info)
cli.add_command(test_connection, name='test')


if __name__ == '__main__':
    cli()
