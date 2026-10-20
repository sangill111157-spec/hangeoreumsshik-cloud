import re

# ==============================================================================
# 1. Patch dashboard/dream_closet_future_master_app.html
# ==============================================================================

app_path = 'dashboard/dream_closet_future_master_app.html'
with open(app_path, 'r', encoding='utf-8') as f:
    app_html = f.read()

# Update version badges
app_html = app_html.replace('v1.0 (초격차 5대 마스터 모듈 가동)', 'v1.2 (초고음질 Neural Voice & 5대 보이스 스튜디오 가동)')
app_html = app_html.replace('v1.0 (최신 배포판)', 'v1.2 (High-End Neural Voice Patch)')
app_html = app_html.replace("current_version: 'v1.0'", "current_version: 'v1.2'")
app_html = app_html.replace("current_version: 'v1.1'", "current_version: 'v1.2'")

voice_studio_ui = '''
      <!-- 🎙️✨ 5대 하이엔드 보이스 페르소나 스튜디오 -->
      <div class="glass-card rounded-2xl p-4 border border-fuchsia-500/30 bg-gradient-to-r from-slate-900/90 via-purple-950/40 to-slate-900/90 shadow-xl space-y-3">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div class="flex items-center gap-2">
            <span class="text-xl">🎙️</span>
            <div>
              <h4 class="font-bold text-white text-xs flex items-center gap-2">
                5대 하이엔드 보이스 페르소나 스튜디오
                <span class="px-2 py-0.5 rounded-full text-[10px] bg-fuchsia-500/20 text-fuchsia-300 border border-fuchsia-500/40 font-bold">Neural Dual-Engine</span>
              </h4>
              <p class="text-[11px] text-slate-400">기계음 완전 탈피! 청담 디자이너부터 힙한 하이틴 언니까지 원하는 성우를 직접 선택하세요.</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button type="button" onclick="previewCurrentVoice()" class="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-400 hover:to-purple-500 text-white font-bold text-xs shadow-lg shadow-pink-500/20 flex items-center gap-1.5 transition active:scale-95">
              <span id="voice-indicator-icon">🔊</span>
              <span>목소리 미리듣기</span>
            </button>
          </div>
        </div>

        <!-- 5대 보이스 칩 -->
        <div class="grid grid-cols-2 sm:grid-cols-5 gap-2" id="voice-persona-chips">
          <button type="button" onclick="selectVoicePersona('designer')" id="voice-chip-designer" class="p-2.5 rounded-xl bg-purple-600/30 border-2 border-purple-400 text-left transition hover:scale-[1.02] shadow-lg shadow-purple-500/10">
            <div class="text-base mb-0.5">👩🎨</div>
            <div class="text-xs font-bold text-white">청담 디자이너</div>
            <div class="text-[10px] text-purple-300">우아·품격 여성</div>
          </button>
          <button type="button" onclick="selectVoicePersona('teen_sister')" id="voice-chip-teen_sister" class="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-left transition hover:scale-[1.02]">
            <div class="text-base mb-0.5">💖</div>
            <div class="text-xs font-bold text-slate-200">하이틴 언니</div>
            <div class="text-[10px] text-pink-300">발랄·힙한 MZ</div>
          </button>
          <button type="button" onclick="selectVoicePersona('gentleman')" id="voice-chip-gentleman" class="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-left transition hover:scale-[1.02]">
            <div class="text-base mb-0.5">🤵</div>
            <div class="text-xs font-bold text-slate-200">젠틀맨 테일러</div>
            <div class="text-[10px] text-amber-300">중후·신뢰감 남성</div>
          </button>
          <button type="button" onclick="selectVoicePersona('healing_dj')" id="voice-chip-healing_dj" class="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-left transition hover:scale-[1.02]">
            <div class="text-base mb-0.5">🌙</div>
            <div class="text-xs font-bold text-slate-200">힐링 DJ</div>
            <div class="text-[10px] text-cyan-300">감성·위로 보이스</div>
          </button>
          <button type="button" onclick="selectVoicePersona('future_self')" id="voice-chip-future_self" class="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-left transition hover:scale-[1.02]">
            <div class="text-base mb-0.5">🚀</div>
            <div class="text-xs font-bold text-slate-200">2035 미래의 나</div>
            <div class="text-[10px] text-emerald-300">당당한 리더</div>
          </button>
        </div>

        <!-- 세부 튜닝 슬라이더 -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-slate-800/80 text-xs">
          <div class="space-y-1">
            <div class="flex justify-between text-slate-400 text-[11px]">
              <span>목소리 톤 (Pitch)</span>
              <span id="voice-pitch-label" class="text-purple-300 font-semibold">기본 (0Hz)</span>
            </div>
            <input type="range" id="voice-pitch-slider" min="-15" max="15" value="0" step="1" oninput="updateVoiceSettings()" class="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500">
            <div class="flex justify-between text-[10px] text-slate-500">
              <span>차분하게</span>
              <span>발랄하게</span>
            </div>
          </div>
          <div class="space-y-1">
            <div class="flex justify-between text-slate-400 text-[11px]">
              <span>말하기 속도 (Rate)</span>
              <span id="voice-rate-label" class="text-purple-300 font-semibold">기본 (0%)</span>
            </div>
            <input type="range" id="voice-rate-slider" min="-15" max="15" value="0" step="1" oninput="updateVoiceSettings()" class="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500">
            <div class="flex justify-between text-[10px] text-slate-500">
              <span>여유롭게</span>
              <span>리드미컬하게</span>
            </div>
          </div>
        </div>
      </div>
'''

