# Moodle AI Processor

A two-stage tool for processing students' work in Moodle using AI (OpenRouter API).

## 🎯 Two-Stage Approach

### Stage 1: Manual File Processing
- Upload HTML files (saved from Moodle forums)
- Upload Word documents (from Moodle assignments)
- Process locally with AI for feedback, grading, or summarization
- **Perfect for**: Quick processing of exported content

### Stage 2: Automated API Processing  
- Direct integration with Moodle API
- Automatically read student posts from forums
- Generate and post AI responses back to Moodle
- **Perfect for**: Ongoing automated assistance

## 🚀 Quick Start

1. **Setup the project:**
   ```bash
   python main_new.py setup
   ```

2. **Check system status:**
   ```bash
   python main_new.py status
   ```

3. **Stage 1 (Manual files):**
   ```bash
   # Place files in stage1_manual/uploads/
   python main_new.py stage1 setup
   python main_new.py stage1 process --type feedback
   ```

4. **Stage 2 (API automation):**
   ```bash
   python main_new.py stage2 test
   python main_new.py stage2 process --course-id 99
   ```

## Project Structure

- `main.py` - Main entry point
- `config/` - Configuration files
- `src/` - Source code modules
  - `moodle_client.py` - Moodle API client
  - `ai_client.py` - OpenRouter AI client
  - `processor.py` - Main processing logic
- `tests/` - Unit tests
- `logs/` - Application logs

## API Documentation

- Moodle Web Services: https://docs.moodle.org/dev/Web_services
- OpenRouter API: https://openrouter.ai/docs
