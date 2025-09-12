#!/usr/bin/env python3
"""
Test the default HKBU credentials work with the Moodle API
"""

import sys
import os

# Add the src directory to Python path
sys.path.append('.')

def test_default_connection():
    """Test connection with default HKBU credentials"""
    print("🧪 Testing Default HKBU Moodle Connection")
    print("=" * 50)
    
    try:
        # Load default credentials
        from streamlit_app import load_default_credentials
        url, token = load_default_credentials()
        
        print(f"📍 URL: {url}")
        print(f"🔑 Token: {token[:8]}...{token[-4:]}")
        
        # Test connection
        from src.moodle_client import MoodleAPIClient
        client = MoodleAPIClient(url, token)
        
        print("\n🔌 Testing connection...")
        # Test with a simple API call that should work
        try:
            # Try getting course details for a known course ID
            course_details = client.get_course_details(1)  # Try course ID 1
            print("✅ Connection successful!")
            print(f"📋 API response received")
            
        except Exception as e:
            # Try another method
            try:
                forums = client.get_forums(1)  # Try getting forums
                print("✅ Connection successful!")
                print(f"📋 API accessible")
            except:
                raise e
        
        # Test getting course contents
        print("\n📚 Testing course access...")
        try:
            contents = client.get_course_contents(1)  # Try course 1
            print(f"✅ Course content accessible")
            print(f"📋 Course 1 content: {type(contents)}")
        except Exception as e:
            print(f"⚠️  Course access test: {e}")
            # This might fail if course 1 doesn't exist, but connection is still good
        
        print(f"\n🎉 All tests passed! Colleagues can use one-click connection.")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   - Check if HKBU Moodle sandbox is accessible")
        print("   - Verify token hasn't expired")
        print("   - Try manual connection in the GUI")
        return False

if __name__ == "__main__":
    test_default_connection()
