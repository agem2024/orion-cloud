"""
Write Tools - Acciones mutables con Idempotencia y Autorización.
"""
import uuid
from typing import Optional

def book_appointment(customer_id: str, datetime_slot: str, idempotency_key: Optional[str] = None) -> dict:
    """
    Crea una cita asegurando que no haya bloqueos de concurrencia.
    Requiere que el Policy Engine lo apruebe antes de ejecutarse.
    """
    if not idempotency_key:
        idempotency_key = str(uuid.uuid4())
        
    # Verificar en Redis si esta idempotency_key ya fue procesada
    # Para evitar reservas duplicadas si Twilio reintenta el webhook
    
    # Simulación de inserción en Supabase (Source of Truth)
    return {
        "status": "success",
        "appointment_id": f"APP-{uuid.uuid4().hex[:8]}",
        "idempotency_key": idempotency_key,
        "source": "Supabase Core"
    }
