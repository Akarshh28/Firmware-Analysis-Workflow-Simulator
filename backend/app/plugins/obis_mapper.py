from typing import Dict, Any, List
import asyncio
from app.plugins.base import BaseToolPlugin, ToolInput, ToolOutput
import sys
import os
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
# pyrefly: ignore [missing-import]
from app.obis_parser import OBISParser

class OBISMapperPlugin(BaseToolPlugin):
    @property
    def name(self) -> str:
        return "obis_mapper"

    @property
    def documentation(self) -> Dict[str, Any]:
        return {
            "purpose": "Finds and decodes hardcoded DLMS/COSEM OBIS codes (e.g., 1.0.1.8.0.255) from the firmware.",
            "commands": ["Internal OBIS parser using regex on strings output"],
            "troubleshooting": ""
        }

    def validate_inputs(self, tool_input: ToolInput) -> bool:
        return os.path.exists(tool_input.target_filepath) or True

    async def execute_real(self, tool_input: ToolInput) -> ToolOutput:
        # Run strings to get text, then parse
        try:
            process = await asyncio.create_subprocess_exec(
                "strings", tool_input.target_filepath,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            text = stdout.decode(errors="ignore")
            
            codes = OBISParser.extract_from_text(text)
            # Remove duplicates by code
            unique_codes = {c['code']: c for c in codes}.values()
            
            logs = [f"[OBIS Mapper] Found {len(unique_codes)} unique OBIS codes."]
            for code in unique_codes:
                logs.append(f"    - {code['code']}: {code['name']} ({code['access']})")
                
            return ToolOutput(
                success=True,
                exit_code=0,
                logs=logs,
                generated_files=[],
                parsed_metrics={"obis_codes": list(unique_codes)}
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                exit_code=1,
                logs=[f"[OBIS Mapper] Error: {e}"],
                generated_files=[],
                parsed_metrics={}
            )

    async def execute_simulated(self, tool_input: ToolInput) -> ToolOutput:
        await asyncio.sleep(0.5)
        logs = [
            "[OBIS Mapper] Scanning data segments for OBIS patterns...",
            "[OBIS Mapper] Found 3 unique OBIS codes.",
            "    - 1.0.1.8.0.255: Active Energy Import (+A) (Time Integral) Total (Read)",
            "    - 0.0.96.1.0.255: Device ID / Serial Number (Read)",
            "    - 0.0.96.2.0.255: Configuration Changes Count (Read/Write)"
        ]
        return ToolOutput(
            success=True,
            exit_code=0,
            logs=logs,
            generated_files=[],
            parsed_metrics={
                "obis_codes": [
                    {"code": "1.0.1.8.0.255", "name": "Active Energy Import (+A)", "access": "Read"},
                    {"code": "0.0.96.1.0.255", "name": "Device ID", "access": "Read"}
                ]
            }
        )
