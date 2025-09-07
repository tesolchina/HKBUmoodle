"""
Outline Analyzer - Task 1: Contextual Overview and Outline Submission Analysis
Analyzes forum discussion data to generate reports on student outline submissions.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any
from collections import defaultdict, Counter

class OutlineAnalyzer:
    def __init__(self, json_file_path: str):
        """Initialize the analyzer with forum discussion data."""
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
        # Split by whitespace and filter out empty strings
        words = [w for w in text.split() if w.strip()]
        return len(words)
    
    def extract_section_from_text(self, text: str) -> str:
        """Extract section information from post content."""
        # Look for section patterns in the text
        section_patterns = [
            r'Section\s*([A-Z0-9]+)',
            r'Sec\s*([A-Z0-9]+)',
            r'Class\s*([A-Z0-9]+)',
            r'Group\s*([A-Z0-9]+)'
        ]
        
        for pattern in section_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "Unknown"
    
    def identify_outline_posts(self) -> List[Dict]:
        """Identify posts that contain student outlines."""
        outline_posts = []
        
        # Keywords that might indicate an outline submission
        outline_keywords = [
            'outline', 'plan', 'structure', 'thesis', 'introduction',
            'body paragraph', 'conclusion', 'topic sentence', 'main point',
            'argument', 'evidence', 'supporting details'
        ]
        
        for post in self.posts:
            # Skip the initial instructor post (usually the first one)
            if post.get('parent') == '0':
                continue
            
            message = self.clean_text(post.get('message', ''))
            subject = post.get('subject', '')
            
            # Check if it's likely an outline
            word_count = self.count_words(message)
            
            # Consider it an outline if:
            # 1. Has substantial content (more than 20 words)
            # 2. Contains outline-related keywords
            # 3. Is not just AI feedback (doesn't start with common AI phrases)
            
            has_outline_keywords = any(keyword in message.lower() for keyword in outline_keywords)
            is_substantial = word_count > 20
            
            # Check if it might be AI feedback instead
            ai_feedback_starters = [
                'your outline', 'this outline', 'great work', 'well done',
                'consider', 'suggestion', 'feedback', 'improvement'
            ]
            is_likely_ai_feedback = any(message.lower().startswith(starter) for starter in ai_feedback_starters)
            
            if is_substantial and (has_outline_keywords or not is_likely_ai_feedback):
                # Try to extract section info
                section = self.extract_section_from_text(message + " " + subject)
                
                outline_posts.append({
                    'id': post.get('id'),
                    'userid': post.get('userid'),
                    'userfullname': post.get('userfullname', 'Anonymous'),
                    'subject': subject,
                    'message': message,
                    'word_count': word_count,
                    'section': section,
                    'created': post.get('created'),
                    'parent': post.get('parent')
                })
        
        return outline_posts
    
    def generate_contextual_overview(self) -> Dict[str, Any]:
        """Generate a contextual overview of the discussion."""
        if not self.posts:
            return {"error": "No posts loaded"}
        
        # Find the instructor's initial post
        instructor_post = None
        for post in self.posts:
            if post.get('parent') == '0':  # Root post
                instructor_post = post
                break
        
        total_posts = len(self.posts)
        unique_users = len(set(post.get('userid') for post in self.posts if post.get('userid')))
        
        # Get date range
        timestamps = [int(post.get('created', 0)) for post in self.posts if post.get('created')]
        start_date = datetime.fromtimestamp(min(timestamps)) if timestamps else None
        end_date = datetime.fromtimestamp(max(timestamps)) if timestamps else None
        
        overview = {
            "discussion_title": instructor_post.get('subject', 'Unknown') if instructor_post else 'Unknown',
            "total_posts": total_posts,
            "unique_participants": unique_users,
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d %H:%M") if start_date else "Unknown",
                "end": end_date.strftime("%Y-%m-%d %H:%M") if end_date else "Unknown"
            },
            "instructor_prompt": self.clean_text(instructor_post.get('message', '')) if instructor_post else "Not found"
        }
        
        return overview
    
    def generate_outline_submission_report(self) -> Dict[str, Any]:
        """Generate a report on outline submissions by section."""
        outline_posts = self.identify_outline_posts()
        
        # Group by section
        sections = defaultdict(list)
        total_words_by_section = defaultdict(int)
        
        for outline in outline_posts:
            section = outline['section']
            sections[section].append(outline)
            total_words_by_section[section] += outline['word_count']
        
        # Generate summary statistics
        section_stats = {}
        for section, outlines in sections.items():
            section_stats[section] = {
                "student_count": len(outlines),
                "total_words": total_words_by_section[section],
                "average_words": round(total_words_by_section[section] / len(outlines), 1),
                "students": [
                    {
                        "name": outline['userfullname'],
                        "word_count": outline['word_count'],
                        "subject": outline['subject']
                    }
                    for outline in outlines
                ]
            }
        
        report = {
            "summary": {
                "total_outlines_identified": len(outline_posts),
                "sections_with_submissions": len(sections),
                "total_words_across_all_outlines": sum(total_words_by_section.values())
            },
            "by_section": section_stats,
            "detailed_outlines": outline_posts
        }
        
        return report
    
    def save_contextual_overview(self, output_file: str):
        """Save contextual overview to file for LLM processing."""
        overview = self.generate_contextual_overview()
        outline_report = self.generate_outline_submission_report()
        
        # Combine both reports
        combined_report = {
            "contextual_overview": overview,
            "outline_submission_analysis": outline_report,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "source_file": self.json_file_path,
                "analysis_type": "Task 1 - Contextual Overview and Outline Analysis"
            }
        }
        
        # Save as JSON for structured data
        json_output_file = output_file.replace('.txt', '.json') if output_file.endswith('.txt') else output_file + '.json'
        with open(json_output_file, 'w', encoding='utf-8') as f:
            json.dump(combined_report, f, indent=2, ensure_ascii=False)
        
        # Also save as human-readable text
        text_output_file = output_file.replace('.json', '.txt') if output_file.endswith('.json') else output_file + '.txt'
        with open(text_output_file, 'w', encoding='utf-8') as f:
            f.write("CONTEXTUAL OVERVIEW AND OUTLINE SUBMISSION ANALYSIS\n")
            f.write("=" * 55 + "\n\n")
            
            # Contextual Overview
            f.write("CONTEXTUAL OVERVIEW:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Discussion Title: {overview['discussion_title']}\n")
            f.write(f"Total Posts: {overview['total_posts']}\n")
            f.write(f"Unique Participants: {overview['unique_participants']}\n")
            f.write(f"Date Range: {overview['date_range']['start']} to {overview['date_range']['end']}\n\n")
            
            f.write("Instructor Prompt:\n")
            f.write(overview['instructor_prompt'][:500] + "...\n\n")
            
            # Outline Analysis
            f.write("OUTLINE SUBMISSION ANALYSIS:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total Outlines Identified: {outline_report['summary']['total_outlines_identified']}\n")
            f.write(f"Sections with Submissions: {outline_report['summary']['sections_with_submissions']}\n")
            f.write(f"Total Words Across All Outlines: {outline_report['summary']['total_words_across_all_outlines']}\n\n")
            
            # By Section
            f.write("SUBMISSIONS BY SECTION:\n")
            f.write("-" * 25 + "\n")
            for section, stats in outline_report['by_section'].items():
                f.write(f"\nSection {section}:\n")
                f.write(f"  Students: {stats['student_count']}\n")
                f.write(f"  Total Words: {stats['total_words']}\n")
                f.write(f"  Average Words: {stats['average_words']}\n")
                f.write("  Student Details:\n")
                for student in stats['students']:
                    f.write(f"    - {student['name']}: {student['word_count']} words\n")
        
        print(f"Reports saved to:")
        print(f"  JSON: {json_output_file}")
        print(f"  Text: {text_output_file}")
        
        return json_output_file, text_output_file

if __name__ == "__main__":
    # Test with the current discussion file
    analyzer = OutlineAnalyzer("/workspaces/HKBUmoodle/moodle-ai-processor/stage1_manual/uploads/discussion-7Sept.json")
    
    # Generate and save reports
    json_file, text_file = analyzer.save_contextual_overview(
        "/workspaces/HKBUmoodle/moodle-ai-processor/stage1_manual/processed/task1_contextual_overview"
    )
    
    print("\nTask 1 Analysis Complete!")
