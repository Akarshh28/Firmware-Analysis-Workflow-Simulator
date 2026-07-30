"use client";

import React, { useState } from "react";
import {
  BookOpen,
  Search,
  ChevronRight,
  ExternalLink,
  Shield,
  Cpu,
  Network,
  Code2,
  FileText,
  Zap,
  Lock,
} from "lucide-react";

/* ─────────── Knowledge Base data ─────────── */
interface KBArticle {
  id: string;
  title: string;
  category: string;
  icon: React.ReactNode;
  tags: string[];
  content: { heading: string; body: string }[];
  references: { label: string; url: string }[];
}

const KB_ARTICLES: KBArticle[] = [
  {
    id: "dlms-cosem-overview",
    title: "DLMS/COSEM Protocol Overview",
    category: "Protocol",
    icon: <Network size={16} />,
    tags: ["DLMS", "COSEM", "IEC 62056", "Smart Grid"],
    content: [
      {
        heading: "What is DLMS/COSEM?",
        body: "DLMS (Device Language Message Specification) / COSEM (Companion Specification for Energy Metering) is the global standard for data exchange with energy meters. It is defined in the IEC 62056 series of standards and is used worldwide in smart meter deployments for AMI (Advanced Metering Infrastructure).",
      },
      {
        heading: "Protocol Architecture",
        body: "DLMS/COSEM operates on a client-server model. The meter (server) exposes COSEM objects addressable by OBIS codes. Clients (e.g., head-end systems) connect via a transport layer (HDLC over serial, TCP/IP, or GPRS) and use APDU (Application Protocol Data Units) to read/write meter data.",
      },
      {
        heading: "Security Levels",
        body: "DLMS supports three security modes:\n• None (0x00): No authentication or encryption\n• Low (0x01): Password-based authentication only (plaintext)\n• High (0x02): AES-128 based encryption and authentication (GMAC/GCM)\n\nMany deployed meters use None or Low security, creating serious vulnerabilities.",
      },
      {
        heading: "OBIS Codes",
        body: "OBIS (Object Identification System) codes are 6-octet identifiers for meter data objects. Example: 1.0.1.8.0.255 = Active Energy Import Tariff 1. Attackers who know OBIS codes can read arbitrary meter registers if authentication is bypassed.",
      },
    ],
    references: [
      { label: "IEC 62056-21 Standard", url: "https://www.iec.ch/dyn/www/f?p=103:38:0::::FSP_ORG_ID:1251" },
      { label: "DLMS/COSEM User Association", url: "https://www.dlms.com/dlms-cosem/overview" },
    ],
  },
  {
    id: "firmware-analysis-methodology",
    title: "Firmware Analysis Methodology",
    category: "Methodology",
    icon: <Shield size={16} />,
    tags: ["Methodology", "Static Analysis", "Dynamic Analysis", "Reverse Engineering"],
    content: [
      {
        heading: "Phase 1: Firmware Acquisition",
        body: "Firmware can be obtained via: (1) Official vendor download portals, (2) Physical chip extraction (JTAG, UART, SPI flash dump), (3) Network capture during OTA updates, or (4) Binwalk extraction from update packages. For DLMS meters, the firmware often ships as a flat binary or ELF file.",
      },
      {
        heading: "Phase 2: Filesystem Extraction",
        body: "Use Binwalk to identify and extract compressed filesystems (SquashFS, JFFS2, cramfs). This reveals the entire meter OS: init scripts, config files, shared libraries (libcosem.so), and the main application binary.",
      },
      {
        heading: "Phase 3: Static Analysis",
        body: "Perform static analysis WITHOUT executing the binary: (1) String extraction to find hardcoded credentials and OBIS codes, (2) Entropy analysis to detect encrypted regions, (3) Disassembly via Ghidra/Cutter to understand code logic.",
      },
      {
        heading: "Phase 4: Dynamic Analysis",
        body: "Execute the binary in a controlled environment: (1) QEMU for ARM emulation, (2) Symbolic execution via angr to discover input-dependent vulnerabilities, (3) AFL fuzzing to discover crashes, (4) Network traffic analysis via Wireshark.",
      },
      {
        heading: "Phase 5: Reporting",
        body: "Document all findings with CVSS scores, CWE classifications, and PoC (Proof of Concept) reproduction steps. Map findings to the DLMS security model and IEC 62056 compliance requirements.",
      },
    ],
    references: [
      { label: "OWASP Firmware Security Guide", url: "https://owasp.org/www-project-embedded-application-security/" },
      { label: "NIST SP 800-193 Platform Firmware Resiliency", url: "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-193.pdf" },
    ],
  },
  {
    id: "binwalk-deep-dive",
    title: "Binwalk: Deep Dive",
    category: "Tools",
    icon: <Cpu size={16} />,
    tags: ["binwalk", "Extraction", "SquashFS", "Magic Bytes"],
    content: [
      {
        heading: "How Binwalk Works",
        body: "Binwalk uses a signature database (magic bytes) to identify file types embedded within a binary at arbitrary offsets. It scans the binary byte-by-byte, comparing against signatures like: SquashFS (0x73717368), gzip (0x1f8b), LZMA (0x5d000000), ELF (0x7f454c46).",
      },
      {
        heading: "Entropy Analysis",
        body: "Binwalk's -E flag generates an entropy graph. High entropy (>7.5 bits/byte) indicates encryption or random data. Low entropy (<5.0 bits/byte) indicates plaintext or repetitive data. This helps identify encrypted sections that cannot be easily extracted.",
      },
      {
        heading: "Smart Meter Filesystem Structures",
        body: "Most ARM-based smart meters use SquashFS (read-only, compressed) for the root filesystem. The typical layout after extraction:\n/bin/, /sbin/ — system utilities\n/etc/ — configuration files (dlms.conf, network.conf)\n/usr/lib/ — shared libraries (libcosem.so)\n/usr/sbin/ — main application binary",
      },
      {
        heading: "Common Extraction Failures",
        body: "1. sasquatch not installed → cannot extract non-standard SquashFS\n2. Jefferson not installed → cannot extract JFFS2\n3. Encrypted partition → binwalk cannot extract (need key first)\n4. Custom bootloader → may need offset override (-l flag)",
      },
    ],
    references: [
      { label: "Binwalk GitHub", url: "https://github.com/ReFirmLabs/binwalk" },
      { label: "SquashFS-Tools", url: "https://github.com/plougher/squashfs-tools" },
    ],
  },
  {
    id: "symbolic-execution-angr",
    title: "Symbolic Execution with angr",
    category: "Tools",
    icon: <Code2 size={16} />,
    tags: ["angr", "Z3", "Symbolic Execution", "Path Exploration"],
    content: [
      {
        heading: "Symbolic Execution Theory",
        body: "Instead of executing a program with concrete values, symbolic execution uses symbolic (algebraic) variables to represent all possible inputs simultaneously. Each branch condition becomes a constraint. By collecting all constraints along a path and solving them with an SMT solver (Z3), we find exact inputs that take that path.",
      },
      {
        heading: "angr Architecture",
        body: "angr consists of: (1) CLE loader — loads binaries and their dependencies, (2) VEX IR — lifts machine code to intermediate representation, (3) Claripy — symbolic expression engine, (4) SimManager — manages exploration of execution states, (5) Z3 — SMT solver for constraint solving.",
      },
      {
        heading: "Applying angr to DLMS Parsers",
        body: "For DLMS binary analysis: (1) Identify authentication check function via Ghidra analysis, (2) Set entry_state at the function start, (3) Use simgr.explore(find=bypass_addr, avoid=failure_addr) to find path to authentication bypass, (4) Extract concrete input from found state's stdin buffer.",
      },
      {
        heading: "State Explosion Problem",
        body: "Complex loops and cryptographic functions create millions of execution states, making symbolic execution infeasible. Mitigations: (1) angr.SIM_PROCEDURES to hook standard library functions (memcmp, strcmp), (2) Veritesting to merge states at loop headers, (3) Limit exploration depth with step limits.",
      },
    ],
    references: [
      { label: "angr Documentation", url: "https://docs.angr.io/" },
      { label: "angr Tutorial Papers", url: "https://github.com/angr/angr-doc" },
    ],
  },
  {
    id: "vulnerability-classes",
    title: "Smart Meter Vulnerability Classes",
    category: "Security",
    icon: <Lock size={16} />,
    tags: ["Vulnerabilities", "CWE", "CVSS", "Smart Meter Security"],
    content: [
      {
        heading: "CWE-798: Hardcoded Credentials",
        body: "CVSS Base: 7.5–9.8 HIGH/CRITICAL. Smart meters frequently ship with hardcoded DLMS passwords, AES keys, or administrative passwords that are identical across the entire deployed fleet. A single disclosure compromises all devices simultaneously.",
      },
      {
        heading: "CWE-120: Buffer Copy Without Checking Size",
        body: "CVSS Base: 9.8 CRITICAL. Unsafe C functions (strcpy, sprintf, gets) in the DLMS packet parser can be overflowed with malformed APDU packets. This can lead to remote code execution on the meter — a critical smart grid threat.",
      },
      {
        heading: "CWE-326: Inadequate Encryption Strength",
        body: "CVSS Base: 7.5 HIGH. Using AES-128 in ECB mode (versus GCM) means identical plaintext blocks produce identical ciphertext, leaking data patterns. Some meters use XOR 'encryption' with a single-byte key.",
      },
      {
        heading: "CWE-287: Improper Authentication",
        body: "CVSS Base: 8.2 HIGH. DLMS association without proper HLS (High Level Security) challenge-response allows network-adjacent attackers to read meter data, inject commands, or reset energy counters — potential for energy theft at scale.",
      },
      {
        heading: "CWE-134: Format String Vulnerability",
        body: "CVSS Base: 8.1 HIGH. If meter firmware logs DLMS request data using printf(user_input) instead of printf('%s', user_input), attackers can read arbitrary memory, crash the meter, or potentially achieve RCE via format string exploits.",
      },
    ],
    references: [
      { label: "CWE Database", url: "https://cwe.mitre.org" },
      { label: "CVSS v3.1 Calculator", url: "https://www.first.org/cvss/calculator/3.1" },
      { label: "ICS-CERT Smart Grid Advisories", url: "https://www.cisa.gov/ics-cert" },
    ],
  },
  {
    id: "tools-reference",
    title: "Tool Reference Card",
    category: "Reference",
    icon: <FileText size={16} />,
    tags: ["Tools", "Quick Reference", "Commands"],
    content: [
      {
        heading: "Extraction & Identification",
        body: "• binwalk -e firmware.bin — Extract firmware components\n• file firmware.bin — Identify binary format\n• strings -n 8 firmware.bin — Extract printable strings\n• xxd firmware.bin | head -20 — Hex dump header",
      },
      {
        heading: "Reverse Engineering",
        body: "• ghidra (GUI) — Full decompilation\n• r2 -A binary; aaa; pdf @ main — Radare2 analysis\n• cutter binary — Cutter visual analysis\n• objdump -d binary — ARM disassembly\n• readelf -a binary — ELF sections",
      },
      {
        heading: "Secret Detection",
        body: "• trufflehog filesystem ./extracted/ — Scan for secrets\n• grep -rn 'password\\|passwd\\|key\\|secret' ./etc/ — Manual scan\n• entropy.py binary — Custom entropy check",
      },
      {
        heading: "Dynamic Analysis",
        body: "• afl-fuzz -i seeds/ -o out/ -- ./binary @@ — Fuzzing\n• python3 angr_script.py binary — Symbolic execution\n• qemu-arm-static -L ./sysroot ./binary — ARM emulation",
      },
      {
        heading: "Network Analysis",
        body: "• tshark -i eth0 -Y dlms — Live DLMS capture\n• tshark -r capture.pcap -T json — Parse PCAP\n• nmap -p 4059 --script dlms-discover 192.168.1.0/24 — Scan",
      },
    ],
    references: [
      { label: "Ghidra Scripting Guide", url: "https://ghidra.re" },
      { label: "AFL++ Manual", url: "https://aflplus.plus/docs/" },
    ],
  },
  {
    id: "c3ihub-context",
    title: "Project Context: C3iHub IIT Kanpur",
    category: "Project",
    icon: <Zap size={16} />,
    tags: ["C3iHub", "IIT Kanpur", "Project Context", "FAWS"],
    content: [
      {
        heading: "About C3iHub",
        body: "C3iHub (Center of Excellence in Cyber Security) is a National Technology Innovation Hub established at IIT Kanpur under the National Mission on Interdisciplinary Cyber-Physical Systems (NM-ICPS) by DST, Government of India. It focuses on cybersecurity research for critical infrastructure including smart grids, IoT, and industrial control systems.",
      },
      {
        heading: "DLMS/COSEM Smart Meter Security Research",
        body: "The research project aims to analyze firmware security of DLMS/COSEM protocol-based smart electricity meters deployed under India's RDSS (Revamped Distribution Sector Scheme). Millions of smart prepaid meters are being deployed — securing them is critical to national energy infrastructure.",
      },
      {
        heading: "FAWS: Digital Twin Approach",
        body: "Since physical smart meter hardware and actual firmware binaries require vendor partnerships and NDAs, FAWS (Firmware Analysis Workflow Simulator) was designed as a digital twin of the full analysis pipeline. It allows researchers to learn, practice, and document the complete methodology without physical hardware.",
      },
      {
        heading: "Expected Deliverables",
        body: "1. Complete firmware analysis methodology report\n2. Vulnerability assessment framework for DLMS/COSEM meters\n3. Tool configuration guides and automation scripts\n4. Security recommendation report for meter vendors\n5. This FAWS digital twin application for future researchers",
      },
    ],
    references: [
      { label: "C3iHub Official Website", url: "https://c3ihub.org" },
      { label: "IIT Kanpur Cybersecurity", url: "https://iitk.ac.in" },
      { label: "India RDSS Smart Meter Program", url: "https://www.recindia.nic.in/rdss" },
    ],
  },
];

