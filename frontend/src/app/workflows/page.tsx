'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import Sidebar from '@/components/Sidebar';

const PROVIDERS = [
    { key: 'openai', label: 'OpenAI', icon: '🟢' },
    { key: 'claude', label: 'Claude', icon: '🟠' },
    { key: 'gemini', label: 'Gemini', icon: '🔵' },
    { key: 'mistral', label: 'Mistral', icon: '🟡' },
    { key: 'deepseek', label: 'DeepSeek', icon: '🟣' },
    { key: 'ollama', label: 'Ollama', icon: '⚫' },
];

const TEMPLATE_WORKFLOWS = [
    {
        name: 'Blog Post Pipeline',
        description: 'Research → Outline → Write → Polish',
        steps: [
            { name: 'Research', instruction: 'Research the topic thoroughly and provide key facts, statistics, and insights', use_previous_output: false },
            { name: 'Outline', instruction: 'Create a detailed blog post outline based on the research above', use_previous_output: true },
            { name: 'Write Draft', instruction: 'Write the full blog post following the outline. Make it engaging and informative', use_previous_output: true },
            { name: 'Polish', instruction: 'Polish and improve the blog post. Fix any issues, improve transitions, and add a compelling conclusion', use_previous_output: true },
        ],
    },
    {
        name: 'Code Development',
        description: 'Design → Implement → Review → Test',
        steps: [
            { name: 'Design', instruction: 'Design the architecture and approach for the implementation', use_previous_output: false },
            { name: 'Implement', instruction: 'Write the complete implementation based on the design', use_previous_output: true },
            { name: 'Review', instruction: 'Review the code for bugs, edge cases, and best practices violations', use_previous_output: true },
            { name: 'Test', instruction: 'Write comprehensive unit tests for the implementation', use_previous_output: true },
        ],
    },
];

