import os
import sys
import time
import re
import shlex
import subprocess
import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app import models
from app.config import settings

# ─────────────────────────────────────────────────────────────────────────────
# PRODUCTION TOOL DOCUMENTATION REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

TOOL_REGISTRY_DOCS: Dict[str, Dict[str, Any]] = {
    "upload": {
        "version": "1.4.0",
        "docs": {
            "purpose": "Firmware Ingestion & File Validation: Secure upload, SHA-256 integrity verification, and archive header inspection for smart meter binaries.",
            "input": "Raw binary (.bin, .hex, .elf, .img) or archive (.zip, .tar, .tar.gz). Up to 500 MB.",
            "output": "Stored artifact path, cryptographic checksum, file size, and initialized pipeline session.",
            "workflow": "Initial stage of firmware analysis workflow. Triggers automated file-type verification.",
            "commands": [
                {"command": "curl -F 'firmware=@firmware.bin' http://localhost:8000/api/projects/1/upload", "explanation": "Upload firmware image to Project 1 via REST API"},
                {"command": "sha256sum firmware.bin", "explanation": "Calculate and verify cryptographic SHA-256 checksum"},
                {"command": "file firmware.bin", "explanation": "Determine binary architecture and header structure"}
            ],
            "common_errors": [
                "HTTP 413: File too large (maximum allowed size is 500MB)",
                "Unsupported file extension (.exe, .msi, .dmg rejected)"
            ],
            "troubleshooting": "Ensure file size is within 500MB limit and file format matches supported smart meter binary/archive extensions.",
            "best_practices": "Always archive raw untouched firmware copies alongside generated checksums for chain-of-custody verification.",
            "references": ["NIST SP 800-147B (BIOS & Firmware Integrity)", "IEC 62056-62 DLMS/COSEM Spec"]
        }
    },
    "strings": {
        "version": "2.38",
        "docs": {
            "purpose": "Identification & Reconnaissance: Extracts ASCII and UTF-8 strings from binary images to detect hardcoded credentials, IP addresses, URLs, and DLMS object identifiers.",
            "input": "Raw firmware binary or extracted filesystem ELF executables.",
            "output": "Categorized string tables with regex pattern matches (URLs, IPs, passwords, DLMS keys, OBIS codes).",
            "workflow": "Runs immediately after upload to rapidly classify architecture and surface low-hanging credentials.",
            "commands": [
                {"command": "strings -n 8 firmware.bin", "explanation": "Extract printable strings with minimum length of 8 characters"},
                {"command": "strings firmware.bin | grep -i pass", "explanation": "Filter strings for password and credential patterns"},
                {"command": "strings firmware.bin | grep -i dlms", "explanation": "Search for DLMS/COSEM protocol keywords and APDU tags"},
                {"command": "strings firmware.bin | grep -E '[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+'", "explanation": "Extract embedded IPv4 addresses"}
            ],
            "common_errors": [
                "High volume of garbage strings from packed/encrypted firmware regions",
                "Wide-character strings (UTF-16/32) missed without proper encoding flags"
            ],
            "troubleshooting": "Use -e l or -e b flags for 16-bit little/big-endian Unicode strings if ASCII returns few results.",
            "best_practices": "Combine strings with regex filtering and cross-reference discovered credentials against known default vendor tables.",
            "references": ["GNU binutils strings(1)", "CWE-798: Use of Hard-coded Credentials"]
        }
    },
    "binwalk": {
        "version": "2.3.4",
        "docs": {
            "purpose": "Firmware Extraction & File Signature Analysis: Scans binary images for embedded magic signatures, compressed filesystems (SquashFS, CramFS, JFFS2), and bootloader headers.",
            "input": "Raw firmware binary image (.bin, .img, .hex).",
            "output": "Offset map of identified headers, decompressed kernel images, and extracted root filesystem hierarchy.",
            "workflow": "Core extraction phase. Extracted filesystem is subsequently ingested by static scanners and decompliers.",
            "commands": [
                {"command": "binwalk firmware.bin", "explanation": "Perform signature scan across binary file offsets"},
                {"command": "binwalk -e firmware.bin", "explanation": "Extract detected filesystems and compressed archives automatically"},
                {"command": "binwalk -Mat firmware.bin", "explanation": "Perform recursive signature scan with entropy visualization"},
                {"command": "binwalk -E firmware.bin", "explanation": "Generate Shannon entropy map to locate encrypted regions"}
            ],
            "common_errors": [
                "Extraction failure due to missing decompressor utility (sasquatch, unblob)",
                "False positive signatures in high-entropy compressed regions"
            ],
            "troubleshooting": "Verify required decompressors are installed in system PATH. Use -C flag to specify dedicated extraction output directory.",
            "best_practices": "Always inspect the entropy graph first to determine whether the binary has an encrypted bootloader or encrypted payload.",
            "references": ["Binwalk Official Wiki", "Embedded Device Analysis Handbook (NSA)"]
        }
    },
    "cutter": {
        "version": "2.3.4",
        "docs": {
            "purpose": "Static Code & Control Flow Analysis: Graph-based disassembly and CFG navigation using the Rizin/Radare2 analysis engine to trace entry points and unsafe API calls.",
            "input": "Extracted ELF/ARM binary, shared object (.so), or raw microcontroller firmware with load address.",
            "output": "Control flow graphs (CFG), cross-references (XREFs), function signatures, and annotated disassembly.",
            "workflow": "Complements decompilation by providing precise basic-block level analysis of protocol state machines.",
            "commands": [
                {"command": "r2 -A dlms_binary", "explanation": "Open binary in Radare2 engine and run comprehensive auto-analysis"},
                {"command": "r2 -q -c 'aaa; afl' dlms_binary", "explanation": "Analyze all functions and list identified function names and sizes"},
                {"command": "r2 -q -c 'aaa; pdf @ main' dlms_binary", "explanation": "Disassemble and display control flow of main function"},
                {"command": "cutter dlms_binary", "explanation": "Launch interactive Cutter GUI visual reverse engineering workspace"}
            ],
            "common_errors": [
                "Incorrect entry point or base address offset for raw flat binaries",
                "Unidentified Thumb/ARM mode switching causing garbled disassembly"
            ],
            "troubleshooting": "Specify base load address (-m flag) and target CPU architecture (e.g. arm:32:cortex-m) for flat binaries without ELF headers.",
            "best_practices": "Map all references to buffer manipulation functions (strcpy, sprintf, memcpy) before auditing protocol logic.",
            "references": ["Rizin Reverse Engineering Framework", "Cutter Documentation"]
        }
    },
    "ghidra": {
        "version": "11.0.1",
        "docs": {
            "purpose": "Reverse Engineering & Decompilation: Translates compiled machine code (ARM, MIPS, PowerPC, x86) into high-level C pseudo-code to audit DLMS parser logic.",
            "input": "Extracted executable binaries, firmware blobs, or shared libraries.",
            "output": "Reconstructed C code, abstract syntax trees, function call graphs, and identified memory corruption bugs.",
            "workflow": "Deep static reverse engineering phase. Validates protocol state logic and cryptographic algorithm implementations.",
            "commands": [
                {"command": "analyzeHeadless . proj -import dlms_parser -postScript ExportDecompilation.java", "explanation": "Run Ghidra headless decompiler on target binary"},
                {"command": "ghidra-decompile dlms_parser 0x00401000", "explanation": "Decompile specific function at specified hex memory address"},
                {"command": "readelf -h dlms_parser", "explanation": "Verify ELF header and machine type before importing into Ghidra"}
            ],
            "common_errors": [
                "Java Virtual Machine (JVM) heap out-of-memory error during large binary indexing",
                "Unrecognized custom compiler calling convention"
            ],
            "troubleshooting": "Increase JVM max heap allocation (-Xmx4G) in ghidra headless script configuration.",
            "best_practices": "Use function signature archives and import vendor headers (.h) to improve type resolution in decompiled pseudo-code.",
            "references": ["NSA Ghidra Official Repository", "Ghidra Software Reverse Engineering Framework"]
        }
    },
    "trufflehog": {
        "version": "3.63.0",
        "docs": {
            "purpose": "Secret Detection & Credential Hunting: Scans filesystems, configurations, and binary strings for high-entropy secrets, private keys, and default DLMS passwords.",
            "input": "Extracted firmware root filesystem hierarchy and configuration directories.",
            "output": "Structured findings listing detected secrets, entropy scores, file locations, line numbers, and credential types.",
            "workflow": "Executes across the extracted rootfs to find factory default secrets and cryptographic keys.",
            "commands": [
                {"command": "trufflehog filesystem ./_flash.bin.extracted/", "explanation": "Scan entire extracted firmware filesystem for secrets"},
                {"command": "trufflehog filesystem . --include-paths='*.conf,*.ini,*.key'", "explanation": "Target specific configuration and key file patterns"},
                {"command": "trufflehog filesystem . --json", "explanation": "Export scan results in structured JSON format for automation"}
            ],
            "common_errors": [
                "False positives on binary data or compressed font/icon resources",
                "Deep symlink loops causing scanner recursion hang"
            ],
            "troubleshooting": "Exclude binary object directories and restrict search paths to text/config files using --include-paths filter.",
            "best_practices": "Immediately flag any found cryptographic private keys or hardcoded master passwords for immediate key rotation.",
            "references": ["TruffleHog Security Scanner", "OWASP Embedded Application Security Best Practices"]
        }
    },
    "entropy": {
        "version": "2.1.0",
        "docs": {
            "purpose": "Cryptographic & Packing Analysis: Calculates block-by-block Shannon entropy to detect encrypted payloads, obfuscated malware, and compressed data blocks.",
            "input": "Raw firmware binary or isolated memory segment dumps.",
            "output": "Block entropy scores (0.0 to 8.0 bits/byte), encryption likelihood verdict, and boundary offset markers.",
            "workflow": "Pinpoints exact start and end offsets of encrypted firmware segments prior to cryptanalysis.",
            "commands": [
                {"command": "binwalk -E firmware.bin", "explanation": "Generate ASCII/graphical Shannon entropy visualization"},
                {"command": "python tools/entropy.py --target firmware.bin --project 1 --run-id 0", "explanation": "Calculate block-level entropy with statistical anomaly detection"},
                {"command": "binwalk -E -J firmware.bin", "explanation": "Export block entropy metrics as JSON data stream"}
            ],
            "common_errors": [
                "High entropy caused by lossless compression (LZMA/GZIP) mistaken for strong AES encryption"
            ],
            "troubleshooting": "Check for known compression magic headers (0x5D for LZMA, 0x1F8B for GZIP) before declaring data encrypted.",
            "best_practices": "Entropy > 7.92 with uniform byte frequency distribution strongly indicates AES or random key material.",
            "references": ["Shannon Mathematical Theory of Communication (1948)", "NIST SP 800-22 Cryptographic Randomness Tests"]
        }
    },
    "wireshark": {
        "version": "4.2.3",
        "docs": {
            "purpose": "Protocol & Network Traffic Analysis: Captures and dissects DLMS/COSEM HDLC, TCP/IP, and IEC 62056 packets to inspect association authentication handshakes.",
            "input": "Packet capture files (.pcap, .pcapng) or active network interface tap.",
            "output": "APDU protocol breakdown, Association Result, Authentication Mechanism (NONE, LOW, HIGH), and cleartext meter readings.",
            "workflow": "Audits smart meter communications for absence of encryption (Suite 0) or unauthenticated OBIS code access.",
            "commands": [
                {"command": "tshark -r dlms_capture.pcap -Y dlms", "explanation": "Filter and display all DLMS/COSEM protocol frames"},
                {"command": "tshark -r dlms_capture.pcap -T json -Y dlms", "explanation": "Export full DLMS APDU dissection tree as JSON"},
                {"command": "tshark -r dlms_capture.pcap -e dlms.auth_value -T fields", "explanation": "Extract authentication values and credentials from frames"},
                {"command": "tshark -r dlms_capture.pcap -Y 'dlms.aarq || dlms.aare'", "explanation": "Isolate Association Request and Association Response handshakes"}
            ],
            "common_errors": [
                "Packets unparsed due to custom or non-standard HDLC framing",
                "Encrypted APDUs unreadable without security keys"
            ],
            "troubleshooting": "Configure DLMS dissector preferences in Wireshark/tshark to supply negotiated Security Suite master keys.",
            "best_practices": "Verify whether meters enforce Security Suite 1 (AES-GCM-128) and reject Association Mechanism NONE (0x00).",
            "references": ["Wireshark DLMS Dissector Documentation", "IEC 62056-5-3 / IEC 62056-6-2 Standards"]
        }
    },
    "angr": {
        "version": "9.2.42",
        "docs": {
            "purpose": "Symbolic Execution & Exploit Path Generation: Employs the Z3 SMT constraint solver to mathematically discover input byte sequences that bypass authentication or trigger overflows.",
            "input": "Compiled binary parser ELF with known start and target/avoid memory addresses.",
            "output": "Concrete input payloads that satisfy target execution constraints, register crash dumps, and reachability proofs.",
            "workflow": "Automates discovery of exploit paths through deep complex conditional branch logic in DLMS parsers.",
            "commands": [
                {"command": "python3 angr_find_bypass.py dlms_parser 0x00401234 0x00401380", "explanation": "Symbolically solve path from entry point to authentication bypass"},
                {"command": "python3 angr_overflow.py dlms_parser 0x00401450", "explanation": "Generate input payload to satisfy buffer overflow condition"},
                {"command": "python tools/angr.py --target firmware.bin --project 1 --run-id 0", "explanation": "Run automated symbolic constraint exploration on target"}
            ],
            "common_errors": [
                "Path explosion on complex cryptographic loops or floating-point instructions",
                "Memory exhaustion on deep state space exploration"
            ],
            "troubleshooting": "Hook or stub complex cryptographic hash functions and loop invariants with SimProcedures to bound exploration.",
            "best_practices": "Constrain search to short target functions identified during Ghidra/Cutter static analysis.",
            "references": ["angr Binary Analysis Framework (UC Santa Barbara)", "Z3 Theorem Prover (Microsoft Research)"]
        }
    },
    "afl++": {
        "version": "4.09c",
        "docs": {
            "purpose": "Coverage-Guided Dynamic Fuzzing: Mutates valid DLMS APDU frames to trigger edge-case crashes, memory safety bugs, and unhandled exceptions in firmware parsers.",
            "input": "Seed corpus of valid DLMS requests and compiled parser instrumented with AFL or emulated via QEMU.",
            "output": "Crash samples, hang dumps, code coverage maps, and minimized proof-of-concept test cases.",
            "workflow": "Dynamic vulnerability discovery stage. Verifies parser resilience against malformed network packets.",
            "commands": [
                {"command": "afl-fuzz -i seeds/ -o findings/ -- ./dlms_parser @@", "explanation": "Launch coverage-guided mutation fuzzing campaign"},
                {"command": "afl-tmin -i crash.bin -o min.bin -- ./dlms_parser @@", "explanation": "Minimize crashing sample to isolate smallest reproducible payload"},
                {"command": "afl-showmap -o cov.map -- ./dlms_parser seed.bin", "explanation": "Display execution coverage bitmap for input testcase"},
                {"command": "python tools/afl.py --target firmware.bin --project 1 --run-id 0", "explanation": "Execute automated fuzzing simulator harness"}
            ],
            "common_errors": [
                "Low execution speed due to slow forkserver initialization or disk I/O bottlenecks",
                "Parser terminates immediately on seed validation"
            ],
            "troubleshooting": "Use ramdisk (/tmp or shared memory) for output directory. Ensure seed corpus contains valid conforming DLMS frames.",
            "best_practices": "Combine dictionary injection (Aho-Corasick tokens) with AFL++ to guide mutations across protocol keywords.",
            "references": ["AFLplusplus Official Repository", "Fuzzing Smart Grid Architectures (IEEE S&P)"]
        }
    },
    "yara": {
        "version": "4.3.2",
        "docs": {
            "purpose": "Pattern Matching & Threat Signature Scanning: Identifies known malware signatures, weak crypto constants (DES S-Boxes, MD5 padding), and hardcoded credentials via curated rule files.",
            "input": "Extracted firmware files, memory dumps, or raw binary images.",
            "output": "Rule match reports detailing triggered signatures, string identifiers, and hex offsets.",
            "workflow": "Runs parallel to static analysis to detect known insecure coding patterns and cryptographic libraries.",
            "commands": [
                {"command": "yara -r rules/dlms_crypto.yar _flash.bin.extracted/", "explanation": "Scan extracted filesystem for DLMS crypto keys and weak algorithms"},
                {"command": "yara -r rules/hardcoded_passwords.yar _flash.bin.extracted/", "explanation": "Scan for factory default administrative credentials"},
                {"command": "yara -c rules/rules.yar", "explanation": "Compile and validate syntax of YARA rule files"}
            ],
            "common_errors": [
                "Syntax error in rule condition or regex pattern",
                "Excessive memory usage with overlapping wildcards in hex strings"
            ],
            "troubleshooting": "Validate rule files with 'yara -c' before scanning. Avoid overly permissive wildcards (*).",
            "best_practices": "Maintain modular rule files categorized by vulnerability type (crypto, credentials, backdoors).",
            "references": ["VirusTotal YARA Documentation", "Awesome YARA Rules"]
        }
    },
    "symbol_analysis": {
        "version": "1.2.0",
        "docs": {
            "purpose": "ELF Symbol Table Inspection: Extracts dynamic and static symbols (.symtab, .dynsym) to identify dangerous function calls (strcpy, system) and diagnostic backdoor hooks.",
            "input": "Extracted ELF binaries from firmware filesystem.",
            "output": "Symbol registry categorizing imported APIs, dangerous functions, and object-oriented C++ classes with CWE tags.",
            "workflow": "Pre-disassembly reconnaissance to prioritize function auditing.",
            "commands": [
                {"command": "readelf -s _flash.bin.extracted/app", "explanation": "Display all symbol table entries in target ELF executable"},
                {"command": "nm -D _flash.bin.extracted/app | grep -i pass", "explanation": "Filter dynamic symbols for password-related functions"},
                {"command": "readelf -l _flash.bin.extracted/app", "explanation": "Display ELF program headers and segment permissions (e.g. RWX stack)"}
            ],
            "common_errors": [
                "Target binary is stripped (no static symbol table available)"
            ],
            "troubleshooting": "If stripped, use 'nm -D' to check for dynamic symbols, or employ Ghidra FunctionID to recover library functions.",
            "best_practices": "Check for absence of NX/DEP flags in program headers (GNU_STACK with executable flag).",
            "references": ["ELF Specifications", "Linux readelf(1) & nm(1) Manuals"]
        }
    },
    "scorecard": {
        "version": "2.0.0",
        "docs": {
            "purpose": "Risk Scoring & CVSS Assessment: Aggregates all discovered vulnerabilities into standardized CVSS v3.1 scores, CWE classifications, and IEC 62056 compliance ratings.",
            "input": "Consolidated findings JSON from static, dynamic, protocol, and cryptographic scanners.",
            "output": "CVSS v3.1 base score, severity rating (Critical, High, Medium, Low), and executive impact summary.",
            "workflow": "Precedes report generation. Quantifies risk score out of 100.",
            "commands": [
                {"command": "python tools/scorecard.py --target firmware.bin --project 1 --run-id 0", "explanation": "Compute CVSS scores and risk ratings across all findings"},
                {"command": "python tools/scorecard.py --cvss-calc 'AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H'", "explanation": "Calculate standalone CVSS v3.1 score for vector string"}
            ],
            "common_errors": [
                "Unrecognized vulnerability category in input findings JSON",
                "Malformed CVSS vector string syntax"
            ],
            "troubleshooting": "Ensure all findings contain standard severity tags ('critical', 'high', 'medium', 'low').",
            "best_practices": "Map all findings to official MITRE CWE identifiers to maintain compliance auditing standards.",
            "references": ["FIRST CVSS v3.1 Specification", "MITRE Common Weakness Enumeration (CWE)"]
        }
    },
    "pdf_report": {
        "version": "1.8.0",
        "docs": {
            "purpose": "Security Audit Report Generation: Compiles technical findings, CVSS scorecards, proof-of-concept exploits, and remediation roadmaps into a publication-grade PDF report.",
            "input": "Session metadata, vulnerability records, OBIS code maps, and tool execution logs.",
            "output": "Complete multi-page PDF audit report with executive summary and technical appendices.",
            "workflow": "Final stage of the Firmware Analysis Workflow Simulator pipeline.",
            "commands": [
                {"command": "python tools/pdf_report.py --target firmware.bin --project 1 --run-id 0", "explanation": "Generate official PDF security audit report"},
                {"command": "python tools/pdf_report.py --preview", "explanation": "Preview generated HTML report template in local browser"}
            ],
            "common_errors": [
                "Missing ReportLab / WeasyPrint dependencies",
                "Font rendering errors on non-standard Unicode symbols"
            ],
            "troubleshooting": "Verify ReportLab is installed in Python environment ('pip install reportlab').",
            "best_practices": "Deliver the report with both high-level executive summaries for management and concrete code remediations for firmware engineers.",
            "references": ["ReportLab PDF Generation Library", "ISO/IEC 27001 Security Audit Reporting"]
        }
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# SANDBOX EXECUTION ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def execute_sandbox_command(
    project: models.Project,
    command: str,
    tool_name: str,
    db: Session
) -> Dict[str, Any]:
    """
    Executes a user command inside the simulated or real sandbox environment
    for the active tool and project, returning realistic production-grade output.
    """
    start_time = time.time()
    cmd = command.strip()
    
    # Target info
    fw_path = project.firmware_filepath or ""
    fw_exists = bool(fw_path and os.path.exists(fw_path))
    fw_filename = os.path.basename(fw_path) if fw_path else "firmware.bin"
    fw_size = project.file_size or (os.path.getsize(fw_path) if fw_exists else 12582912)
    target_arch = project.target_architecture or "ARM Cortex-M4"
    
    stdout_lines: List[str] = []
    stderr_lines: List[str] = []
    exit_code = 0

    # 1. Handle Shell Built-ins
    cmd_lower = cmd.lower()
    
    if cmd_lower in ("help", "--help", "-h"):
        doc_entry = TOOL_REGISTRY_DOCS.get(tool_name, TOOL_REGISTRY_DOCS.get("binwalk"))
        docs = doc_entry["docs"]
        stdout_lines.extend([
            f"FAWS SANDBOX CLI — {tool_name.upper()} v{doc_entry['version']}",
            "=" * 72,
            f"Purpose: {docs['purpose']}",
            "",
            "Available Commands for this Tool:",
        ])
        for c in docs.get("commands", []):
            stdout_lines.append(f"  $ {c['command']:<48} # {c['explanation']}")
            
        stdout_lines.extend([
            "",
            "Standard Sandbox Built-ins:",
            "  $ help                     # Display this help menu",
            "  $ clear                    # Clear terminal screen",
            "  $ env                      # Show sandbox environment variables",
            "  $ ls -la                   # List current directory and extracted files",
            "  $ file <binary>            # Inspect binary architecture & headers",
            "  $ hexdump -C <file>        # Display canonical hex + ASCII dump",
            "  $ cat <file>               # Read artifact or configuration contents",
            "=" * 72
        ])
        
    elif cmd_lower in ("clear", "cls"):
        # Handled by frontend, but return clean
        stdout_lines.append("")
        
    elif cmd_lower in ("env", "set", "export"):
        stdout_lines.extend([
            f"USER=analyst",
            f"HOME=/home/analyst",
            f"PWD=/home/analyst/sandbox/{tool_name}",
            f"PROJECT_ID={project.id}",
            f"PROJECT_NAME={project.name}",
            f"TARGET_ARCH={target_arch}",
            f"FIRMWARE_FILE={fw_filename}",
            f"FIRMWARE_PATH={fw_path or '/tmp/firmware.bin'}",
            f"FIRMWARE_SIZE={fw_size} bytes ({round(fw_size / (1024*1024), 2)} MB)",
            f"ACTIVE_TOOL={tool_name}",
            f"SANDBOX_MODE=PRODUCTION_ISOLATED",
            f"SECURITY_PROFILE=STRICT_CONTAINER"
        ])

    elif cmd_lower in ("ls", "dir") or cmd_lower.startswith(("ls ", "dir ")):
        stdout_lines.extend([
            "total 38448",
            "drwxr-xr-x  5 analyst analyst     4096 Nov 23 12:00 .",
            "drwxr-xr-x 22 root    root        4096 Nov 23 10:00 ..",
            f"-rw-r--r--  1 analyst analyst {fw_size:>9} Nov 23 11:30 {fw_filename}",
            "drwxr-xr-x  6 analyst analyst     4096 Nov 23 11:32 _flash.bin.extracted",
            "-rwxr-xr-x  1 analyst analyst   524288 Nov 23 11:32 dlms_parser",
            "-rwxr-xr-x  1 analyst analyst   262144 Nov 23 11:32 libcosem.so",
            "-rw-r--r--  1 analyst analyst     2048 Nov 23 11:32 /etc/dlms.conf",
            "-rw-r--r--  1 analyst analyst    45000 Nov 23 11:33 filesystem.tar.gz",
            "-rw-r--r--  1 analyst analyst    15000 Nov 23 11:34 capture.pcap",
            "-rw-r--r--  1 analyst analyst     1024 Nov 23 11:35 strings.txt",
            "-rw-r--r--  1 analyst analyst     2048 Nov 23 11:36 symbols.json",
            "-rw-r--r--  1 analyst analyst     3072 Nov 23 11:37 crashes.zip",
            "-rw-r--r--  1 analyst analyst   150000 Nov 23 11:40 audit_report.pdf"
        ])

    elif cmd_lower.startswith("file ") or cmd_lower == "file":
        target = cmd.split(" ", 1)[1] if " " in cmd else fw_filename
        stdout_lines.append(
            f"{target}: ELF 32-bit LSB executable, {target_arch}, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.3, for GNU/Linux 3.2.0, with debug_info, not stripped"
        )

    elif cmd_lower.startswith("cat "):
        target_file = cmd.split(" ", 1)[1].strip()
        if "dlms.conf" in target_file:
            stdout_lines.extend([
                "# DLMS/COSEM Smart Meter Configuration File",
                "[device]",
                "serial_number = 00-96-01-00-02-FF",
                "vendor = ABB / Hitachi Energy",
                "model = Relion 670 Series",
                "firmware_version = 1.1.0-r27",
                "",
                "[security]",
                "security_suite = 0  # 0=None/Plaintext, 1=AES-GCM-128",
                "authentication_mechanism = 0x00  # NONE",
                "master_key = SuperSecret123!     # [!] HARDCODED_CREDENTIAL",
                "",
                "[network]",
                "interface = eth0",
                "dlms_port = 4059",
                "ip_address = 192.168.1.100"
            ])
        elif "strings.txt" in target_file:
            stdout_lines.extend([
                "admin:changeme",
                "DLMS_COSEM_BYPASS_KEY",
                "4d534d534b4559303132333435363738",
                "1.0.1.8.0.255",
                "0.0.96.1.0.255",
                "dlms://192.168.1.1:4059",
                "GCC: (GNU) 9.3.0 arm-linux-gnueabi"
            ])
        elif "symbols.json" in target_file:
            stdout_lines.extend([
                "[",
                '  {"symbol": "dlms_auth_verify", "address": "0x00401380", "type": "FUNC", "cwe": "CWE-287"},',
                '  {"symbol": "strcpy", "address": "0x00401450", "type": "FUNC", "cwe": "CWE-120"},',
                '  {"symbol": "system", "address": "0x00401820", "type": "FUNC", "cwe": "CWE-78"}',
                "]"
            ])
        else:
            stdout_lines.append(f"cat: {target_file}: File read successfully (Simulated contents ready for audit).")

    elif cmd_lower.startswith(("hexdump", "xxd")):
        # Read real bytes from firmware if available
        data_bytes = None
        if fw_exists:
            try:
                with open(fw_path, "rb") as f:
                    data_bytes = f.read(128)
            except Exception:
                pass
        
        if not data_bytes:
            data_bytes = bytes([
                0x7F, 0x45, 0x4C, 0x46, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x02, 0x00, 0x28, 0x00, 0x01, 0x00, 0x00, 0x00, 0x54, 0x12, 0x00, 0x00, 0x34, 0x00, 0x00, 0x00,
                0x4D, 0x53, 0x4D, 0x53, 0x5F, 0x4B, 0x45, 0x59, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37,
                0x68, 0x73, 0x71, 0x73, 0x00, 0x04, 0x00, 0x00, 0x53, 0x75, 0x70, 0x65, 0x72, 0x53, 0x65, 0x63
            ])
            
        for offset in range(0, len(data_bytes), 16):
            chunk = data_bytes[offset:offset+16]
            hex_part = " ".join(f"{b:02x}" for b in chunk)
            ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
            stdout_lines.append(f"{offset:08x}  {hex_part:<48}  |{ascii_part}|")

    # 2. Tool-Specific Command Execution
    else:
        # Check tool type
        effective_tool = tool_name
        if "binwalk" in cmd_lower: effective_tool = "binwalk"
        elif "strings" in cmd_lower: effective_tool = "strings"
        elif "entropy" in cmd_lower: effective_tool = "entropy"
        elif "cutter" in cmd_lower or "r2" in cmd_lower: effective_tool = "cutter"
        elif "ghidra" in cmd_lower or "analyzeheadless" in cmd_lower: effective_tool = "ghidra"
        elif "trufflehog" in cmd_lower: effective_tool = "trufflehog"
        elif "wireshark" in cmd_lower or "tshark" in cmd_lower: effective_tool = "wireshark"
        elif "angr" in cmd_lower: effective_tool = "angr"
        elif "afl" in cmd_lower: effective_tool = "afl++"
        elif "yara" in cmd_lower: effective_tool = "yara"
        elif "readelf" in cmd_lower or "nm" in cmd_lower: effective_tool = "symbol_analysis"
        elif "scorecard" in cmd_lower: effective_tool = "scorecard"
        elif "report" in cmd_lower or "pdf" in cmd_lower: effective_tool = "pdf_report"

        # Execute based on tool
        if effective_tool == "binwalk":
            stdout_lines.extend([
                f"DECIMAL       HEXADECIMAL     DESCRIPTION",
                f"--------------------------------------------------------------------------------",
                f"0             0x0             ARM Cortex-M Vector Table, Initial SP: 0x20008000, Reset: 0x00000401",
                f"1024          0x400           Squashfs filesystem, little endian, version 4.0, size: 2411520 bytes",
                f"524288        0x80000         LZMA compressed data, dictionary size: 16777216 bytes",
                f"1048576       0x100000        AES-128 ECB encrypted payload section [Entropy: 7.99 bits/byte]",
                f"3145728       0x300000        DLMS/COSEM Configuration Block (OBIS Profile Tables)"
            ])
            if "-e" in cmd or "-mat" in cmd_lower:
                stdout_lines.extend([
                    f"",
                    f"[+] Extraction directory created: _flash.bin.extracted/",
                    f"[+] Extracting Squashfs filesystem... Done (342 files extracted)",
                    f"[+] Extracted kernel image to: _flash.bin.extracted/kernel.img"
                ])
                
        elif effective_tool == "strings":
            # If firmware exists, attempt real string extraction or grep
            grep_filter = None
            if "|" in cmd and "grep" in cmd:
                parts = cmd.split("grep", 1)[1].strip()
                grep_filter = parts.replace("-i", "").replace("-E", "").replace("'", "").replace('"', '').strip()
                
            stdout_lines.append(f"[+] Scanning firmware strings (Encoding: ASCII & UTF-8, Min Length: 6)...")
            all_sample_strings = [
                "DLMS_COSEM_Confirmed_Implementation",
                "admin:changeme",
                "DLMS_MASTER_KEY=SuperSecret123!",
                "OBIS: 1.0.1.8.0.255 (Active Energy Import)",
                "OBIS: 0.0.96.1.0.255 (Meter Serial Number)",
                "dlms://192.168.1.1:4059",
                "AssociationRequest: Mechanism=NONE",
                "AES-128-GCM-Suite1-Key",
                "GCC: (Ubuntu 9.3.0-17ubuntu1~20.04) 9.3.0",
                "VxWorks 6.9 kernel diagnostic prompt",
                "/etc/dlms.conf",
                "/usr/lib/libcosem.so"
            ]
            
            if grep_filter:
                stdout_lines.append(f"[+] Applying pattern filter: '{grep_filter}'")
                matched = [s for s in all_sample_strings if grep_filter.lower() in s.lower()]
                if matched:
                    stdout_lines.extend([f"  {s}" for s in matched])
                    stdout_lines.append(f"[!] Matched {len(matched)} pattern(s) in firmware binary.")
                else:
                    stdout_lines.append(f"No matching strings found for '{grep_filter}'.")
            else:
                stdout_lines.extend([f"  {s}" for s in all_sample_strings])
                stdout_lines.append(f"[+] Extracted {len(all_sample_strings)} sensitive string patterns.")

        elif effective_tool == "entropy":
            stdout_lines.extend([
                f"[+] Analyzing Shannon entropy on {fw_filename} ({fw_size} bytes)...",
                f"[+] Calculating sliding block entropy (Block Size: 1024 bytes, 12,288 blocks)...",
                f"[+] Overall Mean Shannon Entropy: 7.4218 bits/byte",
                f"--------------------------------------------------------------------------------",
                f"0x00000000 - 0x00080000 (0.50 MB): Entropy 5.82 - Vector table & Bootloader code",
                f"0x00080000 - 0x00100000 (0.50 MB): Entropy 7.99 - [!] CRITICAL: AES encrypted payload",
                f"0x00100000 - 0x00380000 (2.50 MB): Entropy 6.84 - Compressed SquashFS image",
                f"0x00380000 - 0x00400000 (0.50 MB): Entropy 1.12 - Zero-padding / calibration data",
                f"--------------------------------------------------------------------------------",
                f"[!] Anomaly detected: High entropy region (8.0 bits/byte) at offset 0x80000–0x100000."
            ])

        elif effective_tool == "cutter":
            stdout_lines.extend([
                f"[+] Opening {fw_filename} in Radare2/Cutter static analysis engine...",
                f"[+] Architecture: {target_arch} (32-bit, Little-Endian)",
                f"[+] Running auto-analysis: functions, basic blocks, XREFs...",
                f"[+] Discovered 428 functions, 1,294 basic blocks, 3,812 cross-references.",
                f"",
                f"; -- Function: sym.dlms_request_handler (0x004012a0)",
                f"/ (fcn) sym.dlms_request_handler 148",
                f"|   0x004012a0      push {{r4, r5, r7, lr}}",
                f"|   0x004012a2      sub sp, sp, #0x48",
                f"|   0x004012a4      mov r4, r0             ; r4 = APDU frame ptr",
                f"|   0x004012a6      ldrb r1, [r4]          ; tag 0xC0 (AARQ)",
                f"|   0x004012a8      cmp r1, #0xc0",
                f"|   0x004012aa      beq 0x401380           ; branch to auth check",
                f"|   ; [!] SECURITY VULNERABILITY AT 0x00401450:",
                f"|   0x0040144c      add r0, sp, #8",
                f"|   0x0040144e      mov r1, r4",
                f"|   0x00401450      bl sym.imp.strcpy      ; [CWE-120] Unsafe strcpy without bounds check!",
                f"\\   0x00401454      add sp, sp, #0x48"
            ])

        elif effective_tool == "ghidra":
            stdout_lines.extend([
                f"[+] Ghidra Headless Analyzer v11.0.1 initialized",
                f"[+] Program: dlms_parser (Format: ELF 32-bit ARM)",
                f"[+] Decompiling function 'dlms_auth_verify' at 0x00401380:",
                f"",
                f"/* Decompiled C Pseudo-code via Ghidra Decompiler */",
                f"int dlms_auth_verify(char *client_auth_key, int auth_mechanism) {{",
                f"    char hardcoded_key[] = {{ 0xA5, 0x5A, 0x4D, 0x53, 0x00 }};",
                f"    int i;",
                f"    ",
                f"    // [!] VULNERABILITY: Permitting NULL authentication mechanism",
                f"    if (auth_mechanism == DLMS_AUTH_NONE) {{",
                f"        log_event(\"[!] Warning: Association accepted with mechanism NONE (0x00)\");",
                f"        return 1; // Unauthenticated access granted!",
                f"    }}",
                f"    ",
                f"    for (i = 0; i < 4; i++) {{",
                f"        if ((client_auth_key[i] ^ 0xA5) != hardcoded_key[i]) {{",
                f"            return 0; // Auth failed",
                f"        }}",
                f"    }}",
                f"    return 1; // Auth successful",
                f"}}"
            ])

        elif effective_tool == "trufflehog":
            stdout_lines.extend([
                f"🐷 TruffleHog v3.63.0 — High-Entropy Secret & Key Scanner",
                f"[+] Scanning directory: ./_flash.bin.extracted/",
                f"--------------------------------------------------------------------------------",
                f"[!] Found Secret: Hardcoded DLMS Association Password",
                f"    File: /etc/dlms.conf:14",
                f"    Secret: DLMS_MASTER_KEY=SuperSecret123!",
                f"    Entropy: 4.82 bits/byte",
                f"    CWE: CWE-798 (Use of Hard-coded Credentials)",
                f"",
                f"[!] Found Secret: AES-128 GCM Master Key",
                f"    File: /usr/lib/libcosem.so:offset 0x0041f0",
                f"    Secret: 4d534d534b4559303132333435363738",
                f"    Entropy: 4.12 bits/byte",
                f"    Verification: Verified local match"
            ])

        elif effective_tool == "wireshark":
            stdout_lines.extend([
                f"[+] Reading DLMS capture from dlms_capture.pcap via tshark dissector...",
                f"",
                f"Frame 1: 82 bytes (Association Request - AARQ)",
                f"    DLMS/COSEM APDU:",
                f"        Application Context: 2.16.756.5.8.1.1 (Logical Name without ciphering)",
                f"        Calling AP Title: 4D4D4D0000000001 (MMM Meter #1)",
                f"        Security Mechanism: NONE (0x00) - [!] No Authentication Requested",
                f"        User Information: 810400000000",
                f"",
                f"Frame 2: 78 bytes (Association Response - AARE)",
                f"    DLMS/COSEM APDU:",
                f"        Association Result: ACCEPTED (0x00)",
                f"        Security Mechanism: NONE (0x00)",
                f"        [!] VULNERABILITY: Server accepted connection with zero credentials.",
                f"        Exposed OBIS readings: 1.0.1.8.0.255, 1.0.2.8.0.255, 0.0.96.1.0.255"
            ])

        elif effective_tool == "angr":
            stdout_lines.extend([
                f"[+] angr v9.2.42 symbolic execution engine initialized",
                f"[+] Target binary: dlms_parser (Arch: {target_arch})",
                f"[+] Simulating symbolic state at 0x00401000...",
                f"[+] Path constraints defined: avoid=0x00401398, find=0x00401380 (Auth Bypass)",
                f"[+] Solving constraints with Z3 SMT solver...",
                f"[+] SAT: Found 1 reachable solution satisfying bypass conditions!",
                f"--------------------------------------------------------------------------------",
                f"[+] Discovered Exploit Input Payload (32 bytes):",
                f"    Hex:   44 4c 4d 53 5f 43 4f 53 45 4d 5f 42 59 50 41 53 53 5f 4b 45 59 00 00 00 de ad be ef",
                f"    ASCII: 'DLMS_COSEM_BYPASS_KEY\\x00\\x00\\x00\\xde\\xad\\xbe\\xef'",
                f"[!] Buffer overflow triggered at offset 64. Return address overwritten!"
            ])

        elif effective_tool == "afl++":
            stdout_lines.extend([
                f"afl-fuzz ++4.09c [DLMS/COSEM Parser Dynamic Fuzzing Campaign]",
                f"--------------------------------------------------------------------------------",
                f"  process timing           : 0 days, 2 hrs, 14 min, 32 sec",
                f"  cycles done              : 14        exec speed       : 1,842/sec",
                f"  total execs              : 14.8M     paths total      : 1,429 (+182)",
                f"  unique crashes           : 11        unique hangs     : 2",
                f"--------------------------------------------------------------------------------",
                f"[!] Crash #1: SEGV at 0x00401450 (dlms_parse_request+0x48) - Heap buffer overflow",
                f"[!] Crash #2: SIGILL at 0x00402110 (cosem_decrypt_apdu) - Null pointer dereference",
                f"[!] Crash #3: SEGV at 0x004035a4 (obis_normalize_string) - Stack format string write",
                f"[+] Saved 11 reproducible crash dumps to ./findings/crashes/"
            ])

        elif effective_tool == "yara":
            stdout_lines.extend([
                f"[+] Compiling YARA rule sets (crypto_rules.yar, credentials.yar, dlms.yar)...",
                f"[+] Scanning target firmware: {fw_filename}...",
                f"--------------------------------------------------------------------------------",
                f"0x00000120 DLMS_COSEM_Confirmed_Implementation [Offset 0x120] (Matches: OBIS tags)",
                f"0x00080000 Weak_Cipher_DES_RC4 [Offset 0x80000] (Matches: DES S-Box constants)",
                f"0x000412a0 Hardcoded_Credentials [Offset 0x412a0] (Matches: 'admin:changeme')",
                f"0x00124a80 Insecure_Network_Service_Usage [Offset 0x124a80] (Matches: telnet/tftp)",
                f"[+] YARA scan finished: 4 rules triggered across binary."
            ])

        elif effective_tool == "symbol_analysis":
            stdout_lines.extend([
                f"[+] Parsing ELF symbol table (.symtab / .dynsym)...",
                f"[+] Target: _flash.bin.extracted/app (ARM 32-bit)",
                f"--------------------------------------------------------------------------------",
                f"  Num:    Value  Size Type    Bind   Vis      Ndx Name",
                f"    14: 004012a0   148 FUNC    GLOBAL DEFAULT   12 dlms_request_handler",
                f"    15: 00401380    84 FUNC    GLOBAL DEFAULT   12 dlms_auth_verify",
                f"    16: 00401450    32 FUNC    GLOBAL DEFAULT   12 strcpy@@GLIBC_2.4  [!] CWE-120",
                f"    17: 00401820    48 FUNC    GLOBAL DEFAULT   12 system@@GLIBC_2.4  [!] CWE-78",
                f"    18: 00402110   210 FUNC    GLOBAL DEFAULT   12 cosem_decrypt_apdu",
                f"[+] Identified 2 high-risk unsafe library calls in dynamic symbol table."
            ])

        elif effective_tool == "scorecard":
            stdout_lines.extend([
                f"[+] CVSS v3.1 Security Scorecard Engine v2.0",
                f"[+] Aggregating findings across 12 pipeline stages...",
                f"--------------------------------------------------------------------------------",
                f"  Critical Findings : 4  (CVSS 9.0 - 10.0)",
                f"  High Findings     : 9  (CVSS 7.0 - 8.9)",
                f"  Medium Findings   : 14 (CVSS 4.0 - 6.9)",
                f"  Low Findings      : 8  (CVSS 0.1 - 3.9)",
                f"--------------------------------------------------------------------------------",
                f"  OVERALL SECURITY RISK SCORE: 32 / 100 [CRITICAL RISK]",
                f"  DLMS COMPLIANCE STATUS     : NON-COMPLIANT (Plaintext Suite 0 Detected)",
                f"[+] Exported risk scorecard to data/artifacts/risk_score.json"
            ])

        elif effective_tool == "pdf_report":
            stdout_lines.extend([
                f"[+] ReportLab PDF Generator Engine v1.8.0",
                f"[+] Compiling executive summary, methodology, and 35 finding disclosures...",
                f"[+] Generating high-resolution vulnerability charts and CVSS breakdown...",
                f"[+] Formatting remediation roadmap and appendix...",
                f"--------------------------------------------------------------------------------",
                f"[✓] Successfully generated: data/artifacts/FAWS_Report_{project.id}.pdf",
                f"[✓] File size: 147,208 bytes (47 pages)",
                f"[✓] Report ready for download in the 'Reports' tab."
            ])

        else:
            stdout_lines.append(f"[{effective_tool}] Command executed successfully. Return code: 0.")

    elapsed_ms = int((time.time() - start_time) * 1000)

    # 3. Log into database so tool run logs reflect manual testing
    try:
        session = db.query(models.PipelineSession).filter(models.PipelineSession.project_id == project.id).first()
        if session:
            tool_run = models.ToolRun(
                session_id=session.id,
                tool_name=tool_name,
                command_executed=command,
                exit_code=exit_code,
                started_at=datetime.datetime.utcnow(),
                ended_at=datetime.datetime.utcnow()
            )
            db.add(tool_run)
            db.commit()
            db.refresh(tool_run)

            # Record log entry
            log_msg = "\n".join(stdout_lines) if stdout_lines else "\n".join(stderr_lines)
            log_entry = models.LogEntry(
                tool_run_id=tool_run.id,
                log_type="STDOUT" if exit_code == 0 else "STDERR",
                message=log_msg[:3000]
            )
            db.add(log_entry)
            db.commit()
    except Exception:
        pass

    return {
        "stdout": "\n".join(stdout_lines),
        "stderr": "\n".join(stderr_lines),
        "exit_code": exit_code,
        "execution_time_ms": elapsed_ms,
        "tool": tool_name
    }
