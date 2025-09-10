#!/usr/bin/env python3
"""
Targeted Moodle API Test

Testing specific course IDs that should be accessible in the sandbox.
"""

import requests
import json

class TargetedMoodleTest:
    """Test specific known course IDs"""
    
    def __init__(self):
        self.base_url = "https://moddw12-buelearning.hkbu.edu.hk"
        self.token = "eac84a6e8c353a7f88f424b14a340df4"
        self.api_endpoint = f"{self.base_url}/webservice/rest/server.php"
        
        print(f"🎯 Targeted Moodle API Test")
        print(f"📍 Base URL: {self.base_url}")
        print(f"🔑 Token: {self.token[:10]}...")
    
    def test_specific_course(self, course_id: int):
        """Test a specific course ID"""
        print(f"\n{'='*50}")
        print(f"🧪 Testing Course ID: {course_id}")
        print(f"{'='*50}")
        
        # Test 1: Get course details
        print(f"\n📚 Test 1: Get Course Details")
        params = {
            'wstoken': self.token,
            'wsfunction': 'core_course_get_courses',
            'moodlewsrestformat': 'json',
            'options[ids][0]': str(course_id)
        }
        
        try:
            response = requests.get(self.api_endpoint, params=params, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and 'exception' in data:
                    print(f"❌ Error: {data['exception']} - {data.get('message', '')}")
                    return False
                elif isinstance(data, list) and len(data) > 0:
                    course = data[0]
                    print(f"✅ Course Found!")
                    print(f"   Name: {course.get('fullname', 'Unknown')}")
                    print(f"   Short Name: {course.get('shortname', 'Unknown')}")
                    print(f"   ID: {course.get('id', 'Unknown')}")
                    print(f"   Category ID: {course.get('categoryid', 'Unknown')}")
                    
                    # Test 2: Get course content
                    print(f"\n📄 Test 2: Get Course Content")
                    content_params = {
                        'wstoken': self.token,
                        'wsfunction': 'core_course_get_contents',
                        'moodlewsrestformat': 'json',
                        'courseid': str(course_id)
                    }
                    
                    content_response = requests.get(self.api_endpoint, params=content_params, timeout=30)
                    
                    if content_response.status_code == 200:
                        content_data = content_response.json()
                        
                        if isinstance(content_data, dict) and 'exception' in content_data:
                            print(f"❌ Content Error: {content_data['exception']} - {content_data.get('message', '')}")
                        elif isinstance(content_data, list):
                            print(f"✅ Content Found!")
                            print(f"   Sections: {len(content_data)}")
                            
                            total_modules = 0
                            module_types = {}
                            
                            for section in content_data:
                                modules = section.get('modules', [])
                                total_modules += len(modules)
                                
                                for module in modules:
                                    mod_type = module.get('modname', 'unknown')
                                    module_types[mod_type] = module_types.get(mod_type, 0) + 1
                            
                            print(f"   Total Modules: {total_modules}")
                            print(f"   Module Types: {dict(module_types)}")
                            
                            # Save detailed data
                            course_data = {
                                'course_info': course,
                                'content_structure': content_data,
                                'analysis': {
                                    'total_sections': len(content_data),
                                    'total_modules': total_modules,
                                    'module_types': module_types
                                }
                            }
                            
                            filename = f"course_{course_id}_complete_data.json"
                            with open(filename, 'w', encoding='utf-8') as f:
                                json.dump(course_data, f, indent=2, ensure_ascii=False)
                            
                            print(f"💾 Data saved to: {filename}")
                            return True
                    else:
                        print(f"❌ Content request failed: {content_response.status_code}")
                        return False
                else:
                    print(f"❌ Unexpected response format")
                    return False
            else:
                print(f"❌ Request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return False
    
    def scan_course_range(self, start_id: int = 1, end_id: int = 200):
        """Scan a range of course IDs to find accessible ones"""
        print(f"\n🔍 Scanning course IDs from {start_id} to {end_id}")
        
        accessible_courses = []
        
        for course_id in range(start_id, end_id + 1):
            print(f"Testing ID {course_id}...", end=" ")
            
            params = {
                'wstoken': self.token,
                'wsfunction': 'core_course_get_courses',
                'moodlewsrestformat': 'json',
                'options[ids][0]': str(course_id)
            }
            
            try:
                response = requests.get(self.api_endpoint, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, list) and len(data) > 0:
                        course = data[0]
                        if 'fullname' in course:
                            print(f"✅ FOUND: {course.get('shortname', 'Unknown')}")
                            accessible_courses.append({
                                'id': course_id,
                                'fullname': course.get('fullname', 'Unknown'),
                                'shortname': course.get('shortname', 'Unknown')
                            })
                        else:
                            print(f"❌")
                    else:
                        print(f"❌")
                else:
                    print(f"❌")
                    
            except Exception:
                print(f"❌")
            
            # Small delay to avoid overwhelming the server
            import time
            time.sleep(0.1)
        
        print(f"\n📊 Scan Results:")
        print(f"Found {len(accessible_courses)} accessible courses:")
        
        for course in accessible_courses:
            print(f"  ID {course['id']}: {course['shortname']} - {course['fullname']}")
        
        # Save scan results
        with open('accessible_courses.json', 'w', encoding='utf-8') as f:
            json.dump(accessible_courses, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: accessible_courses.json")
        return accessible_courses

def main():
    """Main function"""
    print(f"🚀 Targeted Moodle API Testing")
    
    tester = TargetedMoodleTest()
    
    # Test some common course IDs first
    test_ids = [1, 2, 3, 99, 100, 180]
    
    print(f"\n📚 Testing Common Course IDs")
    working_courses = []
    
    for course_id in test_ids:
        if tester.test_specific_course(course_id):
            working_courses.append(course_id)
    
    print(f"\n📊 Summary:")
    print(f"Working courses: {working_courses}")
    
    if not working_courses:
        print(f"\n🔍 No courses worked with common IDs, scanning range 1-50...")
        accessible = tester.scan_course_range(1, 50)
        
        if accessible:
            print(f"\n✅ Found accessible courses! Testing the first one in detail...")
            tester.test_specific_course(accessible[0]['id'])

if __name__ == "__main__":
    main()
