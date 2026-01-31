import React, { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Fingerprint, Shield, Zap, Globe, QrCode, BarChart3, Activity, Award, ShieldCheck } from 'lucide-react';
import './Passport.css';

const Passport = forwardRef(({ user, stats, analysis }, ref) => {
    const currentDate = new Date().toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    // Helper to determine tier based on stats
    const getTier = () => {
        const score = stats?.avg_dependency || 0;
        if (score < 30) return { name: 'Sovereign', color: '#059669', icon: ShieldCheck };
        if (score < 60) return { name: 'Collaborator', color: '#2563eb', icon: Award };
        return { name: 'Dependent', color: '#db2777', icon: Activity };
    };

    const tier = getTier();
    const TierIcon = tier.icon;

    // SVG Circular Progress Component
    const CircularMetric = ({ value, color, label }) => {
        const radius = 35;
        const circumference = 2 * Math.PI * radius;
        const offset = circumference - (value / 100) * circumference;

        return (
            <div className="metric-circle-item">
                <svg width="100" height="100" viewBox="0 0 100 100">
                    <circle
                        cx="50" cy="50" r={radius}
                        fill="transparent"
                        stroke="rgba(255,255,255,0.05)"
                        strokeWidth="8"
                    />
                    <circle
                        cx="50" cy="50" r={radius}
                        fill="transparent"
                        stroke={color}
                        strokeWidth="8"
                        strokeDasharray={circumference}
                        strokeDashoffset={offset}
                        strokeLinecap="round"
                        style={{ filter: `drop-shadow(0 0 5px ${color})` }}
                    />
                    <text
                        x="50" y="55"
                        textAnchor="middle"
                        fill="var(--color-text-primary)"
                        fontSize="18"
                        fontWeight="900"
                    >
                        {Math.round(value)}%
                    </text>
                </svg>
                <span className="metric-label">{label}</span>
            </div>
        );
    };

    return (
        <div className="passport-container" ref={ref}>
            <div className="passport-hologram-overlay" />

            <div className="passport-frame">
                <div className="official-stamp">
                    <div className="stamp-inner">
                        <Fingerprint size={32} style={{ marginBottom: 4 }} />
                        <br />VERIFIED<br />AGENT
                    </div>
                </div>

                <div className="passport-header">
                    <div className="passport-logo">
                        <Zap size={24} style={{ color: 'var(--neon-cyan)', marginRight: 10 }} />
                        <h1 style={{ fontSize: 20, letterSpacing: 3, margin: 0, fontWeight: 900 }}>OFFICIAL AI AGENT PASS</h1>
                    </div>
                    <div className="passport-id-badge">
                        <span style={{ fontSize: 10, opacity: 0.5, letterSpacing: 2 }}>REF: {user?.id?.slice(0, 12).toUpperCase()}</span>
                    </div>
                </div>

                <div className="passport-body">
                    <div className="passport-profile-side">
                        <div className="profile-hex-container">
                            <span className="profile-avatar-placeholder">
                                {user?.email?.[0]?.toUpperCase() || 'A'}
                            </span>
                        </div>
                        <div className="passport-qr">
                            <QrCode size={60} color="rgba(255,255,255,0.2)" />
                        </div>
                    </div>

                    <div className="passport-info-side">
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
                            <div className="detail-row">
                                <label>AGENT IDENTIFIER</label>
                                <p>{user?.email?.split('@')[0].toUpperCase() || 'UNKNOWN'}</p>
                            </div>
                            <div className="detail-row">
                                <label>SYSTEM STATUS</label>
                                <p style={{ color: tier.color }}>{tier.name.toUpperCase()}</p>
                            </div>
                            <div className="detail-row">
                                <label>DATE OF ISSUE</label>
                                <p>{currentDate.toUpperCase()}</p>
                            </div>
                            <div className="detail-row">
                                <label>EXPIRY</label>
                                <p>UNLIMITED</p>
                            </div>
                        </div>

                        <div className="passport-metrics-header" style={{ marginTop: 10, borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: 5 }}>
                            <span style={{ fontSize: 10, fontWeight: 800, opacity: 0.4, letterSpacing: 2 }}>CORE BEHAVIORAL METRICS</span>
                        </div>

                        <div className="passport-metrics-grid">
                            <CircularMetric
                                value={100 - (stats?.avg_dependency || 0)}
                                color="var(--neon-cyan)"
                                label="AUTONOMY"
                            />
                            <CircularMetric
                                value={stats?.avg_capability || 0}
                                color="var(--neon-purple)"
                                label="CAPABILITY"
                            />
                            <CircularMetric
                                value={stats?.total_sessions > 10 ? 100 : (stats?.total_sessions / 10) * 100}
                                color="var(--neon-pink)"
                                label="ENGAGEMENT"
                            />
                        </div>
                    </div>
                </div>

                <div className="passport-footer">
                    <div className="mrz-code">
                        P&lt;AI&lt;{user?.email?.split('@')[0].toUpperCase().padEnd(15, '&lt;')}AGENT&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;
                        <br />
                        {user?.id?.replace(/-/g, '').toUpperCase().slice(0, 20)}&lt;&lt;DEP{Math.round(stats?.avg_dependency || 0).toString().padStart(3, '0')}CAP{Math.round(stats?.avg_capability || 0).toString().padStart(3, '0')}
                    </div>
                </div>
            </div>
        </div>
    );
});

export default Passport;
