import os
import anthropic
from typing import List, Dict, Optional

class ClaudeService:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            self.client = None
            print("Warning: ANTHROPIC_API_KEY not found")
        else:
            self.client = anthropic.Anthropic(api_key=api_key)
            
        self.model = "claude-3-5-sonnet-20241022" 

    def generate_response(self, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        if not self.client:
            raise ValueError("Anthropic API key not configured")

        try:
            messages = []
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get('role', 'user')
                    content = msg.get('message', '')
                    messages.append({"role": role, "content": content})
            
            messages.append({"role": "user", "content": message})

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=messages
            )
            
            if response.content and len(response.content) > 0:
                return response.content[0].text
            return ""
            
        except Exception as e:
            print(f"Error generating Claude response: {e}")
            raise e

_service = None
def get_claude_service():
    global _service
    if _service is None:
        _service = ClaudeService()
    return _service
