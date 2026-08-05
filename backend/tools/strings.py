import argparse
import sys
import re
import os
import time

def extract_strings(filepath, min_length=4):
    strings = []
    try:
        with open(filepath, "rb") as f:
            data = f.read()
            
            # Simple ASCII string extraction
            current_string = ""
            for byte in data:
                if 32 <= byte <= 126:  # Printable ASCII
                    current_string += chr(byte)
                else:
                    if len(current_string) >= min_length:
                        strings.append(current_string)
                    current_string = ""
                    
            if len(current_string) >= min_length:
                strings.append(current_string)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
        
    return strings

def analyze_strings(strings):
    findings = []
    
    # regex patterns for interesting things
    patterns = {
        "IPv4_ADDRESS": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        "URL": r"https?://[^\s/$.?#].[^\s]*",
        "FILE_PATH": r"(?:/[a-zA-Z0-9_\-\.]+)+",
        "PRIVATE_KEY_MARKER": r"-----BEGIN RSA PRIVATE KEY-----"
    }
    
    for s in strings:
        for p_name, p_regex in patterns.items():
            if re.search(p_regex, s):
                findings.append({
                    "type": p_name,
                    "match": s
                })
                
    return findings

def main():
    parser = argparse.ArgumentParser(description="Basic Strings Extraction & Analysis")
    parser.add_argument("--target", required=True, help="Path to firmware file")
    parser.add_argument("--project", required=True, help="Project ID")
    parser.add_argument("--run-id", required=True, help="Tool Run ID")
    args = parser.parse_args()

    print(f"Starting Strings Analysis on {args.target}...")
    time.sleep(1) # simulate spin up
    
    if not os.path.exists(args.target):
        print(f"File not found: {args.target}")
        sys.exit(1)
        
    extracted = extract_strings(args.target)
    print(f"Extracted {len(extracted)} strings.")
    
    findings = analyze_strings(extracted)
    
    if findings:
        print(f"Found {len(findings)} finding(s).") # Matches UI log parser
        # limit to 10 findings so we don't spam the DB
        for f in findings[:10]:
            print(f"[!] {f['type']}: {f['match']}")
            time.sleep(0.2)
    else:
        print("No interesting strings found (URLs, IPs, etc.).")
        
    print("Scan complete.")
    sys.exit(0)

if __name__ == "__main__":
    main()
