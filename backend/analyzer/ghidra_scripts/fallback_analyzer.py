# fallback_analyzer.py - Ghidra Headless Analyzer script
# Analyzes stripped binaries to recover functions and decompiles those matching given keywords.

import os
import json
from ghidra.app.util.headless import HeadlessScript
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

if "currentProgram" not in globals():
    currentProgram = None # Will be populated by Ghidra

def get_args():
    args = getScriptArgs()
    if len(args) < 2:
        print("Usage: analyzeHeadless ... -postScript fallback_analyzer.py <output.json> <comma_separated_keywords>")
        return None, None
    return args[0], args[1]

def run():
    output_file, keywords_str = get_args()
    if not output_file:
        return
        
    keywords = [k.strip().lower() for k in keywords_str.split(",") if k.strip()]
    
    print("Starting Ghidra Fallback Analysis for stripped binary...")
    
    findings = []
    
    # Initialize decompiler
    decompInterface = DecompInterface()
    decompInterface.openProgram(currentProgram)
    monitor = ConsoleTaskMonitor()
    
    fm = currentProgram.getFunctionManager()
    funcs = fm.getFunctions(True)
    
    for func in funcs:
        name = func.getName()
        name_lower = name.lower()
        
        # Check if function name matches any of the keywords
        match_found = False
        for kw in keywords:
            if kw in name_lower:
                match_found = True
                break
                
        if match_found:
            # Try to decompile
            disassembly = ""
            status = "ok"
            try:
                results = decompInterface.decompileFunction(func, 30, monitor) # 30 seconds timeout per function
                if results.decompileCompleted():
                    disassembly = results.getDecompiledFunction().getC()
                else:
                    status = "error"
                    disassembly = "Decompilation failed or timed out."
            except Exception as e:
                status = "error"
                disassembly = str(e)
                
            findings.append({
                "name": name,
                "address": hex(func.getEntryPoint().getOffset()),
                "size": int(func.getBody().getNumAddresses()),
                "disassembly_status": status,
                "disassembly": disassembly
            })
            
    try:
        with open(output_file, 'w') as f:
            json.dump(findings, f, indent=4)
        print("Fallback analysis complete. Findings written to: " + output_file)
    except Exception as e:
        print("Error writing output file: " + str(e))

if __name__ == "__main__":
    run()
