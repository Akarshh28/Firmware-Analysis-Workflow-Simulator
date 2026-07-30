from langgraph.graph import StateGraph, END
# pyrefly: ignore [missing-import]
from langgraph.state import GraphState
# pyrefly: ignore [missing-import]
from langgraph.nodes import (
    upload_node, strings_node, binwalk_node, cutter_node, ghidra_node,
    trufflehog_node, entropy_node, wireshark_node, afl_node, angr_node,
    scorecard_node, report_node
)

def create_firmware_analysis_graph():
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("upload", upload_node)
    workflow.add_node("strings", strings_node)
    workflow.add_node("binwalk", binwalk_node)
    workflow.add_node("cutter", cutter_node)
    workflow.add_node("ghidra", ghidra_node)
    workflow.add_node("trufflehog", trufflehog_node)
    workflow.add_node("entropy", entropy_node)
    workflow.add_node("wireshark", wireshark_node)
    workflow.add_node("afl++", afl_node)
    workflow.add_node("angr", angr_node)
    workflow.add_node("scorecard", scorecard_node)
    workflow.add_node("pdf_report", report_node)

    def check_status(state: GraphState):
        if state.get("status") == "FAILED":
            return "end"
        return "continue"

    workflow.set_entry_point("upload")
    
    stages = ["upload", "strings", "binwalk", "cutter", "ghidra", "trufflehog", 
              "entropy", "wireshark", "afl++", "angr", "scorecard", "pdf_report"]
              
    for i in range(len(stages) - 1):
        workflow.add_conditional_edges(
            stages[i],
            check_status,
            {"continue": stages[i+1], "end": END}
        )
        
    workflow.add_conditional_edges(
        stages[-1],
        check_status,
        {"continue": END, "end": END}
    )

    return workflow.compile()

graph = create_firmware_analysis_graph()
