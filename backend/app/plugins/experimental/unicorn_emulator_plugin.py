from typing import Dict, Any, List
import asyncio
from app.plugins.base import BaseToolPlugin, ToolInput, ToolOutput
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
# pyrefly: ignore [missing-import]
from analyzer.modules.unicorn_emulator import run_emulation

class UnicornEmulatorPlugin(BaseToolPlugin):
    @property
    def name(self) -> str:
        return "unicorn_emulator"

    @property
    def documentation(self) -> Dict[str, Any]:
        return {
            "purpose": "Function-Level Emulation for DLMS parsing and Input Mutation fuzzing.",
            "commands": ["Internal Unicorn Engine (ARM/THUMB) execution"],
            "troubleshooting": "Ensure 'unicorn' Python package is installed."
        }

    def validate_inputs(self, tool_input: ToolInput) -> bool:
        return os.path.exists(tool_input.target_filepath) or True

    async def execute_real(self, tool_input: ToolInput) -> ToolOutput:
        # In a real integration, the Ghidra plugin would output the 'function_starts' addresses.
        # Here we retrieve them from the extra_args passed by the orchestrator.
        function_starts = tool_input.extra_args.get("function_starts", [])
        
        try:
            result = run_emulation(tool_input.target_filepath, function_starts)
            
            success = result.get("success", False)
            logs = []
            
            if success:
                logs.append(f"[Unicorn] Successfully loaded firmware code into emulator memory.")
                logs.append(f"[Unicorn] Target functions to emulate: {result.get('emulated_functions')}")
                
                vulns = result.get('vulnerabilities_found', [])
                if vulns:
                    logs.append(f"[Unicorn] WARNING: Found {len(vulns)} crashes during mutation fuzzing!")
                    for vuln in vulns:
                        logs.append(f"    - Function 0x{vuln['function']}: Crashed on payload idx {vuln['payload_index']}")
                        for crash in vuln.get('crashes', []):
                            logs.append(f"      -> {crash['type']} at {crash.get('address')}")
                else:
                    logs.append("[Unicorn] All emulated functions survived mutation fuzzing without crashes.")
            else:
                logs.append(f"[Unicorn] Emulation Failed: {result.get('error')}")
                
            return ToolOutput(
                success=success,
                exit_code=0 if success else 1,
                logs=logs,
                generated_files=[],
                parsed_metrics=result
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                exit_code=1,
                logs=[f"[Unicorn] Unexpected error: {e}"],
                generated_files=[],
                parsed_metrics={}
            )

    async def execute_simulated(self, tool_input: ToolInput) -> ToolOutput:
        await asyncio.sleep(1.0)
        logs = [
            "[Unicorn] Setting up ARM/THUMB emulator context...",
            "[Unicorn] Loading DLMS parser functions at 0x08012A00, 0x08015C20...",
            "[Unicorn] Injecting mutation payloads (Buffer Overflows, Malformed APDUs)...",
            "    - Function 0x08012A00: Passed (No crash)",
            "    - Function 0x08015C20: CRASH DETECTED!",
            "      -> Memory Write Violation at 0x3005A0 (Buffer Overflow)",
            "[Unicorn] Emulation complete. Identified 1 vulnerable parsing function."
        ]
        return ToolOutput(
            success=True,
            exit_code=0,
            logs=logs,
            generated_files=[],
            parsed_metrics={
                "emulated_functions": 2,
                "vulnerabilities_found": [
                    {"function": "0x08015C20", "type": "Memory Write Violation", "address": "0x3005A0"}
                ]
            }
        )
