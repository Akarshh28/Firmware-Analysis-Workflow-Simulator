import os
import subprocess
import re
import sys
import json

# Add analyzer to sys.path so it can import its own modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from modules.extractor import walk_and_extract, flatten_tree, is_known_document
from modules.string_scanner import scan_strings
from modules.entropy_analysis import analyze_entropy
from modules.yara_scanner import scan_with_yara
from modules.symbol_analyzer import analyze_symbols
from modules.ghidra_scanner import scan_with_ghidra
from app.obis_parser import OBISParser
from main import compute_signature, is_binary_leaf
from app.config import settings

def get_state_path(project_id: int) -> str:
    return os.path.join(settings.ARTIFACTS_DIR, f"{project_id}_real_state.json")

def load_state(project_id: int) -> dict:
    path = get_state_path(project_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"leaf_binaries": [], "extra_keywords": [], "strings_results": {}, "yara_results": {}}

def save_state(project_id: int, state: dict):
    with open(get_state_path(project_id), "w") as f:
        json.dump(state, f, indent=2)

# ---------------------------------------------------------------------------
# Real analyzer wrappers
# ---------------------------------------------------------------------------

def run_binwalk(file_path: str, project_id: int) -> dict:
    work_dir = os.path.join(settings.ARTIFACTS_DIR, f"{project_id}_extraction")
    os.makedirs(work_dir, exist_ok=True)
    
    findings = []
    
    try:
        tree_root = walk_and_extract(file_path, work_dir, max_depth=6)
    except Exception as e:
        return {
            "stage": "extraction",
            "tool": "binwalk",
            "status": "error",
            "error": f"extraction failed: {e}",
            "findings": []
        }

    all_nodes = flatten_tree(tree_root)
    leaf_binaries = []
    content_signature_cache = {}

    for node in all_nodes:
        if node.status == "error":
            findings.append({
                "description": f"Extraction error on {os.path.basename(node.path)}: {node.status_detail}",
                "severity": "medium",
                "cwe": "CWE-000",
                "category": "extraction_error"
            })
        elif is_binary_leaf(node):
            sig = compute_signature(node.path)
            if sig is not None and sig in content_signature_cache:
                continue # duplicate
            if sig is not None:
                content_signature_cache[sig] = node.path
            leaf_binaries.append(node.path)

    state = load_state(project_id)
    state["leaf_binaries"] = leaf_binaries
    save_state(project_id, state)

    return {
        "stage": "extraction",
        "tool": "binwalk",
        "status": "success",
        "findings": findings,
    }

def run_strings(file_path: str, project_id: int) -> dict:
    state = load_state(project_id)
    findings = []
    
    cat_to_cwe = {
        "dlms_cosem": ("CWE-200", "medium"),
        "iec61850": ("CWE-200", "medium"),
        "acse_association": ("CWE-200", "medium"),
        "weak_crypto": ("CWE-327", "high"),
        "unsafe_functions": ("CWE-120", "high"),
        "auth_credentials": ("CWE-798", "critical"),
        "network_services": ("CWE-319", "medium"),
        "rtos_platform": ("CWE-200", "info"),
    }
    
    extra_keywords = []
    all_strings_results = {}
    
    for leaf in state.get("leaf_binaries", []):
        res = scan_strings(leaf)
        all_strings_results[leaf] = res
        if res.get("success"):
            matches = res.get("matches", {})
            for cat, values in matches.items():
                cwe, severity = cat_to_cwe.get(cat, ("CWE-000", "info"))
                for val in values:
                    findings.append({
                        "description": f"[{cat}] {val}",
                        "severity": severity,
                        "cwe": cwe,
                        "category": cat,
                        "value": val,
                        "file": os.path.basename(leaf)
                    })
                if cat in ("unsafe_functions", "auth_credentials"):
                    extra_keywords.extend(values)
                    
    state["extra_keywords"] = extra_keywords
    state["strings_results"] = all_strings_results
    save_state(project_id, state)
    
    return {
        "stage": "identification",
        "tool": "strings",
        "status": "success",
        "findings": findings,
    }

