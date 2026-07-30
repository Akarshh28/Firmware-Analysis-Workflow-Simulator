from typing import TypedDict, List, Dict, Any, Optional

class GraphState(TypedDict):
    project_id: int
    session_id: int
    db_url: str
    current_stage: str
    logs: List[Dict[str, Any]]
    artifacts: List[Dict[str, Any]]
    errors: List[str]
    status: str
