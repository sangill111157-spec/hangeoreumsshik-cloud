import json, re

# Load prebuilt base64 voices
with open('dashboard/audio/prebuilt_voices.json', 'r', encoding='utf-8') as f:
    b64_voices = json.load(f)

print(f"Loaded {len(b64_voices)} prebuilt base64 voices!")

# ==============================================================================
# HTML Component: 🎧 5대 하이엔드 보이스 스튜디오 (골드/퍼플 네온 박스)
# ==============================================================================
def get_voice_studio_html(prefix=""):
    p = prefix
    return f'''
        <!-- 🎧🔥 [5대 하이엔드 성우 & 트렌디 보이스 스튜디오 (모바일 최적화 골드/퍼플 네온 박스)] -->
        <div class="p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-purple-950/80 via-slate-900/95 to-amber-950/70 border-2 border-amber-400/80 shadow-2xl shadow-purple-900/40 space-y-3.5 my-3 relative overflow-hidden">
          <div class="absolute -right-10 -top-10 w-32 h-32 bg-amber-500/10 rounded-full blur-2xl pointer-events-none"></div>
          
          <div class="flex items-center justify-between flex-wrap gap-2 pb-2.5 border-b border-amber-500/30">
            <div class="flex items-center gap-2.5">
              <span class="text-2xl p-2 rounded-xl bg-gradient-to-tr from-amber-400 to-pink-500 text-slate-950 font-black shadow-lg shadow-amber-500/30">🎧</span>
              <div>
                <div class="flex items-center gap-2 flex-wrap">
                  <h4 class="font-black text-white text-sm sm:text-base tracking-wide flex items-center gap-1.5">
                    〈5대 하이엔드 성우 & 트렌디 보이스 스튜디오〉
                  </h4>
                  <span class="px-2 py-0.5 rounded-full text-[10px] font-black bg-amber-400 text-slate-950 uppercase tracking-wider animate-pulse">
                    v3.2 초고음질 Neural MP3 탑재
                  </span>
                </div>
                <p class="text-[11px] text-amber-200/90 mt-0.5">
                  기계음 0%! 5G 스마트폰·오프라인에서도 0.01초 만에 방송국 성우의 실제 사람 목소리가 터져 나옵니다.
                </p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span id="{p}voice-active-badge" class="px-2.5 py-1 rounded-xl bg-purple-600/40 border border-purple-400/50 text-purple-200 font-bold text-xs">
                현재 성우: 👩🎨 청담 디자이너
              </span>
            </div>
          </div>

          <!-- 5대 성우 선택 큼직한 모바일 터치 버튼 그리드 -->
          <div class="grid grid-cols-1 sm:grid-cols-5 gap-2 sm:gap-2.5" id="{p}voice-persona-buttons">
            <button type="button" onclick="selectStudioVoice('{p}', 'designer')" id="{p}btn-voice-designer" class="p-3 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 border-2 border-amber-300 text-left transition transform scale-[1.02] shadow-lg shadow-purple-900/50 flex sm:flex-col items-center sm:items-start justify-between">
              <div class="flex items-center sm:block gap-2">
                <span class="text-xl">👩🎨</span>
                <div>
                  <div class="text-xs font-black text-white">1. 청담 디자이너</div>
                  <div class="text-[10px] text-amber-200">우아·품격 여성</div>
                </div>
              </div>
              <span class="text-[10px] font-bold text-amber-300">선택됨 ✓</span>
            </button>

            <button type="button" onclick="selectStudioVoice('{p}', 'highteen')" id="{p}btn-voice-highteen" class="p-3 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700 text-left transition hover:scale-[1.01] flex sm:flex-col items-center sm:items-start justify-between">
              <div class="flex items-center sm:block gap-2">
                <span class="text-xl">💖</span>
                <div>
                  <div class="text-xs font-black text-slate-200">2. 하이틴 언니</div>
                  <div class="text-[10px] text-pink-300">발랄·힙한 MZ</div>
                </div>
              </div>
              <span class="text-[10px] font-bold text-slate-400">선택</span>
            </button>

            <button type="button" onclick="selectStudioVoice('{p}', 'gentleman')" id="{p}btn-voice-gentleman" class="p-3 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700 text-left transition hover:scale-[1.01] flex sm:flex-col items-center sm:items-start justify-between">
              <div class="flex items-center sm:block gap-2">
                <span class="text-xl">🤵</span>
                <div>
                  <div class="text-xs font-black text-slate-200">3. 젠틀맨 테일러</div>
                  <div class="text-[10px] text-amber-300">중후·신사 남성</div>
                </div>
              </div>
              <span class="text-[10px] font-bold text-slate-400">선택</span>
            </button>

            <button type="button" onclick="selectStudioVoice('{p}', 'dj')" id="{p}btn-voice-dj" class="p-3 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700 text-left transition hover:scale-[1.01] flex sm:flex-col items-center sm:items-start justify-between">
              <div class="flex items-center sm:block gap-2">
                <span class="text-xl">🌙</span>
                <div>
                  <div class="text-xs font-black text-slate-200">4. 심야 힐링 DJ</div>
                  <div class="text-[10px] text-cyan-300">따뜻·위로 감성</div>
                </div>
              </div>
              <span class="text-[10px] font-bold text-slate-400">선택</span>
            </button>

            <button type="button" onclick="selectStudioVoice('{p}', 'future')" id="{p}btn-voice-future" class="p-3 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700 text-left transition hover:scale-[1.01] flex sm:flex-col items-center sm:items-start justify-between">
              <div class="flex items-center sm:block gap-2">
                <span class="text-xl">🚀</span>
                <div>
                  <div class="text-xs font-black text-slate-200">5. 2035 미래의 나</div>
                  <div class="text-[10px] text-emerald-300">당당한 리더</div>
                </div>
              </div>
              <span class="text-[10px] font-bold text-slate-400">선택</span>
            </button>
          </div>

          <!-- 🔊 큼직한 고음질 재생 버튼 (메인 액션) -->
          <div class="pt-1">
            <button type="button" onclick="playSelectedStudioVoice('{p}')" id="{p}btn-play-voice-main" class="w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-amber-400 via-pink-500 to-purple-600 hover:from-amber-300 hover:via-pink-400 hover:to-purple-500 text-slate-950 font-black text-sm sm:text-base shadow-xl shadow-pink-500/25 flex items-center justify-center gap-2 transition active:scale-98">
              <span id="{p}voice-play-icon" class="text-xl">🔊</span>
              <span id="{p}voice-play-text">[선택한 성우 목소리 지금 바로 들어보기 (초고음질 Neural MP3 재생)]</span>
            </button>
          </div>

          <!-- 세부 튜닝 컨트롤러 (Pitch / Speed) -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-slate-800/80 text-xs">
            <div class="space-y-1">
              <div class="flex justify-between text-slate-300 text-[11px]">
                <span>목소리 톤 (Pitch)</span>
                <span id="{p}voice-pitch-label" class="text-amber-300 font-bold">기본 (0Hz)</span>
              </div>
              <input type="range" id="{p}voice-pitch-slider" min="-15" max="15" value="0" step="1" oninput="updateStudioVoiceSettings('{p}')" class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-400">
              <div class="flex justify-between text-[10px] text-slate-500">
                <span>차분하게</span>
                <span>발랄하게</span>
              </div>
            </div>
            <div class="space-y-1">
              <div class="flex justify-between text-slate-300 text-[11px]">
                <span>말하기 속도 (Speed)</span>
                <span id="{p}voice-rate-label" class="text-amber-300 font-bold">기본 (1.0x)</span>
              </div>
              <input type="range" id="{p}voice-rate-slider" min="0.8" max="1.3" value="1.0" step="0.05" oninput="updateStudioVoiceSettings('{p}')" class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-400">
              <div class="flex justify-between text-[10px] text-slate-500">
                <span>여유롭게 (0.8x)</span>
                <span>리드미컬하게 (1.3x)</span>
              </div>
            </div>
          </div>
        </div>
'''

