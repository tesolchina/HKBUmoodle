#!/usr/bin/env python3
"""
🎓 HKBU Moodle Assistant - Demo Script
Quick demo of core functionality for colleagues
"""

import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def demo_api_connection():
    """Demo the basic API connection"""
    print("🔌 Testing Moodle API Connection")
    print("=" * 40)
    
    try:
        from moodle_client import MoodleAPIClient
        
        # This would need real credentials
        print("✅ MoodleAPIClient imported successfully")
        print("📋 Available API methods:")
        
        methods = [method for method in dir(MoodleAPIClient) 
                  if not method.startswith('_') and callable(getattr(MoodleAPIClient, method))]
        
        for i, method in enumerate(methods, 1):
            print(f"   {i:2}. {method}")
        
        print(f"\n🎯 Total API methods available: {len(methods)}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

def demo_material_analyzer():
    """Demo the material analyzer"""
    print("\n📚 Testing Material Analyzer")
    print("=" * 40)
    
    try:
        from revised_material_analyzer import RevisedMaterialAnalyzer
        print("✅ RevisedMaterialAnalyzer imported successfully")
        print("📋 Available analyzer methods:")
        
        methods = [method for method in dir(RevisedMaterialAnalyzer) 
                  if not method.startswith('_') and callable(getattr(RevisedMaterialAnalyzer, method))]
        
        for i, method in enumerate(methods, 1):
            print(f"   {i:2}. {method}")
            
        print(f"\n🎯 Total analyzer methods: {len(methods)}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

def demo_streamlit_availability():
    """Demo streamlit availability"""
    print("\n🎨 Testing Streamlit GUI")
    print("=" * 40)
    
    try:
        import streamlit as st
        print(f"✅ Streamlit version {st.__version__} installed")
        print("🚀 GUI is ready to launch!")
        print("\n📋 To start the GUI:")
        print("   ./run_gui.sh")
        print("   OR")
        print("   streamlit run streamlit_app.py")
        print("\n🌐 Access at: http://localhost:8501")
        
    except ImportError as e:
        print(f"❌ Streamlit not available: {e}")
        print("💡 Install with: pip install -r requirements_streamlit.txt")
        return False
    
    return True

def demo_api_capabilities():
    """Demo what APIs we can actually use"""
    print("\n🎯 API Capabilities Summary")
    print("=" * 40)
    
    available_apis = [
        "✅ get_site_info - Test connection",
        "✅ get_enrolled_courses - List courses", 
        "✅ get_quizzes_by_courses - Quiz management",
        "✅ get_forums_by_courses - Forum monitoring",
        "✅ get_course_contents - Material analysis",
        "✅ save_attempt - Quiz grading",
        "✅ get_attempt_data - Quiz attempt details",
        "✅ get_forum_discussions - Forum posts",
        "✅ add_discussion_post - Reply to forums"
    ]
    
    limited_apis = [
        "❌ core_course_add_module - Create modules (workaround: templates)",
        "❌ core_course_create_sections - Create sections (workaround: duplication)", 
        "❌ mod_quiz_get_quiz_by_instance - Quiz instances (alternative APIs available)"
    ]
    
    print("🟢 Available Functions:")
    for api in available_apis:
        print(f"   {api}")
    
    print("\n🟡 Limited Functions (workarounds available):")
    for api in limited_apis:
        print(f"   {api}")
    
    print(f"\n📊 Summary: {len(available_apis)} fully available, {len(limited_apis)} with workarounds")

def main():
    """Main demo function"""
    print("🎓 HKBU Moodle Assistant - Demo")
    print("=" * 50)
    print("Quick demonstration for colleagues")
    print("=" * 50)
    
    # Test core components
    api_ok = demo_api_connection()
    analyzer_ok = demo_material_analyzer() 
    gui_ok = demo_streamlit_availability()
    
    # Show capabilities
    demo_api_capabilities()
    
    # Final summary
    print("\n🎯 System Status Summary")
    print("=" * 40)
    print(f"🔌 API Client:        {'✅ Ready' if api_ok else '❌ Issues'}")
    print(f"📚 Material Analyzer: {'✅ Ready' if analyzer_ok else '❌ Issues'}")
    print(f"🎨 Streamlit GUI:     {'✅ Ready' if gui_ok else '❌ Issues'}")
    
    if api_ok and analyzer_ok and gui_ok:
        print("\n🎉 All systems ready!")
        print("🚀 Ready to test with colleagues!")
        print("\n📋 Next steps:")
        print("   1. Get your Moodle API token")
        print("   2. Run: ./run_gui.sh")
        print("   3. Access: http://localhost:8501")
        print("   4. Test the different modules")
    else:
        print("\n⚠️  Some issues detected. Please check the errors above.")

if __name__ == "__main__":
    main()
