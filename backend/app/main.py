import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load env vars before anything else
load_dotenv()

from app.routes import sessions, analytics

app = FastAPI(title="AI Dependency System Backend")

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
    "*" 
]

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
