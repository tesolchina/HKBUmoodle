# 🎓 HKBU Moodle Assistant - Streamlit GUI

**Quick Prototype** - Web interface for testing Moodle API functions with colleagues

## 🚀 Quick Start

### Option 1: Use the Launcher Script
```bash
cd moodle-ai-processor
./run_gui.sh
```

### Option 2: Manual Launch
```bash
cd moodle-ai-processor
pip install -r requirements_streamlit.txt
export PYTHONPATH=".:$PYTHONPATH"
streamlit run streamlit_app.py
```

## 🌐 Access the GUI

Once running, open your browser to:
**http://localhost:8501**

## 🔧 Setup Instructions

### **🚀 One-Click Setup (Recommended)**
1. **Launch the GUI:**
   ```bash
   cd moodle-ai-processor
   ./run_gui.sh
   ```

2. **Connect instantly:**
   - Click the big **"Quick Connect"** button
   - ✅ Done! Pre-configured with HKBU credentials

### **🔑 No API Token Needed!**
- Uses pre-configured HKBU Moodle sandbox credentials
- Colleagues can test immediately without setup
- Credentials are safely stored in config files

### **🎯 Advanced Setup (Optional)**
If you want to use different credentials:
1. Uncheck "Use Default HKBU Credentials" 
2. Enter custom Moodle URL and API token
3. Click "Connect to Moodle"

## 📱 Available Features

### 🏠 Dashboard
- Connection status and quick stats
- Overview of available functions
- Quick action buttons

### 📚 Material Analysis
- Analyze course structure and content
- Generate duplication plans (with API limitation workarounds)
- Export analysis reports
- View detailed course breakdown

### 🎯 Quiz Management  
- List quizzes in courses
- View quiz details and settings
- Test grading functionality
- Manage quiz attempts

### 💬 Forum Monitoring
- View forums in courses
- List discussions and posts
- Test forum interaction APIs
- Setup for AI auto-response (future)

### 🔍 API Testing
- Test individual Moodle API functions
- Input parameters and view responses
- Download API results
- Debug API calls

## 🛠️ Technical Details

### Built With:
- **Streamlit** - Web framework
- **Python** - Backend logic
- **Our Moodle API Client** - Core functionality
- **Pandas** - Data handling

### Features:
- ✅ **Real-time API testing** - Test all available Moodle APIs
- ✅ **Course material analysis** - Detailed content breakdown
- ✅ **Quiz grading interface** - Manage quiz attempts
- ✅ **Forum monitoring** - View and manage discussions
- ✅ **Export capabilities** - Download reports and data
- ✅ **Error handling** - User-friendly error messages
- ✅ **Responsive design** - Works on desktop and tablet

### API Functions Tested:
- `get_site_info` - Connection testing
- `get_enrolled_courses` - Course listing
- `get_quizzes_by_courses` - Quiz management
- `get_forums_by_courses` - Forum monitoring
- `get_course_contents` - Material analysis
- `save_attempt` - Quiz grading
- And more...

## ⚠️ Known Limitations

Based on our API testing, some functions are **not available**:
- `core_course_add_module` - Cannot create new modules
- `core_course_create_sections` - Cannot create new sections
- `mod_quiz_get_quiz_by_instance` - Alternative APIs available

**Workarounds implemented:**
- Template-based material duplication
- Manual creation + API updates
- Analysis and planning tools

## 🔍 Troubleshooting

### Import Errors
If you see import errors:
```bash
# Make sure you're in the right directory
cd moodle-ai-processor

# Check Python path
export PYTHONPATH=".:$PYTHONPATH"
```

### Connection Issues
- ✅ **Default credentials should work automatically**
- If issues persist, try unchecking "Use Default HKBU Credentials" and entering manually:
  - URL: `https://moddw12-buelearning.hkbu.edu.hk`
  - Token: Available in `config/MoodleSandbox.txt`
- Check that the HKBU Moodle sandbox is accessible

### Package Issues
```bash
# Reinstall dependencies
pip install -r requirements_streamlit.txt
```

## 📝 Usage Examples

### Test Course Analysis:
1. Connect to Moodle
2. Go to "Material Analysis"
3. Select a course (e.g., UCLC1009)
4. Click "Analyze Course Content"
5. View detailed breakdown and export report

### Test Quiz Grading:
1. Go to "Quiz Management"
2. Select course with quizzes
3. Click "Get Quizzes" 
4. View quiz details
5. Test grading with attempt ID

### Test API Functions:
1. Go to "API Testing"
2. Select function (e.g., "Site Info")
3. Click "Test API Function"
4. View response and download results

## 🎯 Next Steps

This prototype demonstrates:
- ✅ Full API integration working
- ✅ User-friendly interface
- ✅ Real-world workflow testing
- ✅ Error handling and validation

**For production deployment:**
- Enhanced UI with React/FastAPI
- User authentication system  
- Background job processing
- Advanced reporting features
- AI integration for forum responses

## 📞 Support

If you encounter issues:
1. Check the terminal output for errors
2. Verify your API token permissions
3. Try the API Testing module to debug
4. Contact the development team

---

**Ready to test!** 🚀 Launch the GUI and start exploring your Moodle API capabilities.
