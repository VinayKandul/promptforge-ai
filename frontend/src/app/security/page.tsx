'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import Sidebar from '@/components/Sidebar';

type Tab = 'adversarial' | 'diff' | 'consistency' | 'threat' | 'cve';

const TABS: { key: Tab; icon: string; label: string }[] = [
  { key: 'adversarial', icon: '🎯', label: 'Adversarial Probes' },
  { key: 'diff', icon: '🔀', label: 'Prompt Diff' },
  { key: 'consistency', icon: '📊', label: 'Consistency' },
  { key: 'threat', icon: '🏷️', label: 'Threat Model' },
  { key: 'cve', icon: '🛡️', label: 'CVE Tracker' },
];

export default function SecurityPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<Tab>('adversarial');
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);

  useEffect(() => {
    if (!authLoading && !user) router.push('/login');
  }, [user, authLoading, router]);

  if (authLoading || !user) return null;

  const runAnalysis = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setResults(null);
    try {
      let data;
      switch (activeTab) {
        case 'adversarial': data = await api.adversarialProbe(prompt); break;
        case 'diff': data = await api.promptDiff(prompt); break;
        case 'consistency': data = await api.consistencyScore(prompt); break;
        case 'threat': data = await api.threatModel(prompt); break;
        case 'cve': data = await api.cveScan(prompt); break;
      }
      setResults(data);
    } catch (err: any) {
      setResults({ error: err.message });
    }
    setLoading(false);
  };

  const riskColor = (level: string) => {
    const l = level?.toUpperCase();
    if (l === 'CRITICAL') return '#ef4444';
    if (l === 'HIGH') return '#f97316';
    if (l === 'MEDIUM') return '#eab308';
    if (l === 'LOW') return '#22c55e';
    return '#6b7280';
  };

  const severityBg = (level: string) => {
    const c = riskColor(level);
    return { background: `${c}20`, color: c, border: `1px solid ${c}40` };
  };

  return (
    <div>
      <Sidebar />
      <div className="main-content">
        <div className="fade-in">
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '0.25rem' }}>
            🔒 <span className="gradient-text">Security Analysis Suite</span>
          </h1>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
            Enterprise-grade prompt security analysis — adversarial testing, hardening, and compliance.
          </p>

          {/* Tab bar */}
          <div style={{ display: 'flex', gap: '0.25rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
            {TABS.map(t => (
              <button
                key={t.key}
                onClick={() => { setActiveTab(t.key); setResults(null); }}
                style={{
                  padding: '0.6rem 1rem',
                  borderRadius: '0.5rem',
                  border: activeTab === t.key ? '1px solid var(--accent)' : '1px solid var(--border)',
                  background: activeTab === t.key ? 'rgba(139, 92, 246, 0.15)' : 'transparent',
                  color: activeTab === t.key ? 'var(--accent)' : 'var(--text-secondary)',
                  fontWeight: activeTab === t.key ? 700 : 500,
                  fontSize: '0.8rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
              >
                {t.icon} {t.label}
              </button>
            ))}
          </div>

          {/* Input area */}
          <div className="card" style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--text-secondary)' }}>
              Paste your prompt for analysis
            </h3>
            <textarea
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              className="textarea-dark"
              rows={5}
              placeholder="e.g., You are a helpful AI assistant. Generate a blog post about cybersecurity best practices for enterprise teams..."
              style={{ width: '100%', marginBottom: '0.75rem' }}
            />
            <button onClick={runAnalysis} className="btn-primary" disabled={loading || !prompt.trim()}>
              {loading ? <><span className="spinner" style={{ width: 16, height: 16 }} /> Analyzing...</> : `🔍 Run ${TABS.find(t => t.key === activeTab)?.label}`}
            </button>
          </div>

          {/* Results */}
          {results?.error && (
            <div className="card" style={{ borderColor: 'rgba(248,113,113,0.3)' }}>
              <p style={{ color: 'var(--danger)' }}>❌ {results.error}</p>
            </div>
          )}

          {results && !results.error && activeTab === 'adversarial' && <AdversarialResults data={results} riskColor={riskColor} severityBg={severityBg} />}
          {results && !results.error && activeTab === 'diff' && <DiffResults data={results} />}
          {results && !results.error && activeTab === 'consistency' && <ConsistencyResults data={results} />}
          {results && !results.error && activeTab === 'threat' && <ThreatResults data={results} riskColor={riskColor} severityBg={severityBg} />}
          {results && !results.error && activeTab === 'cve' && <CVEResults data={results} riskColor={riskColor} severityBg={severityBg} />}
        </div>
      </div>
    </div>
  );
}

/* ================================================================ */
/*  1. ADVERSARIAL PROBE RESULTS                                    */
/* ================================================================ */

function AdversarialResults({ data, riskColor, severityBg }: { data: any; riskColor: (l: string) => string; severityBg: (l: string) => any }) {
  return (
    <div className="fade-in">
      {/* Summary card */}
      <div className="card" style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
        <div style={{ fontSize: '3rem', fontWeight: 900, color: riskColor(data.risk_level) }}>
          {data.probes_broken}/{data.total_probes}
        </div>
        <div style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.25rem' }}>{data.summary}</div>
        <span style={{ ...severityBg(data.risk_level), padding: '0.3rem 0.75rem', borderRadius: '999px', fontSize: '0.75rem', fontWeight: 700 }}>
          {data.risk_level} RISK
        </span>
      </div>

      {/* Recommendations */}
      {data.recommendations?.length > 0 && (
        <div className="card" style={{ marginBottom: '1.5rem', borderLeft: '3px solid var(--accent)' }}>
          <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.5rem' }}>💡 Recommendations</h3>
          {data.recommendations.map((r: string, i: number) => (
            <p key={i} style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>• {r}</p>
          ))}
        </div>
      )}

      {/* Individual probes */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
        {data.results?.map((r: any) => (
          <div key={r.probe_id} className="card" style={{ padding: '1rem', borderLeft: `3px solid ${r.breaks ? '#ef4444' : '#22c55e'}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <span style={{ fontWeight: 700, fontSize: '0.85rem' }}>{r.probe_name}</span>
              <span style={{ ...severityBg(r.severity), padding: '0.2rem 0.5rem', borderRadius: '999px', fontSize: '0.65rem', fontWeight: 700 }}>
                {r.severity.toUpperCase()}
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <span style={{ color: r.breaks ? '#ef4444' : '#22c55e', fontWeight: 700, fontSize: '0.8rem' }}>
                {r.breaks ? '❌ BREAKS' : '✅ DEFENDED'}
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Score: {r.resilience_score}%</span>
            </div>
            {r.vulnerabilities?.length > 0 && (
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                {r.vulnerabilities.map((v: string, i: number) => <div key={i}>• {v}</div>)}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ================================================================ */
/*  2. PROMPT DIFF RESULTS                                          */
/* ================================================================ */

function DiffResults({ data }: { data: any }) {
  const [showRaw, setShowRaw] = useState(false);

  return (
    <div className="fade-in">
      {/* Score improvement */}
      <div className="card" style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Security Score</p>
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '1.5rem' }}>
          <div>
            <div style={{ fontSize: '2rem', fontWeight: 900, color: '#ef4444' }}>{data.original_score}%</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Original</div>
          </div>
          <div style={{ fontSize: '1.5rem', color: 'var(--accent)' }}>→</div>
          <div>
            <div style={{ fontSize: '2rem', fontWeight: 900, color: '#22c55e' }}>{data.hardened_score}%</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Hardened</div>
          </div>
        </div>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>{data.summary}</p>
      </div>

      {/* Changes list */}
      <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem' }}>What We Changed & Why</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.5rem' }}>
        {data.changes?.map((c: any, i: number) => (
          <div key={i} className="card" style={{ padding: '1rem', borderLeft: '3px solid var(--accent)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontWeight: 700, fontSize: '0.85rem', color: '#ef4444' }}>⚠ {c.weakness}</span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{c.type}</span>
            </div>
            <p style={{ fontSize: '0.8rem', color: '#f97316', marginBottom: '0.35rem' }}>Risk: {c.risk}</p>
            <p style={{ fontSize: '0.8rem', color: '#22c55e', marginBottom: '0.5rem' }}>✅ {c.explanation}</p>
            <pre style={{ fontSize: '0.7rem', background: 'rgba(139,92,246,0.08)', padding: '0.5rem', borderRadius: '0.5rem', whiteSpace: 'pre-wrap', color: 'var(--text-primary)' }}>
              {c.change}
            </pre>
          </div>
        ))}
      </div>

      {/* Side-by-side prompts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
        <div>
          <h4 style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: '0.5rem', color: '#ef4444' }}>❌ Original Prompt</h4>
          <pre className="card" style={{ fontSize: '0.75rem', whiteSpace: 'pre-wrap', padding: '1rem', maxHeight: '300px', overflow: 'auto' }}>{data.original_prompt}</pre>
        </div>
        <div>
          <h4 style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: '0.5rem', color: '#22c55e' }}>✅ Hardened Prompt</h4>
          <pre className="card" style={{ fontSize: '0.75rem', whiteSpace: 'pre-wrap', padding: '1rem', maxHeight: '300px', overflow: 'auto' }}>{data.hardened_prompt}</pre>
        </div>
      </div>

      {/* Raw diff toggle */}
      <button onClick={() => setShowRaw(!showRaw)} className="btn-secondary" style={{ fontSize: '0.75rem', marginBottom: '0.75rem' }}>
        {showRaw ? 'Hide' : 'Show'} Unified Diff
      </button>
      {showRaw && (
        <pre className="card" style={{ fontSize: '0.7rem', whiteSpace: 'pre-wrap', padding: '1rem', fontFamily: 'monospace' }}>{data.diff}</pre>
      )}
    </div>
  );
}

/* ================================================================ */
/*  3. CONSISTENCY RESULTS                                          */
/* ================================================================ */

function ConsistencyResults({ data }: { data: any }) {
  const scoreColor = data.consistency_score >= 70 ? '#22c55e' : data.consistency_score >= 50 ? '#eab308' : '#ef4444';

  return (
    <div className="fade-in">
      {/* Score ring */}
      <div className="card" style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
        <div style={{ position: 'relative', width: '120px', height: '120px', margin: '0 auto 1rem' }}>
          <svg viewBox="0 0 120 120" style={{ transform: 'rotate(-90deg)' }}>
            <circle cx="60" cy="60" r="52" fill="none" stroke="var(--border)" strokeWidth="8" />
            <circle cx="60" cy="60" r="52" fill="none" stroke={scoreColor} strokeWidth="8"
              strokeDasharray={`${(data.consistency_score / 100) * 327} 327`}
              strokeLinecap="round" />
          </svg>
          <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', fontWeight: 900, fontSize: '1.75rem', color: scoreColor }}>
            {data.consistency_score}%
          </div>
        </div>
        <div style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.25rem' }}>{data.verdict}</div>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', maxWidth: '500px', margin: '0 auto' }}>{data.verdict_detail}</p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', marginTop: '1rem' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Simulated Variance</div>
            <div style={{ fontWeight: 700 }}>{data.simulated_variance}</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Production Ready</div>
            <div style={{ fontWeight: 700, color: data.production_ready ? '#22c55e' : '#ef4444' }}>{data.production_ready ? '✅ Yes' : '❌ No'}</div>
          </div>
        </div>
      </div>

      {/* Factors */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        <div>
          <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.75rem' }}>✅ Consistency Boosters Present</h3>
          {data.factors_present?.filter((f: any) => f.type === 'booster').length === 0 ? (
            <div className="card" style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-muted)' }}>None detected</div>
          ) : data.factors_present?.filter((f: any) => f.type === 'booster').map((f: any, i: number) => (
            <div key={i} className="card" style={{ padding: '0.75rem', marginBottom: '0.5rem', borderLeft: '3px solid #22c55e' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontWeight: 700, fontSize: '0.8rem' }}>{f.name.replace(/_/g, ' ')}</span>
                <span style={{ color: '#22c55e', fontSize: '0.75rem', fontWeight: 700 }}>{f.impact}</span>
              </div>
              <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{f.description}</p>
            </div>
          ))}

          {data.factors_present?.filter((f: any) => f.type === 'reducer').length > 0 && (
            <>
              <h3 style={{ fontSize: '0.9rem', fontWeight: 700, margin: '1rem 0 0.75rem', color: '#ef4444' }}>⚠️ Variance Increasers</h3>
              {data.factors_present?.filter((f: any) => f.type === 'reducer').map((f: any, i: number) => (
                <div key={i} className="card" style={{ padding: '0.75rem', marginBottom: '0.5rem', borderLeft: '3px solid #ef4444' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontWeight: 700, fontSize: '0.8rem' }}>{f.name.replace(/_/g, ' ')}</span>
                    <span style={{ color: '#ef4444', fontSize: '0.75rem', fontWeight: 700 }}>{f.impact}</span>
                  </div>
                  <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{f.description}</p>
                </div>
              ))}
            </>
          )}
        </div>
        <div>
          <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.75rem' }}>💡 Suggestions</h3>
          {data.suggestions?.map((s: string, i: number) => (
            <div key={i} className="card" style={{ padding: '0.75rem', marginBottom: '0.5rem', borderLeft: '3px solid var(--accent)' }}>
              <p style={{ fontSize: '0.8rem' }}>{s}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ================================================================ */
/*  4. THREAT MODEL RESULTS                                         */
/* ================================================================ */

function ThreatResults({ data, riskColor, severityBg }: { data: any; riskColor: (l: string) => string; severityBg: (l: string) => any }) {
  return (
    <div className="fade-in">
      {/* Overall risk */}
      <div className="card" style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
        <div style={{ fontSize: '1.5rem', fontWeight: 900, color: riskColor(data.overall_risk?.includes('HIGH') ? 'HIGH' : 'LOW'), marginBottom: '0.25rem' }}>
          {data.overall_risk}
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto' }}>{data.overall_detail}</p>
        <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
          Standard: {data.compliance_artifact?.standard} | Categories Assessed: {data.compliance_artifact?.assessed_categories}
        </p>
      </div>

      {/* Tags */}
      <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem' }}>OWASP LLM Top 10 Risk Tags</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {data.tags?.map((t: any) => (
          <div key={t.code} className="card" style={{ padding: '1rem', borderLeft: `3px solid ${riskColor(t.risk_level)}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
              <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>
                {t.code}: {t.name}
              </span>
              <span style={{ ...severityBg(t.risk_level), padding: '0.2rem 0.6rem', borderRadius: '999px', fontSize: '0.7rem', fontWeight: 700 }}>
                {t.risk_level}
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>{t.description}</p>
            {t.signals?.length > 0 && (
              <div style={{ fontSize: '0.7rem' }}>
                {t.signals.map((s: any, i: number) => (
                  <div key={i} style={{ color: s.impact === 'defensive' ? '#22c55e' : '#f97316', marginBottom: '0.15rem' }}>
                    {s.impact === 'defensive' ? '🛡️' : '⚠️'} {s.signal}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ================================================================ */
/*  5. CVE TRACKER RESULTS                                          */
/* ================================================================ */

function CVEResults({ data, riskColor, severityBg }: { data: any; riskColor: (l: string) => string; severityBg: (l: string) => any }) {
  return (
    <div className="fade-in">
      {/* Summary */}
      <div className="card" style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
        <div style={{ fontSize: '1.75rem', fontWeight: 900, color: riskColor(data.scan_result), marginBottom: '0.25rem' }}>
          {data.scan_result}
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto' }}>{data.summary}</p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', marginTop: '0.75rem' }}>
          {Object.entries(data.severity_breakdown || {}).map(([sev, count]) => (
            <div key={sev} style={{ textAlign: 'center' }}>
              <div style={{ fontWeight: 800, fontSize: '1.1rem', color: riskColor(sev) }}>{count as number}</div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>{sev}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Matched CVEs */}
      {data.matches?.length > 0 && (
        <>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem', color: '#ef4444' }}>🚨 Matched Attack Patterns</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.5rem' }}>
            {data.matches.map((m: any) => (
              <div key={m.cve_id} className="card" style={{ padding: '1rem', borderLeft: `3px solid ${riskColor(m.severity)}` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <div>
                    <span style={{ fontWeight: 800, fontSize: '0.85rem', fontFamily: 'monospace', color: riskColor(m.severity) }}>
                      {m.cve_id}
                    </span>
                    <span style={{ fontWeight: 700, fontSize: '0.85rem', marginLeft: '0.5rem' }}>{m.name}</span>
                  </div>
                  <span style={{ ...severityBg(m.severity), padding: '0.2rem 0.5rem', borderRadius: '999px', fontSize: '0.65rem', fontWeight: 700 }}>
                    {m.severity.toUpperCase()}
                  </span>
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>{m.description}</p>
                <div style={{ fontSize: '0.7rem', marginBottom: '0.35rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Matched: </span>
                  {m.matched_patterns.map((p: string, i: number) => (
                    <span key={i} style={{ background: 'rgba(239,68,68,0.1)', color: '#ef4444', padding: '0.1rem 0.4rem', borderRadius: '4px', marginRight: '0.25rem', fontSize: '0.7rem', fontFamily: 'monospace' }}>
                      {p}
                    </span>
                  ))}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#22c55e', marginTop: '0.35rem' }}>
                  💡 <strong>Mitigation:</strong> {m.mitigation}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Susceptibilities */}
      {data.susceptibilities?.length > 0 && (
        <>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem', color: '#f97316' }}>⚠️ Structural Susceptibilities</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            {data.susceptibilities.map((s: any, i: number) => (
              <div key={i} className="card" style={{ padding: '1rem', borderLeft: '3px solid #f97316' }}>
                <div style={{ fontWeight: 700, fontSize: '0.85rem', marginBottom: '0.35rem' }}>⚠ {s.weakness}</div>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>{s.risk}</p>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                  Vulnerable to: {s.vulnerable_to?.join(', ')}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
