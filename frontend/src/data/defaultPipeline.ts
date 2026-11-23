import { Pipeline } from "../Types/pipeline";

export const defaultPipeline: Pipeline = {
  id: "pipeline1",
  name: "Firmware Analysis",
  nodes: [
    { id: "1",  toolName: "upload",     stage: "Upload & Ingestion",     description: "Upload Smart Meter Firmware",             status: "idle", progress: 0 },
    { id: "2",  toolName: "strings",    stage: "Identification",          description: "Extract hardcoded keys and URLs",          status: "idle", progress: 0 },
    { id: "3",  toolName: "binwalk",    stage: "Extraction",              description: "Extract embedded filesystem",              status: "idle", progress: 0 },
    { id: "4",  toolName: "cutter",     stage: "Static Analysis",         description: "Visual static analysis via Cutter/Radare2",status: "idle", progress: 0 },
    { id: "5",  toolName: "ghidra",     stage: "Reverse Engineering",     description: "Ghidra Headless Decompilation",            status: "idle", progress: 0 },
    { id: "6",  toolName: "trufflehog", stage: "Secret Detection",        description: "Hardcoded secrets & credential scanning",  status: "idle", progress: 0 },
    { id: "7",  toolName: "entropy",    stage: "Cryptographic Analysis",  description: "Entropy + crypto detection",               status: "idle", progress: 0 },
    { id: "8",  toolName: "wireshark",  stage: "Protocol Analysis",       description: "DLMS/COSEM network protocol analysis",     status: "idle", progress: 0 },
    { id: "9",  toolName: "angr",       stage: "Symbolic Execution",      description: "Path exploration & exploit generation",    status: "idle", progress: 0 },
    { id: "10", toolName: "afl++",      stage: "Fuzzing",                 description: "Coverage-guided fuzzing with AFL++",       status: "idle", progress: 0 },
    { id: "11", toolName: "scorecard",  stage: "Risk Scoring",            description: "CVSS scoring & risk assessment",          status: "idle", progress: 0 },
    { id: "12", toolName: "pdf_report", stage: "Report Generation",       description: "Generate PDF Vulnerability Report",        status: "idle", progress: 0 },
  ],
  edges: [
    { from: "1",  to: "2"  },
    { from: "2",  to: "3"  },
    { from: "3",  to: "4"  },
    { from: "4",  to: "5"  },
    { from: "5",  to: "6"  },
    { from: "6",  to: "7"  },
    { from: "7",  to: "8"  },
    { from: "8",  to: "9"  },
    { from: "9",  to: "10" },
    { from: "10", to: "11" },
    { from: "11", to: "12" },
  ],
};