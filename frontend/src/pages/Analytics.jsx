import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { supabase } from '../lib/supabase'
import { motion, AnimatePresence } from 'framer-motion'
import {
    LineChart, Line, AreaChart, Area, XAxis, YAxis,
    CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    BarChart, Bar, PieChart, Pie, Cell,
    Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    ComposedChart
} from 'recharts'
import { ArrowLeft, TrendingUp, Calendar, Activity, BarChart2, Sparkles, Brain, Heart, Briefcase, Dices, Users, AlertTriangle, ShieldCheck, Fingerprint, Award, Crown, Zap, X, Play } from 'lucide-react'
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

    const today = new Date().toISOString().split('T')[0]

    // Filter trends based on view mode
    const dailySessions = (trends.sessions || []).filter(s => s.time?.startsWith(today))

    const activeTrends = view === 'daily' ? dailySessions : (trends.daily || [])
    const dateKey = view === 'daily' ? 'time' : 'date'

    // Calculate dynamic stats for today if in daily view
    const dynamicStats = view === 'daily' ? {
        total_sessions: dailySessions.length,
        avg_dependency: dailySessions.length > 0
            ? Math.round(dailySessions.reduce((acc, s) => acc + s.dependency, 0) / dailySessions.length)
            : 0,
        avg_capability: dailySessions.length > 0
            ? Math.round(dailySessions.reduce((acc, s) => acc + s.capability, 0) / dailySessions.length)
            : 0
    } : {
        total_sessions: summary?.total_sessions || 0,
        avg_dependency: summary?.avg_dependency || 0,
        avg_capability: summary?.avg_capability || 0
    }

    const getRecommendation = (score) => {
        if (score <= 30) {
            return {
                title: "Balanced Mastery",
                text: "We love your balanced approach to AI. You're using it as a tool, not a crutch. Keep up the great independent work!",
                color: "var(--color-success)",
                bg: "rgba(16, 185, 129, 0.1)"
            }
        } else if (score <= 60) {
            return {
                title: "Growth Opportunity",
                text: "You're collaborating well with AI, but try brainstorming your own solutions first before asking for help. It'll strengthen your skills!",
                color: "var(--color-warning)",
                bg: "rgba(245, 158, 11, 0.1)"
            }
        } else if (score <= 85) {
            return {
                title: "Reliance Warning",
                text: "Your dependency is creeping up. Try setting a timer to work independently for 30 minutes before reaching for AI help.",
                color: "#f43f5e",
                bg: "rgba(244, 63, 94, 0.1)"
            }
        } else {
            return {
                title: "Critical Dependency",
                text: "Extreme over-dependence detected. It's time for a break! Try making your next few decisions entirely on your own to regain your creative edge.",
                color: "#be123c",
                bg: "rgba(190, 18, 60, 0.1)"
            }
        }
    }

    const reco = getRecommendation(dynamicStats.avg_dependency)

    // Calculate Dependency Type DNA based on active data
    const dependencyTypes = activeTrends.reduce((acc, s) => {
        // Find session in trends.sessions that correlates with this data point if needed
        // For Daily Stream, s is an individual session object
        // For Monthly Insight, s is a summarized daily point. 
        // We'll use individual sessions for more accurate DNA matching

        const sessionsToAnalyze = view === 'daily'
            ? [s] // In daily, each s is a session object from trends.sessions
            : (trends.sessions || []).filter(ts => ts.time?.startsWith(s.date))

        sessionsToAnalyze.forEach(sess => {
            const type = sess.primary_dependency
            if (type) acc[type] = (acc[type] || 0) + 1
        })

        return acc
    }, {})

    const sortedTypes = Object.entries(dependencyTypes)
        .sort(([, a], [, b]) => b - a)

    const totalDnaSessions = Object.values(dependencyTypes).reduce((a, b) => a + b, 0) || 1

    const typeIcons = {
        'Functional': <Briefcase size={14} />,
        'Cognitive': <Brain size={14} />,
        'Emotional': <Heart size={14} />,
        'Decision-making': <Dices size={14} />,
        'Social': <Users size={14} />,
        'Briefcase': <Briefcase size={14} />,
        'Heart': <Heart size={14} />,
        'Dices': <Dices size={14} />,
        'Users': <Users size={14} />,
        'Brain': <Brain size={14} />,
        'Activity': <Activity size={14} />,
        'Award': <Award size={14} />,
        'Crown': <Crown size={14} />,
        'Zap': <Zap size={14} />,
        'Fingerprint': <Fingerprint size={14} />,
        'Terminal': <Sparkles size={14} />
    }
    const Typewriter = ({ text }) => {
        const [displayedText, setDisplayedText] = useState('')
        const [index, setIndex] = useState(0)

        useEffect(() => {
            setDisplayedText('')
            setIndex(0)
        }, [text])

        useEffect(() => {
            if (index < text.length) {
                const timeout = setTimeout(() => {
                    setDisplayedText(prev => prev + text.charAt(index))
                    setIndex(index + 1)
                }, 20)
                return () => clearTimeout(timeout)
            }
        }, [index, text])

        return (
            <p>
                {displayedText}
                <span className="narrative-cursor"></span>
            </p>
        )
    }


    const TrendBadge = ({ value }) => {
        if (!value || value === 0) return null
        const isUp = value > 0
        return (
            <div className={`trend-badge ${isUp ? 'trend-up' : 'trend-down'} trend-neon-glow`}>
                {isUp ? <TrendingUp size={10} /> : <TrendingUp size={10} style={{ transform: 'rotate(180deg)' }} />}
                <span>{Math.abs(value)}%</span>
            </div>
        )
    }

    const HeatRing = ({ data }) => {
        if (!data || data.length === 0) return (
            <div className="no-data-render">
                <Activity size={40} className="shimmer-icon" />
                <span>Collecting Interaction Signals...</span>
            </div>
        )
        const radius = 95
        const strokeWidth = 14
        const center = 130
        const maxVal = Math.max(...data, 1)

        return (
            <svg width="260" height="260" viewBox="0 0 260 260" className="hour-ring-container">
                <defs>
                    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur stdDeviation="3" result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                </defs>
                {data.map((val, hour) => {
                    const angle = (hour / 24) * 2 * Math.PI - Math.PI / 2
                    const nextAngle = ((hour + 1) / 24) * 2 * Math.PI - Math.PI / 2
                    const x1 = center + radius * Math.cos(angle)
                    const y1 = center + radius * Math.sin(angle)
                    const x2 = center + radius * Math.cos(nextAngle)
                    const y2 = center + radius * Math.sin(nextAngle)

                    const weight = (val / maxVal)
                    const opacity = 0.15 + weight * 0.85
                    const color = val > (maxVal * 0.75) ? '#ec4899' : '#8b5cf6'

                    return (
                        <g key={hour} className="hour-group">
                            <path
                                d={`M ${x1} ${y1} A ${radius} ${radius} 0 0 1 ${x2} ${y2}`}
                                fill="none"
                                stroke={color}
                                strokeWidth={strokeWidth}
                                strokeOpacity={opacity}
                                strokeLinecap="round"
                                className="density-hour-segment"
                                filter={val > maxVal * 0.5 ? "url(#glow)" : "none"}
                                style={{
                                    transition: 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
                                    strokeDasharray: '0.5, 2.5'
                                }}
                            >
                                <title>{hour}:00 - {val} sessions</title>
                            </path>
                        </g>
                    )
                })}
            </svg>
        )
    }

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
            // Check if label is a date/time string (like 2026-01-31 or 14:30)
            const isDate = label && (String(label).includes('-') || String(label).includes(':'));

            return (
                <div className="custom-tooltip glass-card elite-tool">
                    <p className="tooltip-label">
                        {isDate
                            ? (view === 'daily' ? new Date(label).toLocaleString() : new Date(label).toLocaleDateString([], { day: 'numeric', month: 'long', year: 'numeric' }))
                            : label
                        }
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

    const RISK_COLORS = ['#ec4899', '#8b5cf6', '#3b82f6', '#10b981']

    const riskData = trends.risk_assessment?.[view] || { score: 0, level: 'None', factors: [], narrative: "Insufficient data streams." }
    const compData = trends.comparative?.[view] || { dependency: 0, capability: 0, volume: 0 }
    const densityData = trends.density?.[view] || (view === 'daily' ? trends.density?.daily : trends.density?.monthly) || []
    const forecastData = trends.forecast?.[view] || []

    const radarDataWithBenchmark = (riskData.radar || []).map(r => ({
        ...r,
        benchmark: r.subject === 'Dependency' ? 20 : 85
    }))

    // Prepare chart data with forecast
    const chartDataWithForecast = [...activeTrends]
    if (forecastData.length > 0) {
        forecastData.forEach((val, i) => {
            chartDataWithForecast.push({
                [dateKey]: `Forecast ${i + 1}`,
                dependency: null,
                forecast: val,
                isForecast: true
            })
        })
    }

    const persona = riskData.persona || { name: "The Observer", class: "Neutral", icon: "Activity" }

    const getRiskDescription = (level) => {
        switch (level) {
            case 'Critical': return "Immediate intervention recommended. Deep psychological dependency detected with minimal independent cognitive output.";
            case 'High': return "Significant emotional attachment identified. AI is actively substituting core creative and critical thinking processes.";
            case 'Moderate': return "Developing reliance pattern. Frequent use of AI for fundamental decisions and understanding suggests a growing dependency.";
            case 'Low': return "Healthy occasional overuse. Mostly independent with minor behavioral spikes during complex task execution.";
            case 'None': return "Optimal system equilibrium. AI is utilized strictly as a tool without affecting independent cognitive agency.";
            default: return "Analyzing behavioral data streams...";
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
                    <h1 className={view === 'daily' ? 'text-glow-alt' : 'text-glow'}>
                        {view === 'daily' ? 'Live Performance' : 'Strategic Outlook'}
                    </h1>
                    <p className="subtitle-premium">
                        {view === 'daily'
                            ? 'Real-time session dynamics and engagement patterns'
                            : 'Long-term behavioral stability and technical growth matrix'}
                    </p>
                </div>
                <div className="tabs premium-tabs">
                    <div className="tab-group glass-card highlight-border">
                        <button className={`tab-btn ${view === 'daily' ? 'active' : ''}`} onClick={() => setView('daily')}>Daily Analysis</button>
                        <button className={`tab-btn ${view === 'monthly' ? 'active' : ''}`} onClick={() => setView('monthly')}>Monthly Strategic</button>
                    </div>

                </div>
                {view === 'daily' && (
                    <div className="status-indicator">
                        <span className="pulse-dot"></span>
                        <span>Live Map Active</span>
                    </div>
                )}
            </motion.header>

            <div className="persona-display-row">
                <motion.div className="persona-card glass-card highlight-border" variants={itemVariants}>
                    <div className="persona-badge">
                        {typeIcons[persona.icon] || <Crown size={32} />}
                    </div>
                    <div className="persona-info">
                        <span className="persona-tag">Psychological Persona</span>
                        <h2 className="persona-name">{persona.name}</h2>
                        <div className="persona-class-line">
                            <Zap size={14} />
                            <span>{persona.class} Class</span>
                        </div>
                    </div>
                    <div className="persona-visual-glow"></div>
                </motion.div>

                <div className="narrative-log-container">
                    <motion.div className="narrative-log glass-card highlight-border" variants={itemVariants}>
                        <h4><Sparkles size={14} /> SYSTEM ANALYTICS LOG</h4>
                        <Typewriter text={riskData.narrative} />
                    </motion.div>

                    <motion.div className="recommendation-banner glass-card elite-shadow flex-grow-banner" variants={itemVariants} style={{ borderColor: reco.color, background: reco.bg, marginBottom: 0 }}>
                        <div className="reco-icon" style={{ backgroundColor: reco.color }}>
                            <Sparkles size={20} color="#fff" />
                        </div>
                        <div className="reco-content">
                            <h4>{reco.title} Recommendation</h4>
                            <p>{reco.text}</p>
                        </div>
                    </motion.div>
                </div>
            </div>

            <div className="analytics-grid">
                <motion.div className="stat-card glass-card elite-shadow premium-card" variants={itemVariants}>
                    <TrendBadge value={compData.volume} />
                    <div className="stat-content">
                        <h3>Volume</h3>
                        <div className="stat-value">{dynamicStats.total_sessions}</div>
                        <span className="stat-label">{view === 'daily' ? 'Today\'s Sessions' : 'Total Sessions'}</span>
                    </div>
                    <div className="stat-icon-wrapper pulse-soft">
                        <Activity size={28} />
                    </div>
                </motion.div>
                <motion.div className="stat-card glass-card elite-shadow premium-card" variants={itemVariants}>
                    <TrendBadge value={compData.dependency} />
                    <div className="stat-content">
                        <h3>{view === 'daily' ? 'Focus' : 'Stability'}</h3>
                        <div className="stat-value">
                            {view === 'daily' ? (dynamicStats.avg_dependency) : Math.round(((dynamicStats.avg_dependency) + (dynamicStats.avg_capability)) / 2)}%
                        </div>
                        <span className="stat-label">{view === 'daily' ? 'Daily Dependency' : 'System Mean'}</span>
                    </div>
                    <div className="stat-icon-wrapper pulse-soft" style={{ background: 'rgba(236, 72, 153, 0.1)', color: 'var(--color-accent-primary)' }}>
                        <TrendingUp size={28} />
                    </div>
                </motion.div>
                <motion.div className="stat-card glass-card elite-shadow premium-card" variants={itemVariants}>
                    <TrendBadge value={compData.capability} />
                    <div className="stat-content">
                        <h3>Growth</h3>
                        <div className="stat-value">{dynamicStats.avg_capability}%</div>
                        <span className="stat-label">{view === 'daily' ? 'Today\'s Capability' : 'Avg Capability'}</span>
                    </div>
                    <div className="stat-icon-wrapper pulse-soft" style={{ background: 'rgba(139, 92, 246, 0.1)', color: 'var(--color-accent-secondary)' }}>
                        <BarChart2 size={28} />
                    </div>
                </motion.div>
                <motion.div className="stat-card glass-card elite-shadow premium-card dna-card" variants={itemVariants}>
                    <div className="stat-content" style={{ width: '100%' }}>
                        <h3>Dependency DNA</h3>
                        <div className="dna-list">
                            {sortedTypes.length > 0 ? sortedTypes.map(([type, count]) => (
                                <div key={type} className="dna-item">
                                    <div className="dna-label">
                                        <span className="dna-icon">{typeIcons[type] || <Sparkles size={14} />}</span>
                                        <span className="dna-name">{type}</span>
                                    </div>
                                    <div className="dna-bar-bg">
                                        <div
                                            className="dna-bar-fill"
                                            style={{ width: `${(count / totalDnaSessions) * 100}%` }}
                                        >
                                            <span className="dna-percent">
                                                {Math.round((count / totalDnaSessions) * 100)}%
                                            </span>
                                        </div>
                                    </div>
                                    <span className="dna-count">{count}</span>
                                </div>
                            )) : (
                                <div className="no-dna-data">
                                    <Activity size={32} className="shimmer-icon" />
                                    <p>Analyzing behavioral patterns...</p>
                                </div>
                            )}
                        </div>
                    </div>
                </motion.div>
            </div>

            <motion.div className="chart-section" variants={containerVariants}>
                <motion.div className="chart-container-large glass-card elite-chart highlight-border interaction-map-container" variants={itemVariants}>
                    <div className="chart-header">
                        <h2>{view === 'daily' ? 'Session Interaction Map' : 'Strategic Stability Matrix'}</h2>
                    </div>
                    <div style={{ height: '450px', width: '100%' }}>
                        <ResponsiveContainer>
                            <ComposedChart data={chartDataWithForecast} margin={{ top: 20, right: 30, left: 10, bottom: 20 }}>
                                <defs>
                                    <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.4} />
                                        <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0} />
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
                                <YAxis stroke="#94a3b8" fontSize={11} fontWeight={600} domain={[0, 100]} tickLine={false} axisLine={false} />
                                <Tooltip content={<CustomTooltip />} />
                                <Area
                                    type="monotone"
                                    dataKey="dependency"
                                    stroke="#8b5cf6"
                                    strokeWidth={4}
                                    fillOpacity={1}
                                    fill="url(#areaGradient)"
                                    animationDuration={2000}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="forecast"
                                    stroke="#ec4899"
                                    strokeWidth={3}
                                    strokeDasharray="5 5"
                                    dot={{ r: 4, fill: '#ec4899' }}
                                    animationDuration={3000}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="capability"
                                    stroke="#3b82f6"
                                    strokeWidth={3}
                                    dot={{ r: 6, fill: '#3b82f6' }}
                                    animationDuration={2500}
                                />
                            </ComposedChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>

                <motion.div className="chart-container-large glass-card elite-chart highlight-border" variants={itemVariants}>
                    <div className="chart-header">
                        <h2>{view === 'daily' ? 'Understanding Depth' : 'Dynamic Growth Volume'}</h2>
                    </div>
                    <div style={{ height: '350px', width: '100%' }}>
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

                <motion.div className="chart-container-large glass-card elite-chart highlight-border density-map-card" variants={itemVariants}>
                    <div className="chart-header">
                        <div className="title-with-icon">
                            <Activity className="header-icon-glow" size={20} style={{ color: '#F0ABFC' }} />
                            <h2>Interaction Density</h2>
                        </div>
                    </div>
                    <div className="density-heatmap">
                        <HeatRing data={densityData} />
                        <div className="density-center-info">
                            <div className="density-peak-label">Peak Activity</div>
                            <div className="density-peak-value">
                                {densityData.indexOf(Math.max(...densityData))}:00
                            </div>
                        </div>
                    </div>
                </motion.div>

                <motion.div className="chart-container-large glass-card elite-chart highlight-border" variants={itemVariants}>
                    <div className="chart-header">
                        <div className="title-with-icon">
                            <Fingerprint className="header-icon-glow" size={20} style={{ color: '#8b5cf6' }} />
                            <h2>Behavioral Fingerprint</h2>
                        </div>
                    </div>
                    <div style={{ height: '350px', width: '100%', position: 'relative' }}>
                        <ResponsiveContainer>
                            <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarDataWithBenchmark}>
                                <PolarGrid stroke="rgba(0,0,0,0.05)" />
                                <PolarAngleAxis
                                    dataKey="subject"
                                    tick={{ fill: 'var(--color-text-secondary)', fontSize: 11, fontWeight: 700 }}
                                />
                                <PolarRadiusAxis angle={30} domain={[0, 100]} hide />
                                <Radar
                                    name="Current Signature"
                                    dataKey="value"
                                    stroke="var(--color-accent-primary)"
                                    fill="var(--color-accent-primary)"
                                    fillOpacity={0.4}
                                    strokeWidth={3}
                                    dot={{ r: 4, fill: '#fff', stroke: 'var(--color-accent-primary)', strokeWidth: 2 }}
                                />
                                <Radar
                                    name="Ideal Benchmark"
                                    dataKey="benchmark"
                                    stroke="#10b981"
                                    fill="#10b981"
                                    fillOpacity={0.15}
                                    strokeDasharray="4 4"
                                />
                                <Legend iconType="diamond" />
                                <Tooltip content={<CustomTooltip />} />
                            </RadarChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>

                <motion.div className="chart-container-large glass-card elite-chart highlight-border" variants={itemVariants}>
                    <div className="chart-header">
                        <div className="title-with-icon">
                            <Award className="header-icon-glow" size={20} style={{ color: '#ec4899' }} />
                            <h2>Competency Plateau</h2>
                        </div>
                    </div>
                    <div style={{ height: '350px', width: '100%' }}>
                        <ResponsiveContainer>
                            <LineChart data={activeTrends} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                                <defs>
                                    <filter id="lineGlow" x="-20%" y="-20%" width="140%" height="140%">
                                        <feGaussianBlur stdDeviation="5" result="blur" />
                                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                                    </filter>
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
                                    dot={{ r: 7, fill: '#8b5cf6', strokeWidth: 3, stroke: '#fff' }}
                                    activeDot={{ r: 12, stroke: '#fff', strokeWidth: 4, filter: 'url(#lineGlow)' }}
                                    animationDuration={2500}
                                    filter="url(#lineGlow)"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </motion.div>

                <motion.div className="chart-container-large glass-card elite-chart highlight-border risk-summary-card" variants={itemVariants}>
                    <div className="chart-header">
                        <div className="title-with-icon">
                            <Brain className="header-icon-glow" size={20} />
                            <h2>Mental & Behavioral Risk</h2>
                        </div>
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={riskData.level}
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className={`risk-badge level-${riskData.level.toLowerCase()}`}
                            >
                                {riskData.level === 'None' ? <ShieldCheck size={14} /> : <AlertTriangle size={14} />}
                                {riskData.level}
                            </motion.div>
                        </AnimatePresence>
                    </div>

                    <div className="risk-description-premium">
                        <p>{getRiskDescription(riskData.level)}</p>
                    </div>

                    <div className="risk-content-flex">
                        <div className="risk-pie-wrapper">
                            <div style={{ height: '240px', width: '100%' }}>
                                <ResponsiveContainer>
                                    <PieChart>
                                        <Pie
                                            data={riskData.factors.some(f => f.value > 0) ? riskData.factors : [{ name: 'Healthy Balance', value: 100 }]}
                                            innerRadius={65}
                                            outerRadius={90}
                                            paddingAngle={8}
                                            dataKey="value"
                                            stroke="none"
                                            animationDuration={1500}
                                        >
                                            {riskData.factors.some(f => f.value > 0)
                                                ? riskData.factors.map((entry, index) => (
                                                    <Cell
                                                        key={`cell-${index}`}
                                                        fill={RISK_COLORS[index % RISK_COLORS.length]}
                                                        style={{ filter: `drop-shadow(0 0 8px ${RISK_COLORS[index % RISK_COLORS.length]}44)` }}
                                                    />
                                                ))
                                                : <Cell fill="rgba(16, 185, 129, 0.2)" stroke="rgba(16, 185, 129, 0.4)" strokeWidth={1} />
                                            }
                                        </Pie>
                                        <Tooltip />
                                    </PieChart>
                                </ResponsiveContainer>
                                <div className="risk-score-center">
                                    <motion.span
                                        key={riskData.score}
                                        initial={{ scale: 0.5, opacity: 0 }}
                                        animate={{ scale: 1, opacity: 1 }}
                                        transition={{ type: 'spring', stiffness: 260, damping: 20 }}
                                        className="score-val"
                                    >
                                        {riskData.score}%
                                    </motion.span>
                                    <motion.span
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        transition={{ delay: 0.2 }}
                                        className="score-label"
                                    >
                                        System Risk
                                    </motion.span>
                                </div>
                            </div>
                        </div>
                        <div className="risk-factors-info">
                            <h4 className="factors-title">Primary Contributors</h4>
                            {riskData.factors.map((factor, index) => (
                                <div key={index} className="risk-factor-item premium-factor">
                                    <div className="factor-dot-glow" style={{ backgroundColor: RISK_COLORS[index % RISK_COLORS.length] }}></div>
                                    <div className="factor-details">
                                        <div className="factor-header">
                                            <span className="factor-name">{factor.name}</span>
                                            <span className="factor-percent">{factor.value}%</span>
                                        </div>
                                        <div className="factor-bar-bg">
                                            <motion.div
                                                className="factor-bar-fill"
                                                initial={{ width: 0 }}
                                                animate={{ width: `${factor.value}%` }}
                                                style={{ backgroundColor: RISK_COLORS[index % RISK_COLORS.length] }}
                                            ></motion.div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </motion.div>
            </motion.div>
        </motion.div>
    )
}
