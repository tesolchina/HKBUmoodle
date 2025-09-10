#!/usr/bin/env python3
"""
User Management Script - Manage course users and roles
"""

import json
from pathlib import Path

def manage_users():
    """Demonstrate user management operations"""
    data_dir = Path(__file__).parent.parent
    
    with open(data_dir / 'sample_users.json') as f:
        users = json.load(f)
    
    print(f"User Management Demo")
    print(f"=" * 50)
    
    # List all users
    print(f"Current Users ({len(users)}):")
    for user in users:
        roles = ", ".join([role.get('shortname', 'unknown') for role in user.get('roles', [])])
        print(f"  {user.get('fullname', 'Unknown')} ({user.get('email', 'no-email')}) - {roles}")
    
    # Filter by role
    students = [u for u in users if any(r.get('shortname') == 'student' for r in u.get('roles', []))]
    teachers = [u for u in users if any(r.get('shortname') in ['teacher', 'editingteacher'] for r in u.get('roles', []))]
    
    print(f"\nStudents: {len(students)}")
    print(f"Teachers: {len(teachers)}")
    
    # This is where you would add actual Moodle API calls
    # For example: client.enrol_user(course_id, user_id, role_id)
    print(f"\nIn online mode, this would:")
    print(f"   - Enrol new users")
    print(f"   - Change user roles")
    print(f"   - Send notifications")

if __name__ == "__main__":
    manage_users()
