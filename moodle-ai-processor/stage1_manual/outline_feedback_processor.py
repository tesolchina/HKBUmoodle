#!/usr/bin/env python3
"""
Outline Feedback Processor

Processes student outlines from Moodle forum discussions and provides 
AI-generated feedback against a sample outline template.
"""

import json
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from src.ai_client import OpenRouterClient


class OutlineFeedbackProcessor:
    """Process student outlines and generate AI feedback"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """Initialize the outline feedback processor"""
        if not Path(config_path).exists():
            config_path = Path(__file__).parent.parent / config_path
        
        self.config_path = config_path
        self.config = self._load_config()
        self.ai_client = OpenRouterClient(
            api_key=self.config['openrouter']['api_key'],
            base_url=self.config['openrouter']['base_url'],
            model=self.config['openrouter']['model']
        )
        
        self.logger = logging.getLogger(__name__)
        
        # Load sample outline template
        self.sample_outline = self._load_sample_outline()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            raise
    
    def _load_sample_outline(self) -> str:
        """Load the sample outline HTML template"""
        sample_path = Path(__file__).parent / "uploads" / "sampleOutline.html"
        try:
            with open(sample_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Failed to load sample outline: {e}")
            return ""
    
    def parse_discussion_json(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse the nested JSON structure of forum discussion"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle nested array structure
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], list):
                    posts = data[0]
                else:
                    posts = data
            else:
                posts = []
            
            self.logger.info(f"Parsed {len(posts)} posts from {file_path}")
            return posts
        
        except Exception as e:
            self.logger.error(f"Failed to parse discussion JSON: {e}")
            return []
    
    def clean_html_content(self, html_content: str) -> str:
        """Clean HTML content and extract plain text"""
        if not html_content:
            return ""
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_student_outlines(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract student outlines from forum posts"""
        outlines = []
        
        # Skip the first post (instructor's prompt)
        student_posts = posts[1:] if len(posts) > 1 else []
        
        for post in student_posts:
            # Check if this is a student outline (not a reply to another student)
            if post.get('parent', 0) == posts[0]['id']:  # Reply to original instructor post
                outline_text = self.clean_html_content(post.get('message', ''))
                
                if outline_text and len(outline_text.strip()) > 50:  # Filter out very short posts
                    outline_data = {
                        'student_name': post.get('userfullname', 'Unknown'),
                        'post_id': post.get('id'),
                        'outline_text': outline_text,
                        'word_count': post.get('wordcount', 0),
                        'timestamp': post.get('created', 0)
                    }
                    outlines.append(outline_data)
        
        self.logger.info(f"Extracted {len(outlines)} student outlines")
        return outlines
    
    def generate_outline_feedback(self, student_outline: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI feedback for a single student outline"""
        
        # Create system prompt with sample outline context
        system_prompt = f"""You are an expert writing instructor providing detailed feedback on student essay outlines. 

CONTEXT:
- Topic: "Internet benefits vs risks - To what extent do you agree or disagree that the internet's benefits outweigh privacy and cybercrime risks?"
- This is an outline writing exercise where students should create structured outlines with thesis statements, topic sentences, and supporting examples.

SAMPLE OUTLINE STANDARDS (for reference):
{self.clean_html_content(self.sample_outline)}

Your task is to evaluate the student's outline and provide constructive feedback focusing on:

1. THESIS STATEMENT QUALITY
   - Is there a clear, specific thesis statement?
   - Does it take a clear position on the topic?
   - Is it sufficiently specific and arguable?

2. STRUCTURE AND ORGANIZATION  
   - Does the outline follow logical structure (intro, body paragraphs, conclusion)?
   - Are there clear topic sentences for body paragraphs?
   - Do the points flow logically?

3. EVIDENCE AND EXAMPLES
   - Are there specific, relevant examples?
   - Do examples effectively support the main points?
   - Are examples varied and substantial?

4. COHERENCE AND DEPTH
   - Do all points relate clearly to the thesis?
   - Is there sufficient depth of analysis?
   - Are counterarguments or risk management addressed?

5. TECHNICAL ASPECTS
   - Grammar, clarity, and academic writing conventions
   - Appropriate vocabulary and tone

Provide your feedback in this JSON format:
{{
    "overall_score": "score out of 10",
    "strengths": ["list of specific strengths"],
    "areas_for_improvement": ["list of specific issues to address"],
    "thesis_feedback": "specific feedback on thesis statement",
    "structure_feedback": "feedback on outline organization",
    "evidence_feedback": "feedback on examples and support",
    "suggestions": ["specific actionable suggestions for improvement"],
    "comparison_to_sample": "how this outline compares to the sample standard"
}}"""

        user_prompt = f"""Please evaluate this student outline:

STUDENT: {student_outline['student_name']}
WORD COUNT: {student_outline['word_count']}

OUTLINE CONTENT:
{student_outline['outline_text']}"""

        try:
            response = self.ai_client.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=1500
            )
            
            # Try to parse JSON response
            try:
                feedback = json.loads(response)
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured response
                feedback = {
                    "overall_score": "N/A",
                    "raw_feedback": response,
                    "parsing_error": "Could not parse JSON response"
                }
            
            # Add metadata
            feedback['student_name'] = student_outline['student_name']
            feedback['post_id'] = student_outline['post_id']
            feedback['processing_timestamp'] = datetime.now().isoformat()
            
            return feedback
            
        except Exception as e:
            self.logger.error(f"Error generating feedback for {student_outline['student_name']}: {e}")
            return {
                'student_name': student_outline['student_name'],
                'post_id': student_outline['post_id'],
                'error': str(e),
                'processing_timestamp': datetime.now().isoformat()
            }
    
    def generate_aggregate_analysis(self, feedbacks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate aggregate analysis of all student outlines"""
        
        # Collect all feedback for analysis
        valid_feedbacks = [f for f in feedbacks if 'error' not in f and 'areas_for_improvement' in f]
        
        if not valid_feedbacks:
            return {"error": "No valid feedbacks to analyze"}
        
        # Create comprehensive analysis prompt
        feedback_summary = []
        for feedback in valid_feedbacks:
            summary = {
                'student': feedback['student_name'],
                'score': feedback.get('overall_score', 'N/A'),
                'strengths': feedback.get('strengths', []),
                'issues': feedback.get('areas_for_improvement', [])
            }
            feedback_summary.append(summary)
        
        system_prompt = """You are an expert writing instructor analyzing patterns across multiple student outlines for the same assignment. 

Based on the individual feedback provided for each student, identify:

1. COMMON STRENGTHS across students
2. MOST FREQUENT ISSUES that need addressing
3. TEACHING PRIORITIES for the next class
4. SPECIFIC EXAMPLES of good practices to highlight
5. RECOMMENDATIONS for class-wide interventions

Provide your analysis in this JSON format:
{
    "class_overview": {
        "total_students": "number",
        "average_performance": "assessment",
        "overall_readiness": "assessment for next stage"
    },
    "common_strengths": ["list of patterns in good work"],
    "frequent_issues": [
        {
            "issue": "specific problem",
            "frequency": "how many students",
            "impact": "why this matters",
            "solution": "teaching strategy"
        }
    ],
    "teaching_priorities": ["what to focus on in next class"],
    "exemplary_work": ["examples of student work to highlight"],
    "intervention_needed": ["students who need individual help"],
    "class_discussion_topics": ["topics for peer discussion"],
    "next_steps": ["recommended follow-up activities"]
}"""

        user_prompt = f"""Analyze these student outline feedbacks:

TOTAL STUDENTS: {len(valid_feedbacks)}

INDIVIDUAL FEEDBACK SUMMARY:
{json.dumps(feedback_summary, indent=2)}

DETAILED FEEDBACK DATA:
{json.dumps(valid_feedbacks, indent=2)}"""

        try:
            response = self.ai_client.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            try:
                analysis = json.loads(response)
            except json.JSONDecodeError:
                analysis = {
                    "raw_analysis": response,
                    "parsing_error": "Could not parse JSON response"
                }
            
            # Add metadata
            analysis['processing_timestamp'] = datetime.now().isoformat()
            analysis['students_analyzed'] = len(valid_feedbacks)
            analysis['errors_encountered'] = len(feedbacks) - len(valid_feedbacks)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error generating aggregate analysis: {e}")
            return {
                'error': str(e),
                'processing_timestamp': datetime.now().isoformat()
            }
    
    def process_outline_discussion(self, json_file: str, output_dir: str = None) -> Dict[str, Any]:
        """
        Main processing function for outline discussion
        
        Args:
            json_file: Path to the discussion JSON file
            output_dir: Directory to save results (optional)
        
        Returns:
            Dictionary with individual feedbacks and aggregate analysis
        """
        if output_dir is None:
            output_dir = Path(__file__).parent / "processed"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Starting outline processing for {json_file}")
        
        # Parse discussion
        posts = self.parse_discussion_json(json_file)
        if not posts:
            return {"error": "No posts found in discussion file"}
        
        # Extract student outlines
        outlines = self.extract_student_outlines(posts)
        if not outlines:
            return {"error": "No student outlines found"}
        
        self.logger.info(f"Processing {len(outlines)} student outlines...")
        
        # Generate individual feedback
        individual_feedbacks = []
        for outline in outlines:
            self.logger.info(f"Processing outline for {outline['student_name']}")
            feedback = self.generate_outline_feedback(outline)
            individual_feedbacks.append(feedback)
        
        # Generate aggregate analysis
        self.logger.info("Generating aggregate analysis...")
        aggregate_analysis = self.generate_aggregate_analysis(individual_feedbacks)
        
        # Compile results
        results = {
            'task_info': {
                'topic': 'Internet benefits vs risks outline writing',
                'total_posts': len(posts),
                'student_outlines': len(outlines),
                'processing_timestamp': datetime.now().isoformat(),
                'source_file': json_file
            },
            'individual_feedbacks': individual_feedbacks,
            'aggregate_analysis': aggregate_analysis
        }
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"outline_feedback_analysis_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Results saved to {output_file}")
            results['output_file'] = str(output_file)
            
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")
            results['save_error'] = str(e)
        
        return results


def main():
    """CLI entry point for outline feedback processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process student outlines and generate AI feedback')
    parser.add_argument('json_file', help='Path to discussion JSON file')
    parser.add_argument('--output-dir', '-o', help='Output directory for results')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize processor and run
    processor = OutlineFeedbackProcessor()
    results = processor.process_outline_discussion(args.json_file, args.output_dir)
    
    if 'error' in results:
        print(f"Error: {results['error']}")
        return 1
    
    print(f"Processing completed!")
    print(f"- Analyzed {results['task_info']['student_outlines']} student outlines")
    if 'output_file' in results:
        print(f"- Results saved to: {results['output_file']}")
    
    return 0


if __name__ == '__main__':
    exit(main())
