#!/usr/bin/env python3
"""
Quick API Content Checker

Run this after each GUI content creation step to see what the API can detect.
"""

import requests
import json
from datetime import datetime

def check_course_content(course_id=99):
    """Check what content the API can see in the course"""
    
    base_url = "https://moddw12-buelearning.hkbu.edu.hk"
    token = "eac84a6e8c353a7f88f424b14a340df4"
    api_endpoint = f"{base_url}/webservice/rest/server.php"
    
    print(f"🔍 Checking Course Content via API")
    print(f"🎯 Course ID: {course_id}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"=" * 60)
    
    # Get course contents
    try:
        params = {
            'wstoken': token,
            'wsfunction': 'core_course_get_contents',
            'courseid': str(course_id),
            'moodlewsrestformat': 'json'
        }
        
        response = requests.get(api_endpoint, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, dict) and 'exception' in data:
                print(f"❌ API Error: {data['exception']}")
                return
            
            print(f"✅ API Response Successful!")
            print(f"📊 Total Sections: {len(data)}")
            print()
            
            total_modules = 0
            module_types = {}
            
            for i, section in enumerate(data):
                section_name = section.get('name', f'Section {i}')
                section_id = section.get('id', 'Unknown')
                modules = section.get('modules', [])
                
                print(f"📂 Section {i+1}: {section_name} (ID: {section_id})")
                print(f"   📄 Modules: {len(modules)}")
                
                if len(modules) == 0:
                    print(f"   🔹 (Empty section)")
                else:
                    for module in modules:
                        mod_name = module.get('name', 'Unknown')
                        mod_type = module.get('modname', 'unknown')
                        mod_id = module.get('id', 'Unknown')
                        mod_url = module.get('url', 'No URL')
                        
                        print(f"   🔹 {mod_name}")
                        print(f"      Type: {mod_type}")
                        print(f"      ID: {mod_id}")
                        print(f"      URL: {mod_url}")
                        
                        total_modules += 1
                        module_types[mod_type] = module_types.get(mod_type, 0) + 1
                
                print()
            
            print(f"📊 SUMMARY:")
            print(f"   Total modules: {total_modules}")
            print(f"   Module types: {dict(module_types)}")
            
            # Save detailed data for reference
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"course_content_check_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'course_id': course_id,
                    'sections': data,
                    'summary': {
                        'total_sections': len(data),
                        'total_modules': total_modules,
                        'module_types': module_types
                    }
                }, f, indent=2)
            
            print(f"💾 Detailed data saved to: {filename}")
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def check_specific_module_types():
    """Check for specific module types we're interested in"""
    
    print(f"\n🔍 Checking for Specific Module Types")
    print(f"=" * 60)
    
    # First get the content
    base_url = "https://moddw12-buelearning.hkbu.edu.hk"
    token = "eac84a6e8c353a7f88f424b14a340df4"
    api_endpoint = f"{base_url}/webservice/rest/server.php"
    
    params = {
        'wstoken': token,
        'wsfunction': 'core_course_get_contents',
        'courseid': '99',
        'moodlewsrestformat': 'json'
    }
    
    try:
        response = requests.get(api_endpoint, params=params, timeout=30)
        data = response.json()
        
        if isinstance(data, dict) and 'exception' in data:
            print(f"❌ Cannot get course content")
            return
        
        # Look for specific types
        forums = []
        quizzes = []
        pages = []
        resources = []
        
        for section in data:
            for module in section.get('modules', []):
                mod_type = module.get('modname', 'unknown')
                mod_info = {
                    'name': module.get('name', 'Unknown'),
                    'id': module.get('id', 'Unknown'),
                    'section': section.get('name', 'Unknown'),
                    'url': module.get('url', 'No URL')
                }
                
                if mod_type == 'forum':
                    forums.append(mod_info)
                elif mod_type == 'quiz':
                    quizzes.append(mod_info)
                elif mod_type == 'page':
                    pages.append(mod_info)
                elif mod_type == 'resource':
                    resources.append(mod_info)
        
        print(f"💬 FORUMS FOUND: {len(forums)}")
        for forum in forums:
            print(f"   🔹 {forum['name']} (ID: {forum['id']}) in {forum['section']}")
        
        print(f"\n📊 QUIZZES FOUND: {len(quizzes)}")
        for quiz in quizzes:
            print(f"   🔹 {quiz['name']} (ID: {quiz['id']}) in {quiz['section']}")
        
        print(f"\n📄 PAGES FOUND: {len(pages)}")
        for page in pages:
            print(f"   🔹 {page['name']} (ID: {page['id']}) in {page['section']}")
        
        print(f"\n📎 RESOURCES FOUND: {len(resources)}")
        for resource in resources:
            print(f"   🔹 {resource['name']} (ID: {resource['id']}) in {resource['section']}")
        
        # Test forum access if forums exist
        if forums:
            print(f"\n🧪 Testing Forum API Access")
            forum_id = forums[0]['id']
            
            forum_params = {
                'wstoken': token,
                'wsfunction': 'mod_forum_get_forum_discussions',
                'forumid': str(forum_id),
                'moodlewsrestformat': 'json'
            }
            
            forum_response = requests.get(api_endpoint, params=forum_params, timeout=30)
            forum_data = forum_response.json()
            
            if isinstance(forum_data, dict) and 'exception' in forum_data:
                print(f"❌ Forum API blocked: {forum_data['exception']}")
                print(f"💡 Need permission for: mod_forum_get_forum_discussions")
            else:
                print(f"✅ Forum API working!")
                print(f"📊 Discussions found: {len(forum_data) if isinstance(forum_data, list) else 'Unknown'}")
        
        # Test quiz access if quizzes exist
        if quizzes:
            print(f"\n🧪 Testing Quiz API Access")
            
            quiz_params = {
                'wstoken': token,
                'wsfunction': 'mod_quiz_get_quizzes_by_courses',
                'courseids[0]': '99',
                'moodlewsrestformat': 'json'
            }
            
            quiz_response = requests.get(api_endpoint, params=quiz_params, timeout=30)
            quiz_data = quiz_response.json()
            
            if isinstance(quiz_data, dict) and 'exception' in quiz_data:
                print(f"❌ Quiz API blocked: {quiz_data['exception']}")
                print(f"💡 Need permission for: mod_quiz_get_quizzes_by_courses")
            else:
                print(f"✅ Quiz API working!")
                print(f"📊 Quizzes found: {len(quiz_data) if isinstance(quiz_data, list) else 'Unknown'}")
        
    except Exception as e:
        print(f"❌ Request failed: {e}")

def main():
    """Main function"""
    print(f"🚀 Quick API Content Checker")
    print(f"📚 Use this after each GUI content creation step")
    print()
    
    # Check basic course content
    check_course_content(99)
    
    # Check specific module types
    check_specific_module_types()
    
    print(f"\n🎯 USAGE INSTRUCTIONS:")
    print(f"1. Create content via GUI in the sandbox")
    print(f"2. Run this script: python quick_api_check.py")
    print(f"3. Compare results before/after GUI changes")
    print(f"4. Document what the API can and cannot access")
    print(f"5. Use results as evidence for ITO permission requests")

if __name__ == "__main__":
    main()
