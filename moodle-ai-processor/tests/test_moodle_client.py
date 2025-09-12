"""
Test Moodle Client

Basic tests for the Moodle API client functionality
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path.resolve()))

from src.moodle_client import MoodleAPIClient


class TestMoodleClient(unittest.TestCase):
    
    def setUp(self):
        self.client = MoodleAPIClient(
            base_url="https://test.moodle.com",
            token="test_token"
        )
    
    @patch('requests.post')
    def test_get_course_details(self, mock_post):
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = [{"id": 99, "fullname": "Test Course"}]
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.client.get_course_details(99)
        
        self.assertEqual(result["id"], 99)
        self.assertEqual(result["fullname"], "Test Course")
        
        # Verify the correct API call was made
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('wsfunction', call_args[1]['data'])
        self.assertEqual(call_args[1]['data']['wsfunction'], 'core_course_get_courses')
    
    def test_api_url_construction(self):
        expected_url = "https://test.moodle.com/webservice/rest/server.php"
        self.assertEqual(self.client.api_url, expected_url)
        
        # Test with trailing slash
        client_with_slash = MoodleAPIClient(
            base_url="https://test.moodle.com/",
            token="test_token"
        )
        self.assertEqual(client_with_slash.api_url, expected_url)
    
    @patch('requests.post')
    def test_get_forums(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = [{"id": 1, "name": "General Forum"}]
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client.get_forums(99)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[0]["name"], "General Forum")
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['data']['wsfunction'], 'mod_forum_get_forums_by_courses')

    @patch('requests.post')
    def test_get_forum_discussions(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = [{"id": 10, "name": "Discussion Topic"}]
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client.get_forum_discussions(1)
        self.assertEqual(result[0]["id"], 10)
        self.assertEqual(result[0]["name"], "Discussion Topic")
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['data']['wsfunction'], 'mod_forum_get_forum_discussions')

    @patch('requests.post')
    def test_get_discussion_posts(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = [{"id": 100, "message": "Hello world"}]
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client.get_discussion_posts(10)
        self.assertEqual(result[0]["id"], 100)
        self.assertEqual(result[0]["message"], "Hello world")
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['data']['wsfunction'], 'mod_forum_get_discussion_posts')

    @patch('requests.post')
    def test_add_discussion(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"discussionid": 20, "subject": "New Discussion"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client.add_discussion(1, "New Discussion", "Discussion content")
        self.assertEqual(result["discussionid"], 20)
        self.assertEqual(result["subject"], "New Discussion")
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['data']['wsfunction'], 'mod_forum_add_discussion')

    @patch('requests.post')
    def test_add_discussion_post(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"id": 101, "subject": "Test Subject", "message": "Test Message"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client.add_discussion_post(10, "Test Subject", "Test Message", parent_id=0)
        self.assertEqual(result["id"], 101)
        self.assertEqual(result["subject"], "Test Subject")
        self.assertEqual(result["message"], "Test Message")
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['data']['wsfunction'], 'mod_forum_add_discussion_post')

    # Quiz API Tests
    @patch('requests.post')
    def test_get_quizzes_by_courses(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = [{"id": 1, "name": "Test Quiz", "course": 99}]
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client.get_quizzes_by_courses([99])
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[0]["name"], "Test Quiz")
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['data']['wsfunction'], 'mod_quiz_get_quizzes_by_courses')

    # NOTE: mod_quiz_get_quiz_by_instance test removed - API not available

    @patch('requests.post')
    def test_get_attempt_summary(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"id": 100, "quiz": 1, "userid": 10, "state": "finished"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client.get_attempt_summary(100)
        self.assertEqual(result["id"], 100)
        self.assertEqual(result["state"], "finished")
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['data']['wsfunction'], 'mod_quiz_get_attempt_summary')

    @patch('requests.post')
    def test_get_attempt_data(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"questions": [{"id": 1, "slot": 1}], "nextpage": -1}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.client.get_attempt_data(100, page=0)
        self.assertEqual(result["questions"][0]["id"], 1)
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['data']['wsfunction'], 'mod_quiz_get_attempt_data')

    @patch('requests.post')
    def test_save_attempt(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"state": "finished", "warnings": []}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        test_data = [{"name": "q1_answer", "value": "Option A"}]
        result = self.client.save_attempt(100, test_data)
        self.assertEqual(result["state"], "finished")
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['data']['wsfunction'], 'mod_quiz_save_attempt')

    # Course Content Management Tests
    @patch('requests.post')
    def test_create_courses(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = [{"id": 200, "fullname": "New Course", "shortname": "NEW101"}]
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        test_courses = [{"fullname": "New Course", "shortname": "NEW101", "categoryid": 1}]
        result = self.client.create_courses(test_courses)
        self.assertEqual(result[0]["id"], 200)
        self.assertEqual(result[0]["fullname"], "New Course")
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['data']['wsfunction'], 'core_course_create_courses')

    @patch('requests.post')
    def test_update_courses(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"warnings": []}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        test_courses = [{"id": 200, "fullname": "Updated Course"}]
        result = self.client.update_courses(test_courses)
        self.assertEqual(result["warnings"], [])
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['data']['wsfunction'], 'core_course_update_courses')

    # NOTE: create_sections test removed - API not available
    # NOTE: add_module test removed - API not available

    @patch('requests.post')
    def test_edit_section(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"warnings": []}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        test_data = {"name": "Updated Section", "summary": "Updated description"}
        result = self.client.edit_section(300, test_data)
        self.assertEqual(result["warnings"], [])
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['data']['wsfunction'], 'core_course_edit_section')

    @patch('requests.post')
    def test_update_module(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"warnings": []}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        test_data = {"name": "Updated Assignment", "visible": 1}
        result = self.client.update_module(400, test_data)
        self.assertEqual(result["warnings"], [])
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['data']['wsfunction'], 'core_course_edit_module')


if __name__ == '__main__':
    unittest.main()
