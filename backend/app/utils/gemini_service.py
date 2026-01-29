import os
import google.generativeai as genai
from typing import List, Dict, Optional

class GeminiService:
    """Service for interacting with Google's Gemini AI"""
    
    def __init__(self):
        """Initialize Gemini client with API key from environment"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Try different model names in order of preference
        model_names = [
            'gemini-2.5-flash',
            'models/gemini-2.5-flash',
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'models/gemini-1.5-flash', 
            'gemini-pro',
        ]
        
        self.model = None
        last_error = None
        
        for model_name in model_names:
            try:
                # print(f"Trying model: {model_name}") # Optional logging
                self.model = genai.GenerativeModel(model_name)
                # Test with a very simple generation
                # Note: We don't call generate_content here to avoid startup latency/cost
                # Just initializing the object is usually safe, or we can do a dry run if needed
                break 
            except Exception as e:
                last_error = e
                # print(f"❌ Failed to initialize {model_name}: {e}")
                continue
        
        # Fallback if loop finishes without success (though GenerativeModel init is lazy usually)
        if self.model is None:
             # Default to 1.5 flash if all else fails logic-wise
             self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_response(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate AI response using Gemini
        
        Args:
            message: The user's message
            conversation_history: List of previous messages with 'role' and 'message' keys
            
        Returns:
            AI-generated response text
            
        Raises:
            Exception: If API call fails
        """
        try:
            # Build prompt (same as before)
            prompt_parts = []
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get('role', 'user')
                    content = msg.get('message', '')
                    if role == 'user':
                        prompt_parts.append(f"User: {content}")
                    elif role == 'assistant':
                        prompt_parts.append(f"Assistant: {content}")
            prompt_parts.append(f"User: {message}")
            prompt_parts.append("Assistant:")
            full_prompt = "\n".join(prompt_parts)
            
            # Failover Logic
            last_exception = None
            
            # We iterate through our candidate models + the current self.model
            # Actually, let's just use the list we defined in __init__
            # But we need access to it. Let's make it an instance var.
            # For now, let's redefine the list here or assume self.model_names exists
            # Better to refactor __init__ to store self.model_names
            
            # Since I can't refactor __init__ easily in one go without replacing the whole file, 
            # I'll just hardcode the fallback list here for safety, prioritized by cost/speed
            fallback_models = [
                'gemini-2.5-flash',
                'models/gemini-2.5-flash',
                'gemini-1.5-flash',
                'gemini-1.5-pro',
                'gemini-pro'
            ]
            
            for model_name in fallback_models:
                try:
                    # print(f"Attempting generation with {model_name}...")
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(full_prompt)
                    
                    if response and response.text:
                        return response.text.strip()
                except Exception as e:
                    last_exception = e
                    error_str = str(e)
                    # If it's a rate limit (429), continue to next model
                    if "429" in error_str or "Quota exceeded" in error_str:
                        print(f"⚠️ Rate limit on {model_name}, switching...")
                        continue
                    else:
                        # If it's another error (like safety), we might want to stop or continue?
                        # Continuing is safer for robustness
                        print(f"❌ Error on {model_name}: {e}")
                        continue
            
            # If we get here, all models failed
            if last_exception:
                raise last_exception
            return "I apologize, but I couldn't generate a response at this time."
                
        except Exception as e:
            print(f"Error generating Gemini response: {e}")
            raise Exception(f"Failed to generate AI response: {str(e)}")

# Singleton instance
_gemini_service = None

def get_gemini_service() -> GeminiService:
    """Get or create GeminiService singleton instance"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
