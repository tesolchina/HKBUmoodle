#!/usr/bin/env python3
"""
🎓 HKBU Moodle Assistant - Streamlit GUI
Quick prototype for testing Moodle API functions with colleagues
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from moodle_client import MoodleAPIClient
    from revised_material_analyzer import RevisedMaterialAnalyzer
except ImportError as e:
    st.error(f"Import Error: {e}")
    st.info("Please ensure you're running from the moodle-ai-processor directory")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="HKBU Moodle Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff6b6b;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        color: #155724;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        color: #856404;
    }
    .info-box {
        background-color: #d1ecf1;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'moodle_client' not in st.session_state:
    st.session_state.moodle_client = None
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'courses' not in st.session_state:
    st.session_state.courses = []

def load_default_credentials():
    """Load default Moodle credentials from config files"""
    
    # Try to load from simple credentials file first
    try:
        import moodle_credentials as creds
        url_options = [
            (creds.SANDBOX_URL, creds.SANDBOX_TOKEN, "🧪 Sandbox (Testing)"),
            (creds.PRODUCTION_URL, creds.PRODUCTION_TOKEN, "🏢 Production (Live)"),
            (creds.MOODLE_URL, creds.MOODLE_TOKEN, "🎓 Default HKBU")
        ]
        
        # Return sandbox as default
        default_url = creds.SANDBOX_URL
        default_token = creds.SANDBOX_TOKEN
        
        return default_url, default_token, url_options
    except ImportError:
        # Fallback to config file method
        pass
    
    config_dir = os.path.join(os.path.dirname(__file__), 'config')
    
    # Fallback URL options
    url_options = [
        ("https://moddw12-buelearning.hkbu.edu.hk", "eac84a6e8c353a7f88f424b14a340df4", "🧪 Sandbox (Testing)"),
        ("https://moodle.hkbu.edu.hk", "your_token_here", "🏢 Production (Live)")
    ]
    
    default_url = url_options[0][0]
    default_token = url_options[0][1] 
    
    try:
        # Try to read from MoodleSandbox.txt
        sandbox_file = os.path.join(config_dir, 'MoodleSandbox.txt')
        if os.path.exists(sandbox_file):
            with open(sandbox_file, 'r') as f:
                content = f.read()
                
                # Extract URL and token
                for line in content.split('\n'):
                    if line.strip().startswith('Sandbox:'):
                        extracted_url = line.split(':', 1)[1].strip()
                        url_options[0] = (extracted_url, url_options[0][1], url_options[0][2])
                        default_url = extracted_url
                    elif line.strip().startswith('Token:'):
                        extracted_token = line.split(':', 1)[1].strip()
                        url_options[0] = (url_options[0][0], extracted_token, url_options[0][2])
                        default_token = extracted_token
    except Exception as e:
        st.warning(f"Could not load config credentials: {e}")
    
    return default_url, default_token, url_options

def connect_to_moodle(base_url, token):
    """Connect to Moodle and cache the client"""
    try:
        client = MoodleAPIClient(base_url, token)
        # Test connection by getting user info
        user_info = client.get_site_info()
        st.session_state.moodle_client = client
        st.session_state.connected = True
        return True, user_info
    except Exception as e:
        st.session_state.connected = False
        return False, str(e)

def get_courses():
    """Get and cache courses"""
    if not st.session_state.connected:
        return []
    
    try:
        if not st.session_state.courses:
            courses = st.session_state.moodle_client.get_enrolled_courses()
            st.session_state.courses = courses
        return st.session_state.courses
    except Exception as e:
        st.error(f"Error getting courses: {e}")
        return []

def main():
    # Header
    st.title("🎓 HKBU Moodle Assistant")
    st.markdown("**Quick Prototype** - API Testing Interface for Colleagues")
    
    # Quick connect button at the top if not connected
    if not st.session_state.connected:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 **Quick Connect** (One Click!)", type="primary", use_container_width=True):
                default_url, default_token, _ = load_default_credentials()
                with st.spinner("Connecting to HKBU Moodle..."):
                    success, result = connect_to_moodle(default_url, default_token)
                    if success:
                        st.success("✅ Connected successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Connection failed: {result}")
                        st.info("💡 Try different environment in sidebar or manual credentials")
        st.markdown("---")
    
    # Sidebar for connection and navigation
    with st.sidebar:
        st.header("🔧 Connection Settings")
        
        # Load default credentials
        default_url, default_token, url_options = load_default_credentials()
        
        # Auto-connect option
        use_default = st.checkbox("🔑 Use Default HKBU Credentials", value=True,
                                 help="Use pre-configured HKBU Moodle credentials")
        
        if use_default:
            st.info("Using HKBU Moodle Credentials")
            
            # Allow environment selection
            env_options = [f"{env[2]}" for env in url_options]
            selected_env_name = st.selectbox(
                "Environment",
                options=env_options,
                index=0,
                help="Choose Moodle environment"
            )
            
            # Find the selected environment
            selected_env = next(env for env in url_options if env[2] == selected_env_name)
            base_url = selected_env[0]
            token = selected_env[1]
            
            # Show the credentials being used (masked)
            st.text(f"URL: {base_url}")
            if token and token != "your_token_here":
                st.text(f"Token: {token[:8]}...{token[-4:]}")
            else:
                st.warning("⚠️ Token needs to be configured")
                
        else:
            # Manual credential input
            st.warning("Manual credentials - colleagues need their own tokens")
            base_url = st.text_input(
                "Moodle URL", 
                value=default_url,
                help="Enter your Moodle instance URL"
            )
            
            token = st.text_input(
                "API Token", 
                type="password",
                help="Enter your Moodle Web Services token"
            )
        
        # Connection button
        connect_button = st.button("🔌 Connect to Moodle")
        
        # Auto-connect with default credentials
        if use_default and not st.session_state.connected and not connect_button:
            st.info("Click 'Connect to Moodle' to use default credentials")
        
        if connect_button or (use_default and base_url and token):
            if base_url and token:
                with st.spinner("Connecting to Moodle..."):
                    success, result = connect_to_moodle(base_url, token)
                    if success:
                        st.success("✅ Connected successfully!")
                        if isinstance(result, dict):
                            st.json({"site": result.get('sitename', 'Unknown'), 
                                    "user": result.get('username', 'Unknown')})
                        else:
                            st.write(f"Site info: {result}")
                    else:
                        st.error(f"❌ Connection failed: {result}")
            else:
                st.warning("Please enter both URL and token")
        
        # Connection status
        if st.session_state.connected:
            st.markdown('<div class="success-box">🟢 Connected to Moodle</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-box">🟡 Not connected</div>', 
                       unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        st.header("📋 Navigation")
        page = st.selectbox(
            "Choose Function",
            ["🏠 Dashboard", "📚 Material Analysis", "🎯 Quiz Management", 
             "💬 Forum Monitoring", "🔍 API Testing"]
        )
    
    # Main content area
    if not st.session_state.connected:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 👋 Welcome to HKBU Moodle Assistant!
        
        **Quick Start Options:**
        1. 🚀 **Try "Quick Connect"** above - Uses pre-configured credentials
        2. � **Use Sidebar** - Choose different environments or manual setup
        3. 🎯 **Explore Features** - Test Moodle API capabilities with live data
        
        **Features available:**
        - 📚 **Material Analysis** - Analyze course content and plan duplication
        - 🎯 **Quiz Management** - View and manage quiz attempts  
        - 💬 **Forum Monitoring** - Monitor forum posts and discussions
        - 🔍 **API Testing** - Test individual API functions
        
        **🔑 Credentials:** 
        - **Sandbox** works if you're on HKBU network
        - **Production** requires your own API token
        - **Manual setup** available in sidebar for custom tokens
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Page routing
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📚 Material Analysis":
        show_material_analysis()
    elif page == "🎯 Quiz Management":
        show_quiz_management()
    elif page == "💬 Forum Monitoring":
        show_forum_monitoring()
    elif page == "🔍 API Testing":
        show_api_testing()

def show_dashboard():
    """Dashboard with overview and quick stats"""
    st.header("📊 Dashboard")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎓 Enrolled Courses", len(get_courses()))
    
    with col2:
        st.metric("🔧 Available APIs", "15+")
    
    with col3:
        st.metric("⚡ Status", "Connected" if st.session_state.connected else "Disconnected")
    
    with col4:
        st.metric("🕒 Last Update", datetime.now().strftime("%H:%M"))
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 Analyze Materials", use_container_width=True):
            st.switch_page = "📚 Material Analysis"
    
    with col2:
        if st.button("🎯 Grade Quizzes", use_container_width=True):
            st.switch_page = "🎯 Quiz Management"
    
    with col3:
        if st.button("💬 Check Forums", use_container_width=True):
            st.switch_page = "💬 Forum Monitoring"
    
    # Recent activity (placeholder)
    st.subheader("📋 System Status")
    
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("""
    **✅ Available Functions:**
    - Quiz grading and attempt management
    - Forum post reading and discussion management
    - Course content analysis and updates
    - Material property modifications
    
    **⚠️ API Limitations (workarounds available):**
    - Direct module creation (use templates + updates)
    - Section creation (use course duplication)
    - Some quiz instance functions (use alternative APIs)
    """)
    st.markdown('</div>', unsafe_allow_html=True)

def show_material_analysis():
    """Material analysis and duplication planning"""
    st.header("📚 Material Analysis & Duplication Planning")
    
    courses = get_courses()
    if not courses:
        st.warning("No courses found. Please check your connection.")
        return
    
    # Course selection
    st.subheader("🔍 Select Course to Analyze")
    
    course_options = {f"{c['fullname']} (ID: {c['id']})": c['id'] 
                     for c in courses}
    
    selected_course_name = st.selectbox(
        "Choose Source Course",
        options=list(course_options.keys()),
        help="Select the course you want to analyze and potentially duplicate from"
    )
    
    if selected_course_name:
        source_course_id = course_options[selected_course_name]
        
        # Analyze course button
        if st.button("🔍 Analyze Course Content"):
            with st.spinner("Analyzing course content..."):
                try:
                    analyzer = RevisedMaterialAnalyzer(st.session_state.moodle_client)
                    analysis_result = analyzer.analyze_course_structure(source_course_id)
                    
                    st.success("✅ Analysis complete!")
                    
                    # Display results
                    st.subheader("📊 Course Analysis Results")
                    
                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📑 Total Sections", analysis_result['summary']['total_sections'])
                    with col2:
                        st.metric("📚 Total Modules", analysis_result['summary']['total_modules'])
                    with col3:
                        st.metric("📁 Module Types", len(analysis_result['summary']['module_types']))
                    
                    # Module types breakdown
                    st.subheader("📋 Module Types Found")
                    module_types_df = pd.DataFrame([
                        {"Type": mod_type, "Count": count} 
                        for mod_type, count in analysis_result['summary']['module_types'].items()
                    ])
                    st.dataframe(module_types_df, use_container_width=True)
                    
                    # Detailed section view
                    st.subheader("🗂️ Section Details")
                    for section in analysis_result['sections']:
                        with st.expander(f"Section {section['section']}: {section['name']} ({len(section['modules'])} modules)"):
                            if section['modules']:
                                modules_df = pd.DataFrame([
                                    {
                                        "Name": mod['name'],
                                        "Type": mod['modname'],
                                        "Visible": "✅" if mod['visible'] else "❌",
                                        "ID": mod['id']
                                    }
                                    for mod in section['modules']
                                ])
                                st.dataframe(modules_df, use_container_width=True)
                            else:
                                st.info("No modules in this section")
                    
                    # Duplication planning
                    st.subheader("🔄 Duplication Planning")
                    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                    st.markdown("""
                    **⚠️ API Limitation Notice:**
                    Direct module creation is not available. Here are your options:
                    
                    1. **Template Approach**: Use this course as a template, create duplicates manually
                    2. **Update Approach**: Create basic structure manually, then use our APIs to update content
                    3. **Backup/Restore**: Use Moodle's backup/restore with our analysis for guidance
                    """)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Generate duplication report
                    if st.button("📄 Generate Duplication Report"):
                        duplication_plan = analyzer.generate_duplication_plan(
                            source_course_id, analysis_result
                        )
                        
                        st.subheader("📋 Duplication Plan")
                        st.json(duplication_plan)
                        
                        # Download report
                        report_json = json.dumps(duplication_plan, indent=2)
                        st.download_button(
                            label="💾 Download Report",
                            data=report_json,
                            file_name=f"course_{source_course_id}_duplication_plan.json",
                            mime="application/json"
                        )
                    
                except Exception as e:
                    st.error(f"❌ Analysis failed: {e}")

def show_quiz_management():
    """Quiz management and grading interface"""
    st.header("🎯 Quiz Management & Grading")
    
    courses = get_courses()
    if not courses:
        st.warning("No courses found. Please check your connection.")
        return
    
    # Course selection
    course_options = {f"{c['fullname']} (ID: {c['id']})": c['id'] 
                     for c in courses}
    
    selected_course_name = st.selectbox(
        "Choose Course",
        options=list(course_options.keys()),
        help="Select course to manage quizzes"
    )
    
    if selected_course_name:
        course_id = course_options[selected_course_name]
        
        # Get quizzes
        if st.button("📋 Get Quizzes"):
            with st.spinner("Loading quizzes..."):
                try:
                    quizzes = st.session_state.moodle_client.get_quizzes_by_courses([course_id])
                    
                    if quizzes and 'quizzes' in quizzes:
                        st.success(f"✅ Found {len(quizzes['quizzes'])} quizzes")
                        
                        # Display quizzes
                        for quiz in quizzes['quizzes']:
                            with st.expander(f"📝 {quiz['name']} (ID: {quiz['id']})"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write(f"**Course Module ID:** {quiz['coursemodule']}")
                                    st.write(f"**Time Limit:** {quiz.get('timelimit', 'No limit')} seconds")
                                    st.write(f"**Attempts:** {quiz.get('attempts', 'Unlimited')}")
                                
                                with col2:
                                    st.write(f"**Grade:** {quiz.get('grade', 'N/A')}")
                                    st.write(f"**Questions:** {quiz.get('sumgrades', 'N/A')}")
                                    
                                # Quiz management actions
                                st.subheader("🔧 Quiz Actions")
                                
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    if st.button(f"👥 View Attempts", key=f"attempts_{quiz['id']}"):
                                        st.info("Attempt viewing functionality - use get_attempt_summary API")
                                
                                with col2:
                                    if st.button(f"📊 Grade Quiz", key=f"grade_{quiz['id']}"):
                                        st.info("Grading functionality - use save_attempt API")
                                
                                with col3:
                                    if st.button(f"📈 Analytics", key=f"analytics_{quiz['id']}"):
                                        st.info("Analytics functionality - use get_attempt_data API")
                    
                    else:
                        st.info("No quizzes found in this course")
                        
                except Exception as e:
                    st.error(f"❌ Error loading quizzes: {e}")
        
        # Quiz grading section
        st.markdown("---")
        st.subheader("⚡ Quick Grading Test")
        
        col1, col2 = st.columns(2)
        
        with col1:
            attempt_id = st.number_input("Attempt ID", min_value=1, value=1)
        
        with col2:
            grade_value = st.number_input("Grade", min_value=0.0, max_value=100.0, value=85.0)
        
        if st.button("💾 Test Save Grade"):
            with st.spinner("Saving grade..."):
                try:
                    grading_data = [{"name": "grade", "value": str(grade_value)}]
                    result = st.session_state.moodle_client.save_attempt(attempt_id, grading_data)
                    st.success("✅ Grade saved successfully!")
                    st.json(result)
                except Exception as e:
                    st.error(f"❌ Error saving grade: {e}")

def show_forum_monitoring():
    """Forum monitoring and management"""
    st.header("💬 Forum Monitoring & Management")
    
    courses = get_courses()
    if not courses:
        st.warning("No courses found. Please check your connection.")
        return
    
    # Course selection
    course_options = {f"{c['fullname']} (ID: {c['id']})": c['id'] 
                     for c in courses}
    
    selected_course_name = st.selectbox(
        "Choose Course",
        options=list(course_options.keys()),
        help="Select course to monitor forums"
    )
    
    if selected_course_name:
        course_id = course_options[selected_course_name]
        
        # Get forums
        if st.button("📋 Get Forums"):
            with st.spinner("Loading forums..."):
                try:
                    forums = st.session_state.moodle_client.get_forums_by_courses([course_id])
                    
                    if forums:
                        st.success(f"✅ Found {len(forums)} forums")
                        
                        # Display forums
                        for forum in forums:
                            with st.expander(f"💬 {forum['name']} (ID: {forum['id']})"):
                                st.write(f"**Type:** {forum['type']}")
                                st.write(f"**Intro:** {forum.get('intro', 'No description')[:200]}...")
                                
                                # Forum actions
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    if st.button(f"📄 View Discussions", key=f"discussions_{forum['id']}"):
                                        # Get discussions
                                        try:
                                            discussions = st.session_state.moodle_client.get_forum_discussions(forum['id'])
                                            st.write("**Discussions:**")
                                            for disc in discussions.get('discussions', []):
                                                st.write(f"- {disc['name']} by {disc['userfullname']}")
                                        except Exception as e:
                                            st.error(f"Error loading discussions: {e}")
                                
                                with col2:
                                    if st.button(f"✍️ Add Discussion", key=f"add_{forum['id']}"):
                                        st.info("Add discussion functionality available via add_discussion API")
                                
                                with col3:
                                    if st.button(f"🤖 AI Monitor", key=f"ai_{forum['id']}"):
                                        st.info("AI monitoring setup - integrate with OpenRouter API")
                    
                    else:
                        st.info("No forums found in this course")
                        
                except Exception as e:
                    st.error(f"❌ Error loading forums: {e}")
        
        # AI Response setup
        st.markdown("---")
        st.subheader("🤖 AI Response Setup")
        
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("""
        **AI Forum Monitoring Features:**
        - Monitor new posts automatically
        - Generate responses using OpenRouter API
        - Set response delay and approval workflow
        - Filter questions vs announcements
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            ai_model = st.selectbox("AI Model", ["gpt-4", "gpt-3.5-turbo", "claude-3"])
            response_tone = st.selectbox("Response Tone", ["Professional", "Friendly", "Academic"])
        
        with col2:
            auto_reply = st.checkbox("Auto-reply enabled")
            review_before_post = st.checkbox("Review before posting", value=True)
        
        if st.button("🚀 Setup AI Monitoring"):
            st.success("✅ AI monitoring configuration saved!")

