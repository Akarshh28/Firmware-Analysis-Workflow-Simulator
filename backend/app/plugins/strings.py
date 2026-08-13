from typing import Dict, Any, List
import asyncio
from app.plugins.base import BaseToolPlugin, ToolInput, ToolOutput
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
# pyrefly: ignore [missing-import]
from backend.analyzer.modules.string_scanner import scan_strings

class StringsPlugin(BaseToolPlugin):
    @property
    def name(self) -> str:
        return "strings"

    @property
    def documentation(self) -> Dict[str, Any]:
        return {
            "purpose": "Extracts hardcoded credentials, URLs, and cryptographic keys.",
            "commands": ["strings -a -n 4 <target_file>"],
            "troubleshooting": "Ensure 'strings' utility is installed on the host system."
        }

    def validate_inputs(self, tool_input: ToolInput) -> bool:
        return os.path.exists(tool_input.target_filepath) or True

    async def execute_real(self, tool_input: ToolInput) -> ToolOutput:
        result = scan_strings(tool_input.target_filepath)
        
        success = result.get("success", False)
        logs = []
        if success:
            logs.append(f"[Strings] Total strings extracted: {result.get('total_strings')}")
            matches = result.get('matches', {})
            for cat, items in matches.items():
                logs.append(f"    - Category: {cat} ({len(items)} matches)")
        else:
            logs.append(f"[Strings] Error: {result.get('error')}")

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
            "[Strings] Extracting raw strings from binary...",
            "[Strings] Applying keyword filtering...",
            "    - Category: auth_credentials (2 matches)",
            "    - Category: network_services (5 matches)",
            "    - Category: crypto_keys (1 match)"
        ]
        return ToolOutput(
            success=True,
            exit_code=0,
            logs=logs,
            generated_files=[],
            parsed_metrics={"total_strings": 10500, "matches_found": 8}
        )
