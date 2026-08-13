from typing import Dict, Any, List
import asyncio
from app.plugins.base import BaseToolPlugin, ToolInput, ToolOutput
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
# pyrefly: ignore [missing-import]
from backend.analyzer.modules.entropy_analysis import analyze_entropy

class EntropyPlugin(BaseToolPlugin):
    @property
    def name(self) -> str:
        return "entropy"

    @property
    def documentation(self) -> Dict[str, Any]:
        return {
            "purpose": "Shannon entropy scan using scipy to identify encrypted/compressed regions.",
            "commands": ["Internal python script using scipy.stats.entropy"],
            "troubleshooting": "Ensure scipy and numpy are installed."
        }

    def validate_inputs(self, tool_input: ToolInput) -> bool:
        return os.path.exists(tool_input.target_filepath) or True # Allow true for simulation

    async def execute_real(self, tool_input: ToolInput) -> ToolOutput:
        # Run the existing module synchronously but wrapped in an async function
        result = analyze_entropy(tool_input.target_filepath)
        
        success = result.get("success", False)
        logs = []
        if success:
            logs.append(f"[Entropy] Analyzed {result.get('windows_scanned')} windows.")
            logs.append(f"[Entropy] Verdict: {result.get('verdict')}")
            for region in result.get('flagged_regions', []):
                logs.append(f"    - Flagged region: 0x{region['start_offset']:X} to 0x{region['end_offset']:X} (Avg Entropy: {region['avg_entropy']})")
        else:
            logs.append(f"[Entropy] Error: {result.get('error')}")

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
            "[Entropy] Scanning firmware blocks...",
            "[Entropy] Calculating Shannon entropy using scipy...",
            "[Entropy] Verdict: possible_compression_or_encryption",
            "    - Flagged region: 0x80000 to 0x100000 (Avg Entropy: 0.92)"
        ]
        return ToolOutput(
            success=True,
            exit_code=0,
            logs=logs,
            generated_files=[],
            parsed_metrics={"verdict": "possible_compression_or_encryption"}
        )
