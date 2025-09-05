# Usage Examples

This document provides practical examples of how to use the Moodle AI Processor.

## Initial Setup

1. **Run the setup script:**
   ```bash
   python setup.py
   ```

2. **Or manually configure:**
   ```bash
   cp config/config.template.json config/config.json
   # Edit config/config.json with your credentials
   ```

## Basic Usage

### 1. Get Course Information

```bash
# Get basic course info
python main.py info --course-id 99
```

### 2. List Forums in a Course

```bash
# List all forums in a course
python main.py forums --course-id 99
```

### 3. Process Posts (Read-Only)

```bash
# Process posts without replying (safe mode)
python main.py process --course-id 99
```

### 4. Process Posts from Specific Forum

```bash
# Process only posts from forum ID 123
python main.py process --course-id 99 --forum-id 123
```

### 5. Process Posts with Auto-Reply

```bash
# CAUTION: This will post AI responses to Moodle!
python main.py process --course-id 99 --auto-reply
```

### 6. Limit Number of Posts

```bash
# Process only the 5 most recent posts
python main.py process --course-id 99 --limit 5
```

### 7. Save Results to File

```bash
# Save processing results to JSON file
python main.py process --course-id 99 --output results.json
```

### 8. Verbose Mode

```bash
# Enable detailed logging
python main.py process --course-id 99 --verbose
```

## Advanced Usage

### Combining Options

```bash
# Process 10 posts from a specific forum, auto-reply, save results, verbose
python main.py process \
    --course-id 99 \
    --forum-id 123 \
    --limit 10 \
    --auto-reply \
    --output detailed_results.json \
    --verbose
```

### Using Different Configuration Files

```bash
# Use a different config file
python main.py process --course-id 99 --config my_config.json
```

## Configuration Examples

### Basic Configuration (config/config.json)

```json
{
  "moodle": {
    "base_url": "https://your-moodle.edu",
    "token": "your_moodle_webservice_token",
    "username": "your_username",
    "password": "your_password"
  },
  "openrouter": {
    "api_key": "sk-or-v1-your-key-here",
    "base_url": "https://openrouter.ai/api/v1",
    "model": "anthropic/claude-3.5-sonnet"
  },
  "ai_settings": {
    "max_tokens": 1000,
    "temperature": 0.7,
    "system_prompt": "You are a helpful teaching assistant..."
  }
}
```

### Different AI Models

Popular models you can use:

```json
{
  "openrouter": {
    "model": "anthropic/claude-3.5-sonnet"     // Best for education
    "model": "openai/gpt-4"                    // High quality
    "model": "openai/gpt-3.5-turbo"          // Fast and economical
    "model": "meta-llama/llama-2-70b-chat"   // Open source
  }
}
```

### Custom System Prompts

Examples for different teaching styles:

```json
{
  "ai_settings": {
    "system_prompt": "You are a supportive teaching assistant. Focus on encouraging students while providing constructive feedback."
  }
}
```

```json
{
  "ai_settings": {
    "system_prompt": "You are a Socratic teaching assistant. Ask thoughtful questions that help students discover answers themselves."
  }
}
```

## Workflow Examples

### Daily Forum Monitoring

```bash
#!/bin/bash
# daily_check.sh - Check forums daily

COURSE_ID=99
DATE=$(date +%Y%m%d)

# Process recent posts and save results
python main.py process \
    --course-id $COURSE_ID \
    --limit 20 \
    --output "daily_reports/report_$DATE.json" \
    --verbose

echo "Daily check completed. Results saved to daily_reports/report_$DATE.json"
```

### Selective Auto-Reply

```bash
#!/bin/bash
# selective_reply.sh - Only auto-reply to specific forums

# Forums where auto-reply is safe
DISCUSSION_FORUMS=(123 124 125)

for forum_id in "${DISCUSSION_FORUMS[@]}"; do
    echo "Processing forum $forum_id..."
    python main.py process \
        --course-id 99 \
        --forum-id $forum_id \
        --auto-reply \
        --limit 5 \
        --output "forum_${forum_id}_replies.json"
done
```

## Safety Tips

### Before Using Auto-Reply

1. **Test in read-only mode first:**
   ```bash
   python main.py process --course-id 99 --verbose
   ```

2. **Check the AI responses manually before enabling auto-reply**

3. **Start with a small limit:**
   ```bash
   python main.py process --course-id 99 --auto-reply --limit 1
   ```

4. **Use specific forums for testing:**
   ```bash
   python main.py process --course-id 99 --forum-id 999 --auto-reply
   ```

### Monitoring and Logs

- Check logs in `logs/moodle_ai_processor.log`
- Review saved results files
- Monitor Moodle for posted responses

## Troubleshooting

### Common Issues

1. **Moodle connection failed:**
   - Check your base URL and token in config.json
   - Verify the course ID exists and you have access

2. **OpenRouter API errors:**
   - Check your API key
   - Verify you have credits/billing set up
   - Try a different model

3. **No posts found:**
   - Check if the course has forums
   - Verify forum permissions
   - Try a different course ID

### Getting Help

1. **Enable verbose logging:**
   ```bash
   python main.py process --course-id 99 --verbose
   ```

2. **Check the logs:**
   ```bash
   tail -f logs/moodle_ai_processor.log
   ```

3. **Test individual components:**
   ```bash
   python example.py
   ```
