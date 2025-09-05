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
