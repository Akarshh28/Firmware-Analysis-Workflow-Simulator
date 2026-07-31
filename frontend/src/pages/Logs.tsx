"use client";

import React, { useState } from "react";
import { Download, RefreshCw, Filter, AlertCircle, Terminal, Info, CheckCircle } from "lucide-react";
import { useProjectStore } from "../store/projectStore";

interface LogItem {
  id?: number;
  tool_name: string;
  log_type: string;
  message: string;
  timestamp: string;
}

/* ─────────── Simulated logs (used when backend is offline) ─────────── */
const SIMULATED_LOGS: LogItem[] = [
  { id: 1, tool_name: "binwalk",    log_type: "SYSTEM", message: "Initializing simulated scan on 'flash.bin'...",               timestamp: "2026-07-28T09:32:01Z" },
  { id: 2, tool_name: "binwalk",    log_type: "STDOUT", message: "DECIMAL       HEXADECIMAL     DESCRIPTION",                     timestamp: "2026-07-28T09:32:01Z" },
  { id: 3, tool_name: "binwalk",    log_type: "STDOUT", message: "0             0x0             TRX firmware header, length: 4194304 bytes", timestamp: "2026-07-28T09:32:02Z" },
  { id: 4, tool_name: "binwalk",    log_type: "STDOUT", message: "512           0x200           LZMA compressed data",            timestamp: "2026-07-28T09:32:02Z" },
  { id: 5, tool_name: "binwalk",    log_type: "STDOUT", message: "1048576       0x100000        Squashfs filesystem v4.0, 492 inodes", timestamp: "2026-07-28T09:32:03Z" },
  { id: 6, tool_name: "binwalk",    log_type: "SYSTEM", message: "Extraction completed successfully.",                            timestamp: "2026-07-28T09:32:04Z" },
  { id: 7, tool_name: "strings",    log_type: "SYSTEM", message: "Starting string extraction on extracted binaries...",           timestamp: "2026-07-28T09:33:01Z" },
  { id: 8, tool_name: "strings",    log_type: "STDOUT", message: "Found: /etc/dlms.conf: DLMS_PASSWORD='SuperSecret123!'",        timestamp: "2026-07-28T09:33:03Z" },
  { id: 9, tool_name: "strings",    log_type: "STDOUT", message: "Found: OBIS code reference: 1.0.1.8.0.255 (Active Energy Import)", timestamp: "2026-07-28T09:33:04Z" },
  { id: 10, tool_name: "strings",   log_type: "STDOUT", message: "Compiler: GCC 9.3.0 arm-linux-gnueabihf",                       timestamp: "2026-07-28T09:33:05Z" },
  { id: 11, tool_name: "entropy",   log_type: "SYSTEM", message: "Generating entropy map for flash.bin...",                       timestamp: "2026-07-28T09:34:01Z" },
  { id: 12, tool_name: "entropy",   log_type: "STDOUT", message: "High entropy region detected: offsets 0x80000–0x100000 (8.0 bits/byte)", timestamp: "2026-07-28T09:34:03Z" },
  { id: 13, tool_name: "entropy",   log_type: "STDOUT", message: "WARNING: Possible AES-128 ECB encrypted payload detected",      timestamp: "2026-07-28T09:34:04Z" },
  { id: 14, tool_name: "ghidra",    log_type: "SYSTEM", message: "Loading dlms_parser into Ghidra analysis engine...",            timestamp: "2026-07-28T09:36:01Z" },
  { id: 15, tool_name: "ghidra",    log_type: "STDOUT", message: "Function 'dlms_auth_verify()' identified at 0x401234",          timestamp: "2026-07-28T09:36:30Z" },
  { id: 16, tool_name: "ghidra",    log_type: "STDOUT", message: "WARNING: Single-byte XOR encryption found with key 0xA5",       timestamp: "2026-07-28T09:37:10Z" },
  { id: 17, tool_name: "ghidra",    log_type: "STDOUT", message: "VULNERABILITY: Unsafe strcpy at dlms_parse_request+0x48",       timestamp: "2026-07-28T09:37:45Z" },
  { id: 18, tool_name: "ghidra",    log_type: "SYSTEM", message: "Decompilation completed. 3 critical issues found.",             timestamp: "2026-07-28T09:38:00Z" },
  { id: 19, tool_name: "trufflehog", log_type: "SYSTEM", message: "Scanning extracted filesystem for secrets...",                 timestamp: "2026-07-28T09:40:00Z" },
  { id: 20, tool_name: "trufflehog", log_type: "STDOUT", message: "SECRET FOUND: /etc/dlms.conf line 12 — DLMS_KEY='4d534d534b4559'", timestamp: "2026-07-28T09:40:15Z" },
  { id: 21, tool_name: "trufflehog", log_type: "STDOUT", message: "SECRET FOUND: /usr/lib/libcosem.so — Hardcoded AES-128 key at offset 0x3a40", timestamp: "2026-07-28T09:40:20Z" },
  { id: 22, tool_name: "trufflehog", log_type: "SYSTEM", message: "Scan complete: 3 secrets detected.",                          timestamp: "2026-07-28T09:40:25Z" },
  { id: 23, tool_name: "wireshark", log_type: "SYSTEM", message: "Dissecting DLMS/COSEM capture file...",                         timestamp: "2026-07-28T09:42:00Z" },
  { id: 24, tool_name: "wireshark", log_type: "STDOUT", message: "Frame 1: DLMS ASSOCIATION-REQUEST — Authentication: NONE (0x00)", timestamp: "2026-07-28T09:42:01Z" },
  { id: 25, tool_name: "wireshark", log_type: "STDOUT", message: "Frame 2: DLMS ASSOCIATION-RESPONSE — Result: ACCEPTED",         timestamp: "2026-07-28T09:42:01Z" },
  { id: 26, tool_name: "wireshark", log_type: "STDOUT", message: "WARNING: Server accepted unauthenticated association",           timestamp: "2026-07-28T09:42:02Z" },
  { id: 27, tool_name: "angr",      log_type: "SYSTEM", message: "Loading binary into angr symbolic engine...",                   timestamp: "2026-07-28T09:45:00Z" },
  { id: 28, tool_name: "angr",      log_type: "STDOUT", message: "Exploring execution paths to find auth bypass at 0x4012bc...",  timestamp: "2026-07-28T09:45:10Z" },
  { id: 29, tool_name: "angr",      log_type: "STDOUT", message: "SUCCESS: Solved constraints — bypass payload: DLMS_COSEM_BYPASS_KEY", timestamp: "2026-07-28T09:45:40Z" },
  { id: 30, tool_name: "afl++",       log_type: "SYSTEM", message: "Starting AFL++ fuzzing campaign (seed corpus: 24 files)...",    timestamp: "2026-07-28T09:50:00Z" },
  { id: 31, tool_name: "afl++",       log_type: "STDOUT", message: "New coverage: +128 edges discovered (mutation: bit-flip)",       timestamp: "2026-07-28T09:52:00Z" },
  { id: 32, tool_name: "afl++",       log_type: "STDOUT", message: "CRASH: Unique crash #1 — Heap overflow at parser+0x210",        timestamp: "2026-07-28T09:55:30Z" },
  { id: 33, tool_name: "afl++",       log_type: "STDOUT", message: "CRASH: Unique crash #3 — Format string in log handler",         timestamp: "2026-07-28T10:01:00Z" },
  { id: 34, tool_name: "scorecard", log_type: "SYSTEM", message: "Aggregating findings and computing CVSS scores...",             timestamp: "2026-07-28T10:30:00Z" },
  { id: 35, tool_name: "scorecard", log_type: "STDOUT", message: "Total: 35 findings — 4 Critical, 9 High, 14 Medium, 8 Low",    timestamp: "2026-07-28T10:30:10Z" },
  { id: 36, tool_name: "scorecard", log_type: "STDOUT", message: "Overall Risk Score: 32/100 (CRITICAL)",                         timestamp: "2026-07-28T10:30:11Z" },
  { id: 37, tool_name: "pdf_report", log_type: "SYSTEM", message: "Generating final security audit report...",                    timestamp: "2026-07-28T10:31:00Z" },
  { id: 38, tool_name: "pdf_report", log_type: "SYSTEM", message: "Report generated: audit_report.pdf (47 pages)",               timestamp: "2026-07-28T10:31:45Z" },
];

