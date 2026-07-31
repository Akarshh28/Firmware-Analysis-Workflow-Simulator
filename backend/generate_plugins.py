import os

tools = {
    'upload': ('UploadPlugin', 'Upload Firmware', 'Handles uploading firmware images.'),
    'strings': ('StringsPlugin', 'Strings Extraction', 'Extract and analyze ASCII/Unicode strings from binary.'),
    'cutter': ('CutterPlugin', 'Cutter Static Analysis', 'Perform static analysis and reversing using Cutter.'),
    'ghidra': ('GhidraPlugin', 'Ghidra Decompilation', 'Decompile and analyze binary using Ghidra headlessly.'),
    'trufflehog': ('TrufflehogPlugin', 'Secret Detection', 'Scan binary and extracted files for hardcoded secrets.'),
    'entropy': ('EntropyPlugin', 'Entropy Analysis', 'Calculate and visualize Shannon entropy to detect packed/encrypted data.'),
    'wireshark': ('WiresharkPlugin', 'Network Analysis', 'Analyze PCAP files or network dumps.'),
    'afl++': ('AflPlugin', 'AFL++ Fuzzing', 'Perform dynamic analysis and fuzzing via AFL++.'),
    'scorecard': ('ScorecardPlugin', 'Risk Scoring', 'Calculate overall risk score (CVSS) based on findings.'),
    'pdf_report': ('PdfReportPlugin', 'PDF Reporting', 'Generate comprehensive analysis report in PDF format.')
}

template = """import os
import asyncio
from typing import Dict, Any
from app.plugins.base import BaseToolPlugin, ToolInput, ToolOutput

class {class_name}(BaseToolPlugin):
    @property
    def name(self) -> str:
        return "{tool_name}"

    @property
    def version(self) -> str:
        return "v1.0.0 (Simulated)"

    @property
    def documentation(self) -> Dict[str, Any]:
        return {{
            "purpose": "{purpose}",
            "input": "Firmware file or extracted artifacts.",
            "output": "Analysis results and generated artifacts.",
            "workflow": "Standard stage of cybersecurity pipeline",
            "internal_working": "Executes '{tool_name}' on the target.",
            "commands": [
                {{
                    "command": "{tool_name} --help",
                    "explanation": "Display help for {tool_name}"
                }}
            ],
            "common_errors": ["Tool not configured properly in PATH."],
            "troubleshooting": "Check execution logs for details.",
            "best_practices": "Run in an isolated environment.",
            "references": ["C3iHub Smart Meter Analysis wiki"]
        }}

    def validate_inputs(self, tool_input: ToolInput) -> bool:
        return True

    async def execute_real(self, tool_input: ToolInput) -> ToolOutput:
        return await self.execute_simulated(tool_input)

    async def execute_simulated(self, tool_input: ToolInput) -> ToolOutput:
        await asyncio.sleep(1.0)
        return ToolOutput(
            success=True,
            exit_code=0,
            logs=[{{"log_type": "SYSTEM", "message": "Simulated execution of {tool_name} completed."}}],
            generated_files=[],
            parsed_metrics={{}}
        )
"""

base_dir = r'C:\Users\akars\OneDrive\Desktop\Firmware Analysis workflow simulator\backend\app\plugins'

for tool_name, (class_name, title, purpose) in tools.items():
    file_name = f"{tool_name.replace('+', '')}.py"
    path = os.path.join(base_dir, file_name)
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(template.format(
                class_name=class_name,
                tool_name=tool_name,
                title=title,
                purpose=purpose
            ))
        print(f'Created {file_name}')
