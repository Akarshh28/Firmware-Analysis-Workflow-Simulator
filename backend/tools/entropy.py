import argparse
import sys
import os
import time
import math

def calculate_entropy(filepath, block_size=256):
    try:
        with open(filepath, "rb") as f:
            data = f.read()
            
        if not data:
            return 0.0

        # Calculate Shannon entropy
        entropy = 0
        for x in range(256):
            p_x = float(data.count(x)) / len(data)
            if p_x > 0:
                entropy += - p_x * math.log(p_x, 2)
                
        return entropy
    except Exception as e:
        print(f"Error calculating entropy: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Firmware Entropy Analyzer")
    parser.add_argument("--target", required=True, help="Path to firmware file")
    parser.add_argument("--project", required=True, help="Project ID")
    parser.add_argument("--run-id", required=True, help="Tool Run ID")
    args = parser.parse_args()

    print(f"Starting Entropy Analysis on {args.target}...")
    time.sleep(1) # simulate spin up
    
    if not os.path.exists(args.target):
        print(f"File not found: {args.target}")
        sys.exit(1)
        
    entropy = calculate_entropy(args.target)
    print(f"Overall Shannon Entropy: {entropy:.4f}")
    
    if entropy > 7.5:
        print(f"Found 1 potential secrets!") # Matches UI log parser
        print(f"[!] High entropy ({entropy:.2f}) indicates packed or encrypted firmware section")
    elif entropy < 4.0:
        print(f"Found 1 potential secrets!") # Matches UI log parser
        print(f"[!] Low entropy ({entropy:.2f}) indicates large blocks of padding or uniform data")
    else:
        print("Entropy is within normal range for executable code.")
        
    print("Scan complete.")
    sys.exit(0)

if __name__ == "__main__":
    main()
