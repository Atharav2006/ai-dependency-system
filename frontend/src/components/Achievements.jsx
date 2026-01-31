import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Award, Lock, Footprints, Flame, Crown, Handshake, Brain, Trophy } from 'lucide-react'
import { supabase } from '../lib/supabase'
import { api } from '../services/api'
import './Achievements.css'

const ICONS = {
    Footprints,
    Flame,
    Crown,
    Handshake,
    Brain
}

export default function Achievements() {
    const [achievements, setAchievements] = useState([])
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadAchievements()
    }, [])

    const loadAchievements = async () => {
        try {
            const { data: { session } } = await supabase.auth.getSession()
            const token = session?.access_token
            if (!token) return

            // We need to fetch from our new backend endpoint
            // Assuming api.js is updated or we fetch directly
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/gamification/achievements`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            const data = await response.json()

            setAchievements(data.badges || [])
            setStats(data.stats || {})
        } catch (error) {
            console.error("Failed to load achievements", error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) return <div className="ach-loading">Loading Awards...</div>

    return (
        <div className="achievements-container">
            <div className="ach-header">
                <div>
                    <h2><Trophy className="text-yellow-400 inline mr-2" /> Recognition</h2>
                    <p className="text-sm text-gray-400">Unlock badges by improving your independence.</p>
                </div>
                {stats && (
                    <div className="streak-badge">
                        <Flame size={16} className={stats.current_streak > 0 ? "text-orange-500 animate-pulse" : "text-gray-600"} />
                        <span>{stats.current_streak} Day Streak</span>
                    </div>
                )}
            </div>

            <div className="badges-grid">
                {achievements.map((badge) => {
                    const Icon = ICONS[badge.icon] || Award
                    return (
                        <motion.div
                            key={badge.id}
                            className={`badge-card ${badge.unlocked ? 'unlocked' : 'locked'}`}
                            whileHover={{ scale: 1.05 }}
                        >
                            <div className="badge-icon">
                                {badge.unlocked ? (
                                    <Icon size={32} />
                                ) : (
                                    <Lock size={24} />
                                )}
                            </div>
                            <div className="badge-info">
                                <h3>{badge.name}</h3>
                                <p>{badge.description}</p>
                                {badge.unlocked && (
                                    <span className="award-date">
                                        {new Date(badge.awarded_at).toLocaleDateString()}
                                    </span>
                                )}
                            </div>
                        </motion.div>
                    )
                })}
            </div>
        </div>
    )
}
