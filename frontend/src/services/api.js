const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'

class ApiClient {
    constructor() {
        this.baseUrl = BACKEND_URL
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`
        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        }

        const response = await fetch(url, config)

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Request failed' }))
            throw new Error(error.detail || `HTTP ${response.status}`)
        }

        return response.json()
    }

    // Session Management
    async startSession(accessToken) {
        return this.request('/sessions/start', {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        })
    }

    async sendMessage(sessionId, message, role, accessToken) {
        return this.request(`/sessions/${sessionId}/message`, {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
            body: JSON.stringify({ message, role }),
        })
    }

    async endSession(sessionId, accessToken) {
        return this.request(`/sessions/${sessionId}/end`, {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        })
    }

    async getSessionAnalysis(sessionId, accessToken) {
        return this.request(`/sessions/${sessionId}/analysis`, {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        })
    }

    async listSessions(accessToken) {
        return this.request('/sessions/', {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        })
    }

    async getSessionMessages(sessionId, accessToken) {
        return this.request(`/sessions/${sessionId}/messages`, {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        })
    }

    // Analytics
    async getAnalyticsSummary(accessToken) {
        return this.request('/analytics/summary', {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        })
    }

    async getAnalyticsTrends(accessToken) {
        return this.request('/analytics/trends', {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        })
    }
}

export const api = new ApiClient()
