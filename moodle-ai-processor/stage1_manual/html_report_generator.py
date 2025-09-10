#!/usr/bin/env python3
"""
HTML Report Generator for Student Outline Feedback

Generates HTML feedback reports that can be posted to Moodle forums,
providing individual feedback to each student with improvement suggestions.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup


class HTMLReportGenerator:
    """Generate HTML reports for student outline feedback"""
    
    def __init__(self):
        self.report_template = self._create_report_template()
        self.individual_template = self._create_individual_template()
    
    def _create_report_template(self) -> str:
        """Create the main HTML template for the feedback report"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Outline Feedback Report - Week 1 Section 38</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f7fa;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .content {{
            padding: 30px;
        }}
        .summary-box {{
            background: #f8f9fa;
            border-left: 5px solid #007bff;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .student-feedback {{
            margin: 30px 0;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
        }}
        .student-header {{
            background: #007bff;
            color: white;
            padding: 15px 20px;
            font-weight: bold;
            font-size: 1.2em;
        }}
        .feedback-content {{
            padding: 20px;
        }}
        .score-badge {{
            background: #28a745;
            color: white;
            padding: 5px 15px;
            border-radius: 15px;
            font-weight: bold;
            float: right;
        }}
        .score-badge.low {{
            background: #dc3545;
        }}
        .score-badge.medium {{
            background: #ffc107;
            color: #333;
        }}
        .strengths {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
        }}
        .improvements {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
        }}
        .suggestions {{
            background: #e2e3e5;
            border: 1px solid #d6d8db;
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
        }}
        .section-title {{
            font-weight: bold;
            margin-bottom: 10px;
            color: #495057;
        }}
        ul {{
            margin: 0;
            padding-left: 20px;
        }}
        li {{
            margin: 5px 0;
        }}
        .class-overview {{
            background: #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .priority-box {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
        }}
        .next-steps {{
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
        }}
        .footer {{
            background: #6c757d;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 5px;
            }}
            .header {{
                padding: 20px;
            }}
            .header h1 {{
                font-size: 2em;
            }}
            .content {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📝 Outline Feedback Report</h1>
            <p>Week 1: Internet Benefits vs Risks - Section 38</p>
            <p>Generated on {{report_date}}</p>
        </div>
        
        <div class="content">
            {{content}}
        </div>
        
        <div class="footer">
            <p>💡 Remember: This feedback is designed to help you improve your outline structure and argumentation skills. 
            Please review the suggestions carefully and apply them to your revised outline.</p>
            <p><strong>Next steps:</strong> Revise your outline based on this feedback and submit your improved version by the deadline.</p>
        </div>
    </div>
</body>
</html>'''
    
    def _create_individual_template(self) -> str:
        """Create template for individual student feedback"""
        return '''<div class="student-feedback">
    <div class="student-header">
        {{student_name}}
        <span class="score-badge {{score_class}}">{{score}}</span>
    </div>
    <div class="feedback-content">
        {{feedback_sections}}
    </div>
</div>'''
    
    def _get_score_class(self, score_str: str) -> str:
        """Determine CSS class based on score"""
        try:
            if '/' in score_str:
                score = float(score_str.split('/')[0])
                if score >= 7:
                    return ""  # high (green)
                elif score >= 4:
                    return "medium"  # medium (yellow)
                else:
                    return "low"  # low (red)
        except:
            pass
        return "medium"
    
    def _create_feedback_sections(self, feedback: Dict[str, Any]) -> str:
        """Create HTML sections for individual feedback"""
        sections = []
        
        # Strengths section
        if feedback.get('strengths'):
            strengths_html = '<div class="strengths">'
            strengths_html += '<div class="section-title">✅ Strengths</div>'
            strengths_html += '<ul>'
            for strength in feedback['strengths']:
                strengths_html += f'<li>{strength}</li>'
            strengths_html += '</ul></div>'
            sections.append(strengths_html)
        
        # Areas for improvement
        if feedback.get('areas_for_improvement'):
            improvements_html = '<div class="improvements">'
            improvements_html += '<div class="section-title">📋 Areas for Improvement</div>'
            improvements_html += '<ul>'
            for improvement in feedback['areas_for_improvement']:
                improvements_html += f'<li>{improvement}</li>'
            improvements_html += '</ul></div>'
            sections.append(improvements_html)
        
        # Specific feedback sections
        feedback_sections = [
            ('thesis_feedback', '🎯 Thesis Statement Feedback'),
            ('structure_feedback', '🏗️ Structure & Organization'),
            ('evidence_feedback', '📊 Evidence & Examples')
        ]
        
        for key, title in feedback_sections:
            if feedback.get(key):
                section_html = f'<div class="suggestions">'
                section_html += f'<div class="section-title">{title}</div>'
                section_html += f'<p>{feedback[key]}</p></div>'
                sections.append(section_html)
        
        # Suggestions
        if feedback.get('suggestions'):
            suggestions_html = '<div class="suggestions">'
            suggestions_html += '<div class="section-title">💡 Specific Suggestions</div>'
            suggestions_html += '<ul>'
            for suggestion in feedback['suggestions']:
                suggestions_html += f'<li>{suggestion}</li>'
            suggestions_html += '</ul></div>'
            sections.append(suggestions_html)
        
        # Comparison to sample
        if feedback.get('comparison_to_sample'):
            comparison_html = '<div class="suggestions">'
            comparison_html += '<div class="section-title">📏 Comparison to Sample Standard</div>'
            comparison_html += f'<p>{feedback["comparison_to_sample"]}</p></div>'
            sections.append(comparison_html)
        
        return ''.join(sections)
    
    def _create_class_overview(self, aggregate: Dict[str, Any]) -> str:
        """Create class overview section"""
        if not aggregate or 'error' in aggregate:
            return '<div class="summary-box"><h3>⚠️ Class Overview Not Available</h3><p>Unable to generate class overview due to processing errors.</p></div>'
        
        overview_html = '<div class="class-overview">'
        overview_html += '<h3>📊 Class Overview</h3>'
        
        # Basic stats
        class_info = aggregate.get('class_overview', {})
        overview_html += f'<p><strong>Total Students Analyzed:</strong> {class_info.get("total_students", "N/A")}</p>'
        overview_html += f'<p><strong>Average Performance:</strong> {class_info.get("average_performance", "N/A")}</p>'
        overview_html += f'<p><strong>Overall Readiness:</strong> {class_info.get("overall_readiness", "N/A")}</p>'
        
        # Common strengths
        if aggregate.get('common_strengths'):
            overview_html += '<div class="strengths">'
            overview_html += '<div class="section-title">✅ Common Strengths Across Class</div>'
            overview_html += '<ul>'
            for strength in aggregate['common_strengths']:
                overview_html += f'<li>{strength}</li>'
            overview_html += '</ul></div>'
        
        # Teaching priorities
        if aggregate.get('teaching_priorities'):
            overview_html += '<div class="priority-box">'
            overview_html += '<div class="section-title">🎯 Teaching Priorities for Next Class</div>'
            overview_html += '<ul>'
            for priority in aggregate['teaching_priorities']:
                overview_html += f'<li>{priority}</li>'
            overview_html += '</ul></div>'
        
        # Next steps
        if aggregate.get('next_steps'):
            overview_html += '<div class="next-steps">'
            overview_html += '<div class="section-title">🚀 Recommended Next Steps</div>'
            overview_html += '<ul>'
            for step in aggregate['next_steps']:
                overview_html += f'<li>{step}</li>'
            overview_html += '</ul></div>'
        
        overview_html += '</div>'
        return overview_html
    
    def generate_feedback_report(self, analysis_data: Dict[str, Any], output_file: str = None) -> str:
        """
        Generate complete HTML feedback report
        
        Args:
            analysis_data: The processed analysis data from outline_feedback_processor
            output_file: Optional path to save the HTML file
        
        Returns:
            HTML content as string
        """
        content_sections = []
        
        # Add summary information
        task_info = analysis_data.get('task_info', {})
        summary_html = f'''<div class="summary-box">
            <h3>📋 Assignment Summary</h3>
            <p><strong>Topic:</strong> {task_info.get('topic', 'Outline Writing Exercise')}</p>
            <p><strong>Total Posts:</strong> {task_info.get('total_posts', 'N/A')}</p>
            <p><strong>Student Outlines Analyzed:</strong> {task_info.get('student_outlines', 'N/A')}</p>
            <p><strong>Analysis Date:</strong> {task_info.get('processing_timestamp', 'N/A')}</p>
        </div>'''
        content_sections.append(summary_html)
        
        # Add class overview
        aggregate_analysis = analysis_data.get('aggregate_analysis', {})
        content_sections.append(self._create_class_overview(aggregate_analysis))
        
        # Add individual feedback sections
        individual_feedbacks = analysis_data.get('individual_feedbacks', [])
        
        if individual_feedbacks:
            content_sections.append('<h2>👥 Individual Student Feedback</h2>')
            
            # Sort by student name for consistent ordering
            sorted_feedbacks = sorted(individual_feedbacks, key=lambda x: x.get('student_name', ''))
            
            for feedback in sorted_feedbacks:
                if 'error' in feedback:
                    # Handle error cases
                    error_html = f'''<div class="student-feedback">
                        <div class="student-header">
                            {feedback.get('student_name', 'Unknown Student')}
                            <span class="score-badge low">Error</span>
                        </div>
                        <div class="feedback-content">
                            <div class="improvements">
                                <div class="section-title">⚠️ Processing Error</div>
                                <p>Unable to generate feedback: {feedback['error']}</p>
                            </div>
                        </div>
                    </div>'''
                    content_sections.append(error_html)
                elif 'parsing_error' in feedback:
                    # Handle JSON parsing errors with raw feedback
                    raw_feedback = feedback.get('raw_feedback', 'No feedback available')
                    parsing_html = f'''<div class="student-feedback">
                        <div class="student-header">
                            {feedback.get('student_name', 'Unknown Student')}
                            <span class="score-badge medium">Review Needed</span>
                        </div>
                        <div class="feedback-content">
                            <div class="suggestions">
                                <div class="section-title">📝 Feedback (Manual Review Required)</div>
                                <p>{raw_feedback}</p>
                            </div>
                        </div>
                    </div>'''
                    content_sections.append(parsing_html)
                else:
                    # Normal feedback processing
                    score = feedback.get('overall_score', 'N/A')
                    score_class = self._get_score_class(score)
                    feedback_sections = self._create_feedback_sections(feedback)
                    
                    individual_html = self.individual_template.format(
                        student_name=feedback.get('student_name', 'Unknown Student'),
                        score=score,
                        score_class=score_class,
                        feedback_sections=feedback_sections
                    )
                    content_sections.append(individual_html)
        
        # Combine all content
        full_content = '\n'.join(content_sections)
        
        # Generate final HTML
        html_content = self.report_template.format(
            report_date=datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            content=full_content
        )
        
        # Save to file if requested
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"HTML report saved to: {output_path}")
        
        return html_content
    
    def generate_individual_student_reports(self, analysis_data: Dict[str, Any], output_dir: str = None) -> List[str]:
        """
        Generate individual HTML reports for each student
        
        Args:
            analysis_data: The processed analysis data
            output_dir: Directory to save individual reports
        
        Returns:
            List of file paths for generated reports
        """
        if output_dir is None:
            output_dir = Path(__file__).parent / "individual_reports"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        generated_files = []
        
        individual_feedbacks = analysis_data.get('individual_feedbacks', [])
        
        for feedback in individual_feedbacks:
            student_name = feedback.get('student_name', 'Unknown_Student')
            # Clean filename
            safe_name = re.sub(r'[^\w\s-]', '', student_name).strip().replace(' ', '_')
            
            # Create individual report with just this student's feedback
            individual_data = {
                'task_info': analysis_data.get('task_info', {}),
                'individual_feedbacks': [feedback],
                'aggregate_analysis': {}  # Skip aggregate for individual reports
            }
            
            # Generate HTML
            html_content = self.generate_feedback_report(individual_data)
            
            # Save file
            output_file = output_dir / f"{safe_name}_feedback.html"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            generated_files.append(str(output_file))
            print(f"Individual report generated for {student_name}: {output_file}")
        
        return generated_files


def main():
    """CLI entry point for HTML report generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate HTML feedback reports from outline analysis')
    parser.add_argument('analysis_file', help='Path to analysis JSON file')
    parser.add_argument('--output', '-o', help='Output HTML file path')
    parser.add_argument('--individual', '-i', action='store_true', help='Generate individual student reports')
    parser.add_argument('--output-dir', help='Output directory for individual reports')
    
    args = parser.parse_args()
    
    # Load analysis data
    try:
        with open(args.analysis_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
    except Exception as e:
        print(f"Error loading analysis file: {e}")
        return 1
    
    # Initialize generator
    generator = HTMLReportGenerator()
    
    # Generate main report
    if args.output:
        output_file = args.output
    else:
        # Auto-generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"outline_feedback_report_{timestamp}.html"
    
    try:
        html_content = generator.generate_feedback_report(analysis_data, output_file)
        print(f"Main feedback report generated: {output_file}")
        
        # Generate individual reports if requested
        if args.individual:
            individual_files = generator.generate_individual_student_reports(
                analysis_data, 
                args.output_dir
            )
            print(f"Generated {len(individual_files)} individual student reports")
        
    except Exception as e:
        print(f"Error generating reports: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
