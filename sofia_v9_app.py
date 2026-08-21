"""
Sofia Lin V9.1 - Core Brain Implementation
Integrates Policy Engine, Data Layer, LangGraph FSM, and real LLM (OpenAI/Gemini).
"""
import os
import json
import logging
import requests
from typing import Dict, Any

from policy_engine.human_override import PolicyEngine, ActionLevel
from orchestrator.langgraph_fsm import triage_node, routing_decision
from core.config import SystemConfig, DegradedMode
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SofiaLinV9Engine:
    def __init__(self):
        self.config = SystemConfig()
        self.policy_engine = PolicyEngine()
        self.openai_key = os.getenv("OPENAI_API_KEY")
        logger.info(f"Sofia Lin V9.1 Engine Initialized. Mode: {self.config.CURRENT_MODE}")

    def process_incoming_call(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for incoming voice/text streams.
        """
        caller_id = call_data.get("caller_id", "Unknown")
        transcript = call_data.get("transcript", "")
        
        logger.info(f"Incoming stream from {caller_id}: {transcript}")

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

        # 4. LLM GENERATION (Real Intelligence)
        response_text = self._generate_llm_response(transcript)
        
        return {
            "status": "success",
            "audio_response_text": response_text,
            "action": "continue_call"
        }

    def _generate_llm_response(self, text: str) -> str:
        if not self.openai_key:
            return "Error interno: API Key de Inteligencia Artificial no encontrada."
            
        system_prompt = """You are Sofia Lin, the official AI Dispatcher for MORALES PLUMBING (AI-INTEGRATED SERVICES).
CRITICAL RULES:
1. License: CSLB Lic. C-36 #1156542 | San Jose, CA.
2. Official Phone: (669) 213-4422.
3. NEVER invent data, phone numbers, or emails.
4. There is NO $85 fee. Never quote repairs by phone without an in-person technical inspection.
5. Be concise, highly professional, and helpful. Always respond in the language the user speaks.
"""
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "max_tokens": 150,
            "temperature": 0.3
        }
        
        try:
            resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=10)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            return "Disculpe, nuestro sistema de inteligencia artificial está experimentando un ligero retraso. Un despachador se comunicará con usted."

    def _trigger_human_transfer(self, reason: str) -> Dict[str, Any]:
        logger.warning(f"Initiating Human Transfer: {reason}")
        return {
            "status": "transferred",
            "transfer_number": self.config.HUMAN_DISPATCH_NUMBER,
            "reason": reason,
            "audio_response_text": "Por favor, manténgase en la línea. Transfiriendo a nuestro equipo de despacho de Morales Plumbing."
        }

if __name__ == "__main__":
    engine = SofiaLinV9Engine()
    test_call = {"caller_id": "+1234567890", "transcript": "Hola, ocupo un plomero para mi baño. ¿Cobran 85 dólares por ir a ver?"}
    result = engine.process_incoming_call(test_call)
    print(json.dumps(result, indent=2))
