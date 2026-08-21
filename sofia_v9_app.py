"""
Sofia Lin V9.1 - Core Brain Implementation
Integrates Policy Engine, Data Layer, and LangGraph FSM.
"""
import os
import json
import logging
from typing import Dict, Any

from policy_engine.human_override import PolicyEngine, ActionLevel
from orchestrator.langgraph_fsm import triage_node, routing_decision
from core.config import SystemConfig, DegradedMode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SofiaLinV9Engine:
    def __init__(self):
        self.config = SystemConfig()
        self.policy_engine = PolicyEngine()
        logger.info(f"Sofia Lin V9.1 Engine Initialized. Mode: {self.config.CURRENT_MODE}")

    def process_incoming_call(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for incoming voice streams (Twilio/Pipecat).
        """
        caller_id = call_data.get("caller_id", "Unknown")
        transcript = call_data.get("transcript", "")
        
        logger.info(f"Incoming audio stream from {caller_id}")

        # 1. DEGRADED MODE CHECK
        if self.config.CURRENT_MODE == DegradedMode.LEVEL_4_EMERGENCY:
            return self._trigger_human_transfer("System in L4 Emergency Mode")
            
        if self.config.CURRENT_MODE == DegradedMode.LEVEL_3_AI_DISABLED:
            return self._trigger_human_transfer("AI Disabled - Routing to Dispatch")

        # 2. POLICY ENGINE - PRE-PROCESSING SAFETY CHECK
        if "gas" in transcript.lower() and "smell" in transcript.lower():
            if not self.policy_engine.evaluate_action("gas_leak_emergency", {}):
                return self._trigger_human_transfer("L4 Safety Critical - Gas Leak Detected")

        # 3. STATE MACHINE / ORCHESTRATION (LangGraph)
        state = {
            "call_id": call_data.get("call_id", "000"),
            "customer_phone": caller_id,
            "current_fsm_state": "triage",
            "collected_fields": {},
            "confidence_score": 0.95,
            "requires_human": False
        }
        
        state = triage_node(state)
        next_action = routing_decision(state)
        
        if next_action == "transfer_to_human":
            return self._trigger_human_transfer("LangGraph required human transfer")

        # 4. LLM GENERATION
        response_text = self._generate_llm_response(transcript)
        
        return {
            "status": "success",
            "audio_response_text": response_text,
            "action": "continue_call"
        }

    def _generate_llm_response(self, text: str) -> str:
        return "Thank you for calling Morales Plumbing. How can I help you today?"

    def _trigger_human_transfer(self, reason: str) -> Dict[str, Any]:
        logger.warning(f"Initiating Human Transfer: {reason}")
        return {
            "status": "transferred",
            "transfer_number": self.config.HUMAN_DISPATCH_NUMBER,
            "reason": reason,
            "audio_response_text": "Please hold while I transfer you to our live dispatch team."
        }

if __name__ == "__main__":
    engine = SofiaLinV9Engine()
    test_call = {"caller_id": "+1234567890", "transcript": "I smell gas in my basement"}
    result = engine.process_incoming_call(test_call)
    print(json.dumps(result, indent=2))
