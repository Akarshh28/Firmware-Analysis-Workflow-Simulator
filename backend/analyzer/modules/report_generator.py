"""
report_generator.py - Turns the pipeline's per-file results into:
  1. A machine-readable JSON file (full detail, for feeding into other tools)
  2. A human-readable Markdown summary (for the Vulnerability Assessment Report)
"""

import json
import os
from datetime import datetime, timezone


def determine_protocol_verdict(string_matches: dict, yara_matches: list):
    """Same logic used manually on Relion670: ACSE alone never counts as
    DLMS/COSEM; literal DLMS/COSEM/OBIS evidence is required."""
    yara_rule_names = {m["rule"] for m in yara_matches}

    if "DLMS_COSEM_Confirmed_Implementation" in yara_rule_names:
        return "DLMS/COSEM confirmed"

    has_dlms_strings = bool(
        string_matches.get("dlms_cosem") and len(string_matches["dlms_cosem"]) >= 2
    )
    if has_dlms_strings:
        return "DLMS/COSEM likely (string evidence, YARA rule did not fire - review manually)"

    if "IEC61850_Without_DLMS" in yara_rule_names or (string_matches.get("iec61850") and len(string_matches["iec61850"]) >= 2):
        return "IEC 61850 (DLMS/COSEM not present)"

    if string_matches.get("acse_association") and len(string_matches["acse_association"]) >= 2:
        return "ACSE association layer present, but neither DLMS/COSEM nor IEC 61850 confirmed - manual review needed"

    return "No DLMS/COSEM or IEC 61850 evidence found"


def build_file_report(artifact_path, file_type, extraction_status,
                       entropy_result=None, string_result=None,
                       yara_result=None, symbol_result=None):
    report = {
        "path": artifact_path,
        "file_type": file_type,
        "extraction_status": extraction_status,
    }

    if entropy_result is not None:
        report["entropy_analysis"] = entropy_result
    if string_result is not None:
        report["string_scan"] = string_result
    if yara_result is not None:
        report["yara_scan"] = yara_result
    if symbol_result is not None:
        report["symbol_analysis"] = symbol_result

    if string_result and string_result.get("success") and yara_result and yara_result.get("success"):
        report["protocol_verdict"] = determine_protocol_verdict(
            string_result.get("matches", {}), yara_result.get("matches", [])
        )

    return report


def write_json_report(all_file_reports: list, output_path: str):
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_files_processed": len(all_file_reports),
        "files": all_file_reports,
    }
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(payload, f, indent=2)