# Insert above the main 2-column grid or canvas column
col_target = '<div class="grid grid-cols-1 lg:grid-cols-12 gap-6">'
if '5대 하이엔드 보이스 페르소나 스튜디오' not in app_html:
    if col_target in app_html:
        app_html = app_html.replace(col_target, voice_studio_ui + '\n\n    ' + col_target, 1)
        print("Inserted Voice Studio UI into app_html before main grid!")

# JS logic replacement for app_html
voice_js_code = '''    // 🎙️✨ 5대 하이엔드 보이스 페르소나 & 듀얼 엔진 (Edge Neural TTS + WebSpeech Fallback) ✨🎙️
    const DREAM_VOICE_PERSONAS = {
      designer: {
        id: 'designer',
        name: '청담 수석 디자이너',
        badge: '우아·품격 여성',
        avatar: '👩🎨',
        sample: '대표님, 오늘 고르신 청담 VIP 수트 라인이 어깨선을 예술적으로 잡아주네요. 정면 V존 비율부터 뒷모습 실루엣까지 완벽한 걸작입니다.',
        webPitch: 1.0,
        webRate: 0.95
      },
      teen_sister: {
        id: 'teen_sister',
        name: '하이틴 트렌디 언니',
        badge: '발랄·힙한 MZ',
        avatar: '💖',
        sample: '우와! 이 코디 진짜 트렌디하고 예쁘다! 친구들이 어디서 샀냐고 다들 물어보겠는데요? 오늘 자신감 뿜뿜해서 당당하게 걸어봐요!',
        webPitch: 1.25,
        webRate: 1.10
      },
      gentleman: {
        id: 'gentleman',
        name: '젠틀맨 테일러',
        badge: '중후·신뢰감 남성',
        avatar: '🤵',
        sample: '멋진 안목이십니다. 단정하면서도 기품 있는 실루엣이 상대를 편안하고 신뢰감 있게 이끌어 주는군요. 오늘 성공은 따놓은 당상입니다.',
        webPitch: 0.85,
        webRate: 0.95
      },
      healing_dj: {
        id: 'healing_dj',
        name: '심야 힐링 라디오 DJ',
        badge: '감성·위로 보이스',
        avatar: '🌙',
        sample: '오늘 하루도 참 고생 많으셨어요. 편안한 옷처럼 당신의 마음도 따뜻하게 쉴 수 있기를 바랄게요. 당신은 언제나 소중한 사람입니다.',
        webPitch: 0.92,
        webRate: 0.88
      },
      future_self: {
        id: 'future_self',
        name: '2035 미래의 나',
        badge: '당당한 리더',
        avatar: '🚀',
        sample: '안녕, 과거의 나! 오늘의 멋진 선택과 따뜻한 인성 실천이 10년 뒤 위대한 결실을 맺었어! 끝까지 나를 믿고 당당하게 전진하자!',
        webPitch: 1.05,
        webRate: 1.02
      }
    };

    let currentVoicePersona = 'designer';
    let currentPitchOffset = 0;
    let currentRateOffset = 0;
    let currentAudioPlayer = null;

    function selectVoicePersona(id) {
      if (!DREAM_VOICE_PERSONAS[id]) return;
      currentVoicePersona = id;
      const allIds = Object.keys(DREAM_VOICE_PERSONAS);
      allIds.forEach(k => {
        const chip = document.getElementById('voice-chip-' + k);
        if (chip) {
          if (k === id) {
            chip.className = 'p-2.5 rounded-xl bg-purple-600/30 border-2 border-purple-400 text-left transition scale-[1.02] shadow-lg shadow-purple-500/20';
            const t = chip.querySelector('.text-xs');
            if (t) t.className = 'text-xs font-bold text-white';
          } else {
            chip.className = 'p-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-left transition hover:scale-[1.02]';
            const t = chip.querySelector('.text-xs');
            if (t) t.className = 'text-xs font-bold text-slate-200';
          }
        }
      });
      showToast(DREAM_VOICE_PERSONAS[id].avatar + ' ' + DREAM_VOICE_PERSONAS[id].name + ' 성우로 변경되었습니다!', 'info');
    }

    function updateVoiceSettings() {
      const pSlider = document.getElementById('voice-pitch-slider');
      const rSlider = document.getElementById('voice-rate-slider');
      if (pSlider) {
        currentPitchOffset = parseInt(pSlider.value, 10) || 0;
        const pLabel = document.getElementById('voice-pitch-label');
        if (pLabel) pLabel.innerText = (currentPitchOffset > 0 ? '+' : '') + currentPitchOffset + 'Hz';
      }
      if (rSlider) {
        currentRateOffset = parseInt(rSlider.value, 10) || 0;
        const rLabel = document.getElementById('voice-rate-label');
        if (rLabel) rLabel.innerText = (currentRateOffset > 0 ? '+' : '') + currentRateOffset + '%';
      }
    }

    function previewCurrentVoice() {
      const p = DREAM_VOICE_PERSONAS[currentVoicePersona] || DREAM_VOICE_PERSONAS.designer;
      speakText(p.sample, currentVoicePersona);
    }

    // 대화형 트렌디 구어체 스크립트 스타일러
    function getStyledSpeechScript(rawText, personaKey) {
      if (!rawText) return '';
      const p = personaKey || currentVoicePersona || 'designer';
      if (rawText.length > 80) return rawText; // 긴 문장은 원문 유지

      if (p === 'teen_sister') {
        return '우와! ' + rawText.replace('입니다.', '이에요! 완전 찰떡이죠?').replace('하십시오.', '해봐요 대박!') + ' 자신감 뿜뿜!';
      } else if (p === 'gentleman') {
        return '기품 있는 선택이십니다. ' + rawText;
      } else if (p === 'healing_dj') {
        return '오늘도 참 애쓰셨어요. ' + rawText + ' 언제나 곁에서 응원할게요.';
      } else if (p === 'future_self') {
        return '안녕! 미래의 내가 전하는 말이야. ' + rawText + ' 넌 정말 멋진 사람이야!';
      }
      // designer default
      return '대표님, ' + rawText;
    }

    async function speakText(text, forcePersona) {
      const personaKey = forcePersona || currentVoicePersona || 'designer';
      const persona = DREAM_VOICE_PERSONAS[personaKey] || DREAM_VOICE_PERSONAS.designer;
      const finalText = getStyledSpeechScript(text, personaKey);

      // 기존 오디오 중단
      if (currentAudioPlayer) {
        try {
          currentAudioPlayer.pause();
          currentAudioPlayer.currentTime = 0;
        } catch(e) {}
        currentAudioPlayer = null;
      }
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }

      const ind = document.getElementById('voice-indicator-icon');
      if (ind) ind.innerText = '⚡';

      // 1. 고음질 백엔드 Neural TTS API 호출 시도
      try {
        const resp = await fetch('/api/neural-tts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: finalText,
            persona: personaKey,
            pitch_offset: currentPitchOffset,
            rate_offset: currentRateOffset
          })
        });
        if (resp.ok) {
          const res = await resp.json();
          if (res.success && res.audio_url) {
            const audio = new Audio(res.audio_url);
            currentAudioPlayer = audio;
            audio.onended = () => { if (ind) ind.innerText = '🔊'; };
            audio.onerror = () => { fallbackWebSpeech(finalText, persona); };
            await audio.play();
            return;
          }
        }
      } catch (e) {
        console.warn('Backend neural TTS failed, falling back to WebSpeech:', e);
      }

      // 2. 오프라인 또는 API 미응답 시 고품질 WebSpeech 폴백
      fallbackWebSpeech(finalText, persona);
    }

    function fallbackWebSpeech(text, persona) {
      const ind = document.getElementById('voice-indicator-icon');
      if (!('speechSynthesis' in window)) {
        if (ind) ind.innerText = '🔊';
        return;
      }
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'ko-KR';

      const voices = window.speechSynthesis.getVoices();
      const bestVoice = voices.find(v => v.lang.includes('ko') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('SunHi') || v.name.includes('Yuna')))
                     || voices.find(v => v.lang.includes('ko'));
      if (bestVoice) utterance.voice = bestVoice;

      const pOffset = currentPitchOffset / 50.0;
      const rOffset = currentRateOffset / 50.0;
      utterance.pitch = Math.max(0.5, Math.min(2.0, persona.webPitch + pOffset));
      utterance.rate = Math.max(0.5, Math.min(2.0, persona.webRate + rOffset));

      utterance.onend = () => { if (ind) ind.innerText = '🔊'; };
      utterance.onerror = () => { if (ind) ind.innerText = '🔊'; };
      window.speechSynthesis.speak(utterance);
    }
'''

