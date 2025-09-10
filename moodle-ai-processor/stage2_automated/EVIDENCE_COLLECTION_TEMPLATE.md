# Evidence Collection Template for ITO Permission Request

## Current API Status Summary

**Date:** [FILL IN DATE]  
**Tester:** [YOUR NAME]  
**Token:** eac84a6e8c353a7f88f424b14a340df4  

---

## ✅ WORKING API Functions (No Permission Changes Needed)

| Function | Purpose | Test Result | Evidence |
|----------|---------|-------------|----------|
| `core_course_get_contents` | Read course structure | ✅ Working | Can see sections, modules, basic info |
| `core_course_get_courses` | List available courses | ✅ Working | Returns courses 1, 99, 100, 180 |
| `core_enrol_get_enrolled_users` | Get student list | ✅ Working | Returns user details for courses |
| `core_course_search_courses` | Search courses | ✅ Working | Can search course catalog |

---

## ❌ BLOCKED API Functions (Permission Request Required)

### Forum Functions
| Function | Purpose | Current Error | Required Permission |
|----------|---------|---------------|-------------------|
| `mod_forum_get_forums_by_courses` | List forums in course | `Access control exception` | [TO BE DOCUMENTED] |
| `mod_forum_get_forum_discussions` | Read forum posts | `Access control exception` | [TO BE DOCUMENTED] |
| `mod_forum_add_discussion` | Create forum post | `Access control exception` | [TO BE DOCUMENTED] |
| `mod_forum_add_discussion_post` | Reply to forum | `Access control exception` | [TO BE DOCUMENTED] |

### Quiz Functions
| Function | Purpose | Current Error | Required Permission |
|----------|---------|---------------|-------------------|
| `mod_quiz_get_quizzes_by_courses` | List quizzes | `Access control exception` | [TO BE DOCUMENTED] |
| `mod_quiz_get_quiz_by_instance` | Get quiz details | `Access control exception` | [TO BE DOCUMENTED] |
| `mod_quiz_get_attempt_summary` | Get student attempts | `Access control exception` | [TO BE DOCUMENTED] |

### Content Creation Functions
| Function | Purpose | Current Error | Required Permission |
|----------|---------|---------------|-------------------|
| `core_course_create_courses` | Create new course | `Access control exception` | [TO BE DOCUMENTED] |
| `core_course_update_courses` | Edit course | `Access control exception` | [TO BE DOCUMENTED] |
| `core_course_duplicate_course` | Copy course | `Access control exception` | [TO BE DOCUMENTED] |

---

## 🧪 Evidence Collection Workflow

### Step 1: GUI Content Creation
**Date/Time:** [FILL IN]
- [ ] Created new forum in GUI: [Forum name and ID]
- [ ] Created test quiz in GUI: [Quiz name and ID]  
- [ ] Added content to section: [Section name and ID]
- [ ] Screenshot saved: `gui_content_creation_[timestamp].png`

### Step 2: API Detection Test
**Date/Time:** [FILL IN]
- [ ] Ran `quick_api_check.py`
- [ ] API can see new content: YES/NO
- [ ] Content details: [What the API detected]
- [ ] Results saved: `course_content_check_[timestamp].json`

### Step 3: API Access Test
**Date/Time:** [FILL IN]
- [ ] Tested forum API on created content
- [ ] Tested quiz API on created content
- [ ] Documented exact error messages
- [ ] Error logs saved: `api_error_log_[timestamp].txt`

---

## 📋 Permission Request for ITO

**Priority 1 - Essential Functions:**
1. **Forum Management**: Need read/write access for automated forum interaction
   - Reading student posts and replies
   - Posting instructor responses
   - Managing forum discussions

2. **Quiz Management**: Need read access for automated grading support
   - Reading quiz responses
   - Accessing attempt details
   - Getting submission data

**Priority 2 - Advanced Functions:**
3. **Content Creation**: Need write access for course automation
   - Creating course sections
   - Adding resources and activities
   - Duplicating course templates

---

## 📸 Evidence Files to Attach

- [ ] `gui_content_creation_[timestamp].png` - Screenshot of GUI setup
- [ ] `course_content_check_[timestamp].json` - API detection results
- [ ] `api_error_log_[timestamp].txt` - Error messages for blocked functions
- [ ] `PRACTICAL_TESTING_WORKFLOW.md` - Complete testing methodology
- [ ] `sandbox_exploration_results.json` - Systematic API testing results

---

## 💬 Communication Draft for ITO

**Subject:** Moodle API Permission Request - Course Automation Project

Hi [ITO Contact],

We've been testing the Moodle API for our course automation project using the provided sandbox token. Our systematic testing shows that basic read functions work well, but we need additional permissions for forum and quiz automation.

**Current Status:**
- ✅ Course content reading: Working
- ✅ Student enrollment data: Working  
- ❌ Forum interaction: Blocked by access control
- ❌ Quiz data access: Blocked by access control

**Evidence Package:**
Please find attached our complete testing evidence including:
- Screenshots of GUI content creation
- API response logs and error messages
- Systematic testing methodology documentation

**Request:**
Could you please enable the following API functions for our token:
[LIST FROM BLOCKED FUNCTIONS TABLE ABOVE]

**Timeline:**
We're ready to begin development as soon as permissions are granted. This will enable automated forum interaction and quiz grading support for our pilot courses.

Best regards,
[YOUR NAME]

---

## 📝 Notes and Observations

**Technical Notes:**
- [Record any technical insights during testing]
- [Note any workarounds discovered]
- [Document any unexpected behaviors]

**Next Steps:**
- [ ] Complete evidence collection
- [ ] Submit permission request to ITO
- [ ] Begin development once permissions granted
- [ ] Plan pilot course implementation
