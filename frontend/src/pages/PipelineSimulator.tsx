"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Play,
  RotateCcw,
  Upload as UploadIcon,
  ChevronRight,
  ChevronDown,
  Terminal,
  BookOpen,
  Cpu,
  ArrowRight,
  Info,
  CheckCircle,
  XCircle,
  Loader,
  Circle,
} from "lucide-react";
import { usePipelineStore } from "../store/pipelineStore";
import { useProjectStore } from "../store/projectStore";
import { useNotificationStore } from "../store/notificationStore";
import { Upload as UploadComponent } from "./Upload";
import { PageId } from "../components/Sidebar";

/* ─────────── Stage Details Data ─────────── */
const STAGE_DETAILS: Record<
  string,
  {
    purpose: string;
    input: string;
    output: string;
    why: string;
    internalWorking: string;
    commands: { cmd: string; desc: string }[];
    expectedResults: string;
    nextStage: string;
    tags: string[];
    cvssImpact?: string;
  }
> = {
  binwalk: {
    purpose:
      "Scan the raw firmware binary for embedded file signatures, compressed archives, filesystems, and kernel images.",
    input:
      "Raw firmware binary image (flash.bin, firmware.img, *.hex). Typically 2–64 MB.",
    output:
      "Offset table listing all identified file signatures, extracted filesystem directories (SquashFS, cramfs, JFFS2), and any nested binaries.",
    why: "Without extraction we cannot inspect file contents. Most smart meter firmware encrypts/compresses the filesystem — binwalk's signature library can identify and extract these structures even without a key for unencrypted sections.",
    internalWorking:
      "Binwalk reads the binary byte-by-byte, comparing sequences against a database of 'magic byte' signatures (e.g., SquashFS magic 0x73717368, LZMA header 0x5D000080). When a match is found it records the offset. The -e flag then invokes decompressors (sasquatch, lzma, gzip) on those offsets to produce the filesystem tree.",
    commands: [
      { cmd: "binwalk flash.bin",     desc: "Scan and list all signatures" },
      { cmd: "binwalk -e flash.bin",  desc: "Extract detected filesystems" },
      { cmd: "binwalk -Mat flash.bin", desc: "Recursive extraction with entropy" },
      { cmd: "binwalk -E flash.bin",  desc: "Generate entropy graph (detect encryption)" },
    ],
    expectedResults:
      "SquashFS filesystem extracted at offset 0x100000, LZMA kernel at 0x200, bootloader at 0x0. Extraction directory: _flash.bin.extracted/",
    nextStage: "strings (Identification)",
    tags: ["Extraction", "Filesystem", "Signature Scan"],
  },
  strings: {
    purpose:
      "Extract all printable ASCII and Unicode strings from the firmware binary to identify compiler info, function names, hardcoded credentials, and version strings.",
    input: "Raw firmware binary or extracted ELF/ARM binary files.",
    output:
      "Text dump of all strings ≥ 4 characters — reveals DLMS object labels, passwords, IP addresses, URL endpoints, build paths.",
    why: "Smart meter firmware often embeds meter serial numbers, default admin credentials, API endpoints, and DLMS object identifiers directly in the binary. String extraction is the fastest way to identify low-hanging fruit before deep analysis.",
    internalWorking:
      "The 'strings' utility scans the binary for sequences of printable characters (ASCII 0x20–0x7E) above a minimum length threshold. The result is filtered through grep patterns targeting common sensitive patterns: passwords, keys, IP patterns, and DLMS OBIS codes.",
    commands: [
      { cmd: "strings -n 8 flash.bin",         desc: "Extract strings of length ≥ 8" },
      { cmd: "strings flash.bin | grep -i pass", desc: "Search for password strings" },
      { cmd: "strings flash.bin | grep -E '[0-9]+\\.[0-9]+\\.[0-9]+'", desc: "Find OBIS codes" },
      { cmd: "strings flash.bin | grep -i dlms", desc: "Find DLMS-specific labels" },
    ],
    expectedResults:
      "Found: 'admin:changeme', OBIS code '1.0.1.8.0.255', endpoint 'dlms://192.168.1.1:4059', compiler 'GCC 9.3.0 arm-linux-gnueabi'.",
    nextStage: "entropy (Cryptographic Analysis)",
    tags: ["String Extraction", "Credential Hunt", "OSINT"],
  },
  entropy: {
    purpose:
      "Generate an entropy analysis map of the firmware to identify encrypted regions, compressed data, and areas containing random-looking data (keys, encrypted payloads).",
    input: "Raw firmware binary file.",
    output:
      "Entropy graph (0.0–8.0 bits per byte), high-entropy region offsets, and recommendations for further investigation.",
    why: "Encrypted data or strong compression appears as high-entropy (near 8.0 bits/byte) noise. By mapping entropy we can pinpoint where encryption keys and cipher-text payloads are stored — critical for DLMS security layer analysis.",
    internalWorking:
      "Entropy is calculated using Shannon entropy formula: H = -Σ(p(x) * log2(p(x))) over sliding blocks of 1024 bytes. Encrypted AES blocks will show entropy approaching 8.0. Known signatures (LZMA ~7.5, JPEG ~7.9, plaintext ~4.5) help classify regions.",
    commands: [
      { cmd: "binwalk -E flash.bin",        desc: "Generate entropy visualization" },
      { cmd: "binwalk -E -J flash.bin",     desc: "Output entropy as JSON" },
      { cmd: "python3 entropy.py flash.bin", desc: "Custom entropy analysis script" },
    ],
    expectedResults:
      "High entropy region at offsets 0x80000–0x100000 (8.0 bits/byte — AES-128 ECB encrypted payload). Normal entropy at 0x0–0x80000 (SquashFS ~6.8).",
    nextStage: "ghidra (Reverse Engineering)",
    tags: ["Entropy", "Encryption Detection", "Cryptographic"],
  },
  ghidra: {
    purpose:
      "Perform full reverse engineering of the DLMS/COSEM parser binary: decompile ARM assembly to C pseudo-code, recover function signatures, and trace authentication logic.",
    input:
      "Extracted ELF binary from firmware (dlms_parser, libcosem.so, or main_app).",
    output:
      "Decompiled C pseudo-code, control flow graph, function call graph, data cross-references, and annotated disassembly of the DLMS authentication and parsing routines.",
    why: "Smart meter security relies on the correctness of the DLMS/COSEM protocol parser. Ghidra allows us to read the parser logic as C code without source, enabling identification of logic flaws, authentication bypasses, and unsafe pointer operations.",
    internalWorking:
      "Ghidra runs a multi-phase analysis: (1) binary loader identifies ELF sections, (2) disassembler decodes ARM Thumb-2 instructions, (3) decompiler reconstructs high-level C via data flow analysis, (4) auto-analysis identifies known library functions via FunctionID signatures.",
    commands: [
      { cmd: "analyzeHeadless . proj -import dlms_parser -postScript ExportDecompilation.java", desc: "Headless analysis" },
      { cmd: "ghidra-decompile dlms_parser 0x401000", desc: "Decompile function at address" },
    ],
    expectedResults:
      "Function 'dlms_auth_verify()' decompiled — reveals single-byte XOR 'encryption' with hardcoded key 0xA5. Buffer overflow found at dlms_parse_request+0x48.",
    nextStage: "cutter (Static Analysis)",
    tags: ["Decompilation", "Reverse Engineering", "ARM", "DLMS Parser"],
    cvssImpact: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H — Score: 9.8 CRITICAL",
  },
  cutter: {
    purpose:
      "Visual static analysis of firmware binary using Cutter (Radare2 frontend) — graph-based CFG navigation, cross-references, and XREFS to locate entry points.",
    input: "Firmware ELF binary or raw binary with entry point override.",
    output:
      "Control flow graphs (CFG), call graphs, function list, cross-reference maps, and annotated disassembly view.",
    why: "Cutter provides an interactive graph-based view that makes it easier than Ghidra for quickly navigating complex branching logic in the DLMS state machine, which involves deeply nested switch-case structures.",
    internalWorking:
      "Uses Radare2 analysis engine under the hood. r2 performs automatic function discovery via linear sweep and recursive descent. CFG is built by tracing all conditional branches (BEQ, BNE, BGT etc.) and call instructions from the entry point.",
    commands: [
      { cmd: "r2 -A dlms_binary",           desc: "Open and auto-analyze binary" },
      { cmd: "r2 -q -e anal.depth=4 -c 'aaa; pdf @ main' dlms_binary", desc: "Print main function" },
      { cmd: "cutter dlms_binary",           desc: "Launch Cutter GUI" },
    ],
    expectedResults:
      "DLMS request handler at 0x4012a0, authentication check function at 0x401380, unsafe strcpy call at 0x401450 (buffer overflow candidate).",
    nextStage: "trufflehog (Secret Detection)",
    tags: ["Static Analysis", "CFG", "Radare2", "Call Graph"],
  },
  trufflehog: {
    purpose:
      "Scan extracted filesystem and all embedded files for hardcoded secrets: API keys, passwords, private keys, DLMS security keys, and authentication tokens.",
    input:
      "Extracted firmware filesystem directory (_flash.bin.extracted/) and all text/config files.",
    output:
      "List of discovered secrets with their file path, line number, secret type, entropy score, and verification status.",
    why: "Smart meters often ship with hardcoded defaults that operators never change. Finding these secrets is essential: a hardcoded DLMS association password allows any attacker on the network to read meter data or execute commands.",
    internalWorking:
      "TruffleHog v3 uses a regex + entropy detector approach. It scans every file for patterns matching 700+ known secret formats (AWS keys, GitHub tokens, private PEM blocks), AND flags any high-entropy string (Shannon entropy > 4.5) as a potential secret, even if unrecognized.",
    commands: [
      { cmd: "trufflehog filesystem ./_flash.bin.extracted/", desc: "Scan extracted filesystem" },
      { cmd: "trufflehog filesystem . --include-paths='*.conf,*.sh,*.json'", desc: "Scan configs only" },
      { cmd: "trufflehog filesystem . --json",      desc: "Output results as JSON" },
    ],
    expectedResults:
      "Found: /etc/dlms.conf: DLMS_PASSWORD='SuperSecret123!', /usr/lib/libcosem.so: hardcoded AES key 0x4d534d534b4559...",
    nextStage: "wireshark (Protocol Analysis)",
    tags: ["Secret Detection", "Hardcoded Credentials", "Entropy"],
    cvssImpact: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N — Score: 7.5 HIGH",
  },
  wireshark: {
    purpose:
      "Capture and dissect DLMS/COSEM network traffic to analyze the protocol handshake, authentication frames, and identify protocol-level vulnerabilities.",
    input:
      "PCAP file of DLMS/COSEM traffic over HDLC or TCP/IP (port 4059).",
    output:
      "Protocol dissection report: authentication frames, cipher negotiation details, replay attack vectors, and unencrypted command sequences.",
    why: "The DLMS/COSEM protocol specification (IEC 62056) allows several cipher suites, including unauthenticated variants. Real-world meters often negotiate down to no-security or low-security modes — only packet analysis reveals this misconfiguration.",
    internalWorking:
      "Wireshark uses LUA-based DLMS dissector plugins to parse the binary HDLC/APDU framing. The ASSOCIATION-REQUEST and ASSOCIATION-RESPONSE frames reveal authentication mechanism: NONE (0x00), LOW (0x01), or HIGH (0x02). High-security mode uses AES-GCM-128.",
    commands: [
      { cmd: "tshark -r dlms_capture.pcap -Y dlms",           desc: "Filter DLMS packets" },
      { cmd: "tshark -r dlms_capture.pcap -T json -Y dlms",   desc: "Export as JSON" },
      { cmd: "tshark -r dlms_capture.pcap -e dlms.auth_value -T fields", desc: "Extract auth values" },
    ],
    expectedResults:
      "Association Request contains authentication-mechanism: NONE. Server accepts connection without credentials. 1200 meter readings exposed without encryption.",
    nextStage: "angr (Symbolic Execution)",
    tags: ["Protocol Analysis", "DLMS", "PCAP", "Network Security"],
    cvssImpact: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N — Score: 8.2 HIGH",
  },
  angr: {
    purpose:
      "Perform automated symbolic execution on the DLMS parser binary to discover execution paths that bypass authentication checks, trigger buffer overflows, or reach dangerous code paths.",
    input:
      "Stripped ELF binary (DLMS parser executable) with known entry point and target/avoid addresses from Ghidra analysis.",
    output:
      "Concrete input payloads that trigger specific execution paths (e.g., authentication bypass), discovered vulnerabilities, and memory constraint violations.",
    why: "Manual analysis via Ghidra can identify suspicious code, but generating the exact input sequence that triggers a vulnerability is extremely difficult manually. Angr automates this by treating inputs as symbolic variables and solving the constraints mathematically.",
    internalWorking:
      "Angr uses Z3 SMT solver for constraint solving. Each branch instruction becomes a constraint: if (input[3] == 0xA5) go_left else go_right. By accumulating these constraints along a chosen path and asking Z3 to solve them, we get the exact byte sequence that follows that path.",
    commands: [
      { cmd: "python3 angr_find_bypass.py dlms_parser 0x401234 0x401380", desc: "Find path from start to bypass" },
      { cmd: "python3 angr_overflow.py dlms_parser 0x401450",             desc: "Trigger buffer overflow" },
    ],
    expectedResults:
      "Bypass key discovered: 0x444C4D535F434F53454D5F4259504153535F4B45590000 (ASCII: DLMS_COSEM_BYPASS_KEY). Buffer overflow triggered at offset 64 with payload 'A' * 64 + 0xdeadbeef.",
    nextStage: "afl (Fuzzing)",
    tags: ["Symbolic Execution", "Z3 Solver", "Path Exploration", "Exploit Generation"],
    cvssImpact: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H — Score: 9.8 CRITICAL",
  },
  "afl++": {
    purpose:
      "Coverage-guided fuzzing of the DLMS request parser to discover crashes, hangs, and unexpected behaviors through automated mutation-based testing.",
    input:
      "Seed corpus of valid DLMS/COSEM request packets (APDU frames) and the compiled DLMS parser binary with AFL instrumentation.",
    output:
      "Crash samples, hang samples, and edge-case inputs that cause undefined behavior — each saved as a reproducible test case.",
    why: "Fuzzing complements symbolic execution by discovering bugs that are difficult to reason about statically (e.g., off-by-one errors, integer overflows deep inside parsing loops). AFL can generate millions of test inputs automatically.",
    internalWorking:
      "AFL instruments the binary at compile time (or via QEMU for black-box) to track code coverage via a bitmap of branch edges. New inputs that increase coverage are kept in the queue; others are discarded. Inputs are mutated via bit-flips, byte swaps, dictionary injection, and splicing.",
    commands: [
      { cmd: "afl-fuzz -i seeds/ -o findings/ -- ./dlms_parser @@", desc: "Start fuzzing campaign" },
      { cmd: "afl-tmin -i crash.bin -o min.bin -- ./dlms_parser @@", desc: "Minimize crash sample" },
      { cmd: "afl-showmap -o cov.map -- ./dlms_parser crash.bin",    desc: "Show coverage map" },
    ],
    expectedResults:
      "11 unique crashes found after 2 hours: 3 heap overflows, 2 null pointer dereferences, 1 format string, 5 assertion failures. Coverage: 68% of parser code paths.",
    nextStage: "scorecard (Risk Assessment)",
    tags: ["Fuzzing", "Crash Detection", "Coverage-Guided", "AFL++"],
  },
  scorecard: {
    purpose:
      "Aggregate all findings from the pipeline into a structured risk assessment with CVSS scores, CWE classifications, and DLMS-specific impact analysis.",
    input:
      "All tool outputs: Ghidra findings, TruffleHog secrets, Wireshark protocol issues, Angr exploit payloads, AFL crashes.",
    output:
      "CVSS v3.1 scored vulnerability report, CWE-mapped findings, DLMS security compliance check against IEC 62056-62, and risk prioritization matrix.",
    why: "Raw tool outputs need to be translated into actionable security findings with standardized severity scores (CVSS) so that engineers and management can prioritize remediation efforts and understand business impact.",
    internalWorking:
      "The scorecard engine maps each finding type to CVSS v3.1 metrics (Attack Vector, Complexity, Privileges Required, Impact) using rule templates. CWE IDs are assigned from a knowledge base. DLMS compliance checks verify cipher suite, authentication level, and data integrity requirements from IEC 62056.",
    commands: [
      { cmd: "python3 scorecard.py --findings findings.json --output report.json", desc: "Generate risk scorecard" },
      { cmd: "python3 scorecard.py --cvss-calc AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H", desc: "Calculate CVSS score" },
    ],
    expectedResults:
      "35 findings total: 4 Critical (CVSS ≥ 9.0), 9 High (7.0–8.9), 14 Medium (4.0–6.9), 8 Low (<4.0). Overall risk score: 32/100 (CRITICAL).",
    nextStage: "pdf_report (Report Generation)",
    tags: ["CVSS", "CWE", "Risk Assessment", "IEC 62056"],
  },
  pdf_report: {
    purpose:
      "Generate a professional security audit report combining all analysis findings, executive summary, technical details, and remediation recommendations.",
    input: "Risk scorecard JSON, all tool output artifacts, analysis session metadata.",
    output:
      "Formatted PDF security audit report with executive summary, methodology, findings table, CVSS scores, proof-of-concept details, and remediation guidance.",
    why: "The final deliverable must communicate security findings clearly to multiple audiences: technical engineers (need PoC details), managers (need risk summary), and compliance teams (need standards mapping). A structured report achieves this.",
    internalWorking:
      "The report generator uses Jinja2 templates to combine all JSON artifacts into an HTML structure, which is then rendered to PDF via Weasyprint or ReportLab. Finding tables are sorted by CVSS score, and PoC code is syntax-highlighted.",
    commands: [
      { cmd: "python3 generate_report.py --template audit --output audit_report.pdf", desc: "Generate PDF report" },
      { cmd: "python3 generate_report.py --format html --findings report.json", desc: "Preview as HTML" },
    ],
    expectedResults:
      "audit_report.pdf: 47 pages. Sections: Executive Summary, Methodology, 35 Findings (with PoC), DLMS Compliance Matrix, Remediation Roadmap, Appendix (Tool Commands).",
    nextStage: "— End of Pipeline —",
    tags: ["Report Generation", "PDF", "Executive Summary", "Remediation"],
  },
  upload: {
    purpose: "Upload the firmware binary to begin the analysis pipeline.",
    input: "Firmware binary file (.bin, .hex, .elf, .img)",
    output: "Stored firmware file ready for analysis pipeline",
    why: "The pipeline requires a firmware binary as its starting artifact. The upload stage validates the file format and stores it securely.",
    internalWorking: "File is validated by extension and magic bytes, then stored in the artifacts directory. A new pipeline session is created and initialized.",
    commands: [
      { cmd: "curl -F 'firmware=@flash.bin' http://localhost:8000/api/projects/1/upload", desc: "Upload via API" },
    ],
    expectedResults: "File stored at artifacts/flash.bin. Pipeline session initialized with status IDLE.",
    nextStage: "binwalk (Extraction)",
    tags: ["Upload", "Validation", "Setup"],
  },
};

