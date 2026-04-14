'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { api } from '@/lib/api';

interface User {
    id: string;
    email: string;
    username: string;
    created_at: string;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, username: string, password: string) => Promise<void>;
    logout: () => void;
    loading: boolean;
}

const AuthContext = createContext<AuthContextType>({
    user: null,
    token: null,
    login: async () => { },
    register: async () => { },
    logout: () => { },
    loading: true,
});

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const stored = localStorage.getItem('pf_token');
        if (stored) {
            setToken(stored);
            api.getMe()
                .then((u) => setUser(u))
                .catch(() => {
                    localStorage.removeItem('pf_token');
                    setToken(null);
                })
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, []);

    const login = async (email: string, password: string) => {
        const res = await api.login({ email, password });
        localStorage.setItem('pf_token', res.access_token);
        setToken(res.access_token);
        setUser(res.user);
    };

    const register = async (email: string, username: string, password: string) => {
        const res = await api.register({ email, username, password });
        localStorage.setItem('pf_token', res.access_token);
        setToken(res.access_token);
        setUser(res.user);
    };

    const logout = () => {
        localStorage.removeItem('pf_token');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
