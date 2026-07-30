from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langgraph.graph import WorkflowGraph


def test_workflow_stage_order_is_fixed_and_sequential():
    graph = WorkflowGraph()
    assert graph.stage_names == [
        "upload",
        "strings",
        "binwalk",
        "cutter",
        "ghidra",
        "trufflehog",
        "entropy",
        "wireshark",
        "afl",
        "angr",
        "scorecard",
        "pdf_report",
    ]
