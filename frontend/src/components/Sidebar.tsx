'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth';

const NAV_ITEMS = [
    { href: '/dashboard', icon: '⚡', label: 'Forge Prompt' },
    { href: '/debugger', icon: '🔧', label: 'Debugger' },
    { href: '/history', icon: '📜', label: 'History' },
    { href: '/library', icon: '📚', label: 'Library' },
    { href: '/workflows', icon: '🔄', label: 'Workflows' },
    { href: '/settings', icon: '⚙️', label: 'Settings' },
];

export default function Sidebar() {
    const pathname = usePathname();
    const { user, logout } = useAuth();

    return (
        <div className="sidebar">
            <div style={{ padding: '0 1.5rem', marginBottom: '2rem' }}>
                <Link href="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ fontSize: '1.25rem' }}>⚡</span>
                    <span className="gradient-text" style={{ fontWeight: 800, fontSize: '1.1rem' }}>
                        PromptForge AI
                    </span>
                </Link>
            </div>

            <nav style={{ flex: 1 }}>
                {NAV_ITEMS.map((item) => (
                    <Link
                        key={item.href}
                        href={item.href}
                        className={`sidebar-link ${pathname === item.href ? 'active' : ''}`}
                    >
                        <span>{item.icon}</span>
                        <span>{item.label}</span>
                    </Link>
                ))}
            </nav>

            <div style={{ padding: '1rem 1.5rem', borderTop: '1px solid var(--border)' }}>
                {user && (
                    <div style={{ marginBottom: '0.75rem' }}>
                        <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{user.username}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{user.email}</div>
                    </div>
                )}
                <button onClick={logout} className="btn-secondary" style={{ width: '100%', fontSize: '0.8rem', padding: '0.5rem' }}>
                    Logout
                </button>
            </div>
        </div>
    );
}
