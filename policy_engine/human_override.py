"""
Policy Engine - Human Override Matrix
Clasifica y bloquea acciones según los niveles L0 a L4.
"""
from enum import Enum

class ActionLevel(Enum):
    L0_INFORMATIONAL = 0   # Sofia can do it
    L1_LOW_RISK = 1        # Sofia can do it automatically
    L2_BUSINESS_IMPACT = 2 # Requires validation
    L3_HIGH_IMPACT = 3     # Requires human confirmation
    L4_SAFETY_CRITICAL = 4 # HUMAN ONLY

class PolicyEngine:
    def __init__(self):
        self.rules = {
            "get_weather": ActionLevel.L0_INFORMATIONAL,
            "lookup_appointment": ActionLevel.L1_LOW_RISK,
            "create_appointment": ActionLevel.L2_BUSINESS_IMPACT,
            "refund_payment": ActionLevel.L3_HIGH_IMPACT,
            "gas_leak_emergency": ActionLevel.L4_SAFETY_CRITICAL
        }

    def evaluate_action(self, action_name: str, context: dict) -> bool:
        level = self.rules.get(action_name, ActionLevel.L4_SAFETY_CRITICAL)
        
        if level == ActionLevel.L4_SAFETY_CRITICAL:
            self.trigger_human_transfer(reason=f"Policy Block: {action_name} is L4")
            return False
            
        if level == ActionLevel.L3_HIGH_IMPACT and not context.get("human_confirmed"):
            return False
            
        return True

    def trigger_human_transfer(self, reason: str):
        # Envía el payload a Chatwoot y desvía la llamada
        print(f"[KILL SWITCH / TRANSFER] Triggered. Reason: {reason}")
