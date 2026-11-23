import pytest
import os
import struct
import tempfile
import asyncio
from app.plugins.unicorn import UnicornPlugin
from app.plugins.base import ToolInput

def test_unicorn_real_crash_detection():
    plugin = UnicornPlugin()

    # Create a minimal ARM Thumb vulnerable binary
    # SP = 0x20010000, PC = 0x08000009 (Thumb mode entry at 0x08000008)
    # At 0x08000008: LDR R1, =0x30000000 (invalid address, simplified to just load a high address)
    # Then STR R0, [R1] -> triggers memory write violation

    vector_table = struct.pack('<II', 0x20010000, 0x08000009)
    
    # Assembly (Thumb): 
    # movs r1, #0x40    => 40 21
    # lsls r1, r1, #24  => 09 06  (r1 is now 0x40000000)
    # str r0, [r1, #0]  => 08 60
    # b .               => fe e7
    
    code = b"\x40\x21\x09\x06\x08\x60\xfe\xe7"
    
    fw_data = vector_table + code

    with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as tmp:
        tmp.write(fw_data)
        tmp_path = tmp.name

    try:
        tool_input = ToolInput(target_filepath=tmp_path)
        result = asyncio.run(plugin.execute_real(tool_input))

        assert result.success is True
        
        # Check that it caught the vulnerability
        if len(result.parsed_metrics["vulnerabilities"]) == 0:
            print("Logs from execution:", "\n".join(result.logs))
        assert len(result.parsed_metrics["vulnerabilities"]) > 0
        vuln = result.parsed_metrics["vulnerabilities"][0]
        
        assert "Invalid Memory Write" in vuln["type"]
        assert vuln["severity"] == "CRITICAL"
        
        # Check logs
        log_str = "\n".join(result.logs)
        assert "CRASH DETECTED" in log_str
        assert "Register Dump" in log_str
    finally:
        os.remove(tmp_path)
