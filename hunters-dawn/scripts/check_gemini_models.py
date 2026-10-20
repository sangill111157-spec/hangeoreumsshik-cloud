import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("[ERROR] GEMINI_API_KEY is missing.")
else:
    genai.configure(api_key=api_key)
    print("=== Gemini API Available Models ===")
    try:
        models = genai.list_models()
        img_vid_models = []
        for m in models:
            name = m.name
            if any(k in name.lower() for k in ['imagen', 'flash', 'veo', 'vision', 'generate']):
                img_vid_models.append(name)
                print(f"Model ID: {name} | Methods: {m.supported_generation_methods}")
        print(f"Total matching models found: {len(img_vid_models)}")
    except Exception as e:
        print(f"[ERROR] Failed to list models: {e}")
