import re

with open('brain.py', 'r', encoding='utf-8') as f:
    content = f.read()

appendix_es = """
  REGLA ESTRICTA: ESTA TOTALMENTE PROHIBIDO DAR PRECIOS O ESTIMADOS BAJO CUALQUIER CIRCUNSTANCIA. Si te preguntan por precios, debes decir que un técnico especializado debe evaluar el problema en persona para dar un precio exacto.
  Sí conoces nuestras actividades y servicios (pero NUNCA sus precios):
  - Deteccion de fugas (Precision Leak Detection)
  - Reemplazo de tuberia casa completa (Full House Repipe)
  - Filtracion y suavizado de agua (Water Filtration & Softening)
  - Instalacion de valvula inteligente (Smart Valve Installation)
  - Inspeccion con camara (SeeSnake Camera Inspection)
  - Reemplazo alcantarillado (Main Sewer Replacement)
  - Calentador de agua hibrido (Hybrid Heat Pump Water Heater)
  - Valvula reductora de presion (PRV)
  - Triage de Emergencia (Emergency Triage)
  - Trazado Digital y CAD (CAD & Digital Tracing)
  - Calentador de agua sin tanque (Tankless Water Heater)
  - Ensamble de prevencion de reflujo (Backflow Preventer Assembly)
  - Cambio de accesorios de lujo (Luxury Fixture Swap)
  - Panel quimico de agua (Water Chemistry Panel)
  - Hidro-lavado comercial (Commercial Hydro-Jetting)"""

appendix_en = """
  STRICT RULE: YOU ARE STRICTLY FORBIDDEN FROM GIVING PRICES OR ESTIMATES UNDER ANY CIRCUMSTANCES. If asked for prices, state that a specialized technician must evaluate the issue in person to provide an accurate quote.
  You DO know our activities and services (but NEVER their prices):
  - Precision Leak Detection
  - Full House Repipe
  - Water Filtration & Softening
  - Smart Valve Installation
  - SeeSnake Camera Inspection
  - Main Sewer Replacement
  - Hybrid Heat Pump Water Heater
  - Pressure Reducing Valve (PRV)
  - Emergency Triage
  - CAD & Digital Tracing
  - Tankless Water Heater
  - Backflow Preventer Assembly
  - Luxury Fixture Swap
  - Water Chemistry Panel
  - Commercial Hydro-Jetting"""

# Modificando el prompt en español
content = re.sub(
    r'(No hables de ORION Tech ni ofrezcas servicios de IA\.)\"\"\"',
    r'\1' + appendix_es + '"""',
    content
)

# Modificando el prompt en inglés
content = re.sub(
    r'(Do not mention ORION Tech or offer AI services\.)\"\"\"',
    r'\1' + appendix_en + '"""',
    content
)

with open('brain.py', 'w', encoding='utf-8') as f:
    f.write(content)