const CATEGORIES = Array.from(new Set(KB_ARTICLES.map((a) => a.category)));

export const KnowledgeBase: React.FC = () => {
  const [selectedArticle, setSelectedArticle] = useState<KBArticle | null>(KB_ARTICLES[0]);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState<string>("All");

  const filtered = KB_ARTICLES.filter((a) => {
    const matchCat = activeCategory === "All" || a.category === activeCategory;
    const matchSearch =
      !searchQuery ||
      a.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchCat && matchSearch;
  });

  return (
    <div className="animate-fade-in" style={{ display: "flex", gap: 24, height: "calc(100vh - 116px)" }}>

      {/* Left: Article List */}
      <div style={{ width: 300, display: "flex", flexDirection: "column", gap: 12 }}>
        {/* Search */}
        <div style={{ position: "relative" }}>
          <Search size={14} style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
          <input
            className="input-field"
            style={{ paddingLeft: 36 }}
            placeholder="Search knowledge base…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* Category Filters */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
          {["All", ...CATEGORIES].map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              style={{
                padding: "4px 10px",
                borderRadius: 99,
                fontSize: 11,
                fontWeight: 600,
                border: "1px solid",
                cursor: "pointer",
                background: activeCategory === cat ? "var(--accent-blue)" : "transparent",
                color: activeCategory === cat ? "var(--text-primary)" : "var(--text-secondary)",
                borderColor: activeCategory === cat ? "var(--accent-blue)" : "var(--border-subtle)",
                fontFamily: "var(--font-sans)",
              }}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Article List */}
        <div
          className="card"
          style={{ padding: 0, flex: 1, overflow: "auto" }}
        >
          {filtered.length === 0 ? (
            <div style={{ padding: 20, color: "var(--text-muted)", fontSize: 13, textAlign: "center" }}>
              No articles found.
            </div>
          ) : (
            filtered.map((article) => (
              <div
                key={article.id}
                onClick={() => setSelectedArticle(article)}
                style={{
                  padding: "12px 16px",
                  borderBottom: "1px solid var(--border-subtle)",
                  cursor: "pointer",
                  background: selectedArticle?.id === article.id ? "rgba(99,120,255,0.08)" : "transparent",
                  borderLeft: selectedArticle?.id === article.id ? "3px solid var(--accent-blue)" : "3px solid transparent",
                  transition: "all 0.15s",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                  <span style={{ color: "var(--accent-blue)" }}>{article.icon}</span>
                  <span
                    style={{
                      fontSize: 10,
                      padding: "1px 6px",
                      borderRadius: 99,
                      background: "var(--bg-tertiary)",
                      color: "var(--text-muted)",
                      border: "1px solid var(--border-subtle)",
                    }}
                  >
                    {article.category}
                  </span>
                </div>
                <div
                  style={{
                    fontSize: 13,
                    fontWeight: 600,
                    color: selectedArticle?.id === article.id ? "var(--accent-blue)" : "var(--text-primary)",
                    lineHeight: 1.4,
                  }}
                >
                  {article.title}
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginTop: 6 }}>
                  {article.tags.slice(0, 2).map((t) => (
                    <span key={t} style={{ fontSize: 9, color: "var(--text-muted)" }}>
                      #{t}
                    </span>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Right: Article Content */}
      <div className="card" style={{ flex: 1, overflow: "auto", display: "flex", flexDirection: "column" }}>
        {!selectedArticle ? (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", flex: 1, color: "var(--text-muted)", fontSize: 14 }}>
            Select an article to read
          </div>
        ) : (
          <div>
            {/* Header */}
            <div style={{ display: "flex", alignItems: "flex-start", gap: 14, marginBottom: 24 }}>
              <div
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: "var(--radius-md)",
                  background: "rgba(99,120,255,0.12)",
                  border: "1px solid rgba(99,120,255,0.25)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "var(--accent-blue)",
                  flexShrink: 0,
                }}
              >
                {selectedArticle.icon}
              </div>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", marginBottom: 6 }}>
                  <span
                    style={{
                      fontSize: 11,
                      padding: "2px 8px",
                      borderRadius: 99,
                      background: "rgba(99,120,255,0.15)",
                      color: "var(--accent-blue)",
                      border: "1px solid rgba(99,120,255,0.3)",
                    }}
                  >
                    {selectedArticle.category}
                  </span>
                  {selectedArticle.tags.map((t) => (
                    <span key={t} style={{ fontSize: 10, color: "var(--text-muted)" }}>#{t}</span>
                  ))}
                </div>
                <h2 style={{ fontSize: 20, fontWeight: 800, color: "var(--text-primary)", lineHeight: 1.3 }}>
                  {selectedArticle.title}
                </h2>
              </div>
            </div>

            {/* Sections */}
            <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
              {selectedArticle.content.map((section, i) => (
                <div key={i}>
                  <h3
                    style={{
                      fontSize: 14,
                      fontWeight: 700,
                      color: "var(--accent-cyan)",
                      marginBottom: 10,
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
                    }}
                  >
                    <ChevronRight size={14} />
                    {section.heading}
                  </h3>
                  <div
                    style={{
                      fontSize: 14,
                      color: "var(--text-secondary)",
                      lineHeight: 1.8,
                      whiteSpace: "pre-line",
                      paddingLeft: 22,
                    }}
                  >
                    {section.body}
                  </div>
                </div>
              ))}
            </div>

            {/* References */}
            {selectedArticle.references.length > 0 && (
              <div style={{ marginTop: 28 }}>
                <div className="divider" />
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    marginBottom: 12,
                    color: "var(--text-muted)",
                    fontSize: 12,
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: "0.06em",
                  }}
                >
                  <BookOpen size={13} /> References & Further Reading
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {selectedArticle.references.map((r, i) => (
                    <a
                      key={i}
                      href={r.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                        padding: "8px 12px",
                        background: "var(--bg-secondary)",
                        border: "1px solid var(--border-subtle)",
                        borderRadius: "var(--radius-sm)",
                        fontSize: 13,
                        color: "var(--accent-blue)",
                        textDecoration: "none",
                        transition: "all 0.15s",
                      }}
                      onMouseEnter={(e) => {
                        (e.currentTarget as HTMLAnchorElement).style.borderColor = "rgba(99,120,255,0.4)";
                        (e.currentTarget as HTMLAnchorElement).style.background = "rgba(99,120,255,0.08)";
                      }}
                      onMouseLeave={(e) => {
                        (e.currentTarget as HTMLAnchorElement).style.borderColor = "var(--border-subtle)";
                        (e.currentTarget as HTMLAnchorElement).style.background = "var(--bg-secondary)";
                      }}
                    >
                      <ExternalLink size={12} />
                      {r.label}
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default KnowledgeBase;
