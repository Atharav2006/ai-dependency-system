@router.get("/benchmarks")
async def get_benchmarks(user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user.get("sub")
    token = user.get("access_token")
    
    try:
        supabase = get_supabase_client(token)
        
        # 1. Get Global Average Dependency
        # Note: This is computationally expensive on large datasets. 
        # For production, this should be a periodic materialised view calculation.
        # For MVP, we calculate on the fly or fetch from a stats table if we created one.
        
        # Let's try to get all session metrics
        # For scalability, we should limit or use a dedicated stats table. 
        # But let's assume < 10000 rows for now.
        all_metrics_res = supabase.table("session_metrics").select("dependency_score, capability_score").execute()
        
        if not all_metrics_res.data:
            return {
                "global_avg_dependency": 0,
                "global_avg_capability": 0,
                "user_percentile": 0
            }
            
        all_data = all_metrics_res.data
        total_global = len(all_data)
        global_avg_dep = sum(m["dependency_score"] for m in all_data) / total_global
        global_avg_cap = sum(m["capability_score"] for m in all_data) / total_global
        
        # 2. Get User Stats
        user_metrics_res = supabase.table("session_metrics") \
            .select("dependency_score") \
            .eq("sessions.user_id", user_id) \
            .select("*, sessions!inner(user_id)") \
            .execute()
            
        user_data = user_metrics_res.data
        if not user_data:
            return {
                "global_avg_dependency": round(global_avg_dep, 1),
                "global_avg_capability": round(global_avg_cap, 1),
                "user_percentile": 0,
                "message": "No user sessions to compare"
            }
            
        user_avg_dep = sum(m["dependency_score"] for m in user_data) / len(user_data)
        
        # 3. Calculate Percentile (Dependency - Lower is better)
        # Count how many sessions have HIGHER dependency than user avg
        worse_than_user = sum(1 for m in all_data if m["dependency_score"] > user_avg_dep)
        percentile = (worse_than_user / total_global) * 100
        
        return {
            "global_avg_dependency": round(global_avg_dep, 1),
            "global_avg_capability": round(global_avg_cap, 1),
            "user_percentile": round(percentile, 1),
            "user_avg_dependency": round(user_avg_dep, 1)
        }
        
    except Exception as e:
        print(f"Benchmark error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
