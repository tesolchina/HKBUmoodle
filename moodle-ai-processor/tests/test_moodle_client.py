"""
Test Moodle Client

Basic tests for the Moodle API client functionality
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

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


if __name__ == '__main__':
    unittest.main()
