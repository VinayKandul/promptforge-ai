'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import Sidebar from '@/components/Sidebar';

export default function HistoryPage() {
    const { user, loading: authLoading } = useAuth();
    const router = useRouter();
    const [items, setItems] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [expandedId, setExpandedId] = useState<string | null>(null);

    useEffect(() => {
        if (!authLoading && !user) router.push('/login');
    }, [user, authLoading, router]);

    useEffect(() => {
        if (user) {
            api.getHistory().then((res) => { setItems(res.items || []); setLoading(false); }).catch(() => setLoading(false));
        }
    }, [user]);

    if (authLoading || !user) return null;

    const handleDelete = async (id: string) => {
        try {
            await api.deleteHistory(id);
            setItems(items.filter((i) => i.id !== id));
        } catch (err: any) {
            alert('Failed to delete: ' + err.message);
        }
    };

    const getCategoryColor = (cat: string) => {
        const map: Record<string, string> = {
            coding: 'badge-accent', content_creation: 'badge-success',
            research: 'badge-info', education: 'badge-warning',
            marketing: 'badge-danger', analysis: 'badge-info',
        };
        return map[cat] || 'badge-accent';
    };

    return (
        <div>
            <Sidebar />
            <div className="main-content">
                <div className="fade-in">
                    <h1 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '0.5rem' }}>
                        📜 <span className="gradient-text">Prompt History</span>
                    </h1>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', fontSize: '0.9rem' }}>
                        All your previously generated prompts and responses
                    </p>

                    {loading ? (
                        <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
                            <span className="spinner" style={{ width: '30px', height: '30px' }} />
                        </div>
                    ) : items.length === 0 ? (
                        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
                            <p style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📝</p>
                            <p style={{ color: 'var(--text-secondary)' }}>No history yet. Start forging prompts!</p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                            {items.map((item) => (
                                <div key={item.id} className="card" style={{ cursor: 'pointer' }} onClick={() => setExpandedId(expandedId === item.id ? null : item.id)}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <div style={{ flex: 1 }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
                                                <span className={`badge ${getCategoryColor(item.intent_category)}`}>{(item.intent_category || '').replace('_', ' ')}</span>
                                                <span className="badge badge-info" style={{ fontSize: '0.7rem' }}>{item.model_used}</span>
                                                <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                                                    {item.created_at ? new Date(item.created_at).toLocaleString() : ''}
                                                </span>
                                            </div>
                                            <p style={{ fontWeight: 600, fontSize: '0.95rem' }}>{item.user_request}</p>
                                        </div>
                                        <button onClick={(e) => { e.stopPropagation(); handleDelete(item.id); }} className="btn-danger" style={{ flexShrink: 0 }}>
                                            🗑️
                                        </button>
                                    </div>

                                    {expandedId === item.id && (
                                        <div className="fade-in" style={{ marginTop: '1rem', borderTop: '1px solid var(--border)', paddingTop: '1rem' }}>
                                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                                <div>
                                                    <h4 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Generated Prompt</h4>
                                                    <pre style={{ background: 'var(--bg-primary)', border: '1px solid var(--border)', borderRadius: '0.5rem', padding: '0.75rem', fontSize: '0.75rem', whiteSpace: 'pre-wrap', color: 'var(--text-secondary)', maxHeight: '250px', overflow: 'auto' }}>
                                                        {item.generated_prompt}
                                                    </pre>
                                                </div>
                                                <div>
                                                    <h4 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>AI Response</h4>
                                                    <div style={{ background: 'var(--bg-primary)', border: '1px solid var(--border)', borderRadius: '0.5rem', padding: '0.75rem', fontSize: '0.75rem', whiteSpace: 'pre-wrap', color: 'var(--text-secondary)', maxHeight: '250px', overflow: 'auto' }}>
                                                        {item.ai_response || 'No response'}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
