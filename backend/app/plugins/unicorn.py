from typing import Dict, Any, List
import asyncio
import os
import struct
import copy
from app.plugins.base import BaseToolPlugin, ToolInput, ToolOutput

try:
    from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_PROT_READ, UC_PROT_WRITE, UC_PROT_EXEC, \
        UC_HOOK_MEM_READ_UNMAPPED, UC_HOOK_MEM_WRITE_UNMAPPED, UC_HOOK_MEM_FETCH_UNMAPPED, UC_HOOK_CODE, UcError, \
        UC_MEM_WRITE_UNMAPPED, UC_MEM_FETCH_UNMAPPED
    from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP, UC_ARM_REG_PC
    UNICORN_AVAILABLE = True
except ImportError:
    UNICORN_AVAILABLE = False

class UnicornPlugin(BaseToolPlugin):
    @property
    def name(self) -> str:
        return "unicorn"

    @property
    def documentation(self) -> Dict[str, Any]:
        return {
            "purpose": "Dynamic emulation of isolated binary functions (e.g. DLMS parsers).",
            "commands": ["Internal Python Unicorn script execution"],
            "troubleshooting": "Ensure unicorn-engine python bindings are installed."
        }

    def validate_inputs(self, tool_input: ToolInput) -> bool:
        return os.path.exists(tool_input.target_filepath)

    def _align_size(self, size: int, alignment: int = 4096) -> int:
        return (size + alignment - 1) & ~(alignment - 1)

    async def execute_real(self, tool_input: ToolInput) -> ToolOutput:
        if not UNICORN_AVAILABLE:
            return ToolOutput(
                success=False,
                exit_code=1,
                logs=["[Error] unicorn python package is not installed. Emulation could not run."],
                generated_files=[],
                parsed_metrics={}
            )

        target = tool_input.target_filepath
        try:
            with open(target, 'rb') as f:
                fw_data = f.read()
        except Exception as e:
            return ToolOutput(
                success=False,
                exit_code=1,
                logs=[f"[Error] Failed to read firmware file: {e}"],
                generated_files=[],
                parsed_metrics={}
            )

        if len(fw_data) < 8:
            return ToolOutput(
                success=False,
                exit_code=1,
                logs=["[Error] Firmware file too small to contain a valid ARM vector table."],
                generated_files=[],
                parsed_metrics={}
            )

        # Parse ARM Vector Table (assuming standard Cortex-M placement at offset 0)
        # SP is at offset 0x00, Reset Vector is at offset 0x04
        initial_sp = struct.unpack_from('<I', fw_data, 0)[0]
        reset_vector = struct.unpack_from('<I', fw_data, 4)[0]

        # Reset vector in ARM Cortex-M must have the LSB set to 1 (Thumb mode)
        if not (reset_vector & 1):
            return ToolOutput(
                success=False,
                exit_code=1,
                logs=[f"[Error] Emulation could not run: Reset vector (0x{reset_vector:08X}) is not in Thumb mode (LSB != 1)."],
                generated_files=[],
                parsed_metrics={}
            )

        entry_point = reset_vector & ~1

        logs = [
            f"[Unicorn] Initializing ARM Cortex-M CPU emulation...",
            f"[Unicorn] Parsed initial SP: 0x{initial_sp:08X}",
            f"[Unicorn] Parsed Reset Vector (PC): 0x{reset_vector:08X} (Thumb entry: 0x{entry_point:08X})"
        ]

        # Memory layout assumptions for generic Cortex-M
        FLASH_BASE = 0x08000000
        FLASH_SIZE = self._align_size(len(fw_data), 4096)
        # Ensure we map enough flash for at least 1MB if binary is small, or just exactly what's needed
        if FLASH_SIZE < 1024 * 1024:
            FLASH_SIZE = 1024 * 1024

        # Pad firmware with NOPs (0xbf00) if it's very short to avoid instruction fetch overruns
        padded_fw = bytearray(fw_data)
        padded_fw.extend(b'\x00\xbf' * 100) # 100 Thumb NOPs
        
        SRAM_BASE = 0x20000000
        SRAM_SIZE = 256 * 1024  # 256KB RAM

        # Input Mutation Engine properties
        seed_payload = b"\x00\x01\x00\x10\x00\x01\x00\x0f\x01\x02\x03\x04" # Fake DLMS APDU wrapper
        mutations = [
            seed_payload,
            seed_payload + b"A" * 64, # Buffer overflow attempt
            seed_payload + b"\xff" * 128, # Negative/Boundary values
            b"\x00" * 256, # Null payload
            b"\x7f\xff\xff\xff" + seed_payload # Large length header attempt
        ]
        
        MAX_INSTRUCTIONS = 10000
        vulnerabilities = []

        for i, payload in enumerate(mutations):
            logs.append(f"\n[Unicorn] --- Fuzzing Iteration {i+1}/{len(mutations)} ---")
            
            try:
                uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
                
                # Map memory
                uc.mem_map(FLASH_BASE, FLASH_SIZE, UC_PROT_READ | UC_PROT_EXEC)
                uc.mem_map(SRAM_BASE, SRAM_SIZE, UC_PROT_READ | UC_PROT_WRITE)
                
                # Write firmware to flash
                uc.mem_write(FLASH_BASE, bytes(padded_fw))
                
                # Write fuzzed input to SRAM (Input Buffer)
                input_buffer_addr = SRAM_BASE + 0x1000
                uc.mem_write(input_buffer_addr, payload)
                
                # Setup AAPCS arguments and stack
                uc.reg_write(UC_ARM_REG_SP, initial_sp if initial_sp != 0 else (SRAM_BASE + SRAM_SIZE - 0x10))
                uc.reg_write(UC_ARM_REG_R0, input_buffer_addr) # Arg 1: Buffer pointer
                uc.reg_write(UC_ARM_REG_R1, len(payload))      # Arg 2: Buffer length

                # Hook State
                hook_state = {"instruction_count": 0, "crash_detected": False, "crash_reason": None, "fault_address": None}
                
                def hook_code(uc_engine, address, size, user_data):
                    user_data["instruction_count"] += 1
                    if user_data["instruction_count"] > MAX_INSTRUCTIONS:
                        user_data["crash_detected"] = True
                        user_data["crash_reason"] = "Timeout/Infinite Loop"
                        uc_engine.emu_stop()

                def hook_mem_invalid(uc_engine, access, address, size, value, user_data):
                    user_data["crash_detected"] = True
                    is_write = (access == UC_MEM_WRITE_UNMAPPED)
                    is_fetch = (access == UC_MEM_FETCH_UNMAPPED)
                    if is_fetch:
                        user_data["crash_reason"] = "Invalid Memory Fetch"
                    else:
                        user_data["crash_reason"] = f"Invalid Memory {'Write' if is_write else 'Read'}"
                    user_data["fault_address"] = address
                    uc_engine.emu_stop()
                    return False

                uc.hook_add(UC_HOOK_CODE, hook_code, hook_state)
                uc.hook_add(UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED | UC_HOOK_MEM_FETCH_UNMAPPED, hook_mem_invalid, hook_state)

                # Execute
                try:
                    # Emulate starting from entry point (must have LSB=1 for Thumb)
                    uc.emu_start(entry_point | 1, entry_point + 0x1000, timeout=0, count=MAX_INSTRUCTIONS)
                except UcError as e:
                    hook_state["crash_detected"] = True
                    if not hook_state.get("crash_reason"):
                        hook_state["crash_reason"] = f"CPU Exception: {e}"

                if hook_state["crash_detected"]:
                    crash_pc = uc.reg_read(UC_ARM_REG_PC)
                    logs.append(f"[!] CRASH DETECTED at PC 0x{crash_pc:08X}: {hook_state['crash_reason']}")
                    if hook_state['fault_address'] is not None:
                        logs.append(f"    Faulting Memory Address: 0x{hook_state['fault_address']:08X}")
                    logs.append(f"    Mutated Input (hex): {payload.hex()}")
                    
                    # Capture R0-R3 for context
                    r0 = uc.reg_read(UC_ARM_REG_R0)
                    r1 = uc.reg_read(UC_ARM_REG_R1)
                    r2 = uc.reg_read(UC_ARM_REG_R2)
                    r3 = uc.reg_read(UC_ARM_REG_R3)
                    logs.append(f"    Register Dump: R0=0x{r0:08X} R1=0x{r1:08X} R2=0x{r2:08X} R3=0x{r3:08X}")
                    
                    vulnerabilities.append({
                        "type": hook_state["crash_reason"],
                        "address": f"0x{crash_pc:08X}",
                        "severity": "CRITICAL",
                        "mutated_payload": payload.hex()
                    })
                    break # Stop fuzzing on first genuine crash
                else:
                    logs.append(f"    Clean execution. Instructions executed: {hook_state['instruction_count']}")

            except Exception as e:
                logs.append(f"[-] Emulation iteration failed due to internal error: {e}")
                
        return ToolOutput(
            success=True,
            exit_code=0,
            logs=logs,
            generated_files=[],
            parsed_metrics={
                "vulnerabilities": vulnerabilities
            }
        )

    async def execute_simulated(self, tool_input: ToolInput) -> ToolOutput:
        await asyncio.sleep(1)
        
        logs = [
            f"[Unicorn] Initializing ARM CPU emulation environment...",
            f"[Unicorn] Mapping memory and loading segment at 0x08000000",
            f"[Unicorn] Fuzzing input buffer at parser endpoint...",
            f"[!] CRASH DETECTED: Invalid Memory Write",
            f"    Reason: Buffer Overflow when parsing AARQ length field."
        ]
        
        return ToolOutput(
            success=True,
            exit_code=0,
            logs=logs,
            generated_files=[],
            parsed_metrics={
                "vulnerabilities": [
                    {
                        "type": "Buffer Overflow",
                        "address": "0x0800A458",
                        "severity": "CRITICAL",
                        "mutated_payload": "000100100001000f01020304"
                    }
                ]
            }
        )
