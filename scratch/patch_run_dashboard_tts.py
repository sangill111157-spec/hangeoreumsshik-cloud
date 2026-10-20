import re

path = 'run_dashboard.py'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add edge_tts import if not present
if 'import edge_tts' not in code:
    import_idx = code.find('import json')
    if import_idx != -1:
        code = code[:import_idx] + 'import edge_tts\nimport asyncio\nimport base64\n' + code[import_idx:]
    else:
        code = 'import edge_tts\nimport asyncio\nimport base64\n' + code

# 2. Add generate_neural_tts_audio function
func_def = '''
async def generate_neural_tts_audio(text: str, persona: str = "designer", pitch_offset: int = 0, rate_offset: int = 0) -> dict:
    """초고음질 엣지 신경망 TTS(Neural Voice) 합성 함수 (한국어 5대 보이스 페르소나)"""
    persona_configs = {
        "designer": {
            "voice": "ko-KR-SunHiNeural",
            "base_rate": -4,
            "base_pitch": 0,
            "title": "청담 수석 디자이너",
            "style": "우아하고 세련된 디자이너 톤"
        },
        "teen_sister": {
            "voice": "ko-KR-SunHiNeural",
            "base_rate": 10,
            "base_pitch": 14,
            "title": "하이틴 트렌디 언니",
            "style": "통통 튀고 발랄한 MZ 아이돌 멘토 톤"
        },
        "gentleman": {
            "voice": "ko-KR-InJoonNeural",
            "base_rate": -4,
            "base_pitch": -8,
            "title": "젠틀맨 테일러",
            "style": "중후하고 든든한 킹스맨 신사 톤"
        },
        "healing_dj": {
            "voice": "ko-KR-SunHiNeural",
            "base_rate": -10,
            "base_pitch": -5,
            "title": "심야 힐링 라디오 DJ",
            "style": "마음을 편안하게 감싸주는 포근한 힐링 톤"
        },
        "future_self": {
            "voice": "ko-KR-InJoonNeural",
            "base_rate": 3,
            "base_pitch": 4,
            "title": "2035 미래의 나",
            "style": "당당하고 확신에 찬 성공한 미래 리더 톤"
        }
    }

    cfg = persona_configs.get(persona, persona_configs["designer"])
    rate_val = cfg["base_rate"] + rate_offset
    pitch_val = cfg["base_pitch"] + pitch_offset
    rate_str = f"{rate_val:+d}%"
    pitch_str = f"{pitch_val:+d}Hz"

    try:
        communicate = edge_tts.Communicate(text, cfg["voice"], rate=rate_str, pitch=pitch_str)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        if audio_data:
            b64_audio = base64.b64encode(audio_data).decode("utf-8")
            return {
                "success": True,
                "status": "success",
                "audio_url": f"data:audio/mp3;base64,{b64_audio}",
                "engine": "edge-tts-neural",
                "voice": cfg["voice"],
                "persona": persona,
                "title": cfg["title"],
                "rate": rate_str,
                "pitch": pitch_str
            }
    except Exception as e:
        logger.error(f"[Neural TTS] 오류 발생: {e}")

    return {
        "success": False,
        "status": "fallback",
        "engine": "client-fallback",
        "persona": persona,
        "title": cfg["title"]
    }
'''

if 'def generate_neural_tts_audio' not in code:
    pos = code.find('def analyze_app_voc_evolution')
    if pos != -1:
        code = code[:pos] + func_def + '\n' + code[pos:]
    else:
        print("Warning: analyze_app_voc_evolution not found, appending to top functions")

# 3. Add handler in do_POST
handler_code = '''        # 17. 초고음질 신경망 TTS 음성 합성 (POST /api/neural-tts)
        if self.path == '/api/neural-tts':
            length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(length) if length > 0 else b'{}'
            try:
                data = json.loads(raw_body.decode('utf-8')) if raw_body else {}
                text = data.get("text", "").strip()
                persona = data.get("persona", "designer")
                pitch_offset = int(data.get("pitch_offset", 0))
                rate_offset = int(data.get("rate_offset", 0))

                if not text:
                    res = {"success": False, "error": "텍스트가 비어 있습니다."}
                else:
                    res = asyncio.run(generate_neural_tts_audio(text, persona, pitch_offset, rate_offset))

                resp_bytes = json.dumps(res, ensure_ascii=False).encode('utf-8')
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(resp_bytes)))
                self.end_headers()
                self.wfile.write(resp_bytes)
                return
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e), "success": False}).encode('utf-8'))
                return
'''

if '/api/neural-tts' not in code:
    voc_route_marker = "if self.path == '/api/app-voc-evolution':"
    idx = code.find(voc_route_marker)
    if idx != -1:
        code = code[:idx] + handler_code + '\n        ' + code[idx:]
        print("Successfully injected /api/neural-tts route into do_POST!")
    else:
        print("Error: voc_route_marker not found!")

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print("run_dashboard.py updated with Neural TTS engine!")
