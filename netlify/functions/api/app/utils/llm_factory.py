import os
from app.utils.gemini_service import get_gemini_service
from app.utils.openai_service import get_openai_service
from app.utils.gemini_service import get_gemini_service
from app.utils.openai_service import get_openai_service
from app.utils.claude_service import get_claude_service
from app.utils.groq_service import get_groq_service

class LLMFactory:
    @staticmethod
    def get_llm_service(provider: str = None):
        """
        Get the LLM service instance based on provider name.
        Defaults to DEFAULT_LLM_PROVIDER env var, or 'gemini'.
        """
        if not provider:
            provider = os.getenv("DEFAULT_LLM_PROVIDER", "gemini")
            
        provider = provider.lower()
        
        if provider == "openai":
            return get_openai_service()
        elif provider == "claude" or provider == "anthropic":
            return get_claude_service()
        elif provider == "gemini":
            return get_gemini_service()
        elif provider == "groq":
            return get_groq_service()
        else:
            print(f"Unknown provider '{provider}', falling back to Gemini")
            return get_gemini_service()

def get_llm_service(provider: str = None):
    return LLMFactory.get_llm_service(provider)
