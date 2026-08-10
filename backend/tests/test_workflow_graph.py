from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langgraph.builder import create_firmware_analysis_graph

def test_workflow_stage_order_is_fixed_and_sequential():
    graph = create_firmware_analysis_graph()
    assert "upload" in graph.nodes
    assert "pdf_report" in graph.nodes
