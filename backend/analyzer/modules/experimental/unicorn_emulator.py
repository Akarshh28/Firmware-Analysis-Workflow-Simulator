"""
unicorn_emulator.py - Function-Level Emulation for DLMS Parsing
Uses Unicorn engine to isolate and emulate specific functions identified by Ghidra.
"""
import os
import struct

unicorn_installed = True
try:
    # pyright: ignore[reportMissingImports, reportUndefinedVariable, reportWildcardImportFromLibrary]
    from unicorn import *
    # pyright: ignore[reportMissingImports, reportUndefinedVariable, reportWildcardImportFromLibrary]
    from unicorn.arm_const import *
except ImportError:
    unicorn_installed = False
    from unittest.mock import MagicMock
    # Mock all Unicorn constants and classes to silence IDE linters
    UC_ARCH_ARM = UC_MODE_THUMB = UC_MODE_ARM = MagicMock()
    UC_ARM_REG_SP = UC_ARM_REG_R0 = UC_ARM_REG_R1 = UC_ARM_REG_R2 = UC_ARM_REG_R3 = MagicMock()
    UC_HOOK_MEM_INVALID = UC_MEM_READ = UC_MEM_WRITE = MagicMock()
    Uc = MagicMock
    class UcError(Exception): pass

class EmulatorContext:
    def __init__(self, architecture="ARM", mode="THUMB"):
        self.architecture = architecture
        self.mode = mode
        self.uc = None
        self.memory_base = 0x10000
        self.memory_size = 2 * 1024 * 1024 # default 2MB
        self.stack_base = 0x30000000
        self.stack_size = 1024 * 1024 # 1MB
        
        self.crashes = []
        
    def setup(self, code_size=None):
        if self.architecture == "ARM":
            arch = UC_ARCH_ARM
            mode = UC_MODE_THUMB if self.mode == "THUMB" else UC_MODE_ARM
        else:
            raise ValueError(f"Unsupported architecture: {self.architecture}")
            
        try:
            if unicorn_installed:
                self.uc = Uc(arch, mode)
            else:
                raise RuntimeError("Unicorn engine not installed. Run: pip install unicorn")
        except NameError:
            raise RuntimeError("Unicorn engine not installed. Run: pip install unicorn")
            
        # Dynamically size memory to fit the binary (aligned to 4KB)
        if code_size and code_size > self.memory_size:
            self.memory_size = (code_size + 0xFFF) & ~0xFFF
            # Push stack base higher if memory size grew significantly
            self.stack_base = self.memory_base + self.memory_size + 0x1000000
            
        # Map code and stack memory
        self.uc.mem_map(self.memory_base, self.memory_size)
        self.uc.mem_map(self.stack_base, self.stack_size)
        
        # Set up a basic stack pointer
        sp = self.stack_base + self.stack_size - 1024
        if self.architecture == "ARM":
            self.uc.reg_write(UC_ARM_REG_SP, sp)
            
        # Hook invalid memory accesses to catch crashes
        self.uc.hook_add(UC_HOOK_MEM_INVALID, self._hook_mem_invalid)
        
    def _hook_mem_invalid(self, uc, access, address, size, value, user_data):
        crash_type = "Memory Read Violation" if access == UC_MEM_READ else "Memory Write Violation"
        self.crashes.append({
            "type": crash_type,
            "address": hex(address),
            "size": size,
            "value": hex(value) if access == UC_MEM_WRITE else None
        })
        return False # Stop emulation
        
    def load_code(self, code_bytes, start_address=None):
        addr = start_address if start_address else self.memory_base
        self.uc.mem_write(addr, code_bytes)
        return addr
        
    def emulate_function(self, start_addr, end_addr, args=None):
        self.crashes = []
        
        # Setup arguments (assuming ARM AAPCS: R0-R3)
        if args and self.architecture == "ARM":
            regs = [UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3]
            for i, arg in enumerate(args[:4]):
                if isinstance(arg, bytes):
                    # Write buffer to memory and pass pointer
                    buf_addr = self.stack_base + 1024 + (i * 256)
                    self.uc.mem_write(buf_addr, arg)
                    self.uc.reg_write(regs[i], buf_addr)
                elif isinstance(arg, int):
                    self.uc.reg_write(regs[i], arg)
        
        try:
            # Run emulation
            self.uc.emu_start(start_addr, end_addr, timeout=5000) # 5 second timeout
        except UcError as e:
            self.crashes.append({
                "type": "Unicorn Error",
                "message": str(e)
            })
            
        return {
            "success": len(self.crashes) == 0,
            "crashes": self.crashes
        }

def find_function_prologues(code: bytes) -> list:
    """
    Heuristically scans for common ARM/Thumb function prologues.
    Returns a list of potential function addresses.
    """
    addresses = []
    # Thumb prologue: PUSH {R4-R7, LR} -> \xf0\xb5
    # Thumb prologue: PUSH {R4, LR} -> \x10\xb5
    
    for i in range(0, len(code) - 1, 2):
        if code[i:i+2] in [b"\xf0\xb5", b"\x10\xb5"]:
            addresses.append(i)
            
    # Limit to a reasonable number to avoid excessive emulation time
    return addresses[:10]

def run_emulation(target_bin: str, function_starts: list):
    """
    Given a binary and a list of identified parser function addresses,
    this attempts to emulate them with basic fuzzed inputs to detect crashes.
    """
    if not unicorn_installed:
        return {"success": False, "error": "Unicorn engine is not installed. Run: pip install unicorn"}
        
    if not os.path.exists(target_bin):
        return {"success": False, "error": "Binary not found"}
        
    results = []
    
    with open(target_bin, "rb") as f:
        code = f.read()
        
    # We only emulate up to the size of the binary (naive loading for now)
    try:
        emu = EmulatorContext(architecture="ARM", mode="THUMB")
        emu.setup(code_size=len(code))
        base_addr = emu.load_code(code)
    except Exception as e:
        return {"success": False, "error": f"Emulation setup failed: {e}"}
        
    for func_addr in function_starts:
        try:
            addr = int(func_addr, 16)
            # Adjust thumb bit
            if addr % 2 != 0:
                addr -= 1 
            
            # Simple test inputs (simulating APDUs)
            test_inputs = [
                b"A" * 128,          # Buffer overflow test
                b"\x00\x01\x02\x03", # Minimal DLMS header test
                b"%s%s%s%s%s"        # Format string test
            ]
            
            for i, payload in enumerate(test_inputs):
                res = emu.emulate_function(base_addr + addr, base_addr + addr + 0x100, args=[payload])
                if not res["success"]:
                    results.append({
                        "function": hex(addr),
                        "payload_index": i,
                        "crashes": res["crashes"]
                    })
                    break # Stop testing this function on first crash
                    
        except ValueError:
            continue
            
    return {
        "success": True,
        "emulated_functions": len(function_starts),
        "vulnerabilities_found": results
    }
