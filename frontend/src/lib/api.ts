/**
 * API Client for PromptForge AI backend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function getHeaders(): HeadersInit {
    const headers: HeadersInit = { 'Content-Type': 'application/json' };
    if (typeof window !== 'undefined') {
        const token = localStorage.getItem('pf_token');
        if (token) headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers: { ...getHeaders(), ...options.headers },
    });
    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(error.detail || 'Request failed');
    }
    return res.json();
}

export const api = {
    // Auth
    register: (data: { email: string; username: string; password: string }) =>
        request<any>('/api/auth/register', { method: 'POST', body: JSON.stringify(data) }),

    login: (data: { email: string; password: string }) =>
        request<any>('/api/auth/login', { method: 'POST', body: JSON.stringify(data) }),

    getMe: () => request<any>('/api/auth/me'),

    // Models
    getModels: () => request<any>('/api/models'),

    // Generate
    generate: (data: {
        user_request: string;
        provider: string;
        model_name?: string;
        custom_role?: string;
        custom_tone?: string;
        execute?: boolean;
    }) => request<any>('/api/generate', { method: 'POST', body: JSON.stringify(data) }),

    // Debug
    debugPrompt: (prompt_text: string) =>
        request<any>('/api/debug', { method: 'POST', body: JSON.stringify({ prompt_text }) }),

    // History
    getHistory: (skip = 0, limit = 50) =>
        request<any>(`/api/history?skip=${skip}&limit=${limit}`),

    deleteHistory: (id: string) =>
        request<any>(`/api/history/${id}`, { method: 'DELETE' }),

    // Library
    getLibrary: (category?: string) =>
        request<any>(`/api/library${category ? `?category=${category}` : ''}`),

    createLibraryItem: (data: {
        title: string; category: string; prompt_text: string;
        description?: string; tags?: string[];
    }) => request<any>('/api/library', { method: 'POST', body: JSON.stringify(data) }),

    deleteLibraryItem: (id: string) =>
        request<any>(`/api/library/${id}`, { method: 'DELETE' }),

    // Workflows
    getWorkflows: () => request<any>('/api/workflows'),

    createWorkflow: (data: { name: string; description?: string; steps: any[] }) =>
        request<any>('/api/workflows', { method: 'POST', body: JSON.stringify(data) }),

    runWorkflow: (data: { workflow_id: string; provider: string; model_name?: string }) =>
        request<any>('/api/workflows/run', { method: 'POST', body: JSON.stringify(data) }),

    deleteWorkflow: (id: string) =>
        request<any>(`/api/workflows/${id}`, { method: 'DELETE' }),

    // API Key Management
    getAPIKeys: () => request<any>('/api/settings/api-keys'),

    addAPIKey: (data: { provider: string; api_key: string; label?: string }) =>
        request<any>('/api/settings/api-keys', { method: 'POST', body: JSON.stringify(data) }),

    deleteAPIKey: (id: string) =>
        request<any>(`/api/settings/api-keys/${id}`, { method: 'DELETE' }),

    // Health
    health: () => request<any>('/api/health'),
};
