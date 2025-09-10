#!/usr/bin/env python3
"""
Advanced Moodle API Diagnostics

This script performs comprehensive diagnostics to identify API access issues.
"""

import requests
import json
import sys
from urllib.parse import urljoin

class MoodleAPIDiagnostics:
    """Advanced diagnostics for Moodle API troubleshooting"""
    
    def __init__(self):
        self.base_url = "https://moddw12-buelearning.hkbu.edu.hk"
        self.token = "eac84a6e8c353a7f88f424b14a340df4"
        self.username = "lcadmin"
        self.password = "Lcadm#2025"
        
        print(f"🔍 Moodle API Diagnostics")
        print(f"📍 Target: {self.base_url}")
        print(f"🔑 Token: {self.token[:10]}...")
        print(f"👤 User: {self.username}")
        
    def test_basic_connectivity(self):
        """Test if we can reach the Moodle site at all"""
        print(f"\n{'='*60}")
        print(f"🧪 TEST 1: Basic Site Connectivity")
        print(f"{'='*60}")
        
        try:
            # Test main site
            response = requests.get(self.base_url, timeout=10)
            print(f"✅ Site reachable - Status: {response.status_code}")
            
            # Test login page
            login_url = f"{self.base_url}/login/index.php"
            login_response = requests.get(login_url, timeout=10)
            print(f"✅ Login page accessible - Status: {login_response.status_code}")
            
            # Test web service endpoint
            ws_url = f"{self.base_url}/webservice/rest/server.php"
            ws_response = requests.get(ws_url, timeout=10)
            print(f"📡 Web service endpoint - Status: {ws_response.status_code}")
            print(f"Response length: {len(ws_response.text)} chars")
            
            if ws_response.status_code == 200:
                print(f"Response preview: {ws_response.text[:200]}...")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Connectivity failed: {e}")
            return False
    
    def test_token_validity(self):
        """Test if the token format and basic usage is correct"""
        print(f"\n{'='*60}")
        print(f"🧪 TEST 2: Token Validity Check")
        print(f"{'='*60}")
        
        if len(self.token) != 32:
            print(f"⚠️  Token length unusual: {len(self.token)} chars (expected 32)")
        else:
            print(f"✅ Token length correct: 32 chars")
        
        # Test with minimal web service call
        api_url = f"{self.base_url}/webservice/rest/server.php"
        
        params = {
            'wstoken': self.token,
            'wsfunction': 'core_webservice_get_site_info',
            'moodlewsrestformat': 'json'
        }
        
        try:
            print(f"📡 Testing token with core_webservice_get_site_info...")
            response = requests.get(api_url, params=params, timeout=15)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"JSON Response: {json.dumps(data, indent=2)}")
                    
                    if 'exception' in data:
                        print(f"❌ API Error: {data['exception']}")
                        print(f"Error Code: {data.get('errorcode', 'Unknown')}")
                        print(f"Message: {data.get('message', 'Unknown')}")
                        return False
                    else:
                        print(f"✅ Token appears valid!")
                        return True
                        
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON response")
                    print(f"Raw response: {response.text}")
                    return False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False
    
    def test_alternative_functions(self):
        """Test different web service functions to identify permission issues"""
        print(f"\n{'='*60}")
        print(f"🧪 TEST 3: Alternative Function Tests")
        print(f"{'='*60}")
        
        api_url = f"{self.base_url}/webservice/rest/server.php"
        
        # List of functions to test (from most basic to more complex)
        test_functions = [
            'core_webservice_get_site_info',
            'core_course_get_courses',
            'core_user_get_users_by_field',
            'core_course_get_contents'
        ]
        
        results = {}
        
        for func in test_functions:
            print(f"\n🔍 Testing function: {func}")
            
            params = {
                'wstoken': self.token,
                'wsfunction': func,
                'moodlewsrestformat': 'json'
            }
            
            # Add specific parameters for certain functions
            if func == 'core_course_get_courses':
                params['options[ids][0]'] = '99'  # Test course ID
            elif func == 'core_user_get_users_by_field':
                params['field'] = 'username'
                params['values[0]'] = 'lcadmin'
            elif func == 'core_course_get_contents':
                params['courseid'] = '99'
            
            try:
                response = requests.get(api_url, params=params, timeout=15)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        if 'exception' in data:
                            print(f"❌ {func}: {data['exception']} - {data.get('message', '')}")
                            results[func] = 'error'
                        else:
                            print(f"✅ {func}: Success!")
                            results[func] = 'success'
                            # Show limited preview of successful responses
                            if isinstance(data, dict) and len(str(data)) < 300:
                                print(f"   Preview: {json.dumps(data, indent=2)[:200]}...")
                            elif isinstance(data, list) and len(data) > 0:
                                print(f"   Found {len(data)} items")
                    
                    except json.JSONDecodeError:
                        print(f"❌ {func}: Invalid JSON")
                        results[func] = 'json_error'
                        
                else:
                    print(f"❌ {func}: HTTP {response.status_code}")
                    results[func] = 'http_error'
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ {func}: Request failed - {e}")
                results[func] = 'request_error'
        
        return results
    
    def test_direct_login(self):
        """Test if we can login directly to get additional info"""
        print(f"\n{'='*60}")
        print(f"🧪 TEST 4: Direct Login Test")
        print(f"{'='*60}")
        
        # Create a session for cookie management
        session = requests.Session()
        
        try:
            # Get login page to obtain login token/sesskey
            login_url = f"{self.base_url}/login/index.php"
            print(f"📥 Getting login page...")
            
            login_page = session.get(login_url, timeout=10)
            print(f"Login page status: {login_page.status_code}")
            
            if login_page.status_code == 200:
                print(f"✅ Login page accessible")
                print(f"Page contains 'username': {'username' in login_page.text}")
                print(f"Page contains 'password': {'password' in login_page.text}")
                
                # This is mainly for informational purposes
                # We won't actually attempt login as it might affect the sandbox
                print(f"ℹ️  Login functionality detected but not attempted")
                print(f"   (Avoiding potential account lockout)")
                
                return True
            else:
                print(f"❌ Login page not accessible")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Login test failed: {e}")
            return False
    
    def generate_diagnostic_report(self):
        """Generate comprehensive diagnostic report"""
        print(f"\n{'='*80}")
        print(f"🔍 COMPREHENSIVE MOODLE API DIAGNOSTIC REPORT")
        print(f"{'='*80}")
        
        results = {}
        
        # Run all tests
        results['connectivity'] = self.test_basic_connectivity()
        results['token_validity'] = self.test_token_validity()
        results['function_tests'] = self.test_alternative_functions()
        results['login_test'] = self.test_direct_login()
        
        # Generate summary
        print(f"\n{'='*80}")
        print(f"📊 DIAGNOSTIC SUMMARY")
        print(f"{'='*80}")
        
        print(f"Site Connectivity: {'✅ PASS' if results['connectivity'] else '❌ FAIL'}")
        print(f"Token Validity: {'✅ PASS' if results['token_validity'] else '❌ FAIL'}")
        print(f"Login Page Access: {'✅ PASS' if results['login_test'] else '❌ FAIL'}")
        
        # Function test summary
        func_results = results['function_tests']
        success_count = sum(1 for status in func_results.values() if status == 'success')
        total_count = len(func_results)
        
        print(f"Function Tests: {success_count}/{total_count} successful")
        
        for func, status in func_results.items():
            status_icon = "✅" if status == 'success' else "❌"
            print(f"  {status_icon} {func}: {status}")
        
        # Recommendations
        print(f"\n🔧 RECOMMENDATIONS:")
        
        if not results['connectivity']:
            print(f"❌ Check network connection to HKBU")
            print(f"   - Verify you're on campus network or VPN")
            print(f"   - Check firewall settings")
        
        if not results['token_validity']:
            print(f"❌ Token issues detected:")
            print(f"   - Verify token is correct")
            print(f"   - Check if web services are enabled")
            print(f"   - Contact ITO to verify token permissions")
        
        if success_count == 0 and results['connectivity']:
            print(f"❌ All functions failed despite connectivity:")
            print(f"   - Web service may be disabled")
            print(f"   - Token may lack necessary permissions")
            print(f"   - User account may need additional capabilities")
        
        if success_count > 0:
            print(f"✅ Some functions work - API is partially functional")
            print(f"   - Focus on working functions for development")
            print(f"   - Request additional permissions for failing functions")
        
        # Save report
        report_data = {
            'timestamp': '2025-09-10',
            'base_url': self.base_url,
            'token_preview': self.token[:10] + '...',
            'results': results
        }
        
        report_file = 'diagnostic_report.json'
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Report saved to: {report_file}")
        
        return results

def main():
    """Main function"""
    print(f"🚀 Advanced Moodle API Diagnostics")
    print(f"🎯 Comprehensive troubleshooting for HKBU sandbox access")
    
    diagnostics = MoodleAPIDiagnostics()
    results = diagnostics.generate_diagnostic_report()
    
    # Final recommendation
    print(f"\n🎯 NEXT STEPS:")
    if any(status == 'success' for status in results.get('function_tests', {}).values()):
        print(f"✅ API is working! Continue with development using successful functions.")
    else:
        print(f"❌ API access blocked. Contact ITO colleagues with this diagnostic report.")

if __name__ == "__main__":
    main()
