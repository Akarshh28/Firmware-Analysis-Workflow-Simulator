# Ghidra Headless Analyzer Script for FAWS
# Runs under Jython 2.7 in Ghidra environment
# @category FAWS_Security

import sys
import os
import json
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
from ghidra.program.model.symbol import RefType

# SENSITIVE_APIS maps API/Function substrings to their security categories
SENSITIVE_APIS = {
    "strcpy": ("CWE-120", "unsafe_functions"),
    "strcat": ("CWE-120", "unsafe_functions"),
    "sprintf": ("CWE-120", "unsafe_functions"),
    "memmove": ("CWE-120", "unsafe_functions"),
    "MD5": ("CWE-327", "weak_crypto"),
    "DES": ("CWE-327", "weak_crypto"),
    "RC4": ("CWE-327", "weak_crypto"),
    "SHA1": ("CWE-327", "weak_crypto"),
    "Password": ("CWE-798", "auth_credentials"),
    "Login": ("CWE-798", "auth_credentials"),
    "ftp": ("CWE-319", "network_services"),
    "ssh": ("CWE-319", "network_services"),
    "socket": ("CWE-319", "network_services")
}

def get_category_and_cwe(func_name):
    for key, (cwe, cat) in SENSITIVE_APIS.items():
        if key.lower() in func_name.lower():
            return cwe, cat
    return None, None

def analyze_firmware():
    print("[FAWS-Ghidra] Starting Headless Analysis on: " + currentProgram.getName())
    
    # Initialize Decompiler
    decompiler = DecompInterface()
    decompiler.openProgram(currentProgram)
    monitor = ConsoleTaskMonitor()
    
    fm = currentProgram.getFunctionManager()
    funcs = fm.getFunctions(True) # True means forward iterator
    
    findings = []
    
    for func in funcs:
        func_name = func.getName()
        cwe, cat = get_category_and_cwe(func_name)
        
        # If it's an interesting function (e.g., strcpy)
        if cwe and cat:
            print("[FAWS-Ghidra] Found sensitive target: " + func_name)
            
            # Find cross references to this function
            entry_point = func.getEntryPoint()
            references = getReferencesTo(entry_point)
            
            callers = set()
            for ref in references:
                if ref.getReferenceType().isCall():
                    caller_addr = ref.getFromAddress()
                    caller_func = fm.getFunctionContaining(caller_addr)
                    if caller_func:
                        callers.add(caller_func)
            
            for caller in callers:
                # Decompile caller
                decomp_results = decompiler.decompileFunction(caller, 30, monitor)
                decompiled_code = ""
                if decomp_results and decomp_results.decompileCompleted():
                    decompiled_code = decomp_results.getDecompiledFunction().getC()
                
                # Truncate large code blocks
                if len(decompiled_code) > 1000:
                    decompiled_code = decompiled_code[:1000] + "\n...[TRUNCATED]"
                
                finding = {
                    "vulnerable_api": func_name,
                    "cwe": cwe,
                    "category": cat,
                    "caller_function": caller.getName(),
                    "caller_address": str(caller.getEntryPoint()),
                    "decompiled_snippet": decompiled_code
                }
                findings.append(finding)
                
    # Parse CLI args to find output file path (Ghidra headless passes args after script name)
    args = getScriptArgs()
    output_path = args[0] if args else "ghidra_findings.json"
    
    print("[FAWS-Ghidra] Saving findings to: " + output_path)
    with open(output_path, "w") as f:
        # Jython json.dump works, but we manually format to ensure compatibility
        json.dump(findings, f, indent=4)
        
    print("[FAWS-Ghidra] Analysis Complete.")

if __name__ == "__main__":
    analyze_firmware()
