"""
OpenRouter AI Client

This module provides a client for interacting with OpenRouter API for AI processing.
"""

import requests
import json
import logging
from typing import Dict, Any, List, Optional


class OpenRouterClient:
    """Client for OpenRouter AI API"""
    
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1", 
                 model: str = "anthropic/claude-3.5-sonnet"):
        """
        Initialize OpenRouter client
        
        Args:
            api_key: OpenRouter API key
            base_url: OpenRouter API base URL
            model: AI model to use
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://github.com/tesolchina/HKBUmoodle',
            'X-Title': 'HKBU Moodle AI Processor'
        }
    
    def generate_response(self, prompt: str, system_prompt: str = None, 
                         max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Generate AI response for a given prompt
        
        Args:
            prompt: User prompt/student post content
            system_prompt: System prompt to guide AI behavior
            max_tokens: Maximum tokens in response
            temperature: Randomness in response (0.0-1.0)
            
        Returns:
            AI-generated response
        """
        print(f"      🌐 Sending request to {self.model}...")
        print(f"      📝 Prompt length: {len(prompt)} characters")
        
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user", 
            "content": prompt
        })
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                response_text = result['choices'][0]['message']['content'].strip()
                print(f"      ✅ Received response: {len(response_text)} characters")
                
                # Show usage info if available
                if 'usage' in result:
                    usage = result['usage']
                    print(f"      📊 Tokens used: {usage.get('total_tokens', 'N/A')} (prompt: {usage.get('prompt_tokens', 'N/A')}, completion: {usage.get('completion_tokens', 'N/A')})")
                
                return response_text
            else:
                self.logger.error(f"Unexpected API response format: {result}")
                raise Exception("Invalid response format from OpenRouter API")
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"OpenRouter API request failed: {e}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            raise
    
    def analyze_student_post(self, post_content: str, context: str = None) -> Dict[str, Any]:
        """
        Analyze a student post and generate feedback
        
        Args:
            post_content: The student's post content
            context: Additional context (course info, assignment details, etc.)
            
        Returns:
            Analysis results including feedback and suggestions
        """
        system_prompt = """You are a helpful teaching assistant analyzing student posts. 
        Provide constructive feedback that:
        1. Acknowledges good points in the student's post
        2. Identifies areas for improvement
        3. Asks thoughtful follow-up questions
        4. Provides relevant suggestions or resources
        
        Be encouraging and supportive while maintaining academic standards."""
        
        prompt = f"Student Post: {post_content}"
        if context:
            prompt = f"Context: {context}\n\n{prompt}"
        
        prompt += "\n\nPlease analyze this post and provide constructive feedback."
        
        feedback = self.generate_response(prompt, system_prompt)
        
        return {
            "original_post": post_content,
            "feedback": feedback,
            "context": context,
            "model_used": self.model
        }
    
    def generate_reply(self, student_post: str, discussion_context: str = None, 
                      reply_style: str = "supportive") -> str:
        """
        Generate a reply to a student post
        
        Args:
            student_post: The student's original post
            discussion_context: Context from the discussion thread
            reply_style: Style of reply ("supportive", "questioning", "informative")
            
        Returns:
            Generated reply content
        """
        style_prompts = {
            "supportive": "Provide an encouraging and supportive response that validates the student's effort and offers constructive guidance.",
            "questioning": "Ask thoughtful questions that help the student think deeper about the topic and explore new perspectives.",
            "informative": "Provide additional information, examples, or resources that expand on the student's points."
        }
        
        system_prompt = f"""You are a teaching assistant responding to student posts. 
        {style_prompts.get(reply_style, style_prompts['supportive'])}
        
        Keep your response concise but meaningful, typically 2-4 sentences.
        Be professional yet friendly in tone."""
        
        prompt = f"Student wrote: \"{student_post}\""
        if discussion_context:
            prompt = f"Discussion context: {discussion_context}\n\n{prompt}"
        
        prompt += f"\n\nPlease write a {reply_style} response to this student."
        
        return self.generate_response(prompt, system_prompt, max_tokens=500)
    
    def moderate_content(self, content: str) -> Dict[str, Any]:
        """
        Check content for inappropriate material
        
        Args:
            content: Content to moderate
            
        Returns:
            Moderation results
        """
        system_prompt = """You are a content moderator for educational discussions. 
        Analyze the content for:
        1. Inappropriate language or content
        2. Academic integrity issues
        3. Spam or irrelevant content
        4. Potential safety concerns
        
        Respond with a brief assessment and severity level (low, medium, high)."""
        
        prompt = f"Please moderate this content: \"{content}\""
        
        assessment = self.generate_response(prompt, system_prompt, max_tokens=200)
        
        return {
            "content": content,
            "assessment": assessment,
            "timestamp": "placeholder_for_timestamp"
        }
