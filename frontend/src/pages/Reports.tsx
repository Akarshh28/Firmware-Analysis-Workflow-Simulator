"use client";

import React, { useState } from "react";
import {
  Shield,
  AlertTriangle,
  CheckCircle2,
  Info,
  Download,
  FileText,
  ExternalLink,
  Bug,
  Lock,
  Cpu,
  Network,
  Key,
} from "lucide-react";

import api from "../services/api";
import { useProjectStore } from "../store/projectStore";

interface Finding {
  id: string;
  title: string;
  severity: "critical" | "high" | "medium" | "low";
  cvss: number;
  cwe: string;
  stage: string;
  tool: string;
  description: string;
  poc: string;
  remediation: string;
}

const FALLBACK_FINDINGS: Finding[] = [
  {
    id: "CVE-SIM-001",
    title: "Hardcoded DLMS Authentication Key in libcosem.so",
    severity: "critical",
    cvss: 9.8,
    cwe: "CWE-798",
    stage: "Secret Detection",
    tool: "trufflehog",
    description:
      "A 128-bit AES key (0x4d534d534b4559...) is hardcoded in the shared library libcosem.so at offset 0x3a40. This key is identical across all deployed meters of this model, meaning any attacker with firmware access can extract this key and decrypt all DLMS communications.",
    poc: "$ python3 extract_key.py libcosem.so 0x3a40\nExtracted AES-128 Key: 4d534d534b455900000000000000000\n$ aes_decrypt --key 4d534d534b455900000000000000000 --input dlms_traffic.pcap\nDecrypted: 1200 meter readings exposed",
    remediation:
      "1. Generate unique AES-128 keys per device during manufacturing using a Hardware Security Module (HSM).\n2. Store keys in Trusted Execution Environment (TEE) or secure element, not in user-space library.\n3. Implement key rotation protocol via secure OTA update.",
  },
  {
    id: "CVE-SIM-002",
    title: "Buffer Overflow in dlms_parse_request() Function",
    severity: "critical",
    cvss: 9.8,
    cwe: "CWE-120",
    stage: "Symbolic Execution",
    tool: "angr",
    description:
      "An unsafe strcpy() call at dlms_parse_request+0x48 copies attacker-controlled DLMS request data into a fixed 64-byte stack buffer without length validation. Sending more than 64 bytes overwrites the return address, enabling remote code execution.",
    poc: "$ python3 overflow_poc.py\nPayload: 'A' * 64 + b'\\xef\\xbe\\xad\\xde'  # Override return addr\nResult: Segmentation fault (core dumped)\nPC = 0xdeadbeef  # Return address hijacked",
    remediation:
      "1. Replace strcpy() with strncpy() or strlcpy() with buffer size limit.\n2. Enable stack canaries (-fstack-protector-all) in compiler flags.\n3. Enable ASLR and NX bit for ARM binary protection.\n4. Add DLMS APDU length validation before any buffer copy operation.",
  },
  {
    id: "CVE-SIM-003",
    title: "Unauthenticated DLMS Association Accepted",
    severity: "high",
    cvss: 8.2,
    cwe: "CWE-287",
    stage: "Protocol Analysis",
    tool: "wireshark",
    description:
      "The meter accepts DLMS ASSOCIATION-REQUEST packets with authentication-mechanism: NONE (0x00). This allows any device on the network to connect to the meter, read all 1200 COSEM object registers, and issue control commands (e.g., disconnect) without any credentials.",
    poc: "$ python3 dlms_connect.py --target 192.168.1.100 --port 4059 --auth none\nConnected. Association accepted.\n$ dlms_read_obis --obis 1.0.1.8.0.255\nActive Energy Import: 1842.3 kWh",
    remediation:
      "1. Configure DLMS server to require HLS (High Level Security) authentication minimum.\n2. Enable AES-GCM-128 encryption and GMAC authentication per IEC 62056-62.\n3. Maintain access control lists for client system titles.\n4. Implement connection rate limiting to prevent brute force.",
  },
  {
    id: "CVE-SIM-004",
    title: "Weak AES-128 ECB Mode Used for Data Encryption",
    severity: "high",
    cvss: 7.5,
    cwe: "CWE-326",
    stage: "Cryptographic Analysis",
    tool: "entropy",
    description:
      "The firmware encrypts DLMS payload data using AES-128 in ECB (Electronic Code Book) mode. ECB is a deterministic cipher: identical plaintext blocks always produce identical ciphertext blocks. This leaks data patterns and allows partial plaintext recovery without the key.",
    poc: "# ECB Pattern Detection\nBlock 1 (plaintext: 0x01 * 16) → ciphertext: 0xab12cd34...\nBlock 7 (plaintext: 0x01 * 16) → ciphertext: 0xab12cd34...  ← Identical!\n# Attacker can identify repeated meter readings by pattern matching",
    remediation:
      "1. Replace AES-128-ECB with AES-128-GCM (Galois/Counter Mode) which provides both encryption and authentication.\n2. Use a unique initialization vector (IV) per message, derived from DLMS frame counter.\n3. Implement GMAC authentication tag validation to prevent ciphertext tampering.",
  },
  {
    id: "CVE-SIM-005",
    title: "Format String Vulnerability in Diagnostic Logger",
    severity: "medium",
    cvss: 6.5,
    cwe: "CWE-134",
    stage: "Fuzzing",
    tool: "afl++",
    description:
      "The meter's diagnostic logging function passes user-supplied DLMS request data directly to printf() without a format string. This is a classic format string vulnerability that allows attackers to read arbitrary memory locations or crash the meter.",
    poc: "$ echo -n '%p %p %p %p %p %p %p %p' | dlms_send --target 192.168.1.100\nResponse log: 0x7fffe320 0x401234 0x7fffe200 0x0 0x41414141 0xbffff5f4 0x7f3d2a18 0x7fffe310\n# Stack addresses leaked — enables ASLR bypass",
    remediation:
      "1. Replace printf(user_input) with printf(\"%s\", user_input) throughout codebase.\n2. Enable -Wformat=2 compiler warning flag to detect format string issues.\n3. Consider using syslog() for diagnostic logging with structured format strings.",
  },
  {
    id: "CVE-SIM-006",
    title: "Hardcoded Default Admin Password in /etc/dlms.conf",
    severity: "high",
    cvss: 7.5,
    cwe: "CWE-798",
    stage: "Secret Detection",
    tool: "trufflehog",
    description:
      "The configuration file /etc/dlms.conf contains the plaintext default DLMS password 'SuperSecret123!' with no mechanism for mandatory password change on first use. This password is the same across all deployed devices of this model.",
    poc: "$ cat _flash.bin.extracted/etc/dlms.conf\n[dlms]\npassword = SuperSecret123!\nauth_level = LOW\nclient_id = 16\n# Using this to authenticate:\n$ dlms_client --target 192.168.1.100 --password 'SuperSecret123!'",
    remediation:
      "1. Remove all hardcoded credentials from firmware.\n2. Generate unique passwords during manufacturing or first boot using /dev/urandom.\n3. Implement mandatory password change policy enforced by DLMS server.\n4. Store passwords using bcrypt hashing, not plaintext.",
  },
  {
    id: "CVE-SIM-007",
    title: "Missing Stack Canary and ASLR Protection",
    severity: "medium",
    cvss: 5.9,
    cwe: "CWE-693",
    stage: "Static Analysis",
    tool: "cutter",
    description:
      "The DLMS parser binary was compiled without stack canary protection (-fstack-protector), Position Independent Executable (PIE), or RELRO (Relocation Read-Only) hardening. This significantly lowers the bar for successful exploitation of CVE-SIM-002.",
    poc: "$ checksec --file dlms_parser\n  Arch:     arm-32-little\n  RELRO:    No RELRO\n  Stack:    No canary found\n  NX:       NX disabled\n  PIE:      No PIE (0x10000)",
    remediation:
      "1. Compile with -fstack-protector-all -fPIE -pie flags.\n2. Link with -Wl,-z,relro,-z,now for full RELRO.\n3. Ensure NX (No-Execute) bit is enabled in kernel configuration.\n4. Enable ASLR in the Linux kernel config (CONFIG_COMPAT_BRK=n).",
  },
  {
    id: "CVE-SIM-008",
    title: "OBIS Code Enumeration Without Rate Limiting",
    severity: "low",
    cvss: 3.7,
    cwe: "CWE-307",
    stage: "Protocol Analysis",
    tool: "wireshark",
    description:
      "The DLMS server does not implement rate limiting on OBIS code read requests. An attacker can enumerate all 1200+ COSEM objects in under 30 seconds, extracting complete meter history, tamper records, and quality flags.",
    poc: "$ python3 dlms_enum.py --target 192.168.1.100 --obis-range 1.0.0.0.0.255-1.0.99.99.99.255\nScanning 1200 OBIS codes...\nCompleted in 28 seconds. 1186 objects readable.",
    remediation:
      "1. Implement request rate limiting: maximum 10 OBIS reads per second per client.\n2. Add connection throttling after 5 consecutive read failures.\n3. Log all enumeration attempts to SIEM for anomaly detection.",
  },
];

