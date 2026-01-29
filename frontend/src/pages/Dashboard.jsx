import { useState, useEffect, useRef } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { api } from '../services/api'
import { motion, AnimatePresence } from 'framer-motion'
import { LogOut, Send, Plus, MessageSquare, Sparkles, Activity, BarChart2 } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import ChatMessage from '../components/ChatMessage'
import './Dashboard.css'

export default function Dashboard() {
    const [user, setUser] = useState(null)
    const [sessions, setSessions] = useState([])
    const [currentSession, setCurrentSession] = useState(null)
    const [messages, setMessages] = useState([])
    const [analysis, setAnalysis] = useState(null)
    const [inputMessage, setInputMessage] = useState('')
    const [loading, setLoading] = useState(false)
    const messagesEndRef = useRef(null)
    const navigate = useNavigate()

    useEffect(() => {
        checkUser()
        loadSessions()
    }, [])

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const checkUser = async () => {
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) {
            navigate('/login')
            return
        }
        setUser(user)
    }

    const loadSessions = async () => {
        try {
            const { data: { session } } = await supabase.auth.getSession()
            const accessToken = session?.access_token
            if (!accessToken) return

            const fetchedSessions = await api.listSessions(accessToken)
            setSessions(fetchedSessions)
        } catch (error) {
            console.error('Error loading sessions:', error)
        }
    }

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    const getScoreColor = (score) => {
        if (score >= 70) return 'danger' // High dependency -> Red
        if (score >= 40) return 'warning'
        return 'success'
    }

    const handleSignOut = async () => {
        await supabase.auth.signOut()
        navigate('/login')
    }

    const startNewSession = async () => {
        if (!user) return

        setLoading(true)
        try {
            const { data: { session: authSession } } = await supabase.auth.getSession()
            const accessToken = authSession?.access_token

            // Ensure all other sessions are marked ended in the list before starting new one
            setSessions(prev => prev.map(s => ({ ...s, status: 'ended' })))

            const response = await api.startSession(accessToken)

            // Refresh session list to show newest session and updated status of previous one
            await loadSessions()

            // Set current session to the new one
            const responseData = await api.getSessionMessages(response.session_id, accessToken)
            setMessages(responseData)
            setCurrentSession({
                id: response.session_id,
                status: response.status,
                created_at: new Date().toISOString()
            })
            setAnalysis(null)
        } catch (error) {
            console.error('Error starting session:', error)
            alert('Failed to start session: ' + error.message)
        } finally {
            setLoading(false)
        }
    }

    const sendMessage = async (e) => {
        e.preventDefault()
        if (!inputMessage.trim() || !currentSession || loading) return

        const userMessage = {
            role: 'user',
            message: inputMessage,
            created_at: new Date().toISOString()
        }

        setMessages([...messages, userMessage])
        setInputMessage('')
        setLoading(true)

        try {
            const { data: { session } } = await supabase.auth.getSession()
            const accessToken = session?.access_token

            const response = await api.sendMessage(currentSession.id, inputMessage, 'user', accessToken)

            if (response.ai_response) {
                setMessages(prev => [...prev, response.ai_response])
            }

            setLoading(false)
        } catch (error) {
            console.error('Error sending message:', error)
            alert('Failed to send message: ' + error.message)
            setLoading(false)
        }
    }

    const endCurrentSession = async (sessionIdToEnd = null) => {
        // If called via onClick, sessionIdToEnd will be the event object. Ignore it.
        const id = (typeof sessionIdToEnd === 'string') ? sessionIdToEnd : currentSession?.id
        if (!id || (currentSession?.status === 'ended' && typeof sessionIdToEnd !== 'string')) return

        try {
            const { data: { session: authSession } } = await supabase.auth.getSession()
            const accessToken = authSession?.access_token

            await api.endSession(id, accessToken)
            // We'll update the session status in the state immediately for responsiveness
            setSessions(prev => prev.map(s => s.id === id ? { ...s, status: 'ended' } : s))
            if (currentSession?.id === id) {
                setCurrentSession(prev => ({ ...prev, status: 'ended' }))
            }
        } catch (error) {
            console.error('Error ending session:', error)
        }
    }

    const loadSessionHistory = async (session) => {
        if (session.id === currentSession?.id) return

        // If we are switching TO a session, and there is currently a "started" session, end it.
        const currentActive = sessions.find(s => s.status === 'started')
        if (currentActive && currentActive.id !== session.id) {
            await endCurrentSession(currentActive.id)
        }

        setLoading(true)
        try {
            const { data: { session: authSession } } = await supabase.auth.getSession()
            const accessToken = authSession?.access_token

            // Load messages
            const fetchedMessages = await api.getSessionMessages(session.id, accessToken)
            setMessages(fetchedMessages)
            setCurrentSession(session)

            // If session is ended, try to load analysis
            if (session.status === 'ended') {
                try {
                    const analysisRes = await api.getSessionAnalysis(session.id, accessToken)
                    if (analysisRes.status === 'complete') {
                        setAnalysis(analysisRes.data)
                    } else {
                        setAnalysis(null)
                    }
                } catch (e) {
                    setAnalysis(null)
                }
            } else {
                setAnalysis(null)
            }
        } catch (error) {
            console.error('Error loading session history:', error)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="dashboard">
            {/* Sidebar */}
            <aside className="sidebar">
                <div className="sidebar-header">
                    <div className="logo-small">
                        <Sparkles size={24} />
                    </div>
                    <h2>AI Sessions</h2>
                </div>

                <button onClick={startNewSession} disabled={loading} className="btn btn-primary btn-full">
                    <Plus size={18} />
                    New Session
                </button>

                <div className="sessions-list">
                    <Link to="/analytics" className="session-link-wrapper" style={{ textDecoration: 'none', color: 'inherit' }}>
                        <div className="session-card glass-card nav-highlight" style={{ marginBottom: '1rem', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
                            <div className="session-info">
                                <BarChart2 size={16} className="text-primary" />
                                <span className="session-id">View Analytics</span>
                            </div>
                            <span className="badge badge-success">New</span>
                        </div>
                    </Link>

                    {loading && sessions.length === 0 ? (
                        [1, 2, 3, 4, 5].map(i => (
                            <div key={i} className="session-card glass-card shimmer" style={{ height: '64px', marginBottom: '0.75rem' }}></div>
                        ))
                    ) : sessions.length === 0 ? (
                        <div className="empty-state">
                            <MessageSquare size={32} className="empty-icon" />
                            <p>No sessions yet</p>
                            <p className="empty-hint">Start a new session to begin</p>
                        </div>
                    ) : (
                        <AnimatePresence>
                            {sessions.map((session, index) => (
                                <motion.div
                                    key={session.id}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{
                                        type: "spring",
                                        stiffness: 100,
                                        delay: index * 0.05
                                    }}
                                    className={`session-card glass-card ${currentSession?.id === session.id ? 'active' : ''} interactive`}
                                    onClick={() => {
                                        setCurrentSession(session)
                                        loadSessionHistory(session)
                                    }}
                                >
                                    <div className="session-info">
                                        <MessageSquare size={16} />
                                        <span className="session-id">
                                            {new Date(session.created_at).toLocaleString([], {
                                                month: 'short',
                                                day: 'numeric',
                                                hour: '2-digit',
                                                minute: '2-digit'
                                            })}
                                        </span>
                                    </div>
                                    <span className={`badge badge-${session.status === 'started' ? 'success' : 'warning'}`}>
                                        {session.status}
                                    </span>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    )}
                </div>

                <div className="sidebar-footer">
                    <div className="user-info">
                        <div className="user-avatar">
                            {user?.email?.[0]?.toUpperCase() || 'U'}
                        </div>
                        <div className="user-details">
                            <p className="user-email">{user?.email}</p>
                        </div>
                    </div>
                    <button onClick={handleSignOut} className="btn btn-ghost btn-icon">
                        <LogOut size={18} />
                    </button>
                </div>
            </aside >

            {/* Main Chat Area */}
            < main className="chat-container" >
                {
                    currentSession ? (
                        <>
                            <div className="chat-header">
                                <div>
                                    <h1>
                                        {new Date(currentSession.created_at).toLocaleString([], {
                                            dateStyle: 'medium',
                                            timeStyle: 'short'
                                        })}
                                    </h1>
                                    <p className="chat-subtitle">Session Details & Behavioral Insights</p>
                                </div>
                                <button onClick={endCurrentSession} className="btn btn-secondary">
                                    End Session
                                </button>
                            </div>

                            <div className="messages-container">
                                {messages.length === 0 ? (
                                    <div className="chat-welcome">
                                        <Sparkles size={48} className="welcome-icon" />
                                        <h2>Start a conversation</h2>
                                        <p>Send a message to begin your AI session</p>
                                    </div>
                                ) : (
                                    messages.map((msg, idx) => (
                                        <ChatMessage key={idx} message={msg} index={idx} />
                                    ))
                                )}
                                <div ref={messagesEndRef} />
                            </div>

                            <form onSubmit={sendMessage} className="chat-input-container">
                                <input
                                    type="text"
                                    className="input chat-input"
                                    placeholder="Type your message..."
                                    value={inputMessage}
                                    onChange={(e) => setInputMessage(e.target.value)}
                                    disabled={loading}
                                />
                                <button
                                    type="submit"
                                    disabled={loading || !inputMessage.trim()}
                                    className="btn btn-primary btn-icon-lg"
                                >
                                    {loading ? <div className="spinner"></div> : <Send size={20} />}
                                </button>
                            </form>
                        </>

                    ) : analysis ? (
                        <div className="analysis-container slide-in">
                            <div className="analysis-header">
                                <Activity size={32} className="analysis-icon" />
                                <div>
                                    <h2>Session Analysis</h2>
                                    <p className="text-secondary">AI-generated behavioral report</p>
                                </div>
                            </div>

                            <div className="analysis-grid">
                                <div className="chart-card glass-card">
                                    <h3>Dependency Score</h3>
                                    <div className="score-display">
                                        <div className={`score-circle score-${getScoreColor(analysis.dependency_score)}`}>
                                            {analysis.dependency_score}
                                        </div>
                                        <p>
                                            {analysis.dependency_score > 70 ? 'High Dependency' :
                                                analysis.dependency_score > 40 ? 'Moderate' : 'Low Dependency'}
                                        </p>
                                    </div>
                                </div>

                                <div className="chart-card glass-card">
                                    <h3>Performance Metrics</h3>
                                    <div style={{ height: '200px', width: '100%' }}>
                                        <ResponsiveContainer>
                                            <BarChart
                                                data={[
                                                    { name: 'Understanding', score: analysis.understanding_score },
                                                    { name: 'Capability', score: analysis.capability_score }
                                                ]}
                                                layout="vertical"
                                                margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                                            >
                                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                                                <XAxis type="number" domain={[0, 100]} hide />
                                                <YAxis dataKey="name" type="category" stroke="#fff" tick={{ fontSize: 12 }} />
                                                <Tooltip
                                                    contentStyle={{ backgroundColor: '#1e1e1e', border: '1px solid #333' }}
                                                    itemStyle={{ color: '#fff' }}
                                                />
                                                <Bar dataKey="score" fill="#8884d8" radius={[0, 4, 4, 0]}>
                                                    {
                                                        [0, 1].map((entry, index) => (
                                                            <Cell key={`cell-${index}`} fill={index === 0 ? '#3b82f6' : '#10b981'} />
                                                        ))
                                                    }
                                                </Bar>
                                            </BarChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>

                                <div className="stats-card glass-card">
                                    <h3>Session Stats</h3>
                                    <div className="stats-list">
                                        <div className="stat-item">
                                            <span className="stat-label">Messages</span>
                                            <span className="stat-value">{analysis.raw_metrics?.message_count || 0}</span>
                                        </div>
                                        <div className="stat-item">
                                            <span className="stat-label">Duration</span>
                                            <span className="stat-value">{analysis.raw_metrics?.session_duration_seconds || 0}s</span>
                                        </div>
                                        <div className="stat-item">
                                            <span className="stat-label">Avg Length</span>
                                            <span className="stat-value">{analysis.raw_metrics?.avg_prompt_length || 0} chars</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <button onClick={startNewSession} className="btn btn-primary btn-lg mt-8">
                                <Plus size={20} />
                                Start New Session
                            </button>
                        </div>
                    ) : (
                        <div className="no-session">
                            <Sparkles size={64} className="no-session-icon" />
                            <h2>Welcome to AI Dependency System</h2>
                            <p>Start a new session to begin your AI-powered conversation</p>
                            <button onClick={startNewSession} disabled={loading} className="btn btn-primary btn-lg">
                                <Plus size={20} />
                                Start New Session
                            </button>
                        </div>
                    )
                }
            </main >
        </div >
    )
}
