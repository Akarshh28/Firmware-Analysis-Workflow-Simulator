import argparse
import sys
import os
import time

def analyze_pcap(filepath):
    findings = []
    try:
        with open(filepath, "rb") as f:
            data = f.read(1024)
            # PCAP magic numbers: a1b2c3d4 or d4c3b2a1
            # PCAPNG magic numbers: 0A 0D 0D 0A
            if data.startswith(b"\xa1\xb2\xc3\xd4") or data.startswith(b"\xd4\xc3\xb2\xa1"):
                findings.append({"type": "Network", "match": "Valid PCAP file detected"})
            elif data.startswith(b"\x0a\x0d\x0d\x0a"):
                findings.append({"type": "Network", "match": "Valid PCAPNG file detected"})
                
        with open(filepath, "rb") as f:
             data = f.read()
             if b"HTTP/1.1" in data or b"HTTP/1.0" in data:
                 findings.append({"type": "Network", "match": "HTTP traffic signatures found"})
             if b"ssh-rsa" in data or b"SSH-2.0" in data:
                 findings.append({"type": "Network", "match": "SSH traffic signatures found"})
                
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    return findings

def main():
    parser = argparse.ArgumentParser(description="Basic Wireshark Python Fallback")
    parser.add_argument("--target", required=True, help="Path to firmware file")
    parser.add_argument("--project", required=True, help="Project ID")
    parser.add_argument("--run-id", required=True, help="Tool Run ID")
    args = parser.parse_args()

    print(f"Starting Wireshark (Lightweight Fallback) on {args.target}...")
    time.sleep(1)
    
    if not os.path.exists(args.target):
        print(f"File not found: {args.target}")
        sys.exit(1)
        
    findings = analyze_pcap(args.target)
    
    if findings:
        print(f"Found {len(findings)} finding(s).")
        for f in findings:
            print(f"[!] {f['type']}: {f['match']}")
            time.sleep(0.2)
    else:
        print("No interesting network packets found.")
        
    print("Scan complete.")
    sys.exit(0)

if __name__ == "__main__":
    main()
