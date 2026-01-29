import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from app.utils.supabase_client import get_supabase_client
from app.utils.llm_factory import get_llm_service
import asyncio

logger = logging.getLogger(__name__)

class DependencyService:
    def __init__(self):
        """Initialize DependencyService with LLM and Supabase clients"""
        self.supabase = get_supabase_client()
        self.llm = get_llm_service()

    async def analyze_session(self, session_id: str, token: str = None) -> Dict[str, Any]:
        """
        Full analysis pipeline:
        1. Fetch session logs
        2. Calculate raw metrics
        3. Get AI scores
        4. Save to DB
        """
        try:
            # Use authenticated client if token provided, else default (which might fail RLS)
            client = get_supabase_client(token) if token else self.supabase
            
            # 1. Fetch logs
            response = client.table("session_logs") \
                .select("*") \
                .eq("session_id", session_id) \
                .order("created_at") \
                .execute()
            
            logs = response.data
            if not logs:
                return {"error": "No logs found for session"}

            # 2. Calculate Raw Metrics
            metrics = self._calculate_raw_metrics(logs)
            
            # 3. Get AI Scores
            ai_analysis = await self._get_ai_scoring(logs, metrics)
            
            # 4. Save to DB
            result = {
                "session_id": session_id,
                "dependency_score": ai_analysis.get("dependency_score", 0),
                "understanding_score": ai_analysis.get("understanding_score", 0),
                "capability_score": ai_analysis.get("capability_score", 0),
                "raw_metrics": metrics
            }
            
            # Save to DB using authenticated client (requires INSERT policy)
            client.table("session_metrics").insert(result).execute()
            
            return result

        except Exception as e:
            logger.error(f"Error analyzing session {session_id}: {e}")
            import traceback
            traceback.print_exc()
            raise e

    def _calculate_raw_metrics(self, logs: List[Dict]) -> Dict[str, Any]:
        user_msgs = [l for l in logs if l['role'] == 'user']
        ai_msgs = [l for l in logs if l['role'] == 'assistant']
        
        if not user_msgs:
            return {}

        # 1. Message Count
        msg_count = len(user_msgs)
        
        # 2. Avg Prompt Length
        total_chars = sum(len(m['message']) for m in user_msgs)
        avg_length = total_chars / msg_count if msg_count > 0 else 0
        
        # 3. Session Duration (if >1 message)
        duration_seconds = 0
        if len(logs) > 1:
            try:
                # Ensure we handle multiple ISO formats (Z or +00:00)
                start_str = logs[0]['created_at'].replace('Z', '+00:00')
                end_str = logs[-1]['created_at'].replace('Z', '+00:00')
                start = datetime.fromisoformat(start_str)
                end = datetime.fromisoformat(end_str)
                duration_seconds = (end - start).total_seconds()
            except Exception as e:
                logger.warning(f"Error calculating duration: {e}")

        return {
            "message_count": msg_count,
            "avg_prompt_length": round(avg_length, 2),
            "session_duration_seconds": round(duration_seconds, 2),
            "interaction_count": len(logs)
        }

    async def _get_ai_scoring(self, logs: List[Dict], metrics: Dict) -> Dict[str, Any]:
        """
        Asks Gemini to act as a psychologist/analyst to score the user.
        """
        conversation_text = ""
        for log in logs:
            role = "User" if log['role'] == "user" else "AI"
            conversation_text += f"{role}: {log['message']}\n"
            
        prompt = f"""
        You are an expert behavioral analyst and evaluator.

        Your task is to analyze the USER'S behavior, NOT the quality of the AI’s replies.

        You are given:
        1) The full User–AI conversation transcript
        2) Session statistics (message count, average length, duration)

        Session Metrics:
        - Message Count: {metrics.get('message_count')}
        - Avg Prompt Length: {metrics.get('avg_prompt_length')} chars
        - Duration: {metrics.get('session_duration_seconds')} seconds

        TRANSCRIPT:
        {conversation_text}

        You MUST strictly follow the scoring rubric below.
        Every score MUST be justified by observable user behavior.

        --------------------------------------------------
        SCORING DIMENSIONS
        --------------------------------------------------

        1) DEPENDENCY SCORE (0–100)
        Measure emotional and behavioral reliance on the AI.
        0–20  = Independent | 21–40 = Low | 41–60 = Moderate | 61–80 = High | 81–100 = Severe

        2) UNDERSTANDING SCORE (0–100)
        Measure how well the user comprehends and integrates information.
        0-20 = None | 41-60 = Basic | 81-100 = Deep

        3) CAPABILITY SCORE (0–100)
        Measure problem-solving ability, autonomy, and reasoning skill.
        0-20 = Unable | 41-60 = Intermediate | 81-100 = Expert

        --------------------------------------------------
        OUTPUT FORMAT (STRICT)
        --------------------------------------------------
        Return ONLY valid JSON.
        Do NOT include explanations or markdown.

        {{
          "dependency_score": <integer 0–100>,
          "dependency_label": "Low | Moderate | High | Severe",
          "understanding_score": <integer 0–100>,
          "capability_score": <integer 0–100>
        }}
        """
        
        try:
            # Clean up indentation in prompt to save tokens/confusion
            import textwrap
            prompt = textwrap.dedent(prompt)

            # Use generic generate_response (assumed thread-safe or synchronous wrapped in thread)
            text = await asyncio.to_thread(self.llm.generate_response, prompt)
            
            # Clean up markdown if present
            if "```json" in text:
                text = text.split("```json")[-1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            ai_analysis = json.loads(text.strip())
            
            return {
                "dependency_score": ai_analysis.get("dependency_score", 50),
                "dependency_label": ai_analysis.get("dependency_label", "Moderate"),
                "understanding_score": ai_analysis.get("understanding_score", 50),
                "capability_score": ai_analysis.get("capability_score", 50)
            }

        except Exception as e:
            logger.error(f"AI Scoring failed: {e}")
            import traceback
            traceback.print_exc()
            # Fallback scores
            return {
                "dependency_score": 50,
                "dependency_label": "Moderate",
                "understanding_score": 50,
                "capability_score": 50
            }

_service = None
def get_dependency_service():
    global _service
    if _service is None:
        _service = DependencyService()
    return _service
