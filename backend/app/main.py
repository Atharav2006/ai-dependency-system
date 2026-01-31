import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load env vars before anything else
load_dotenv()

from app.routes import sessions, analytics

app = FastAPI(title="AI Dependency System Backend")

# CORS configuration
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "")
origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

# Add default development origins
dev_origins = ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
for o in dev_origins:
    if o not in origins:
        origins.append(o)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router)
app.include_router(analytics.router)

@app.get("/")
def health_check():
    return {"status": "ok"}
