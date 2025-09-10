#!/usr/bin/env python3
"""
Moodle Sandbox Explorer

This script helps us explore what we can actually do in the sandbox
by combining GUI setup with API testing.
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

class MoodleSandboxExplorer:
    """Explorer for testing actual capabilities in the Moodle sandbox"""
    
    def __init__(self):
        self.base_url = "https://moddw12-buelearning.hkbu.edu.hk"
        self.token = "eac84a6e8c353a7f88f424b14a340df4"
        self.api_endpoint = f"{self.base_url}/webservice/rest/server.php"
        
        print(f"🔍 Moodle Sandbox Explorer")
        print(f"📍 Sandbox URL: {self.base_url}")
        print(f"🔑 Token: {self.token[:10]}...")
        print(f"⚡ API Endpoint: {self.api_endpoint}")
        print(f"🌐 GUI Access: {self.base_url}/login/index.php")
    
    def _make_request(self, function: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
        """Make API request with detailed logging"""
        if params is None:
            params = {}
        
        request_params = {
            'wstoken': self.token,
            'wsfunction': function,
            'moodlewsrestformat': 'json'
        }
        request_params.update(params)
        
        try:
            print(f"📡 API Call: {function}")
            if params:
                print(f"📋 Parameters: {json.dumps(params, indent=2)}")
            
            response = requests.get(self.api_endpoint, params=request_params, timeout=30)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and 'exception' in data:
                    print(f"❌ API Error: {data['exception']}")
                    print(f"💬 Message: {data.get('message', 'No message')}")
                    print(f"🔧 Error Code: {data.get('errorcode', 'No code')}")
                    return None
                else:
                    print(f"✅ Success! Response size: {len(json.dumps(data))} chars")
                    return data
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def explore_available_functions(self):
        """Try to discover what web service functions are available"""
        print(f"\n{'='*60}")
        print(f"🔍 EXPLORING AVAILABLE API FUNCTIONS")
        print(f"{'='*60}")
        
        # List of functions to test (from basic to advanced)
        test_functions = [
            # Basic functions
            'core_webservice_get_site_info',
            
            # Course functions (we know these work)
            'core_course_get_courses',
            'core_course_get_contents',
            'core_course_get_courses_by_field',
            
            # User functions
            'core_user_get_users_by_field',
            'core_enrol_get_enrolled_users',
            'core_user_get_course_user_profiles',
            
            # Forum functions (your requirements)
            'mod_forum_get_forums_by_courses',
            'mod_forum_get_forum_discussions',
            'mod_forum_get_discussion_posts',
            'mod_forum_add_discussion_post',
            'mod_forum_add_discussion',
            
            # Quiz functions (your requirements)
            'mod_quiz_get_quizzes_by_courses',
            'mod_quiz_get_quiz_attempts',
            'mod_quiz_get_attempt_data',
            'mod_quiz_save_attempt',
            
            # Content creation functions (your requirements)
            'core_course_create_course_section',
            'core_course_add_module',
            'core_course_edit_module',
            'core_course_delete_module',
            
            # Grade functions
            'core_grades_update_grades',
            'gradereport_user_get_grade_items',
            'core_grades_get_grades',
        ]
        
        results = {}
        
        for function in test_functions:
            print(f"\n🧪 Testing: {function}")
            
            # Use minimal parameters for testing
            test_params = {}
            
            # Add specific parameters for certain functions
            if 'course' in function.lower():
                if 'by_courses' in function:
                    test_params['courseids[0]'] = '99'
                elif 'courseid' in function or function in ['core_course_get_contents']:
                    test_params['courseid'] = '99'
                elif 'options' in function or function == 'core_course_get_courses':
                    test_params['options[ids][0]'] = '99'
            
            if 'user' in function.lower():
                if 'by_field' in function:
                    test_params['field'] = 'username'
                    test_params['values[0]'] = 'lcadmin'
                elif 'enrolled' in function:
                    test_params['courseid'] = '99'
            
            result = self._make_request(function, test_params)
            
            if result is not None:
                results[function] = 'SUCCESS'
                print(f"✅ {function}: WORKING!")
                
                # Show preview of successful results
                if isinstance(result, list) and len(result) > 0:
                    print(f"   📊 Returned {len(result)} items")
                elif isinstance(result, dict):
                    print(f"   📊 Returned object with keys: {list(result.keys())[:5]}")
            else:
                results[function] = 'FAILED'
                print(f"❌ {function}: NOT ACCESSIBLE")
        
        return results
    
    def create_gui_setup_guide(self):
        """Create a guide for setting up test scenarios via GUI"""
        print(f"\n{'='*60}")
        print(f"🖥️  GUI SETUP GUIDE FOR TESTING")
        print(f"{'='*60}")
        
        setup_guide = f"""
