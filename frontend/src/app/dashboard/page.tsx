'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import Sidebar from '@/components/Sidebar';

const PROVIDERS = [
    { key: 'openai', label: 'OpenAI GPT-4', icon: '🟢' },
    { key: 'claude', label: 'Claude 3.5', icon: '🟠' },
    { key: 'gemini', label: 'Gemini 2.0', icon: '🔵' },
    { key: 'mistral', label: 'Mistral Large', icon: '🟡' },
    { key: 'deepseek', label: 'DeepSeek', icon: '🟣' },
    { key: 'ollama', label: 'Ollama (Local)', icon: '⚫' },
];

export default function DashboardPage() {
    const { user, loading: authLoading } = useAuth();
    const router = useRouter();

    const [userRequest, setUserRequest] = useState('');
    const [provider, setProvider] = useState('openai');
    const [generating, setGenerating] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState('');
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        if (!authLoading && !user) router.push('/login');
    }, [user, authLoading, router]);

    if (authLoading || !user) return null;

    const handleGenerate = async () => {
        if (!userRequest.trim()) return;
        setGenerating(true);
        setError('');
        setResult(null);
        try {
            const res = await api.generate({
                user_request: userRequest,
                provider,
                execute: true,
            });
            setResult(res);
        } catch (err: any) {
            setError(err.message || 'Generation failed');
        } finally {
            setGenerating(false);
        }
    };

    const handleSaveToLibrary = async () => {
        if (!result) return;
        try {
            await api.createLibraryItem({
                title: userRequest.slice(0, 100),
                category: result.intent?.category || 'general',
                prompt_text: result.generated_prompt,
                description: userRequest,
            });
            alert('Saved to library!');
        } catch (err: any) {
            alert('Failed to save: ' + err.message);
        }
    };

    const quickExamples = [
        'Write a blog post about AI security best practices',
        'Generate Python code for a REST API with authentication',
        'Create a YouTube video script about machine learning',
        'Analyze the competitive landscape of cloud providers',
        'Design a marketing strategy for a SaaS product launch',
    ];

    return (
        <div>
            <Sidebar />
            <div className="main-content">
                <div className="fade-in">
                    {/* Header */}
                    <div style={{ marginBottom: '2rem' }}>
                        <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>
                            ⚡ <span className="gradient-text">Forge Your Prompt</span>
                        </h1>
                        <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem', fontSize: '0.9rem' }}>
                            Describe what you need — we&apos;ll engineer the perfect prompt
                        </p>
                    </div>

                    {/* Input Section */}
                    <div className="card" style={{ marginBottom: '1.5rem' }}>
                        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
                            <div style={{ flex: 1, minWidth: '250px' }}>
                                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>
                                    Your Request
                                </label>
                                <textarea
                                    ref={textareaRef}
                                    value={userRequest}
                                    onChange={(e) => setUserRequest(e.target.value)}
                                    className="textarea-dark"
                                    placeholder="Describe what you want the AI to do... e.g., 'Write a blog post about AI security'"
                                    style={{ minHeight: '100px' }}
                                    onKeyDown={(e) => { if (e.key === 'Enter' && e.metaKey) handleGenerate(); }}
                                />
                            </div>
                            <div style={{ minWidth: '200px' }}>
                                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>
                                    AI Model
                                </label>
                                <select value={provider} onChange={(e) => setProvider(e.target.value)} className="select-dark" style={{ width: '100%' }}>
                                    {PROVIDERS.map((p) => (
                                        <option key={p.key} value={p.key}>{p.icon} {p.label}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        {/* Quick examples */}
                        <div style={{ marginBottom: '1rem' }}>
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginRight: '0.5rem' }}>Try:</span>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.25rem' }}>
                                {quickExamples.map((ex, i) => (
                                    <button
                                        key={i}
                                        onClick={() => setUserRequest(ex)}
                                        style={{
                                            background: 'var(--bg-secondary)', border: '1px solid var(--border)',
                                            color: 'var(--text-secondary)', padding: '0.35rem 0.75rem',
                                            borderRadius: '999px', fontSize: '0.75rem', cursor: 'pointer',
                                            transition: 'all 0.15s',
                                        }}
                                        onMouseOver={(e) => { (e.target as any).style.borderColor = 'var(--accent)'; (e.target as any).style.color = 'var(--accent)'; }}
                                        onMouseOut={(e) => { (e.target as any).style.borderColor = 'var(--border)'; (e.target as any).style.color = 'var(--text-secondary)'; }}
                                    >
                                        {ex}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <button onClick={handleGenerate} className="btn-primary" disabled={generating || !userRequest.trim()} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            {generating ? <><span className="spinner" /> Forging...</> : '⚡ Generate Prompt & Response'}
                        </button>
                    </div>

                    {error && (
                        <div style={{ background: 'rgba(248, 113, 113, 0.1)', border: '1px solid rgba(248, 113, 113, 0.3)', borderRadius: '0.75rem', padding: '1rem', marginBottom: '1.5rem', color: 'var(--danger)', fontSize: '0.85rem' }}>
                            {error}
                        </div>
                    )}

                    {/* Security warnings */}
                    {result?.security_scan?.warnings?.length > 0 && (
                        <div className="card" style={{ borderColor: 'rgba(251, 191, 36, 0.3)', marginBottom: '1.5rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                                <span>⚠️</span>
                                <span style={{ fontWeight: 700, color: 'var(--warning)' }}>Security Warnings</span>
                                <span className="badge badge-warning">{result.security_scan.risk_level}</span>
                            </div>
                            {result.security_scan.recommendations.map((rec: string, i: number) => (
                                <p key={i} style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.25rem' }}>{rec}</p>
                            ))}
                        </div>
                    )}

                    {/* Three Panel View */}
                    {result && (
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                            {/* Panel 1: Intent & Context */}
                            <div className="panel fade-in">
                                <div className="panel-header">
                                    <span>🔍</span> Intent Analysis
                                </div>
                                <div className="panel-body">
                                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
                                        <span className="badge badge-accent">{result.intent?.category?.replace('_', ' ')}</span>
                                        <span className="badge badge-success">confidence: {(result.intent?.confidence * 100).toFixed(0)}%</span>
                                    </div>
                                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                        <p><strong style={{ color: 'var(--text-primary)' }}>Audience:</strong> {result.context?.audience}</p>
                                        <p><strong style={{ color: 'var(--text-primary)' }}>Scope:</strong> {result.context?.scope}</p>
                                        <p><strong style={{ color: 'var(--text-primary)' }}>Specificity:</strong> {result.context?.specificity_level}</p>
                                        {result.context?.key_topics?.length > 0 && (
                                            <div style={{ marginTop: '0.5rem' }}>
                                                <strong style={{ color: 'var(--text-primary)' }}>Topics: </strong>
                                                {result.context.key_topics.map((t: string, i: number) => (
                                                    <span key={i} className="badge badge-info" style={{ margin: '0.15rem' }}>{t}</span>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                    <div style={{ marginTop: '1rem' }}>
                                        <strong style={{ fontSize: '0.8rem' }}>Optimizations Applied:</strong>
                                        <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap', marginTop: '0.35rem' }}>
                                            {result.optimizations?.map((o: string, i: number) => (
                                                <span key={i} className="badge badge-accent" style={{ fontSize: '0.7rem' }}>{o.replace(/_/g, ' ')}</span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Panel 2: Generated Prompt */}
                            <div className="panel fade-in" style={{ gridRow: 'span 2' }}>
                                <div className="panel-header" style={{ justifyContent: 'space-between' }}>
                                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                        <span>🏗️</span> Generated Prompt
                                    </span>
                                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                                        <button onClick={() => navigator.clipboard.writeText(result.generated_prompt)} className="btn-secondary" style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem' }}>
                                            📋 Copy
                                        </button>
                                        <button onClick={handleSaveToLibrary} className="btn-secondary" style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem' }}>
                                            💾 Save
                                        </button>
                                    </div>
                                </div>
                                <div className="panel-body">
                                    <pre style={{
                                        background: 'var(--bg-primary)', border: '1px solid var(--border)',
                                        borderRadius: '0.5rem', padding: '1rem', fontSize: '0.8rem',
                                        whiteSpace: 'pre-wrap', wordBreak: 'break-word',
                                        color: 'var(--text-secondary)', lineHeight: 1.6,
                                        maxHeight: '500px', overflow: 'auto',
                                    }}>
                                        {result.generated_prompt}
                                    </pre>
                                </div>
                            </div>

                            {/* Panel 3: AI Response */}
                            <div className="panel fade-in">
                                <div className="panel-header" style={{ justifyContent: 'space-between' }}>
                                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                        <span>🤖</span> AI Response
                                        <span className="badge badge-info" style={{ fontSize: '0.7rem' }}>{result.model_used}</span>
                                    </span>
                                    {result.ai_response && (
                                        <button onClick={() => navigator.clipboard.writeText(result.ai_response)} className="btn-secondary" style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem' }}>
                                            📋 Copy
                                        </button>
                                    )}
                                </div>
                                <div className="panel-body response-content" style={{ maxHeight: '400px', overflow: 'auto' }}>
                                    {result.ai_response ? (
                                        <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.85rem', lineHeight: 1.7, color: 'var(--text-secondary)' }}>
                                            {result.ai_response}
                                        </div>
                                    ) : (
                                        <p style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>No response generated</p>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
