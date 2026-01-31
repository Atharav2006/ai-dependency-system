from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from app.dependencies.auth import get_current_user
from app.utils.supabase_client import get_supabase_client
from datetime import datetime
import json

router = APIRouter(prefix="/gamification", tags=["gamification"])

# Badge Definitions
BADGES = {
    "first_step": {
        "name": "First Step",
        "description": "Completed your first AI session",
        "icon": "Footprints",
        "condition": lambda stats: stats.get("total_sessions", 0) >= 1
    },
    "sovereign_mind": {
        "name": "Sovereign Mind",
        "description": "Achieved < 30% dependency in a session",
        "icon": "Crown",
        "condition": lambda last_session: last_session.get("dependency_score", 100) < 30
    },
    "collaborator": {
        "name": "Collaborator",
        "description": "Achieved balanced dependency (30-60%)",
        "icon": "Handshake",
        "condition": lambda last_session: 30 <= last_session.get("dependency_score", 0) <= 60
    },
    "streak_master": {
        "name": "Streak Master",
        "description": "Maintained a 3-session streak",
        "icon": "Flame",
        "condition": lambda stats: stats.get("current_streak", 0) >= 3
    },
    "deep_thinker": {
        "name": "Deep Thinker",
        "description": "Score > 80% Understanding in a session",
        "icon": "Brain",
        "condition": lambda last_session: last_session.get("understanding_score", 0) > 80
    }
}

async def check_and_award_badges(user_id: str, token: str, session_data: dict = None):
    """
    Internal function to check and award badges.
    session_data: Optional dict containing metrics from the just-completed session.
    """
    try:
        supabase = get_supabase_client(token)
        
        # 1. Get or Create User Stats
        stats_res = supabase.table("user_stats").select("*").eq("user_id", user_id).single().execute()
        
        if not stats_res.data:
            # Initialize stats if not exist
            init_stats = {"user_id": user_id, "total_sessions": 0, "current_streak": 0}
            stats_res = supabase.table("user_stats").insert(init_stats).select().single().execute()
            
        stats = stats_res.data
        
        # 2. Update Stats (Total Sessions) if session_data provided
        if session_data:
            new_total = stats["total_sessions"] + 1
            # Simple streak logic: if last session was 'recently', increment. 
            # For MVP, just increment streak for every session to show progress easily.
            new_streak = stats["current_streak"] + 1
            
            update_data = {
                "total_sessions": new_total,
                "current_streak": new_streak,
                "last_session_at": datetime.now().isoformat()
            }
            stats_res = supabase.table("user_stats").update(update_data).eq("user_id", user_id).select().single().execute()
            stats = stats_res.data

        # 3. Fetch existing badges
        existing_badges_res = supabase.table("achievements").select("badge_type").eq("user_id", user_id).execute()
        existing_badges = {b["badge_type"] for b in existing_badges_res.data}
        
        new_badges = []
        
        # 4. Check Conditions
        # Check 'stats' based badges
        if "first_step" not in existing_badges and BADGES["first_step"]["condition"](stats):
            new_badges.append("first_step")
            
        if "streak_master" not in existing_badges and BADGES["streak_master"]["condition"](stats):
            new_badges.append("streak_master")

        # Check 'session' based badges
        if session_data:
            if "sovereign_mind" not in existing_badges and BADGES["sovereign_mind"]["condition"](session_data):
                new_badges.append("sovereign_mind")
            if "collaborator" not in existing_badges and BADGES["collaborator"]["condition"](session_data):
                new_badges.append("collaborator")
            if "deep_thinker" not in existing_badges and BADGES["deep_thinker"]["condition"](session_data):
                new_badges.append("deep_thinker")

        # 5. Award Badges
        for badge in new_badges:
            badge_entry = {
                "user_id": user_id,
                "badge_type": badge,
                "awarded_at": datetime.now().isoformat()
            }
            supabase.table("achievements").insert(badge_entry).execute()
            print(f"Awarded badge {badge} to user {user_id}")

    except Exception as e:
        print(f"Error checking badges: {e}")
        # Non-blocking error for game logic

@router.get("/achievements")
async def get_achievements(user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user.get("sub")
    token = user.get("access_token")
    
    try:
        supabase = get_supabase_client(token)
        
        # Fetch User Badges
        badges_res = supabase.table("achievements").select("*").eq("user_id", user_id).execute()
        user_badges = {b["badge_type"]: b["awarded_at"] for b in badges_res.data}
        
        # Fetch Stats
        stats_res = supabase.table("user_stats").select("*").eq("user_id", user_id).single().execute()
        stats = stats_res.data if stats_res.data else {"current_streak": 0, "total_sessions": 0}
        
        # Construct Response with all defined badges + status
        response_badges = []
        for key, definition in BADGES.items():
            response_badges.append({
                "id": key,
                "name": definition["name"],
                "description": definition["description"],
                "icon": definition["icon"],
                "unlocked": key in user_badges,
                "awarded_at": user_badges.get(key)
            })
            
        return {
            "stats": stats,
            "badges": response_badges
        }

    except Exception as e:
        print(f"Error fetching achievements: {e}")
        raise HTTPException(status_code=500, detail=str(e))
