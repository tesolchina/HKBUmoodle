"""
Main Processor

This module contains the core processing logic for handling student posts with AI.
"""

import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .moodle_client import MoodleAPIClient
from .ai_client import OpenRouterClient


class MoodleAIProcessor:
    """Main processor for handling student posts with AI"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """
        Initialize the processor
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._setup_logging()
        
        # Initialize clients
        self.moodle_client = MoodleAPIClient(
            base_url=self.config['moodle']['base_url'],
            token=self.config['moodle']['token']
        )
        
        self.ai_client = OpenRouterClient(
            api_key=self.config['openrouter']['api_key'],
            base_url=self.config['openrouter']['base_url'],
            model=self.config['openrouter']['model']
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file', 'logs/moodle_ai_processor.log')
        
        # Create logs directory if it doesn't exist
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def get_course_forums(self, course_id: int) -> List[Dict[str, Any]]:
        """
        Get all forums in a course
        
        Args:
            course_id: Moodle course ID
            
        Returns:
            List of forums
        """
        try:
            forums = self.moodle_client.get_forums(course_id)
            self.logger.info(f"Found {len(forums)} forums in course {course_id}")
            return forums
        except Exception as e:
            self.logger.error(f"Failed to get forums for course {course_id}: {e}")
            return []
    
    def get_recent_posts(self, forum_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent posts from a forum
        
        Args:
            forum_id: Forum ID
            limit: Maximum number of posts to retrieve
            
        Returns:
            List of recent posts
        """
        try:
            discussions = self.moodle_client.get_forum_discussions(forum_id)
            all_posts = []
            
            for discussion in discussions[:limit]:  # Limit discussions processed
                posts = self.moodle_client.get_discussion_posts(discussion['discussion'])
                all_posts.extend(posts)
            
            # Sort by creation time (most recent first)
            all_posts.sort(key=lambda x: x.get('created', 0), reverse=True)
            
            self.logger.info(f"Retrieved {len(all_posts)} posts from forum {forum_id}")
            return all_posts[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get posts from forum {forum_id}: {e}")
            return []
    
    def process_post(self, post: Dict[str, Any], auto_reply: bool = False) -> Dict[str, Any]:
        """
        Process a single post with AI
        
        Args:
            post: Post data from Moodle
            auto_reply: Whether to automatically post reply to Moodle
            
        Returns:
            Processing results
        """
        try:
            post_content = post.get('message', '')
            post_subject = post.get('subject', 'No subject')
            
            self.logger.info(f"Processing post: {post_subject}")
            
            # Generate AI analysis
            analysis = self.ai_client.analyze_student_post(post_content)
            
            # Generate reply
            reply_content = self.ai_client.generate_reply(
                student_post=post_content,
                reply_style="supportive"
            )
            
            result = {
                'post_id': post.get('id'),
                'post_subject': post_subject,
                'post_author': post.get('author', {}),
                'original_content': post_content,
                'ai_analysis': analysis,
                'ai_reply': reply_content,
                'processed_at': datetime.now().isoformat(),
                'auto_replied': False
            }
            
            # Auto-reply if enabled
            if auto_reply and post.get('discussion'):
                try:
                    reply_subject = f"Re: {post_subject}"
                    reply_result = self.moodle_client.add_discussion_post(
                        discussion_id=post['discussion'],
                        subject=reply_subject,
                        message=reply_content,
                        parent_id=post.get('id', 0)
                    )
                    result['auto_replied'] = True
                    result['reply_post_id'] = reply_result.get('postid')
                    self.logger.info(f"Auto-replied to post {post.get('id')}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to auto-reply to post {post.get('id')}: {e}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process post {post.get('id')}: {e}")
            return {
                'post_id': post.get('id'),
                'error': str(e),
                'processed_at': datetime.now().isoformat()
            }
    
    def process_forum_posts(self, course_id: int, forum_id: int = None, 
                           auto_reply: bool = False, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Process posts from a forum or all forums in a course
        
        Args:
            course_id: Moodle course ID
            forum_id: Specific forum ID (optional)
            auto_reply: Whether to automatically reply to posts
            limit: Maximum number of posts to process
            
        Returns:
            List of processing results
        """
        results = []
        
        try:
            if forum_id:
                forums = [{'id': forum_id}]
            else:
                forums = self.get_course_forums(course_id)
            
            for forum in forums:
                self.logger.info(f"Processing forum {forum['id']}")
                
                posts = self.get_recent_posts(forum['id'], limit)
                
                for post in posts:
                    # Skip posts by instructors/TAs (you might want to customize this logic)
                    if self._is_instructor_post(post):
                        continue
                    
                    result = self.process_post(post, auto_reply)
                    results.append(result)
                    
                    # Rate limiting to avoid overwhelming APIs
                    time.sleep(1)
            
            self.logger.info(f"Processed {len(results)} posts total")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to process forum posts: {e}")
            return results
    
    def _is_instructor_post(self, post: Dict[str, Any]) -> bool:
        """
        Determine if a post is from an instructor/TA
        
        Args:
            post: Post data
            
        Returns:
            True if post is from instructor/TA
        """
        # This is a simple check - you might want to enhance this
        # based on user roles or specific user IDs
        author = post.get('author', {})
        author_name = author.get('fullname', '').lower()
        
        # Skip posts from admin/instructor accounts
        instructor_keywords = ['admin', 'instructor', 'teacher', 'ta']
        return any(keyword in author_name for keyword in instructor_keywords)
    
    def generate_summary_report(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate a summary report of processing results
        
        Args:
            results: Processing results
            
        Returns:
            Summary report as string
        """
        total_posts = len(results)
        successful = len([r for r in results if 'error' not in r])
        auto_replied = len([r for r in results if r.get('auto_replied', False)])
        
        report = f"""
Moodle AI Processor Summary Report
================================

Total posts processed: {total_posts}
Successful: {successful}
Failed: {total_posts - successful}
Auto-replied: {auto_replied}

Processing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        if total_posts - successful > 0:
            report += "\nErrors encountered:\n"
            for result in results:
                if 'error' in result:
                    report += f"- Post {result.get('post_id')}: {result['error']}\n"
        
        return report
