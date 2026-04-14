'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import Sidebar from '@/components/Sidebar';

export default function DebuggerPage() {
    const { user, loading: authLoading } = useAuth();
    const router = useRouter();
    const [promptText, setPromptText] = useState('');
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!authLoading && !user) router.push('/login');
    }, [user, authLoading, router]);

    if (authLoading || !user) return null;

    const handleDebug = async () => {
        if (!promptText.trim()) return;
        setLoading(true);
        setError('');
        setResult(null);
        try {
            const res = await api.debugPrompt(promptText);
            setResult(res);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return 'var(--success)';
        if (score >= 60) return 'var(--info)';
        if (score >= 40) return 'var(--warning)';
        return 'var(--danger)';
    };

    return (
        <div>
            <Sidebar />
            <div className="main-content">
                <div className="fade-in">
                    <h1 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '0.5rem' }}>
                        🔧 <span className="gradient-text">Prompt Debugger</span>
                    </h1>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', fontSize: '0.9rem' }}>
                        Paste any prompt to analyze its quality and get improvement suggestions
                    </p>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                        {/* Input */}
                        <div>
                            <div className="card">
                                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>
                                    Paste Your Prompt
                                </label>
                                <textarea
                                    value={promptText}
                                    onChange={(e) => setPromptText(e.target.value)}
                                    className="textarea-dark"
                                    style={{ minHeight: '300px' }}
                                    placeholder="Paste your prompt here to analyze it..."
                                />
                                <button onClick={handleDebug} className="btn-primary" disabled={loading || !promptText.trim()} style={{ marginTop: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    {loading ? <><span className="spinner" /> Analyzing...</> : '🔍 Analyze Prompt'}
                                </button>
                            </div>
                        </div>

                        {/* Results */}
                        <div>
                            {error && (
                                <div style={{ background: 'rgba(248, 113, 113, 0.1)', border: '1px solid rgba(248, 113, 113, 0.3)', borderRadius: '0.75rem', padding: '1rem', marginBottom: '1rem', color: 'var(--danger)', fontSize: '0.85rem' }}>
                                    {error}
                                </div>
                            )}

                            {result && (
                                <div className="fade-in">
                                    {/* Score */}
                                    <div className="card" style={{ marginBottom: '1.5rem', textAlign: 'center', padding: '2rem' }}>
                                        <div className="score-ring" style={{
                                            margin: '0 auto 1rem',
                                            background: `conic-gradient(${getScoreColor(result.score)} ${result.score * 3.6}deg, var(--bg-secondary) 0deg)`,
                                            padding: '4px',
                                        }}>
                                            <div style={{
                                                background: 'var(--bg-card)',
                                                borderRadius: '50%',
                                                width: '100%',
                                                height: '100%',
                                                display: 'flex',
                                                flexDirection: 'column',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                            }}>
                                                <span style={{ fontSize: '1.5rem', fontWeight: 800, color: getScoreColor(result.score) }}>{result.score}</span>
                                                <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>/100</span>
                                            </div>
                                        </div>
                                        <span className={`badge ${result.score >= 70 ? 'badge-success' : result.score >= 40 ? 'badge-warning' : 'badge-danger'}`} style={{ fontSize: '1rem', padding: '0.4rem 1.2rem' }}>
                                            Grade: {result.grade}
                                        </span>
                                        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '0.5rem' }}>
                                            {result.word_count} words
                                        </p>
                                    </div>

                                    {/* Components Found */}
                                    {result.components_found?.length > 0 && (
                                        <div className="card" style={{ marginBottom: '1rem' }}>
                                            <h3 style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--success)' }}>✅ Components Present</h3>
                                            {result.components_found.map((c: any, i: number) => (
                                                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.4rem 0', borderBottom: i < result.components_found.length - 1 ? '1px solid var(--border)' : 'none' }}>
                                                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{c.description}</span>
                                                    <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>{c.score}/{c.max_score}</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {/* Missing Components */}
                                    {result.components_missing?.length > 0 && (
                                        <div className="card" style={{ marginBottom: '1rem' }}>
                                            <h3 style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--danger)' }}>❌ Missing Components</h3>
                                            {result.components_missing.map((c: any, i: number) => (
                                                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.4rem 0', borderBottom: i < result.components_missing.length - 1 ? '1px solid var(--border)' : 'none' }}>
                                                    <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{c.description}</span>
                                                    <span className="badge badge-danger" style={{ fontSize: '0.7rem' }}>{c.score}/{c.max_score}</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}

                                    {/* Suggestions */}
                                    {result.suggestions?.length > 0 && (
                                        <div className="card">
                                            <h3 style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--accent)' }}>💡 Improvement Suggestions</h3>
                                            {result.suggestions.map((s: string, i: number) => (
                                                <div key={i} style={{ padding: '0.5rem 0', borderBottom: i < result.suggestions.length - 1 ? '1px solid var(--border)' : 'none', fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                                                    {s}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
