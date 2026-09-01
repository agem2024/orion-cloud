import re

with open('brain.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscamos el bloque que agregamos antes y lo reemplazamos
appendix_es_new = """
  REGLA ESTRICTA: ESTA TOTALMENTE PROHIBIDO DAR PRECIOS O ESTIMADOS AL PUBLICO BAJO CUALQUIER CIRCUNSTANCIA. Si te preguntan por precios, debes decir que un tecnico especializado debe evaluar el problema en persona para dar un precio exacto.
  Sí conoces las 495 actividades y servicios de nuestro Price Book y puedes hablar de ellos, pero NUNCA dar precios."""

appendix_en_new = """
  STRICT RULE: YOU ARE STRICTLY FORBIDDEN FROM GIVING PRICES OR ESTIMATES TO THE PUBLIC UNDER ANY CIRCUMSTANCES. If asked for prices, state that a specialized technician must evaluate the issue in person to provide an accurate quote.
  You DO know the 495 activities and services in our Price Book and can talk about them, but NEVER give their prices."""

# Para reemplazar, busco desde "REGLA ESTRICTA:" hasta el final del string """
# Uso re.sub con un regex que atrape ese bloque completo
content = re.sub(
    r'REGLA ESTRICTA:.*?Hidro-lavado comercial \(Commercial Hydro-Jetting\)',
    appendix_es_new.strip(),
    content,
    flags=re.DOTALL
)

content = re.sub(
    r'STRICT RULE:.*?Commercial Hydro-Jetting',
    appendix_en_new.strip(),
    content,
    flags=re.DOTALL
)

with open('brain.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("brain.py patched with 495 activities rule.")
