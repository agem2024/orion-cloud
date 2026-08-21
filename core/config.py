"""
Configuración Core - Sofia Lin V9.1
Definición de Modos Degradados, Roles y Constantes del Sistema.
"""
from enum import Enum

class DegradedMode(Enum):
    LEVEL_0_NORMAL = "Normal AI Operation"
    LEVEL_1_LLM_DEGRADED = "LLM Degraded (Pre-defined Responses)"
    LEVEL_2_API_DEGRADED = "APIs Degraded (No validation)"
    LEVEL_3_AI_DISABLED = "AI Disabled (Human Transfer Only)"
    LEVEL_4_EMERGENCY = "Emergency (Direct Telephony to Human)"

class SystemConfig:
    CURRENT_MODE = DegradedMode.LEVEL_0_NORMAL
    MANUAL_VERSION = "9.1"
    MAX_LATENCY_P95_MS = 1500
    HUMAN_DISPATCH_NUMBER = "+16692342444"
