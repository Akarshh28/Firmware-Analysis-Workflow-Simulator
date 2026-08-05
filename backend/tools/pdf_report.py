import argparse
import sys
import os
import time

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.report_generator import generate_report

def main():
    parser = argparse.ArgumentParser(description="PDF Report Generation")
    parser.add_argument("--target", required=True, help="Path to firmware file")
    parser.add_argument("--project", required=True, help="Project ID")
    parser.add_argument("--run-id", required=True, help="Tool Run ID")
    args = parser.parse_args()

    print(f"Starting PDF Report Generation on project {args.project}...")
    time.sleep(1)
    
    try:
        # Note: generate_report writes the PDF file to disk and registers the Artifact in DB
        generate_report(int(args.project))
        print("PDF generation successful.")
    except Exception as e:
        print(f"Error generating PDF report: {e}")
        sys.exit(1)
        
    print("Report generation complete.")
    sys.exit(0)

if __name__ == "__main__":
    main()
