
from main import ask_voice_ai, extract_appointment_info, brain

print('Has Gemini Client:', hasattr(brain, 'gemini_client'))
print('Gemini Client Is Not None:', brain.gemini_client is not None)

try:
    response = brain.gemini_client.models.generate_content(
        model='gemini-2.5-flash',
        contents='test'
    )
    print('Gemini call success!')
except Exception as e:
    print('Gemini call failed directly:', e)


