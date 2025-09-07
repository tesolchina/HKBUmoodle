"""
AI Feedback Collector - Task 2: Collect and Analyze AI Feedback Messages
Identifies AI feedback posts, handles image submissions, and reports by section.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict

class AIFeedbackCollector:
    def __init__(self, json_file_path: str):
        """Initialize the collector with forum discussion data."""
        self.json_file_path = json_file_path
        self.posts = []
        self.load_data()
    
    def load_data(self):
        """Load and parse the JSON discussion data."""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle nested array structure
                if isinstance(data, list) and len(data) > 0:
                    if isinstance(data[0], list):
                        self.posts = data[0]  # Extract from nested array
                    else:
                        self.posts = data
                print(f"Loaded {len(self.posts)} posts from discussion data")
        except Exception as e:
            print(f"Error loading data: {e}")
            self.posts = []
    
    def clean_text(self, html_text: str) -> str:
        """Clean HTML and extract plain text."""
        if not html_text:
            return ""
        
        # Remove HTML tags
        clean = re.sub('<[^<]+?>', '', html_text)
        # Replace HTML entities
        clean = clean.replace('&nbsp;', ' ')
        clean = clean.replace('&amp;', '&')
        clean = clean.replace('&lt;', '<')
        clean = clean.replace('&gt;', '>')
        # Clean up whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean
    
    def count_words(self, text: str) -> int:
        """Count words in text."""
        if not text:
            return 0
        words = [w for w in text.split() if w.strip()]
        return len(words)
    
    def extract_section_from_text(self, text: str) -> str:
        """Extract section information from post content."""
        section_patterns = [
            r'Section\s*([A-Z0-9]+)',
            r'Sec\s*([A-Z0-9]+)', 
            r'Class\s*([A-Z0-9]+)',
            r'Group\s*([A-Z0-9]+)',
            r'section\s*([A-Z0-9]+)'
        ]
        
        for pattern in section_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "Unknown"
    
    def is_ai_feedback(self, post: Dict) -> Dict[str, Any]:
        """
        Determine if a post contains AI feedback and classify the type.
        Returns classification info including confidence level.
        """
        message = self.clean_text(post.get('message', ''))
        subject = post.get('subject', '')
        word_count = self.count_words(message)
        
        # AI feedback indicators
        ai_feedback_phrases = [
            'your outline', 'this outline', 'great work', 'well done',
            'excellent', 'good job', 'consider', 'suggestion', 'feedback',
            'improvement', 'strengthen', 'clarify', 'expand', 'develop',
            'thesis statement', 'topic sentence', 'supporting evidence',
            'conclusion', 'body paragraph', 'introduction', 'structure',
            'organization', 'flow', 'transition', 'coherence', 'clarity'
        ]
        
        # Check for AI feedback language patterns
        feedback_score = 0
        matched_phrases = []
        
        message_lower = message.lower()
        for phrase in ai_feedback_phrases:
            if phrase in message_lower:
                feedback_score += 1
                matched_phrases.append(phrase)
        
        # Additional patterns that suggest AI feedback
        if re.search(r'you (could|should|might|can) (consider|try|add|improve)', message_lower):
            feedback_score += 2
            matched_phrases.append("suggestion pattern")
        
        if re.search(r'(overall|in general|to summarize)', message_lower):
            feedback_score += 1
            matched_phrases.append("summary pattern")
        
        # Check if it's likely an image submission
        is_likely_image = self.is_likely_image_submission(message, subject, word_count)
        
        # Determine feedback type and confidence
        feedback_type = "none"
        confidence = "low"
        
        if is_likely_image['is_image']:
            feedback_type = "image_based"
            confidence = is_likely_image['confidence']
        elif feedback_score >= 3:
            feedback_type = "text_feedback"
            confidence = "high"
        elif feedback_score >= 1 and word_count > 30:
            feedback_type = "text_feedback"
            confidence = "medium"
        elif word_count > 100 and any(word in message_lower for word in ['feedback', 'comment', 'review']):
            feedback_type = "text_feedback"
            confidence = "medium"
        
        return {
            'is_feedback': feedback_type != "none",
            'feedback_type': feedback_type,
            'confidence': confidence,
            'feedback_score': feedback_score,
            'matched_phrases': matched_phrases,
            'word_count': word_count,
            'is_image': is_likely_image['is_image']
        }
    
    def is_likely_image_submission(self, message: str, subject: str, word_count: int) -> Dict[str, Any]:
        """
        Detect if a post likely contains an image submission.
        Near-empty messages often indicate image attachments that weren't captured in text.
        """
        
        # Very short messages might be image-only
        if word_count <= 5:
            return {
                'is_image': True,
                'confidence': 'high',
                'reason': 'very_short_message'
            }
        
        # Check for image-related keywords in short messages
        image_indicators = [
            'attached', 'image', 'picture', 'screenshot', 'photo',
            'see above', 'see below', 'shown', 'displayed'
        ]
        
        if word_count <= 15:
            for indicator in image_indicators:
                if indicator in message.lower():
                    return {
                        'is_image': True,
                        'confidence': 'high', 
                        'reason': f'short_message_with_{indicator}'
                    }
        
        # Check for HTML image tags or file references
        if re.search(r'<img|\.jpg|\.png|\.jpeg|\.gif', message, re.IGNORECASE):
            return {
                'is_image': True,
                'confidence': 'high',
                'reason': 'image_html_tags'
            }
        
        # Medium confidence: Short messages with feedback-like subjects
        if word_count <= 10 and any(word in subject.lower() for word in ['feedback', 'comment', 'review']):
            return {
                'is_image': True,
                'confidence': 'medium',
                'reason': 'short_with_feedback_subject'
            }
        
        return {
            'is_image': False,
            'confidence': 'low',
            'reason': 'sufficient_text_content'
        }
    
    def collect_ai_feedback_posts(self) -> List[Dict]:
        """Collect all posts that contain AI feedback."""
        ai_feedback_posts = []
        
        for post in self.posts:
            # Skip the initial instructor post
            if post.get('parent') == '0':
                continue
            
            feedback_analysis = self.is_ai_feedback(post)
            
            if feedback_analysis['is_feedback']:
                # Extract section info
                message = self.clean_text(post.get('message', ''))
                subject = post.get('subject', '')
                section = self.extract_section_from_text(message + " " + subject)
                
                feedback_post = {
                    'id': post.get('id'),
                    'userid': post.get('userid'),
                    'userfullname': post.get('userfullname', 'Anonymous'),
                    'subject': subject,
                    'message': message,
                    'section': section,
                    'created': post.get('created'),
                    'parent': post.get('parent'),
                    'feedback_analysis': feedback_analysis
                }
                
                ai_feedback_posts.append(feedback_post)
        
        return ai_feedback_posts
    
    def generate_feedback_report_by_section(self) -> Dict[str, Any]:
        """Generate a report of AI feedback submissions by section."""
        feedback_posts = self.collect_ai_feedback_posts()
        
        # Group by section
        sections = defaultdict(lambda: {
            'text_feedback': [],
            'image_feedback': [],
            'total_feedback': []
        })
        
        for post in feedback_posts:
            section = post['section']
            sections[section]['total_feedback'].append(post)
            
            if post['feedback_analysis']['feedback_type'] == 'text_feedback':
                sections[section]['text_feedback'].append(post)
            elif post['feedback_analysis']['feedback_type'] == 'image_based':
                sections[section]['image_feedback'].append(post)
        
        # Generate statistics
        section_stats = {}
        total_text_feedback = 0
        total_image_feedback = 0
        
        for section, data in sections.items():
            text_count = len(data['text_feedback'])
            image_count = len(data['image_feedback'])
            total_count = len(data['total_feedback'])
            
            total_text_feedback += text_count
            total_image_feedback += image_count
            
            section_stats[section] = {
                'total_feedback_posts': total_count,
                'text_feedback_count': text_count,
                'image_feedback_count': image_count,
                'students_with_feedback': len(set(p['userfullname'] for p in data['total_feedback'])),
                'text_feedback_details': [
                    {
                        'student': p['userfullname'],
                        'word_count': p['feedback_analysis']['word_count'],
                        'confidence': p['feedback_analysis']['confidence'],
                        'subject': p['subject'][:50] + '...' if len(p['subject']) > 50 else p['subject']
                    }
                    for p in data['text_feedback']
                ],
                'image_feedback_details': [
                    {
                        'student': p['userfullname'],
                        'reason': p['feedback_analysis'].get('reason', 'unknown'),
                        'confidence': p['feedback_analysis']['confidence'],
                        'subject': p['subject'][:50] + '...' if len(p['subject']) > 50 else p['subject']
                    }
                    for p in data['image_feedback']
                ]
            }
        
        report = {
            'summary': {
                'total_feedback_posts': len(feedback_posts),
                'total_text_feedback': total_text_feedback,
                'total_image_feedback': total_image_feedback,
                'sections_with_feedback': len(sections),
                'unique_students_providing_feedback': len(set(p['userfullname'] for p in feedback_posts))
            },
            'by_section': section_stats,
            'all_feedback_posts': feedback_posts
        }
        
        return report
    
    def save_ai_feedback_analysis(self, output_file: str):
        """Save AI feedback analysis to file for LLM processing."""
        feedback_report = self.generate_feedback_report_by_section()
        
        # Combine with metadata
        combined_report = {
            'ai_feedback_analysis': feedback_report,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'source_file': self.json_file_path,
                'analysis_type': 'Task 2 - AI Feedback Collection and Analysis'
            }
        }
        
        # Save as JSON for structured data
        json_output_file = output_file.replace('.txt', '.json') if output_file.endswith('.txt') else output_file + '.json'
        with open(json_output_file, 'w', encoding='utf-8') as f:
            json.dump(combined_report, f, indent=2, ensure_ascii=False)
        
        # Also save as human-readable text
        text_output_file = output_file.replace('.json', '.txt') if output_file.endswith('.json') else output_file + '.txt'
        with open(text_output_file, 'w', encoding='utf-8') as f:
            f.write("AI FEEDBACK COLLECTION AND ANALYSIS\n")
            f.write("=" * 40 + "\n\n")
            
            # Summary
            summary = feedback_report['summary']
            f.write("SUMMARY:\n")
            f.write("-" * 10 + "\n")
            f.write(f"Total Feedback Posts: {summary['total_feedback_posts']}\n")
            f.write(f"Text-based Feedback: {summary['total_text_feedback']}\n")
            f.write(f"Image-based Feedback: {summary['total_image_feedback']}\n")
            f.write(f"Sections with Feedback: {summary['sections_with_feedback']}\n")
            f.write(f"Unique Students Providing Feedback: {summary['unique_students_providing_feedback']}\n\n")
            
            # By Section Analysis
            f.write("FEEDBACK BY SECTION:\n")
            f.write("-" * 20 + "\n")
            for section, stats in feedback_report['by_section'].items():
                f.write(f"\nSection {section}:\n")
                f.write(f"  Total Feedback Posts: {stats['total_feedback_posts']}\n")
                f.write(f"  Text Feedback: {stats['text_feedback_count']}\n")
                f.write(f"  Image Feedback: {stats['image_feedback_count']}\n")
                f.write(f"  Students with Feedback: {stats['students_with_feedback']}\n")
                
                if stats['text_feedback_details']:
                    f.write("  Text Feedback Details:\n")
                    for detail in stats['text_feedback_details']:
                        f.write(f"    - {detail['student']}: {detail['word_count']} words ({detail['confidence']} confidence)\n")
                
                if stats['image_feedback_details']:
                    f.write("  Image Feedback Details:\n")
                    for detail in stats['image_feedback_details']:
                        f.write(f"    - {detail['student']}: {detail['reason']} ({detail['confidence']} confidence)\n")
        
        print(f"AI Feedback Analysis saved to:")
        print(f"  JSON: {json_output_file}")
        print(f"  Text: {text_output_file}")
        
        return json_output_file, text_output_file

if __name__ == "__main__":
    # Test with the current discussion file
    collector = AIFeedbackCollector("/workspaces/HKBUmoodle/moodle-ai-processor/stage1_manual/uploads/discussion-7Sept.json")
    
    # Generate and save reports
    json_file, text_file = collector.save_ai_feedback_analysis(
        "/workspaces/HKBUmoodle/moodle-ai-processor/stage1_manual/processed/task2_ai_feedback_analysis"
    )
    
    print("\nTask 2 Analysis Complete!")
