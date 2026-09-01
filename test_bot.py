import httpx

async def run_test():
    async with httpx.AsyncClient() as client:
        # Test incoming call menu
        response = await client.post("http://localhost:8000/incoming-call")
        print("1. INCOMING CALL MENU:")
        print(response.text)
        print("-" * 50)
        
        # Test Spanish endpoint (simulate pressing 2)
        response = await client.post("http://localhost:8000/select-language", data={"Digits": "2"})
        print("2. SELECT LANGUAGE (ES):")
        print(response.text)
        print("-" * 50)
        
        # Test processing speech in Spanish
        response = await client.post("http://localhost:8000/process-speech-es", data={"SpeechResult": "Necesito un plomero para mi baño, se rompió la tubería", "CallSid": "test1234"})
        print("3. PROCESS SPEECH (ES):")
        print(response.text)
        print("-" * 50)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_test())