# Replace speakText in app_html
old_speak_pattern = re.compile(r'function speakText\(text\)\s*\{.*?window\.speechSynthesis\.speak\(utterance\);\s*\}', re.DOTALL)
if old_speak_pattern.search(app_html):
    app_html = old_speak_pattern.sub(voice_js_code, app_html, count=1)
    print("Replaced speakText with high-end voice_js_code in dream_closet_future_master_app.html!")

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_html)

print("dream_closet_future_master_app.html updated successfully!")


# ==============================================================================
# 2. Patch dashboard/index.html (Tab 4 Dream Closet section)
# ==============================================================================

dash_path = 'dashboard/index.html'
with open(dash_path, 'r', encoding='utf-8') as f:
    dash_html = f.read()

# Update version badges
dash_html = dash_html.replace('v1.0 (초격차 5대 마스터 모듈 가동)', 'v1.2 (초고음질 Neural Voice & 5대 보이스 스튜디오 가동)')
dash_html = dash_html.replace('v1.0 (최신 배포판)', 'v1.2 (High-End Neural Voice Patch)')
dash_html = dash_html.replace("current_version: 'v1.0'", "current_version: 'v1.2'")
dash_html = dash_html.replace("current_version: 'v1.1'", "current_version: 'v1.2'")

# Voice Studio UI for Dashboard Tab 4 (with distinctive IDs)
dash_voice_studio_ui = '''
      <!-- 🎙️✨ 5대 하이엔드 보이스 페르소나 스튜디오 (대시보드) -->
      <div class="glass-card rounded-2xl p-4 border border-fuchsia-500/30 bg-gradient-to-r from-slate-900/90 via-purple-950/40 to-slate-900/90 shadow-xl space-y-3">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div class="flex items-center gap-2">
            <span class="text-xl">🎙️</span>
            <div>
              <h4 class="font-bold text-white text-xs flex items-center gap-2">
                5대 하이엔드 보이스 페르소나 스튜디오
                <span class="px-2 py-0.5 rounded-full text-[10px] bg-fuchsia-500/20 text-fuchsia-300 border border-fuchsia-500/40 font-bold">Neural Dual-Engine</span>
              </h4>
              <p class="text-[11px] text-slate-400">기계음 완전 탈피! 청담 디자이너부터 힙한 하이틴 언니까지 원하는 성우를 직접 선택하세요.</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button type="button" onclick="previewCurrentVoiceDashboard()" class="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-400 hover:to-purple-500 text-white font-bold text-xs shadow-lg shadow-pink-500/20 flex items-center gap-1.5 transition active:scale-95">
              <span id="dash-voice-indicator-icon">🔊</span>
              <span>목소리 미리듣기</span>
            </button>
          </div>
        </div>

        <!-- 5대 보이스 칩 -->
        <div class="grid grid-cols-2 sm:grid-cols-5 gap-2" id="dash-voice-persona-chips">
          <button type="button" onclick="selectVoicePersonaDashboard('designer')" id="dash-voice-chip-designer" class="p-2.5 rounded-xl bg-purple-600/30 border-2 border-purple-400 text-left transition hover:scale-[1.02] shadow-lg shadow-purple-500/10">
            <div class="text-base mb-0.5">👩🎨</div>
            <div class="text-xs font-bold text-white">청담 디자이너</div>
            <div class="text-[10px] text-purple-300">우아·품격 여성</div>
          </button>
          <button type="button" onclick="selectVoicePersonaDashboard('teen_sister')" id="dash-voice-chip-teen_sister" class="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-left transition hover:scale-[1.02]">
            <div class="text-base mb-0.5">💖</div>
            <div class="text-xs font-bold text-slate-200">하이틴 언니</div>
            <div class="text-[10px] text-pink-300">발랄·힙한 MZ</div>
          </button>
          <button type="button" onclick="selectVoicePersonaDashboard('gentleman')" id="dash-voice-chip-gentleman" class="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-left transition hover:scale-[1.02]">
            <div class="text-base mb-0.5">🤵</div>
            <div class="text-xs font-bold text-slate-200">젠틀맨 테일러</div>
            <div class="text-[10px] text-amber-300">중후·신뢰감 남성</div>
          </button>
          <button type="button" onclick="selectVoicePersonaDashboard('healing_dj')" id="dash-voice-chip-healing_dj" class="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-left transition hover:scale-[1.02]">
            <div class="text-base mb-0.5">🌙</div>
            <div class="text-xs font-bold text-slate-200">힐링 DJ</div>
            <div class="text-[10px] text-cyan-300">감성·위로 보이스</div>
          </button>
          <button type="button" onclick="selectVoicePersonaDashboard('future_self')" id="dash-voice-chip-future_self" class="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-left transition hover:scale-[1.02]">
            <div class="text-base mb-0.5">🚀</div>
            <div class="text-xs font-bold text-slate-200">2035 미래의 나</div>
            <div class="text-[10px] text-emerald-300">당당한 리더</div>
          </button>
        </div>

        <!-- 세부 튜닝 슬라이더 -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-slate-800/80 text-xs">
          <div class="space-y-1">
            <div class="flex justify-between text-slate-400 text-[11px]">
              <span>목소리 톤 (Pitch)</span>
              <span id="dash-voice-pitch-label" class="text-purple-300 font-semibold">기본 (0Hz)</span>
            </div>
            <input type="range" id="dash-voice-pitch-slider" min="-15" max="15" value="0" step="1" oninput="updateVoiceSettingsDashboard()" class="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500">
            <div class="flex justify-between text-[10px] text-slate-500">
              <span>차분하게</span>
              <span>발랄하게</span>
            </div>
          </div>
          <div class="space-y-1">
            <div class="flex justify-between text-slate-400 text-[11px]">
              <span>말하기 속도 (Rate)</span>
              <span id="dash-voice-rate-label" class="text-purple-300 font-semibold">기본 (0%)</span>
            </div>
            <input type="range" id="dash-voice-rate-slider" min="-15" max="15" value="0" step="1" oninput="updateVoiceSettingsDashboard()" class="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500">
            <div class="flex justify-between text-[10px] text-slate-500">
              <span>여유롭게</span>
              <span>리드미컬하게</span>
            </div>
          </div>
        </div>
      </div>
'''

