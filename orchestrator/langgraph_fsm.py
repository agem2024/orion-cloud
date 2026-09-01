"""
LangGraph Orchestrator - State Machine determinista
"""
from typing import TypedDict, Optional

class SofiaState(TypedDict):
    call_id: str
    customer_phone: str
    current_fsm_state: str
    collected_fields: dict
    confidence_score: float
    requires_human: bool

def triage_node(state: SofiaState) -> SofiaState:
    # 1. Verificar Policy Engine para identificar emergencias (Gas P0)
    # 2. Si hay emergencia, state["requires_human"] = True
    return state

def routing_decision(state: SofiaState) -> str:
    if state["requires_human"]:
        return "transfer_to_human"
    if not state["collected_fields"].get("address"):
        return "collect_address"
    return "process_appointment"
