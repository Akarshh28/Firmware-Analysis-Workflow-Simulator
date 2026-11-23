from typing import Dict, Any, List
import asyncio
import os
from app.plugins.base import BaseToolPlugin, ToolInput, ToolOutput

class QemuPlugin(BaseToolPlugin):
    @property
    def name(self) -> str:
        return "qemu"

    @property
    def documentation(self) -> Dict[str, Any]:
        return {
            "purpose": "Emulates extracted firmware kernels to test execution flow, boot sequences, and dynamically scan for runtime vulnerabilities like unauthorized port openings or crash behaviors.",
            "commands": ["qemu-system-arm -M versatilepb -kernel <target_file> -nographic -m 256M"],
            "troubleshooting": "Ensure qemu-system-arm is installed on the host system. For real runs, verify the firmware architecture matches the QEMU machine type (versatilepb by default)."
        }

    def validate_inputs(self, tool_input: ToolInput) -> bool:
        target = tool_input.target_filepath
        
        # 1. Path traversal check (sandboxing)
        if ".." in target:
            print(f"[QEMU] Path traversal detected: {target}")
            return False
            
        return True

    async def execute_real(self, tool_input: ToolInput) -> ToolOutput:
        target = tool_input.target_filepath
        
        # Security sandbox check repeated just in case
        if ".." in target:
             return ToolOutput(
                success=False,
                exit_code=-1,
                logs=["[Error] Path traversal attempt blocked."],
                generated_files=[],
                parsed_metrics={}
            )

        if not os.path.exists(target):
             return ToolOutput(
                success=False,
                exit_code=-1,
                logs=[f"[Error] Firmware file not found: {target}"],
                generated_files=[],
                parsed_metrics={}
            )

        # Build QEMU command for headless execution
        cmd = [
            "qemu-system-arm",
            "-M", "versatilepb",
            "-kernel", target,
            "-nographic",
            "-m", "256"
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Hard runtime boundary of 300 seconds (5 minutes)
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            except asyncio.TimeoutError:
                # Process is hanging, kill it
                process.kill()
                # Ensure it completes (Wait for cleanup)
                stdout, stderr = await process.communicate()
                
                return ToolOutput(
                    success=False,
                    exit_code=-1,
                    logs=["[Timeout] Execution exceeded 300 seconds boundary and was terminated."] + 
                         (stdout.decode().splitlines() if stdout else []) + 
                         (stderr.decode().splitlines() if stderr else []),
                    generated_files=[],
                    parsed_metrics={"timeout_reached": True}
                )

            logs = stdout.decode().splitlines() + stderr.decode().splitlines()
            return ToolOutput(
                success=(process.returncode == 0),
                exit_code=process.returncode or 0,
                logs=logs,
                generated_files=[],
                parsed_metrics={"execution_time": "Finished under timeout"}
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                exit_code=-1,
                logs=[str(e)],
                generated_files=[],
                parsed_metrics={}
            )

    async def execute_simulated(self, tool_input: ToolInput) -> ToolOutput:
        # Simulate QEMU Boot Time
        await asyncio.sleep(2) 
        
        logs = [
            "[QEMU] Starting qemu-system-arm emulation...",
            "[QEMU] Machine type: versatilepb, Memory: 256M",
            "[QEMU] Loading kernel image...",
            "Booting Linux on physical CPU 0x0",
            "Linux version 4.19.100-yocto-standard (oe-user@oe-host) (gcc version 8.3.0)",
            "Machine model: DLMS Smart Meter Platform v2.1",
            "Memory policy: Data cache writeback",
            "random: get_random_bytes called from start_kernel+0x310/0x450 with crng_init=0",
            "Mounting root file system...",
            "Starting DLMS COSEM Server daemon...",
            "[gurux_dlms_server] Listening on port 4059...",
            "[QEMU-Agent] Firmware boot sequence complete. System is stable."
        ]
        
        return ToolOutput(
            success=True,
            exit_code=0,
            logs=logs,
            generated_files=[],
            parsed_metrics={
                "cpu_architecture": "armv7l",
                "boot_time_ms": 1450,
                "detected_services": ["gurux_dlms_server_tcp:4059"]
            }
        )
