import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { supabase } from '../lib/supabase'
import { motion, AnimatePresence } from 'framer-motion'
import {
    LineChart, Line, AreaChart, Area, XAxis, YAxis,
    CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    BarChart, Bar
} from 'recharts'
import { ArrowLeft, TrendingUp, Calendar, Activity, BarChart2 } from 'lucide-react'
import './Analytics.css'

export default function Analytics() {
    const [summary, setSummary] = useState(null)
    const [trends, setTrends] = useState({ daily: [], monthly: [] })
    const [loading, setLoading] = useState(true)
    const [view, setView] = useState('daily')

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        setLoading(true)
        try {
            const { data: { session } } = await supabase.auth.getSession()
            const token = session?.access_token

            const [summaryData, trendsData] = await Promise.all([
                api.getAnalyticsSummary(token),
                api.getAnalyticsTrends(token)
            ])

            setSummary(summaryData)
            setTrends(trendsData)
        } catch (error) {
            console.error('Error fetching analytics:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="analytics-page">
                <div className="analytics-grid">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="stat-card glass-card shimmer" style={{ height: '140px' }}></div>
                    ))}
                </div>
                <div className="chart-container-large glass-card shimmer" style={{ height: '400px', marginTop: '2rem' }}></div>
            </div>
        )
    }

    const activeTrends = view === 'daily' ? (trends.sessions || []) : (trends.daily || [])
    const dateKey = view === 'daily' ? 'time' : 'date'

    const formatXAxis = (val) => {
        if (!val) return ''
        if (view === 'daily') {
            const date = new Date(val)
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
        // val is YYYY-MM-DD
        const date = new Date(val)
        return date.toLocaleDateString([], { day: 'numeric', month: 'long' })
    }

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            return (
                <div className="custom-tooltip glass-card elite-tool">
                    <p className="tooltip-label">
                        {view === 'daily' ? new Date(label).toLocaleString() : new Date(label).toLocaleDateString([], { day: 'numeric', month: 'long', year: 'numeric' })}
                    </p>
                    {payload.map((entry, index) => (
                        <div key={index} className="tooltip-item">
                            <span className="dot" style={{ backgroundColor: entry.color, boxShadow: `0 0 12px ${entry.color}` }}></span>
                            <span className="tooltip-name">{entry.name}:</span>
                            <span className="tooltip-value">{entry.value.toFixed(1)}%</span>
                        </div>
                    ))}
                    {view === 'monthly' && (
                        <div className="tooltip-footer">
                            <div className="tooltip-subitem">
                                <span className="text-secondary">Sessions Found:</span>
                                <span className="tooltip-value">{payload[0].payload.session_count}</span>
                            </div>
                            <div className="tooltip-subitem">
                                <span className="text-secondary">Daily Stability:</span>
                                <span className="tooltip-value" style={{ color: '#10b981' }}>High</span>
                            </div>
                        </div>
                    )}
                </div>
            )
        }
        return null
    }

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { staggerChildren: 0.1, delayChildren: 0.2 }
        }
    }

    const itemVariants = {
        hidden: { opacity: 0, y: 30 },
        visible: {
            opacity: 1,
            y: 0,
            transition: { type: "spring", stiffness: 120, damping: 20 }
        }
    }

    return (
        <motion.div
            className="analytics-page elite-dashboard"
            initial="hidden"
            animate="visible"
            variants={containerVariants}
        >
            <motion.div variants={itemVariants}>
                <Link to="/dashboard" className="back-btn">
                    <ArrowLeft size={16} />
                    System Overview
                </Link>
            </motion.div>

            <motion.header className="analytics-header" variants={itemVariants}>
                <div>
                    <h1>{view === 'daily' ? 'Live Performance' : 'Strategic Outlook'}</h1>
                    <p className="text-secondary">
                        {view === 'daily' ? 'Real-time session dynamics and engagement metrics' : 'Comprehensive long-term behavioural analysis'}
                    </p>
                </div>
                <div className="tabs premium-tabs">
                    <button
                        className={`tab-btn ${view === 'daily' ? 'active' : ''}`}
                        onClick={() => setView('daily')}
                    >
                        Daily Stream
                    </button>
                    <button
                        className={`tab-btn ${view === 'monthly' ? 'active' : ''}`}
                        onClick={() => setView('monthly')}
                    >
                        Monthly Insight
                    </button>
                </div>
            </motion.header>

            <div className="analytics-grid">
                <motion.div className="stat-card glass-card elite-shadow premium-card" variants={itemVariants}>
                    <div className="stat-content">
                        <h3>Volume</h3>
                        <div className="stat-value">{summary?.total_sessions || 0}</div>
                        <span className="stat-label">Total Sessions</span>
                    </div>
                    <div className="stat-icon-wrapper pulse-soft">
                        <Activity size={28} />
                    </div>
                </motion.div>
                <motion.div className="stat-card glass-card elite-shadow premium-card" variants={itemVariants}>
                    <div className="stat-content">
                        <h3>{view === 'daily' ? 'Focus' : 'Stability'}</h3>
                        <div className="stat-value">
                            {view === 'daily' ? (summary?.avg_dependency || 0) : Math.round(((summary?.avg_dependency || 0) + (summary?.avg_capability || 0)) / 2)}%
                        </div>
                        <span className="stat-label">{view === 'daily' ? 'Avg Dependency' : 'System Mean'}</span>
                    </div>
                    <div className="stat-icon-wrapper pulse-soft" style={{ background: 'rgba(236, 72, 153, 0.1)', color: 'var(--color-accent-primary)' }}>
                        <TrendingUp size={28} />
                    </div>
                </motion.div>
                <motion.div className="stat-card glass-card elite-shadow premium-card" variants={itemVariants}>
                    <div className="stat-content">
                        <h3>Growth</h3>
                        <div className="stat-value">{summary?.avg_capability || 0}%</div>
                        <span className="stat-label">Avg Capability</span>
                    </div>
                    <div className="stat-icon-wrapper pulse-soft" style={{ background: 'rgba(139, 92, 246, 0.1)', color: 'var(--color-accent-secondary)' }}>
                        <BarChart2 size={28} />
                    </div>
                </motion.div>
            </div>

            <motion.div className="chart-section" variants={containerVariants}>
                <motion.div className="chart-container-large glass-card chart-full elite-chart highlight-border" variants={itemVariants}>
                    <div className="chart-header">
                        <h2>{view === 'daily' ? 'Session Interaction Map' : 'Strategic Stability Matrix'}</h2>
                    </div>
                    <div style={{ height: '520px', width: '100%' }}>
                        <ResponsiveContainer>
                            <AreaChart data={activeTrends} margin={{ top: 20, right: 30, left: 10, bottom: 20 }}>
                                <defs>
                                    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                                        <feGaussianBlur stdDeviation="6" result="blur" />
                                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                                    </filter>
                                    <linearGradient id="colorDep" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#ec4899" stopOpacity={0.8} />
                                        <stop offset="40%" stopColor="#ec4899" stopOpacity={0.4} />
                                        <stop offset="95%" stopColor="#ec4899" stopOpacity={0.05} />
                                    </linearGradient>
                                    <linearGradient id="colorCap" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                                        <stop offset="40%" stopColor="#8b5cf6" stopOpacity={0.4} />
                                        <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.05} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="4 4" vertical={false} stroke="rgba(226, 232, 240, 0.3)" />
                                <XAxis
                                    dataKey={dateKey}
                                    stroke="#94a3b8"
                                    fontSize={12}
                                    fontWeight={600}
                                    tickFormatter={formatXAxis}
                                    tickLine={false}
                                    axisLine={false}
                                    dy={15}
                                />
                                <YAxis
                                    stroke="#94a3b8"
                                    fontSize={12}
                                    fontWeight={600}
                                    domain={[0, 100]}
                                    tickLine={false}
                                    axisLine={false}
                                    tickFormatter={(val) => `${val}%`}
                                />
                                <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(236, 72, 153, 0.3)', strokeWidth: 2 }} />
                                <Legend verticalAlign="top" height={80} align="right" iconType="circle" />
                                <Area
                                    type="monotone"
                                    dataKey="dependency"
                                    name="Dependency"
                                    stroke="#ec4899"
                                    fillOpacity={1}
                                    fill="url(#colorDep)"
                                    strokeWidth={4}
                                    animationDuration={2800}
                                    filter="url(#glow)"
                                    activeDot={{ r: 10, stroke: '#fff', strokeWidth: 4, boxShadow: '0 0 20px rgba(236, 72, 153, 0.6)' }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="capability"
                                    name="Capability"
                                    stroke="#8b5cf6"
                                    fillOpacity={1}
                                    fill="url(#colorCap)"
                                    strokeWidth={4}
                                    animationDuration={3200}
                                    filter="url(#glow)"
                                    activeDot={{ r: 10, stroke: '#fff', strokeWidth: 4, boxShadow: '0 0 20px rgba(139, 92, 246, 0.6)' }}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>

                <motion.div className="chart-container-large glass-card elite-chart highlight-border" variants={itemVariants}>
                    <div className="chart-header">
                        <h2>{view === 'daily' ? 'Understanding Depth' : 'Dynamic Growth Volume'}</h2>
                    </div>
                    <div style={{ height: '380px', width: '100%' }}>
                        <ResponsiveContainer>
                            <BarChart data={activeTrends} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#ec4899" stopOpacity={1} />
                                        <stop offset="60%" stopColor="#db2777" stopOpacity={0.9} />
                                        <stop offset="100%" stopColor="#9d174d" stopOpacity={0.8} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(226, 232, 240, 0.4)" />
                                <XAxis
                                    dataKey={dateKey}
                                    stroke="#94a3b8"
                                    fontSize={11}
                                    fontWeight={600}
                                    tickFormatter={formatXAxis}
                                    tickLine={false}
                                    axisLine={false}
                                    dy={15}
                                />
                                <YAxis stroke="#94a3b8" fontSize={11} fontWeight={600} tickLine={false} axisLine={false} />
                                <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(236, 72, 153, 0.08)', radius: [12, 12, 0, 0] }} />
                                <Bar
                                    dataKey={view === 'daily' ? "understanding" : "session_count"}
                                    name={view === 'daily' ? "Understanding" : "Daily Load"}
                                    fill="url(#barGradient)"
                                    radius={[12, 12, 4, 4]}
                                    animationDuration={2200}
                                    barSize={view === 'daily' ? 32 : 48}
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>

                <motion.div className="chart-container-large glass-card elite-chart highlight-border" variants={itemVariants}>
                    <div className="chart-header">
                        <h2>Technical Competency Plateau</h2>
                    </div>
                    <div style={{ height: '380px', width: '100%' }}>
                        <ResponsiveContainer>
                            <LineChart data={activeTrends} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                                <defs>
                                    <filter id="lineGlow" x="-20%" y="-20%" width="140%" height="140%">
                                        <feGaussianBlur stdDeviation="5" result="blur" />
                                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                                    </filter>
                                    <linearGradient id="plateauFill" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.2} />
                                        <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="4 4" vertical={false} stroke="rgba(139, 92, 246, 0.15)" />
                                <XAxis
                                    dataKey={dateKey}
                                    stroke="#94a3b8"
                                    fontSize={11}
                                    fontWeight={600}
                                    tickFormatter={formatXAxis}
                                    tickLine={false}
                                    axisLine={false}
                                    dy={15}
                                />
                                <YAxis stroke="#94a3b8" fontSize={11} fontWeight={600} domain={[0, 100]} tickLine={false} axisLine={false} />
                                <Tooltip content={<CustomTooltip />} />
                                <Line
                                    type="stepAfter"
                                    dataKey="understanding"
                                    name="Understanding"
                                    stroke="#8b5cf6"
                                    strokeWidth={5}
                                    dot={{ r: 7, fill: '#8b5cf6', strokeWidth: 3, stroke: '#fff', filter: 'drop-shadow(0 4px 8px rgba(139, 92, 246, 0.4))' }}
                                    activeDot={{ r: 12, stroke: '#fff', strokeWidth: 4, filter: 'url(#lineGlow)' }}
                                    animationDuration={2500}
                                    filter="url(#lineGlow)"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>
            </motion.div>
        </motion.div>
    )
}