const LOG_TYPE_STYLES: Record<string, { color: string; label: string; icon: React.ReactNode }> = {
  SYSTEM:  { color: "var(--accent-blue)",   label: "SYS",  icon: <Info size={11} />         },
  STDOUT:  { color: "var(--text-secondary)", label: "OUT",  icon: <Terminal size={11} />     },
  STDERR:  { color: "var(--accent-red)",    label: "ERR",  icon: <AlertCircle size={11} />   },
  SUCCESS: { color: "var(--accent-green)",  label: "OK",   icon: <CheckCircle size={11} />   },
};

const ALL_TOOLS = Array.from(new Set(SIMULATED_LOGS.map((l) => l.tool_name)));

export const Logs: React.FC = () => {
  const { logs: storeLogs, fetchLogs, activeProject } = useProjectStore();
  const [filter, setFilter] = useState<string>("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [autoScroll, setAutoScroll] = useState(true);
  const [loading, setLoading] = useState(false);
  const logContainerRef = React.useRef<HTMLDivElement>(null);

  const activeLogs = storeLogs.length > 0 ? storeLogs : SIMULATED_LOGS;

  const filteredLogs = activeLogs.filter((log: LogItem) => {
    const matchTool = filter === "all" || log.tool_name === filter;
    const matchType = typeFilter === "all" || log.log_type === typeFilter;
    return matchTool && matchType;
  });

  // Auto-scroll
  React.useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop =
        logContainerRef.current.scrollHeight;
    }
  }, [filteredLogs, autoScroll]);

  // Fetch logs from backend
  const fetchFromBackend = async () => {
    if (!activeProject) return;
    setLoading(true);
    await fetchLogs(activeProject.id);
    setLoading(false);
  };

  // Load logs once when page opens
  React.useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchFromBackend();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeProject]);

  const handleExport = () => {
    const text = filteredLogs
      .map(
        (l) =>
          `[${l.timestamp}] [${l.tool_name}] [${l.log_type}] ${l.message}`
      )
      .join("\n");

    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "faws_execution_logs.txt";
    a.click();
  };

  return (
    <div className="animate-fade-in" style={{ height: "calc(100vh - 116px)", display: "flex", flexDirection: "column", gap: 16 }}>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
        <div style={{ flex: 1 }}>
          <h1 className="page-title" style={{ fontSize: 18 }}>Execution Logs</h1>
          <p className="page-subtitle">
            {activeLogs === SIMULATED_LOGS ? "Showing simulated pipeline run logs" : "Live backend logs"}
            · {filteredLogs.length} entries
          </p>
        </div>

        {/* Controls */}
        <div style={{ display: "flex", gap: 8 }}>
          <button
            className="btn btn-secondary btn-sm"
            onClick={fetchFromBackend}
            disabled={loading}
            title="Fetch logs from backend"
          >
            <RefreshCw size={12} style={{ animation: loading ? "spin 1s linear infinite" : "none" }} />
            {loading ? "Loading…" : "Refresh"}
          </button>
          <button className="btn btn-secondary btn-sm" onClick={handleExport}>
            <Download size={12} /> Export
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card" style={{ padding: "12px 16px", flexShrink: 0 }}>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--text-muted)", fontSize: 12 }}>
            <Filter size={12} /> Filters:
          </div>

          {/* Tool filter */}
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            <button
              onClick={() => setFilter("all")}
              style={{
                padding: "3px 10px",
                borderRadius: 99,
                fontSize: 11,
                border: "1px solid",
                cursor: "pointer",
                background: filter === "all" ? "var(--accent-blue)" : "transparent",
                color: filter === "all" ? "#fff" : "var(--text-secondary)",
                borderColor: filter === "all" ? "var(--accent-blue)" : "var(--border-subtle)",
                fontFamily: "var(--font-mono)",
              }}
            >
              All Tools
            </button>
            {ALL_TOOLS.map((t) => (
              <button
                key={t}
                onClick={() => setFilter(t)}
                style={{
                  padding: "3px 10px",
                  borderRadius: 99,
                  fontSize: 11,
                  border: "1px solid",
                  cursor: "pointer",
                  background: filter === t ? "rgba(99,120,255,0.2)" : "transparent",
                  color: filter === t ? "var(--accent-blue)" : "var(--text-muted)",
                  borderColor: filter === t ? "rgba(99,120,255,0.4)" : "var(--border-subtle)",
                  fontFamily: "var(--font-mono)",
                }}
              >
                {t}
              </button>
            ))}
          </div>

          <div style={{ height: 16, width: 1, background: "var(--border-subtle)" }} />

          {/* Type filter */}
          {["all", "SYSTEM", "STDOUT", "STDERR"].map((t) => (
            <button
              key={t}
              onClick={() => setTypeFilter(t)}
              style={{
                padding: "3px 10px",
                borderRadius: 99,
                fontSize: 11,
                border: "1px solid",
                cursor: "pointer",
                background: typeFilter === t ? "var(--bg-tertiary)" : "transparent",
                color: typeFilter === t ? "var(--text-primary)" : "var(--text-muted)",
                borderColor: typeFilter === t ? "var(--border-dim)" : "var(--border-subtle)",
                fontFamily: "var(--font-mono)",
              }}
            >
              {t}
            </button>
          ))}

          <label style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: "var(--text-secondary)", cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              style={{ accentColor: "var(--accent-blue)" }}
            />
            Auto-scroll
          </label>
        </div>
      </div>

      {/* Terminal Log Output */}
      <div className="terminal" style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        <div className="terminal-header">
          <div className="terminal-dot terminal-dot-red" />
          <div className="terminal-dot terminal-dot-amber" />
          <div className="terminal-dot terminal-dot-green" />
          <span className="terminal-title">FAWS Execution Log — Pipeline Run</span>
          <span style={{ marginLeft: "auto", fontSize: 11, color: "var(--text-muted)" }}>
            {filteredLogs.length} log entries
          </span>
        </div>

        <div
          ref={logContainerRef}
          style={{ flex: 1, overflowY: "auto", padding: "12px 16px", fontFamily: "var(--font-mono)", fontSize: 12 }}
        >
          {filteredLogs.map((log, i) => {
            const typeStyle = LOG_TYPE_STYLES[log.log_type] ?? LOG_TYPE_STYLES["STDOUT"];
            const isError = log.log_type === "STDERR" || log.message.toLowerCase().includes("error") || log.message.toLowerCase().includes("crash");
            const isWarning = log.message.toLowerCase().includes("warning") || log.message.toLowerCase().includes("found");
            const isCritical = log.message.toLowerCase().includes("secret") || log.message.toLowerCase().includes("critical") || log.message.toLowerCase().includes("vulnerability") || log.message.toLowerCase().includes("bypass");

            return (
              <div
                key={log.id || i}
                className="terminal-line"
                style={{
                  display: "flex",
                  gap: 10,
                  padding: "3px 0",
                  borderBottom: "1px solid rgba(255,255,255,0.02)",
                  color: isError
                    ? "var(--accent-red)"
                    : isCritical
                    ? "var(--accent-amber)"
                    : isWarning
                    ? "#fbbf24"
                    : typeStyle.color,
                }}
              >
                {/* Timestamp */}
                <span style={{ color: "var(--text-muted)", flexShrink: 0, fontSize: 10, paddingTop: 1 }}>
                  {new Date(log.timestamp.endsWith("Z") ? log.timestamp : log.timestamp + "Z").toLocaleTimeString()}
                </span>

                {/* Tool */}
                <span
                  style={{
                    color: "var(--accent-cyan)",
                    flexShrink: 0,
                    minWidth: 80,
                    fontWeight: 600,
                    fontSize: 11,
                  }}
                >
                  [{log.tool_name}]
                </span>

                {/* Type badge */}
                <span
                  style={{
                    flexShrink: 0,
                    fontSize: 10,
                    padding: "1px 5px",
                    borderRadius: 3,
                    background: `${typeStyle.color}22`,
                    color: typeStyle.color,
                    display: "flex",
                    alignItems: "center",
                    gap: 3,
                    height: "fit-content",
                    marginTop: 1,
                  }}
                >
                  {typeStyle.icon} {typeStyle.label}
                </span>

                {/* Message */}
                <span style={{ wordBreak: "break-all" }}>{log.message}</span>
              </div>
            );
          })}

          {filteredLogs.length === 0 && (
            <div style={{ color: "var(--text-muted)", textAlign: "center", padding: "32px 0" }}>
              No log entries match the current filter.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Logs;