# JavaScript Engine to inject into both files
js_b64_json = json.dumps(b64_voices, ensure_ascii=False)

voice_engine_js = f'''
    // 🎧🔥 [초고음질 Neural MP3 Base64 캐시 및 5대 성우 하이브리드 엔진]
    const PREBUILT_NEURAL_VOICES = {js_b64_json};

    const STUDIO_PERSONAS = {{
      designer: {{
        id: 'designer',
        name: '청담 디자이너',
        avatar: '👩🎨',
        title: '우아·품격 여성',
        audioUrl: '/audio/voice_designer.mp3',
        text: '대표님, 안녕하세요! 청담동 수석 디자이너입니다. 오늘 고르신 청담 VIP 수트 라인이 어깨선을 예술적으로 잡아주네요. 정면 V존 비율부터 뒷모습 실루엣까지 완벽한 걸작입니다.'
      }},
      highteen: {{
        id: 'highteen',
        name: '하이틴 언니',
        avatar: '💖',
        title: '발랄·힙한 MZ',
        audioUrl: '/audio/voice_highteen.mp3',
        text: '우와! 대표님, 이 코디 진짜 트렌디하고 예뻐요! 친구들이 어디서 샀냐고 다들 물어보겠는데요? 오늘 자신감 뿜뿜해서 당당하게 걸어봐요!'
      }},
      gentleman: {{
        id: 'gentleman',
        name: '젠틀맨 테일러',
        avatar: '🤵',
        title: '중후·신사 남성',
        audioUrl: '/audio/voice_gentleman.mp3',
        text: '대표님, 멋진 안목이십니다. 단정하면서도 기품 있는 실루엣이 상대를 편안하고 신뢰감 있게 이끌어 주는군요. 오늘 성공은 따놓은 당상입니다.'
      }},
      dj: {{
        id: 'dj',
        name: '심야 힐링 DJ',
        avatar: '🌙',
        title: '따뜻·위로 감성',
        audioUrl: '/audio/voice_dj.mp3',
        text: '오늘 하루도 참 고생 많으셨어요. 편안한 옷처럼 당신의 마음도 따뜻하게 쉴 수 있기를 바랄게요. 당신은 언제나 소중한 사람입니다.'
      }},
      future: {{
        id: 'future',
        name: '2035 미래의 나',
        avatar: '🚀',
        title: '당당한 리더',
        audioUrl: '/audio/voice_future.mp3',
        text: '안녕, 과거의 나! 오늘의 멋진 선택과 따뜻한 인성 실천이 10년 뒤 위대한 글로벌 결실을 맺었어. 끝까지 나를 믿고 당당하게 전진하자!'
      }}
    }};

    let globalSelectedVoicePersona = 'designer';
    let globalVoicePitchOffset = 0;
    let globalVoiceSpeedRate = 1.0;
    let studioActiveAudio = null;

    function selectStudioVoice(prefix, id) {{
      if (!STUDIO_PERSONAS[id]) return;
      globalSelectedVoicePersona = id;

      const personas = Object.keys(STUDIO_PERSONAS);
      personas.forEach(k => {{
        ['', 'c3_'].forEach(p => {{
          const btn = document.getElementById(p + 'btn-voice-' + k);
          if (btn) {{
            if (k === id) {{
              btn.className = 'p-3 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 border-2 border-amber-300 text-left transition transform scale-[1.02] shadow-lg shadow-purple-900/50 flex sm:flex-col items-center sm:items-start justify-between';
              const s = btn.querySelector('span:last-child');
              if (s) s.className = 'text-[10px] font-bold text-amber-300';
              if (s) s.innerText = '선택됨 ✓';
            }} else {{
              btn.className = 'p-3 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700 text-left transition hover:scale-[1.01] flex sm:flex-col items-center sm:items-start justify-between';
              const s = btn.querySelector('span:last-child');
              if (s) s.className = 'text-[10px] font-bold text-slate-400';
              if (s) s.innerText = '선택';
            }}
          }});
          const badge = document.getElementById(p + 'voice-active-badge');
          if (badge) {{
            badge.innerText = '현재 성우: ' + STUDIO_PERSONAS[id].avatar + ' ' + STUDIO_PERSONAS[id].name;
          }}
        }});
      }});

      showToast(STUDIO_PERSONAS[id].avatar + ' ' + STUDIO_PERSONAS[id].name + ' 성우가 선택되었습니다!', 'success');
    }}

    function updateStudioVoiceSettings(prefix) {{
      const pSlider = document.getElementById(prefix + 'voice-pitch-slider');
      const rSlider = document.getElementById(prefix + 'voice-rate-slider');
      if (pSlider) {{
        globalVoicePitchOffset = parseInt(pSlider.value, 10) || 0;
        const l = document.getElementById(prefix + 'voice-pitch-label');
        if (l) l.innerText = (globalVoicePitchOffset > 0 ? '+' : '') + globalVoicePitchOffset + 'Hz';
      }}
      if (rSlider) {{
        globalVoiceSpeedRate = parseFloat(rSlider.value) || 1.0;
        const l = document.getElementById(prefix + 'voice-rate-label');
        if (l) l.innerText = globalVoiceSpeedRate.toFixed(2) + 'x';
      }}
    }}

    // 0.01초 즉시 재생: 내장 Base64 또는 정적 MP3로 재생 (기계음 절대 불가!)
    async function playSelectedStudioVoice(prefix) {{
      const persona = STUDIO_PERSONAS[globalSelectedVoicePersona] || STUDIO_PERSONAS.designer;
      const b64Data = PREBUILT_NEURAL_VOICES[globalSelectedVoicePersona];

      // 기존 오디오 중지
      if (studioActiveAudio) {{
        try {{
          studioActiveAudio.pause();
          studioActiveAudio.currentTime = 0;
        }} catch(e) {{}}
        studioActiveAudio = null;
      }}
      if ('speechSynthesis' in window) {{
        window.speechSynthesis.cancel();
      }}

      // UI 애니메이션
      ['', 'c3_'].forEach(p => {{
        const icon = document.getElementById(p + 'voice-play-icon');
        const txt = document.getElementById(p + 'voice-play-text');
        if (icon) icon.innerText = '⚡';
        if (txt) txt.innerText = '[' + persona.name + ' 성우 음성 재생 중...]';
      }});

      const resetUI = () => {{
        ['', 'c3_'].forEach(p => {{
          const icon = document.getElementById(p + 'voice-play-icon');
          const txt = document.getElementById(p + 'voice-play-text');
          if (icon) icon.innerText = '🔊';
          if (txt) txt.innerText = '[선택한 성우 목소리 지금 바로 들어보기 (초고음질 Neural MP3 재생)]';
        }});
      }};

      try {{
        // 1순위: 내장된 Base64 오디오 데이터로 재생 (통신 실패 불가능, 0.01초 즉시 재생)
        const audioSrc = b64Data || persona.audioUrl;
        const audio = new Audio(audioSrc);
        studioActiveAudio = audio;
        audio.playbackRate = globalVoiceSpeedRate;
        if ('preservesPitch' in audio) {{
          audio.preservesPitch = true;
        }}

        audio.onended = resetUI;
        audio.onerror = () => {{
          console.warn('Audio playback error, falling back to static MP3 file:', persona.audioUrl);
          const fbAudio = new Audio(persona.audioUrl);
          studioActiveAudio = fbAudio;
          fbAudio.playbackRate = globalVoiceSpeedRate;
          fbAudio.onended = resetUI;
          fbAudio.onerror = () => {{
            resetUI();
            showToast('오디오 재생을 위해 화면을 한 번 터치해 주세요.', 'info');
          }};
          fbAudio.play();
        }};

        await audio.play();
        showToast(persona.avatar + ' ' + persona.name + ' 고음질 음성이 재생됩니다!', 'info');
        return;
      }} catch (err) {{
        console.warn('Direct audio play failed (user interaction required):', err);
        resetUI();
        showToast('스마트폰 화면을 터치하시면 즉시 음성이 재생됩니다.', 'info');
      }}
    }}

    // 동적 텍스트 발성 (대시보드 & 모바일 앱 공용)
    async function playSmartNeuralVoice(text, forcePersona) {{
      const personaKey = forcePersona || globalSelectedVoicePersona || 'designer';
      const persona = STUDIO_PERSONAS[personaKey] || STUDIO_PERSONAS.designer;

      // 대표 멘트와 일치하면 내장 Base64로 즉시 재생!
      if (!text || text === persona.text) {{
        playSelectedStudioVoice('');
        return;
      }}

      // 서버 연결 시 실시간 API 호출
      try {{
        const resp = await fetch('/api/neural-tts', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            text: text,
            persona: personaKey,
            pitch_offset: globalVoicePitchOffset,
            rate_offset: Math.round((globalVoiceSpeedRate - 1.0) * 50)
          }})
        }});
        if (resp.ok) {{
          const res = await resp.json();
          if (res.success && res.audio_url) {{
            if (studioActiveAudio) {{
              try {{ studioActiveAudio.pause(); }} catch(e) {{}}
            }}
            const audio = new Audio(res.audio_url);
            studioActiveAudio = audio;
            audio.playbackRate = globalVoiceSpeedRate;
            await audio.play();
            return;
          }}
        }}
      }} catch(e) {{
        console.warn('Neural TTS API failed, playing prebuilt persona voice instead:', e);
      }}

      // 통신 불가 시 사전 녹음된 성우 음성으로 친절히 대체 (기계음 절대 방지!)
      playSelectedStudioVoice('');
    }}

    // 캐시 강제 갱신 함수 (대표님 모바일 캐시 파괴)
    function forceBustMobileCache() {{
      const newUrl = window.location.pathname + '?v=' + Date.now() + (window.location.hash || '#tab-daughters');
      window.location.href = newUrl;
      setTimeout(() => {{
        window.location.reload(true);
      }}, 100);
    }}
'''