🎯 STEP-BY-STEP GUI SETUP FOR API TESTING

1. 📂 ACCESS SANDBOX VIA GUI
   URL: {self.base_url}/login/index.php
   Username: lcladmin
   Password: Lcadm#2025
   
2. 🎓 SELECT TEST COURSE
   Recommended: UCLC1009 University English II (Section 1) [2024 S2]
   Course ID: 99 (confirmed working via API)
   
3. 🏗️  TEST CONTENT CREATION (YOUR REQUIREMENT #1)
   Via GUI:
   - Go to course → Turn editing on
   - Add section: "API Test Section"
   - Add page: "Test Page Content"
   - Add forum: "Test Discussion Forum"
   - Add resource: "Test File/Link"
   
   Then via API:
   - Run our content scanning to see if it appears
   - Try to read the new content structure
   - Document IDs for further testing
   
4. 💬 TEST FORUM INTERACTION (YOUR REQUIREMENTS #2 & #3)
   Via GUI:
   - Create a test discussion post
   - Add 2-3 student replies (using admin account)
   - Note discussion ID and post IDs
   
   Then via API:
   - Try mod_forum_get_forum_discussions
   - Try mod_forum_get_discussion_posts
   - Try mod_forum_add_discussion_post
   
5. 📊 TEST QUIZ FUNCTIONALITY (YOUR REQUIREMENT #4)
   Via GUI:
   - Create a simple quiz with 2-3 questions
   - Take the quiz as a student (preview mode)
   - Submit answers
   
   Then via API:
   - Try mod_quiz_get_quizzes_by_courses
   - Try mod_quiz_get_quiz_attempts
   - Try to read quiz data
   
6. 👥 TEST USER MANAGEMENT
   Via GUI:
   - Check enrolled users
   - Note user IDs and roles
   
   Then via API:
   - Try core_enrol_get_enrolled_users
   - Try core_user_get_course_user_profiles
"""
        
        print(setup_guide)
        
        # Save guide to file
        with open('gui_setup_guide.txt', 'w', encoding='utf-8') as f:
            f.write(setup_guide)
        
        print(f"💾 Guide saved to: gui_setup_guide.txt")
        
        return setup_guide
    
    def test_specific_course_operations(self, course_id: int = 99):
        """Test specific operations on a known working course"""
        print(f"\n{'='*60}")
        print(f"🧪 TESTING SPECIFIC COURSE OPERATIONS")
        print(f"{'='*60}")
        
        print(f"🎯 Target Course: {course_id}")
        
        # Test 1: Get detailed course info
        print(f"\n📚 Test 1: Get Course Details")
        course_data = self._make_request('core_course_get_courses', {
            'options[ids][0]': str(course_id)
        })
        
        if course_data and len(course_data) > 0:
            course = course_data[0]
            print(f"✅ Course found: {course.get('fullname')}")
            print(f"📊 Sections: {course.get('numsections', 'Unknown')}")
            print(f"🎨 Format: {course.get('format', 'Unknown')}")
        
        # Test 2: Get course structure
        print(f"\n📄 Test 2: Get Course Structure")
        content_data = self._make_request('core_course_get_contents', {
            'courseid': str(course_id)
        })
        
        if content_data:
            print(f"✅ Retrieved {len(content_data)} sections")
            
            for i, section in enumerate(content_data):
                section_name = section.get('name', f'Section {i+1}')
                modules = section.get('modules', [])
                print(f"  📂 {section_name}: {len(modules)} modules")
                
                for module in modules:
                    mod_name = module.get('name', 'Unknown')
                    mod_type = module.get('modname', 'unknown')
                    mod_id = module.get('id', 'Unknown')
                    print(f"    📄 {mod_name} ({mod_type}) - ID: {mod_id}")
        
        # Test 3: Try to get forum details
        print(f"\n💬 Test 3: Forum Analysis")
        if content_data:
            forums = []
            for section in content_data:
                for module in section.get('modules', []):
                    if module.get('modname') == 'forum':
                        forums.append(module)
            
            print(f"✅ Found {len(forums)} forums")
            
            for forum in forums:
                forum_id = forum.get('id')
                forum_name = forum.get('name')
                print(f"  💬 Forum: {forum_name} (ID: {forum_id})")
                
                # Try to get forum discussions
                print(f"    🔍 Testing forum discussion access...")
                discussions = self._make_request('mod_forum_get_forum_discussions', {
                    'forumid': str(forum_id)
                })
                
                if discussions:
                    print(f"    ✅ Forum discussions accessible!")
                    print(f"    📊 Found {len(discussions)} discussions")
                else:
                    print(f"    ❌ Forum discussions not accessible")
        
        # Test 4: Try to get enrolled users
        print(f"\n👥 Test 4: User Access")
        users = self._make_request('core_enrol_get_enrolled_users', {
            'courseid': str(course_id)
        })
        
        if users:
            print(f"✅ User access working!")
            print(f"👥 Found {len(users)} enrolled users")
            
            for user in users[:3]:  # Show first 3 users
                user_name = user.get('fullname', 'Unknown')
                user_id = user.get('id', 'Unknown')
                roles = user.get('roles', [])
                role_names = [role.get('shortname', 'unknown') for role in roles]
                print(f"  👤 {user_name} (ID: {user_id}) - Roles: {role_names}")
        else:
            print(f"❌ User access not available")
    
    def generate_sandbox_test_plan(self):
        """Generate a comprehensive test plan for sandbox exploration"""
        print(f"\n{'='*60}")
        print(f"📋 COMPREHENSIVE SANDBOX TEST PLAN")
        print(f"{'='*60}")
        
        test_plan = {
            "Phase 1: API Function Discovery": {
                "objective": "Map all available API functions",
                "method": "Systematic testing of common Moodle web service functions",
                "timeline": "30 minutes",
                "priority": "High"
            },
            "Phase 2: GUI Content Setup": {
                "objective": "Create test content via GUI for API testing", 
                "method": "Manual content creation in sandbox course",
                "timeline": "45 minutes",
                "priority": "High"
            },
            "Phase 3: API Content Reading": {
                "objective": "Verify API can read GUI-created content",
                "method": "Use working API functions to read new content",
                "timeline": "20 minutes", 
                "priority": "High"
            },
            "Phase 4: Forum Testing": {
                "objective": "Test forum reading and writing capabilities",
                "method": "Create forum posts via GUI, try to read/write via API",
                "timeline": "30 minutes",
                "priority": "Critical"
            },
            "Phase 5: Quiz Testing": {
                "objective": "Test quiz creation and grading capabilities",
                "method": "Create quiz via GUI, try to access via API",
                "timeline": "30 minutes",
                "priority": "Medium"
            }
        }
        
        print(f"📋 Test Plan Overview:")
        for phase, details in test_plan.items():
            print(f"\n🎯 {phase}")
            print(f"   Objective: {details['objective']}")
            print(f"   Method: {details['method']}")
            print(f"   Timeline: {details['timeline']}")
            print(f"   Priority: {details['priority']}")
        
        return test_plan

def main():
    """Main exploration function"""
    print(f"🚀 Moodle Sandbox Exploration Session")
    print(f"🎯 Goal: Test your 4 specific requirements using GUI + API")
    
    explorer = MoodleSandboxExplorer()
    
    # Step 1: Explore available functions
    print(f"\n🔍 STEP 1: Discover Available API Functions")
    results = explorer.explore_available_functions()
    
    # Step 2: Create GUI setup guide
    print(f"\n🖥️  STEP 2: Generate GUI Setup Guide")
    explorer.create_gui_setup_guide()
    
    # Step 3: Test specific course operations
    print(f"\n🧪 STEP 3: Test Known Working Course")
    explorer.test_specific_course_operations(99)
    
    # Step 4: Generate comprehensive test plan
    print(f"\n📋 STEP 4: Generate Test Plan")
    test_plan = explorer.generate_sandbox_test_plan()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 EXPLORATION SUMMARY")
    print(f"{'='*60}")
    
    working_functions = [func for func, status in results.items() if status == 'SUCCESS']
    failed_functions = [func for func, status in results.items() if status == 'FAILED']
    
    print(f"✅ Working Functions: {len(working_functions)}")
    for func in working_functions:
        print(f"  ✅ {func}")
    
    print(f"\n❌ Functions Needing Permissions: {len(failed_functions)}")
    for func in failed_functions[:5]:  # Show first 5
        print(f"  ❌ {func}")
    
    if len(failed_functions) > 5:
        print(f"  ... and {len(failed_functions) - 5} more")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"1. 🖥️  Use GUI to set up test content in Course 99")
    print(f"2. 🧪 Test API reading of GUI-created content")
    print(f"3. 💬 Focus on forum functions (your priority)")
    print(f"4. 📊 Test quiz functions if available")
    print(f"5. 📧 Report findings to ITO colleagues")
    
    # Save results
    with open('sandbox_exploration_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'api_function_results': results,
            'working_functions': working_functions,
            'failed_functions': failed_functions,
            'test_plan': test_plan
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: sandbox_exploration_results.json")

if __name__ == "__main__":
    main()
