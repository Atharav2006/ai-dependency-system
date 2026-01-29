# AI Dependency System - Frontend

A modern, beautiful React-based frontend for the AI Dependency System with Supabase authentication and real-time session management.

## Features

- 🎨 **Modern UI**: Beautiful dark mode with glassmorphism effects
- 🔐 **Authentication**: Google OAuth and email/password login via Supabase
- 💬 **Chat Interface**: Real-time messaging with AI sessions
- 📊 **Session Management**: Create, manage, and end AI sessions
- 🎭 **Responsive Design**: Works seamlessly on all devices

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Supabase** - Authentication and database
- **React Router** - Client-side routing
- **Lucide React** - Beautiful icons

## Getting Started

### Prerequisites

- Node.js 16+ installed
- Backend server running on `http://localhost:8000`
- Supabase project configured

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will open at `http://localhost:5173`

### Environment Variables

Create a `.env.local` file with:

```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_BACKEND_URL=http://localhost:8000
```

## Usage

1. **Login**: Use Google OAuth or email/password to authenticate
2. **Start Session**: Click "New Session" to begin an AI conversation
3. **Chat**: Send messages and receive AI responses
4. **End Session**: Close the session when done

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable components
│   │   └── ChatMessage.jsx
│   ├── pages/           # Page components
│   │   ├── Login.jsx
│   │   └── Dashboard.jsx
│   ├── lib/             # Utilities
│   │   └── supabase.js
│   ├── services/        # API clients
│   │   └── api.js
│   ├── App.jsx          # Main app component
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles
├── index.html
├── vite.config.js
└── package.json
```

## Design System

The app uses a comprehensive design system with:

- **Color Palette**: Vibrant dark theme with accent gradients
- **Typography**: Inter font family
- **Spacing**: Consistent spacing scale
- **Components**: Reusable button, input, and card components
- **Animations**: Smooth transitions and micro-interactions

## Building for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

## License

MIT
