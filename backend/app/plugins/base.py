from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class ToolInput(BaseModel):
    target_filepath: str
    extra_args: Dict[str, Any] = {}
    project_id: Optional[int] = None

class ToolOutput(BaseModel):
    success: bool
    exit_code: int
    logs: List[str]
    generated_files: List[str]
    parsed_metrics: Dict[str, Any]

class BaseToolPlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier of the tool (e.g., 'binwalk', 'ghidra')"""
        pass

    @property
    @abstractmethod
    def documentation(self) -> Dict[str, Any]:
        """Returns structured helper info: purpose, commands, common errors, troubleshooting."""
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
