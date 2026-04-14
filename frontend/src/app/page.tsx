'use client';

import Link from 'next/link';
import { useAuth } from '@/lib/auth';

export default function HomePage() {
  const { user } = useAuth();

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Nav */}
      <nav style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: '1.25rem 3rem', borderBottom: '1px solid var(--border)',
        background: 'rgba(10, 10, 15, 0.8)', backdropFilter: 'blur(20px)',
        position: 'sticky', top: 0, zIndex: 50,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '1.5rem' }}>⚡</span>
          <span style={{ fontWeight: 800, fontSize: '1.25rem' }} className="gradient-text">
            PromptForge AI
          </span>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          {user ? (
            <Link href="/dashboard" className="btn-primary" style={{ textDecoration: 'none' }}>
              Dashboard →
            </Link>
          ) : (
            <>
              <Link href="/login" className="btn-secondary" style={{ textDecoration: 'none' }}>
                Log In
              </Link>
              <Link href="/signup" className="btn-primary" style={{ textDecoration: 'none' }}>
                Get Started Free
              </Link>
            </>
          )}
        </div>
      </nav>

      {/* Hero */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem 2rem', textAlign: 'center' }}>
        <div className="fade-in" style={{ maxWidth: '800px' }}>
          <div className="badge badge-accent" style={{ marginBottom: '1.5rem', fontSize: '0.8rem' }}>
            ✨ AI-Powered Prompt Engineering
          </div>
          <h1 style={{ fontSize: '3.5rem', fontWeight: 800, lineHeight: 1.1, marginBottom: '1.5rem' }}>
            Transform Simple Requests into{' '}
            <span className="gradient-text">Powerful AI Prompts</span>
          </h1>
          <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: '2.5rem', maxWidth: '600px', margin: '0 auto 2.5rem' }}>
            Just describe what you need in plain language. PromptForge automatically engineers
            optimized prompts that get better results from any AI model.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link href={user ? '/dashboard' : '/signup'} className="btn-primary" style={{ textDecoration: 'none', padding: '1rem 2.5rem', fontSize: '1.1rem' }}>
              ⚡ Start Forging Prompts
            </Link>
            <Link href="#features" className="btn-secondary" style={{ textDecoration: 'none', padding: '1rem 2.5rem', fontSize: '1.1rem' }}>
              See How It Works
            </Link>
          </div>
        </div>

        {/* Pipeline visualization */}
        <div className="fade-in" style={{ marginTop: '4rem', maxWidth: '900px', width: '100%' }}>
          <div className="card glow-accent" style={{ padding: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', flexWrap: 'wrap', fontSize: '0.85rem' }}>
              {['📝 Your Request', '🔍 Intent Analysis', '🧱 Context Building', '🏗️ Prompt Architect', '✨ Optimization', '🤖 AI Model', '📊 Response'].map((step, i) => (
                <span key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span className="badge badge-accent">{step}</span>
                  {i < 6 && <span style={{ color: 'var(--accent)' }}>→</span>}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Features */}
        <div id="features" style={{ marginTop: '5rem', maxWidth: '1100px', width: '100%' }}>
          <h2 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '3rem', textAlign: 'center' }}>
            Everything You Need for <span className="gradient-text">Perfect Prompts</span>
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
            {[
              { icon: '🧠', title: 'Intent Analyzer', desc: 'Automatically classifies your request into coding, content, research, marketing, education, or analysis.' },
              { icon: '🏗️', title: 'Prompt Architect', desc: 'Structures prompts with Role, Context, Task, Constraints, and Output Format for maximum quality.' },
              { icon: '🔒', title: 'Security Scanner', desc: 'Detects prompt injection, API keys, credentials, and PII before sending to AI models.' },
              { icon: '🔧', title: 'Prompt Debugger', desc: 'Paste any prompt to get a quality score, missing component analysis, and improvement suggestions.' },
              { icon: '🤖', title: '6 AI Models', desc: 'OpenAI, Claude, Gemini, Mistral, DeepSeek, and local Ollama models. One click switch.' },
              { icon: '🔄', title: 'Workflow Engine', desc: 'Chain multiple prompts together for complex tasks like research → outline → content → polish.' },
            ].map((f, i) => (
              <div key={i} className="card glass-hover" style={{ cursor: 'default' }}>
                <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>{f.icon}</div>
                <h3 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>{f.title}</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6 }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid var(--border)', padding: '2rem 3rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
        © 2026 PromptForge AI — Intelligent Prompt Engineering Platform
      </footer>
    </div>
  );
}
