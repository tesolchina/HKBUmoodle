#!/usr/bin/env python3
"""
Example Usage Script

This script demonstrates basic usage of the Moodle AI Processor
"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.moodle_client import MoodleAPIClient
from src.ai_client import OpenRouterClient


def main():
    print("Moodle AI Processor - Example Usage")
    print("=" * 40)
    
    # Load configuration
    try:
        with open('config/config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("ERROR: config/config.json not found!")
        print("Please copy config/config.template.json to config/config.json and fill in your credentials")
        return
    
    # Initialize Moodle client
    moodle_client = MoodleAPIClient(
        base_url=config['moodle']['base_url'],
        token=config['moodle']['token']
    )
    
    print(f"Connected to: {config['moodle']['base_url']}")
    
    try:
        # Test: Get course details
        print("\n1. Testing course details...")
        course = moodle_client.get_course_details(99)  # Course ID from sandbox
        if course:
            print(f"   Course: {course.get('fullname', 'Unknown')}")
            print(f"   ID: {course.get('id')}")
        else:
            print("   No course found with ID 99")
        
        # Test: Get forums in course
        print("\n2. Testing forums...")
        forums = moodle_client.get_forums(99)
        print(f"   Found {len(forums)} forums")
        
        for i, forum in enumerate(forums[:3]):  # Show first 3 forums
            print(f"   {i+1}. {forum.get('name')} (ID: {forum.get('id')})")
        
        # Test AI client (only if API key is configured)
        if config['openrouter']['api_key'] != 'your_openrouter_api_key_here':
            print("\n3. Testing AI client...")
            ai_client = OpenRouterClient(
                api_key=config['openrouter']['api_key'],
                model=config['openrouter']['model']
            )
            
            # Test with a sample student post
            sample_post = "I think the reading material was interesting but I'm not sure I understand the main concepts fully."
            
            response = ai_client.generate_reply(sample_post)
            print(f"   Sample student post: {sample_post}")
            print(f"   AI response: {response}")
        else:
            print("\n3. Skipping AI test - OpenRouter API key not configured")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        print("Make sure your Moodle credentials are correct and the course exists")
    
    print("\nExample completed!")
    print("\nNext steps:")
    print("1. Configure your OpenRouter API key in config/config.json")
    print("2. Run: python main.py process --course-id 99 --help")
    print("3. Run: python main.py forums --course-id 99")


if __name__ == '__main__':
    main()