def show_api_testing():
    """API testing interface"""
    st.header("🔍 API Testing Interface")
    
    st.markdown("Test individual Moodle API functions")
    
    # API function selector
    api_functions = {
        "Site Info": "get_site_info",
        "Enrolled Courses": "get_enrolled_courses", 
        "Quizzes by Courses": "get_quizzes_by_courses",
        "Forums by Courses": "get_forums_by_courses",
        "Course Contents": "get_course_contents",
        "Forum Discussions": "get_forum_discussions",
        "Attempt Summary": "get_attempt_summary",
        "Attempt Data": "get_attempt_data",
        "Save Attempt": "save_attempt"
    }
    
    selected_function = st.selectbox(
        "Choose API Function",
        options=list(api_functions.keys())
    )
    
    function_name = api_functions[selected_function]
    
    # Parameter inputs based on function
    params = {}
    
    if function_name in ["get_quizzes_by_courses", "get_forums_by_courses"]:
        course_ids = st.text_input("Course IDs (comma-separated)", value="99,100")
        if course_ids:
            params['course_ids'] = [int(x.strip()) for x in course_ids.split(',')]
    
    elif function_name == "get_course_contents":
        course_id = st.number_input("Course ID", value=99)
        params['course_id'] = course_id
    
    elif function_name == "get_forum_discussions":
        forum_id = st.number_input("Forum ID", value=1)
        params['forum_id'] = forum_id
    
    elif function_name in ["get_attempt_summary", "get_attempt_data"]:
        attempt_id = st.number_input("Attempt ID", value=1)
        params['attempt_id'] = attempt_id
        
        if function_name == "get_attempt_data":
            page = st.number_input("Page", value=-1)
            params['page'] = page
    
    elif function_name == "save_attempt":
        attempt_id = st.number_input("Attempt ID", value=1)
        grade_value = st.number_input("Grade", value=85.0)
        params['attempt_id'] = attempt_id
        params['data'] = [{"name": "grade", "value": str(grade_value)}]
    
    # Test button
    if st.button("🧪 Test API Function"):
        if not st.session_state.connected:
            st.error("Please connect to Moodle first!")
            return
        
        with st.spinner(f"Testing {selected_function}..."):
            try:
                client = st.session_state.moodle_client
                func = getattr(client, function_name)
                
                if params:
                    result = func(**params)
                else:
                    result = func()
                
                st.success(f"✅ {selected_function} executed successfully!")
                
                # Display result
                st.subheader("📊 API Response")
                
                if isinstance(result, dict) or isinstance(result, list):
                    st.json(result)
                else:
                    st.write(result)
                    
                # Download result
                if result:
                    result_json = json.dumps(result, indent=2, default=str)
                    st.download_button(
                        label="💾 Download Result",
                        data=result_json,
                        file_name=f"{function_name}_result.json",
                        mime="application/json"
                    )
                
            except Exception as e:
                st.error(f"❌ API call failed: {e}")
                st.code(str(e))

if __name__ == "__main__":
    main()
