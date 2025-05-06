import openai
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_ai_response(messages):
    try:
        response = openai.ChatCompletion.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI error: {str(e)}")
        
        # Find the last user message to determine language
        last_msg = next((m for m in reversed(messages) if m['role'] == 'user'), None)
        if last_msg:
            content = last_msg.get('content', '')
            if any('\u0900' <= c <= '\u097F' for c in content):
                return "क्षमा करें, तकनीकी समस्या आई है। कृपया बाद में प्रयास करें।"
            elif any('\u0C00' <= c <= '\u0C7F' for c in content):
                return "క్షమించండి, సాంకేతిక సమస్య ఉంది. దయచేసి తర్వాత ప్రయత్నించండి."
        
        return "Sorry, we're experiencing technical difficulties. Please try again later."