/* ─────────── Status helpers ─────────── */
const statusIcon = (status: string, size = 14) => {
  switch (status) {
    case "completed": return <CheckCircle size={size} color="var(--accent-green)" />;
    case "running":   return <Loader size={size} color="var(--accent-amber)" style={{ animation: "spin 1s linear infinite" }} />;
    case "failed":    return <XCircle size={size} color="var(--accent-red)" />;
    case "queued":    return <Circle size={size} color="var(--accent-blue)" />;
    default:          return <Circle size={size} color="var(--text-muted)" />;
  }
};

const statusClass = (status: string) =>
  `badge badge-${status === "completed" ? "success" : status === "running" ? "running" : status === "failed" ? "failed" : status === "queued" ? "queued" : "idle"}`;

/* ─────────── Full pipeline stage list ─────────── */
const ALL_STAGES = [
  { stage: "Firmware Upload",       tool: "upload",     icon: "📤", order: 1 },
  { stage: "Identification",        tool: "strings",    icon: "🔍", order: 2 },
  { stage: "Extraction",            tool: "binwalk",    icon: "📦", order: 3 },
  { stage: "Static Analysis",       tool: "cutter",     icon: "🔬", order: 4 },
  { stage: "Reverse Engineering",   tool: "ghidra",     icon: "🧩", order: 5 },
  { stage: "Secret Detection",      tool: "trufflehog", icon: "🔑", order: 6 },
  { stage: "Cryptographic Analysis",tool: "entropy",    icon: "📊", order: 7 },
  { stage: "Protocol Analysis",     tool: "wireshark",  icon: "🌐", order: 8 },
  { stage: "Fuzzing",               tool: "afl++",      icon: "⚡", order: 9 },
  { stage: "Symbolic Execution",    tool: "angr",       icon: "🧮", order: 10 },
  { stage: "Risk Assessment",       tool: "scorecard",  icon: "📋", order: 11 },
  { stage: "Report Generation",     tool: "pdf_report", icon: "📄", order: 12 },
];