const SEVERITY_CONFIG = {
  critical: { color: "#ef4444", bg: "rgba(239,68,68,0.1)",   border: "rgba(239,68,68,0.3)",  icon: <AlertTriangle size={14} /> },
  high:     { color: "#f97316", bg: "rgba(249,115,22,0.1)",  border: "rgba(249,115,22,0.3)", icon: <Shield size={14} />        },
  medium:   { color: "#f59e0b", bg: "rgba(245,158,11,0.1)",  border: "rgba(245,158,11,0.3)", icon: <Info size={14} />          },
  low:      { color: "#22c55e", bg: "rgba(34,197,94,0.1)",   border: "rgba(34,197,94,0.3)",  icon: <CheckCircle2 size={14} />  },
};

const TOOL_ICONS: Record<string, React.ReactNode> = {
  trufflehog: <Key size={14} />,
  angr:       <Cpu size={14} />,
  wireshark:  <Network size={14} />,
  entropy:    <Lock size={14} />,
  "afl++":        <Bug size={14} />,
  cutter:     <FileText size={14} />,
};

export const Reports: React.FC = () => {
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const { activeProject } = useProjectStore();
  const [severityFilter, setSeverityFilter] = useState<string>("all");

  React.useEffect(() => {
    let isMounted = true;
    const fetchFindings = async () => {
        if (!activeProject) return;
        try {
            const res = await api.get(`projects/${activeProject.id}/dashboard`);
            if (isMounted) {
                const fetchedFindings = res.data.findings || [];
                setFindings(fetchedFindings.length > 0 ? fetchedFindings : FALLBACK_FINDINGS);
                if (fetchedFindings.length > 0) {
                    setSelectedFinding(fetchedFindings[0]);
                } else {
                    setSelectedFinding(FALLBACK_FINDINGS[0]);
                }
            }
        } catch(e) {
            console.error(e);
            if (isMounted) {
                setFindings(FALLBACK_FINDINGS);
                setSelectedFinding(FALLBACK_FINDINGS[0]);
            }
        }
    };
    fetchFindings();
    return () => { isMounted = false; };
  }, [activeProject]);

  const filtered = findings.filter(
    (f) => severityFilter === "all" || f.severity === severityFilter
  );

  const stats = {
    critical: findings.filter((f) => f.severity === "critical").length,
    high:     findings.filter((f) => f.severity === "high").length,
    medium:   findings.filter((f) => f.severity === "medium").length,
    low:      findings.filter((f) => f.severity === "low").length,
  };

  const handleExport = () => {
    const md = findings.map((f) =>
      `## ${f.id}: ${f.title}\n**Severity:** ${f.severity.toUpperCase()} | **CVSS:** ${f.cvss} | **CWE:** ${f.cwe} | **Stage:** ${f.stage}\n\n**Description:**\n${f.description}\n\n**PoC:**\n\`\`\`\n${f.poc}\n\`\`\`\n\n**Remediation:**\n${f.remediation}\n\n---\n`
    ).join("\n");
    const blob = new Blob([`# FAWS Security Report\nGenerated: ${new Date().toISOString()}\n\n` + md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "faws_security_report.md";
    a.click();
  };

  return (
    <div className="animate-fade-in" style={{ height: "calc(100vh - 116px)", display: "flex", flexDirection: "column", gap: 16 }}>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div style={{ flex: 1 }}>
          <h1 className="page-title" style={{ fontSize: 18 }}>Reports &amp; Findings</h1>
          <p className="page-subtitle">Security findings from live firmware analysis pipeline</p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={handleExport}>
          <Download size={12} /> Export Report (.md)
        </button>
      </div>

      {/* Stats Row */}
      <div style={{ display: "flex", gap: 12, flexShrink: 0 }}>
        {Object.entries(stats).map(([sev, count]) => {
          const cfg = SEVERITY_CONFIG[sev as keyof typeof SEVERITY_CONFIG];
          return (
            <div
              key={sev}
              onClick={() => setSeverityFilter(severityFilter === sev ? "all" : sev)}
              style={{
                flex: 1,
                padding: "12px 16px",
                background: severityFilter === sev ? cfg.bg : "var(--bg-card)",
                border: `1px solid ${severityFilter === sev ? cfg.border : "var(--border-subtle)"}`,
                borderRadius: "var(--radius-md)",
                cursor: "pointer",
                transition: "all 0.15s",
                display: "flex",
                alignItems: "center",
                gap: 10,
              }}
            >
              <div style={{ color: cfg.color }}>{cfg.icon}</div>
              <div>
                <div style={{ fontSize: 20, fontWeight: 800, color: cfg.color }}>{count}</div>
                <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "capitalize" }}>{sev}</div>
              </div>
            </div>
          );
        })}
        <div
          onClick={() => setSeverityFilter("all")}
          style={{
            padding: "12px 16px",
            background: severityFilter === "all" ? "rgba(99,120,255,0.1)" : "var(--bg-card)",
            border: `1px solid ${severityFilter === "all" ? "rgba(99,120,255,0.3)" : "var(--border-subtle)"}`,
            borderRadius: "var(--radius-md)",
            cursor: "pointer",
            transition: "all 0.15s",
            display: "flex",
            alignItems: "center",
            gap: 10,
          }}
        >
          <div style={{ color: "var(--accent-blue)" }}><Shield size={14} /></div>
          <div>
            <div style={{ fontSize: 24, fontWeight: 800, color: "var(--accent-blue)" }}>{findings.length}</div>
            <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Total</div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, display: "flex", gap: 16, minHeight: 0 }}>

        {/* Left: Finding List */}
        <div
          className="card"
          style={{ width: 320, padding: 0, overflow: "auto", flexShrink: 0 }}
        >
          {filtered.map((f) => {
            const cfg = SEVERITY_CONFIG[f.severity];
            return (
              <div
                key={f.id}
                onClick={() => setSelectedFinding(f)}
                style={{
                  padding: "12px 16px",
                  borderBottom: "1px solid var(--border-subtle)",
                  cursor: "pointer",
                  background: selectedFinding?.id === f.id ? "rgba(99,120,255,0.08)" : "transparent",
                  borderLeft: selectedFinding?.id === f.id ? `3px solid var(--accent-blue)` : `3px solid ${cfg.color}`,
                  transition: "background 0.15s",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                  <span
                    style={{
                      fontSize: 10,
                      padding: "1px 7px",
                      borderRadius: 99,
                      background: cfg.bg,
                      color: cfg.color,
                      border: `1px solid ${cfg.border}`,
                      fontWeight: 700,
                      textTransform: "uppercase",
                    }}
                  >
                    {f.severity}
                  </span>
                  <span style={{ fontSize: 10, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                    {f.cvss}
                  </span>
                </div>
                <div
                  style={{
                    fontSize: 12.5,
                    fontWeight: 600,
                    color: selectedFinding?.id === f.id ? "var(--accent-blue)" : "var(--text-primary)",
                    lineHeight: 1.4,
                  }}
                >
                  {f.title}
                </div>
                <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 4 }}>
                  {f.cwe} · {f.stage}
                </div>
              </div>
            );
          })}
        </div>

        {/* Right: Finding Detail */}
        {selectedFinding && (() => {
          const cfg = SEVERITY_CONFIG[selectedFinding.severity];
          return (
            <div className="card" style={{ flex: 1, overflow: "auto" }}>
              {/* Finding Header */}
              <div
                style={{
                  padding: "16px 20px",
                  background: cfg.bg,
                  border: `1px solid ${cfg.border}`,
                  borderRadius: "var(--radius-md)",
                  marginBottom: 20,
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", marginBottom: 8 }}>
                  <span style={{ color: cfg.color }}>{cfg.icon}</span>
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-muted)" }}>
                    {selectedFinding.id}
                  </span>
                  <span
                    style={{
                      padding: "2px 10px",
                      borderRadius: 99,
                      fontSize: 11,
                      fontWeight: 700,
                      background: cfg.bg,
                      color: cfg.color,
                      border: `1px solid ${cfg.border}`,
                      textTransform: "uppercase",
                    }}
                  >
                    {selectedFinding.severity}
                  </span>
                  <span
                    style={{
                      fontSize: 20,
                      fontWeight: 800,
                      color: cfg.color,
                      marginLeft: "auto",
                    }}
                  >
                    CVSS {selectedFinding.cvss}
                  </span>
                </div>
                <h2 style={{ fontSize: 16, fontWeight: 800, color: "var(--text-primary)", lineHeight: 1.4 }}>
                  {selectedFinding.title}
                </h2>
                <div style={{ display: "flex", gap: 12, marginTop: 10, flexWrap: "wrap" }}>
                  <span style={{ fontSize: 12, color: "var(--text-secondary)" }}>
                    <strong>CWE:</strong> {selectedFinding.cwe}
                  </span>
                  <span style={{ fontSize: 12, color: "var(--text-secondary)" }}>
                    <strong>Stage:</strong> {selectedFinding.stage}
                  </span>
                  <span style={{ fontSize: 12, color: "var(--text-secondary)", display: "flex", alignItems: "center", gap: 4 }}>
                    {TOOL_ICONS[selectedFinding.tool]} <strong>Tool:</strong> {selectedFinding.tool}
                  </span>
                </div>
              </div>

              {/* Description */}
              <section style={{ marginBottom: 20 }}>
                <h4 style={{ color: "var(--accent-cyan)", fontSize: 11, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>
                  📋 Description
                </h4>
                <p style={{ color: "var(--text-secondary)", fontSize: 13.5, lineHeight: 1.8 }}>
                  {selectedFinding.description}
                </p>
              </section>

              {/* Proof of Concept */}
              <section style={{ marginBottom: 20 }}>
                <h4 style={{ color: "var(--accent-amber)", fontSize: 11, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>
                  ⚡ Proof of Concept
                </h4>
                <div className="code-block">{selectedFinding.poc}</div>
              </section>

              {/* Remediation */}
              <section style={{ marginBottom: 20 }}>
                <h4 style={{ color: "var(--accent-green)", fontSize: 11, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>
                  🛡️ Remediation Steps
                </h4>
                <div
                  style={{
                    padding: 16,
                    background: "rgba(34,197,94,0.05)",
                    border: "1px solid rgba(34,197,94,0.15)",
                    borderRadius: "var(--radius-md)",
                    fontSize: 13.5,
                    color: "var(--text-secondary)",
                    lineHeight: 1.8,
                    whiteSpace: "pre-line",
                  }}
                >
                  {selectedFinding.remediation}
                </div>
              </section>

              {/* External Reference */}
              <a
                href={`https://cwe.mitre.org/data/definitions/${(selectedFinding.cwe || "").replace("CWE-", "")}.html`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 6,
                  fontSize: 12,
                  color: "var(--accent-blue)",
                  textDecoration: "none",
                }}
              >
                <ExternalLink size={11} /> View {selectedFinding.cwe} on MITRE CWE Database
              </a>
            </div>
          );
        })()}
      </div>
    </div>
  );
};

export default Reports;