def write_markdown_report(all_file_reports: list, output_path: str):
    lines = []
    lines.append("# Firmware Analysis Report")
    lines.append(f"\nGenerated: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"\nTotal files processed: {len(all_file_reports)}\n")

    # --- Summary table ---
    lines.append("## Summary\n")
    lines.append("| File | Status | Protocol Verdict | YARA High-Severity Hits |")
    lines.append("|---|---|---|---|")
    for r in all_file_reports:
        name = os.path.basename(r["path"])
        status = r["extraction_status"]
        verdict = r.get("protocol_verdict", "-")
        high_hits = "-"
        if r.get("yara_scan", {}).get("success"):
            high_hits = str(sum(
                1 for m in r["yara_scan"]["matches"] if m["severity"] == "high"
            ))
        lines.append(f"| {name} | {status} | {verdict} | {high_hits} |")

    # --- Per-file detail ---
    lines.append("\n## File Details\n")
    for r in all_file_reports:
        lines.append(f"### {r['path']}\n")
        lines.append(f"- **File type:** {r.get('file_type', 'unknown')}")
        lines.append(f"- **Extraction status:** {r['extraction_status']}")

        if "protocol_verdict" in r:
            lines.append(f"- **Protocol verdict:** {r['protocol_verdict']}")

        entropy = r.get("entropy_analysis")
        if entropy:
            if entropy.get("success"):
                lines.append(f"- **Entropy verdict:** {entropy['verdict']} "
                              f"({len(entropy['flagged_regions'])} flagged region(s))")
            else:
                lines.append(f"- **Entropy analysis error:** {entropy.get('error')}")

        strings = r.get("string_scan")
        if strings:
            if strings.get("success"):
                cats = ", ".join(strings["matches"].keys()) or "none"
                lines.append(f"- **String scan categories matched:** {cats}")
            else:
                lines.append(f"- **String scan error:** {strings.get('error')}")

        yara = r.get("yara_scan")
        if yara:
            if yara.get("success"):
                if yara["matches"]:
                    lines.append(f"- **YARA matches ({len(yara['matches'])}):**")
                    for m in yara["matches"]:
                        lines.append(f"  - `{m['rule']}` [{m['severity']}] - {m['description']}")
                else:
                    lines.append("- **YARA matches:** none")
            else:
                lines.append(f"- **YARA scan error:** {yara.get('error')}")

        symbols = r.get("symbol_analysis")
        if symbols:
            if symbols.get("success"):
                lines.append(f"- **Symbol table:** {symbols['total_symbols']} symbols "
                              f"(using `{symbols['objdump_used']}`)")
                if symbols["flagged_symbols"]:
                    lines.append(f"- **Flagged symbols disassembled ({len(symbols['flagged_symbols'])}):**")
                    for s in symbols["flagged_symbols"]:
                        lines.append(f"  - `{s['name']}` @ {s['address']} - disassembly: {s['disassembly_status']}")
            else:
                lines.append(f"- **Symbol analysis error:** {symbols.get('error')}")

        lines.append("")  # blank line between files

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines))

def generate_pdf_report(results, out_dir):
    """
    Generates a PDF Vulnerability Assessment Report from the FAWS pipeline results.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError:
        print("Warning: reportlab not installed. Falling back to markdown report.")
        # Minimal fallback
        with open(os.path.join(out_dir, "report.json"), "w") as f:
            json.dump(results, f, indent=4)
        return
        
    pdf_path = os.path.join(out_dir, "FAWS_Vulnerability_Report.pdf")
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "FAWS Vulnerability Assessment Report")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    y = height - 100
    
    # Stage 1
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Stage 1: Pre-Analysis & Extraction")
    y -= 20
    c.setFont("Helvetica", 10)
    stage1 = results.get("stage1", {})
    c.drawString(60, y, f"Entropy Verdict: {stage1.get('entropy', {}).get('verdict')}")
    y -= 15
    c.drawString(60, y, f"Files Extracted: {stage1.get('extraction_nodes')}")
    y -= 30
    
    # Stage 2
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Stage 2: Advanced Static Component Analysis")
    y -= 20
    c.setFont("Helvetica", 10)
    stage2 = results.get("stage2", {})
    ghidra_findings = len(stage2.get("ghidra", {}).get("findings", []))
    yara_matches = len(stage2.get("yara", {}).get("matches", []))
    c.drawString(60, y, f"Ghidra Findings (Unsafe Functions & OBIS): {ghidra_findings}")
    y -= 15
    c.drawString(60, y, f"YARA/String Rule Matches: {yara_matches}")
    y -= 30
    
    # Stage 3
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Stage 3: Dynamic Analysis & Emulation")
    y -= 20
    c.setFont("Helvetica", 10)
    stage3 = results.get("stage3", {})
    if stage3.get("emulation"):
        emu = stage3.get("emulation")
        c.drawString(60, y, f"Emulated Functions: {emu.get('emulated_functions', 0)}")
        y -= 15
        vulns = len(emu.get("vulnerabilities_found", []))
        c.drawString(60, y, f"Vulnerabilities (Crashes) Detected: {vulns}")
    else:
        c.drawString(60, y, "No emulation performed.")
    y -= 30
    
    c.save()

