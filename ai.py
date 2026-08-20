import os
import json

def get_study_plan(user_prompt, tasks):
    """
    Generate AI-powered study plan using Google Gemini API
    
    Set your API key as environment variable:
    export GOOGLE_API_KEY="your-api-key"
    
    Get free API key from: https://ai.google.dev
    """
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            return "⚠️ GOOGLE_API_KEY not set. Set it with: export GOOGLE_API_KEY='your-key'\n\nGet free API: https://ai.google.dev"
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Format tasks for the AI
        tasks_text = ""
        if tasks:
            tasks_text = "\n\nCurrent tasks:\n"
            for task in tasks:
                status = "✓" if task[5] == 'completed' else "○"
                tasks_text += f"- [{status}] {task[2]} (Due: {task[4]})\n"
        
        prompt = f"""You are a helpful study assistant for university students. 
        
A student asked: {user_prompt}

{tasks_text}

Provide helpful, practical study advice. Keep response concise (3-5 sentences max)."""
        
        response = model.generate_content(prompt)
        return response.text
        
    except ImportError:
        return """⚠️ Google AI library not installed. 

Install with: pip install google-generativeai

Then set your API key:
export GOOGLE_API_KEY="your-api-key"

Get free API from: https://ai.google.dev"""
    
    except Exception as e:
        return f"⚠️ Error: {str(e)}\n\nMake sure GOOGLE_API_KEY is set correctly."

def get_mock_study_plan(user_prompt, tasks):
    """Fallback mock response (when API not available)"""
    
    total_tasks = len(tasks)
    completed = len([t for t in tasks if t[5] == 'completed'])
    
    mock_response = f"""Here's my AI-powered study plan for you:

Based on your tasks, you have {total_tasks} total assignments with {completed} completed.

📚 Study Tips:
1. Start with your most urgent deadline
2. Break complex topics into smaller chunks
3. Use the Pomodoro technique (25 min focus, 5 min break)
4. Review your completed tasks to build momentum

Regarding your question about '{user_prompt[:30]}...': 
Focus on understanding core concepts first, then practice problems. Good luck! 🎯"""
    
    return mock_response
