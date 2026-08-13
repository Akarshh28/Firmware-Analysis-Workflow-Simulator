# dlms_analyzer.py - Ghidra Headless Analyzer script
# Analyzes DLMS/COSEM binaries for unsafe functions and extracts OBIS codes.

import os
import json
import string
from ghidra.app.util.headless import HeadlessScript
from ghidra.program.model.symbol import SourceType
from ghidra.program.model.listing import CodeUnit

# Ensure we're running as a script
if "currentProgram" not in globals():
    currentProgram = None # Will be populated by Ghidra

def get_args():
    args = getScriptArgs()
    if len(args) < 1:
        print("Usage: analyzeHeadless ... -postScript dlms_analyzer.py <output.json>")
        return None
    return args[0]

def analyze_unsafe_functions():
    unsafe_funcs = ["strcpy", "sprintf", "strcat", "gets", "memcpy", "memmove"]
    findings = []
    
    fm = currentProgram.getFunctionManager()
    funcs = fm.getFunctions(True) # Forward iterator
    
    for func in funcs:
        func_name = func.getName()
        if func_name in unsafe_funcs:
            # Get cross-references to this function
            entry_point = func.getEntryPoint()
            refs = getReferencesTo(entry_point)
            
            for ref in refs:
                caller_addr = ref.getFromAddress()
                caller_func = fm.getFunctionContaining(caller_addr)
                caller_name = caller_func.getName() if caller_func else "unknown_function"
                
                findings.append({
                    "type": "unsafe_function_call",
                    "target": func_name,
                    "caller": caller_name,
                    "address": caller_addr.toString(),
                    "severity": "high" if func_name in ["strcpy", "gets", "sprintf"] else "medium"
                })
                
    return findings

def extract_obis_codes():
    """
    Heuristically extracts potential OBIS codes (e.g., 1.0.99.1.0.255) from data sections.
    """
    findings = []
    memory = currentProgram.getMemory()
    blocks = memory.getBlocks()
    
    # OBIS pattern: "x.x.x.x.x.x" roughly translates to 6 bytes in memory (often prefixed or structured)
    # We will just look for strings that look like OBIS codes in ASCII representation.
    
    listing = currentProgram.getListing()
    data_iterator = listing.getDefinedData(True)
    
    for data in data_iterator:
        val = data.getValue()
        if isinstance(val, basestring) and len(val) >= 11: # A minimal OBIS string length e.g. 1.0.0.0.0.0
            if val.count('.') >= 3 and all(c in string.digits + '.' for c in val.strip()):
                findings.append({
                    "type": "obis_code",
                    "value": val.strip(),
                    "address": data.getMinAddress().toString(),
                    "severity": "info"
                })
                
    return findings
    
def check_mbedtls():
    """
    Checks for presence of mbedTLS and specific GCM suites.
    """
    findings = []
    fm = currentProgram.getFunctionManager()
    funcs = fm.getFunctions(True)
    
    mbedtls_found = False
    gcm_found = False
    
    for func in funcs:
        name = func.getName()
        if "mbedtls" in name.lower():
            mbedtls_found = True
        if "gcm" in name.lower() or "aes_gcm" in name.lower():
            gcm_found = True
            
    if mbedtls_found:
        findings.append({
            "type": "crypto_library",
            "library": "mbedTLS",
            "supports_gcm": gcm_found,
            "severity": "info" if gcm_found else "medium",
            "message": "mbedTLS found. AES-GCM is " + ("enabled." if gcm_found else "NOT enabled (potential downgrade risk).")
        })
        
    return findings

def run():
    output_file = get_args()
    if not output_file:
        return
        
    print("Starting DLMS/COSEM Firmware Analysis...")
    
    all_findings = []
    
    all_findings.extend(analyze_unsafe_functions())
    all_findings.extend(extract_obis_codes())
    all_findings.extend(check_mbedtls())
    
    # Identify potential DLMS parser functions to feed to Unicorn
    # Heuristic: functions containing "dlms", "cosem", "parse", "apdu"
    parser_funcs = []
    fm = currentProgram.getFunctionManager()
    funcs = fm.getFunctions(True)
    for func in funcs:
        name = func.getName().lower()
        if "dlms" in name or "apdu" in name or ("parse" in name and "frame" in name):
            parser_funcs.append({
                "type": "dlms_parser_function",
                "name": func.getName(),
                "address": func.getEntryPoint().toString(),
                "severity": "info"
            })
            
    all_findings.extend(parser_funcs)
    
    try:
        with open(output_file, 'w') as f:
            json.dump(all_findings, f, indent=4)
        print("Analysis complete. Findings written to: " + output_file)
    except Exception as e:
        print("Error writing output file: " + str(e))

if __name__ == "__main__":
    run()
