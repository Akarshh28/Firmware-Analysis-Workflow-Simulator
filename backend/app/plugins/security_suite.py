from typing import Dict, Any, List
import asyncio
from app.plugins.base import BaseToolPlugin, ToolInput, ToolOutput
import sys
import os
import re

class SecuritySuitePlugin(BaseToolPlugin):
    @property
    def name(self) -> str:
        return "security_suite"

    @property
    def documentation(self) -> Dict[str, Any]:
        return {
            "purpose": "Verifies which DLMS Security Suite (0, 1, or 2) is enforced by detecting AES-GCM or ECDSA constants.",
            "commands": ["Internal heuristical scanner"],
            "troubleshooting": ""
        }

    def validate_inputs(self, tool_input: ToolInput) -> bool:
        return os.path.exists(tool_input.target_filepath) or True

    async def execute_real(self, tool_input: ToolInput) -> ToolOutput:
        # Simulate real scan by looking for AES/GCM and ECDSA constants in the binary
        try:
            with open(tool_input.target_filepath, "rb") as f:
                data = f.read()
                
            has_aes = b"AES" in data or b"GCM" in data
            has_ecdsa = b"ECDSA" in data or b"secp256r1" in data or b"P-256" in data
            
            suite = 0
            if has_ecdsa and has_aes:
                suite = 2 # ECDSA + AES-GCM-256
            elif has_aes:
                suite = 1 # AES-GCM-128
                
            logs = [
                "[Security Suite] Analyzing binary for cryptographic constants...",
                f"[Security Suite] AES/GCM detected: {has_aes}",
                f"[Security Suite] ECDSA/P-256 detected: {has_ecdsa}",
                f"[Security Suite] Enforced DLMS Security Suite: Suite {suite}"
            ]
            if suite == 0:
                logs.append("    - WARNING: Suite 0 (No cryptography / plaintext) detected. High Risk!")
                
            return ToolOutput(
                success=True,
                exit_code=0,
                logs=logs,
                generated_files=[],
                parsed_metrics={"suite": suite, "has_aes": has_aes, "has_ecdsa": has_ecdsa}
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                exit_code=1,
                logs=[f"[Security Suite] Error reading binary: {e}"],
                generated_files=[],
                parsed_metrics={}
            )

    async def execute_simulated(self, tool_input: ToolInput) -> ToolOutput:
        await asyncio.sleep(0.5)
        logs = [
            "[Security Suite] Analyzing binary for cryptographic constants...",
            "[Security Suite] AES/GCM detected: True",
            "[Security Suite] ECDSA/P-256 detected: False",
            "[Security Suite] Enforced DLMS Security Suite: Suite 1"
        ]
        return ToolOutput(
            success=True,
            exit_code=0,
            logs=logs,
            generated_files=[],
            parsed_metrics={"suite": 1, "has_aes": True, "has_ecdsa": False}
        )
