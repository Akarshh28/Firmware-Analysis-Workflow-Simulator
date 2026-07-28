import os
import asyncio
from typing import Dict, Any
from app.plugins.base import BaseToolPlugin, ToolInput, ToolOutput

class AngrPlugin(BaseToolPlugin):
    @property
    def name(self) -> str:
        return "angr"

    @property
    def documentation(self) -> Dict[str, Any]:
        return {
            "purpose": "Perform symbolic execution to analyze binary control flows and solve logic constraints.",
            "input": "Executable binary file (ELF, PE, Mach-O) extracted from firmware.",
            "output": "Discovered execution paths, register/memory state constraints, and input payloads that trigger specific control flow paths.",
            "workflow": "Load binary -> define starting state -> set target/avoid addresses -> solve logic constraints -> generate exploit payload.",
            "internal_working": "Uses a symbolic solver (Z3) to represent input values as algebraic symbols rather than concrete values. It executes instructions symbolically, generating mathematical constraints for each branch.",
            "commands": [
                {
                    "command": "python -c \"import angr; proj = angr.Project('dlms_binary'); state = proj.factory.entry_state(); simgr = proj.factory.simulation_manager(state); simgr.explore(find=0x401234)\"",
                    "explanation": "Load 'dlms_binary' and explore paths leading to address 0x401234."
                }
            ],
            "common_errors": [
                "ImportError: No module named 'angr' (dependency missing).",
                "State explosion (too many execution paths to solve due to loops or complicated crypt algorithms)."
            ],
            "troubleshooting": "Ensure angr is installed in your python environment: 'pip install angr'. For state explosion, restrict the search path or use hook functions to bypass heavy crypt routines.",
            "best_practices": "Avoid symbolic execution on standard hashing functions (like SHA256/MD5). Hook these functions to return concrete values to prevent state explosion.",
            "references": [
                "angr documentation: https://docs.angr.io/",
                "Symbolic Execution Guide: https://github.com/angr/angr-doc"
            ]
        }

    def validate_inputs(self, tool_input: ToolInput) -> bool:
        return bool(tool_input.target_filepath)

    async def execute_real(self, tool_input: ToolInput) -> ToolOutput:
        # Check if angr is installed locally in the backend's environment.
        # Running angr dynamically requires python script orchestration.
        # We will try to run a python command that runs angr on the binary.
        target = tool_input.target_filepath
        try:
            # Running angr requires an actual script or inline script.
            # For real mode, we run a short inline script using python.
            script = f"""
import angr
import sys
try:
    proj = angr.Project('{target}', auto_load_libs=False)
    state = proj.factory.entry_state()
    simgr = proj.factory.simulation_manager(state)
    simgr.explore(find=lambda s: b"access_granted" in s.posix.dumps(1))
    if simgr.found:
        found_state = simgr.found[0]
        input_data = found_state.posix.dumps(0)
        print("SUCCESS")
        print("Input:", input_data.hex())
        sys.exit(0)
    else:
        print("FAILED: Target state not found")
        sys.exit(1)
except Exception as e:
    print("ERROR:", str(e))
    sys.exit(2)
"""
            # Write script to temporary folder in workspace
            script_path = os.path.join(os.path.dirname(target), "angr_run.py")
            with open(script_path, "w") as f:
                f.write(script)
                
            process = await asyncio.create_subprocess_exec(
                "python", script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            # Delete script
            if os.path.exists(script_path):
                os.remove(script_path)
                
            exit_code = process.returncode
            success = exit_code == 0
            
            logs = []
            if stdout:
                logs.append({"log_type": "STDOUT", "message": stdout.decode("utf-8", errors="replace")})
            if stderr:
                logs.append({"log_type": "STDERR", "message": stderr.decode("utf-8", errors="replace")})
                
            return ToolOutput(
                success=success,
                exit_code=exit_code,
                logs=logs,
                generated_files=[],
                parsed_metrics={"angr_status": "completed"}
            )
        except Exception as e:
            return ToolOutput(
                success=False,
                exit_code=-1,
                logs=[{"log_type": "STDERR", "message": f"angr execution failed: {str(e)}"}],
                generated_files=[],
                parsed_metrics={}
            )

    async def execute_simulated(self, tool_input: ToolInput) -> ToolOutput:
        await asyncio.sleep(3.0)
        
        target_name = os.path.basename(tool_input.target_filepath) or "dlms_parser"
        
        logs = [
            {"log_type": "SYSTEM", "message": f"Loading binary '{target_name}' into angr Project..."},
            {"log_type": "SYSTEM", "message": f"Analyzing control flow graph (CFG) for entry point..."},
            {"log_type": "STDOUT", "message": "WARNING | 2026-07-28 10:43:01 | Cle | angr project initialized with auto_load_libs=False"},
            {"log_type": "SYSTEM", "message": "Defining Symbolic State: EntryState with symbolic buffer size 64 bytes..."},
            {"log_type": "SYSTEM", "message": "Initializing Simulation Manager with symbolic state..."},
            {"log_type": "STDOUT", "message": "Active states: <State 0x401080>"},
            {"log_type": "STDOUT", "message": "Exploring paths... finding target address 0x4012bc (auth check bypass)..."},
            {"log_type": "STDOUT", "message": "State 0x401080 -> Split into 2 branches: <State 0x4010b4>, <State 0x4010c2>"},
            {"log_type": "STDOUT", "message": "Path exploration status: 12 active, 4 deadended, 0 found..."},
            {"log_type": "STDOUT", "message": "Path exploration status: 28 active, 16 deadended, 1 found!"},
            {"log_type": "SYSTEM", "message": "Solving constraints for the matching execution path..."},
            {"log_type": "STDOUT", "message": "SUCCESS: Solved input payload constraints."},
            {"log_type": "STDOUT", "message": "Solved Input (Hex): 444c4d535f434f53454d5f4259504153535f4b4559000000"},
            {"log_type": "STDOUT", "message": "Solved Input (ASCII): DLMS_COSEM_BYPASS_KEY"},
            {"log_type": "SYSTEM", "message": "Simulation execution completed."}
        ]
        
        metrics = {
            "execution_paths_explored": 45,
            "deadended_paths": 20,
            "solving_time_seconds": 2.41,
            "target_state_found": True,
            "discovered_secret_keys": ["DLMS_COSEM_BYPASS_KEY"]
        }
        
        return ToolOutput(
            success=True,
            exit_code=0,
            logs=logs,
            generated_files=[],
            parsed_metrics=metrics
        )
