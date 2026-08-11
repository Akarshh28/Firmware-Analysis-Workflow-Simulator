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
            for region in res.get("flagged_regions", []):
                findings.append({
                    "description": f"High entropy region (avg {region['avg_entropy']}) from {region['start_offset']} to {region['end_offset']} in {os.path.basename(leaf)}",
                    "severity": "medium",
                    "cwe": "CWE-310",
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
