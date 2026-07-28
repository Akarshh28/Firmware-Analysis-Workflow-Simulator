"use client";

import React, { useState, useEffect } from "react";
import {
  BookOpen,
  Cpu,
  Terminal,
  ShieldAlert,
} from "lucide-react";

import { useProjectStore } from "../store/projectStore";

export const ToolExplorer: React.FC = () => {
  const { tools, fetchTools } = useProjectStore();
  const [selectedToolName, setSelectedToolName] = useState<string>('binwalk');
  const [activeTab, setActiveTab] = useState<'overview' | 'internals' | 'console' | 'troubleshoot'>('overview');

  // Terminal state
  const [cmdInput, setCmdInput] = useState('');
  const [terminalLogs, setTerminalLogs] = useState<string[]>([
    'FAWS Sandbox Console [Version 1.0.0]',
    'Type "help" or select a pre-made command to run it.',
    ''
  ]);

  useEffect(() => {
    fetchTools();
  }, []);

  const selectedTool = tools.find(t => t.name === selectedToolName) || tools[0];

  const handleCommandSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!cmdInput.trim()) return;

    const cmd = cmdInput.trim();
    let response: string[] = [];

    if (cmd === 'help') {
      response = [
        `> ${cmd}`,
        'Available commands in this sandbox:',
        ...selectedTool.docs.commands.map((c: { command: string; explanation: string }) => `  ${c.command} - ${c.explanation}`),
        '  clear - Clear the console',
        ''
      ];
    } else if (cmd === 'clear') {
      setTerminalLogs([]);
      setCmdInput('');
      return;
    } else {
      // Find if it matches one of the pre-made commands
      const matched = selectedTool.docs.commands.find((c: { command: string; explanation: string }) => c.command === cmd);
      if (matched) {
        response = [
          `> ${cmd}`,
          `Executing simulated ${selectedTool.name} command...`,
          'SYSTEM: Initializing sandbox analysis engine...',
          ...selectedTool.name === 'binwalk' ? [
            'STDOUT: DECIMAL       HEXADECIMAL     DESCRIPTION',
            'STDOUT: 0             0x0             TRX firmware header, lzma compressed, length: 4194304 bytes',
            'STDOUT: 1048576       0x100000        Squashfs filesystem, little endian, version 4.0'
          ] : [
            'STDOUT: Loading symbolic state graph...',
            'STDOUT: Target node found at 0x4012bc',
            'STDOUT: Solved constraint payload: DLMS_COSEM_BYPASS_KEY'
          ],
          'SYSTEM: Command completed successfully.',
          ''
        ];
      } else {
        response = [
          `> ${cmd}`,
          `bash: command not found: ${cmd}`,
          'Type "help" to see available instructions for this tool sandbox.',
          ''
        ];
      }
    }

    setTerminalLogs(prev => [...prev, ...response]);
    setCmdInput('');
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
        width: '240px',
        backgroundColor: 'var(--bg-secondary)',
        border: '1px solid var(--bg-tertiary)',
        borderRadius: 'var(--border-radius-md)',
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        overflowY: 'auto'
      }}>
        <h3 style={{ fontSize: '13px', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '8px', paddingLeft: '8px' }}>
          Registered Tools
        </h3>
        {tools.map(t => (
          <button
            key={t.name}
            onClick={() => {
              setSelectedToolName(t.name);
              setTerminalLogs([
                `FAWS ${t.name.toUpperCase()} Sandbox Terminal [Ready]`,
                'Type "help" to see commands.',
                ''
              ]);
            }}
            style={{
              padding: '10px 14px',
              backgroundColor: selectedToolName === t.name ? 'var(--bg-tertiary)' : 'transparent',
              border: selectedToolName === t.name ? '1px solid var(--accent-cyan)' : '1px solid transparent',
              color: selectedToolName === t.name ? 'var(--accent-cyan)' : 'var(--text-secondary)',
              borderRadius: 'var(--border-radius-sm)',
              cursor: 'pointer',
              textAlign: 'left',
              fontWeight: 600,
              textTransform: 'capitalize',
              transition: 'background-color 0.2s ease'
            }}
          >
            {t.name}
          </button>
        ))}
      </div>

      {/* Main Details Panel */}
      {selectedTool && (
        <div style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: 'var(--bg-secondary)',
          border: '1px solid var(--bg-tertiary)',
          borderRadius: 'var(--border-radius-md)',
          overflow: 'hidden'
        }}>
          {/* Header */}
          <div style={{
            padding: '20px',
            borderBottom: '1px solid var(--bg-tertiary)',
            backgroundColor: 'var(--bg-secondary)'
          }}>
            <h2 style={{ textTransform: 'uppercase', color: '#fff', fontSize: '20px' }}>{selectedTool.name}</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>
              {selectedTool.docs.purpose}
            </p>
          </div>

          {/* Navigation Tabs */}
          <div style={{
            display: 'flex',
            backgroundColor: 'var(--bg-primary)',
            borderBottom: '1px solid var(--bg-tertiary)'
          }}>
            <button
              onClick={() => setActiveTab('overview')}
              style={{
                padding: '12px 20px',
                background: 'none',
                border: 'none',
                borderBottom: activeTab === 'overview' ? '2px solid var(--accent-cyan)' : '2px solid transparent',
                color: activeTab === 'overview' ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                cursor: 'pointer',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <BookOpen size={16} /> Overview
            </button>
            <button
              onClick={() => setActiveTab('internals')}
              style={{
                padding: '12px 20px',
                background: 'none',
                border: 'none',
                borderBottom: activeTab === 'internals' ? '2px solid var(--accent-cyan)' : '2px solid transparent',
                color: activeTab === 'internals' ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                cursor: 'pointer',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <Cpu size={16} /> Internals
            </button>
            <button
              onClick={() => setActiveTab('console')}
              style={{
                padding: '12px 20px',
                background: 'none',
                border: 'none',
                borderBottom: activeTab === 'console' ? '2px solid var(--accent-cyan)' : '2px solid transparent',
                color: activeTab === 'console' ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                cursor: 'pointer',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <Terminal size={16} /> Terminal Sandbox
            </button>
            <button
              onClick={() => setActiveTab('troubleshoot')}
              style={{
                padding: '12px 20px',
                background: 'none',
                border: 'none',
                borderBottom: activeTab === 'troubleshoot' ? '2px solid var(--accent-cyan)' : '2px solid transparent',
                color: activeTab === 'troubleshoot' ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                cursor: 'pointer',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <ShieldAlert size={16} /> Troubleshooting
            </button>
          </div>

          {/* Tab Content Panel */}
          <div style={{ flex: 1, padding: '24px', overflowY: 'auto' }}>

            {activeTab === 'overview' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div>
                  <h4 style={{ color: 'var(--accent-cyan)', marginBottom: '6px' }}>Input Parameters</h4>
                  <p style={{ color: 'var(--text-primary)', fontSize: '15px' }}>{selectedTool.docs.input}</p>
                </div>
                <div>
                  <h4 style={{ color: 'var(--accent-cyan)', marginBottom: '6px' }}>Expected Outputs</h4>
                  <p style={{ color: 'var(--text-primary)', fontSize: '15px' }}>{selectedTool.docs.output}</p>
                </div>
                <div>
                  <h4 style={{ color: 'var(--accent-cyan)', marginBottom: '6px' }}>Analysis Workflow Stage</h4>
                  <p style={{ color: 'var(--text-primary)', fontSize: '15px' }}>{selectedTool.docs.workflow}</p>
                </div>
              </div>
            )}

            {activeTab === 'internals' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div>
                  <h4 style={{ color: 'var(--accent-purple)', marginBottom: '8px' }}>Internal Processing Logic</h4>
                  <p style={{ color: 'var(--text-primary)', fontSize: '15px', lineHeight: '1.6' }}>
                    {selectedTool.docs.internal_working}
                  </p>
                </div>
              </div>
            )}

            {activeTab === 'console' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', height: '100%' }}>

                {/* Pre-made command selectors */}
                <div>
                  <h5 style={{ color: 'var(--text-secondary)', marginBottom: '8px', fontSize: '12px' }}>CLICK TO LOAD Sandbox COMMANDS</h5>
                  <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                    {selectedTool.docs.commands.map((c: { command: string; explanation: string }, i: number) => (
                      <button
                        key={i}
                        onClick={() => setCmdInput(c.command)}
                        style={{
                          padding: '6px 12px',
                          backgroundColor: 'var(--bg-primary)',
                          border: '1px solid var(--bg-tertiary)',
                          color: '#fff',
                          fontSize: '13px',
                          fontFamily: 'var(--font-mono)',
                          borderRadius: 'var(--border-radius-sm)',
                          cursor: 'pointer'
                        }}
                      >
                        {c.command}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Console Window */}
                <div style={{
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  backgroundColor: '#050508',
                  border: '1px solid var(--bg-tertiary)',
                  borderRadius: 'var(--border-radius-sm)',
                  overflow: 'hidden'
                }}>
                  <div className="terminal-console" style={{ flex: 1, padding: '16px', overflowY: 'auto' }}>
                    {terminalLogs.map((log, idx) => (
                      <div key={idx} style={{
                        color: log.startsWith('>') ? 'var(--accent-cyan)' :
                          log.startsWith('SYSTEM') ? 'var(--accent-purple)' :
                            log.startsWith('STDOUT') ? 'var(--text-code)' :
                              log.startsWith('STDERR') ? 'var(--status-error)' :
                                'var(--text-secondary)'
                      }}>
                        {log}
                      </div>
                    ))}
                  </div>

                  <form onSubmit={handleCommandSubmit} style={{ display: 'flex', borderTop: '1px solid var(--bg-tertiary)' }}>
                    <span style={{ color: 'var(--accent-cyan)', padding: '12px', backgroundColor: 'var(--bg-primary)', borderRight: '1px solid var(--bg-tertiary)', fontFamily: 'var(--font-mono)' }}>$</span>
                    <input
                      type="text"
                      value={cmdInput}
                      onChange={e => setCmdInput(e.target.value)}
                      placeholder="Type command here (e.g. help)..."
                      style={{
                        flex: 1,
                        padding: '12px',
                        backgroundColor: 'var(--bg-primary)',
                        border: 'none',
                        color: '#fff',
                        fontFamily: 'var(--font-mono)',
                        outline: 'none'
                      }}
                    />
                  </form>
                </div>

              </div>
            )}

            {activeTab === 'troubleshoot' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div>
                  <h4 style={{ color: 'var(--status-error)', marginBottom: '8px' }}>Common Vulnerability / Errors</h4>
                  <ul style={{ paddingLeft: '20px', color: 'var(--text-primary)', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {selectedTool.docs.common_errors.map((e: string, idx: number) => (
                      <li key={idx}>{e}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 style={{ color: 'var(--status-warning)', marginBottom: '6px' }}>Troubleshooting Steps</h4>
                  <p style={{ color: 'var(--text-primary)', fontSize: '15px' }}>{selectedTool.docs.troubleshooting}</p>
                </div>

                <div>
                  <h4 style={{ color: 'var(--status-success)', marginBottom: '6px' }}>Best Practices</h4>
                  <p style={{ color: 'var(--text-primary)', fontSize: '15px' }}>{selectedTool.docs.best_practices}</p>
                </div>
              </div>
            )}

          </div>
        </div>
      )}

    </div>
  );
};

export default ToolExplorer;
