import asyncio
import json
from unittest.mock import MagicMock, patch

# Mocking the dependencies to test logic in isolation
import sys
from types import ModuleType

# Create mock modules to satisfy imports in dependency_service
mock_supabase = ModuleType('app.utils.supabase_client')
mock_supabase.get_supabase_client = MagicMock()
sys.modules['app.utils.supabase_client'] = mock_supabase

mock_llm = ModuleType('app.utils.llm_factory')
mock_llm.get_llm_service = MagicMock()
sys.modules['app.utils.llm_factory'] = mock_llm

from app.utils.dependency_service import DependencyService

async def test_ai_scoring_parsing():
    service = DependencyService()
    
    # Mock LLM response with JSON in markdown
    service.llm.generate_response.return_value = """
    Random text before JSON.
    ```json
    {
      "dependency_score": 85,
      "dependency_label": "High",
      "understanding_score": 70,
      "capability_score": 60
    }
    ```
    Random text after.
    """
    
    logs = [
        {"role": "user", "message": "Help me with everything.", "created_at": "2023-01-01T10:00:00Z"},
        {"role": "assistant", "message": "Sure, I will.", "created_at": "2023-01-01T10:01:00Z"}
    ]
    metrics = {"message_count": 1, "avg_prompt_length": 25, "session_duration_seconds": 60}
    
    print("Testing AI Scoring Parsing...")
    result = await service._get_ai_scoring(logs, metrics)
    print(f"Result: {json.dumps(result, indent=2)}")
    
    assert result["dependency_score"] == 85
    assert result["dependency_label"] == "High"
    print("✅ AI Scoring Parsing Test Passed!")

async def test_raw_metrics_calculation():
    service = DependencyService()
    logs = [
        {"role": "user", "message": "Hello", "created_at": "2023-01-01T10:00:00Z"},
        {"role": "assistant", "message": "Hi", "created_at": "2023-01-01T10:00:30Z"},
        {"role": "user", "message": "Bye", "created_at": "2023-01-01T10:01:00Z"}
    ]
    
    print("\nTesting Raw Metrics Calculation...")
    metrics = service._calculate_raw_metrics(logs)
    print(f"Metrics: {json.dumps(metrics, indent=2)}")
    
    assert metrics["message_count"] == 2
    assert metrics["session_duration_seconds"] == 60.0
    print("✅ Raw Metrics Calculation Test Passed!")

if __name__ == "__main__":
    asyncio.run(test_ai_scoring_parsing())
    asyncio.run(test_raw_metrics_calculation())
