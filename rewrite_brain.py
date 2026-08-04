import re

with open('brain.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The Morales Plumbing system prompt
plumbing_prompt = """Eres Alex, el Dispatcher Principal y Asistente Virtual Inteligente de "Morales Plumbing", una empresa profesional de plomeria con licencia C-36 del estado de California.
Representas a la empresa en todos los canales de atencion.
Debes actuar exactamente como un dispatcher humano con muchos anos de experiencia.
Telefono: (669) 234-2444.
Tu objetivo principal es proteger primero a las personas y despues a la propiedad, agendar citas y brindar servicio al cliente de Morales Plumbing."""

# Replace all language prompts with the plumbing prompt
new_content = re.sub(r'"""Eres BRUNO.*?ORION Tech.*?("""|ORION TECH.*?""")', '"""' + plumbing_prompt + '"""', content, flags=re.DOTALL)
new_content = re.sub(r'"""You are BRUNO.*?ORION Tech.*?("""|ORION TECH.*?""")', '"""' + plumbing_prompt + '"""', new_content, flags=re.DOTALL)
new_content = re.sub(r'""".*?BRUNO.*?ORION Tech.*?("""|ORION TECH.*?""")', '"""' + plumbing_prompt + '"""', new_content, flags=re.DOTALL)

# Replace the fallback message
new_content = new_content.replace('Soy XONA de ORION Tech', 'Soy Alex de Morales Plumbing')
new_content = new_content.replace("I'm XONA from ORION Tech", "I'm Alex from Morales Plumbing")

with open('brain.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("brain.py updated successfully.")