# ==============================================================================
# Patch dashboard/index.html
# ==============================================================================
with open('dashboard/index.html', 'r', encoding='utf-8') as f:
    dash_html = f.read()

# 1. Add cache-control meta tags if not already present
cache_meta = '''  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">'''
if 'Cache-Control' not in dash_html:
    dash_html = dash_html.replace('<head>', '<head>\n' + cache_meta, 1)

# 2. Update version badge in header
dash_html = re.sub(
    r'<span class="text-xs text-purple-300 font-mono">v[0-9\.]+.*?</span>',
    '<span onclick="forceBustMobileCache()" class="text-xs text-amber-300 font-mono font-bold cursor-pointer hover:underline bg-amber-500/20 px-2 py-0.5 rounded-full border border-amber-400/40" title="터치 시 모바일 캐시 즉시 갱신">v3.2 [🎙️보이스스튜디오 탑재]</span>',
    dash_html
)

# 3. Clean up any previous inserted voice studios to avoid duplication
dash_html = re.sub(r'<!-- 🎙️✨ 5대 하이엔드 보이스 페르소나 스튜디오.*?<!-- 세부 튜닝 슬라이더.*?</div>\s*</div>', '', dash_html, flags=re.DOTALL)
dash_html = re.sub(r'<!-- 🎧🔥 \[5대 하이엔드 성우.*?<!-- 세부 튜닝 컨트롤러.*?</div>\s*</div>', '', dash_html, flags=re.DOTALL)

