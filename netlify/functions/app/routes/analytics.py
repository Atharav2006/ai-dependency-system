from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
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
            .select("dependency_score, understanding_score, capability_score, primary_dependency, secondary_dependency, created_at, sessions!inner(user_id)") \
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

        # Prediction Logic (Linear Projection for next 7 days/intervals)
        def generate_forecast(trend_list, key="dependency"):
            if len(trend_list) < 3:
                return []
            
            # Simple linear projection
            y = [t[key] for t in trend_list[-5:]] # Latest 5 points
            x = list(range(len(y)))
            
            avg_x = sum(x) / len(x)
            avg_y = sum(y) / len(y)
            
            num = sum((xi - avg_x) * (yi - avg_y) for xi, yi in zip(x, y))
            den = sum((xi - avg_x) ** 2 for xi in x)
            
            slope = num / den if den != 0 else 0
            intercept = avg_y - slope * avg_x
            
            forecast = []
            last_val = y[-1]
            for i in range(1, 4): # Project 3 steps forward
                next_val = max(0, min(100, intercept + slope * (len(x) + i)))
                forecast.append(round(next_val, 1))
            return forecast

        daily_forecast = generate_forecast(daily_trends, "dependency")
        monthly_forecast = generate_forecast(monthly_trends, "dependency")

        # --- EXCELLENCE PHASE 3: Density & Trends ---
        
        # 24-hour Density Mapping (Split by Daily/Monthly)
        today_str = datetime.utcnow().strftime('%Y-%m-%d')
        daily_density = [0] * 24
        monthly_density = [0] * 24
        
        for m in data:
            try:
                dt = datetime.fromisoformat(m["created_at"].replace('Z', '+00:00'))
                hour = dt.hour
                monthly_density[hour] += 1
                if m["created_at"].startswith(today_str):
                    daily_density[hour] += 1
            except:
                pass
        
        density_map = {
            "daily": daily_density,
            "monthly": monthly_density
        }
        
        # Comparative Logic
        def get_trends_comparative(current_list, prev_list):
            if not current_list or not prev_list:
                return {"dependency": 0, "capability": 0, "volume": 0}
            
            curr = current_list[-1]
            prev = prev_list[-1] if len(prev_list) > 1 else current_list[-2] if len(current_list) > 1 else curr
            
            def perc_diff(c, p):
                if p == 0: return 0
                return round(((c - p) / p) * 100, 1)

            return {
                "dependency": perc_diff(curr["dependency"], prev["dependency"]),
                "capability": perc_diff(curr["capability"], prev["capability"]),
                "volume": perc_diff(curr["session_count"], prev["session_count"])
            }

        daily_comparative = get_trends_comparative(daily_trends, []) 
        monthly_comparative = get_trends_comparative(monthly_trends, [])

        # Individual sessions (latest 200)
        sessions_trends = []
        for m in data[-200:]:
            sessions_trends.append({
                "id": m.get("session_id"),
                "time": m["created_at"],
                "dependency": m["dependency_score"],
                "understanding": m["understanding_score"],
                "capability": m["capability_score"],
                "primary_dependency": m.get("primary_dependency"),
                "secondary_dependency": m.get("secondary_dependency")
            })
            
        def calculate_risk(stats_list, source_data, factor_modifiers=None):
            # factor_modifiers used for simulation
            if not stats_list:
                return {
                    "score": 0, 
                    "level": "None", 
                    "factors": [],
                    "radar": [],
                    "persona": {"name": "The Observer", "class": "Neutral", "icon": "Activity"},
                    "narrative": "Insufficient data streams for behavioral synthesis."
                }
                
            avg_dep = sum(i["dependency"] for i in stats_list) / len(stats_list)
            avg_freq = sum(i["session_count"] for i in stats_list) / len(stats_list)
            
            if factor_modifiers:
                avg_dep = max(0, min(100, avg_dep * factor_modifiers.get("dependency_mult", 1.0)))
                avg_freq = max(0, min(100, avg_freq * factor_modifiers.get("frequency_mult", 1.0)))

            freq_score = min(100, (avg_freq / 5.0) * 100)
            avg_und = sum(i["understanding"] for i in stats_list) / len(stats_list)
            und_gap_score = max(0, avg_dep - avg_und)
            avg_cap = sum(i["capability"] for i in stats_list) / len(stats_list)
            
            attachment_sessions = [m for m in source_data if m.get("primary_dependency") in ["Emotional", "Social"]]
            attachment_score = (len(attachment_sessions) / len(source_data)) * 100 if source_data else 0
            
            thinking_gap = max(0, 100 - avg_und) * 0.5
            
            risk_score = (avg_dep * 0.4) + (freq_score * 0.2) + (und_gap_score * 0.2) + (attachment_score * 0.2)
            risk_score = round(min(100, risk_score), 1)
            
            risk_level = "None"
            if risk_score > 85: risk_level = "Critical"
            elif risk_score > 65: risk_level = "High"
            elif risk_score > 40: risk_level = "Moderate"
            elif risk_score > 15: risk_level = "Low"
            
            # Persona Logic
            traits = collections.Counter([m.get("primary_dependency") for m in source_data if m.get("primary_dependency")])
            top_trait = traits.most_common(1)[0][0] if traits else "Functional"
            
            persona_map = {
                "Functional": {"name": "The Architect", "class": "Technical", "icon": "Briefcase"},
                "Cognitive": {"name": "The Explorer", "class": "Analytical", "icon": "Brain"},
                "Emotional": {"name": "The Mirror", "class": "Empathetic", "icon": "Heart"},
                "Social": {"name": "The Companion", "class": "Relational", "icon": "Users"},
                "Decision-making": {"name": "The Sentinel", "class": "Decisive", "icon": "Dices"}
            }
            persona = persona_map.get(top_trait, {"name": "The Observer", "class": "Neutral", "icon": "Activity"})

            # Radar Data
            radar = [
                {"subject": 'Dependency', "A": round(avg_dep, 1), "fullMark": 100},
                {"subject": 'Understanding', "A": round(avg_und, 1), "fullMark": 100},
                {"subject": 'Capability', "A": round(avg_cap, 1), "fullMark": 100},
                {"subject": 'Frequency', "A": round(freq_score, 1), "fullMark": 100},
            ]

            # Narrative Synthesis
            narrative = f"System analysis indicates a {persona['class'].lower()} interaction profile. "
            if risk_score < 30:
                narrative += "Behavioral equilibrium is optimal, with high cognitive agency preserved."
            elif risk_score < 60:
                narrative += f"Moderate {top_trait} dependency detected. System suggests intermittent independent creative intervals."
            else:
                narrative += "Critical dependency levels identified. Recommend immediate protocol shift toward unassisted task execution."

            factors = [
                {"name": "Cognitive Substitution", "value": round(und_gap_score, 1)},
                {"name": "Emotional Attachment", "value": round(attachment_score, 1)},
                {"name": "Behavioral Frequency", "value": round(freq_score, 1)},
                {"name": "Independent Thinking", "value": round(thinking_gap, 1)}
            ]
            return {
                "score": risk_score, 
                "level": risk_level, 
                "factors": factors, 
                "persona": persona,
                "radar": radar,
                "narrative": narrative
            }

        # Date Slicing
        today_str = datetime.utcnow().strftime('%Y-%m-%d')
        today_stats = [i for i in daily_trends if i["date"] == today_str]
        today_source = [m for m in data if m["created_at"].startswith(today_str)]
        
        if not today_stats and daily_trends:
            today_stats = [daily_trends[-1]]
            latest_date = daily_trends[-1]["date"]
            today_source = [m for m in data if m["created_at"].startswith(latest_date)]
        
        daily_risk = calculate_risk(today_stats, today_source)
        monthly_risk = calculate_risk(daily_trends, data)

        return {
            "sessions": sessions_trends,
            "daily": daily_trends,
            "monthly": monthly_trends,
            "density": density_map,
            "forecast": {
                "daily": daily_forecast,
                "monthly": monthly_forecast
            },
            "comparative": {
                "daily": daily_comparative,
                "monthly": monthly_comparative
            },
            "risk_assessment": {
                "daily": daily_risk,
                "monthly": monthly_risk
            }
        }
        
    except Exception as e:
        print(f"Error in analytics trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate")
