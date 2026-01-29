from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from app.dependencies.auth import get_current_user
from app.utils.supabase_client import get_supabase_client
from datetime import datetime, timedelta
import collections

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary")
async def get_analytics_summary(user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user.get("sub")
    token = user.get("access_token")
    
    try:
        supabase = get_supabase_client(token)
        
        # We need to join metrics with sessions to filter by user_id
        # Supabase-py doesn't do joins easily with .table().select() if RLS is on and we want to filter by related table
        # But we can select from session_metrics if session_id is in (select id from sessions where user_id = ...)
        
        # Actually, let's just get the metrics for the user's sessions
        metrics_res = supabase.table("session_metrics") \
            .select("*, sessions!inner(user_id)") \
            .eq("sessions.user_id", user_id) \
            .execute()
        
        data = metrics_res.data
        if not data:
            return {
                "total_sessions": 0,
                "avg_dependency": 0,
                "avg_understanding": 0,
                "avg_capability": 0,
                "recent_trend": "neutral"
            }
            
        total = len(data)
        avg_dep = sum(m["dependency_score"] for m in data) / total
        avg_und = sum(m["understanding_score"] for m in data) / total
        avg_cap = sum(m["capability_score"] for m in data) / total
        
        return {
            "total_sessions": total,
            "avg_dependency": round(avg_dep, 1),
            "avg_understanding": round(avg_und, 1),
            "avg_capability": round(avg_cap, 1),
            "metrics": data[-10:] # Last 10 for quick view
        }
        
    except Exception as e:
        print(f"Analytics summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends")
async def get_analytics_trends(user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user.get("sub")
    token = user.get("access_token")
    
    try:
        supabase = get_supabase_client(token)
        
        metrics_res = supabase.table("session_metrics") \
            .select("dependency_score, understanding_score, capability_score, created_at, sessions!inner(user_id)") \
            .eq("sessions.user_id", user_id) \
            .order("created_at") \
            .execute()
        
        data = metrics_res.data
        if not data:
            return {"daily": [], "monthly": []}
            
        # Group by day
        daily_stats = collections.defaultdict(list)
        for m in data:
            date_str = m["created_at"][:10] # YYYY-MM-DD
            daily_stats[date_str].append(m)
            
        daily_trends = []
        for date, items in sorted(daily_stats.items()):
            count = len(items)
            daily_trends.append({
                "date": date,
                "dependency": sum(i["dependency_score"] for i in items) / count,
                "understanding": sum(i["understanding_score"] for i in items) / count,
                "capability": sum(i["capability_score"] for i in items) / count,
                "session_count": count
            })
            
        # Group by month
        monthly_stats = collections.defaultdict(list)
        for m in data:
            month_str = m["created_at"][:7] # YYYY-MM
            monthly_stats[month_str].append(m)
            
        monthly_trends = []
        for month, items in sorted(monthly_stats.items()):
            count = len(items)
            monthly_trends.append({
                "month": month,
                "dependency": sum(i["dependency_score"] for i in items) / count,
                "understanding": sum(i["understanding_score"] for i in items) / count,
                "capability": sum(i["capability_score"] for i in items) / count,
                "session_count": count
            })

        # Individual sessions (latest 50)
        sessions_trends = []
        for m in data[-50:]:
            sessions_trends.append({
                "id": m.get("session_id"),
                "time": m["created_at"],
                "dependency": m["dependency_score"],
                "understanding": m["understanding_score"],
                "capability": m["capability_score"]
            })
            
        return {
            "sessions": sessions_trends,
            "daily": daily_trends,
            "monthly": monthly_trends
        }
        
    except Exception as e:
        print(f"Analytics trends error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
