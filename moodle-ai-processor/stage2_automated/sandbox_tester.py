#!/usr/bin/env python3
"""
Moodle Sandbox API Tester

This script tests the Moodle API connection using the sandbox environment.
Based on the examples provided by ITO colleagues.
"""

import requests
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

class MoodleSandboxTester:
    def __init__(self):
        """Initialize with sandbox credentials"""
        self.base_url = "https://moddw12-buelearning.hkbu.edu.hk"
        self.token = "eac84a6e8c353a7f88f424b14a340df4"
        self.api_endpoint = f"{self.base_url}/webservice/rest/server.php"
        
        print(f"🔧 Moodle Sandbox API Tester")
        print(f"📍 Base URL: {self.base_url}")
        print(f"🔑 Token: {self.token[:20]}...")
        print(f"⚡ API Endpoint: {self.api_endpoint}")
    
    def make_api_call(self, function: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
        """Make a call to the Moodle API"""
        if params is None:
            params = {}
        
        # Base parameters
        request_params = {
            'wstoken': self.token,
            'wsfunction': function,
            'moodlewsrestformat': 'json'
        }
        
        # Add custom parameters
        request_params.update(params)
        
        print(f"\n📡 Making API call: {function}")
        print(f"🔗 Full URL: {self.api_endpoint}")
        print(f"📝 Parameters: {json.dumps(request_params, indent=2)}")
        
        try:
            response = requests.get(self.api_endpoint, params=request_params, timeout=30)
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Response received ({len(json.dumps(data))} characters)")
                    return data
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    print(f"Raw response: {response.text[:500]}...")
                    return None
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response text: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def test_basic_connection(self):
        """Test basic API connection"""
        print(f"\n{'='*60}")
        print(f"🧪 TEST 1: Basic Connection - Get Site Info")
        print(f"{'='*60}")
        
        result = self.make_api_call('core_webservice_get_site_info')
        
        if result:
            if 'sitename' in result:
                print(f"✅ Connection successful!")
                print(f"📍 Site Name: {result.get('sitename', 'Unknown')}")
                print(f"🌐 Site URL: {result.get('siteurl', 'Unknown')}")
                print(f"📱 Moodle Version: {result.get('release', 'Unknown')}")
                print(f"👤 User Full Name: {result.get('userfullname', 'Unknown')}")
                return True
            else:
                print(f"❌ Unexpected response format")
                print(f"Response: {json.dumps(result, indent=2)}")
                return False
        else:
            print(f"❌ Connection failed")
            return False
    
    def test_get_course_details(self, course_id: int = 99):
        """Test getting course details by ID"""
        print(f"\n{'='*60}")
        print(f"🧪 TEST 2: Get Course Details (ID: {course_id})")
        print(f"{'='*60}")
        
        params = {
            'options[ids][0]': course_id
        }
        
        result = self.make_api_call('core_course_get_courses', params)
        
        if result and isinstance(result, list) and len(result) > 0:
            course = result[0]
            print(f"✅ Course found!")
            print(f"📚 Course Name: {course.get('fullname', 'Unknown')}")
            print(f"🔢 Course ID: {course.get('id', 'Unknown')}")
            print(f"📝 Short Name: {course.get('shortname', 'Unknown')}")
            print(f"📅 Start Date: {course.get('startdate', 'Unknown')}")
            return course
        else:
            print(f"❌ Course not found or error occurred")
            if result:
                print(f"Response: {json.dumps(result, indent=2)}")
            return None
    
    def test_get_course_by_idnumber(self, idnumber: str = "2024;S2;UCLC1009;1;"):
        """Test getting course by HKBU ID number"""
        print(f"\n{'='*60}")
        print(f"🧪 TEST 3: Get Course by ID Number ({idnumber})")
        print(f"{'='*60}")
        
        params = {
            'field': 'idnumber',
            'value': idnumber
        }
        
        result = self.make_api_call('core_course_get_courses_by_field', params)
        
        if result and 'courses' in result and len(result['courses']) > 0:
            course = result['courses'][0]
            print(f"✅ Course found by ID number!")
            print(f"📚 Course Name: {course.get('fullname', 'Unknown')}")
            print(f"🔢 Course ID: {course.get('id', 'Unknown')}")
            print(f"🏷️ ID Number: {course.get('idnumber', 'Unknown')}")
            return course
        else:
            print(f"❌ Course not found by ID number")
            if result:
                print(f"Response: {json.dumps(result, indent=2)}")
            return None
    
    def test_get_enrolled_users(self, course_id: int = 180):
        """Test getting enrolled users in a course"""
        print(f"\n{'='*60}")
        print(f"🧪 TEST 4: Get Enrolled Users (Course ID: {course_id})")
        print(f"{'='*60}")
        
        params = {
            'courseid': course_id
        }
        
        result = self.make_api_call('core_enrol_get_enrolled_users', params)
        
        if result and isinstance(result, list):
            print(f"✅ Found {len(result)} enrolled users!")
            for i, user in enumerate(result[:5]):  # Show first 5 users
                print(f"👤 User {i+1}: {user.get('fullname', 'Unknown')} (ID: {user.get('id', 'Unknown')})")
                print(f"   📧 Email: {user.get('email', 'Unknown')}")
                print(f"   🎭 Roles: {', '.join([role.get('shortname', 'Unknown') for role in user.get('roles', [])])}")
            
            if len(result) > 5:
                print(f"   ... and {len(result) - 5} more users")
            
            return result
        else:
            print(f"❌ No users found or error occurred")
            if result:
                print(f"Response: {json.dumps(result, indent=2)}")
            return None
    
    def test_get_course_contents(self, course_id: int = 99):
        """Test getting course contents"""
        print(f"\n{'='*60}")
        print(f"🧪 TEST 5: Get Course Contents (Course ID: {course_id})")
        print(f"{'='*60}")
        
        params = {
            'courseid': course_id
        }
        
        result = self.make_api_call('core_course_get_contents', params)
        
        if result and isinstance(result, list):
            print(f"✅ Found {len(result)} course sections!")
            for i, section in enumerate(result[:3]):  # Show first 3 sections
                print(f"📂 Section {i+1}: {section.get('name', 'Unnamed')}")
                print(f"   🔢 Section ID: {section.get('id', 'Unknown')}")
                print(f"   📋 Modules: {len(section.get('modules', []))}")
                
                # Show first few modules in each section
                modules = section.get('modules', [])
                for j, module in enumerate(modules[:2]):
                    print(f"     📄 Module {j+1}: {module.get('name', 'Unnamed')} ({module.get('modname', 'unknown')})")
                
                if len(modules) > 2:
                    print(f"     ... and {len(modules) - 2} more modules")
                print()
            
            if len(result) > 3:
                print(f"... and {len(result) - 3} more sections")
            
            return result
        else:
            print(f"❌ No course contents found or error occurred")
            if result:
                print(f"Response: {json.dumps(result, indent=2)}")
            return None
    
    def test_get_user_courses(self, user_id: int = 3):
        """Test getting courses for a specific user"""
        print(f"\n{'='*60}")
        print(f"🧪 TEST 6: Get User Courses (User ID: {user_id})")
        print(f"{'='*60}")
        
        params = {
            'userid': user_id
        }
        
        result = self.make_api_call('core_enrol_get_users_courses', params)
        
        if result and isinstance(result, list):
            print(f"✅ User is enrolled in {len(result)} courses!")
            for i, course in enumerate(result[:5]):  # Show first 5 courses
                print(f"📚 Course {i+1}: {course.get('fullname', 'Unknown')}")
                print(f"   🔢 Course ID: {course.get('id', 'Unknown')}")
                print(f"   📝 Short Name: {course.get('shortname', 'Unknown')}")
            
            if len(result) > 5:
                print(f"... and {len(result) - 5} more courses")
            
            return result
        else:
            print(f"❌ No courses found for user or error occurred")
            if result:
                print(f"Response: {json.dumps(result, indent=2)}")
            return None
    
    def run_all_tests(self):
        """Run all API tests"""
        print(f"\n🚀 Starting Moodle Sandbox API Tests")
        print(f"📍 Sandbox URL: {self.base_url}")
        print(f"⚠️  Note: These tests require HKBU campus network access")
        
        test_results = {}
        
        # Test 1: Basic connection
        test_results['basic_connection'] = self.test_basic_connection()
        
        if test_results['basic_connection']:
            # Test 2: Get course details
            course = self.test_get_course_details()
            test_results['course_details'] = course is not None
            
            # Test 3: Get course by ID number  
            course_by_id = self.test_get_course_by_idnumber()
            test_results['course_by_idnumber'] = course_by_id is not None
            
            # Test 4: Get enrolled users
            users = self.test_get_enrolled_users()
            test_results['enrolled_users'] = users is not None
            
            # Test 5: Get course contents
            contents = self.test_get_course_contents()
            test_results['course_contents'] = contents is not None
            
            # Test 6: Get user courses
            user_courses = self.test_get_user_courses()
            test_results['user_courses'] = user_courses is not None
        else:
            print(f"\n❌ Basic connection failed - skipping other tests")
        
        # Summary
        print(f"\n{'='*60}")
        print(f"📊 TEST SUMMARY")
        print(f"{'='*60}")
        
        passed = sum(test_results.values())
        total = len(test_results)
        
        for test_name, passed_status in test_results.items():
            status = "✅ PASS" if passed_status else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
        
        if passed == total:
            print(f"🎉 All tests passed! Moodle API is working correctly.")
        elif passed > 0:
            print(f"⚠️  Some tests failed. Check network connection and API permissions.")
        else:
            print(f"❌ All tests failed. Verify network access and credentials.")
        
        return test_results

def main():
    """Main function"""
    print(f"🔧 Moodle Sandbox API Tester")
    print(f"📚 Testing API connection to HKBU Moodle sandbox")
    print(f"⚠️  Note: This requires HKBU campus network access or VPN")
    
    tester = MoodleSandboxTester()
    results = tester.run_all_tests()
    
    # Save results for reference
    results_file = Path(__file__).parent / 'test_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Test results saved to: {results_file}")

if __name__ == "__main__":
    main()
