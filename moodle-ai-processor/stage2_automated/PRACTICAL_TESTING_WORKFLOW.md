# 🎯 PRACTICAL SANDBOX TESTING WORKFLOW

## 📊 Current API Status Summary

✅ **WORKING API Functions** (4 confirmed):
- `core_course_get_courses` - Get course details
- `core_course_get_contents` - Get course content structure  
- `core_course_get_courses_by_field` - Search courses
- `core_enrol_get_enrolled_users` - Get enrolled users

❌ **BLOCKED API Functions** (Need permissions):
- All forum functions (`mod_forum_*`)
- All quiz functions (`mod_quiz_*`) 
- All content creation functions (`core_course_create_*`)
- Most user management functions

---

## 🖥️ GUI ACCESS INFORMATION

**Login URL**: https://moddw12-buelearning.hkbu.edu.hk/login/index.php  
**Username**: `lcladmin`  
**Password**: `Lcladm#2025`  
**Test Course**: UCLC1009 University English II (Section 1) [2024 S2] (ID: 99)

---

## 🧪 STEP-BY-STEP TESTING WORKFLOW

### **STEP 1: Login and Course Setup** (5 minutes)

1. **Login via GUI**:
   - Open: https://moddw12-buelearning.hkbu.edu.hk/login/index.php
   - Username: `lcladmin`
   - Password: `Lcladm#2025`

2. **Navigate to Test Course**:
   - Go to "UCLC1009 University English II (Section 1) [2024 S2]"
   - Note: This is Course ID 99 (confirmed working via API)

3. **Enable Editing**:
   - Click "Turn editing on" (top right)
   - This allows you to add content

---

### **STEP 2: Test Content Creation (YOUR REQUIREMENT #1)** (15 minutes)

#### **2A: Create Test Section via GUI**
```
Actions in GUI:
1. Scroll to bottom of course page
2. Click "Add section" 
3. Name it: "API Testing Section"
4. Add description: "Section created for API testing purposes"
5. Save changes
```

#### **2B: Add Page to Section via GUI**
```
Actions in GUI:
1. In the new section, click "Add an activity or resource"
2. Select "Page"
3. Name: "API Test Page"
4. Content: "This page was created via GUI to test API content reading"
5. Save and return to course
```

#### **2C: Add Forum to Section via GUI**
```
Actions in GUI:
1. In the same section, click "Add an activity or resource"
2. Select "Forum"
3. Name: "API Test Discussion Forum"
4. Description: "Forum created for testing API forum functions"
5. Save and return to course
```

#### **2D: Verify API Can Read New Content**
```python
# Run this API test after GUI setup:
python -c "
import requests
response = requests.get('https://moddw12-buelearning.hkbu.edu.hk/webservice/rest/server.php', 
params={'wstoken': 'eac84a6e8c353a7f88f424b14a340df4', 'wsfunction': 'core_course_get_contents', 'courseid': '99', 'moodlewsrestformat': 'json'})
import json
data = response.json()
print('Sections found:', len(data))
for section in data:
    print(f'Section: {section.get(\"name\", \"Unknown\")} - Modules: {len(section.get(\"modules\", []))}')
    for module in section.get('modules', []):
        print(f'  - {module.get(\"name\", \"Unknown\")} ({module.get(\"modname\", \"unknown\")}) ID: {module.get(\"id\")}')
"
```

**Expected Result**: 🎯 You should see your new section and modules in the API response

---

### **STEP 3: Test Forum Functions (YOUR REQUIREMENTS #2 & #3)** (20 minutes)

#### **3A: Create Forum Content via GUI**
```
Actions in GUI:
1. Click on your "API Test Discussion Forum"
2. Click "Add a new discussion topic"
3. Subject: "Test Discussion for API"
4. Message: "This is a test post to verify API can read forum content. Please reply to test API forum reading capabilities."
5. Post to forum

6. Add a reply to your own post:
   - Click on the discussion
   - Click "Reply"
   - Write: "This is a test reply to verify API can read forum replies."
   - Post reply
```

#### **3B: Note Important IDs**
```
Record these for API testing:
- Forum ID: [Check the URL when viewing forum - should be visible in course content API]
- Discussion ID: [Check URL when viewing discussion]
- Post IDs: [Check URLs when viewing individual posts]
```

#### **3C: Test Forum API Access**
```python
# Test 1: Try to get forum discussions (currently blocked)
python -c "
import requests
response = requests.get('https://moddw12-buelearning.hkbu.edu.hk/webservice/rest/server.php',
params={'wstoken': 'eac84a6e8c353a7f88f424b14a340df4', 'wsfunction': 'mod_forum_get_forum_discussions', 'forumid': '[FORUM_ID]', 'moodlewsrestformat': 'json'})
print('Forum API Response:', response.json())
"
```

