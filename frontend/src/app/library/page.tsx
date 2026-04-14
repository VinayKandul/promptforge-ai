'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import Sidebar from '@/components/Sidebar';

const CATEGORIES = ['all', 'coding', 'content_creation', 'research', 'education', 'marketing', 'analysis'];

export default function LibraryPage() {
    const { user, loading: authLoading } = useAuth();
    const router = useRouter();
    const [items, setItems] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeCategory, setActiveCategory] = useState('all');
    const [expandedId, setExpandedId] = useState<string | null>(null);

    useEffect(() => {
        if (!authLoading && !user) router.push('/login');
    }, [user, authLoading, router]);

    useEffect(() => {
        if (user) fetchLibrary();
    }, [user, activeCategory]);

    const fetchLibrary = async () => {
        setLoading(true);
        try {
            const cat = activeCategory === 'all' ? undefined : activeCategory;
            const res = await api.getLibrary(cat);
            setItems(res.items || []);
        } catch { }
        setLoading(false);
    };

    if (authLoading || !user) return null;

    const handleDelete = async (id: string) => {
        try {
            await api.deleteLibraryItem(id);
            setItems(items.filter((i) => i.id !== id));
        } catch (err: any) {
            alert('Failed to delete: ' + err.message);
        }
    };

    return (
        <div>
            <Sidebar />
            <div className="main-content">
                <div className="fade-in">
                    <h1 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '0.5rem' }}>
                        📚 <span className="gradient-text">Prompt Library</span>
                    </h1>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', fontSize: '0.9rem' }}>
                        Your saved and organized prompt collection
                    </p>

                    {/* Category filters */}
                    <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
                        {CATEGORIES.map((cat) => (
                            <button
                                key={cat}
                                onClick={() => setActiveCategory(cat)}
                                className={activeCategory === cat ? 'btn-primary' : 'btn-secondary'}
                                style={{ padding: '0.5rem 1rem', fontSize: '0.8rem', textTransform: 'capitalize' }}
                            >
                                {cat.replace('_', ' ')}
                            </button>
                        ))}
                    </div>

                    {loading ? (
                        <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
                            <span className="spinner" style={{ width: '30px', height: '30px' }} />
                        </div>
                    ) : items.length === 0 ? (
                        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
                            <p style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📚</p>
                            <p style={{ color: 'var(--text-secondary)' }}>No saved prompts yet. Save prompts from the dashboard!</p>
                        </div>
                    ) : (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1rem' }}>
                            {items.map((item) => (
                                <div key={item.id} className="card glass-hover" style={{ cursor: 'pointer' }} onClick={() => setExpandedId(expandedId === item.id ? null : item.id)}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                                        <h3 style={{ fontWeight: 700, fontSize: '0.95rem' }}>{item.title}</h3>
                                        <button onClick={(e) => { e.stopPropagation(); handleDelete(item.id); }} className="btn-danger" style={{ flexShrink: 0 }}>
                                            🗑️
                                        </button>
                                    </div>
                                    <span className="badge badge-accent" style={{ marginBottom: '0.5rem' }}>{item.category?.replace('_', ' ')}</span>
                                    {item.description && (
                                        <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>{item.description}</p>
                                    )}
                                    {item.tags?.length > 0 && (
                                        <div style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
                                            {item.tags.map((t: string, i: number) => (
                                                <span key={i} className="badge badge-info" style={{ fontSize: '0.65rem' }}>{t}</span>
                                            ))}
                                        </div>
                                    )}

                                    {expandedId === item.id && (
                                        <div className="fade-in" style={{ marginTop: '1rem', borderTop: '1px solid var(--border)', paddingTop: '1rem' }}>
                                            <pre style={{ background: 'var(--bg-primary)', border: '1px solid var(--border)', borderRadius: '0.5rem', padding: '0.75rem', fontSize: '0.75rem', whiteSpace: 'pre-wrap', color: 'var(--text-secondary)', maxHeight: '300px', overflow: 'auto' }}>
                                                {item.prompt_text}
                                            </pre>
                                            <button onClick={(e) => { e.stopPropagation(); navigator.clipboard.writeText(item.prompt_text); }} className="btn-secondary" style={{ marginTop: '0.5rem', fontSize: '0.75rem', padding: '0.35rem 0.75rem' }}>
                                                📋 Copy Prompt
                                            </button>
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