export default function WorkflowsPage() {
    const { user, loading: authLoading } = useAuth();
    const router = useRouter();
    const [workflows, setWorkflows] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreate, setShowCreate] = useState(false);
    const [newName, setNewName] = useState('');
    const [newDesc, setNewDesc] = useState('');
    const [newSteps, setNewSteps] = useState([{ name: '', instruction: '', use_previous_output: true }]);
    const [runningId, setRunningId] = useState<string | null>(null);
    const [runResult, setRunResult] = useState<any>(null);
    const [provider, setProvider] = useState('openai');

    useEffect(() => {
        if (!authLoading && !user) router.push('/login');
    }, [user, authLoading, router]);

    useEffect(() => {
        if (user) fetchWorkflows();
    }, [user]);

    const fetchWorkflows = async () => {
        try {
            const res = await api.getWorkflows();
            setWorkflows(res.items || []);
        } catch { }
        setLoading(false);
    };

    if (authLoading || !user) return null;

    const addStep = () => setNewSteps([...newSteps, { name: '', instruction: '', use_previous_output: true }]);
    const removeStep = (i: number) => setNewSteps(newSteps.filter((_, idx) => idx !== i));
    const updateStep = (i: number, field: string, value: any) => {
        const updated = [...newSteps];
        (updated[i] as any)[field] = value;
        setNewSteps(updated);
    };

    const handleCreate = async () => {
        if (!newName.trim() || newSteps.some((s) => !s.name.trim() || !s.instruction.trim())) return;
        try {
            await api.createWorkflow({ name: newName, description: newDesc, steps: newSteps });
            setShowCreate(false);
            setNewName('');
            setNewDesc('');
            setNewSteps([{ name: '', instruction: '', use_previous_output: true }]);
            fetchWorkflows();
        } catch (err: any) {
            alert('Failed: ' + err.message);
        }
    };

    const handleUseTemplate = async (template: any) => {
        try {
            await api.createWorkflow(template);
            fetchWorkflows();
        } catch (err: any) {
            alert('Failed: ' + err.message);
        }
    };

    const handleRun = async (id: string) => {
        setRunningId(id);
        setRunResult(null);
        try {
            const res = await api.runWorkflow({ workflow_id: id, provider });
            setRunResult(res);
        } catch (err: any) {
            alert('Failed: ' + err.message);
        } finally {
            setRunningId(null);
        }
    };

    const handleDelete = async (id: string) => {
        try {
            await api.deleteWorkflow(id);
            setWorkflows(workflows.filter((w) => w.id !== id));
        } catch (err: any) {
            alert('Failed: ' + err.message);
        }
    };

    return (
        <div>
            <Sidebar />
            <div className="main-content">
                <div className="fade-in">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                        <div>
                            <h1 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '0.5rem' }}>
                                🔄 <span className="gradient-text">Workflow Engine</span>
                            </h1>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                Chain multiple prompts together for complex tasks
                            </p>
                        </div>
                        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                            <select value={provider} onChange={(e) => setProvider(e.target.value)} className="select-dark">
                                {PROVIDERS.map((p) => (
                                    <option key={p.key} value={p.key}>{p.icon} {p.label}</option>
                                ))}
                            </select>
                            <button onClick={() => setShowCreate(!showCreate)} className="btn-primary">
                                + New Workflow
                            </button>
                        </div>
                    </div>

                    {/* Templates */}
                    <div style={{ marginBottom: '2rem' }}>
                        <h3 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            Quick Templates
                        </h3>
                        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                            {TEMPLATE_WORKFLOWS.map((t, i) => (
                                <div key={i} className="card glass-hover" style={{ cursor: 'pointer', flex: '1 1 300px', maxWidth: '400px' }} onClick={() => handleUseTemplate(t)}>
                                    <h4 style={{ fontWeight: 700 }}>{t.name}</h4>
                                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>{t.description}</p>
                                    <div style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
                                        {t.steps.map((s, j) => (
                                            <span key={j} className="badge badge-accent" style={{ fontSize: '0.7rem' }}>{s.name}</span>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Create form */}
                    {showCreate && (
                        <div className="card fade-in" style={{ marginBottom: '2rem' }}>
                            <h3 style={{ fontWeight: 700, marginBottom: '1rem' }}>Create Workflow</h3>
                            <input value={newName} onChange={(e) => setNewName(e.target.value)} className="input-dark" placeholder="Workflow name" style={{ marginBottom: '0.75rem' }} />
                            <input value={newDesc} onChange={(e) => setNewDesc(e.target.value)} className="input-dark" placeholder="Description (optional)" style={{ marginBottom: '1rem' }} />

                            {newSteps.map((step, i) => (
                                <div key={i} style={{ background: 'var(--bg-secondary)', borderRadius: '0.75rem', padding: '1rem', marginBottom: '0.75rem', border: '1px solid var(--border)' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                                        <span style={{ fontWeight: 600, fontSize: '0.8rem', color: 'var(--accent)' }}>Step {i + 1}</span>
                                        {newSteps.length > 1 && (
                                            <button onClick={() => removeStep(i)} className="btn-danger" style={{ fontSize: '0.7rem' }}>Remove</button>
                                        )}
                                    </div>
                                    <input value={step.name} onChange={(e) => updateStep(i, 'name', e.target.value)} className="input-dark" placeholder="Step name" style={{ marginBottom: '0.5rem' }} />
                                    <textarea value={step.instruction} onChange={(e) => updateStep(i, 'instruction', e.target.value)} className="textarea-dark" placeholder="What should this step do?" style={{ minHeight: '60px' }} />
                                    {i > 0 && (
                                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                                            <input type="checkbox" checked={step.use_previous_output} onChange={(e) => updateStep(i, 'use_previous_output', e.target.checked)} />
                                            Use previous step&apos;s output
                                        </label>
                                    )}
                                </div>
                            ))}

                            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
                                <button onClick={addStep} className="btn-secondary">+ Add Step</button>
                                <button onClick={handleCreate} className="btn-primary">Create Workflow</button>
                            </div>
                        </div>
                    )}

                    {/* Existing workflows */}
                    {loading ? (
                        <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
                            <span className="spinner" style={{ width: '30px', height: '30px' }} />
                        </div>
                    ) : workflows.length === 0 ? (
                        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
                            <p style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🔄</p>
                            <p style={{ color: 'var(--text-secondary)' }}>No workflows yet. Create one or use a template!</p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {workflows.map((wf) => (
                                <div key={wf.id} className="card">
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <div>
                                            <h3 style={{ fontWeight: 700, fontSize: '1rem' }}>{wf.name}</h3>
                                            {wf.description && <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>{wf.description}</p>}
                                            <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
                                                {wf.steps?.map((s: any, i: number) => (
                                                    <span key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                                        <span className="badge badge-accent" style={{ fontSize: '0.7rem' }}>{s.name}</span>
                                                        {i < wf.steps.length - 1 && <span style={{ color: 'var(--accent)', fontSize: '0.8rem' }}>→</span>}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                                            <button onClick={() => handleRun(wf.id)} className="btn-primary" style={{ fontSize: '0.8rem', padding: '0.5rem 1rem' }} disabled={runningId === wf.id}>
                                                {runningId === wf.id ? <><span className="spinner" /> Running...</> : '▶ Run'}
                                            </button>
                                            <button onClick={() => handleDelete(wf.id)} className="btn-danger">🗑️</button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Run results */}
                    {runResult && (
                        <div className="card fade-in" style={{ marginTop: '2rem' }}>
                            <h3 style={{ fontWeight: 700, marginBottom: '1rem' }}>
                                Workflow Results
                                <span className={`badge ${runResult.success ? 'badge-success' : 'badge-danger'}`} style={{ marginLeft: '0.5rem' }}>
                                    {runResult.steps_completed}/{runResult.total_steps} steps completed
                                </span>
                            </h3>
                            {runResult.results?.map((step: any, i: number) => (
                                <div key={i} style={{ background: 'var(--bg-secondary)', borderRadius: '0.75rem', padding: '1rem', marginBottom: '0.75rem', border: '1px solid var(--border)' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                                        <span className={`badge ${step.success ? 'badge-success' : 'badge-danger'}`}>Step {step.step_number}</span>
                                        <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{step.step_name}</span>
                                    </div>
                                    <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.8rem', color: 'var(--text-secondary)', maxHeight: '200px', overflow: 'auto', lineHeight: 1.6 }}>
                                        {step.response || step.error || 'No output'}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
