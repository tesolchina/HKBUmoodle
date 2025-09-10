#!/usr/bin/env python3
"""
Course Analytics Script - Analyze course data and generate reports
"""

import json
import sys
from pathlib import Path

def analyze_course_data():
    """Analyze course data and generate insights"""
    # Load sample data
    data_dir = Path(__file__).parent.parent
    
    with open(data_dir / 'sample_course.json') as f:
        course = json.load(f)
    
    with open(data_dir / 'sample_users.json') as f:
        users = json.load(f)
    
    with open(data_dir / 'sample_content.json') as f:
        content = json.load(f)
    
    print(f"Course Analytics Report")
    print(f"=" * 50)
    print(f"Course: {course.get('fullname', 'Unknown')}")
    print(f"ID: {course.get('id', 'Unknown')}")
    print(f"Users: {len(users)}")
    print(f"Content Sections: {len(content)}")
    
    # Analyze user roles
    role_counts = {}
    for user in users:
        for role in user.get('roles', []):
            role_name = role.get('shortname', 'unknown')
            role_counts[role_name] = role_counts.get(role_name, 0) + 1
    
    print(f"\nUser Roles:")
    for role, count in role_counts.items():
        print(f"  {role}: {count}")
    
    # Analyze content types
    module_counts = {}
    total_modules = 0
    for section in content:
        for module in section.get('modules', []):
            mod_type = module.get('modname', 'unknown')
            module_counts[mod_type] = module_counts.get(mod_type, 0) + 1
            total_modules += 1
    
    print(f"\nContent Modules ({total_modules} total):")
    for mod_type, count in module_counts.items():
        print(f"  {mod_type}: {count}")

if __name__ == "__main__":
    analyze_course_data()