# 4. Insert Voice Studio at Card 1 (Under Dream Closet Header)
card1_marker = '<div class="p-4 rounded-xl bg-slate-950/80 border border-purple-500/30 space-y-2.5">'
if card1_marker in dash_html:
    dash_html = dash_html.replace(card1_marker, get_voice_studio_html('') + '\n\n        ' + card1_marker, 1)
    print("Injected Voice Studio into Card 1 in dashboard/index.html!")

# 5. Insert Voice Studio at Card 3 (Inside 양방향 보이스 소통 카드)
card3_marker = '<span>양방향 보이스 소통 & 긍정 확언 스피치</span>'
if card3_marker in dash_html:
    # insert before the closing of that speech recognition box
    pos = dash_html.find(card3_marker)
    box_end = dash_html.find('</div>\n          </div>\n        </div>', pos)
    if box_end != -1:
        dash_html = dash_html[:box_end] + get_voice_studio_html('c3_') + '\n            ' + dash_html[box_end:]
        print("Injected Voice Studio into Card 3 in dashboard/index.html!")

# 6. Inject voice_engine_js into script
if 'PREBUILT_NEURAL_VOICES' not in dash_html:
    script_end = dash_html.rfind('</script>')
    if script_end != -1:
        dash_html = dash_html[:script_end] + voice_engine_js + '\n  ' + dash_html[script_end:]
        print("Injected voice_engine_js into dashboard/index.html!")
