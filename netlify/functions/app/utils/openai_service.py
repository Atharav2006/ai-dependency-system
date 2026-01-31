import os
from openai import OpenAI
from typing import List, Dict, Optional

class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # We don't raise error here to allow other providers to work even if this one is missing
            self.client = None
            print("Warning: OPENAI_API_KEY not found")
        else:
            self.client = OpenAI(api_key=api_key)
            
        self.model = "gpt-4o" # Default model

    def generate_response(self, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        if not self.client:
            raise ValueError("OpenAI API key not configured")

        try:
            messages = []
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get('role', 'user')
                    # OpenAI uses 'assistant' for AI, 'user' for human
                    messages.append({"role": role, "content": msg.get('message', '')})
            
            messages.append({"role": "user", "content": message})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating OpenAI response: {e}")
            raise e

_service = None
def get_openai_service():
    global _service
    if _service is None:
        _service = OpenAIService()
    return _service
