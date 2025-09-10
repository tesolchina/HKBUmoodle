#!/usr/bin/env python3
"""
Moodle API Implementation Framework

This script demonstrates the proposed implementation of key Moodle API functions
based on Dr. Wang's requirements and successful API testing.
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

class MoodleAPIFramework:
    """Framework implementing the proposed Moodle API functions"""
    
    def __init__(self):
        self.base_url = "https://moddw12-buelearning.hkbu.edu.hk"
        self.token = "eac84a6e8c353a7f88f424b14a340df4"
        self.api_endpoint = f"{self.base_url}/webservice/rest/server.php"
        
        print(f"🚀 Moodle API Implementation Framework")
        print(f"📍 Target: {self.base_url}")
        print(f"🔑 Token: {self.token[:10]}...")
    
    def _make_request(self, function: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
        """Make API request with comprehensive error handling"""
        if params is None:
            params = {}
        
        request_params = {
            'wstoken': self.token,
            'wsfunction': function,
            'moodlewsrestformat': 'json'
        }
        request_params.update(params)
        
        try:
            response = requests.get(self.api_endpoint, params=request_params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and 'exception' in data:
                    print(f"❌ API Error: {data['exception']} - {data.get('message', '')}")
                    return None
                else:
                    return data
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None

    # ========================================
    # PHASE 1: COURSE CONTENT MANAGEMENT
    # ========================================
    
    def create_course_section(self, course_id: int, section_name: str, section_number: int) -> bool:
        """
        REQUIREMENT: Create new sections
        STATUS: Needs API permission expansion
        """
        print(f"\n📚 Creating section '{section_name}' in course {course_id}")
        print(f"⚠️  Note: Requires 'core_course_create_course_section' permission")
        
        # This would be the actual implementation when permissions are available
        params = {
            'courseid': str(course_id),
            'sectionnumber': str(section_number),
            'sectionname': section_name,
            'summary': f'Auto-generated section: {section_name}',
            'summaryformat': '1'
        }
        
        # Simulated response for demonstration
        print(f"📝 Would call: core_course_create_course_section")
        print(f"📋 Parameters: {json.dumps(params, indent=2)}")
        print(f"✅ Section creation ready - pending API permissions")
        
        return True
    
    def add_page_to_section(self, course_id: int, section_id: int, page_title: str, page_content: str) -> bool:
        """
        REQUIREMENT: Add pages to sections
        STATUS: Needs API permission expansion
        """
        print(f"\n📄 Adding page '{page_title}' to section {section_id}")
        print(f"⚠️  Note: Requires 'mod_page_create_content' permission")
        
        params = {
            'courseid': str(course_id),
            'sectionid': str(section_id),
            'modulename': 'page',
            'name': page_title,
            'content': page_content,
            'contentformat': '1'
        }
        
        print(f"📝 Would call: core_course_add_module")
        print(f"📋 Parameters: {json.dumps(params, indent=2)}")
        print(f"✅ Page creation ready - pending API permissions")
        
        return True
    
    def add_forum_to_section(self, course_id: int, section_id: int, forum_name: str, forum_description: str) -> bool:
        """
        REQUIREMENT: Add forum to sections
        STATUS: Needs API permission expansion
        """
        print(f"\n💬 Adding forum '{forum_name}' to section {section_id}")
        print(f"⚠️  Note: Requires 'mod_forum_create_forum' permission")
        
        params = {
            'courseid': str(course_id),
            'sectionid': str(section_id),
            'modulename': 'forum',
            'name': forum_name,
            'intro': forum_description,
            'introformat': '1',
            'type': 'general'  # General forum type
        }
        
        print(f"📝 Would call: core_course_add_module")
        print(f"📋 Parameters: {json.dumps(params, indent=2)}")
        print(f"✅ Forum creation ready - pending API permissions")
        
        return True

    # ========================================
    # PHASE 2: FORUM MANAGEMENT (WORKING!)
    # ========================================
    
    def get_course_forums(self, course_id: int) -> List[Dict]:
        """
        REQUIREMENT: Read students' forum replies
        STATUS: Partially working - can get course content, need forum-specific permissions
        """
        print(f"\n💬 Getting forums for course {course_id}")
        
        # First, get course contents (this works!)
        content = self._make_request('core_course_get_contents', {'courseid': str(course_id)})
        
        if content:
            forums = []
            for section in content:
                for module in section.get('modules', []):
                    if module.get('modname') == 'forum':
                        forums.append({
                            'id': module.get('id'),
                            'name': module.get('name'),
                            'url': module.get('url'),
                            'section': section.get('name', 'Unknown section')
                        })
            
            print(f"✅ Found {len(forums)} forums")
            for forum in forums:
                print(f"  📋 {forum['name']} (ID: {forum['id']})")
            
            return forums
        else:
            print(f"❌ Could not retrieve course content")
            return []
    
    def read_forum_discussions(self, forum_id: int) -> List[Dict]:
        """
        REQUIREMENT: Read students' replies to forum
        STATUS: Needs API permission expansion
        """
        print(f"\n📖 Reading discussions from forum {forum_id}")
        print(f"⚠️  Note: Requires 'mod_forum_get_forum_discussions' permission")
        
        # This would be the actual implementation
        params = {
            'forumid': str(forum_id),
            'sortby': 'timemodified',
            'sortdirection': 'DESC'
        }
        
        print(f"📝 Would call: mod_forum_get_forum_discussions")
        print(f"📋 Parameters: {json.dumps(params, indent=2)}")
        print(f"✅ Discussion reading ready - pending API permissions")
        
        # Simulated return data structure
        mock_discussions = [
            {
                'id': 123,
                'name': 'Week 1: Introduction Discussion',
                'timemodified': 1725984000,
                'usermodified': 456,
                'posts': [
                    {
                        'id': 789,
                        'discussion': 123,
                        'subject': 'My introduction',
                        'message': 'Hello everyone, I am excited to start this course...',
                        'userid': 456,
                        'created': 1725984000
                    }
                ]
            }
        ]
        
        print(f"📊 Mock data structure ready for implementation")
        return mock_discussions
    
    def add_forum_reply(self, discussion_id: int, subject: str, message: str) -> bool:
        """
        REQUIREMENT: Add reply to a message in a forum
        STATUS: Needs API permission expansion
        """
        print(f"\n💬 Adding reply to discussion {discussion_id}")
        print(f"📝 Subject: {subject}")
        print(f"💭 Message: {message[:50]}...")
        print(f"⚠️  Note: Requires 'mod_forum_add_discussion_post' permission")
        
        params = {
            'discussionid': str(discussion_id),
            'subject': subject,
            'message': message,
            'messageformat': '1'
        }
        
        print(f"📝 Would call: mod_forum_add_discussion_post")
        print(f"📋 Parameters: {json.dumps(params, indent=2)}")
        print(f"✅ Reply posting ready - pending API permissions")
        
        return True

    # ========================================
    # PHASE 3: QUIZ MANAGEMENT
    # ========================================
    
    def get_course_quizzes(self, course_id: int) -> List[Dict]:
        """
        REQUIREMENT: Read quiz answers and grade quiz
        STATUS: Needs API permission expansion
        """
        print(f"\n📊 Getting quizzes for course {course_id}")
        
        # First, try to find quizzes in course content (this works!)
        content = self._make_request('core_course_get_contents', {'courseid': str(course_id)})
        
        if content:
            quizzes = []
            for section in content:
                for module in section.get('modules', []):
                    if module.get('modname') == 'quiz':
                        quizzes.append({
                            'id': module.get('id'),
                            'name': module.get('name'),
                            'url': module.get('url'),
                            'section': section.get('name', 'Unknown section')
                        })
            
            print(f"✅ Found {len(quizzes)} quizzes")
            for quiz in quizzes:
                print(f"  📋 {quiz['name']} (ID: {quiz['id']})")
            
            if len(quizzes) == 0:
                print(f"ℹ️  No quizzes found in current course content")
            
            return quizzes
        else:
            print(f"❌ Could not retrieve course content")
            return []
    
    def read_quiz_answers(self, quiz_id: int) -> List[Dict]:
        """
        REQUIREMENT: Read quiz answers
        STATUS: Needs API permission expansion
        """
        print(f"\n📖 Reading quiz answers for quiz {quiz_id}")
        print(f"⚠️  Note: Requires 'mod_quiz_get_quiz_attempts' permission")
        
        params = {
            'quizid': str(quiz_id),
            'status': 'finished'
        }
        
        print(f"📝 Would call: mod_quiz_get_quiz_attempts")
        print(f"📋 Parameters: {json.dumps(params, indent=2)}")
        print(f"✅ Quiz reading ready - pending API permissions")
        
        # Mock data structure
        mock_attempts = [
            {
                'id': 789,
                'quiz': quiz_id,
                'userid': 456,
                'attempt': 1,
                'state': 'finished',
                'timestart': 1725984000,
                'timefinish': 1725985800,
                'sumgrades': 85.0,
                'responses': {
                    'question_1': 'Answer A',
                    'question_2': 'The answer is that...',
                    'question_3': 'Multiple choice: B'
                }
            }
        ]
        
        print(f"📊 Mock data structure ready for implementation")
        return mock_attempts
    
    def grade_quiz_attempt(self, attempt_id: int, grades: Dict[str, float]) -> bool:
        """
        REQUIREMENT: Grade quiz
        STATUS: Needs API permission expansion
        """
        print(f"\n📊 Grading quiz attempt {attempt_id}")
        print(f"📋 Grades: {grades}")
        print(f"⚠️  Note: Requires 'mod_quiz_save_attempt' and 'core_grades_update_grades' permissions")
        
        params = {
            'attemptid': str(attempt_id),
            'grades': grades,
            'finish': True
        }
        
        print(f"📝 Would call: mod_quiz_save_attempt")
        print(f"📋 Parameters: {json.dumps(params, indent=2)}")
        print(f"✅ Quiz grading ready - pending API permissions")
        
        return True

    # ========================================
    # DEMONSTRATION & TESTING
    # ========================================
    
    def demonstrate_current_capabilities(self, course_id: int = 99):
        """Demonstrate what currently works with our API permissions"""
        print(f"\n{'='*60}")
        print(f"🧪 DEMONSTRATING CURRENT API CAPABILITIES")
        print(f"{'='*60}")
        
        # Test 1: Get course details (WORKING!)
        print(f"\n✅ TEST 1: Get Course Details (WORKING)")
        params = {'options[ids][0]': str(course_id)}
        course_data = self._make_request('core_course_get_courses', params)
        
        if course_data and len(course_data) > 0:
            course = course_data[0]
            print(f"📚 Course: {course.get('fullname')}")
            print(f"🆔 ID: {course.get('id')}")
            print(f"📝 Short Name: {course.get('shortname')}")
        
        # Test 2: Get course content (WORKING!)
        print(f"\n✅ TEST 2: Get Course Content (WORKING)")
        content_data = self._make_request('core_course_get_contents', {'courseid': str(course_id)})
        
        if content_data:
            print(f"📊 Sections: {len(content_data)}")
            
            total_modules = 0
            module_types = {}
            
            for section in content_data:
                modules = section.get('modules', [])
                total_modules += len(modules)
                
                for module in modules:
                    mod_type = module.get('modname', 'unknown')
                    module_types[mod_type] = module_types.get(mod_type, 0) + 1
            
            print(f"📄 Total Modules: {total_modules}")
            print(f"🏷️  Module Types: {dict(module_types)}")
        
        # Test 3: Identify forums and quizzes (WORKING!)
        print(f"\n✅ TEST 3: Identify Course Components (WORKING)")
        forums = self.get_course_forums(course_id)
        quizzes = self.get_course_quizzes(course_id)
        
        print(f"💬 Forums found: {len(forums)}")
        print(f"📊 Quizzes found: {len(quizzes)}")
    
    def generate_implementation_roadmap(self):
        """Generate a detailed implementation roadmap"""
        print(f"\n{'='*60}")
        print(f"🗺️  IMPLEMENTATION ROADMAP")
        print(f"{'='*60}")
        
        roadmap = {
            "Phase 1: Content Management": {
                "status": "Needs API permissions",
                "functions_needed": [
                    "core_course_create_course_section",
                    "core_course_add_module", 
                    "mod_page_create_content",
                    "mod_forum_create_forum"
                ],
                "timeline": "2-3 weeks after permissions granted",
                "complexity": "Medium"
            },
            "Phase 2: Forum Reading & Writing": {
                "status": "Partially ready",
                "functions_needed": [
                    "mod_forum_get_forum_discussions",
                    "mod_forum_get_discussion_posts",
                    "mod_forum_add_discussion_post"
                ],
                "timeline": "1-2 weeks after permissions granted",
                "complexity": "Low-Medium"
            },
            "Phase 3: Quiz Management": {
                "status": "Needs API permissions",
                "functions_needed": [
                    "mod_quiz_get_quiz_attempts",
                    "mod_quiz_get_attempt_data",
                    "mod_quiz_save_attempt",
                    "core_grades_update_grades"
                ],
                "timeline": "3-4 weeks after permissions granted",
                "complexity": "High"
            }
        }
        
        for phase, details in roadmap.items():
            print(f"\n📋 {phase}")
            print(f"   Status: {details['status']}")
            print(f"   Timeline: {details['timeline']}")
            print(f"   Complexity: {details['complexity']}")
            print(f"   Functions needed:")
            for func in details['functions_needed']:
                print(f"     • {func}")
        
        return roadmap

def main():
    """Main demonstration function"""
    print(f"🚀 Moodle API Implementation Framework Demo")
    print(f"📚 Demonstrating proposed functions for ITO colleagues")
    
    framework = MoodleAPIFramework()
    
    # Show current working capabilities
    framework.demonstrate_current_capabilities(course_id=99)
    
    # Demonstrate proposed content management
    print(f"\n{'='*60}")
    print(f"🏗️  PROPOSED CONTENT MANAGEMENT FUNCTIONS")
    print(f"{'='*60}")
    
    framework.create_course_section(99, "Week 5: Advanced Topics", 5)
    framework.add_page_to_section(99, 5, "Lesson Plan", "This week we will cover...")
    framework.add_forum_to_section(99, 5, "Discussion: Advanced Topics", "Share your thoughts on...")
    
    # Demonstrate proposed forum management
    print(f"\n{'='*60}")
    print(f"💬 PROPOSED FORUM MANAGEMENT FUNCTIONS")
    print(f"{'='*60}")
    
    forums = framework.get_course_forums(99)
    if forums:
        forum_id = forums[0]['id']
        framework.read_forum_discussions(forum_id)
        framework.add_forum_reply(123, "Great discussion!", "Thank you for sharing your insights...")
    
    # Demonstrate proposed quiz management
    print(f"\n{'='*60}")
    print(f"📊 PROPOSED QUIZ MANAGEMENT FUNCTIONS")
    print(f"{'='*60}")
    
    quizzes = framework.get_course_quizzes(99)
    if quizzes:
        quiz_id = quizzes[0]['id']
        framework.read_quiz_answers(quiz_id)
        framework.grade_quiz_attempt(789, {'question_1': 8.5, 'question_2': 9.0, 'question_3': 7.5})
    
    # Generate roadmap
    roadmap = framework.generate_implementation_roadmap()
    
    print(f"\n🎯 NEXT STEPS FOR ITO COLLEAGUES:")
    print(f"1. Review proposed functions and provide feedback")
    print(f"2. Grant additional API permissions for sandbox testing")
    print(f"3. Schedule follow-up meeting to discuss implementation details")
    print(f"4. Begin phased development starting with highest priority functions")

if __name__ == "__main__":
    main()
