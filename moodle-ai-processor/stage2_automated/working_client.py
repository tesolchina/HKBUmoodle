#!/usr/bin/env python3
"""
Working Moodle API Client

This client focuses on the functions that actually work with our current token permissions.
Based on diagnostic results: core_course_get_courses and core_course_get_contents work.
"""

import requests
import json
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path

class WorkingMoodleClient:
    """Moodle API client using only verified working functions"""
    
    def __init__(self):
        self.base_url = "https://moddw12-buelearning.hkbu.edu.hk"
        self.token = "eac84a6e8c353a7f88f424b14a340df4"
        self.api_endpoint = f"{self.base_url}/webservice/rest/server.php"
        
        print(f"🚀 Working Moodle API Client")
        print(f"📍 Base URL: {self.base_url}")
        print(f"🔑 Token: {self.token[:10]}...")
        print(f"⚡ Endpoint: {self.api_endpoint}")
    
    def _make_request(self, function: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
        """Make API request with error handling"""
        if params is None:
            params = {}
        
        request_params = {
            'wstoken': self.token,
            'wsfunction': function,
            'moodlewsrestformat': 'json'
        }
        request_params.update(params)
        
        try:
            print(f"📡 Calling: {function}")
            response = requests.get(self.api_endpoint, params=request_params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and 'exception' in data:
                    print(f"❌ API Error: {data['exception']} - {data.get('message', '')}")
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
    
    def get_course_by_id(self, course_id: int) -> Optional[Dict]:
        """Get course details by ID (VERIFIED WORKING)"""
        print(f"\n📚 Getting course details for ID: {course_id}")
        
        params = {
            'options[ids][0]': str(course_id)
        }
        
        result = self._make_request('core_course_get_courses', params)
        
        if result and isinstance(result, list) and len(result) > 0:
            course = result[0]
            print(f"📋 Course: {course.get('fullname', 'Unknown')}")
            print(f"🏷️  Short Name: {course.get('shortname', 'Unknown')}")
            print(f"🆔 ID Number: {course.get('idnumber', 'Unknown')}")
            return course
        else:
            print(f"❌ Course not found or error occurred")
            return None
    
    def get_all_courses(self) -> List[Dict]:
        """Get all accessible courses (VERIFIED WORKING)"""
        print(f"\n📚 Getting all accessible courses...")
        
        # Get courses without specifying IDs to get all accessible ones
        result = self._make_request('core_course_get_courses')
        
        if result and isinstance(result, list):
            print(f"✅ Found {len(result)} courses!")
            
            for i, course in enumerate(result[:5]):  # Show first 5
                print(f"  {i+1}. {course.get('fullname', 'Unknown')} (ID: {course.get('id', 'Unknown')})")
            
            if len(result) > 5:
                print(f"  ... and {len(result) - 5} more courses")
            
            return result
        else:
            print(f"❌ No courses found or error occurred")
            return []
    
    def get_course_content(self, course_id: int) -> List[Dict]:
        """Get course content structure (VERIFIED WORKING)"""
        print(f"\n📄 Getting course content for ID: {course_id}")
        
        params = {
            'courseid': str(course_id)
        }
        
        result = self._make_request('core_course_get_contents', params)
        
        if result and isinstance(result, list):
            print(f"✅ Found {len(result)} sections!")
            
            total_modules = 0
            for section in result:
                modules = section.get('modules', [])
                total_modules += len(modules)
            
            print(f"📊 Total modules: {total_modules}")
            
            # Show section summary
            for i, section in enumerate(result[:3]):  # Show first 3 sections
                section_name = section.get('name', f'Section {section.get("section", i+1)}')
                module_count = len(section.get('modules', []))
                print(f"  📂 {section_name}: {module_count} modules")
            
            if len(result) > 3:
                print(f"  ... and {len(result) - 3} more sections")
            
            return result
        else:
            print(f"❌ No content found or error occurred")
            return []
    
    def analyze_course_structure(self, course_id: int) -> Dict:
        """Comprehensive analysis of a course"""
        print(f"\n{'='*60}")
        print(f"📊 COMPREHENSIVE COURSE ANALYSIS")
        print(f"{'='*60}")
        
        # Get course details
        course = self.get_course_by_id(course_id)
        
        if not course:
            print(f"❌ Cannot analyze - course not found")
            return {}
        
        # Get course content
        content = self.get_course_content(course_id)
        
        # Analyze content structure
        analysis = {
            'course_info': course,
            'content_structure': content,
            'summary': {}
        }
        
        if content:
            # Count different types of modules
            module_types = {}
            total_modules = 0
            
            for section in content:
                for module in section.get('modules', []):
                    mod_type = module.get('modname', 'unknown')
                    module_types[mod_type] = module_types.get(mod_type, 0) + 1
                    total_modules += 1
            
            analysis['summary'] = {
                'total_sections': len(content),
                'total_modules': total_modules,
                'module_types': module_types
            }
            
            print(f"\n📊 CONTENT SUMMARY:")
            print(f"Sections: {len(content)}")
            print(f"Total Modules: {total_modules}")
            print(f"Module Types:")
            for mod_type, count in module_types.items():
                print(f"  - {mod_type}: {count}")
        
        return analysis
    
    def save_course_data(self, course_id: int, output_dir: str = "course_data"):
        """Save course data to files for further analysis"""
        print(f"\n💾 Saving course data for ID: {course_id}")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Get and save course analysis
        analysis = self.analyze_course_structure(course_id)
        
        if analysis:
            # Save complete analysis
            analysis_file = output_path / f"course_{course_id}_analysis.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Analysis saved to: {analysis_file}")
            
            # Save course info separately
            if 'course_info' in analysis:
                course_file = output_path / f"course_{course_id}_info.json"
                with open(course_file, 'w', encoding='utf-8') as f:
                    json.dump(analysis['course_info'], f, indent=2, ensure_ascii=False)
                
                print(f"✅ Course info saved to: {course_file}")
            
            # Save content structure separately
            if 'content_structure' in analysis:
                content_file = output_path / f"course_{course_id}_content.json"
                with open(content_file, 'w', encoding='utf-8') as f:
                    json.dump(analysis['content_structure'], f, indent=2, ensure_ascii=False)
                
                print(f"✅ Content structure saved to: {content_file}")
            
            # Create readable summary
            summary_file = output_path / f"course_{course_id}_summary.txt"
            with open(summary_file, 'w', encoding='utf-8') as f:
                course_info = analysis.get('course_info', {})
                summary = analysis.get('summary', {})
                
                f.write(f"COURSE ANALYSIS SUMMARY\n")
                f.write(f"{'='*50}\n\n")
                f.write(f"Course: {course_info.get('fullname', 'Unknown')}\n")
                f.write(f"Short Name: {course_info.get('shortname', 'Unknown')}\n")
                f.write(f"ID: {course_info.get('id', 'Unknown')}\n")
                f.write(f"ID Number: {course_info.get('idnumber', 'Unknown')}\n\n")
                
                f.write(f"CONTENT STATISTICS:\n")
                f.write(f"Total Sections: {summary.get('total_sections', 0)}\n")
                f.write(f"Total Modules: {summary.get('total_modules', 0)}\n\n")
                
                f.write(f"MODULE TYPES:\n")
                for mod_type, count in summary.get('module_types', {}).items():
                    f.write(f"  {mod_type}: {count}\n")
            
            print(f"✅ Summary saved to: {summary_file}")
            
            return True
        else:
            print(f"❌ No data to save")
            return False

def main():
    """Main function for testing the working client"""
    print(f"🚀 Working Moodle API Client Test")
    print(f"📚 Testing functions that passed diagnostics")
    
    client = WorkingMoodleClient()
    
    # Test 1: Get all courses
    print(f"\n" + "="*60)
    print(f"TEST 1: Get All Courses")
    print(f"="*60)
    
    all_courses = client.get_all_courses()
    
    if all_courses:
        # Test 2: Analyze first few courses
        test_course_ids = [course['id'] for course in all_courses[:3]]
        
        for course_id in test_course_ids:
            print(f"\n" + "="*60)
            print(f"TEST 2: Analyze Course {course_id}")
            print(f"="*60)
            
            # Analyze and save course data
            client.save_course_data(course_id)
    
    print(f"\n🎯 Testing complete!")
    print(f"📁 Check 'course_data' folder for saved results")

if __name__ == "__main__":
    main()
