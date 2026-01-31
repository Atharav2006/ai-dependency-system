# AI Dependency System 🌌✨

A world-class behavioural analysis platform that monitors user interaction dynamics with AI agents. It calculates dependency, understanding, and capability scores through strategic session oversight.

## 🚀 Features

- **Persistent Sessions**: Automated session tracking with Supabase.
- **Elite Analytics**: Daily Stream and Monthly Insight views with high-definition charts.
- **Behavioural Scoring**: Advanced rubric-based analysis of user engagement.
- **Premium UI**: State-of-the-art dark/pink theme with glassmorphism and motion effects.

## 🛠️ Stack
- **Frontend**: React + Vite + Framer Motion + Recharts
- **Backend**: FastAPI + Supabase + Gemini AI
- **Database**: PostgreSQL (via Supabase)

## 📦 Setup

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
# Set up .env with SUPABASE_URL, SUPABASE_KEY, and GEMINI_API_KEY
uvicorn app.main:app --reload
```

### 2. Frontend
```bash
cd frontend
npm install
# Set up .env with VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY, and VITE_BACKEND_URL
npm run dev
```

## 📈 Architecture
The system uses a monorepo structure with a clear separation between the FastAPI service layer and the React consumer interface. Data is synchronized via Supabase for real-time responsiveness.
