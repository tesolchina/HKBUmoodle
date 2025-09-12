# 🎓 HKBU Moodle Assistant - Setup Guide for Colleagues

## 🚀 Quick Start (Easiest)

### Option 1: Use Pre-configured Credentials
1. **Launch the app:**
   ```bash
   cd moodle-ai-processor
   ./run_gui.sh
   ```

2. **Click "Quick Connect"** on the main page
   - Uses sandbox credentials (works on HKBU network)
   - No setup required!

## 🔧 Custom Setup (If you have your own token)

### Step 1: Get Your Moodle API Token
1. **Log into HKBU Moodle:** https://moodle.hkbu.edu.hk
2. **Go to:** User menu → Preferences → User account → Security keys
3. **Create token:** Click "Create token" for Web services
4. **Copy the token** (long string of letters/numbers)

### Step 2: Configure the App
**Option A: Edit the credential file**
1. Open `moodle_credentials.py` 
2. Replace `"your_token_here"` with your actual token
3. Save the file

**Option B: Use manual input in GUI**
1. Launch the app: `./run_gui.sh`
2. In sidebar, uncheck "Use Default HKBU Credentials"
3. Enter URL: `https://moodle.hkbu.edu.hk`
4. Enter your token
5. Click "Connect to Moodle"

## 🎯 What You Can Test

### 1. Material Analysis
- Select any course you have access to
- See complete breakdown of assignments, quizzes, forums
- Generate duplication plans (great for setting up multiple sections)

### 2. Quiz Management  
- View all quizzes in your courses
- See quiz settings and configurations
- Test programmatic grading capabilities

### 3. Forum Monitoring
- List all forums in your courses
- View discussions and posts
- Test automated response capabilities

### 4. API Testing
- Test individual Moodle API functions
- See raw API responses
- Understand what's possible programmatically

## 🔍 Troubleshooting

### "Connection Failed" Error
- **If using sandbox:** Must be on HKBU network
- **If using production:** Verify your token is correct
- **Try different environment** in the sidebar dropdown

### "Import Error" 
```bash
# Make sure you're in the right directory
cd moodle-ai-processor

# Check dependencies
pip install -r requirements_streamlit.txt
```

### "No courses found"
- Normal if you don't have courses in the test environment
- Try the production environment with your own token
- Use API Testing module to test individual functions

## 💡 Tips for Testing

### For Instructors:
- **Material Analysis** shows how to automate course setup
- **Quiz Management** demonstrates automated grading
- **Forum Monitoring** can help with Q&A automation

### For Administrators:
- **API Testing** shows all available functions
- **Material Analysis** helps with course template creation
- All features work with existing Moodle permissions

### For Developers:
- See `src/moodle_client.py` for API implementation
- Check `tests/` directory for comprehensive test examples
- `demo.py` shows system capabilities

## 🎉 What This Demonstrates

✅ **Full Moodle API Integration** - 17+ API functions working  
✅ **Real-world Workflows** - Course setup, grading, monitoring  
✅ **User-friendly Interface** - No technical knowledge required  
✅ **Extensible System** - Ready for production deployment  

## 📞 Need Help?

1. **Check the terminal output** for detailed error messages
2. **Try the API Testing module** to debug specific functions  
3. **Use different environments** (sandbox vs production)
4. **Contact the development team** for technical support

---

**Ready to explore!** 🚀 The system demonstrates the full potential of automated Moodle management.
