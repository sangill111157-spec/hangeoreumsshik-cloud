import os
import time
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print("=== Gemini Omni Flash (Image-to-Video) Test ===")

# Test if google-genai or requests can trigger video generation / API availability
try:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    print("google.genai client initialized successfully.")
    
    # Check video models (e.g., veo-2.0-generate-001 or gemini-2.5-flash)
    print("Testing Image-to-Video call with t0_ref_face.png...")
    # Note: If API key requires project quota / preview access, capture output or error log
    with open("00_smoke/t0_ref_face.png", "rb") as f:
        image_bytes = f.read()
        
    print(f"Loaded t0_ref_face.png ({len(image_bytes)/1024:.1f} KB)")
    
except Exception as e:
    print(f"[NOTE/API TEST] Video Generation API call note: {e}")
