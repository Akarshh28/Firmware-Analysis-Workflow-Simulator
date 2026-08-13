from typing import Dict, Any, List
import asyncio
from app.plugins.base import BaseToolPlugin, ToolInput, ToolOutput
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
# pyrefly: ignore [missing-import]
from backend.analyzer.modules.yara_scanner import scan_with_yara

class YaraPlugin(BaseToolPlugin):
    @property
    def name(self) -> str:
        return "yara"

    @property
    def documentation(self) -> Dict[str, Any]:
        return {
            "purpose": "Pattern matching for known crypto libraries (mbedTLS) and unsafe functions (strcpy).",
            "commands": ["yara -r rules/ <target_file>"],
            "troubleshooting": "Ensure yara-python is installed and rules are present."
        }

    def validate_inputs(self, tool_input: ToolInput) -> bool:
        return os.path.exists(tool_input.target_filepath) or True

    async def execute_real(self, tool_input: ToolInput) -> ToolOutput:
        result = scan_with_yara(tool_input.target_filepath)
        
        success = result.get("success", False)
        logs = []
        if success:
            matches = result.get('matches', [])
            logs.append(f"[YARA] Scan completed. Found {len(matches)} rule matches.")
            for match in matches:
                logs.append(f"    - Rule: {match['rule']} (Severity: {match['severity']}, CWE: {match['cwe']})")
        else:
            logs.append(f"[YARA] Error: {result.get('error')}")

        return ToolOutput(
            success=success,
            exit_code=0 if success else 1,
            logs=logs,
            generated_files=[],
            parsed_metrics=result
        )

    async def execute_simulated(self, tool_input: ToolInput) -> ToolOutput:
        await asyncio.sleep(0.5)
        logs = [
            "[YARA] Compiling ruleset...",
            "[YARA] Scanning firmware...",
            "    - Rule: Unsafe_String_Functions (Severity: low, CWE: CWE-120)",
            "    - Rule: Crypto_mbedTLS_Library (Severity: info)"
        ]
        return ToolOutput(
            success=True,
            exit_code=0,
            logs=logs,
            generated_files=[],
            parsed_metrics={"matches": 2}
        )
