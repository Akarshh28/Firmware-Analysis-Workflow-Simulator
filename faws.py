#!/usr/bin/env python3
"""
faws.py - Firmware Analysis Workflow Simulator CLI Wrapper
Orchestrates the 5-Stage hardware-level security analysis framework with strict data validation.
"""

import argparse
import os
import sys
import json
from datetime import datetime

# Setup paths so backend modules can be imported
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
analyzer_path = os.path.join(backend_path, "analyzer")
sys.path.insert(0, backend_path)
sys.path.insert(0, analyzer_path)
# pyright: ignore[reportMissingImports]
from analyzer.modules import entropy_analysis, extractor, ghidra_scanner, string_scanner, yara_scanner
# pyright: ignore[reportMissingImports]
from analyzer.modules import report_generator

def stage0_and_1_pre_processing(firmware_path, out_dir):
    print("\n--- [Step 0 & 1] Pre-Processing & Extraction ---")
    
    # STEP 0: Force extraction FIRST
    print(f"[*] Running Extractor (binwalk/unzip/cabextract) on {firmware_path}...")
    extract_tree = extractor.walk_and_extract(firmware_path, out_dir)
    nodes = extractor.flatten_tree(extract_tree)
    
    # STEP 1: Strict Target Filtering
    # Exclude non-executable noise like translation files and windows installers
    ignored_extensions = {".lan", ".dat", ".txt", ".exe", ".zip", ".msi", ".pdf", ".xml"}
    valid_binaries = []
    
    for node in nodes:
        if node.status != "ok" or node.container_kind is not None:
            continue # Skip errors and containers (already extracted)
            
        ext = os.path.splitext(node.path)[1].lower()
        if ext in ignored_extensions:
            print(f"    [-] Ignoring non-executable file: {os.path.basename(node.path)}")
            continue
            
        # Optional: Magic byte checks can be done here using the `file_type` from extractor
        if "executable" in node.file_type.lower() or "elf" in node.file_type.lower() or ext in [".bin", ".hex"]:
            valid_binaries.append(node.path)
        else:
            # Fallback for raw blobs
            valid_binaries.append(node.path)
            
    print(f"[*] Extraction complete. {len(valid_binaries)} valid binary targets found out of {len(nodes)} total nodes.")
    return valid_binaries

def stage2_static_analysis(valid_binaries):
    print("\n--- [Step A] Context-Aware Static Analysis ---")
    
    results = {}
    for binary in valid_binaries:
        print(f"[*] Analyzing {os.path.basename(binary)}...")
        
        # 1. Entropy Check
        ent_res = entropy_analysis.analyze_entropy(binary)
        entropy_score = ent_res.get("average_entropy", 0.0)
        print(f"    Average Entropy: {entropy_score:.2f}/8.0")
        
        if entropy_score > 7.04:
            print("    [!] HIGH ENTROPY DETECTED (>88% / 7.04). File is likely packed/encrypted.")
            print("    [!] Skipping Strings and YARA analysis to prevent false positives.")
            results[binary] = {"entropy": ent_res, "status": "Requires Unpacking"}
            continue
            
        # 2. Strings & YARA (Only for non-packed executables)
        print("    Running Strings Scanner...")
        str_res = string_scanner.scan_strings(binary)
        
        print("    Running YARA Scanner...")
        yara_res = yara_scanner.scan_with_yara(binary)
        
        print("    Running Ghidra Headless...")
        ghidra_res = ghidra_scanner.scan_with_ghidra(binary)
        
        results[binary] = {
            "entropy": ent_res,
            "strings": str_res,
            "yara": yara_res,
            "ghidra": ghidra_res,
            "status": "Analyzed"
        }
        
    return results


def stage4_reporting(results, out_dir):
    print("\n--- [Stage 4] Reporting & Orchestration ---")
    print(f"[*] Generating Vulnerability Assessment Report in {out_dir}...")
    
    # Pass results to report generator if needed
    report_generator.generate_pdf_report(results, out_dir)
    print("    Report generated successfully.")
    


def main():
    parser = argparse.ArgumentParser(description="FAWS: Firmware Analysis Workflow Simulator")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    scan_parser = subparsers.add_parser("scan", help="Run full 4-stage pipeline on a firmware binary")
    scan_parser.add_argument("firmware_path", type=str, help="Path to the firmware binary")
    scan_parser.add_argument("-o", "--output", type=str, default="./faws_output", help="Output directory")
    

    
    args = parser.parse_args()
    
    if args.command == "scan":
        if not os.path.exists(args.firmware_path):
            print(f"Error: File {args.firmware_path} not found.")
            sys.exit(1)
            
        os.makedirs(args.output, exist_ok=True)
        
        valid_binaries = stage0_and_1_pre_processing(args.firmware_path, args.output)
        if not valid_binaries:
            print("[-] No valid targets found for analysis. Exiting.")
            sys.exit(0)
            
        static_results = stage2_static_analysis(valid_binaries)
        final_results = {"static": static_results}
        stage4_reporting(final_results, args.output)
        
        print("\n[+] Full pipeline completed.")
        


if __name__ == "__main__":
    main()