def run_entropy(file_path: str, project_id: int) -> dict:
    state = load_state(project_id)
    findings = []
    
    for leaf in state.get("leaf_binaries", []):
        res = analyze_entropy(leaf)
        if res.get("success"):
            flagged = res.get("flagged_regions", [])
            if flagged:
                total_high_entropy_bytes = sum(r["end_offset"] - r["start_offset"] for r in flagged)
                file_size = os.path.getsize(leaf) if os.path.exists(leaf) else max(1, total_high_entropy_bytes)
                percent = (total_high_entropy_bytes / file_size) * 100
                
                if percent > 80:
                    desc = f"{percent:.1f}% of {os.path.basename(leaf)} is high-entropy — consistent with normal packed/encrypted executable, not necessarily suspicious."
                    sev = "info"
                else:
                    desc = f"Detected {len(flagged)} localized high-entropy regions in {os.path.basename(leaf)} (covering {percent:.1f}% of file). May contain encrypted keys or compressed payloads."
                    sev = "medium"
                    
                findings.append({
                    "description": desc,
                    "severity": sev,
                    "cwe": "CWE-326",
                    "file": os.path.basename(leaf)
                })
                
    return {
        "stage": "entropy",
        "tool": "entropy_analysis",
        "status": "success",
        "findings": findings
    }

def run_yara(file_path: str, project_id: int) -> dict:
    state = load_state(project_id)
    findings = []
    all_yara_results = {}
    
    for leaf in state.get("leaf_binaries", []):
        res = scan_with_yara(leaf)
        all_yara_results[leaf] = res
        if res.get("success"):
            for match in res.get("matches", []):
                severity = match.get("severity", "medium").lower()
                cwe = match.get("cwe")
                    
                findings.append({
                    "description": match.get("description", match.get("rule", "Unknown rule")),
                    "severity": severity,
                    "cwe": cwe,
                    "rule": match.get("rule"),
                    "action": match.get("action"),
                    "file": os.path.basename(leaf)
                })
                
    state["yara_results"] = all_yara_results
    save_state(project_id, state)
                
    return {
        "stage": "yara",
        "tool": "yara_scanner",
        "status": "success",
        "findings": findings
    }

def run_symbols(file_path: str, project_id: int) -> dict:
    state = load_state(project_id)
    findings = []
    extra_keywords = state.get("extra_keywords", [])
    
    for leaf in state.get("leaf_binaries", []):
        # We don't have node.file_type easily, assume elf or auto
        res = analyze_symbols(leaf, file_type="elf", extra_keywords=extra_keywords)
        if res.get("success"):
            for sym in res.get("flagged_symbols", []):
                cwe = sym.get("cwe") or "CWE-000"
                findings.append({
                    "description": f"Suspicious symbol found: {sym.get('name')} at {sym.get('address')} in {os.path.basename(leaf)}",
                    "severity": "high",
                    "cwe": cwe,
                    "name": sym.get("name"),
                    "file": os.path.basename(leaf)
                })
                
    return {
        "stage": "symbol_analysis",
        "tool": "symbol_analyzer",
        "status": "success",
        "findings": findings
    }

def run_ghidra(file_path: str, project_id: int) -> dict:
    state = load_state(project_id)
    findings = []
    
    for leaf in state.get("leaf_binaries", []):
        res = scan_with_ghidra(leaf)
        if res.get("success"):
            for f in res.get("findings", []):
                # The headless script returns: vulnerable_api, cwe, category, caller_function, caller_address, decompiled_snippet
                findings.append({
                    "description": f"Ghidra XREF: {f.get('caller_function')} at {f.get('caller_address')} calls {f.get('vulnerable_api')}",
                    "severity": "critical" if f.get("cwe") == "CWE-798" else "high",
                    "cwe": f.get("cwe"),
                    "category": f.get("category"),
                    "file": os.path.basename(leaf),
                })
                
    return {
        "stage": "Reverse Engineering",
        "tool": "ghidra",
        "status": "success",
        "findings": findings
    }

