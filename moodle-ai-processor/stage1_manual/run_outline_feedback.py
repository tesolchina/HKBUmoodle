#!/usr/bin/env python3
"""
Run outline feedback processing on the section 38 discussion
"""

import sys
from pathlib import Path
import logging

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from outline_feedback_processor import OutlineFeedbackProcessor


def main():
    """Process the section 38 discussion file"""
    
    # Setup logging
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / 'outline_processing.log'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    # File paths
    json_file = "uploads/discussion-week1-section38.json"
    
    logger.info("Starting outline feedback processing...")
    
    try:
        # Initialize processor
        processor = OutlineFeedbackProcessor()
        
        # Process the discussion
        results = processor.process_outline_discussion(json_file)
        
        if 'error' in results:
            logger.error(f"Processing failed: {results['error']}")
            return 1
        
        # Print summary
        task_info = results['task_info']
        print("\n" + "="*60)
        print("OUTLINE FEEDBACK PROCESSING SUMMARY")
        print("="*60)
        print(f"Topic: {task_info.get('topic', 'N/A')}")
        print(f"Total posts: {task_info['total_posts']}")
        print(f"Student outlines: {task_info['student_outlines']}")
        print(f"Processing time: {task_info['processing_timestamp']}")
        
        if 'output_file' in results:
            print(f"Results saved to: {results['output_file']}")
        
        # Print aggregate insights
        if 'aggregate_analysis' in results and 'error' not in results['aggregate_analysis']:
            analysis = results['aggregate_analysis']
            
            print("\n" + "-"*40)
            print("CLASS OVERVIEW")
            print("-"*40)
            
            if 'class_overview' in analysis:
                overview = analysis['class_overview']
                print(f"Students analyzed: {overview.get('total_students', 'N/A')}")
                print(f"Average performance: {overview.get('average_performance', 'N/A')}")
                print(f"Overall readiness: {overview.get('overall_readiness', 'N/A')}")
            
            print("\n" + "-"*40)
            print("MOST FREQUENT ISSUES")
            print("-"*40)
            
            if 'frequent_issues' in analysis:
                for i, issue in enumerate(analysis['frequent_issues'][:3], 1):
                    if isinstance(issue, dict):
                        print(f"{i}. {issue.get('issue', 'N/A')}")
                        print(f"   Frequency: {issue.get('frequency', 'N/A')}")
                        print(f"   Solution: {issue.get('solution', 'N/A')}")
                        print()
            
            print("-"*40)
            print("TEACHING PRIORITIES")
            print("-"*40)
            
            if 'teaching_priorities' in analysis:
                for i, priority in enumerate(analysis['teaching_priorities'][:3], 1):
                    print(f"{i}. {priority}")
        
        print("\n" + "="*60)
        print("Processing completed successfully!")
        print("="*60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
