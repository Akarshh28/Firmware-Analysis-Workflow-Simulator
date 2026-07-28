from abc import ABC, abstractmethod
from typing import Dict, Any, List

class ToolInput:
    def __init__(self, target_filepath: str, extra_args: Dict[str, Any]):
        self.target_filepath = target_filepath  # File to process (e.g. flash.bin)
        self.extra_args = extra_args            # Parameters (e.g., --entropy, -v)

class ToolOutput:
    def __init__(self, success: bool, exit_code: int, logs: List[Dict[str, Any]], generated_files: List[Dict[str, Any]], parsed_metrics: Dict[str, Any]):
        self.success = success                  # Status outcome
        self.exit_code = exit_code              # Execution exit code
        # logs is a list of dicts with keys: 'log_type' (STDOUT/STDERR/SYSTEM) and 'message'
        self.logs = logs                        
        # generated_files is a list of dicts with keys: 'file_name', 'mime_type', 'file_size', 'stage_generated'
        self.generated_files = generated_files  
        self.parsed_metrics = parsed_metrics    # Extracted data (e.g., keys found, sections identified)

class BaseToolPlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier of the tool (e.g., 'binwalk', 'ghidra')"""
        pass

    @property
    @abstractmethod
    def documentation(self) -> Dict[str, Any]:
        """Returns structured helper info: purpose, commands, common errors, troubleshooting, best practices, references."""
        pass

    @abstractmethod
    def validate_inputs(self, tool_input: ToolInput) -> bool:
        """Verifies if the target file exists and is of correct type."""
        pass

    @abstractmethod
    async def execute_real(self, tool_input: ToolInput) -> ToolOutput:
        """Performs actual command-line subprocess execution on the local host."""
        pass

    @abstractmethod
    async def execute_simulated(self, tool_input: ToolInput) -> ToolOutput:
        """Returns pre-recorded execution traces, emulated output logs, and realistic metrics."""
        pass