def run_obis_mapper(file_path: str, project_id: int) -> dict:
    state = load_state(project_id)
    findings = []
    
    all_unique_codes = {}
    
    for leaf in state.get("leaf_binaries", []):
        try:
            # We run strings natively to fetch the text block
            result = subprocess.run(
                ["strings", leaf],
                capture_output=True, text=True, timeout=60,
                errors="ignore"
            )
            text = result.stdout
            codes = OBISParser.extract_from_text(text)
            for c in codes:
                all_unique_codes[c['code']] = c
        except Exception as e:
            pass
            
    if all_unique_codes:
        table_lines = ["| OBIS Code | Description | Access |", "|---|---|---|"]
        for c in all_unique_codes.values():
            table_lines.append(f"| {c['code']} | {c['name']} | {c['access']} |")
            
        findings.append({
            "description": "Extracted OBIS Code Map\n\n" + "\n".join(table_lines),
            "severity": "info",
            "cwe": "CWE-200",
            "category": "dlms_obis",
            "file": "Multiple" if len(state.get("leaf_binaries", [])) > 1 else os.path.basename(state.get("leaf_binaries", [])[0])
        })

    return {
        "stage": "Protocol Analysis",
        "tool": "obis_mapper",
        "status": "success",
        "findings": findings
    }

def run_security_suite(file_path: str, project_id: int) -> dict:
    state = load_state(project_id)
    findings = []
    
    is_firmware_dlms = False
    
    # First pass: determine if ANY binary in the firmware is DLMS
    for leaf in state.get("leaf_binaries", []):
        try:
            with open(leaf, "rb") as f:
                data = f.read()
                if b"DLMS" in data.upper() or b"COSEM" in data.upper() or b"OBIS" in data.upper():
                    is_firmware_dlms = True
                    break
        except Exception:
            pass
            
        strings_res = state.get("strings_results", {}).get(leaf, {})
        if strings_res.get("matches", {}).get("dlms_cosem"):
            is_firmware_dlms = True
            break
            
    if not is_firmware_dlms:
        findings.append({
            "description": "Security Suite Verification: Not identified as a DLMS/COSEM binary. Skipping validation.",
            "severity": "info",
            "cwe": "CWE-000",
            "category": "crypto",
            "file": "Overall Firmware"
        })
    else:
        # Second pass: only check crypto constants on leaf binaries if firmware is DLMS
        for leaf in state.get("leaf_binaries", []):
            try:
                with open(leaf, "rb") as f:
                    data = f.read()
                    
                    has_aes = b"AES" in data or b"GCM" in data
                    has_ecdsa = b"ECDSA" in data or b"secp256r1" in data or b"P-256" in data
                    
                    suite = 0
                    if has_ecdsa and has_aes:
                        suite = 2
                    elif has_aes:
                        suite = 1
                        
                    if suite == 0:
                        findings.append({
                            "description": f"Security Suite Verification: DLMS binary lacks strong crypto constants (AES/ECDSA). It may be using Suite 0 (Plaintext), but requires dynamic verification.",
                            "severity": "medium",
                            "cwe": "CWE-319",
                            "category": "weak_crypto",
                            "file": os.path.basename(leaf)
                        })
                    else:
                        findings.append({
                            "description": f"Security Suite Verification: DLMS binary enforces Security Suite {suite}.",
                            "severity": "info",
                            "cwe": "CWE-000",
                            "category": "crypto",
                            "file": os.path.basename(leaf)
                        })
            except Exception:
                pass

    return {
        "stage": "Protocol Analysis",
        "tool": "security_suite",
        "status": "success",
        "findings": findings
    }