export default function PipelineSimulator({ onNavigate }: { onNavigate?: (page: PageId) => void }) {
  const { pipeline, fetchPipeline, resetPipelineBackend } = usePipelineStore();
  const { activeProject, activePipeline, clearActiveProject, startPipeline, fetchPipelineStatus } = useProjectStore();

  const [selectedTool, setSelectedTool] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "commands" | "expected">("overview");
  const [running, setRunning] = useState(false);

  const prevStatusRef = useRef<string | undefined>(activePipeline?.status);

  useEffect(() => {
    if (activeProject) {
        fetchPipeline(activeProject.id);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeProject]);

  useEffect(() => {
    const currentStatus = activePipeline?.status;
    const prevStatus = prevStatusRef.current;
    
    if (currentStatus === "COMPLETED" && prevStatus === "RUNNING") {
      useNotificationStore.getState().addNotification({
        title: "Analysis Complete",
        message: "Firmware analysis pipeline has successfully finished.",
        type: "success",
        action: { label: "View Report", pageId: "reports" }
      });

      if (onNavigate) {
        const t = setTimeout(() => {
          onNavigate("reports");
        }, 1500);
        
        prevStatusRef.current = currentStatus;
        return () => clearTimeout(t);
      }
    } else if (currentStatus === "FAILED" && prevStatus === "RUNNING") {
      useNotificationStore.getState().addNotification({
        title: "Analysis Failed",
        message: "The firmware analysis pipeline encountered an error.",
        type: "error",
        action: { label: "Open Simulator", pageId: "pipeline" }
      });
    }
    
    prevStatusRef.current = currentStatus;
  }, [activePipeline?.status, onNavigate]);

  const nodeMap = Object.fromEntries(pipeline.nodes.map((n) => [n.toolName, n]));

  const handleRun = async () => {
    if (!activeProject) return;
    setRunning(true);
    await resetPipelineBackend(activeProject.id);
    await startPipeline(activeProject.id);
    await fetchPipeline(activeProject.id);
    setRunning(false);
  };

  const handleReset = () => {
    if (activeProject) clearActiveProject();
    setSelectedTool(null);
  };

  const details = selectedTool ? STAGE_DETAILS[selectedTool] : null;
  const selectedStage = ALL_STAGES.find((s) => s.tool === selectedTool);

  const canRun = !!activeProject && activePipeline?.status !== "WAITING_UPLOAD" && activePipeline?.status !== "RUNNING" && !running;
  const isPipelineRunning = running || activePipeline?.status === "RUNNING";

  return (
    <div className="animate-fade-in" style={{ display: "flex", gap: 24, height: "calc(100vh - 116px)" }}>

      {/* Left Column: Upload + Stage List */}
      <div style={{ width: 300, display: "flex", flexDirection: "column", gap: 16 }}>

        {/* Upload Component if not running/completed */}
        {!isPipelineRunning && activePipeline?.status !== "COMPLETED" && activePipeline?.status !== "FAILED" && (
           <div className="card" style={{ padding: 16, overflow: "hidden", flexShrink: 0 }}>
             <h3 style={{ fontSize: 14, color: "var(--text-muted)", marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6, fontWeight: 600 }}>
               <UploadIcon size={14} /> Firmware Setup
             </h3>
             <UploadComponent />
           </div>
        )}

        {/* Start / Reset Actions */}
        <div style={{ display: "flex", gap: 8 }}>
            <button
              className="btn btn-primary"
              style={{ flex: 1, justifyContent: "center", opacity: canRun ? 1 : 0.5, cursor: canRun ? "pointer" : "not-allowed" }}
              disabled={!canRun}
              onClick={handleRun}
            >
              {isPipelineRunning ? (
                <>
                  <Loader size={14} className="animate-spin" /> Running...
                </>
              ) : (
                <>
                  <Play size={14} /> Run Pipeline
                </>
              )}
            </button>
            <button
              className="btn btn-secondary"
              onClick={handleReset}
              disabled={isPipelineRunning || !activeProject}
              style={{ opacity: (isPipelineRunning || !activeProject) ? 0.5 : 1, padding: "8px 16px" }}
            >
              Reset
            </button>
        </div>

        {/* Stage List */}
        <div
          className="card"
          style={{ padding: 0, flex: 1, overflow: "hidden", display: "flex", flexDirection: "column" }}
        >
          <div style={{ padding: "14px 18px", borderBottom: "1px solid var(--border-subtle)", flexShrink: 0 }}>
            <div className="card-title" style={{ marginBottom: 0 }}>
              <Cpu size={13} /> Pipeline Stages
            </div>
          </div>
          <div style={{ overflow: "auto", flex: 1, padding: "8px 8px" }}>
            {ALL_STAGES.map((s, i) => {
              const node = nodeMap[s.tool];
              const status = node?.status ?? "idle";
              const progress = node?.progress ?? 0;
              const isSelected = selectedTool === s.tool;

              return (
                <div key={s.tool}>
                  <div
                    className={`stage-card status-${status} ${isSelected ? "selected" : ""}`}
                    style={{ padding: "10px 14px", marginBottom: 0 }}
                    onClick={() => setSelectedTool(s.tool)}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ fontSize: 14 }}>{s.icon}</span>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div
                          style={{
                            fontSize: 12,
                            fontWeight: 600,
                            color: isSelected ? "var(--accent-blue)" : "var(--text-primary)",
                            whiteSpace: "nowrap",
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                          }}
                        >
                          {s.stage}
                        </div>
                        <div style={{ fontSize: 10, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
                          {s.tool}
                        </div>
                      </div>
                      {statusIcon(status, 13)}
                    </div>
                    {status === "running" && (
                      <div className="progress-track" style={{ marginTop: 6 }}>
                        <div
                          className="progress-bar progress-bar-amber"
                          style={{ width: `${progress}%` }}
                        />
                      </div>
                    )}
                    {status === "completed" && (
                      <div className="progress-track" style={{ marginTop: 6 }}>
                        <div className="progress-bar progress-bar-green" style={{ width: "100%" }} />
                      </div>
                    )}
                  </div>
                  {i < ALL_STAGES.length - 1 && (
                    <div className="connector-arrow" style={{ padding: "2px 0", height: 16 }}>
                      <ChevronDown size={10} />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Right Column: Stage Detail */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
        {!selectedTool ? (
          <div
            className="card"
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: 48, marginBottom: 16 }}>🔬</div>
            <div style={{ fontSize: 18, fontWeight: 700, color: "var(--text-primary)", marginBottom: 8 }}>
              Select a Pipeline Stage
            </div>
            <div style={{ fontSize: 14, color: "var(--text-secondary)", maxWidth: 380 }}>
              Click any stage card on the left to see its complete documentation — purpose, internal workings, commands, and expected outputs.
            </div>
          </div>
        ) : (
          <div className="card" style={{ padding: 0, overflow: "hidden", flex: 1, display: "flex", flexDirection: "column" }}>
            {/* Detail Header */}
            <div
              style={{
                padding: "18px 24px",
                borderBottom: "1px solid var(--border-subtle)",
                background: "rgba(99,120,255,0.04)",
                flexShrink: 0,
              }}
            >
              <div style={{ display: "flex", alignItems: "flex-start", gap: 14 }}>
                <div
                  style={{
                    width: 48,
                    height: 48,
                    borderRadius: "var(--radius-md)",
                    background: "rgba(99,120,255,0.12)",
                    border: "1px solid rgba(99,120,255,0.25)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 22,
                    flexShrink: 0,
                  }}
                >
                  {selectedStage?.icon}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
                    <h2 style={{ fontSize: 18, fontWeight: 800, color: "var(--text-primary)" }}>
                      {selectedStage?.stage}
                    </h2>
                    <span
                      style={{
                        fontSize: 12,
                        fontFamily: "var(--font-mono)",
                        color: "var(--accent-cyan)",
                        background: "rgba(34,211,238,0.1)",
                        padding: "2px 8px",
                        borderRadius: 99,
                        border: "1px solid rgba(34,211,238,0.2)",
                      }}
                    >
                      {selectedTool}
                    </span>
                    <span
                      className={statusClass(nodeMap[selectedTool]?.status ?? "idle")}
                    >
                      {nodeMap[selectedTool]?.status?.toUpperCase() ?? "IDLE"}
                    </span>
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 8 }}>
                    {details?.tags.map((t) => (
                      <span
                        key={t}
                        style={{
                          fontSize: 10,
                          padding: "2px 8px",
                          borderRadius: 99,
                          background: "var(--bg-tertiary)",
                          color: "var(--text-secondary)",
                          border: "1px solid var(--border-subtle)",
                        }}
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
                <div style={{ textAlign: "right", fontSize: 12, color: "var(--text-muted)", flexShrink: 0 }}>
                  Stage {selectedStage?.order} / {ALL_STAGES.length}
                </div>
              </div>
            </div>

            {/* Tabs */}
            <div className="tabs" style={{ padding: "0 24px", flexShrink: 0, background: "var(--bg-primary)" }}>
              <button
                className={`tab-btn ${activeTab === "overview" ? "active" : ""}`}
                onClick={() => setActiveTab("overview")}
              >
                <BookOpen size={13} /> Overview
              </button>
              <button
                className={`tab-btn ${activeTab === "commands" ? "active" : ""}`}
                onClick={() => setActiveTab("commands")}
              >
                <Terminal size={13} /> Commands
              </button>
              <button
                className={`tab-btn ${activeTab === "expected" ? "active" : ""}`}
                onClick={() => setActiveTab("expected")}
              >
                <Info size={13} /> Expected Output
              </button>
            </div>

            {/* Tab Content */}
            <div style={{ flex: 1, overflowY: "auto", padding: 24 }}>
              {activeTab === "overview" && details && (
                <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
                  {/* Purpose */}
                  <section>
                    <h4 style={{ color: "var(--accent-cyan)", fontSize: 12, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>
                      🎯 Purpose
                    </h4>
                    <p style={{ color: "var(--text-primary)", lineHeight: 1.7, fontSize: 14 }}>
                      {details.purpose}
                    </p>
                  </section>

                  <div className="grid-2">
                    {/* Input */}
                    <section
                      style={{
                        padding: 16,
                        background: "rgba(34,211,238,0.05)",
                        border: "1px solid rgba(34,211,238,0.15)",
                        borderRadius: "var(--radius-md)",
                      }}
                    >
                      <h4 style={{ color: "var(--accent-cyan)", fontSize: 11, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>
                        📥 Input
                      </h4>
                      <p style={{ color: "var(--text-secondary)", fontSize: 13, lineHeight: 1.6 }}>
                        {details.input}
                      </p>
                    </section>

                    {/* Output */}
                    <section
                      style={{
                        padding: 16,
                        background: "rgba(168,85,247,0.05)",
                        border: "1px solid rgba(168,85,247,0.15)",
                        borderRadius: "var(--radius-md)",
                      }}
                    >
                      <h4 style={{ color: "var(--accent-purple)", fontSize: 11, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>
                        📤 Output
                      </h4>
                      <p style={{ color: "var(--text-secondary)", fontSize: 13, lineHeight: 1.6 }}>
                        {details.output}
                      </p>
                    </section>
                  </div>

                  {/* Why Required */}
                  <section
                    style={{
                      padding: 16,
                      background: "rgba(245,158,11,0.05)",
                      border: "1px solid rgba(245,158,11,0.2)",
                      borderRadius: "var(--radius-md)",
                    }}
                  >
                    <h4 style={{ color: "var(--accent-amber)", fontSize: 11, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>
                      ❓ Why This Stage Is Required
                    </h4>
                    <p style={{ color: "var(--text-secondary)", fontSize: 13, lineHeight: 1.7 }}>
                      {details.why}
                    </p>
                  </section>

                  {/* Internal Working */}
                  <section>
                    <h4 style={{ color: "var(--accent-purple)", fontSize: 12, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>
                      ⚙️ Internal Working
                    </h4>
                    <p style={{ color: "var(--text-primary)", fontSize: 13, lineHeight: 1.8 }}>
                      {details.internalWorking}
                    </p>
                  </section>

                  {/* CVSS */}
                  {details.cvssImpact && (
                    <section
                      style={{
                        padding: 14,
                        background: "rgba(239,68,68,0.06)",
                        border: "1px solid rgba(239,68,68,0.2)",
                        borderRadius: "var(--radius-md)",
                        fontFamily: "var(--font-mono)",
                        fontSize: 12,
                        color: "var(--text-code)",
                      }}
                    >
                      🔴 {details.cvssImpact}
                    </section>
                  )}

                  {/* Next Stage */}
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
                      padding: "10px 14px",
                      background: "rgba(99,120,255,0.06)",
                      border: "1px solid rgba(99,120,255,0.15)",
                      borderRadius: "var(--radius-sm)",
                      fontSize: 13,
                      color: "var(--text-secondary)",
                    }}
                  >
                    <ArrowRight size={14} color="var(--accent-blue)" />
                    <span>
                      Next Stage: <strong style={{ color: "var(--accent-blue)" }}>{details.nextStage}</strong>
                    </span>
                  </div>
                </div>
              )}

              {activeTab === "commands" && details && (
                <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                  <p style={{ color: "var(--text-secondary)", fontSize: 13 }}>
                    Click any command to copy it to your clipboard.
                  </p>
                  {details.commands.map((c, i) => (
                    <div
                      key={i}
                      className="card"
                      style={{ padding: 0, overflow: "hidden", cursor: "pointer" }}
                      onClick={() => navigator.clipboard?.writeText(c.cmd)}
                    >
                      <div className="code-block" style={{ borderRadius: 0, border: "none", borderBottom: "1px solid var(--border-subtle)" }}>
                        $ {c.cmd}
                      </div>
                      <div style={{ padding: "10px 16px", fontSize: 12, color: "var(--text-secondary)" }}>
                        {c.desc}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === "expected" && details && (
                <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                  <div className="terminal">
                    <div className="terminal-header">
                      <div className="terminal-dot terminal-dot-red" />
                      <div className="terminal-dot terminal-dot-amber" />
                      <div className="terminal-dot terminal-dot-green" />
                      <span className="terminal-title">Expected Output — {selectedTool}</span>
                    </div>
                    <div className="terminal-body">
                      <div className="terminal-line log-system">$ {selectedTool} --run [target]</div>
                      <div className="terminal-line log-system">FAWS Analysis Engine v1.0.0 · Stage: {selectedStage?.stage}</div>
                      <div className="terminal-line" style={{ color: "var(--text-muted)" }}>─────────────────────────────────────────</div>
                      <div className="terminal-line log-stdout">{details.expectedResults}</div>
                      <div className="terminal-line" style={{ color: "var(--text-muted)" }}>─────────────────────────────────────────</div>
                      <div className="terminal-line log-success">✓ Stage completed successfully.</div>
                    </div>
                  </div>
                  <div
                    style={{
                      padding: 16,
                      background: "rgba(34,197,94,0.05)",
                      border: "1px solid rgba(34,197,94,0.15)",
                      borderRadius: "var(--radius-md)",
                      fontSize: 13,
                      color: "var(--text-secondary)",
                    }}
                  >
                    <div style={{ color: "var(--accent-green)", fontWeight: 600, marginBottom: 6 }}>
                      ✓ Expected Results Summary
                    </div>
                    {details.expectedResults}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
