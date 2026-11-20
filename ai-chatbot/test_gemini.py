import time
import os
from dotenv import load_dotenv
from google import genai

load_dotenv(".env", override=True)
api_key = os.getenv("GEMINI_API_KEY", "").strip()

print(f"Loaded API Key: {api_key[:8]}... (length: {len(api_key)})")
client = genai.Client(api_key=api_key)

for model in ["gemini-3.1-flash-lite", "gemini-2.5-flash-lite", "gemini-3.5-flash-lite", "gemini-3.5-flash"]:
    t0 = time.time()
    try:
        response = client.models.generate_content(
            model=model,
            contents="Say 'OK' in one word."
        )
        elapsed = time.time() - t0
        print(f"SUCCESS with {model} in {elapsed:.2f}s: {response.text.strip()}")
    except Exception as e:
        print(f"FAILED with {model} in {time.time()-t0:.2f}s: {e}")