**Expected Result**: ❌ Access control exception (need permissions from ITO)

---

### **STEP 4: Test Quiz Functions (YOUR REQUIREMENT #4)** (15 minutes)

#### **4A: Create Quiz via GUI**
```
Actions in GUI:
1. In your test section, click "Add an activity or resource"
2. Select "Quiz"
3. Name: "API Test Quiz"
4. Description: "Quiz created to test API quiz reading capabilities"
5. Save and continue

6. Add questions:
   - Click "Edit quiz"
   - Click "Add" → "a new question"
   - Choose "Multiple choice"
   - Question name: "Test Question 1"
   - Question text: "What is the purpose of this quiz?"
   - Add answers: A) API Testing B) Learning C) Fun D) All of the above
   - Set correct answer: D
   - Save changes

7. Publish the quiz (make it available)
```

#### **4B: Take the Quiz (as test student)**
```
Actions in GUI:
1. View the quiz as a student would
2. Click "Attempt quiz now"
3. Answer the questions
4. Submit the quiz
5. Note the attempt ID if visible
```

#### **4C: Test Quiz API Access**
```python
# Test: Try to get quiz attempts (currently blocked)
python -c "
import requests
response = requests.get('https://moddw12-buelearning.hkbu.edu.hk/webservice/rest/server.php',
params={'wstoken': 'eac84a6e8c353a7f88f424b14a340df4', 'wsfunction': 'mod_quiz_get_quizzes_by_courses', 'courseids[0]': '99', 'moodlewsrestformat': 'json'})
print('Quiz API Response:', response.json())
"
```

**Expected Result**: ❌ Access control exception (need permissions from ITO)

---

### **STEP 5: Document What Works vs. What Needs Permissions** (10 minutes)

#### **5A: Test Content Reading After GUI Changes**
```python
# This should work - verify API can see GUI-created content
python sandbox_explorer.py
```

#### **5B: Create Evidence Package**
```
Document for ITO:
1. Screenshots of GUI-created content
2. API responses showing content is visible
3. Error messages when trying forum/quiz functions
4. Specific function names that need permissions
```

---

## 📋 TESTING CHECKLIST

### ✅ **What We CAN Test Today**:
- [x] GUI content creation (sections, pages, forums, quizzes)
- [x] API reading of GUI-created content structure
- [x] User enrollment verification
- [x] Course metadata access

### ❌ **What We CANNOT Test (Need ITO Permissions)**:
- [ ] Reading forum discussions/posts via API
- [ ] Adding forum replies via API
- [ ] Reading quiz attempts/answers via API
- [ ] Automated grading via API
- [ ] Creating content via API

---

## 🎯 EXPECTED OUTCOMES

### **Immediate Results** (Today):
1. ✅ Confirm API can read GUI-created content structure
2. ✅ Document exact forum/quiz IDs for future API testing
3. ✅ Create realistic test content for permission testing
4. ❌ Confirm forum/quiz APIs are blocked (expected)

### **After ITO Permission Grant**:
1. 🔄 Forum reading: `mod_forum_get_forum_discussions`
2. 🔄 Forum writing: `mod_forum_add_discussion_post`
3. 🔄 Quiz reading: `mod_quiz_get_quiz_attempts`
4. 🔄 Quiz grading: `mod_quiz_save_attempt`

---

## 📧 EVIDENCE FOR ITO COLLEAGUES

### **Proof of Concept**:
- Screenshots showing GUI content creation working
- API responses showing content structure is readable
- Error logs showing exactly which permissions are needed

### **Clear Request**:
```
Dear ITO Colleagues,

We have successfully tested the sandbox and can confirm:

✅ WORKING: Content reading, course structure, user enrollment
❌ NEED PERMISSIONS: Forum functions, Quiz functions, Content creation

Specific functions we need enabled:
• mod_forum_get_forum_discussions
• mod_forum_add_discussion_post  
• mod_quiz_get_quizzes_by_courses
• mod_quiz_get_quiz_attempts

We have created test content in Course 99 ready for API testing once permissions are granted.
```

---

## 🚀 NEXT STEPS

1. **Complete this workflow** (estimated 45 minutes)
2. **Document results** with screenshots and API responses
3. **Send evidence package** to ITO colleagues
4. **Request specific API permissions** listed above
5. **Resume testing** once permissions are granted

---

**Start with Step 1 and work through systematically. This will give us concrete evidence of what works and what needs permissions from ITO!** 🎯
