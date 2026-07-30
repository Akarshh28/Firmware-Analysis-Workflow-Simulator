import React, { useState, useRef, useEffect } from 'react';
import { User, Shield, LogOut, BookOpen } from 'lucide-react';
import { useProjectStore } from '../store/projectStore';
import { useNotificationStore } from '../store/notificationStore';

export const UserProfileDropdown: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { clearActiveProject } = useProjectStore();
  const { addNotification } = useNotificationStore();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    setIsOpen(false);
    clearActiveProject();
    addNotification({
      title: "Logged Out",
      message: "You have been successfully logged out of the session.",
      type: "info"
    });
  };

  return (
    <div style={{ position: 'relative' }} ref={dropdownRef}>
      <div
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: 30,
          height: 30,
          borderRadius: "50%",
          background: "var(--bg-tertiary)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 11,
          fontWeight: 800,
          color: "var(--text-primary)",
          cursor: "pointer",
          border: isOpen ? '1px solid var(--accent-cyan)' : '1px solid var(--border-dim)',
          transition: 'border 0.2s ease',
        }}
        title="Akarsh Pandey"
      >
        A
      </div>

      {isOpen && (
        <div style={{
          position: 'absolute',
          top: 'calc(100% + 12px)',
          right: 0,
          width: 240,
          background: 'var(--bg-secondary)',
          border: '1px solid var(--bg-tertiary)',
          borderRadius: 8,
          boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
          zIndex: 100,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}>
          {/* User Info */}
          <div style={{ padding: '16px', borderBottom: '1px solid var(--bg-tertiary)', display: 'flex', gap: 12, alignItems: 'center' }}>
            <div style={{
              width: 40, height: 40, borderRadius: "50%", background: "var(--bg-tertiary)",
              border: "1px solid var(--border-dim)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 16, fontWeight: 800, color: "var(--text-primary)"
            }}>
              A
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--text-primary)' }}>Akarsh Pandey</div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>akarshpandey2815@gmail.com</div>
              <div style={{
                marginTop: 4, display: 'inline-flex', alignItems: 'center', gap: 4,
                background: 'rgba(99,120,255,0.1)', color: 'var(--accent-cyan)',
                padding: '2px 6px', borderRadius: 4, fontSize: 10, fontWeight: 700
              }}>
                <Shield size={10} /> System Admin
              </div>
            </div>
          </div>

          {/* Menu Items */}
          <div style={{ padding: 8 }}>
            <button
              className="dropdown-item"
              style={{
                width: '100%', padding: '10px 12px', background: 'none', border: 'none',
                display: 'flex', alignItems: 'center', gap: 10, color: 'var(--text-secondary)',
                cursor: 'pointer', borderRadius: 6, fontSize: 13, fontWeight: 500,
                textAlign: 'left', transition: 'background 0.2s ease'
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-tertiary)')}
              onMouseLeave={(e) => (e.currentTarget.style.background = 'none')}
              onClick={() => setIsOpen(false)}
            >
              <User size={15} /> My Account
            </button>
            <button
              className="dropdown-item"
              style={{
                width: '100%', padding: '10px 12px', background: 'none', border: 'none',
                display: 'flex', alignItems: 'center', gap: 10, color: 'var(--text-secondary)',
                cursor: 'pointer', borderRadius: 6, fontSize: 13, fontWeight: 500,
                textAlign: 'left', transition: 'background 0.2s ease'
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-tertiary)')}
              onMouseLeave={(e) => (e.currentTarget.style.background = 'none')}
              onClick={() => setIsOpen(false)}
            >
              <BookOpen size={15} /> Documentation
            </button>

            <div style={{ height: 1, background: 'var(--bg-tertiary)', margin: '8px 0' }} />

            <button
              className="dropdown-item"
              style={{
                width: '100%', padding: '10px 12px', background: 'none', border: 'none',
                display: 'flex', alignItems: 'center', gap: 10, color: 'var(--accent-red)',
                cursor: 'pointer', borderRadius: 6, fontSize: 13, fontWeight: 500,
                textAlign: 'left', transition: 'background 0.2s ease'
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(239,68,68,0.1)')}
              onMouseLeave={(e) => (e.currentTarget.style.background = 'none')}
              onClick={handleLogout}
            >
              <LogOut size={15} /> Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