else:
    # update voice_engine_js
    pat = re.compile(r'// 🎧🔥 \[초고음질 Neural MP3 Base64 캐시.*?function forceBustMobileCache\(\).*?\}\s*', re.DOTALL)
    if pat.search(dash_html):
        dash_html = pat.sub(voice_engine_js, dash_html, count=1)
        print("Updated voice_engine_js in dashboard/index.html!")

with open('dashboard/index.html', 'w', encoding='utf-8') as f:
    f.write(dash_html)

print("dashboard/index.html updated successfully!")


# ==============================================================================
# Patch dashboard/dream_closet_future_master_app.html
# ==============================================================================
with open('dashboard/dream_closet_future_master_app.html', 'r', encoding='utf-8') as f:
    app_html = f.read()

# 1. Add cache-control meta tags
if 'Cache-Control' not in app_html:
    app_html = app_html.replace('<head>', '<head>\n' + cache_meta, 1)

# 2. Update version badge
app_html = app_html.replace('v1.2 (초고음질 Neural Voice & 5대 보이스 스튜디오 가동)', 'v3.2 [🎙️5대 성우 Neural MP3 스튜디오 탑재]')
app_html = app_html.replace('v1.2 (High-End Neural Voice Patch)', 'v3.2 (Neural Voice Masterpiece)')

