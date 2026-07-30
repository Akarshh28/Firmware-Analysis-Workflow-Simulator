import React, { useState, useRef, useEffect } from 'react';
import { BellRing, Check, Trash2, X, AlertTriangle, Info, CheckCircle } from 'lucide-react';
import { useNotificationStore, AppNotification } from '../store/notificationStore';
import { PageId } from './Sidebar';

export const NotificationsDropdown: React.FC<{ onNavigate: (page: PageId) => void }> = ({ onNavigate }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  const { notifications, unreadCount, markAsRead, markAllAsRead, clearAll } = useNotificationStore();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getIcon = (type: AppNotification['type']) => {
    switch (type) {
      case 'info': return <Info size={16} color="var(--accent-cyan)" />;
      case 'success': return <CheckCircle size={16} color="var(--accent-green)" />;
      case 'warning': return <AlertTriangle size={16} color="#eab308" />;
      case 'error': return <X size={16} color="var(--accent-red)" />;
    }
  };

  const timeAgo = (timestamp: number) => {
    // eslint-disable-next-line react-hooks/purity
    const seconds = Math.floor((Date.now() - timestamp) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  return (
    <div style={{ position: 'relative' }} ref={dropdownRef}>
      <button
        className="btn btn-secondary btn-icon"
        title="Notifications"
        style={{ padding: 7, position: 'relative' }}
        onClick={() => setIsOpen(!isOpen)}
      >
        <BellRing size={15} />
        {unreadCount() > 0 && (
          <span style={{
            position: 'absolute',
            top: -2,
            right: -2,
            background: 'var(--accent-red)',
            color: '#fff',
            fontSize: 9,
            fontWeight: 800,
            borderRadius: '50%',
            width: 14,
            height: 14,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            {unreadCount()}
          </span>
        )}
      </button>

      {isOpen && (
        <div style={{
          position: 'absolute',
          top: 'calc(100% + 8px)',
          right: 0,
          width: 320,
          background: 'var(--bg-secondary)',
          border: '1px solid var(--bg-tertiary)',
          borderRadius: 8,
          boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
          zIndex: 100,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--bg-tertiary)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontWeight: 600, fontSize: 14 }}>Notifications</span>
            <div style={{ display: 'flex', gap: 8 }}>
              {unreadCount() > 0 && (
                <button onClick={markAllAsRead} style={{ background: 'none', border: 'none', color: 'var(--accent-cyan)', fontSize: 11, cursor: 'pointer' }} title="Mark all as read">
                  <Check size={14} />
                </button>
              )}
              {notifications.length > 0 && (
                <button onClick={clearAll} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: 11, cursor: 'pointer' }} title="Clear all">
                  <Trash2 size={14} />
                </button>
              )}
            </div>
          </div>
          
          <div style={{ maxHeight: 300, overflowY: 'auto' }}>
            {notifications.length === 0 ? (
              <div style={{ padding: 32, textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
                No notifications yet.
              </div>
            ) : (
              notifications.map((n) => (
                <div 
                  key={n.id} 
                  style={{ 
                    padding: '12px 16px', 
                    borderBottom: '1px solid var(--bg-tertiary)',
                    background: n.isRead ? 'transparent' : 'rgba(99,120,255,0.05)',
                    display: 'flex',
                    gap: 12,
                    cursor: n.action ? 'pointer' : 'default',
                    transition: 'background 0.2s ease'
                  }}
                  onClick={() => {
                    if (!n.isRead) markAsRead(n.id);
                    if (n.action) {
                      onNavigate(n.action.pageId);
                      setIsOpen(false);
                    }
                  }}
                  onMouseEnter={(e) => {
                    if (n.action) (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.05)';
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLElement).style.background = n.isRead ? 'transparent' : 'rgba(99,120,255,0.05)';
                  }}
                >
                  <div style={{ marginTop: 2 }}>{getIcon(n.type)}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
                      <span style={{ fontSize: 13, fontWeight: 600, color: n.isRead ? 'var(--text-secondary)' : 'var(--text-primary)' }}>{n.title}</span>
                      <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{timeAgo(n.timestamp)}</span>
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                      {n.message}
                    </div>
                    {n.action && (
                      <div style={{ marginTop: 8, fontSize: 12, color: 'var(--accent-cyan)', fontWeight: 600 }}>
                        {n.action.label} &rarr;
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};