async def simulate_behavior(params: Dict[str, Any], user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user.get("sub")
    token = user.get("access_token")
    
    # Extract multipliers
    dep_mult = params.get("dependency_mult", 1.0)
    freq_mult = params.get("frequency_mult", 1.0)
    view = params.get("view", "daily")

    try:
        supabase = get_supabase_client(token)
        metrics_res = supabase.table("session_metrics") \
            .select("dependency_score, understanding_score, capability_score, primary_dependency, created_at, sessions!inner(user_id)") \
            .eq("sessions.user_id", user_id) \
            .order("created_at") \
            .execute()
        
        data = metrics_res.data
        if not data:
            return {"score": 0, "level": "None"}

        # Define calculate_risk locally or refactor to top-level if needed
        # For the simulation, we'll re-calculate based on the latest data + modifiers
        
        # Grouping for trends
        daily_stats = collections.defaultdict(list)
        for m in data:
            date_str = m["created_at"][:10]
            daily_stats[date_str].append(m)
        
        daily_trends = []
        for date, items in sorted(daily_stats.items()):
            daily_trends.append({
                "date": date,
                "dependency": sum(i["dependency_score"] for i in items) / len(items),
                "understanding": sum(i["understanding_score"] for i in items) / len(items),
                "capability": sum(i["capability_score"] for i in items) / len(items),
                "session_count": len(items)
            })

        # Logic from get_analytics_trends
        def calculate_risk_local(stats_list, source_data, factor_modifiers=None):
            if not stats_list: return {"score": 0}
            
            avg_dep = sum(i["dependency"] for i in stats_list) / len(stats_list)
            avg_freq = sum(i["session_count"] for i in stats_list) / len(stats_list)
            
            if factor_modifiers:
                avg_dep = max(0, min(100, avg_dep * factor_modifiers.get("dependency_mult", 1.0)))
                avg_freq = max(0, min(100, avg_freq * factor_modifiers.get("frequency_mult", 1.0)))

            freq_score = min(100, (avg_freq / 5.0) * 100)
            avg_und = sum(i["understanding"] for i in stats_list) / len(stats_list)
            und_gap_score = max(0, avg_dep - avg_und)
            
            attachment_sessions = [m for m in source_data if m.get("primary_dependency") in ["Emotional", "Social"]]
            attachment_score = (len(attachment_sessions) / len(source_data)) * 100 if source_data else 0
            
            risk_score = (avg_dep * 0.4) + (freq_score * 0.2) + (und_gap_score * 0.2) + (attachment_score * 0.2)
            risk_score = round(min(100, risk_score), 1)
            
            level = "None"
            if risk_score > 85: level = "Critical"
            elif risk_score > 65: level = "High"
            elif risk_score > 40: level = "Moderate"
            elif risk_score > 15: level = "Low"
            
            return {"score": risk_score, "level": level}

        if view == "daily":
            # Use latest day
            latest_stats = [daily_trends[-1]]
            latest_source = [m for m in data if m["created_at"].startswith(daily_trends[-1]["date"])]
            result = calculate_risk_local(latest_stats, latest_source, {"dependency_mult": dep_mult, "frequency_mult": freq_mult})
        else:
            result = calculate_risk_local(daily_trends, data, {"dependency_mult": dep_mult, "frequency_mult": freq_mult})

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
