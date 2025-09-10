# Email Draft to Fai and ITO Colleagues

---

**To:** Fai and ITO Colleagues  
**Subject:** Moodle API Permission Request - Course Automation Project  
**Date:** September 10, 2025  

---

Dear Fai and colleagues,

I hope this email finds you well. Thank you for providing the Moodle API sandbox access and token for our course automation project. We have completed our initial testing and would like to request additional API permissions to enable the full functionality we discussed.

## 🔍 **Current Testing Results**

We have successfully established API connectivity and conducted comprehensive testing using token `eac84a6e8c353a7f88f424b14a340df4`. Here are our findings:

### ✅ **Currently Working Functions** (No changes needed):
- **Course Structure Reading** (`core_course_get_contents`) - Successfully reads course sections and modules
- **Course Listing** (`core_course_get_courses`) - Lists available courses 
- **Student Enrollment Data** (`core_enrol_get_enrolled_users`) - Retrieves enrolled student information
- **Course Search** (`core_course_search_courses`) - Searches course catalog

These functions are working perfectly and provide good foundation access.

### ❌ **Functions Requiring Permission** (Currently blocked with "access control exception"):

## 📋 **Specific Permission Request**

To implement the course automation features we discussed, we need API access for the following function categories:

### 1. **Forum Management Functions**
- `mod_forum_get_forums_by_courses` - List forums in courses
- `mod_forum_get_forum_discussions` - Read forum posts and student replies
- `mod_forum_add_discussion` - Create new forum posts  
- `mod_forum_add_discussion_post` - Reply to forum messages
- `mod_forum_get_discussion_posts` - Get detailed post content

**Use Case:** Automated forum interaction for instructor responses and discussion management.

### 2. **Quiz Management Functions**  
- `mod_quiz_get_quizzes_by_courses` - List quizzes in courses
- `mod_quiz_get_quiz_by_instance` - Get quiz details and settings
- `mod_quiz_get_attempt_summary` - Read student quiz attempts
- `mod_quiz_get_attempt_data` - Access quiz answers and responses
- `mod_quiz_save_attempt` - Submit quiz responses (if applicable)

**Use Case:** Automated quiz analysis, grading support, and response processing.

### 3. **Course Content Management Functions**
- `core_course_create_courses` - Create new courses
- `core_course_update_courses` - Edit existing courses  
- `core_course_create_sections` - Add new sections to courses
- `core_course_edit_section` - Modify section properties
- `core_course_add_module` - Add activities and resources to sections
- `core_course_update_module` - Edit existing activities and resources

**Use Case:** Automated course structure management, content creation, and organization.

## 🧪 **Testing Evidence**

We have documented our testing methodology and results extensively:

- **GUI Testing Completed**: Successfully created test course and forum content via the sandbox interface
- **API Detection Confirmed**: The API can see newly created content (e.g., Forum ID 94 in our test course)
- **Permission Barriers Identified**: All advanced functions return "webservice_access_exception" errors
- **Function Mapping Complete**: We have mapped each required feature to specific API functions

**Test Example:** 
- Created forum at: https://moddw12-buelearning.hkbu.edu.hk/mod/forum/discuss.php?d=3#p5
- API can detect forum module (ID: 94) but cannot access discussion content due to permissions

## 🎯 **Project Impact**

Enabling these API functions will allow us to:

1. **Automate Forum Interaction**: Read student posts and provide automated instructor responses
2. **Streamline Quiz Management**: Analyze quiz responses and support grading workflows  
3. **Enhance Course Creation**: Programmatically create and organize course content
4. **Improve Efficiency**: Reduce manual administrative tasks for instructors

## 📁 **Documentation Package**

We have prepared comprehensive documentation including:
- Complete API testing results and methodology
- Function-by-function permission requirements  
- Implementation framework and development roadmap
- Evidence of current working functions and blocked functions

These documents are available upon request for your technical review.

## ⏰ **Timeline**

We are ready to begin development immediately upon receiving the requested permissions. The testing framework and implementation tools are already prepared and validated with the currently working API functions.

## 🙏 **Request**

Could you please enable the API functions listed above for our sandbox token? This will allow us to proceed with the full implementation of the course automation features we discussed.

Please let us know if you need any additional information, technical details, or clarification about our requirements. We're happy to provide any additional documentation or demonstrations as needed.

Thank you for your continued support of this project. We look forward to your response.

Best regards,

[Your Name]  
[Your Title/Department]  
[Contact Information]

---

**Attachments Available:**
- API Testing Results (JSON format)
- Technical Implementation Documentation  
- Function Permission Requirements List
- Testing Methodology Documentation
