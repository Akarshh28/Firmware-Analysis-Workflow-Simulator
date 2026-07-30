import React, { useState } from 'react';
import { X, Save, Key, Sliders, Shield, Check } from 'lucide-react';
import { useSettingsStore } from '../store/settingsStore';

export const SettingsModal: React.FC<{ onClose: () => void }> = ({ onClose }) => {
  const { apiKeys, ui, updateApiKey, updateUI } = useSettingsStore();
  const [activeTab, setActiveTab] = useState<'integrations' | 'preferences'>('integrations');
  
  // Local state for edits
  const [localKeys, setLocalKeys] = useState(apiKeys);
  const [localUI, setLocalUI] = useState(ui);
  
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    updateApiKey('virusTotal', localKeys.virusTotal);
    updateApiKey('openAI', localKeys.openAI);
    updateApiKey('ghidraUrl', localKeys.ghidraUrl);
    updateUI('theme', localUI.theme);
    updateUI('compactMode', localUI.compactMode);
    
    setSaved(true);
    setTimeout(() => {
      setSaved(false);
      onClose();
    }, 1000);
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0,0,0,0.6)',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    }}>
      <div style={{
        background: 'var(--bg-primary)',
        width: 500,
        borderRadius: 12,
        border: '1px solid var(--bg-tertiary)',
        boxShadow: '0 25px 50px -12px rgba(0,0,0,0.5)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* Header */}
        <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--bg-tertiary)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ fontSize: 18, fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Sliders size={20} color="var(--accent-cyan)" /> System Settings
          </h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', borderBottom: '1px solid var(--bg-tertiary)', padding: '0 24px' }}>
          <button
            onClick={() => setActiveTab('integrations')}
            style={{
              padding: '12px 16px',
              background: 'none',
              border: 'none',
              borderBottom: activeTab === 'integrations' ? '2px solid var(--accent-cyan)' : '2px solid transparent',
              color: activeTab === 'integrations' ? 'var(--accent-cyan)' : 'var(--text-secondary)',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 8
            }}
          >
            <Key size={16} /> Integrations & API Keys
          </button>
          <button
            onClick={() => setActiveTab('preferences')}
            style={{
              padding: '12px 16px',
              background: 'none',
              border: 'none',
              borderBottom: activeTab === 'preferences' ? '2px solid var(--accent-cyan)' : '2px solid transparent',
              color: activeTab === 'preferences' ? 'var(--accent-cyan)' : 'var(--text-secondary)',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 8
            }}
          >
            <Shield size={16} /> Preferences
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: 24, flex: 1, minHeight: 250 }}>
          {activeTab === 'integrations' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                  VirusTotal API Key
                </label>
                <input
                  type="password"
                  value={localKeys.virusTotal}
                  onChange={(e) => setLocalKeys({...localKeys, virusTotal: e.target.value})}
                  placeholder="Enter VT API Key..."
                  style={{ width: '100%', padding: '10px 14px', borderRadius: 6, background: 'var(--bg-secondary)', border: '1px solid var(--bg-tertiary)', color: 'var(--text-primary)', outline: 'none' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                  OpenAI API Key (for LLM analysis)
                </label>
                <input
                  type="password"
                  value={localKeys.openAI}
                  onChange={(e) => setLocalKeys({...localKeys, openAI: e.target.value})}
                  placeholder="sk-..."
                  style={{ width: '100%', padding: '10px 14px', borderRadius: 6, background: 'var(--bg-secondary)', border: '1px solid var(--bg-tertiary)', color: 'var(--text-primary)', outline: 'none' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>
                  Ghidra Server URL
                </label>
                <input
                  type="text"
                  value={localKeys.ghidraUrl}
                  onChange={(e) => setLocalKeys({...localKeys, ghidraUrl: e.target.value})}
                  placeholder="http://localhost:1337"
                  style={{ width: '100%', padding: '10px 14px', borderRadius: 6, background: 'var(--bg-secondary)', border: '1px solid var(--bg-tertiary)', color: 'var(--text-primary)', outline: 'none' }}
                />
              </div>
            </div>
          )}

          {activeTab === 'preferences' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Compact Mode</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Reduce padding and condense data tables</div>
                </div>
                <div 
                  onClick={() => setLocalUI({...localUI, compactMode: !localUI.compactMode})}
                  style={{
                    width: 44, height: 24, borderRadius: 12,
                    background: localUI.compactMode ? 'var(--accent-cyan)' : 'var(--bg-tertiary)',
                    position: 'relative', cursor: 'pointer', transition: '0.3s'
                  }}
                >
                  <div style={{
                    width: 20, height: 20, borderRadius: '50%', background: '#fff',
                    position: 'absolute', top: 2, left: localUI.compactMode ? 22 : 2,
                    transition: '0.3s'
                  }}/>
                </div>
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Theme Mode</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>System theme overrides coming soon.</div>
                </div>
                <select
                  value={localUI.theme}
                  onChange={(e) => setLocalUI({...localUI, theme: e.target.value as 'dark'|'light'})}
                  style={{ background: 'var(--bg-secondary)', border: '1px solid var(--bg-tertiary)', color: 'var(--text-primary)', padding: '6px 12px', borderRadius: 6, outline: 'none' }}
                >
                  <option value="dark">Dark</option>
                  <option value="light">Light</option>
                </select>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{ padding: '16px 24px', borderTop: '1px solid var(--bg-tertiary)', background: 'var(--bg-secondary)', display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
          <button 
            className="btn btn-secondary" 
            onClick={onClose}
          >
            Cancel
          </button>
          <button 
            className="btn btn-primary" 
            onClick={handleSave}
            style={{ display: 'flex', alignItems: 'center', gap: 6, minWidth: 100, justifyContent: 'center' }}
            disabled={saved}
          >
            {saved ? <><Check size={16} /> Saved</> : <><Save size={16} /> Save Changes</>}
          </button>
        </div>
      </div>
    </div>
  );
};
