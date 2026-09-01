
import os
import openai
from google import genai
from dotenv import load_dotenv

load_dotenv()

print('Testing OpenAI...')
try:
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Hello'}],
        max_tokens=10
    )
    print('OpenAI Success:', response.choices[0].message.content)
except Exception as e:
    print('OpenAI Error:', e)

print('\nTesting Gemini...')
try:
    gemini_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    response = gemini_client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Hello'
    )
    print('Gemini Success:', response.text)
except Exception as e:
    print('Gemini Error:', e)

