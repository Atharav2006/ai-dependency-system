import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load env vars before anything else
load_dotenv()

from app.routes import sessions, analytics

app = FastAPI(title="AI Dependency System Backend")

# CORS configuration
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
origins = [origin.strip() for origin in allowed_origins_str.split(",")]
# Always allow localhost for dev
if "http://localhost:3000" not in origins: origins.append("http://localhost:3000")
if "http://localhost:5173" not in origins: origins.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router)
app.include_router(analytics.router)

@app.get("/")
def health_check():
    return {"status": "ok"}
