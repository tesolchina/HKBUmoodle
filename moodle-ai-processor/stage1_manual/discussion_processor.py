"""
Forum Discussion Processor for LLM Feedback

This module specifically processes JSON forum discussion files and generates 
comprehensive AI feedback on student posts and interactions.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from src.ai_client import OpenRouterClient


class DiscussionProcessor:
    """Process forum discussion JSON files for AI feedback generation"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """Initialize the discussion processor"""
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
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            raise
    
    def parse_discussion_json(self, file_path: str) -> Dict[str, Any]:
        """
        Parse the nested JSON structure of forum discussion
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Structured discussion data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_content = f.read()
            
            # Handle nested array structure
            if json_content.strip().startswith('[['):
                data = json.loads(json_content)[0]  # Get first array element
            else:
                data = json.loads(json_content)
            
            return self._structure_discussion_data(data)
        
        except Exception as e:
            self.logger.error(f"Error parsing JSON: {e}")
            raise
    
    def _structure_discussion_data(self, raw_posts: List[Dict]) -> Dict[str, Any]:
        """
        Structure the raw post data into a hierarchical discussion format
        
        Args:
            raw_posts: List of raw post dictionaries
            
        Returns:
            Structured discussion with threads, participants, and content
        """
        posts = []
        thread_map = {}  # Map post IDs to their data
        
        # Filter personal info and clean posts
        for post_data in raw_posts:
            clean_post = self._sanitize_post(post_data)
            if clean_post and clean_post['has_content']:
                posts.append(clean_post)
                thread_map[clean_post['id']] = clean_post
        
        # Build thread hierarchy
        root_posts = []
        for post in posts:
            if post['parent'] == 0:
                post['replies'] = []
                root_posts.append(post)
            else:
                if post['parent'] in thread_map:
                    if 'replies' not in thread_map[post['parent']]:
                        thread_map[post['parent']]['replies'] = []
                    thread_map[post['parent']]['replies'].append(post)
        
        # Identify discussion context
        instructor_post = next((p for p in root_posts if self._is_instructor_post(p)), None)
        student_posts = [p for p in posts if not self._is_instructor_post(p)]
        
        return {
            'metadata': {
                'total_posts': len(posts),
                'root_posts': len(root_posts),
                'student_posts': len(student_posts),
                'processed_at': datetime.now().isoformat()
            },
            'instructor_context': instructor_post,
            'threaded_discussion': root_posts,
            'student_contributions': student_posts,
            'discussion_flow': self._analyze_discussion_flow(posts)
        }
    
    def _sanitize_post(self, post_data: Dict) -> Optional[Dict]:
        """
        Remove personal information and clean post content
        
        Args:
            post_data: Raw post data
            
        Returns:
            Sanitized post or None if no meaningful content
        """
        # Extract safe, anonymized content
        clean_post = {
            'id': post_data.get('id'),
            'discussion': post_data.get('discussion'),
            'parent': post_data.get('parent', 0),
            'created': post_data.get('created'),
            'modified': post_data.get('modified'),
            'subject': post_data.get('subject', '').strip(),
            'raw_message': post_data.get('message', ''),
            'wordcount': post_data.get('wordcount', 0),
            'charcount': post_data.get('charcount', 0)
        }
        
        # Clean HTML and extract text content
        if clean_post['raw_message']:
            soup = BeautifulSoup(clean_post['raw_message'], 'html.parser')
            clean_post['clean_message'] = soup.get_text().strip()
            
            # Extract any links or special formatting
            links = [a.get('href') for a in soup.find_all('a', href=True)]
            clean_post['contains_links'] = len(links) > 0
            clean_post['links'] = links
        else:
            clean_post['clean_message'] = ''
        
        # Add readable timestamp
        if clean_post['created']:
            try:
                clean_post['created_readable'] = datetime.fromtimestamp(clean_post['created']).strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, OSError):
                clean_post['created_readable'] = str(clean_post['created'])
        
        # Determine if post has meaningful content
        clean_post['has_content'] = (
            len(clean_post['clean_message']) > 15 and 
            clean_post['clean_message'].lower() not in ['1', 'test', 'ok', 'yes', 'no']
        )
        
        # Classify post type
        clean_post['post_type'] = self._classify_post_type(clean_post)
        
        return clean_post if clean_post['has_content'] else None
    
    def _classify_post_type(self, post: Dict) -> str:
        """
        Classify the type of post based on content patterns
        
        Args:
            post: Clean post data
            
        Returns:
            Post type classification
        """
        message = post['clean_message'].lower()
        subject = post['subject'].lower()
        
        # Identify different post types
        if 'outline' in message or 'position:' in message or 'reason1' in message:
            return 'student_outline'
        elif 'deepseek' in message or 'chatgpt' in message or 'ai' in message:
            return 'ai_feedback'
        elif post['parent'] == 0 and len(message) > 200:
            return 'instructor_prompt'
        elif 'agree' in message or 'disagree' in message:
            return 'student_response'
        elif post['parent'] > 0:
            return 'reply'
        else:
            return 'general_post'
    
    def _is_instructor_post(self, post: Dict) -> bool:
        """Check if a post is likely from an instructor"""
        # Look for instructor patterns in content
        message = post['clean_message'].lower()
        return (
            'first spend' in message or
            'reply to this post' in message or
            'pair up and discuss' in message or
            'you are an experienced' in message or
            len(message) > 300 and post['parent'] == 0
        )
    
    def _analyze_discussion_flow(self, posts: List[Dict]) -> Dict[str, Any]:
        """
        Analyze the temporal and thematic flow of the discussion
        
        Args:
            posts: List of clean posts
            
        Returns:
            Discussion flow analysis
        """
        # Sort posts by creation time
        sorted_posts = sorted(posts, key=lambda x: x['created'])
        
        # Analyze post types over time
        post_types = {}
        for post in sorted_posts:
            post_type = post['post_type']
            post_types[post_type] = post_types.get(post_type, 0) + 1
        
        # Identify discussion phases
        phases = []
        current_phase = None
        
        for post in sorted_posts[:10]:  # Look at first 10 posts for phase detection
            if post['post_type'] == 'instructor_prompt':
                current_phase = 'prompt_introduction'
            elif post['post_type'] == 'student_outline':
                current_phase = 'outline_submission'
            elif post['post_type'] == 'ai_feedback':
                current_phase = 'ai_feedback_phase'
            elif post['post_type'] == 'reply':
                current_phase = 'peer_discussion'
                
            if current_phase and (not phases or phases[-1] != current_phase):
                phases.append(current_phase)
        
        return {
            'post_type_distribution': post_types,
            'discussion_phases': phases,
            'total_timeline_hours': (sorted_posts[-1]['created'] - sorted_posts[0]['created']) // 3600 if len(sorted_posts) > 1 else 0,
            'most_active_period': self._find_most_active_period(sorted_posts)
        }
    
    def _find_most_active_period(self, posts: List[Dict]) -> Dict[str, Any]:
        """Find the most active discussion period"""
        if len(posts) < 2:
            return {'period': 'insufficient_data', 'post_count': len(posts)}
        
        # Group posts by hour
        hourly_counts = {}
        for post in posts:
            try:
                hour = datetime.fromtimestamp(post['created']).replace(minute=0, second=0, microsecond=0)
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
            except (ValueError, OSError):
                continue
        
        if not hourly_counts:
            return {'period': 'no_valid_timestamps', 'post_count': 0}
        
        most_active_hour = max(hourly_counts.items(), key=lambda x: x[1])
        
        return {
            'period': most_active_hour[0].strftime('%Y-%m-%d %H:00'),
            'post_count': most_active_hour[1],
            'total_active_hours': len(hourly_counts)
        }
    
    def generate_comprehensive_feedback(self, discussion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive LLM feedback on the forum discussion
        
        Args:
            discussion_data: Structured discussion data
            
        Returns:
            Comprehensive feedback analysis
        """
        feedback_components = {}
        
        # 1. Overall discussion quality assessment
        feedback_components['overall_assessment'] = self._generate_overall_feedback(discussion_data)
        
        # 2. Individual student post analysis
        feedback_components['individual_analysis'] = self._analyze_individual_contributions(
            discussion_data['student_contributions']
        )
        
        # 3. Academic writing quality feedback
        feedback_components['writing_quality'] = self._assess_academic_writing(
            discussion_data['student_contributions']
        )
        
        # 4. Discussion engagement patterns
        feedback_components['engagement_analysis'] = self._analyze_engagement_patterns(
            discussion_data
        )
        
        # 5. Learning objectives assessment
        feedback_components['learning_outcomes'] = self._assess_learning_outcomes(
            discussion_data
        )
        
        return {
            'discussion_metadata': discussion_data['metadata'],
            'feedback_generated_at': datetime.now().isoformat(),
            'comprehensive_feedback': feedback_components,
            'summary_insights': self._generate_summary_insights(feedback_components)
        }
    
    def _generate_overall_feedback(self, discussion_data: Dict[str, Any]) -> str:
        """Generate overall discussion quality feedback"""
        prompt = f"""
        Analyze this academic forum discussion about internet benefits vs. risks.
        
        Discussion Overview:
        - Total posts: {discussion_data['metadata']['total_posts']}
        - Student contributions: {discussion_data['metadata']['student_posts']}
        - Discussion phases: {discussion_data['discussion_flow']['discussion_phases']}
        
        Instructor Context: {discussion_data.get('instructor_context', {}).get('clean_message', 'Not available')[:500]}
        
        Provide a comprehensive assessment of:
        1. Overall discussion quality and academic rigor
        2. How well students engaged with the topic
        3. Evidence of critical thinking and analysis
        4. Areas for improvement in future discussions
        
        Format as a structured academic assessment.
        """
        
        try:
            return self.ai_client.generate_response(
                prompt=prompt,
                system_prompt="You are an experienced university instructor providing constructive feedback on student forum discussions. Focus on academic development and learning outcomes.",
                max_tokens=800,
                temperature=0.3
            )
        except Exception as e:
            self.logger.error(f"Error generating overall feedback: {e}")
            return "Error generating feedback"
    
    def _analyze_individual_contributions(self, student_posts: List[Dict]) -> Dict[str, Any]:
        """Analyze individual student contributions"""
        individual_feedback = {}
        
        # Group posts by discussion thread or similarity
        outline_posts = [p for p in student_posts if p['post_type'] == 'student_outline']
        response_posts = [p for p in student_posts if p['post_type'] == 'student_response']
        
        # Analyze outline quality
        for i, post in enumerate(outline_posts[:5], 1):  # Limit to first 5 for API efficiency
            prompt = f"""
            Analyze this student's essay outline for the topic: "Internet benefits vs. cybercrime risks"
            
            Student Outline:
            Subject: {post['subject']}
            Content: {post['clean_message']}
            Word Count: {post['wordcount']}
            
            Assess the outline on:
            1. Clarity of position/thesis
            2. Logical structure and organization  
            3. Quality of supporting reasons/examples
            4. Academic writing conventions
            5. Critical thinking depth
            
            Provide specific, actionable feedback for improvement.
            """
            
            try:
                feedback = self.ai_client.generate_response(
                    prompt=prompt,
                    system_prompt="You are a university writing instructor. Provide constructive, specific feedback that helps students improve their academic writing and critical thinking.",
                    max_tokens=600,
                    temperature=0.2
                )
                individual_feedback[f'outline_{i}'] = {
                    'post_id': post['id'],
                    'wordcount': post['wordcount'],
                    'feedback': feedback
                }
            except Exception as e:
                self.logger.error(f"Error analyzing outline {i}: {e}")
                continue
        
        return individual_feedback
    
    def _assess_academic_writing(self, student_posts: List[Dict]) -> Dict[str, Any]:
        """Assess academic writing quality across posts"""
        writing_samples = []
        total_wordcount = 0
        
        for post in student_posts:
            if post['wordcount'] > 30:  # Focus on substantial posts
                writing_samples.append({
                    'content': post['clean_message'][:300],  # Truncate for API efficiency
                    'wordcount': post['wordcount'],
                    'post_type': post['post_type']
                })
                total_wordcount += post['wordcount']
        
        if not writing_samples:
            return {'assessment': 'Insufficient writing samples for analysis'}
        
        combined_samples = "\n\n---\n\n".join([s['content'] for s in writing_samples[:3]])
        
        prompt = f"""
        Assess the academic writing quality in these student forum posts about internet benefits vs. risks:
        
        {combined_samples}
        
        Total posts analyzed: {len(writing_samples)}
        Average word count: {total_wordcount // len(writing_samples)}
        
        Evaluate:
        1. Academic tone and register
        2. Grammar and sentence structure
        3. Use of evidence and examples
        4. Logical coherence and flow
        5. Vocabulary and terminology use
        
        Provide overall writing quality assessment and specific improvement recommendations.
        """
        
        try:
            assessment = self.ai_client.generate_response(
                prompt=prompt,
                system_prompt="You are an academic writing instructor. Focus on constructive feedback that helps students develop better academic writing skills.",
                max_tokens=700,
                temperature=0.2
            )
            
            return {
                'samples_analyzed': len(writing_samples),
                'average_wordcount': total_wordcount // len(writing_samples),
                'writing_assessment': assessment
            }
        except Exception as e:
            self.logger.error(f"Error assessing writing quality: {e}")
            return {'assessment': 'Error in analysis'}
    
    def _analyze_engagement_patterns(self, discussion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze student engagement patterns"""
        engagement_metrics = {
            'participation_rate': len(discussion_data['student_contributions']),
            'reply_interactions': len([p for p in discussion_data['student_contributions'] if p['parent'] > 0]),
            'discussion_phases': discussion_data['discussion_flow']['discussion_phases'],
            'post_type_distribution': discussion_data['discussion_flow']['post_type_distribution']
        }
        
        # Generate engagement analysis
        prompt = f"""
        Analyze student engagement patterns in this academic forum discussion:
        
        Metrics:
        - Total student posts: {engagement_metrics['participation_rate']}
        - Reply interactions: {engagement_metrics['reply_interactions']}
        - Discussion phases: {engagement_metrics['discussion_phases']}
        - Post types: {engagement_metrics['post_type_distribution']}
        
        Assess:
        1. Level of student participation and interaction
        2. Quality of peer-to-peer engagement
        3. Progression through discussion phases
        4. Evidence of collaborative learning
        5. Recommendations for improving engagement
        
        Focus on pedagogical insights for the instructor.
        """
        
        try:
            analysis = self.ai_client.generate_response(
                prompt=prompt,
                system_prompt="You are an educational researcher analyzing student engagement in online discussions. Provide insights that help instructors improve discussion quality.",
                max_tokens=600,
                temperature=0.3
            )
            
            return {
                'engagement_metrics': engagement_metrics,
                'engagement_analysis': analysis
            }
        except Exception as e:
            self.logger.error(f"Error analyzing engagement: {e}")
            return {'metrics': engagement_metrics, 'analysis': 'Error in analysis'}
    
    def _assess_learning_outcomes(self, discussion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess achievement of learning objectives"""
        student_posts = discussion_data['student_contributions']
        outline_posts = [p for p in student_posts if p['post_type'] == 'student_outline']
        
        # Extract learning evidence
        learning_evidence = []
        for post in outline_posts:
            if post['wordcount'] > 40:
                learning_evidence.append(post['clean_message'][:200])
        
        if not learning_evidence:
            return {'assessment': 'Insufficient evidence for learning outcome assessment'}
        
        evidence_text = "\n\n".join(learning_evidence[:4])
        
        prompt = f"""
        Assess learning outcomes based on student responses to the essay prompt about internet benefits vs. cybercrime risks:
        
        Student Evidence:
        {evidence_text}
        
        Evaluate evidence of:
        1. Critical thinking and analysis skills
        2. Ability to construct logical arguments
        3. Understanding of essay structure and organization
        4. Capacity for balanced evaluation of complex issues
        5. Academic writing development
        
        Provide specific evidence of learning achievement and areas needing development.
        Rate overall learning outcome achievement as: Excellent/Good/Satisfactory/Needs Improvement
        """
        
        try:
            assessment = self.ai_client.generate_response(
                prompt=prompt,
                system_prompt="You are an educational assessor evaluating student learning outcomes. Focus on evidence-based assessment of academic skills development.",
                max_tokens=700,
                temperature=0.2
            )
            
            return {
                'evidence_samples': len(learning_evidence),
                'learning_assessment': assessment
            }
        except Exception as e:
            self.logger.error(f"Error assessing learning outcomes: {e}")
            return {'assessment': 'Error in analysis'}
    
    def _generate_summary_insights(self, feedback_components: Dict[str, Any]) -> str:
        """Generate summary insights from all feedback components"""
        prompt = f"""
        Synthesize key insights from this comprehensive forum discussion analysis:
        
        Components analyzed:
        - Overall discussion quality
        - Individual student contributions  
        - Academic writing assessment
        - Engagement patterns
        - Learning outcomes
        
        Generate 5 key insights and 3 actionable recommendations for the instructor to improve future forum discussions.
        
        Focus on practical, evidence-based suggestions for enhancing student learning and engagement.
        """
        
        try:
            return self.ai_client.generate_response(
                prompt=prompt,
                system_prompt="You are an educational consultant providing strategic insights for improving online learning experiences.",
                max_tokens=500,
                temperature=0.4
            )
        except Exception as e:
            self.logger.error(f"Error generating summary insights: {e}")
            return "Error generating summary insights"

    def run_comprehensive_analysis(self, task1_path: str, task2_path: str, output_path: str):
        """
        Runs the comprehensive analysis by aggregating Task 1 and Task 2 results.
        """
        print("Executing Task 3: Comprehensive Analysis")
        
        # Load results from previous tasks
        try:
            with open(task1_path, 'r', encoding='utf-8') as f:
                task1_results = json.load(f)
            with open(task2_path, 'r', encoding='utf-8') as f:
                task2_results = json.load(f)
            print("Successfully loaded results from Task 1 and Task 2.")
        except Exception as e:
            self.logger.error(f"Failed to load task results: {e}")
            print(f"ERROR: Failed to load task results. Details: {e}")
            return

        # Aggregate data and generate prompts
        user_prompt = self._aggregate_data_for_llm(task1_results, task2_results)
        system_prompt = self._get_system_prompt_for_final_analysis()

        # Generate the final analysis from the LLM
        print("Sending aggregated data to LLM for final analysis...")
        final_analysis = self.ai_client.generate_response(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=4000,
            temperature=0.5
        )

        # Save the results
        self._save_final_report(final_analysis, user_prompt, system_prompt, output_path)

    def _aggregate_data_for_llm(self, task1_results: Dict, task2_results: Dict) -> str:
        """
        Combine data from Task 1 and Task 2 into a single prompt for the LLM.
        """
        print("Aggregating data for LLM prompt...")
        
        context = task1_results.get('contextual_overview', {})
        outline_analysis = task1_results.get('outline_submission_analysis', {})
        feedback_analysis = task2_results.get('ai_feedback_analysis', {})
        
        prompt = f"""
        # Comprehensive Analysis of Moodle Forum Discussion

        ## 1. Contextual Overview
        - **Discussion Title**: {context.get('discussion_title', 'N/A')}
        - **Total Posts**: {context.get('total_posts', 'N/A')}
        - **Unique Participants**: {context.get('unique_participants', 'N/A')}
        - **Date Range**: {context.get('date_range', {}).get('start')} to {context.get('date_range', {}).get('end')}

        ## 2. Outline Submission Analysis
        - **Total Outlines Identified**: {outline_analysis.get('summary', {}).get('total_outlines_identified', 'N/A')}
        - **Submission Summary by Section**:
        """
        
        for section, stats in outline_analysis.get('by_section', {}).items():
            prompt += f"  - **Section {section}**: {stats['student_count']} students, {stats['total_words']} total words, {stats['average_words']} avg words.\n"
            
        prompt += """
        ## 3. AI & Peer Feedback Analysis
        - **Total Feedback Posts**: {feedback_analysis_summary.get('total_feedback_posts', 'N/A')}
        - **Text-based Feedback**: {feedback_analysis_summary.get('total_text_feedback', 'N/A')}
        - **Image-based Feedback (Detected)**: {feedback_analysis_summary.get('total_image_feedback', 'N/A')}
        - **Feedback Summary by Section**:
        """.format(feedback_analysis_summary=feedback_analysis.get('summary', {}))

        for section, stats in feedback_analysis.get('by_section', {}).items():
            prompt += f"  - **Section {section}**: {stats['total_feedback_posts']} feedback posts ({stats['text_feedback_count']} text, {stats['image_feedback_count']} image).\n"

        prompt += "\n## 4. Detailed AI & Peer Feedback Content (Sample)\n"
        all_feedback_posts = feedback_analysis.get('all_feedback_posts', [])
        
        for i, post in enumerate(all_feedback_posts[:15]): # Limit to first 15 for brevity
            prompt += f"""
            ### Feedback Post {i+1}
            - **Student**: {post.get('userfullname')} | **Section**: {post.get('section')}
            - **Feedback Type**: {post.get('feedback_analysis', {}).get('feedback_type')} ({post.get('feedback_analysis', {}).get('confidence')} confidence)
            - **Message**: {post.get('message', 'N/A')[:800]}...
            ---
            """
        return prompt

    def _get_system_prompt_for_final_analysis(self) -> str:
        """
        Define the system prompt to guide the LLM's final analysis.
        """
        return """
        You are an expert educational analyst. Your task is to synthesize data from a Moodle forum discussion into a final report.

        Based on the provided data, generate a report with these sections:
        1.  **Executive Summary**: High-level overview of engagement and quality.
        2.  **Engagement & Participation Analysis**: Compare outline submissions vs. feedback provision. Identify active/inactive sections and students.
        3.  **Quality of Outlines & Feedback**: Infer quality from word counts and content. Assess if feedback is constructive. Provide examples of high-quality feedback.
        4.  **Key Insights & Pedagogical Recommendations**: Provide key takeaways and 2-3 actionable recommendations for the instructor to improve future discussions.

        Structure your response clearly using Markdown. Be data-driven and provide actionable insights.
        """

    def _save_final_report(self, final_analysis: str, user_prompt: str, system_prompt: str, output_path: str):
        """Saves the final analysis to JSON and text files."""
        report_data = {
            "final_analysis_report": final_analysis,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "source_files": [
                    "task1_contextual_overview.json",
                    "task2_ai_feedback_analysis.json"
                ],
                "llm_model": self.ai_client.model
            },
            "source_prompt": {
                "user_prompt": user_prompt,
                "system_prompt": system_prompt
            }
        }
        
        json_output_file = output_path.replace('.txt', '.json')
        with open(json_output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        text_output_file = output_path.replace('.json', '.txt')
        with open(text_output_file, 'w', encoding='utf-8') as f:
            f.write("FINAL COMPREHENSIVE ANALYSIS REPORT\n" + "="*40 + "\n\n" + final_analysis)
        
        print(f"Final analysis report saved to:\n  - JSON: {json_output_file}\n  - Text: {text_output_file}")


def main():
    """Main function to run the comprehensive analysis."""
    import os
    
    # Define paths
    CONFIG_PATH = "/workspaces/HKBUmoodle/moodle-ai-processor/config/config.json"
    TASK1_PATH = "/workspaces/HKBUmoodle/moodle-ai-processor/stage1_manual/processed/task1_contextual_overview.json"
    TASK2_PATH = "/workspaces/HKBUmoodle/moodle-ai-processor/stage1_manual/processed/task2_ai_feedback_analysis.json"
    FINAL_REPORT_PATH = "/workspaces/HKBUmoodle/moodle-ai-processor/stage1_manual/processed/final_discussion_analysis"
    
    if not os.path.exists(CONFIG_PATH):
        print(f"ERROR: Config file not found at {CONFIG_PATH}")
        return

    processor = DiscussionProcessor(config_path=CONFIG_PATH)
    processor.run_comprehensive_analysis(
        task1_path=TASK1_PATH,
        task2_path=TASK2_PATH,
        output_path=FINAL_REPORT_PATH
    )
    print("\nTask 3: Final Analysis Complete!")


if __name__ == "__main__":
    main()
