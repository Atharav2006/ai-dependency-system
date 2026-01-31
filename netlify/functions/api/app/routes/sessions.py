from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
# Using absolute imports based on execution from 'backend' folder
from app.dependencies.auth import get_current_user
from app.utils.supabase_client import get_supabase_client
from app.utils.llm_factory import get_llm_service

router = APIRouter(prefix="/sessions", tags=["sessions"])

class MessageRequest(BaseModel):
    message: str
    role: str  # user or assistant

@router.post("/start")
async def start_session(background_tasks: BackgroundTasks, user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user.get("sub")
    email = user.get("email")
    token = user.get("access_token")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    try:
        # Use authenticated client (RLS aware)
        supabase = get_supabase_client(token)

        # Check users table, insert if missing
        # We need to verify user exists to maintain FK constraint
        # Use simple error handling - try insert, if fails (duplicate), ignore or update
        
        # Check if user exists
        user_check = supabase.table("users").select("id").eq("id", user_id).execute()
        if not user_check.data:
             # Insert user
             new_user = {"id": user_id, "email": email}
             r_user = supabase.table("users").insert(new_user).execute()

        # Automated Closing: Find and end any previous active sessions
        active_sessions = supabase.table("sessions") \
            .select("id") \
            .eq("user_id", user_id) \
            .eq("status", "started") \
            .execute()
        
        if active_sessions.data:
            from app.utils.dependency_service import get_dependency_service
            dependency_service = get_dependency_service()
            for s in active_sessions.data:
                old_id = s["id"]
                # Mark as ended
                supabase.table("sessions").update({"status": "ended"}).eq("id", old_id).execute()
                # Run analysis in background
                background_tasks.add_task(dependency_service.analyze_session, old_id, token)

        # Create session
        new_session = {"user_id": user_id, "status": "started"}
        
        # If user insert succeeded or user exists, this should work if RLS allows
        res = supabase.table("sessions").insert(new_session).execute()
        
        if not res.data:
            raise HTTPException(status_code=500, detail="Failed to create session")
            
        session = res.data[0]
        return {"session_id": session["id"], "status": session["status"]}

    except Exception as e:
        print(f"Error starting session: {e}")
        # Return detail for debugging
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/message")
async def add_message(session_id: str, request: MessageRequest, user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user.get("sub")
    token = user.get("access_token")
    
    try:
        supabase = get_supabase_client(token)
        
        # Verify session ownership
        session_res = supabase.table("sessions").select("user_id").eq("id", session_id).single().execute()
        
        if not session_res.data:
             raise HTTPException(status_code=404, detail="Session not found")
             
        if session_res.data["user_id"] != user_id:
             raise HTTPException(status_code=403, detail="Unauthorized access to session")

        # Insert User Message
        log_entry = {
            "session_id": session_id,
            "message": request.message,
            "role": request.role
        }
        user_msg_res = supabase.table("session_logs").insert(log_entry).execute()
        
        # Generate AI response if the message is from user
        ai_response = None
        if request.role == "user":
            try:
                from app.utils.gemini_service import get_gemini_service
                
                # Fetch recent conversation history (last 10 messages)
                history_res = supabase.table("session_logs")\
                    .select("role, message")\
                    .eq("session_id", session_id)\
                    .order("created_at", desc=False)\
                    .limit(10)\
                    .execute()
                
                conversation_history = history_res.data if history_res.data else []
                
                # Get LLM Service (Provider can be passed in request later, using default for now)
                # We could add 'provider' to MessageRequest if we want per-message switching
                llm = get_llm_service() 
                
                ai_response_text = llm.generate_response(
                    request.message,
                    conversation_history=conversation_history
                )
                
                # Store AI response
                ai_log_entry = {
                    "session_id": session_id,
                    "message": ai_response_text,
                    "role": "assistant"
                }
                ai_msg_res = supabase.table("session_logs").insert(ai_log_entry).execute()
                
                if ai_msg_res.data:
                    ai_response = ai_msg_res.data[0]
                    
            except Exception as ai_error:
                print(f"Error generating AI response: {ai_error}")
                import traceback
                traceback.print_exc()
                ai_response = {"message": f"AI Error: {str(ai_error)}", "role": "assistant"} # Debugging
        
        return {
            "status": "success", 
            "user_message": user_msg_res.data[0] if user_msg_res.data else None,
            "ai_response": ai_response
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error adding message: {e}")
        raise HTTPException(status_code=500, detail=f"{str(e)}")

@router.post("/{session_id}/end")
async def end_session(session_id: str, background_tasks: BackgroundTasks, user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user.get("sub")
    token = user.get("access_token")

    try:
        supabase = get_supabase_client(token)

        # Verify ownership
        session_res = supabase.table("sessions").select("user_id").eq("id", session_id).single().execute()
        
        if not session_res.data:
             raise HTTPException(status_code=404, detail="Session not found")
             
        if session_res.data["user_id"] != user_id:
             raise HTTPException(status_code=403, detail="Unauthorized")

        # Update status
        res = supabase.table("sessions").update({"status": "ended"}).eq("id", session_id).execute()

        # Trigger Analysis
        try:
            from app.utils.dependency_service import get_dependency_service
            dependency_service = get_dependency_service()
            # Run analysis in background
            background_tasks.add_task(dependency_service.analyze_session, session_id, token)
        except Exception as analysis_error:
            print(f"Analysis failed: {analysis_error}")
            # Don't fail the end_session call, just log it
        
        return {
            "status": "ended", 
            "data": res.data,
            "analysis": "pending"
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error ending session: {e}")
        # Return more detailed error for debugging (remove in prod)
        raise HTTPException(status_code=500, detail=f"{str(e)}: {traceback.format_exc()}")

@router.get("/{session_id}/analysis")
async def get_session_analysis(session_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user.get("sub")
    token = user.get("access_token")

    try:
        supabase = get_supabase_client(token)
        
        # Verify ownership
        session_res = supabase.table("sessions").select("user_id").eq("id", session_id).single().execute()
        if not session_res.data:
             raise HTTPException(status_code=404, detail="Session not found")
        if session_res.data["user_id"] != user_id:
             raise HTTPException(status_code=403, detail="Unauthorized")

        # Fetch metrics
        metrics_res = supabase.table("session_metrics").select("*").eq("session_id", session_id).single().execute()
        
        if not metrics_res.data:
            return {"status": "pending", "message": "Analysis not available yet"}
            
        return {"status": "complete", "data": metrics_res.data}
        
    except Exception as e:
        print(f"Error fetching analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_sessions(user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user.get("sub")
    token = user.get("access_token")
    
    try:
        supabase = get_supabase_client(token)
        res = supabase.table("sessions") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .execute()
        return res.data
    except Exception as e:
        print(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/messages")
async def get_session_messages(session_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    user_id = user.get("sub")
    token = user.get("access_token")
    
    try:
        supabase = get_supabase_client(token)
        
        # Verify ownership
        session_res = supabase.table("sessions").select("user_id").eq("id", session_id).single().execute()
        if not session_res.data:
             raise HTTPException(status_code=404, detail="Session not found")
        if session_res.data["user_id"] != user_id:
             raise HTTPException(status_code=403, detail="Unauthorized")
             
        res = supabase.table("session_logs") \
            .select("*") \
            .eq("session_id", session_id) \
            .order("created_at", desc=False) \
            .execute()
        return res.data
    except Exception as e:
        print(f"Error fetching messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))
