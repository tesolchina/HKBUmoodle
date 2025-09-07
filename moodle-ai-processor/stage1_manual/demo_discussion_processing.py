#!/usr/bin/env python3
"""
Demo script to test the discussion processor with the current JSON file
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / 'src'))
sys.path.append(str(project_root / 'stage1_manual'))

from process_discussions import preview_discussion_structure, process_single_discussion


def demo_discussion_processing():
    """Demonstrate the discussion processing capabilities"""
    
    print("🎯 Discussion Processing Demo")
    print("=" * 50)
    
    # File paths
    input_file = "/workspaces/HKBUmoodle/moodle-ai-processor/stage1_manual/uploads/discussion-7Sept.json"
    
    print(f"\n📁 Input file: {Path(input_file).name}")
    
    # Step 1: Preview the structure
    print("\n🔍 Step 1: Previewing Discussion Structure")
    print("-" * 40)
    
    discussion_data = preview_discussion_structure(input_file)
    
    if not discussion_data:
        print("❌ Failed to preview discussion structure")
        return
    
    # Step 2: Ask user if they want to proceed with full processing
    print(f"\n🤔 The discussion contains {discussion_data['metadata']['student_posts']} student posts")
    print("Full processing will generate comprehensive AI feedback using OpenRouter API.")
    
    proceed = input("\n📝 Proceed with full AI processing? (y/N): ").lower().strip()
    
    if proceed not in ['y', 'yes']:
        print("✋ Processing cancelled by user")
        return
    
    # Step 3: Full processing with AI feedback
    print("\n🚀 Step 2: Processing with AI Feedback")
    print("-" * 40)
    print("⏳ This may take several minutes depending on API response times...")
    
    try:
        results = process_single_discussion(input_file)
        
        if results:
            print(f"\n🎉 Processing completed successfully!")
            print(f"📊 Generated feedback components:")
            
            feedback_components = results['ai_feedback']['comprehensive_feedback']
            for component_name in feedback_components.keys():
                print(f"   ✅ {component_name.replace('_', ' ').title()}")
            
            # Show sample feedback
            if 'overall_assessment' in feedback_components:
                print(f"\n📝 Sample Overall Assessment (first 200 chars):")
                sample = feedback_components['overall_assessment'][:200] + "..."
                print(f"   {sample}")
            
            output_file = Path(input_file).parent.parent / "processed" / f"{Path(input_file).stem}_comprehensive_feedback.json"
            print(f"\n💾 Full results saved to: {output_file.name}")
            
        else:
            print("❌ Processing failed")
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return
    
    print("\n✨ Demo completed!")


def show_processing_plan():
    """Show the comprehensive processing plan"""
    
    print("📋 Comprehensive Discussion Processing Plan")
    print("=" * 60)
    
    plan = """
🎯 PHASE 1: Data Parsing and Structure Analysis
   • Parse nested JSON discussion structure
   • Filter personal information (userids, names) for privacy
   • Clean HTML content and extract plain text
   • Build hierarchical thread relationships (posts → replies)
   • Classify post types (instructor_prompt, student_outline, ai_feedback, etc.)
   • Analyze discussion timeline and engagement patterns

🎯 PHASE 2: Content Analysis and Classification  
   • Identify instructor context and assignment requirements
   • Extract student essay outlines and position statements
   • Categorize student arguments and reasoning patterns
   • Detect AI-human interaction patterns in the discussion
   • Map discussion flow through different phases

🎯 PHASE 3: AI-Powered Feedback Generation
   • Overall Discussion Assessment
     - Academic rigor and quality evaluation
     - Critical thinking evidence analysis
     - Engagement and participation patterns
   
   • Individual Student Analysis
     - Essay outline structure and clarity assessment  
     - Argument strength and evidence evaluation
     - Position statement coherence analysis
   
   • Academic Writing Quality Review
     - Grammar, syntax, and style assessment
     - Academic tone and register evaluation
     - Use of examples and evidence analysis
   
   • Learning Outcomes Assessment
     - Critical thinking skills demonstration
     - Essay structuring competency
     - Balanced argument construction ability
   
   • Engagement Pattern Analysis
     - Peer interaction quality assessment
     - Discussion progression through phases
     - Collaborative learning evidence

🎯 PHASE 4: Comprehensive Reporting
   • Structured feedback with specific recommendations
   • Individual student development insights
   • Class-level learning outcome achievement
   • Pedagogical insights for instructor improvement
   • Actionable suggestions for future discussions

🔧 TECHNICAL FEATURES:
   ✅ Privacy-compliant processing (personal info filtered)
   ✅ Scalable batch processing for multiple discussions
   ✅ Configurable AI models and parameters
   ✅ Detailed logging and error handling
   ✅ JSON output for integration with other systems
   ✅ Preview mode for structure analysis without API calls

📊 SAMPLE METRICS GENERATED:
   • Total posts and student participation rates
   • Discussion timeline and engagement periods
   • Post type distribution and interaction patterns
   • Word count analysis and content depth metrics
   • Learning objective achievement indicators
    """
    
    print(plan)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'plan':
        show_processing_plan()
    else:
        demo_discussion_processing()
