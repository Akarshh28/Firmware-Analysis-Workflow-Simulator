import React, { useState, useEffect, useRef } from "react";
import {
  BookOpen,
  Cpu,
  Terminal,
  ShieldAlert,
  Search,
  Wrench,
  CheckCircle,
  Copy,
  ChevronRight,
  Trash2,
  AlertTriangle,
  Info,
  Check,
  Activity
} from "lucide-react";

import { useProjectStore } from "../store/projectStore";
import api from "../services/api";

export const ToolExplorer: React.FC = () => {
  const { tools, fetchTools, activeProject, toolExplorerState, setToolExplorerState } = useProjectStore();
  const [selectedToolName, setSelectedToolName] = useState<string>(toolExplorerState.toolName || 'binwalk');
  const [activeTab, setActiveTab] = useState<'overview' | 'commands' | 'console' | 'troubleshoot'>(
    toolExplorerState.activeTab
  );
  const [searchQuery, setSearchQuery] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Terminal state
  const [cmdInput, setCmdInput] = useState('');
  const [terminalLogs, setTerminalLogs] = useState<string[]>([
    'FAWS Sandbox Console [Version 1.0.0]',
    'Type "help" or select a pre-made command to run it.',
    ''
  ]);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (toolExplorerState.toolName) {
      setSelectedToolName(toolExplorerState.toolName);
      setActiveTab(toolExplorerState.activeTab);
    }
  }, [toolExplorerState]);

  useEffect(() => {
    fetchTools();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (activeTab === 'console' && terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [terminalLogs, activeTab]);

  const selectedTool = tools.find(t => t.name === selectedToolName) || tools[0];
  const filteredTools = tools.filter(t => t.name.toLowerCase().includes(searchQuery.toLowerCase()));

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleCommandSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!cmdInput.trim()) return;

    const cmd = cmdInput.trim();
    
    if (cmd === 'clear') {
      setTerminalLogs([]);
      setCmdInput('');
      return;
    }
    
    if (cmd === 'help') {
      setTerminalLogs(prev => [...prev, 
        `user@faws:~$ ${cmd}`,
        'Available commands in this sandbox:',
        ...selectedTool.docs.commands.map((c: { command: string; explanation: string }) => `  ${c.command} - ${c.explanation}`),
        '  clear - Clear the console',
        ''
      ]);
      setCmdInput('');
      return;
    }

    if (!activeProject) {
      setTerminalLogs(prev => [...prev, `user@faws:~$ ${cmd}`, 'SYSTEM ERROR: No active project or firmware uploaded. Please upload a firmware file first.', '']);
      setCmdInput('');
      return;
    }

    setTerminalLogs(prev => [...prev, `user@faws:~$ ${cmd}`, 'SYSTEM: Executing command in backend sandbox...']);
    setCmdInput('');

    try {
      const res = await api.post(`projects/${activeProject.id}/sandbox`, {
        command: cmd,
        tool: selectedTool.name
      });
      
      const { stdout, stderr, exit_code } = res.data;
      
      const newLogs: string[] = [];
      if (stdout) {
          newLogs.push(...stdout.split('\n').map((l: string) => `STDOUT: ${l}`));
      }
      if (stderr) {
          newLogs.push(...stderr.split('\n').map((l: string) => `STDERR: ${l}`));
      }
      newLogs.push(`SYSTEM: Process exited with code ${exit_code}`);
      newLogs.push('');
      
      setTerminalLogs(prev => [...prev, ...newLogs]);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (e: any) {
      setTerminalLogs(prev => [...prev, `SYSTEM ERROR: Failed to reach sandbox engine. ${e.message}`, '']);
    }
  };

  if (tools.length === 0) {
    return (
      <div className="view-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <p style={{ color: 'var(--text-secondary)' }}>Loading registered system tools...</p>
      </div>
    );
  }

  return (
    <div className="view-container" style={{ display: 'flex', gap: '24px', height: 'calc(100vh - 80px)' }}>

      {/* Sidebar Tool List */}
      <div style={{
        width: '280px',
        backgroundColor: 'var(--bg-secondary)',
        border: '1px solid var(--bg-tertiary)',
        borderRadius: '12px',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        flexShrink: 0
      }}>
        <div style={{ padding: '16px', borderBottom: '1px solid var(--bg-tertiary)' }}>
          <h3 style={{ fontSize: '13px', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '12px', fontWeight: 700 }}>
            System Tools
          </h3>
          <div style={{ position: 'relative' }}>
            <Search size={14} color="var(--text-muted)" style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              placeholder="Search tools..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%', padding: '8px 12px 8px 32px', borderRadius: '6px',
                background: 'var(--bg-tertiary)', border: '1px solid var(--border-dim)',
                color: 'var(--text-primary)', fontSize: '13px', outline: 'none'
              }}
            />
          </div>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {filteredTools.map(t => {
            const isActive = selectedToolName === t.name;
            const isInstalled = t.version !== 'Not Installed';
            return (
              <button
                key={t.name}
                onClick={() => {
                  setToolExplorerState(t.name, activeTab);
                  setSelectedToolName(t.name);
                  if (activeTab === 'console') {
                     setTerminalLogs([
                      `FAWS ${t.name.toUpperCase()} Sandbox Terminal [Ready]`,
                      'Type "help" to see commands.',
                      ''
                    ]);
                  }
                }}
                style={{
                  padding: '12px 14px',
                  backgroundColor: isActive ? 'var(--bg-tertiary)' : 'transparent',
                  border: isActive ? '1px solid var(--accent-cyan)' : '1px solid transparent',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  textAlign: 'left',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  transition: 'all 0.2s ease',
                  boxShadow: isActive ? '0 4px 12px rgba(0,0,0,0.1)' : 'none'
                }}
                onMouseEnter={(e) => {
                  if (!isActive) e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.03)';
                }}
                onMouseLeave={(e) => {
                  if (!isActive) e.currentTarget.style.backgroundColor = 'transparent';
                }}
              >
                <div style={{
                  width: 32, height: 32, borderRadius: 6,
                  background: isActive ? 'rgba(34,211,238,0.1)' : 'rgba(255,255,255,0.05)',
                  color: isActive ? 'var(--accent-cyan)' : 'var(--text-muted)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                  <Wrench size={16} />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)', textTransform: 'capitalize', fontSize: '14px' }}>
                    {t.name}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '2px' }}>
                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: isInstalled ? 'var(--accent-green)' : 'var(--accent-red)' }} />
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{t.version}</span>
                  </div>
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* Main Details Panel */}
      {selectedTool && (
        <div style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: 'var(--bg-secondary)',
          border: '1px solid var(--bg-tertiary)',
          borderRadius: '12px',
          overflow: 'hidden'
        }}>
          {/* Header */}
          <div style={{
            padding: '24px',
            borderBottom: '1px solid var(--bg-tertiary)',
            backgroundColor: 'var(--bg-secondary)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            position: 'sticky',
            top: 0,
            zIndex: 10
          }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                <div style={{
                  width: 44, height: 44, borderRadius: 8,
                  background: 'var(--bg-tertiary)', border: '1px solid var(--border-dim)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: 'var(--accent-cyan)'
                }}>
                  <Cpu size={24} />
                </div>
                <div>
                  <h2 style={{ textTransform: 'uppercase', color: 'var(--text-primary)', fontSize: '24px', fontWeight: 800, margin: 0 }}>
                    {selectedTool.name}
                  </h2>
                  <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '2px 8px', borderRadius: '4px', background: 'rgba(255,255,255,0.05)', fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                    <CheckCircle size={10} color={selectedTool.version !== 'Not Installed' ? 'var(--accent-green)' : 'var(--text-muted)'} />
                    {selectedTool.version !== 'Not Installed' ? 'Ready for execution' : 'Not installed'}
                  </div>
                </div>
              </div>
            </div>
            
            <div style={{ display: 'flex', gap: '8px' }}>
              <button className="btn btn-secondary" onClick={() => { setActiveTab('console'); setToolExplorerState(selectedToolName, 'console'); }} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Terminal size={14} /> Open Sandbox
              </button>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div style={{
            display: 'flex',
            backgroundColor: 'var(--bg-primary)',
            borderBottom: '1px solid var(--bg-tertiary)',
            padding: '0 12px'
          }}>
            <button
              onClick={() => { setActiveTab('overview'); setToolExplorerState(selectedToolName, 'overview'); }}
              style={{
                padding: '16px 20px', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px',
                borderBottom: activeTab === 'overview' ? '2px solid var(--accent-cyan)' : '2px solid transparent',
                color: activeTab === 'overview' ? 'var(--accent-cyan)' : 'var(--text-secondary)',
              }}
            >
              <BookOpen size={16} /> Overview
            </button>
            <button
              onClick={() => { setActiveTab('commands'); setToolExplorerState(selectedToolName, 'commands'); }}
              style={{
                padding: '16px 20px', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px',
                borderBottom: activeTab === 'commands' ? '2px solid var(--accent-cyan)' : '2px solid transparent',
                color: activeTab === 'commands' ? 'var(--accent-cyan)' : 'var(--text-secondary)',
              }}
            >
              <Terminal size={16} /> Commands & Usage
            </button>
            <button
              onClick={() => { setActiveTab('console'); setToolExplorerState(selectedToolName, 'console'); }}
              style={{
                padding: '16px 20px', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px',
                borderBottom: activeTab === 'console' ? '2px solid var(--accent-cyan)' : '2px solid transparent',
                color: activeTab === 'console' ? 'var(--accent-cyan)' : 'var(--text-secondary)',
              }}
            >
              <Cpu size={16} /> Sandbox Console
            </button>
            <button
              onClick={() => { setActiveTab('troubleshoot'); setToolExplorerState(selectedToolName, 'troubleshoot'); }}
              style={{
                padding: '16px 20px', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px',
                borderBottom: activeTab === 'troubleshoot' ? '2px solid var(--accent-cyan)' : '2px solid transparent',
                color: activeTab === 'troubleshoot' ? 'var(--accent-cyan)' : 'var(--text-secondary)',
              }}
            >
              <ShieldAlert size={16} /> Troubleshoot
            </button>
          </div>

          {/* Content Area */}
          <div style={{ padding: '24px', overflowY: 'auto', flex: 1, backgroundColor: activeTab === 'console' ? '#000' : 'var(--bg-primary)' }}>
            
            {activeTab === 'overview' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '800px' }}>
                <div style={{ padding: '20px', background: 'var(--bg-secondary)', border: '1px solid var(--bg-tertiary)', borderRadius: '8px' }}>
                  <h4 style={{ color: 'var(--text-primary)', fontSize: '16px', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <BookOpen size={18} color="var(--accent-cyan)" /> Primary Purpose
                  </h4>
                  <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6' }}>{selectedTool.docs.purpose}</p>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div style={{ padding: '20px', background: 'var(--bg-secondary)', border: '1px solid var(--bg-tertiary)', borderRadius: '8px' }}>
                    <h4 style={{ color: 'var(--text-primary)', fontSize: '14px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      <ChevronRight size={16} color="var(--accent-purple)" /> Input Format
                    </h4>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>{selectedTool.docs.input}</p>
                  </div>
                  <div style={{ padding: '20px', background: 'var(--bg-secondary)', border: '1px solid var(--bg-tertiary)', borderRadius: '8px' }}>
                    <h4 style={{ color: 'var(--text-primary)', fontSize: '14px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      <CheckCircle size={16} color="var(--accent-green)" /> Expected Output
                    </h4>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>{selectedTool.docs.output}</p>
                  </div>
                </div>

                <div>
                  <h4 style={{ color: 'var(--text-primary)', fontSize: '16px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Activity size={18} color="var(--accent-amber)" /> Workflow Integration
                  </h4>
                  <p style={{ color: 'var(--text-secondary)', lineHeight: '1.6' }}>{selectedTool.docs.workflow}</p>
                </div>
                
                {selectedTool.docs.references && selectedTool.docs.references.length > 0 && (
                  <div>
                    <h4 style={{ color: 'var(--text-primary)', fontSize: '16px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <BookOpen size={18} color="var(--text-muted)" /> References
                    </h4>
                    <ul style={{ paddingLeft: '24px', margin: 0, color: 'var(--accent-cyan)' }}>
                      {selectedTool.docs.references.map((ref: string, i: number) => (
                        <li key={i} style={{ marginBottom: '8px' }}>
                          <a href="#" style={{ color: 'inherit', textDecoration: 'none' }}>{ref}</a>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'commands' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '800px' }}>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '8px' }}>These commands can be executed in the Sandbox Console.</p>
                
                {selectedTool.docs.commands.map((cmd: { command: string; explanation: string }, idx: number) => (
                  <div key={idx} style={{ 
                    backgroundColor: 'var(--bg-secondary)', border: '1px solid var(--bg-tertiary)', 
                    borderRadius: '8px', overflow: 'hidden'
                  }}>
                    <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--bg-tertiary)' }}>
                      <p style={{ color: 'var(--text-primary)', margin: 0, fontSize: '14px', fontWeight: 500 }}>{cmd.explanation}</p>
                    </div>
                    <div style={{ padding: '12px 20px', backgroundColor: '#0a0a0a', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <code style={{ color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)', fontSize: '13px' }}>
                        {cmd.command}
                      </code>
                      <button 
                        className="btn btn-icon" 
                        onClick={() => handleCopy(cmd.command, `cmd-${idx}`)}
                        style={{ padding: '6px', background: 'rgba(255,255,255,0.05)' }}
                      >
                        {copiedId === `cmd-${idx}` ? <Check size={14} color="var(--accent-green)" /> : <Copy size={14} color="var(--text-muted)" />}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'troubleshoot' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '800px' }}>
                
                {/* Errors */}
                <div>
                  <h4 style={{ color: 'var(--text-primary)', fontSize: '16px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <AlertTriangle size={18} color="var(--accent-red)" /> Common Errors
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {selectedTool.docs.common_errors.map((err: string, idx: number) => (
                      <div key={idx} style={{ 
                        padding: '16px', borderRadius: '8px', 
                        background: 'rgba(239, 68, 68, 0.05)', border: '1px solid rgba(239, 68, 68, 0.2)',
                        display: 'flex', gap: '12px', alignItems: 'flex-start'
                      }}>
                        <AlertTriangle size={18} color="var(--accent-red)" style={{ marginTop: '2px', flexShrink: 0 }} />
                        <span style={{ color: 'var(--text-primary)', lineHeight: 1.5, fontSize: '14px' }}>{err}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Troubleshooting */}
                <div>
                  <h4 style={{ color: 'var(--text-primary)', fontSize: '16px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Wrench size={18} color="var(--accent-amber)" /> Troubleshooting Steps
                  </h4>
                  <div style={{ 
                        padding: '16px', borderRadius: '8px', 
                        background: 'rgba(245, 158, 11, 0.05)', border: '1px solid rgba(245, 158, 11, 0.2)',
                        display: 'flex', gap: '12px', alignItems: 'flex-start'
                  }}>
                    <Info size={18} color="var(--accent-amber)" style={{ marginTop: '2px', flexShrink: 0 }} />
                    <span style={{ color: 'var(--text-primary)', lineHeight: 1.5, fontSize: '14px' }}>{selectedTool.docs.troubleshooting}</span>
                  </div>
                </div>

                {/* Best Practices */}
                <div>
                  <h4 style={{ color: 'var(--text-primary)', fontSize: '16px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle size={18} color="var(--accent-green)" /> Best Practices
                  </h4>
                  <div style={{ 
                        padding: '16px', borderRadius: '8px', 
                        background: 'rgba(34, 197, 94, 0.05)', border: '1px solid rgba(34, 197, 94, 0.2)',
                        display: 'flex', gap: '12px', alignItems: 'flex-start'
                  }}>
                    <CheckCircle size={18} color="var(--accent-green)" style={{ marginTop: '2px', flexShrink: 0 }} />
                    <span style={{ color: 'var(--text-primary)', lineHeight: 1.5, fontSize: '14px' }}>{selectedTool.docs.best_practices}</span>
                  </div>
                </div>

              </div>
            )}

            {activeTab === 'console' && (
              <div style={{ display: 'flex', flexDirection: 'column', height: '100%', fontFamily: 'var(--font-mono)' }}>
                {/* Fake Terminal Header */}
                <div style={{ 
                  backgroundColor: '#1a1a1a', padding: '8px 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  borderTopLeftRadius: '8px', borderTopRightRadius: '8px', borderBottom: '1px solid #333'
                }}>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#ef4444' }}></div>
                    <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#f59e0b' }}></div>
                    <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#22c55e' }}></div>
                  </div>
                  <div style={{ color: '#888', fontSize: '12px' }}>user@faws: ~/sandbox/{selectedTool.name}</div>
                  <button 
                    onClick={() => {
                      setTerminalLogs([
                        `FAWS ${selectedTool.name.toUpperCase()} Sandbox Terminal [Ready]`,
                        'Type "help" to see commands.',
                        ''
                      ]);
                      setCmdInput('');
                    }}
                    style={{ background: 'none', border: 'none', color: '#888', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px' }}
                  >
                    <Trash2 size={12} /> Clear
                  </button>
                </div>

                <div style={{ 
                  flex: 1, overflowY: 'auto', padding: '16px', backgroundColor: '#000', color: '#a3a3a3',
                  fontSize: '14px', lineHeight: '1.6', display: 'flex', flexDirection: 'column'
                }}>
                  {terminalLogs.map((log, i) => (
                    <div key={i} style={{ 
                      color: log.startsWith('SYSTEM ERROR') || log.startsWith('STDERR') ? '#ef4444' : 
                             log.startsWith('SYSTEM') ? '#a855f7' : 
                             log.startsWith('user@faws') ? '#fff' :
                             log.startsWith('STDOUT') ? '#d4d4d8' : '#22d3ee',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-all',
                      marginBottom: log === '' ? '12px' : '2px'
                    }}>
                      {log}
                    </div>
                  ))}
                  <div ref={terminalEndRef} />
                </div>
                
                <form onSubmit={handleCommandSubmit} style={{ 
                  display: 'flex', borderTop: '1px solid #333', backgroundColor: '#0a0a0a',
                  borderBottomLeftRadius: '8px', borderBottomRightRadius: '8px'
                }}>
                  <div style={{ padding: '16px 8px 16px 16px', color: '#22c55e', fontWeight: 700, display: 'flex', alignItems: 'center' }}>
                    <span style={{ color: '#22c55e' }}>user@faws</span>
                    <span style={{ color: '#fff' }}>:</span>
                    <span style={{ color: '#3b82f6' }}>~</span>
                    <span style={{ color: '#fff', marginLeft: '4px' }}>$</span>
                  </div>
                  <input
                    type="text"
                    value={cmdInput}
                    onChange={(e) => setCmdInput(e.target.value)}
                    placeholder="Type a command or 'help'..."
                    autoFocus
                    style={{
                      flex: 1, background: 'transparent', border: 'none', color: '#fff',
                      padding: '16px', outline: 'none', fontFamily: 'inherit', fontSize: '14px'
                    }}
                  />
                </form>
              </div>
            )}

          </div>
        </div>
      )}

    </div>
  );
};

export default ToolExplorer;
