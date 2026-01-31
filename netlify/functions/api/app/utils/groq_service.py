import os
from groq import Groq
from typing import List, Dict, Optional

class GroqService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            self.client = None
            print("Warning: GROQ_API_KEY not found")
        else:
            self.client = Groq(api_key=api_key)
            
        self.model = "llama-3.3-70b-versatile" # Current stable model

    def generate_response(self, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        if not self.client:
            raise ValueError("Groq API key not configured")

        try:
            messages = []
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get('role', 'user')
                    # Groq supports 'user', 'assistant', 'system'
                    messages.append({"role": role, "content": msg.get('message', '')})
            
            messages.append({"role": "user", "content": message})

            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
            )
            
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Error generating Groq response: {e}")
            raise e

_service = None
def get_groq_service():
    global _service
    if _service is None:
        _service = GroqService()
    return _service