# 3. Clean up previous
app_html = re.sub(r'<!-- 🎙️✨ 5대 하이엔드 보이스 페르소나 스튜디오.*?<!-- 세부 튜닝 슬라이더.*?</div>\s*</div>', '', app_html, flags=re.DOTALL)
app_html = re.sub(r'<!-- 🎧🔥 \[5대 하이엔드 성우.*?<!-- 세부 튜닝 컨트롤러.*?</div>\s*</div>', '', app_html, flags=re.DOTALL)

# 4. Insert at top of main container
app_header_target = '<div class="grid grid-cols-1 lg:grid-cols-12 gap-6">'
if app_header_target in app_html:
    app_html = app_html.replace(app_header_target, get_voice_studio_html('') + '\n\n    ' + app_header_target, 1)
    print("Injected Voice Studio into dream_closet_future_master_app.html!")

# 5. Inject voice_engine_js into standalone app
if 'PREBUILT_NEURAL_VOICES' not in app_html:
    script_end = app_html.rfind('</script>')
    if script_end != -1:
        app_html = app_html[:script_end] + voice_engine_js + '\n  ' + app_html[script_end:]
        print("Injected voice_engine_js into dream_closet_future_master_app.html!")

with open('dashboard/dream_closet_future_master_app.html', 'w', encoding='utf-8') as f:
    f.write(app_html)

print("dream_closet_future_master_app.html updated successfully!")
