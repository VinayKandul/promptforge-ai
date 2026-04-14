'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import Sidebar from '@/components/Sidebar';

const PROVIDERS = [
  { key: 'openai', label: 'OpenAI', icon: '🟢', placeholder: 'sk-...' },
  { key: 'claude', label: 'Anthropic (Claude)', icon: '🟠', placeholder: 'sk-ant-...' },
  { key: 'gemini', label: 'Google (Gemini)', icon: '🔵', placeholder: 'AIza...' },
  { key: 'mistral', label: 'Mistral AI', icon: '🟡', placeholder: 'mis-...' },
  { key: 'deepseek', label: 'DeepSeek', icon: '🟣', placeholder: 'sk-...' },
];

interface APIKeyRecord {
  id: string;
  provider: string;
  label: string | null;
  masked_key: string;
  created_at: string;
  updated_at: string;
}

export default function SettingsPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  const [keys, setKeys] = useState<APIKeyRecord[]>([]);
  const [loading, setLoading] = useState(true);

  // Form state
  const [selectedProvider, setSelectedProvider] = useState('openai');
  const [newKey, setNewKey] = useState('');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (!authLoading && !user) router.push('/login');
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user) fetchKeys();
  }, [user]);

  const fetchKeys = async () => {
    try {
      const res = await api.getAPIKeys();
      setKeys(res.items || []);
    } catch { }
    setLoading(false);
  };

  if (authLoading || !user) return null;

  const handleAddKey = async () => {
    if (!newKey.trim()) return;
    setSaving(true);
    setMessage(null);
    try {
      await api.addAPIKey({
        provider: selectedProvider,
        api_key: newKey,
      });
      setNewKey('');
      setMessage({ type: 'success', text: `API key for ${selectedProvider} saved & encrypted successfully!` });
      fetchKeys();
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to save API key' });
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string, provider: string) => {
    if (!confirm(`Remove API key for ${provider}? You can re-add it later.`)) return;
    try {
      await api.deleteAPIKey(id);
      setKeys(keys.filter((k) => k.id !== id));
      setMessage({ type: 'success', text: `API key for ${provider} removed` });
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message });
    }
  };

  const getProviderInfo = (key: string) =>
    PROVIDERS.find((p) => p.key === key) || { key, label: key, icon: '🔑', placeholder: '' };

  const configuredProviders = new Set(keys.map((k) => k.provider));

  return (
    <div>
      <Sidebar />
      <div className="main-content">
        <div className="fade-in">
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '0.5rem' }}>
            ⚙️ <span className="gradient-text">Account Settings</span>
          </h1>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', fontSize: '0.9rem' }}>
            Manage your API keys securely. All keys are encrypted at rest using AES-256.
          </p>

          {message && (
            <div
              style={{
                background: message.type === 'success'
                  ? 'rgba(74, 222, 128, 0.1)'
                  : 'rgba(248, 113, 113, 0.1)',
                border: `1px solid ${message.type === 'success'
                  ? 'rgba(74, 222, 128, 0.3)'
                  : 'rgba(248, 113, 113, 0.3)'}`,
                borderRadius: '0.75rem',
                padding: '0.75rem 1rem',
                marginBottom: '1.5rem',
                color: message.type === 'success' ? 'var(--success)' : 'var(--danger)',
                fontSize: '0.85rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
              }}
            >
              <span>{message.type === 'success' ? '✅' : '❌'}</span>
              {message.text}
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            {/* Add key form */}
            <div className="card">
              <h2 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem' }}>
                🔑 Add API Key
              </h2>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>
                  Provider
                </label>
                <select
                  value={selectedProvider}
                  onChange={(e) => setSelectedProvider(e.target.value)}
                  className="select-dark"
                  style={{ width: '100%' }}
                >
                  {PROVIDERS.map((p) => (
                    <option key={p.key} value={p.key}>
                      {p.icon} {p.label} {configuredProviders.has(p.key) ? '(update)' : ''}
                    </option>
                  ))}
                </select>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>
                  API Key
                </label>
                <input
                  type="password"
                  value={newKey}
                  onChange={(e) => setNewKey(e.target.value)}
                  className="input-dark"
                  placeholder={getProviderInfo(selectedProvider).placeholder}
                  autoComplete="off"
                />
              </div>

              <button
                onClick={handleAddKey}
                className="btn-primary"
                disabled={saving || !newKey.trim()}
                style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
              >
                {saving ? <><span className="spinner" /> Encrypting...</> : '🔐 Save Encrypted Key'}
              </button>

              {/* Security info */}
              <div style={{
                marginTop: '1.5rem',
                padding: '1rem',
                background: 'rgba(139, 92, 246, 0.05)',
                border: '1px solid rgba(139, 92, 246, 0.15)',
                borderRadius: '0.75rem',
              }}>
                <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent)', marginBottom: '0.5rem' }}>
                  🛡️ How we protect your keys
                </h4>
                <ul style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: 1.8, paddingLeft: '1rem' }}>
                  <li>Keys are encrypted using <strong>Fernet (AES-128-CBC)</strong> before storage</li>
                  <li>Keys are <strong>never logged</strong> or exposed in API responses</li>
                  <li>Only <strong>masked versions</strong> are shown in the UI</li>
                  <li>Keys are decrypted only at execution time, in-memory</li>
                  <li>You can delete your keys at any time</li>
                </ul>
              </div>
            </div>

            {/* Configured keys */}
            <div>
              <h2 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem' }}>
                Configured Keys
              </h2>

              {loading ? (
                <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
                  <span className="spinner" style={{ width: '30px', height: '30px' }} />
                </div>
              ) : keys.length === 0 ? (
                <div className="card" style={{ textAlign: 'center', padding: '2.5rem' }}>
                  <p style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>🔑</p>
                  <p style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>No API keys configured</p>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                    Add your AI provider keys to use real model responses
                  </p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {keys.map((k) => {
                    const info = getProviderInfo(k.provider);
                    return (
                      <div key={k.id} className="card" style={{ padding: '1rem 1.25rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <span style={{ fontSize: '1.5rem' }}>{info.icon}</span>
                            <div>
                              <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>{info.label}</div>
                              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'monospace', marginTop: '0.15rem' }}>
                                {k.masked_key}
                              </div>
                            </div>
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                            <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>Active</span>
                            <button
                              onClick={() => handleDelete(k.id, info.label)}
                              className="btn-danger"
                              style={{ padding: '0.35rem 0.5rem', fontSize: '0.75rem' }}
                            >
                              🗑️
                            </button>
                          </div>
                        </div>
                        <div style={{ marginTop: '0.35rem', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                          Updated: {k.updated_at ? new Date(k.updated_at).toLocaleDateString() : 'N/A'}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Provider status overview */}
              <div className="card" style={{ marginTop: '1.5rem' }}>
                <h3 style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--text-secondary)' }}>
                  Provider Status
                </h3>
                {PROVIDERS.map((p) => (
                  <div key={p.key} style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    padding: '0.5rem 0',
                    borderBottom: '1px solid var(--border)',
                  }}>
                    <span style={{ fontSize: '0.85rem' }}>{p.icon} {p.label}</span>
                    <span className={`badge ${configuredProviders.has(p.key) ? 'badge-success' : 'badge-warning'}`} style={{ fontSize: '0.7rem' }}>
                      {configuredProviders.has(p.key) ? '✓ Configured' : 'Not Set'}
                    </span>
                  </div>
                ))}
                <div style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '0.5rem 0',
                }}>
                  <span style={{ fontSize: '0.85rem' }}>⚫ Ollama (Local)</span>
                  <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>
                    ✓ No Key Needed
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
