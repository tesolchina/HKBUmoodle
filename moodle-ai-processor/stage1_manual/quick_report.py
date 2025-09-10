#!/usr/bin/env python3
"""
Quick HTML Report Generator

Simple script to generate HTML feedback reports for posting to Moodle.
"""

import sys
from pathlib import Path
from html_report_generator import HTMLReportGenerator
import json

def main():
    """Generate HTML reports from the latest analysis"""
    
    # Find the most recent analysis file
    processed_dir = Path(__file__).parent / "processed"
    analysis_files = list(processed_dir.glob("outline_feedback_analysis_*.json"))
    
    if not analysis_files:
        print("❌ No analysis files found in processed/ directory")
        print("Please run the outline_feedback_processor.py first")
        return 1
    
    # Use the most recent file
    latest_file = max(analysis_files, key=lambda x: x.stat().st_mtime)
    print(f"📊 Using analysis file: {latest_file.name}")
    
    # Load analysis data
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading analysis file: {e}")
        return 1
    
    # Initialize generator
    generator = HTMLReportGenerator()
    
    # Generate reports
    try:
        print("🔄 Generating HTML reports...")
        
        # Main comprehensive report
        main_report = "moodle_feedback_report.html"
        generator.generate_feedback_report(analysis_data, main_report)
        print(f"✅ Main report: {main_report}")
        
        # Individual student reports
        individual_dir = "individual_reports"
        individual_files = generator.generate_individual_student_reports(
            analysis_data, 
            individual_dir
        )
        print(f"✅ Individual reports: {len(individual_files)} files in {individual_dir}/")
        
        # Summary
        print("\n📋 SUMMARY:")
        task_info = analysis_data.get('task_info', {})
        print(f"   - Topic: {task_info.get('topic', 'N/A')}")
        print(f"   - Students analyzed: {task_info.get('student_outlines', 'N/A')}")
        print(f"   - Analysis date: {task_info.get('processing_timestamp', 'N/A')}")
        
        print("\n📤 READY FOR MOODLE:")
        print(f"   - Post main report: {main_report}")
        print(f"   - Send individual reports to students")
        print("\n💡 TIP: You can open the HTML files in a browser to preview before posting to Moodle")
        
    except Exception as e:
        print(f"❌ Error generating reports: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
