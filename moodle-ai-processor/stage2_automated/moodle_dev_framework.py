#!/usr/bin/env python3
"""
Enhanced Moodle API Development Framework

This script provides a comprehensive framework for Moodle API development
and testing, including offline mode for when campus network is unavailable.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'src'))

try:
    from moodle_client import MoodleAPIClient
except ImportError:
    print("⚠️  Could not import MoodleAPIClient - creating mock client")
    MoodleAPIClient = None

class MoodleDevelopmentFramework:
    """Enhanced Moodle API development and testing framework"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with configuration"""
        self.config_path = config_path or str(Path(__file__).parent.parent.parent.parent / 'config' / 'config.json')
        self.config = self._load_config()
        self.client = None
        self.offline_mode = False
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        print(f"🚀 Moodle Development Framework Initialized")
        print(f"📁 Config Path: {self.config_path}")
        
        if self.config:
            print(f"📍 Moodle URL: {self.config.get('moodle_url', 'Not configured')}")
            print(f"🔑 Token: {'✅ Configured' if self.config.get('api_token') else '❌ Missing'}")
            
            # Try to initialize client
            if MoodleAPIClient and self.config.get('moodle_url') and self.config.get('api_token'):
                try:
                    self.client = MoodleAPIClient(
                        self.config['moodle_url'],
                        self.config['api_token']
                    )
                    print(f"✅ Moodle API Client initialized")
                except Exception as e:
                    print(f"⚠️  Client initialization failed: {e}")
                    self.offline_mode = True
            else:
                self.offline_mode = True
                print(f"📴 Running in offline mode")
        else:
            self.offline_mode = True
            print(f"❌ No configuration found - running in offline mode")
    
    def _load_config(self) -> Optional[Dict]:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Config file not found: {self.config_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in config file: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test basic API connection"""
        if self.offline_mode or not self.client:
            print(f"📴 Offline mode - cannot test connection")
            return False
        
        try:
            print(f"🧪 Testing API connection...")
            # This would be the actual test when online
            result = self.client._make_request('core_webservice_get_site_info')
            
            if result and 'sitename' in result:
                print(f"✅ Connection successful!")
                print(f"📍 Site: {result.get('sitename')}")
                print(f"🌐 URL: {result.get('siteurl')}")
                print(f"👤 User: {result.get('userfullname')}")
                return True
            else:
                print(f"❌ Unexpected response format")
                return False
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def get_course_info(self, course_id: Optional[int] = None, idnumber: Optional[str] = None) -> Optional[Dict]:
        """Get course information by ID or idnumber"""
        if self.offline_mode or not self.client:
            print(f"📴 Offline mode - returning mock course data")
            return {
                'id': course_id or 99,
                'fullname': 'Mock Course for Development',
                'shortname': 'MOCK101',
                'idnumber': idnumber or '2024;S2;MOCK101;1;',
                'offline_mode': True
            }
        
        try:
            if course_id:
                print(f"🔍 Getting course by ID: {course_id}")
                return self.client.get_course_details(course_id)
            elif idnumber:
                print(f"🔍 Getting course by ID number: {idnumber}")
                return self.client.get_course_by_idnumber(idnumber)
            else:
                print(f"❌ Must provide either course_id or idnumber")
                return None
                
        except Exception as e:
            print(f"❌ Failed to get course info: {e}")
            return None
    
    def get_course_users(self, course_id: int) -> List[Dict]:
        """Get enrolled users in course"""
        if self.offline_mode or not self.client:
            print(f"📴 Offline mode - returning mock user data")
            return [
                {
                    'id': 1,
                    'fullname': 'Mock Student 1',
                    'email': 'student1@mock.hkbu.edu.hk',
                    'roles': [{'shortname': 'student'}],
                    'offline_mode': True
                },
                {
                    'id': 2,
                    'fullname': 'Mock Teacher',
                    'email': 'teacher@mock.hkbu.edu.hk',
                    'roles': [{'shortname': 'editingteacher'}],
                    'offline_mode': True
                }
            ]
        
        try:
            print(f"👥 Getting enrolled users for course {course_id}")
            return self.client.get_enrolled_users(course_id)
        except Exception as e:
            print(f"❌ Failed to get course users: {e}")
            return []
    
    def get_course_content(self, course_id: int) -> List[Dict]:
        """Get course content structure"""
        if self.offline_mode or not self.client:
            print(f"📴 Offline mode - returning mock content data")
            return [
                {
                    'id': 1,
                    'name': 'Week 1',
                    'section': 1,
                    'modules': [
                        {
                            'id': 1,
                            'name': 'Course Introduction',
                            'modname': 'page',
                            'url': 'https://mock.hkbu.edu.hk/mod/page/view.php?id=1'
                        },
                        {
                            'id': 2,
                            'name': 'Discussion Forum',
                            'modname': 'forum',
                            'url': 'https://mock.hkbu.edu.hk/mod/forum/view.php?id=2'
                        }
                    ],
                    'offline_mode': True
                }
            ]
        
        try:
            print(f"📚 Getting course content for course {course_id}")
            return self.client.get_course_contents(course_id)
        except Exception as e:
            print(f"❌ Failed to get course content: {e}")
            return []
    
    def create_development_workspace(self):
        """Create a development workspace with sample data and scripts"""
        workspace_dir = Path(__file__).parent / 'dev_workspace'
        workspace_dir.mkdir(exist_ok=True)
        
        print(f"🛠️  Creating development workspace at: {workspace_dir}")
        
        # Sample course data
        sample_course = self.get_course_info(course_id=99)
        sample_users = self.get_course_users(99)
        sample_content = self.get_course_content(99)
        
        # Save sample data
        with open(workspace_dir / 'sample_course.json', 'w', encoding='utf-8') as f:
            json.dump(sample_course, f, indent=2)
        
        with open(workspace_dir / 'sample_users.json', 'w', encoding='utf-8') as f:
            json.dump(sample_users, f, indent=2)
        
        with open(workspace_dir / 'sample_content.json', 'w', encoding='utf-8') as f:
            json.dump(sample_content, f, indent=2)
        
        # Create development scripts
        self._create_dev_scripts(workspace_dir)
        
        print(f"✅ Development workspace created!")
        print(f"📁 Location: {workspace_dir}")
        print(f"📄 Files created:")
        print(f"   - sample_course.json")
        print(f"   - sample_users.json") 
        print(f"   - sample_content.json")
        print(f"   - dev_scripts/")
    
    def _create_dev_scripts(self, workspace_dir: Path):
        """Create development scripts"""
        scripts_dir = workspace_dir / 'dev_scripts'
        scripts_dir.mkdir(exist_ok=True)
        
        # Course Analytics Script (remove emojis for Windows compatibility)
        course_analytics_script = '''#!/usr/bin/env python3
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
    
    print(f"\\nUser Roles:")
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
    
    print(f"\\nContent Modules ({total_modules} total):")
    for mod_type, count in module_counts.items():
        print(f"  {mod_type}: {count}")

if __name__ == "__main__":
    analyze_course_data()
'''
        
        with open(scripts_dir / 'course_analytics.py', 'w', encoding='utf-8') as f:
            f.write(course_analytics_script)
        
        # Script 2: User Management
        user_management_script = '''#!/usr/bin/env python3
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
    
    print(f"\\nStudents: {len(students)}")
    print(f"Teachers: {len(teachers)}")
    
    # This is where you would add actual Moodle API calls
    # For example: client.enrol_user(course_id, user_id, role_id)
    print(f"\\nIn online mode, this would:")
    print(f"   - Enrol new users")
    print(f"   - Change user roles")
    print(f"   - Send notifications")

if __name__ == "__main__":
    manage_users()
'''
        
        with open(scripts_dir / 'user_management.py', 'w', encoding='utf-8') as f:
            f.write(user_management_script)
        
        print(f"📄 Development scripts created:")
        print(f"   - dev_scripts/course_analytics.py")
        print(f"   - dev_scripts/user_management.py")
    
    def run_demo(self):
        """Run a complete demo of the framework"""
        print(f"\n🎯 Running Moodle Development Framework Demo")
        print(f"=" * 60)
        
        # Test connection
        connection_ok = self.test_connection()
        
        if not connection_ok and not self.offline_mode:
            print(f"⚠️  Connection failed - switching to offline mode")
            self.offline_mode = True
        
        # Get sample data
        print(f"\n📚 Getting course information...")
        course = self.get_course_info(course_id=99)
        
        print(f"\n👥 Getting course users...")
        users = self.get_course_users(99)
        
        print(f"\n📄 Getting course content...")
        content = self.get_course_content(99)
        
        # Create workspace
        print(f"\n🛠️  Setting up development workspace...")
        self.create_development_workspace()
        
        print(f"\n✅ Demo completed!")
        print(f"📍 Next steps:")
        print(f"   1. Connect to HKBU campus network/VPN")
        print(f"   2. Test real API connections")
        print(f"   3. Use development workspace for testing")
        print(f"   4. Integrate with GCAP 3056 course automation")
        
        return {
            'connection_tested': connection_ok,
            'offline_mode': self.offline_mode,
            'sample_data_created': True,
            'workspace_created': True
        }

def main():
    """Main function"""
    print(f"🚀 Moodle Development Framework")
    print(f"📚 Advanced testing and development for HKBU Moodle integration")
    
    # Initialize framework
    framework = MoodleDevelopmentFramework()
    
    # Run demo
    results = framework.run_demo()
    
    print(f"\n💾 Results: {json.dumps(results, indent=2)}")

if __name__ == "__main__":
    main()
