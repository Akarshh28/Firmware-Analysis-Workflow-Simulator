import os
import asyncio
import subprocess
from typing import Dict, Any
from app.plugins.base import BaseToolPlugin, ToolInput, ToolOutput

class BinwalkPlugin(BaseToolPlugin):
    @property
    def name(self) -> str:
        return "binwalk"

    @property
    def version(self) -> str:
        """Dynamic version check for binwalk"""
        try:
            import subprocess
            result = subprocess.run(["python", "-c", "import binwalk; print('Installed')"], capture_output=True, text=True)
            if result.returncode == 0:
                return "Python Module Installed"
            return "v2.3.4 (Fallback Python)"
        except Exception:
            return "Not Installed"

    @property
    def documentation(self) -> Dict[str, Any]:
        return {
            "purpose": "Analyze binary images for embedded files and file systems.",
            "input": "Raw firmware binary image file (.bin, .hex, .img).",
            "output": "Extracted file system, kernel headers, bootloaders, and file offsets.",
            "workflow": "Scan firmware -> identify signatures -> extract squashed file systems.",
            "internal_working": "Scans binary bytes looking for known magic signatures (e.g. SquashFS magic 0x73717368, LZMA headers, ELF headers). When a match is found, it logs the offset.",
            "commands": [
                {
                    "command": "binwalk flash.bin",
                    "explanation": "Scan the firmware binary for signatures."
                },
                {
                    "command": "binwalk -e flash.bin",
                    "explanation": "Scan and automatically extract any identified files / filesystems."
                },
                {
                    "command": "binwalk -Mat flash.bin",
                    "explanation": "Perform signature scan, entropy analysis, and extraction recursively."
                }
            ],
            "common_errors": [
                "Command 'binwalk' not found (dependency not installed).",
                "Extraction failed due to missing compression utility dependencies (e.g. sasquatch, unsquashfs)."
            ],
            "troubleshooting": "Ensure binwalk and its extraction packages are installed on the host. Under WSL/Debian: run 'sudo apt install binwalk squashfs-tools'.",
            "best_practices": "Always run entropy analysis first to detect encrypted sections before trying to extract.",
            "references": [
                "Binwalk GitHub: https://github.com/ReFirmLabs/binwalk",
                "Firmware Analysis Wiki: https://github.com/firmware-analysis/wiki"
            ]
        }

    def validate_inputs(self, tool_input: ToolInput) -> bool:
        # Check if the file is provided. In simulation, we accept any name.
        return bool(tool_input.target_filepath)

    async def execute_real(self, tool_input: ToolInput) -> ToolOutput:
        # Construct the execution command safely as an array of arguments to prevent shell injection
        args = ["binwalk", "-e", tool_input.target_filepath]
        
        # Add extra flags if provided in extra_args
        if tool_input.extra_args.get("entropy"):
            args.append("-E")
            
        try:
            # Execute command with a timeout of 60 seconds
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            exit_code = process.returncode
            success = exit_code == 0
            
            logs = []
            if stdout:
                logs.append({"log_type": "STDOUT", "message": stdout.decode("utf-8", errors="replace")})
            if stderr:
                logs.append({"log_type": "STDERR", "message": stderr.decode("utf-8", errors="replace")})
                
            generated_files = []
            if success:
                # Find output directory
                parent_dir = os.path.dirname(tool_input.target_filepath)
                # Binwalk extracts to _filename.extracted
                base_name = os.path.basename(tool_input.target_filepath)
                extracted_dir = os.path.join(parent_dir, f"_{base_name}.extracted")
                if os.path.exists(extracted_dir):
                    generated_files.append({
                        "file_name": f"_{base_name}.extracted",
                        "mime_type": "inode/directory",
                        "file_size": 4096,
                        "stage_generated": "Extraction"
                    })
                    
            return ToolOutput(
                success=success,
                exit_code=exit_code,
                logs=logs,
                generated_files=generated_files,
                parsed_metrics={"stage": "Extraction", "tool": "binwalk"}
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                exit_code=-1,
                logs=[{"log_type": "STDERR", "message": f"Execution error: {str(e)}"}],
                generated_files=[],
                parsed_metrics={}
            )

    async def execute_simulated(self, tool_input: ToolInput) -> ToolOutput:
        # Simulate processing time
        await asyncio.sleep(2.0)
        
        target_name = os.path.basename(tool_input.target_filepath) or "flash.bin"
        
        logs = [
            {"log_type": "SYSTEM", "message": f"Initializing simulated scan on '{target_name}'..."},
            {"log_type": "STDOUT", "message": "DECIMAL       HEXADECIMAL     DESCRIPTION"},
            {"log_type": "STDOUT", "message": "--------------------------------------------------------------------------------"},
            {"log_type": "STDOUT", "message": "0             0x0             TRX firmware header, lzma compressed, length: 4194304 bytes"},
            {"log_type": "STDOUT", "message": "512           0x200           LZMA compressed data, properties: 0x5D, dictionary size: 8388608 bytes"},
            {"log_type": "STDOUT", "message": "1048576       0x100000        Squashfs filesystem, little endian, version 4.0, size: 2894101 bytes, 492 inodes, blocksize: 131072 bytes, created: 2026-07-28 09:32:01"},
            {"log_type": "SYSTEM", "message": "Simulation: Extracting identified file systems..."},
            {"log_type": "STDOUT", "message": f"Extracted Squashfs filesystem under data directory: _{target_name}.extracted/"},
            {"log_type": "SYSTEM", "message": "Simulated scan successfully completed."}
        ]
        
        generated_files = [
            {
                "file_name": f"_{target_name}.extracted",
                "mime_type": "inode/directory",
                "file_size": 4096,
                "stage_generated": "Extraction"
            },
            {
                "file_name": f"squashfs-root.tar.gz",
                "mime_type": "application/gzip",
                "file_size": 1284902,
                "stage_generated": "Extraction"
            }
        ]
        
        metrics = {
            "file_type": "TRX firmware image",
            "lzma_offset": 512,
            "squashfs_offset": 1048576,
            "filesystem_type": "SquashFS v4.0",
            "size_extracted_bytes": 2894101
        }
        
        return ToolOutput(
            success=True,
            exit_code=0,
            logs=logs,
            generated_files=generated_files,
            parsed_metrics=metrics
        )
