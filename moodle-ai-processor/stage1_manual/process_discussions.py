#!/usr/bin/env python3
"""
Discussion Processing Pipeline

This script provides a complete pipeline for processing forum discussion JSON files
and generating comprehensive LLM feedback.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / 'src'))
sys.path.append(str(project_root / 'stage1_manual'))

from discussion_processor import DiscussionProcessor


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/discussion_processing.log'),
            logging.StreamHandler()
        ]
    )


def process_discussion_batch(input_dir: str, output_dir: str, file_pattern: str = "*.json"):
    """
    Process multiple discussion JSON files in batch
    
    Args:
        input_dir: Directory containing JSON files
        output_dir: Directory to save processed results
        file_pattern: File pattern to match (default: *.json)
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize processor
    processor = DiscussionProcessor()
    
    # Find JSON files
    json_files = list(input_path.glob(file_pattern))
    
    if not json_files:
        print(f"⚠️  No JSON files found in {input_dir} matching pattern {file_pattern}")
        return
    
    print(f"🔍 Found {len(json_files)} JSON files to process")
    
    results_summary = []
    
    for json_file in json_files:
        print(f"\n📝 Processing: {json_file.name}")
        
        try:
            # Generate output filename
            output_file = output_path / f"{json_file.stem}_comprehensive_feedback.json"
            
            # Process the file
            results = processor.process_discussion_file(str(json_file), str(output_file))
            
            # Track results
            summary = {
                'file': json_file.name,
                'status': 'success',
                'total_posts': results['discussion_data']['metadata']['total_posts'],
                'student_posts': results['discussion_data']['metadata']['student_posts'],
                'output_file': output_file.name,
                'processed_at': results['processed_at']
            }
            results_summary.append(summary)
            
            print(f"   ✅ Successfully processed {summary['total_posts']} posts")
            print(f"   📊 {summary['student_posts']} student contributions analyzed")
            print(f"   💾 Results saved to: {output_file.name}")
            
        except Exception as e:
            print(f"   ❌ Error processing {json_file.name}: {e}")
            logging.error(f"Failed to process {json_file}: {e}")
            
            summary = {
                'file': json_file.name,
                'status': 'error',
                'error': str(e),
                'processed_at': datetime.now().isoformat()
            }
            results_summary.append(summary)
    
    # Print final summary
    print(f"\n📈 Processing Summary:")
    print(f"   Total files: {len(json_files)}")
    print(f"   Successful: {len([r for r in results_summary if r['status'] == 'success'])}")
    print(f"   Errors: {len([r for r in results_summary if r['status'] == 'error'])}")
    
    return results_summary


def process_single_discussion(input_file: str, output_file: Optional[str] = None):
    """
    Process a single discussion JSON file
    
    Args:
        input_file: Path to the JSON file
        output_file: Optional output path (auto-generated if not provided)
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"❌ Input file not found: {input_file}")
        return None
    
    # Generate output path if not provided
    if not output_file:
        output_dir = input_path.parent.parent / "stage1_manual" / "processed"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = str(output_dir / f"{input_path.stem}_comprehensive_feedback.json")
    
    # Initialize processor
    processor = DiscussionProcessor()
    
    print(f"📝 Processing: {input_path.name}")
    
    try:
        results = processor.process_discussion_file(str(input_path), str(output_file))
        
        print(f"✅ Processing completed successfully!")
        print(f"📊 Total posts processed: {results['discussion_data']['metadata']['total_posts']}")
        print(f"👥 Student contributions: {results['discussion_data']['metadata']['student_posts']}")
        print(f"🔄 Discussion phases: {results['discussion_data']['discussion_flow']['discussion_phases']}")
        print(f"💾 Results saved to: {output_file}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        logging.error(f"Processing failed for {input_file}: {e}")
        return None


def preview_discussion_structure(input_file: str):
    """
    Preview the structure of a discussion JSON file without full processing
    
    Args:
        input_file: Path to the JSON file
    """
    processor = DiscussionProcessor()
    
    try:
        # Parse structure only
        discussion_data = processor.parse_discussion_json(input_file)
        
        print(f"📋 Discussion Structure Preview for: {Path(input_file).name}")
        print(f"   📊 Total posts: {discussion_data['metadata']['total_posts']}")
        print(f"   🔄 Root posts: {discussion_data['metadata']['root_posts']}")
        print(f"   👥 Student posts: {discussion_data['metadata']['student_posts']}")
        print(f"   📅 Discussion phases: {discussion_data['discussion_flow']['discussion_phases']}")
        print(f"   📈 Post type distribution:")
        
        for post_type, count in discussion_data['discussion_flow']['post_type_distribution'].items():
            print(f"      {post_type}: {count}")
        
        print(f"   ⏱️  Discussion timeline: {discussion_data['discussion_flow']['total_timeline_hours']} hours")
        
        # Show sample post titles
        if discussion_data['student_contributions']:
            print(f"   📝 Sample student post subjects:")
            for post in discussion_data['student_contributions'][:3]:
                subject = post['subject'][:50] + "..." if len(post['subject']) > 50 else post['subject']
                print(f"      - {subject}")
        
        return discussion_data
        
    except Exception as e:
        print(f"❌ Error previewing file: {e}")
        return None


def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("""
🎯 Discussion Processing Pipeline

Usage:
    python process_discussions.py <command> [options]

Commands:
    single <file>           - Process a single JSON discussion file
    batch <input_dir>       - Process all JSON files in a directory  
    preview <file>          - Preview discussion structure without processing
    
Examples:
    python process_discussions.py single uploads/discussion-7Sept.json
    python process_discussions.py batch uploads/
    python process_discussions.py preview uploads/discussion-7Sept.json
        """)
        return
    
    # Setup logging
    setup_logging()
    
    command = sys.argv[1].lower()
    
    if command == 'single':
        if len(sys.argv) < 3:
            print("❌ Please provide input file path")
            return
        
        input_file = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
        process_single_discussion(input_file, output_file)
        
    elif command == 'batch':
        if len(sys.argv) < 3:
            print("❌ Please provide input directory path")
            return
        
        input_dir = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else str(Path(input_dir).parent / "processed")
        process_discussion_batch(input_dir, output_dir)
        
    elif command == 'preview':
        if len(sys.argv) < 3:
            print("❌ Please provide input file path")
            return
        
        input_file = sys.argv[2]
        preview_discussion_structure(input_file)
        
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: single, batch, preview")


if __name__ == "__main__":
    main()
