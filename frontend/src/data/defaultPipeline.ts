import { Pipeline } from "../Types/pipeline";

export const defaultPipeline: Pipeline = {
  id: "pipeline1",
  name: "Firmware Analysis",
  nodes: [
    { id: "1", toolName: "upload", stage: "Upload & Ingestion", description: "Upload Smart Meter Firmware", status: "idle", progress: 0 },
    { id: "2", toolName: "binwalk", stage: "Extraction", description: "Extract embedded filesystem", status: "idle", progress: 0 },
    { id: "3", toolName: "entropy", stage: "Cryptographic Analysis", description: "Entropy + crypto detection", status: "idle", progress: 0 },
    { id: "4", toolName: "strings", stage: "Identification", description: "Extract hardcoded keys and URLs", status: "idle", progress: 0 },
    { id: "5", toolName: "yara", stage: "YARA Analysis", description: "YARA signature scanning", status: "idle", progress: 0 },
    { id: "6", toolName: "symbol_analysis", stage: "Symbol Analysis", description: "Identify suspicious API symbols", status: "idle", progress: 0 },
    { id: "7", toolName: "ghidra", stage: "Reverse Engineering", description: "Ghidra Headless Decompilation", status: "idle", progress: 0 },
    { id: "8", toolName: "obis_mapper", stage: "Protocol Analysis", description: "DLMS OBIS Code Mapping", status: "idle", progress: 0 },
    { id: "9", toolName: "security_suite", stage: "Protocol Analysis", description: "DLMS Security Suite Verification", status: "idle", progress: 0 },
    { id: "10", toolName: "scorecard", stage: "Risk Scoring", description: "CVSS scoring", status: "idle", progress: 0 },
    { id: "11", toolName: "pdf_report", stage: "Report Generation", description: "Generate PDF Vulnerability Report", status: "idle", progress: 0 },
  ],
  edges: [
    { from: "1", to: "2" },
    { from: "2", to: "3" },
    { from: "3", to: "4" },
    { from: "4", to: "5" },
    { from: "5", to: "6" },
    { from: "6", to: "7" },
    { from: "7", to: "8" },
    { from: "8", to: "9" },
    { from: "9", to: "10" },
    { from: "10", to: "11" },
  ],
};