import sys
import os
import json

# Add current path so we can import our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from analyzer.modules.entropy_analysis import analyze_entropy
from analyzer.modules.extractor import walk_and_extract, flatten_tree

def run_stage_1(target_bin: str):
    print("="*60)
    print(f" FAWS STAGE 1 - PRE-ANALYSIS & EXTRACTION ")
    print("="*60)
    
    if not os.path.exists(target_bin):
        print(f"[!] Error: File '{target_bin}' not found.")
        return

    # STEP 1: ENTROPY ANALYSIS
    print(f"\n[*] Step A: Running Entropy Analysis (scipy) on {target_bin}...")
    entropy_result = analyze_entropy(target_bin)
    
    if not entropy_result.get("success"):
        print(f"[!] Entropy scan failed: {entropy_result.get('error')}")
    else:
        print(f"  - Scanned {entropy_result.get('windows_scanned')} windows.")
        print(f"  - Verdict: {entropy_result.get('verdict').upper()}")
        flagged = entropy_result.get("flagged_regions", [])
        if flagged:
            print(f"  - [WARNING] Found {len(flagged)} high entropy regions (Likely encrypted/compressed):")
            for r in flagged:
                print(f"      -> Offset {r['start_offset']} to {r['end_offset']} | Avg Entropy: {r['avg_entropy']}")
        else:
            print("  - [OK] No highly encrypted regions detected.")

    # STEP 2: BINWALK EXTRACTION
    print(f"\n[*] Step B: Running Binwalk Extraction...")
    print("  - Note: On Windows, this relies on WSL (wsl bash -c 'binwalk ...')")
    
    work_dir = os.path.join(current_dir, "data", "cli_extraction")
    os.makedirs(work_dir, exist_ok=True)
    
    print(f"  - Extracting to: {work_dir}")
    try:
        tree_root = walk_and_extract(target_bin, work_dir, max_depth=3)
        all_nodes = flatten_tree(tree_root)
        
        print("\n[*] Extraction Results:")
        for node in all_nodes:
            indent = "  " * node.depth
            status_symbol = "✅" if node.status == "ok" else "❌" if node.status == "error" else "⏭️"
            name = os.path.basename(node.path)
            print(f"{indent}{status_symbol} {name} [{node.status.upper()}] - {node.status_detail}")
            
    except Exception as e:
        print(f"[!] Extraction crashed: {e}")

    print("\n" + "="*60)
    print(" Stage 1 Complete!")
    print("="*60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python stage1_cli.py <path_to_firmware.bin>")
        sys.exit(1)
        
    run_stage_1(sys.argv[1])
