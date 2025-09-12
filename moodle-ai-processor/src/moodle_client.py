"""
Moodle API Client

This module provides a client for interacting with Moodle Web Services API.
"""

import requests
import json
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin


class MoodleAPIClient:
    """Client for Moodle Web Services API"""
    
    def __init__(self, base_url: str, token: str):
        """
        Initialize Moodle API client
        
        Args:
            base_url: Moodle site base URL
            token: Web service token
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.api_url = f"{self.base_url}/webservice/rest/server.php"
        self.logger = logging.getLogger(__name__)
    
    def _make_request(self, function: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a request to Moodle Web Services API
        
        Args:
            function: Moodle web service function name
            params: Additional parameters for the function
            
        Returns:
            API response as dictionary
        """
        if params is None:
            params = {}
            
        # Base parameters
        request_params = {
            'wstoken': self.token,
            'wsfunction': function,
            'moodlewsrestformat': 'json'
        }
        
        # Add function-specific parameters
        request_params.update(params)
        
        try:
            response = requests.post(self.api_url, data=request_params)
            response.raise_for_status()
            
            result = response.json()
            
            # Check for Moodle API errors
            if isinstance(result, dict) and 'exception' in result:
                self.logger.error(f"Moodle API error: {result}")
                raise Exception(f"Moodle API error: {result['message']}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            raise
    
    def get_course_details(self, course_id: int) -> Dict[str, Any]:
        """
        Get course details by course ID
        
        Args:
            course_id: Moodle course ID
            
        Returns:
            Course details
        """
        params = {
            'options[ids][0]': course_id
        }
        
        result = self._make_request('core_course_get_courses', params)
        return result[0] if result else {}
    
    def get_course_by_idnumber(self, idnumber: str) -> Dict[str, Any]:
        """
        Get course details by HKBU assigned course ID number
        
        Args:
            idnumber: HKBU course ID number (e.g., "2024;S2;UCLC1009;1;")
            
        Returns:
            Course details
        """
        params = {
            'field': 'idnumber',
            'value': idnumber
        }
        
        result = self._make_request('core_course_get_courses_by_field', params)
        return result['courses'][0] if result.get('courses') else {}
    
    def get_enrolled_users(self, course_id: int) -> List[Dict[str, Any]]:
        """
        Get enrolled users in a course
        
        Args:
            course_id: Moodle course ID
            
        Returns:
            List of enrolled users
        """
        params = {
            'courseid': course_id
        }
        
        return self._make_request('core_enrol_get_enrolled_users', params)
    
    def get_course_contents(self, course_id: int) -> List[Dict[str, Any]]:
        """
        Get course contents (sections, activities, etc.)
        
        Args:
            course_id: Moodle course ID
            
        Returns:
            Course contents
        """
        params = {
            'courseid': course_id
        }
        
        return self._make_request('core_course_get_contents', params)
    
    def get_forums(self, course_id: int) -> List[Dict[str, Any]]:
        """
        Get forums in a course
        
        Args:
            course_id: Moodle course ID
            
        Returns:
            List of forums
        """
        params = {
            'courseids[0]': course_id
        }
        
        return self._make_request('mod_forum_get_forums_by_courses', params)
    
    def get_forum_discussions(self, forum_id: int) -> List[Dict[str, Any]]:
        """
        Get discussions in a forum
        
        Args:
            forum_id: Forum ID
            
        Returns:
            List of discussions
        """
        params = {
            'forumid': forum_id
        }
        
        return self._make_request('mod_forum_get_forum_discussions', params)
    
    def get_discussion_posts(self, discussion_id: int) -> List[Dict[str, Any]]:
        """
        Get posts in a discussion
        
        Args:
            discussion_id: Discussion ID
            
        Returns:
            List of posts
        """
        params = {
            'discussionid': discussion_id
        }
        
        return self._make_request('mod_forum_get_discussion_posts', params)
    
    def add_discussion(self, forum_id: int, name: str, message: str, 
                      group_id: int = -1, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Add a new discussion to a forum
        
        Args:
            forum_id: Forum ID
            name: Discussion name/subject
            message: Discussion message content
            group_id: Group ID (-1 for no group)
            options: Additional options
            
        Returns:
            Created discussion information
        """
        params = {
            'forumid': forum_id,
            'subject': name,
            'message': message,
            'groupid': group_id
        }
        
        if options:
            for key, value in options.items():
                params[f'options[{key}]'] = value
        
        return self._make_request('mod_forum_add_discussion', params)
    
    def add_discussion_post(self, discussion_id: int, subject: str, message: str, 
                           parent_id: int = 0) -> Dict[str, Any]:
        """
        Add a post to a discussion
        
        Args:
            discussion_id: Discussion ID
            subject: Post subject
            message: Post message content
            parent_id: Parent post ID (0 for top-level post)
            
        Returns:
            Created post information
        """
        params = {
            'posts[0][discussionid]': discussion_id,
            'posts[0][subject]': subject,
            'posts[0][message]': message,
            'posts[0][parent]': parent_id
        }
        
        return self._make_request('mod_forum_add_discussion_post', params)

    # Quiz Management Functions
    def get_quizzes_by_courses(self, course_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Get quizzes in specified courses
        
        Args:
            course_ids: List of course IDs
            
        Returns:
            List of quizzes
        """
        params = {}
        for i, course_id in enumerate(course_ids):
            params[f'courseids[{i}]'] = course_id
        
        return self._make_request('mod_quiz_get_quizzes_by_courses', params)
    
    # NOTE: mod_quiz_get_quiz_by_instance is NOT AVAILABLE according to ITO
    # Alternative: Use get_quizzes_by_courses and filter by quiz ID
    
    def get_attempt_summary(self, attempt_id: int) -> Dict[str, Any]:
        """
        Get quiz attempt summary
        
        Args:
            attempt_id: Quiz attempt ID
            
        Returns:
            Attempt summary
        """
        params = {
            'attemptid': attempt_id
        }
        
        return self._make_request('mod_quiz_get_attempt_summary', params)
    
    def get_attempt_data(self, attempt_id: int, page: int = -1) -> Dict[str, Any]:
        """
        Get quiz attempt data
        
        Args:
            attempt_id: Quiz attempt ID
            page: Page number (-1 for all pages)
            
        Returns:
            Attempt data
        """
        params = {
            'attemptid': attempt_id,
            'page': page
        }
        
        return self._make_request('mod_quiz_get_attempt_data', params)
    
    def save_attempt(self, attempt_id: int, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Save quiz attempt data
        
        Args:
            attempt_id: Quiz attempt ID
            data: List of answer data
            
        Returns:
            Save result
        """
        params = {
            'attemptid': attempt_id
        }
        
        for i, answer in enumerate(data):
            for key, value in answer.items():
                params[f'data[{i}][{key}]'] = value
        
        return self._make_request('mod_quiz_save_attempt', params)

    # Course Content Management Functions
    def create_courses(self, courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create new courses
        
        Args:
            courses: List of course data dictionaries
            
        Returns:
            List of created courses
        """
        params = {}
        
        for i, course in enumerate(courses):
            for key, value in course.items():
                params[f'courses[{i}][{key}]'] = value
        
        return self._make_request('core_course_create_courses', params)
    
    def update_courses(self, courses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update existing courses
        
        Args:
            courses: List of course data dictionaries with IDs
            
        Returns:
            Update result
        """
        params = {}
        
        for i, course in enumerate(courses):
            for key, value in course.items():
                params[f'courses[{i}][{key}]'] = value
        
        return self._make_request('core_course_update_courses', params)
    
    # NOTE: core_course_create_sections is NOT AVAILABLE according to ITO
    # Alternative: Sections must be created manually or through other means
    
    def edit_section(self, section_id: int, section_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit a course section
        
        Args:
            section_id: Section ID
            section_data: Section data to update
            
        Returns:
            Update result
        """
        params = {
            'id': section_id
        }
        
        for key, value in section_data.items():
            params[key] = value
        
        return self._make_request('core_course_edit_section', params)
    
    # NOTE: core_course_add_module is NOT AVAILABLE according to ITO
    # Alternative: Modules must be added manually or through web interface
    
    def update_module(self, module_id: int, module_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a course module
        
        Args:
            module_id: Module ID
            module_data: Module data to update
            
        Returns:
            Update result
        """
        params = {
            'cmid': module_id
        }
        
        for key, value in module_data.items():
            params[key] = value
        
        # NOTE: core_course_update_module might be core_course_edit_module
        return self._make_request('core_course_edit_module', params)