# Locate insertion point in dashboard Tab 4: above the 12-col fitting grid
dash_col_target = '<div class="grid grid-cols-1 lg:grid-cols-12 gap-6">'
if '5대 하이엔드 보이스 페르소나 스튜디오 (대시보드)' not in dash_html:
    pos = dash_html.find(dash_col_target)
    if pos != -1:
        dash_html = dash_html[:pos] + dash_voice_studio_ui + '\n\n    ' + dash_html[pos:]
        print("Inserted dash_voice_studio_ui into dashboard/index.html!")

# JS functions to insert for Dashboard
dash_voice_js = '''
    // 🎙️✨ 대시보드 5대 하이엔드 보이스 스튜디오 연동 (Neural TTS + WebSpeech) ✨🎙️
    let dashCurrentVoicePersona = 'designer';
    let dashCurrentPitchOffset = 0;
    let dashCurrentRateOffset = 0;
    let dashCurrentAudioPlayer = null;

    function selectVoicePersonaDashboard(id) {
      if (!DREAM_VOICE_PERSONAS[id]) return;
      dashCurrentVoicePersona = id;
      const allIds = Object.keys(DREAM_VOICE_PERSONAS);
      allIds.forEach(k => {
        const chip = document.getElementById('dash-voice-chip-' + k);
        if (chip) {
          if (k === id) {
            chip.className = 'p-2.5 rounded-xl bg-purple-600/30 border-2 border-purple-400 text-left transition scale-[1.02] shadow-lg shadow-purple-500/20';
            const t = chip.querySelector('.text-xs');
            if (t) t.className = 'text-xs font-bold text-white';
          } else {
            chip.className = 'p-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-left transition hover:scale-[1.02]';
            const t = chip.querySelector('.text-xs');
            if (t) t.className = 'text-xs font-bold text-slate-200';
          }
        }
      });
      showToast(DREAM_VOICE_PERSONAS[id].avatar + ' ' + DREAM_VOICE_PERSONAS[id].name + ' 성우로 변경되었습니다!', 'info');
    }

    function updateVoiceSettingsDashboard() {
      const pSlider = document.getElementById('dash-voice-pitch-slider');
      const rSlider = document.getElementById('dash-voice-rate-slider');
      if (pSlider) {
        dashCurrentPitchOffset = parseInt(pSlider.value, 10) || 0;
        const pLabel = document.getElementById('dash-voice-pitch-label');
        if (pLabel) pLabel.innerText = (dashCurrentPitchOffset > 0 ? '+' : '') + dashCurrentPitchOffset + 'Hz';
      }
      if (rSlider) {
        dashCurrentRateOffset = parseInt(rSlider.value, 10) || 0;
        const rLabel = document.getElementById('dash-voice-rate-label');
        if (rLabel) rLabel.innerText = (dashCurrentRateOffset > 0 ? '+' : '') + dashCurrentRateOffset + '%';
      }
    }

    function previewCurrentVoiceDashboard() {
      const p = DREAM_VOICE_PERSONAS[dashCurrentVoicePersona] || DREAM_VOICE_PERSONAS.designer;
      speakDreamVoiceDashboard(p.sample, dashCurrentVoicePersona);
    }

    // 대시보드 음성 발성 (Neural TTS -> WebSpeech 폴백)
    async function speakDreamVoiceDashboard(text, forcePersona) {
      const personaKey = forcePersona || dashCurrentVoicePersona || 'designer';
      const persona = DREAM_VOICE_PERSONAS[personaKey] || DREAM_VOICE_PERSONAS.designer;
      
      let finalText = text;
      if (personaKey === 'teen_sister') {
        finalText = '우와! ' + text.replace('입니다.', '이에요! 완전 찰떡이죠?').replace('하십시오.', '해봐요 대박!') + ' 자신감 뿜뿜!';
      } else if (personaKey === 'gentleman') {
        finalText = '기품 있는 선택이십니다. ' + text;
      } else if (personaKey === 'healing_dj') {
        finalText = '오늘도 참 애쓰셨어요. ' + text + ' 언제나 곁에서 응원할게요.';
      } else if (personaKey === 'future_self') {
        finalText = '안녕! 미래의 내가 전하는 말이야. ' + text + ' 넌 정말 멋진 사람이야!';
      } else {
        finalText = '대표님, ' + text;
      }

      if (dashCurrentAudioPlayer) {
        try {
          dashCurrentAudioPlayer.pause();
          dashCurrentAudioPlayer.currentTime = 0;
        } catch(e) {}
        dashCurrentAudioPlayer = null;
      }
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }

      const ind = document.getElementById('dash-voice-indicator-icon');
      if (ind) ind.innerText = '⚡';

      try {
        const resp = await fetch('/api/neural-tts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: finalText,
            persona: personaKey,
            pitch_offset: dashCurrentPitchOffset,
            rate_offset: dashCurrentRateOffset
          })
        });
        if (resp.ok) {
          const res = await resp.json();
          if (res.success && res.audio_url) {
            const audio = new Audio(res.audio_url);
            dashCurrentAudioPlayer = audio;
            audio.onended = () => { if (ind) ind.innerText = '🔊'; };
            audio.onerror = () => { fallbackWebSpeechDashboard(finalText, persona); };
            await audio.play();
            return;
          }
        }
      } catch (e) {
        console.warn('Dashboard neural TTS fetch error:', e);
      }

      fallbackWebSpeechDashboard(finalText, persona);
    }

    function fallbackWebSpeechDashboard(text, persona) {
      const ind = document.getElementById('dash-voice-indicator-icon');
      if (!('speechSynthesis' in window)) {
        if (ind) ind.innerText = '🔊';
        return;
      }
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'ko-KR';

      const voices = window.speechSynthesis.getVoices();
      const bestVoice = voices.find(v => v.lang.includes('ko') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('SunHi') || v.name.includes('Yuna')))
                     || voices.find(v => v.lang.includes('ko'));
      if (bestVoice) utterance.voice = bestVoice;

      const pOffset = dashCurrentPitchOffset / 50.0;
      const rOffset = dashCurrentRateOffset / 50.0;
      utterance.pitch = Math.max(0.5, Math.min(2.0, (persona.webPitch || 1.0) + pOffset));
      utterance.rate = Math.max(0.5, Math.min(2.0, (persona.webRate || 1.0) + rOffset));

      utterance.onend = () => { if (ind) ind.innerText = '🔊'; };
      utterance.onerror = () => { if (ind) ind.innerText = '🔊'; };
      window.speechSynthesis.speak(utterance);
    }
'''

# Replace old speakDreamTextDashboard in dash_html with speakDreamVoiceDashboard
old_dash_speak_pattern = re.compile(r'function speakDreamTextDashboard\(text\)\s*\{.*?window\.speechSynthesis\.speak\(utterance\);\s*\}', re.DOTALL)
if old_dash_speak_pattern.search(dash_html):
    dash_html = old_dash_speak_pattern.sub(dash_voice_js, dash_html, count=1)
    # Also replace any direct calls to speakDreamTextDashboard with speakDreamVoiceDashboard
    dash_html = dash_html.replace('speakDreamTextDashboard(', 'speakDreamVoiceDashboard(')
    print("Replaced speakDreamTextDashboard with dash_voice_js in dashboard/index.html!")

with open(dash_path, 'w', encoding='utf-8') as f:
    f.write(dash_html)

print("dashboard/index.html updated successfully!")
