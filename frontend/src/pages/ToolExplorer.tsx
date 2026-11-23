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
  Activity,
  Play,
  RotateCcw,
  Sparkles,
  HelpCircle,
  Clock,
  Layers,
  FileText
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
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState<number>(-1);
  const [isExecuting, setIsExecuting] = useState(false);
  const [lastExitCode, setLastExitCode] = useState<number | null>(null);
  const [lastExecutionTime, setLastExecutionTime] = useState<number | null>(null);

  const selectedTool = tools.find(t => t.name === selectedToolName) || tools[0] || {
    name: 'binwalk',
    version: '2.3.4',
    docs: {
      purpose: 'Firmware extraction and analysis',
      input: 'Firmware binary',
      output: 'Extracted directory',
      workflow: 'Extraction stage',
      commands: [{ command: 'binwalk firmware.bin', explanation: 'Scan firmware' }],
      common_errors: [],
      troubleshooting: '',
      best_practices: '',
      references: []
    }
  };

  const [terminalLogs, setTerminalLogs] = useState<string[]>([
    `FAWS ISOLATED SANDBOX ENGINE v2.4 [Connected]`,
    `Tool: ${selectedTool.name.toUpperCase()} (v${selectedTool.version || '1.0.0'})`,
    `Target: ${activeProject?.name || 'Smart Meter Firmware'} (${activeProject?.target_architecture || 'ARM Cortex-M4'})`,
    `Type "help" or click any quick command below to execute in real-time.`,
    ''
  ]);
  const terminalEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

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

  // Update terminal welcome message when switching tools
  useEffect(() => {
    setTerminalLogs([
      `FAWS ISOLATED SANDBOX ENGINE v2.4 [Connected]`,
      `Tool: ${selectedTool.name.toUpperCase()} (v${selectedTool.version || '1.0.0'})`,
      `Target: ${activeProject?.name || 'Smart Meter Firmware'} (${activeProject?.target_architecture || 'ARM Cortex-M4'})`,
      `Type "help" or click any quick command below to execute.`,
      ''
    ]);
    setLastExitCode(null);
    setLastExecutionTime(null);
  }, [selectedToolName, activeProject]);

  useEffect(() => {
    if (activeTab === 'console' && terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [terminalLogs, activeTab, isExecuting]);

  const filteredTools = tools.filter(t => t.name.toLowerCase().includes(searchQuery.toLowerCase()));

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const executeCommand = async (commandToRun: string) => {
    const cmd = commandToRun.trim();
    if (!cmd) return;

    // Add to history
    setCommandHistory(prev => [cmd, ...prev.filter(c => c !== cmd)]);
    setHistoryIndex(-1);

    if (cmd === 'clear') {
      setTerminalLogs([]);
      setCmdInput('');
      return;
    }

    if (cmd === 'help') {
      setTerminalLogs(prev => [
        ...prev,
        `user@faws:~$ ${cmd}`,
        '═'.repeat(68),
        `FAWS SANDBOX CLI — ${selectedTool.name.toUpperCase()} (v${selectedTool.version || '1.0.0'})`,
        `Available pre-configured commands:`,
        ...selectedTool.docs.commands.map((c: { command: string; explanation: string }) => `  $ ${c.command.padEnd(40)} # ${c.explanation}`),
        '',
        'Standard Sandbox Built-ins:',
        '  $ help                     # Display this help manual',
        '  $ clear                    # Clear console output',
        '  $ env                      # Inspect sandbox environment variables',
        '  $ ls -la                   # List current sandbox files and extracted artifacts',
        '  $ file <binary>            # Display binary architecture and ELF headers',
        '  $ hexdump -C <file>        # Canonical hex + ASCII binary dump',
        '  $ cat <file>               # Read artifact or configuration content',
        '═'.repeat(68),
        ''
      ]);
      setCmdInput('');
      return;
    }

    if (!activeProject) {
      setTerminalLogs(prev => [
        ...prev,
        `user@faws:~$ ${cmd}`,
        'SYSTEM ERROR: No active project selected. Please select or create a project first.',
        ''
      ]);
      setCmdInput('');
      return;
    }

    setTerminalLogs(prev => [...prev, `user@faws:~$ ${cmd}`]);
    setCmdInput('');
    setIsExecuting(true);

    try {
      const res = await api.post(`projects/${activeProject.id}/sandbox`, {
        command: cmd,
        tool: selectedTool.name
      });

      const { stdout, stderr, exit_code, execution_time_ms } = res.data;
      setLastExitCode(exit_code);
      setLastExecutionTime(execution_time_ms || 35);

      const newLogs: string[] = [];
      if (stdout) {
        newLogs.push(...stdout.split('\n'));
      }
      if (stderr) {
        newLogs.push(...stderr.split('\n').map((l: string) => `STDERR: ${l}`));
      }
      newLogs.push(`[Process finished with exit code ${exit_code} in ${execution_time_ms || 35}ms]`);
      newLogs.push('');

      setTerminalLogs(prev => [...prev, ...newLogs]);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (e: any) {
      setTerminalLogs(prev => [
        ...prev,
        `SYSTEM ERROR: Failed to execute sandbox command. ${e.response?.data?.detail || e.message}`,
        ''
      ]);
      setLastExitCode(1);
    } finally {
      setIsExecuting(false);
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }
  };

  const handleCommandSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeCommand(cmdInput);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (commandHistory.length > 0) {
        const nextIdx = Math.min(historyIndex + 1, commandHistory.length - 1);
        setHistoryIndex(nextIdx);
        setCmdInput(commandHistory[nextIdx]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex > 0) {
        const prevIdx = historyIndex - 1;
        setHistoryIndex(prevIdx);
        setCmdInput(commandHistory[prevIdx]);
      } else if (historyIndex === 0) {
        setHistoryIndex(-1);
        setCmdInput('');
      }
    }
  };

  const quickCommands = [
    ...(selectedTool.docs?.commands || []).map((c: { command: string }) => c.command),
    'ls -la',
    'file firmware.bin',
    'hexdump -C firmware.bin',
    'help'
  ];

  if (tools.length === 0) {
    return (
      <div className="view-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <p style={{ color: 'var(--text-secondary)' }}>Loading registered system tools...</p>
      </div>
    );
  }

  return (
    <div className="view-container" style={{ display: 'flex', gap: '20px', height: 'calc(100vh - 80px)' }}>

      {/* Sidebar Tool List */}
      <div style={{
        width: '280px',
        backgroundColor: 'var(--bg-secondary)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '12px',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        flexShrink: 0
      }}>
        <div style={{ padding: '16px', borderBottom: '1px solid var(--border-subtle)' }}>
          <h3 style={{ fontSize: '12px', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '10px', fontWeight: 700, letterSpacing: '0.06em' }}>
            Pipeline & Forensic Tools
          </h3>
          <div style={{ position: 'relative' }}>
            <Search size={14} color="var(--text-muted)" style={{ position: 'absolute', left: '10px', top: '10px' }} />
            <input
              type="text"
              placeholder="Filter tools..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                padding: '8px 10px 8px 32px',
                backgroundColor: 'var(--bg-tertiary)',
                border: '1px solid var(--border-dim)',
                borderRadius: '6px',
                color: 'var(--text-primary)',
                fontSize: '12px',
                outline: 'none'
              }}
            />
          </div>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: '8px' }}>
          {filteredTools.map((t) => {
            const isSelected = t.name === selectedToolName;
            return (
              <button
                key={t.name}
                onClick={() => {
                  setSelectedToolName(t.name);
                  setToolExplorerState(t.name, activeTab);
                }}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px 12px',
                  borderRadius: '6px',
                  backgroundColor: isSelected ? 'rgba(99, 120, 255, 0.12)' : 'transparent',
                  border: isSelected ? '1px solid var(--accent-blue)' : '1px solid transparent',
                  color: isSelected ? 'var(--accent-blue)' : 'var(--text-primary)',
                  cursor: 'pointer',
                  marginBottom: '4px',
                  textAlign: 'left',
                  transition: 'all 0.15s ease'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
                  <Wrench size={14} style={{ flexShrink: 0, opacity: isSelected ? 1 : 0.6 }} />
                  <span style={{ fontSize: '13px', fontWeight: isSelected ? 600 : 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {t.name}
                  </span>
                </div>
                <span style={{
                  fontSize: '10px',
                  padding: '2px 6px',
                  borderRadius: '4px',
                  backgroundColor: isSelected ? 'rgba(99,120,255,0.2)' : 'var(--bg-tertiary)',
                  color: isSelected ? 'var(--accent-blue)' : 'var(--text-muted)',
                  fontFamily: 'var(--font-mono)'
                }}>
                  v{t.version || '1.0'}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Tool Content Pane */}
      {selectedTool && (
        <div style={{
          flex: 1,
          backgroundColor: 'var(--bg-secondary)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '12px',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}>
          {/* Header */}
          <div style={{
            padding: '20px 24px',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start'
          }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>
                  {selectedTool.name}
                </h2>
                <span className="badge badge-queued" style={{ fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
                  v{selectedTool.version || '1.0'}
                </span>
                <span className="badge badge-success" style={{ fontSize: '10px' }}>
                  SANDBOX READY
                </span>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px', margin: 0, maxWidth: '650px', lineHeight: 1.5 }}>
                {selectedTool.docs?.purpose}
              </p>
            </div>

            <button
              className="btn btn-primary"
              onClick={() => {
                setActiveTab('console');
                setToolExplorerState(selectedToolName, 'console');
              }}
              style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', padding: '8px 14px' }}
            >
              <Terminal size={14} /> Open Sandbox
            </button>
          </div>

          {/* Navigation Tabs */}
          <div style={{
            display: 'flex',
            borderBottom: '1px solid var(--border-subtle)',
            backgroundColor: 'var(--bg-tertiary)'
          }}>
            {[
              { id: 'overview', label: 'Overview', icon: <BookOpen size={14} /> },
              { id: 'commands', label: 'CLI Commands', icon: <Terminal size={14} /> },
              { id: 'console', label: 'Sandbox Console', icon: <Cpu size={14} /> },
              { id: 'troubleshoot', label: 'Troubleshooting & Rules', icon: <AlertTriangle size={14} /> }
            ].map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => {
                    setActiveTab(tab.id as any);
                    setToolExplorerState(selectedToolName, tab.id as any);
                  }}
                  style={{
                    padding: '12px 18px',
                    fontSize: '12px',
                    fontWeight: 600,
                    backgroundColor: isActive ? 'var(--bg-secondary)' : 'transparent',
                    border: 'none',
                    borderBottom: isActive ? '2px solid var(--accent-blue)' : '2px solid transparent',
                    color: isActive ? 'var(--accent-blue)' : 'var(--text-secondary)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {tab.icon} {tab.label}
                </button>
              );
            })}
          </div>

          {/* Tab Content */}
          <div style={{ flex: 1, overflowY: 'auto', padding: activeTab === 'console' ? '0' : '24px' }}>

            {/* TAB: Overview */}
            {activeTab === 'overview' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '850px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
                  <div className="card" style={{ padding: '16px' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px', fontWeight: 600 }}>
                      📥 Expected Input
                    </div>
                    <div style={{ fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.5 }}>
                      {selectedTool.docs.input}
                    </div>
                  </div>
                  <div className="card" style={{ padding: '16px' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px', fontWeight: 600 }}>
                      📤 Generated Output
                    </div>
                    <div style={{ fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.5 }}>
                      {selectedTool.docs.output}
                    </div>
                  </div>
                </div>

                <div className="card" style={{ padding: '18px' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '8px', fontWeight: 600 }}>
                    🔄 Pipeline Workflow Role
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.6 }}>
                    {selectedTool.docs.workflow}
                  </div>
                </div>

                {selectedTool.docs.references && selectedTool.docs.references.length > 0 && (
                  <div>
                    <h4 style={{ fontSize: '13px', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '10px', fontWeight: 600 }}>
                      Compliance & Standards References
                    </h4>
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                      {selectedTool.docs.references.map((ref: string, i: number) => (
                        <span key={i} className="badge badge-queued" style={{ fontSize: '11px' }}>
                          {ref}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* TAB: CLI Commands */}
            {activeTab === 'commands' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '850px' }}>
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px', margin: 0 }}>
                  Pre-configured CLI commands verified for this tool. Click the copy icon to copy, or run them directly in the <strong>Sandbox Console</strong>.
                </p>

                {selectedTool.docs.commands.map((cmd: { command: string; explanation: string }, idx: number) => (
                  <div key={idx} style={{
                    backgroundColor: 'var(--bg-tertiary)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '8px',
                    overflow: 'hidden'
                  }}>
                    <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border-subtle)' }}>
                      <p style={{ color: 'var(--text-primary)', margin: 0, fontSize: '13px', fontWeight: 600 }}>
                        {cmd.explanation}
                      </p>
                    </div>
                    <div style={{ padding: '10px 16px', backgroundColor: '#070707', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <code style={{ color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)', fontSize: '12px' }}>
                        $ {cmd.command}
                      </code>
                      <div style={{ display: 'flex', gap: '6px' }}>
                        <button
                          className="btn btn-secondary"
                          onClick={() => {
                            setActiveTab('console');
                            setToolExplorerState(selectedToolName, 'console');
                            executeCommand(cmd.command);
                          }}
                          style={{ padding: '4px 8px', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px' }}
                        >
                          <Play size={11} /> Run in Sandbox
                        </button>
                        <button
                          className="btn btn-icon"
                          onClick={() => handleCopy(cmd.command, `cmd-${idx}`)}
                          style={{ padding: '5px', background: 'rgba(255,255,255,0.06)' }}
                        >
                          {copiedId === `cmd-${idx}` ? <Check size={13} color="var(--accent-green)" /> : <Copy size={13} color="var(--text-muted)" />}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* TAB: Troubleshooting */}
            {activeTab === 'troubleshoot' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '850px' }}>
                <div>
                  <h4 style={{ color: 'var(--text-primary)', fontSize: '14px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <AlertTriangle size={16} color="var(--accent-red)" /> Known Failure Modes & Errors
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {selectedTool.docs.common_errors.map((err: string, idx: number) => (
                      <div key={idx} style={{
                        padding: '12px 16px', borderRadius: '8px',
                        background: 'rgba(239, 68, 68, 0.05)', border: '1px solid rgba(239, 68, 68, 0.2)',
                        display: 'flex', gap: '10px', alignItems: 'flex-start'
                      }}>
                        <AlertTriangle size={16} color="var(--accent-red)" style={{ marginTop: '2px', flexShrink: 0 }} />
                        <span style={{ color: 'var(--text-primary)', lineHeight: 1.5, fontSize: '13px' }}>{err}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 style={{ color: 'var(--text-primary)', fontSize: '14px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Wrench size={16} color="var(--accent-amber)" /> Remediation & Troubleshooting Steps
                  </h4>
                  <div style={{
                    padding: '14px 16px', borderRadius: '8px',
                    background: 'rgba(245, 158, 11, 0.05)', border: '1px solid rgba(245, 158, 11, 0.2)',
                    display: 'flex', gap: '10px', alignItems: 'flex-start'
                  }}>
                    <Info size={16} color="var(--accent-amber)" style={{ marginTop: '2px', flexShrink: 0 }} />
                    <span style={{ color: 'var(--text-primary)', lineHeight: 1.5, fontSize: '13px' }}>{selectedTool.docs.troubleshooting}</span>
                  </div>
                </div>

                <div>
                  <h4 style={{ color: 'var(--text-primary)', fontSize: '14px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle size={16} color="var(--accent-green)" /> Operational Best Practices
                  </h4>
                  <div style={{
                    padding: '14px 16px', borderRadius: '8px',
                    background: 'rgba(34, 197, 94, 0.05)', border: '1px solid rgba(34, 197, 94, 0.2)',
                    display: 'flex', gap: '10px', alignItems: 'flex-start'
                  }}>
                    <CheckCircle size={16} color="var(--accent-green)" style={{ marginTop: '2px', flexShrink: 0 }} />
                    <span style={{ color: 'var(--text-primary)', lineHeight: 1.5, fontSize: '13px' }}>{selectedTool.docs.best_practices}</span>
                  </div>
                </div>
              </div>
            )}

            {/* TAB: PRODUCTION SANDBOX CONSOLE */}
            {activeTab === 'console' && (
              <div style={{ display: 'flex', flexDirection: 'column', height: '100%', fontFamily: 'var(--font-mono)' }}>

                {/* Production Terminal Top Bar */}
                <div style={{
                  backgroundColor: '#121214',
                  padding: '10px 16px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  borderBottom: '1px solid #222226'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ display: 'flex', gap: '6px' }}>
                      <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#ef4444' }} />
                      <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#f59e0b' }} />
                      <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#22c55e' }} />
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ color: '#e4e4e7', fontSize: '12px', fontWeight: 600 }}>
                        user@faws: ~/sandbox/{selectedTool.name}
                      </span>
                      <span style={{
                        fontSize: '10px',
                        padding: '1px 6px',
                        borderRadius: '4px',
                        background: 'rgba(34,197,94,0.15)',
                        color: '#22c55e',
                        border: '1px solid rgba(34,197,94,0.3)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}>
                        <span style={{ width: '5px', height: '5px', borderRadius: '50%', background: '#22c55e' }} />
                        SANDBOX ACTIVE
                      </span>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    {lastExitCode !== null && (
                      <span style={{
                        fontSize: '10px',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        background: lastExitCode === 0 ? 'rgba(34,197,94,0.15)' : 'rgba(239,68,68,0.15)',
                        color: lastExitCode === 0 ? '#22c55e' : '#ef4444',
                        border: `1px solid ${lastExitCode === 0 ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)'}`
                      }}>
                        Exit: {lastExitCode} {lastExecutionTime ? `(${lastExecutionTime}ms)` : ''}
                      </span>
                    )}
                    <button
                      type="button"
                      onClick={() => handleCopy(terminalLogs.join('\n'), 'term-all')}
                      style={{
                        background: 'rgba(255,255,255,0.05)',
                        border: '1px solid #333',
                        color: '#a1a1aa',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        fontSize: '11px'
                      }}
                    >
                      {copiedId === 'term-all' ? <Check size={11} color="var(--accent-green)" /> : <Copy size={11} />} Copy Logs
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setTerminalLogs([
                          `FAWS ISOLATED SANDBOX ENGINE v2.4 [Screen Cleared]`,
                          `Active Module: ${selectedTool.name.toUpperCase()} (v${selectedTool.version || '1.0.0'})`,
                          ''
                        ]);
                        setCmdInput('');
                      }}
                      style={{
                        background: 'rgba(255,255,255,0.05)',
                        border: '1px solid #333',
                        color: '#a1a1aa',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        fontSize: '11px'
                      }}
                    >
                      <Trash2 size={11} /> Clear
                    </button>
                  </div>
                </div>

                {/* Target Metadata Sub-bar */}
                <div style={{
                  backgroundColor: '#0c0c0e',
                  padding: '6px 16px',
                  borderBottom: '1px solid #1c1c20',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  fontSize: '11px',
                  color: 'var(--text-muted)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span>Target: <strong style={{ color: 'var(--text-primary)' }}>{activeProject?.name || 'Firmware Binary'}</strong></span>
                    <span>•</span>
                    <span>Arch: <strong style={{ color: 'var(--accent-cyan)' }}>{activeProject?.target_architecture || 'ARM Cortex-M4'}</strong></span>
                    <span>•</span>
                    <span>Container: <strong style={{ color: '#a855f7' }}>faws-sandbox-isolated</strong></span>
                  </div>
                  <span>Press <kbd style={{ background: '#222', padding: '1px 4px', borderRadius: 3 }}>↑</kbd> <kbd style={{ background: '#222', padding: '1px 4px', borderRadius: 3 }}>↓</kbd> for history</span>
                </div>

                {/* Interactive Quick-Run Preset Command Pills */}
                <div style={{
                  backgroundColor: '#08080a',
                  padding: '8px 16px',
                  borderBottom: '1px solid #1a1a1e',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  overflowX: 'auto',
                  whiteSpace: 'nowrap'
                }}>
                  <span style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'flex', alignItems: 'center', gap: 4 }}>
                    <Sparkles size={11} color="var(--accent-blue)" /> Quick Commands:
                  </span>
                  {quickCommands.map((qCmd, idx) => (
                    <button
                      key={idx}
                      type="button"
                      disabled={isExecuting}
                      onClick={() => executeCommand(qCmd)}
                      style={{
                        padding: '3px 9px',
                        fontSize: '11px',
                        borderRadius: '4px',
                        background: 'rgba(99, 120, 255, 0.08)',
                        border: '1px solid rgba(99, 120, 255, 0.25)',
                        color: 'var(--accent-blue)',
                        cursor: isExecuting ? 'not-allowed' : 'pointer',
                        fontFamily: 'var(--font-mono)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        transition: 'all 0.15s ease'
                      }}
                      onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(99, 120, 255, 0.18)'; }}
                      onMouseLeave={(e) => { e.currentTarget.style.background = 'rgba(99, 120, 255, 0.08)'; }}
                    >
                      <Play size={9} /> {qCmd}
                    </button>
                  ))}
                </div>

                {/* Terminal Log Output Window */}
                <div style={{
                  flex: 1,
                  overflowY: 'auto',
                  padding: '16px',
                  backgroundColor: '#050506',
                  color: '#d4d4d8',
                  fontSize: '13px',
                  lineHeight: '1.65',
                  display: 'flex',
                  flexDirection: 'column'
                }}>
                  {terminalLogs.map((log, i) => {
                    const isCommandPrompt = log.startsWith('user@faws:~$');
                    const isSystemAlert = log.startsWith('SYSTEM ERROR') || log.startsWith('STDERR:');
                    const isSystemInfo = log.startsWith('SYSTEM:') || log.startsWith('FAWS ISOLATED') || log.startsWith('Tool:');
                    const isWarningFinding = log.includes('[!]') || log.includes('VULNERABILITY') || log.includes('CRITICAL');
                    const isSuccess = log.includes('[+]') || log.includes('[✓]') || log.includes('Process finished');
                    const isDivider = log.startsWith('═') || log.startsWith('─') || log.startsWith('-');

                    return (
                      <div
                        key={i}
                        style={{
                          color: isCommandPrompt ? '#22d3ee' :
                                 isSystemAlert ? '#f87171' :
                                 isWarningFinding ? '#fbbf24' :
                                 isSuccess ? '#4ade80' :
                                 isSystemInfo ? '#c084fc' :
                                 isDivider ? '#3f3f46' :
                                 '#d4d4d8',
                          fontWeight: isCommandPrompt ? 700 : isWarningFinding ? 600 : 400,
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-all',
                          marginBottom: log === '' ? '10px' : '2px',
                          background: isSystemAlert ? 'rgba(239,68,68,0.06)' : 'transparent',
                          padding: isSystemAlert ? '2px 6px' : '0',
                          borderRadius: isSystemAlert ? '4px' : '0'
                        }}
                      >
                        {log}
                      </div>
                    );
                  })}

                  {isExecuting && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#a855f7', marginTop: '6px' }}>
                      <Activity size={13} style={{ animation: 'spin 1s linear infinite' }} />
                      <span>Executing in isolated sandbox container...</span>
                    </div>
                  )}

                  <div ref={terminalEndRef} />
                </div>

                {/* Terminal Input Form */}
                <form
                  onSubmit={handleCommandSubmit}
                  style={{
                    display: 'flex',
                    borderTop: '1px solid #222226',
                    backgroundColor: '#0c0c0e'
                  }}
                >
                  <div style={{
                    padding: '14px 10px 14px 16px',
                    color: '#22c55e',
                    fontWeight: 700,
                    display: 'flex',
                    alignItems: 'center',
                    userSelect: 'none'
                  }}>
                    <span style={{ color: '#22c55e' }}>user@faws</span>
                    <span style={{ color: '#71717a' }}>:</span>
                    <span style={{ color: '#38bdf8' }}>~</span>
                    <span style={{ color: '#e4e4e7', marginLeft: '4px' }}>$</span>
                  </div>
                  <input
                    ref={inputRef}
                    type="text"
                    value={cmdInput}
                    onChange={(e) => setCmdInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={isExecuting}
                    placeholder={isExecuting ? "Executing command..." : "Type command (e.g. 'binwalk -e firmware.bin', 'ls -la', 'help')..."}
                    autoFocus
                    style={{
                      flex: 1,
                      background: 'transparent',
                      border: 'none',
                      color: '#fff',
                      padding: '14px 16px 14px 0',
                      outline: 'none',
                      fontFamily: 'inherit',
                      fontSize: '13px'
                    }}
                  />
                  <button
                    type="submit"
                    disabled={isExecuting || !cmdInput.trim()}
                    style={{
                      margin: '8px 12px',
                      padding: '0 14px',
                      background: isExecuting || !cmdInput.trim() ? '#18181b' : 'var(--accent-blue)',
                      border: 'none',
                      borderRadius: '6px',
                      color: '#fff',
                      fontSize: '11px',
                      fontWeight: 600,
                      cursor: isExecuting || !cmdInput.trim() ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}
                  >
                    <Play size={10} /> Run
                  </button>
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
