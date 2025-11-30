/**
 * Frontend API client for calling the C# backend (which delegates to Python backend)
 * Provides methods for projects, routes, and traffic operations
 */

class FrontendApiClient {
    constructor(baseUrl = '/api') {
        this.baseUrl = baseUrl;
    }

    /**
     * Make a fetch request with common error handling
     */
    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({ error: response.statusText }));
                throw new Error(error.error || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // ============ Projects API ============

    async getProjects() {
        return this.request('/projects', { method: 'GET' });
    }

    async getProject(id) {
        return this.request(`/projects/${id}`, { method: 'GET' });
    }

    async createProject(project) {
        return this.request('/projects', {
            method: 'POST',
            body: JSON.stringify(project)
        });
    }

    async updateProject(id, project) {
        return this.request(`/projects/${id}`, {
            method: 'PUT',
            body: JSON.stringify(project)
        });
    }

    // ============ Routes API ============

    async analyzeRoute(coordinates) {
        return this.request('/routes/analyze', {
            method: 'POST',
            body: JSON.stringify({ coordinates })
        });
    }

    async recommendRoute(routeId, startLon, startLat, endLon, endLat) {
        const params = new URLSearchParams({
            startLon,
            startLat,
            endLon,
            endLat
        });
        return this.request(`/routes/${routeId}/recommend?${params}`, { method: 'POST' });
    }

    async getTraffic(routeId) {
        return this.request(`/routes/${routeId}/traffic`, { method: 'GET' });
    }
}

// Export for use in HTML
const apiClient = new FrontendApiClient();
