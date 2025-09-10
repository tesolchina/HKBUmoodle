# Student Outline Feedback System - Stage 1 Manual

This system processes student discussion forum posts from Moodle and generates AI-powered feedback on their essay outlines.

## Quick Start

### 1. Generate HTML Feedback Reports

```bash
cd /workspaces/HKBUmoodle/moodle-ai-processor/stage1_manual
python quick_report.py
```

This will automatically:
- Find the latest analysis file
- Generate a comprehensive HTML report (`moodle_feedback_report.html`)
- Create individual student reports in `individual_reports/` folder

### 2. Post to Moodle

#### Main Report
- Open `moodle_feedback_report.html` in your browser
- Copy the content and paste into a Moodle forum post
- This gives students an overview of class performance and individual feedback

#### Individual Reports  
- Each student gets a personalized HTML report
- Can be sent via Moodle messages or email
- Located in `individual_reports/[Student_Name]_feedback.html`

## Files Generated

### Main Report (`moodle_feedback_report.html`)
- Class overview and aggregate analysis
- Individual feedback for all students
- Teaching priorities and next steps
- Ready to post directly to Moodle forum

### Individual Reports (`individual_reports/`)
- Personalized feedback for each student
- Same structure but focused on individual performance
- Can be sent privately to students

## What the Reports Include

### For Each Student:
- **Overall Score** (out of 10)
- **Strengths** - What they did well
- **Areas for Improvement** - Specific issues to address
- **Thesis Feedback** - Specific guidance on thesis statement
- **Structure Feedback** - Organization and outline format
- **Evidence Feedback** - Examples and supporting details
- **Specific Suggestions** - Actionable improvement steps
- **Comparison to Sample** - How their work compares to the standard

### Class Overview:
- Average performance metrics
- Common strengths across students
- Frequent issues needing attention
- Teaching priorities for next class
- Recommended interventions
- Next steps for improvement

## System Architecture

```
uploads/discussion-week1-section38.json  →  AI Analysis  →  HTML Reports
                ↓                               ↓               ↓
        Raw Moodle Data              processed/*.json    *.html files
```

## File Structure

```
stage1_manual/
├── quick_report.py              # 🚀 Main script to run
├── html_report_generator.py     # HTML report generation
├── outline_feedback_processor.py# AI analysis (already run)
├── uploads/                     # Input data
│   ├── discussion-week1-section38.json
│   └── sampleOutline.html
├── processed/                   # Analysis results
│   └── outline_feedback_analysis_*.json
├── individual_reports/          # Individual student reports
│   └── [Student_Name]_feedback.html
└── moodle_feedback_report.html  # Main comprehensive report
```

## Tips for Moodle Posting

1. **Preview First**: Open HTML files in browser to check formatting
2. **Copy Content**: Copy the inner content (not the full HTML with head/body tags)
3. **Moodle Formatting**: Moodle will preserve most CSS styling
4. **Individual Delivery**: Send individual reports via Moodle messages for privacy

## Regenerating Reports

If you need to regenerate reports with different formatting:

```bash
# Using specific analysis file
python html_report_generator.py processed/outline_feedback_analysis_20250910_072551.json --output new_report.html --individual

# Quick regeneration with latest analysis
python quick_report.py
```

## Customization

The HTML templates in `html_report_generator.py` can be modified to:
- Change color schemes
- Add institution branding
- Modify feedback section layout
- Adjust responsive design for mobile

## Next Steps

After posting feedback:
1. Students review their individual feedback
2. Students revise their outlines based on suggestions
3. Peer review session using improved outlines
4. Final outline submission with revisions marked
