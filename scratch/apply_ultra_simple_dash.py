import re

# ==============================================================================
# Ultra-Simple Minimal Luxury Dark UI Template for Dream Closet
# ==============================================================================

ultra_simple_html = '''
    <!-- 👗 [한걸음씩 상생나눔 제1호 무료 앱: 꿈의 옷장 (Ultra-Simple Minimal Luxury v3.3)] -->
    <div class="max-w-4xl mx-auto space-y-4 font-sans text-slate-100 pb-16">

      <!-- 👑 [Top Compact Header] (애플/토스 스타일 1줄 미니멀 헤더) -->
      <div class="flex items-center justify-between px-3 py-2.5 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-md">
        <div class="flex items-center gap-2.5">
          <span class="text-2xl p-1.5 rounded-xl bg-purple-600/30 text-purple-300 border border-purple-500/30">👗</span>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-sm sm:text-base font-black text-white tracking-tight">꿈의 옷장 <span class="text-xs font-normal text-slate-400">Dream Closet</span></h3>
              <span onclick="forceBustMobileCache()" class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-400/20 text-amber-300 border border-amber-400/40 cursor-pointer hover:bg-amber-400/30 transition" title="터치 시 캐시 즉시 갱신">
                v3.3 Minimal
              </span>
            </div>
            <p class="text-[10px] text-slate-400 hidden sm:block">창안자: <b>이상일</b> 대표님 · 공동기획: <b>은솔·송효·해상</b> · 0원 상생나눔</p>
          </div>
        </div>

        <div class="flex items-center gap-1.5">
          <button type="button" onclick="unlockMainFreePass()" class="px-2.5 py-1.5 rounded-xl bg-amber-400/20 hover:bg-amber-400/30 text-amber-300 border border-amber-400/40 text-xs font-bold transition flex items-center gap-1 active:scale-95">
            <span>⚡</span><span class="hidden sm:inline">프리패스</span>
          </button>
          <button type="button" onclick="registerDreamClosetCopyright()" class="p-1.5 sm:px-2.5 sm:py-1.5 rounded-xl bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 border border-purple-500/30 text-xs font-medium transition active:scale-95" title="저작권 등기">
            <span>📜</span><span class="hidden sm:inline">등기</span>
          </button>
          <a href="/api/download-dream-closet-app" download="dream_closet_future_master_app.html" class="p-1.5 sm:px-2.5 sm:py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition active:scale-95" title="앱 다운로드">
            <span>📲</span><span class="hidden sm:inline">앱받기</span>
          </a>
        </div>
      </div>


      <!-- 🎧 [Zone 1. 상단 1줄 Voice Bar] (ChatGPT Voice / 인스타 스토리형 원형 아이콘 바) -->
      <div class="p-3 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-md space-y-2">
        <div class="flex items-center justify-between gap-2 overflow-x-auto no-scrollbar py-0.5">
          <!-- 5대 성우 원형 아이콘 (터치 즉시 0.01초 Neural MP3 재생!) -->
          <div class="flex items-center gap-2 sm:gap-3 shrink-0" id="voice-circle-bar">
            <!-- 1. 디자이너 -->
            <button type="button" onclick="selectStudioVoiceMinimal('designer')" id="mini-v-designer" class="flex flex-col items-center gap-1 group transition active:scale-90">
              <div class="w-11 h-11 sm:w-12 sm:h-12 rounded-full p-0.5 bg-gradient-to-tr from-amber-400 to-purple-600 shadow-md shadow-purple-900/40 transition ring-2 ring-amber-400">
                <div class="w-full h-full rounded-full bg-slate-900 flex items-center justify-center text-lg sm:text-xl">👩🎨</div>
              </div>
              <span class="text-[10px] font-bold text-amber-300">디자이너</span>
            </button>

            <!-- 2. 하이틴 -->
            <button type="button" onclick="selectStudioVoiceMinimal('highteen')" id="mini-v-highteen" class="flex flex-col items-center gap-1 group transition active:scale-90 opacity-70 hover:opacity-100">
              <div class="w-11 h-11 sm:w-12 sm:h-12 rounded-full p-0.5 bg-slate-800 transition">
                <div class="w-full h-full rounded-full bg-slate-900 flex items-center justify-center text-lg sm:text-xl">💖</div>
              </div>
              <span class="text-[10px] text-slate-400">하이틴</span>
            </button>

            <!-- 3. 젠틀맨 -->
            <button type="button" onclick="selectStudioVoiceMinimal('gentleman')" id="mini-v-gentleman" class="flex flex-col items-center gap-1 group transition active:scale-90 opacity-70 hover:opacity-100">
              <div class="w-11 h-11 sm:w-12 sm:h-12 rounded-full p-0.5 bg-slate-800 transition">
                <div class="w-full h-full rounded-full bg-slate-900 flex items-center justify-center text-lg sm:text-xl">🤵</div>
              </div>
              <span class="text-[10px] text-slate-400">젠틀맨</span>
            </button>

            <!-- 4. 힐링DJ -->
            <button type="button" onclick="selectStudioVoiceMinimal('dj')" id="mini-v-dj" class="flex flex-col items-center gap-1 group transition active:scale-90 opacity-70 hover:opacity-100">
              <div class="w-11 h-11 sm:w-12 sm:h-12 rounded-full p-0.5 bg-slate-800 transition">
                <div class="w-full h-full rounded-full bg-slate-900 flex items-center justify-center text-lg sm:text-xl">🌙</div>
              </div>
              <span class="text-[10px] text-slate-400">힐링DJ</span>
            </button>

            <!-- 5. 2035나 -->
            <button type="button" onclick="selectStudioVoiceMinimal('future')" id="mini-v-future" class="flex flex-col items-center gap-1 group transition active:scale-90 opacity-70 hover:opacity-100">
              <div class="w-11 h-11 sm:w-12 sm:h-12 rounded-full p-0.5 bg-slate-800 transition">
                <div class="w-full h-full rounded-full bg-slate-900 flex items-center justify-center text-lg sm:text-xl">🚀</div>
              </div>
              <span class="text-[10px] text-slate-400">2035나</span>
            </button>
          </div>

          <!-- 음성 액션 버튼 (미리듣기 / 마이크 / 튜닝) -->
          <div class="flex items-center gap-1.5 shrink-0 pl-2 border-l border-slate-800">
            <button type="button" onclick="playSelectedStudioVoice('')" id="btn-quick-play-voice" class="w-9 h-9 rounded-xl bg-purple-600/30 hover:bg-purple-600/50 text-purple-200 border border-purple-500/40 flex items-center justify-center text-base transition active:scale-95" title="성우 목소리 듣기">
              <span id="voice-play-icon">🔊</span>
            </button>
            <button type="button" onclick="toggleMainVoiceSTT()" id="main-btn-mic-stt" class="w-9 h-9 rounded-xl bg-pink-600/30 hover:bg-pink-600/50 text-pink-200 border border-pink-500/40 flex items-center justify-center text-base transition active:scale-95" title="마이크로 말하기">
              🎙️
            </button>
            <button type="button" onclick="toggleVoiceTuningBar()" class="w-9 h-9 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 flex items-center justify-center text-xs transition active:scale-95" title="톤/속도 조절">
              🎛️
            </button>
          </div>
        </div>

        <!-- 미니 튜닝 바 (기본 숨김, 🎛️ 누를 때만 펼쳐짐) -->
        <div id="voice-tuning-bar" class="hidden pt-2 border-t border-slate-800/80 grid grid-cols-2 gap-3 text-xs">
          <div>
            <div class="flex justify-between text-[11px] text-slate-400 mb-1">
              <span>톤(Pitch)</span><span id="voice-pitch-label" class="text-amber-300">0Hz</span>
            </div>
            <input type="range" id="voice-pitch-slider" min="-15" max="15" value="0" step="1" oninput="updateStudioVoiceSettings('')" class="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-400">
          </div>
          <div>
            <div class="flex justify-between text-[11px] text-slate-400 mb-1">
              <span>속도(Speed)</span><span id="voice-rate-label" class="text-amber-300">1.0x</span>
            </div>
            <input type="range" id="voice-rate-slider" min="0.8" max="1.3" value="1.0" step="0.05" oninput="updateStudioVoiceSettings('')" class="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-400">
          </div>
        </div>
      </div>


      <!-- 👗 [Zone 2. 중앙 메인 Canvas] (지그재그·제페토 스타일 시원한 풀뷰 피팅 캔버스) -->
      <div class="p-3.5 sm:p-5 rounded-3xl bg-slate-900/50 border border-slate-800/80 shadow-2xl relative space-y-3">

        <!-- 캔버스 상단 세그먼트 (각도 & 모드) -->
        <div class="flex items-center justify-between flex-wrap gap-2 text-xs">
          <!-- 4방향 각도 -->
          <div class="flex items-center gap-1 p-1 rounded-xl bg-slate-950/80 border border-slate-800">
            <button type="button" onclick="setMainAngle(0)" id="main-angle-btn-0" class="px-2.5 py-1 rounded-lg bg-purple-600 text-white font-bold text-[11px] transition">정면</button>
            <button type="button" onclick="setMainAngle(90)" id="main-angle-btn-90" class="px-2.5 py-1 rounded-lg text-slate-400 hover:text-white text-[11px] transition">좌측</button>
            <button type="button" onclick="setMainAngle(180)" id="main-angle-btn-180" class="px-2.5 py-1 rounded-lg text-slate-400 hover:text-white text-[11px] transition">후면</button>
            <button type="button" onclick="setMainAngle(270)" id="main-angle-btn-270" class="px-2.5 py-1 rounded-lg text-slate-400 hover:text-white text-[11px] transition">우측</button>
          </div>

          <!-- 모드 전환 (피팅 / 2035미래 / 가족룩) -->
          <div class="flex items-center gap-1 p-1 rounded-xl bg-slate-950/80 border border-slate-800">
            <button type="button" onclick="switchMainFittingSubTab('fitting')" id="tab-sub-fitting" class="px-2.5 py-1 rounded-lg bg-purple-600 text-white font-bold text-[11px] transition">피팅</button>
            <button type="button" onclick="switchMainFittingSubTab('future')" id="tab-sub-future" class="px-2.5 py-1 rounded-lg text-slate-400 hover:text-white text-[11px] transition">🔮 2035</button>
            <button type="button" onclick="switchMainFittingSubTab('family')" id="tab-sub-family" class="px-2.5 py-1 rounded-lg text-slate-400 hover:text-white text-[11px] transition">👨‍👧‍👧 가족룩</button>
          </div>

          <!-- 내 얼굴 합성 인풋 -->
          <label class="px-2.5 py-1 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-[11px] cursor-pointer transition flex items-center gap-1 active:scale-95">
            <span>📸</span><span>내 얼굴</span>
            <input type="file" id="main-face-upload" accept="image/*" class="hidden">
          </label>
        </div>

        <!-- 👑 풀뷰 캔버스 뷰포트 -->
        <div class="w-full max-w-[420px] mx-auto aspect-[3/4] max-h-[460px] rounded-2xl bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 border border-slate-800 shadow-inner relative overflow-hidden flex items-center justify-center">
          <canvas id="main-fitting-canvas" width="450" height="600" class="w-full h-full object-contain"></canvas>

          <!-- 캔버스 오버레이 자막 바 -->
          <div class="absolute bottom-2.5 left-2.5 right-2.5 px-3 py-1.5 rounded-xl bg-slate-950/85 backdrop-blur-md border border-slate-800/80 flex items-center justify-between text-[11px] text-slate-300 shadow-md">
            <span id="main-look-label" class="font-medium truncate">👔 화이트 베이직 & 슬림 데님</span>
            <span id="main-angle-label" class="font-mono text-purple-400 shrink-0 ml-2">0° FRONT</span>
          </div>
        </div>

        <!-- 캔버스 하단: 가로 스크롤 원터치 룩 캡슐 바 -->
        <div class="space-y-1.5 pt-1">
          <div class="flex items-center justify-between text-[11px] text-slate-400 px-1">
            <span>원터치 스타일 코디</span>
            <span class="text-purple-300 text-[10px]">가로로 밀어서 선택 ➔</span>
          </div>
          <div class="flex items-center gap-2 overflow-x-auto no-scrollbar py-1 text-xs">
            <button type="button" onclick="applyQuickLook('basic')" class="px-3.5 py-1.5 rounded-full bg-purple-600/30 hover:bg-purple-600/50 text-white border border-purple-400/50 font-bold shrink-0 transition active:scale-95">
              #기본캐주얼
            </button>
            <button type="button" onclick="applyQuickLook('highteen')" class="px-3.5 py-1.5 rounded-full bg-pink-600/20 hover:bg-pink-600/40 text-pink-200 border border-pink-500/30 font-bold shrink-0 transition active:scale-95">
              #하이틴룩
            </button>
            <button type="button" onclick="applyQuickLook('suit')" class="px-3.5 py-1.5 rounded-full bg-amber-600/20 hover:bg-amber-600/40 text-amber-200 border border-amber-500/30 font-bold shrink-0 transition active:scale-95">
              #청담VIP수트
            </button>
            <button type="button" onclick="applyQuickLook('future_ceo')" class="px-3.5 py-1.5 rounded-full bg-purple-600/20 hover:bg-purple-600/40 text-purple-200 border border-purple-500/30 font-bold shrink-0 transition active:scale-95">
              #2035글로벌CEO
            </button>
            <button type="button" onclick="applyQuickLook('family')" class="px-3.5 py-1.5 rounded-full bg-emerald-600/20 hover:bg-emerald-600/40 text-emerald-200 border border-emerald-500/30 font-bold shrink-0 transition active:scale-95">
              #가족시밀러룩
            </button>
            <button type="button" onclick="applyQuickLook('reform_0')" class="px-3.5 py-1.5 rounded-full bg-cyan-600/20 hover:bg-cyan-600/40 text-cyan-200 border border-cyan-500/30 font-bold shrink-0 transition active:scale-95">
              #0원옷장리폼
            </button>
          </div>
        </div>
      </div>


      <!-- 🎮 [Zone 3. 하단 액션 Bar] (듀오링고 스타일 인성 해금 진행 바 & 팝업 퀴즈) -->
      <div class="p-3.5 rounded-2xl bg-gradient-to-r from-purple-950/40 via-slate-900/80 to-slate-950 border border-purple-500/30 space-y-2.5">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div class="flex items-center gap-2">
            <span class="text-xl">🌱</span>
            <div>
              <div class="text-xs font-bold text-white flex items-center gap-1.5">
                <span>인성 해금 상태:</span>
                <span id="main-step-title" class="text-amber-300 font-extrabold">Step 3. 나눔과 공존 마스터</span>
              </div>
              <p class="text-[10px] text-slate-400">드라마틱 상황극 퀴즈를 풀고 특별 코디와 목소리를 해금하세요!</p>
            </div>
          </div>
          <button type="button" onclick="toggleQuizPopup()" id="btn-toggle-quiz" class="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-bold text-xs shadow-md shadow-purple-900/40 transition active:scale-95 flex items-center gap-1">
            <span>🎓</span><span>인성 퀴즈 풀기</span>
          </button>
        </div>

        <!-- 듀오링고 스타일 팝업 퀴즈 카드 (기본 숨김) -->
        <div id="quiz-popup-card" class="hidden p-4 rounded-xl bg-slate-950/95 border border-purple-500/40 space-y-3 transition-all animate-fadeIn">
          <div class="flex items-center justify-between pb-2 border-b border-slate-800">
            <!-- 4단계 스텝 탭 -->
            <div class="flex items-center gap-1">
              <button type="button" onclick="selectMainStep(0)" id="main-step-tab-0" class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400">Lv.0</button>
              <button type="button" onclick="selectMainStep(1)" id="main-step-tab-1" class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400">Step 1</button>
              <button type="button" onclick="selectMainStep(2)" id="main-step-tab-2" class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400">Step 2</button>
              <button type="button" onclick="selectMainStep(3)" id="main-step-tab-3" class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-600 text-white">Step 3</button>
            </div>
            <button type="button" onclick="toggleQuizPopup()" class="text-slate-400 hover:text-white text-base">✕</button>
          </div>

          <!-- 상황극 질문 & 선택지 -->
          <div id="main-quiz-container" class="space-y-2.5">
            <!-- Dynamic quiz content -->
          </div>

          <!-- 긍정 확언 원터치 버튼 -->
          <div class="pt-2 border-t border-slate-800 flex items-center justify-between text-xs">
            <span class="text-[11px] text-slate-400">스피치 미션: 긍정 확언 선서</span>
            <button type="button" onclick="triggerMainAffirmationSuccess()" class="px-3 py-1 rounded-lg bg-pink-600 hover:bg-pink-500 text-white font-bold text-xs transition active:scale-95">
              ✨ 긍정 확언 완료
            </button>
          </div>
        </div>
      </div>


      <!-- 🗂️ [토스(Toss) 스타일 하단 4대 접이식 서랍 (Drawer)] -->
      <div class="space-y-2 pt-2">
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
          <!-- 서랍 1: 체형/컬러 -->
          <button type="button" onclick="toggleDrawer('body')" id="btn-drawer-body" class="p-2.5 rounded-xl bg-slate-900/70 hover:bg-slate-800 border border-slate-800 text-left transition flex items-center gap-2">
            <span class="text-lg">📏</span>
            <div>
              <div class="text-xs font-bold text-slate-200">체형·컬러</div>
              <div class="text-[10px] text-slate-400">비율/퍼스널컬러</div>
            </div>
          </button>

          <!-- 서랍 2: VOC 건의함 -->
          <button type="button" onclick="toggleDrawer('voc')" id="btn-drawer-voc" class="p-2.5 rounded-xl bg-slate-900/70 hover:bg-slate-800 border border-slate-800 text-left transition flex items-center gap-2">
            <span class="text-lg">💬</span>
            <div>
              <div class="text-xs font-bold text-slate-200">전담팀 VOC</div>
              <div class="text-[10px] text-slate-400">4대AI 자동패치</div>
            </div>
          </button>

          <!-- 서랍 3: 앱 배포/설치 -->
          <button type="button" onclick="toggleDrawer('deploy')" id="btn-drawer-deploy" class="p-2.5 rounded-xl bg-slate-900/70 hover:bg-slate-800 border border-slate-800 text-left transition flex items-center gap-2">
            <span class="text-lg">📲</span>
            <div>
              <div class="text-xs font-bold text-slate-200">앱 설치·배포</div>
              <div class="text-[10px] text-slate-400">PWA/무심사배포</div>
            </div>
          </button>

          <!-- 서랍 4: 4Q 인성/인증서 -->
          <button type="button" onclick="toggleDrawer('cert')" id="btn-drawer-cert" class="p-2.5 rounded-xl bg-slate-900/70 hover:bg-slate-800 border border-slate-800 text-left transition flex items-center gap-2">
            <span class="text-lg">🎓</span>
            <div>
              <div class="text-xs font-bold text-slate-200">4Q·인증서</div>
              <div class="text-[10px] text-slate-400">수료증/인재차트</div>
            </div>
          </button>
        </div>

        <!-- 서랍 1 내용: 체형/퍼스널 컬러 -->
        <div id="drawer-body" class="hidden p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
          <div class="flex items-center justify-between border-b border-slate-800 pb-2">
            <h5 class="text-xs font-bold text-white flex items-center gap-1.5"><span>📏</span> 체형 비율 및 퍼스널 컬러 스캐너</h5>
            <button type="button" onclick="toggleDrawer('body')" class="text-slate-400 hover:text-white text-xs">닫기 ✕</button>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div class="space-y-2">
              <div>
                <div class="flex justify-between text-[11px] text-slate-400 mb-1">
                  <span>키 (Height)</span><span id="main-height-val" class="text-purple-300 font-bold">168cm</span>
                </div>
                <input type="range" id="main-slider-height" min="140" max="195" value="168" oninput="updateMainAvatarProportions()" class="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500">
              </div>
              <div>
                <div class="flex justify-between text-[11px] text-slate-400 mb-1">
                  <span>몸무게 (Weight)</span><span id="main-weight-val" class="text-purple-300 font-bold">62kg</span>
                </div>
                <input type="range" id="main-slider-weight" min="40" max="110" value="62" oninput="updateMainAvatarProportions()" class="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500">
              </div>
            </div>
            <div class="space-y-2">
              <span class="text-[11px] text-slate-400 block">피부톤 RGB 스캐너</span>
              <div class="flex items-center gap-2">
                <button type="button" onclick="updateMainSkinTone('#fbe3d5')" class="w-8 h-8 rounded-full border border-white/20 bg-[#fbe3d5] shadow-sm hover:scale-110 transition" title="화사한 웜톤"></button>
                <button type="button" onclick="updateMainSkinTone('#f4cfb8')" class="w-8 h-8 rounded-full border border-white/20 bg-[#f4cfb8] shadow-sm hover:scale-110 transition" title="내추럴 뉴트럴"></button>
                <button type="button" onclick="updateMainSkinTone('#e0ac82')" class="w-8 h-8 rounded-full border border-white/20 bg-[#e0ac82] shadow-sm hover:scale-110 transition" title="건강한 태닝톤"></button>
                <button type="button" onclick="updateMainSkinTone('#8d5524')" class="w-8 h-8 rounded-full border border-white/20 bg-[#8d5524] shadow-sm hover:scale-110 transition" title="딥 브라운"></button>
              </div>
            </div>
          </div>
        </div>

        <!-- 서랍 2 내용: 전담팀 VOC 건의함 -->
        <div id="drawer-voc" class="hidden p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
          <div class="flex items-center justify-between border-b border-slate-800 pb-2">
            <h5 class="text-xs font-bold text-white flex items-center gap-1.5"><span>💬</span> 초격차 관리팀 직통 VOC 건의함 (자율 패치)</h5>
            <button type="button" onclick="toggleDrawer('voc')" class="text-slate-400 hover:text-white text-xs">닫기 ✕</button>
          </div>
          <div class="space-y-2">
            <div class="flex gap-2">
              <input type="text" id="main-app-voc-input" placeholder="불편한 점이나 원하는 코디, 퀴즈 아이디어를 적어주세요!" class="flex-1 px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-xs text-white placeholder-slate-500">
              <button type="button" onclick="submitMainAppVoc()" class="px-3.5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shrink-0 transition">
                제출
              </button>
            </div>
            <div id="main-voc-response-box" class="hidden p-3 rounded-xl bg-purple-950/30 border border-purple-500/30 text-xs text-purple-200">
              <!-- AI 브리핑 출력 -->
            </div>
          </div>
        </div>

        <!-- 서랍 3 내용: 앱 설치 및 배포 -->
        <div id="drawer-deploy" class="hidden p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
          <div class="flex items-center justify-between border-b border-slate-800 pb-2">
            <h5 class="text-xs font-bold text-white flex items-center gap-1.5"><span>📲</span> 무심사 직통 배포 센터 & Google Play 계정 복구</h5>
            <button type="button" onclick="toggleDrawer('deploy')" class="text-slate-400 hover:text-white text-xs">닫기 ✕</button>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5 text-xs">
            <a href="/api/download-dream-closet-app" download="dream_closet_future_master_app.html" class="p-3 rounded-xl bg-slate-950 hover:bg-slate-800 border border-slate-700 flex flex-col items-center justify-center text-center gap-1 transition">
              <span class="text-xl">📁</span>
              <span class="font-bold text-white">단독 웹앱(.html) 다운로드</span>
              <span class="text-[10px] text-slate-400">카톡 전송 시 1초 만에 실행</span>
            </a>
            <div class="p-3 rounded-xl bg-slate-950 border border-slate-700 flex flex-col items-center justify-center text-center gap-1">
              <span class="text-xl">📱</span>
              <span class="font-bold text-white">홈 화면에 추가 (PWA)</span>
              <span class="text-[10px] text-slate-400">브라우저 메뉴 ➔ 홈화면 추가</span>
            </div>
            <button type="button" onclick="openGooglePlayGuideModal()" class="p-3 rounded-xl bg-slate-950 hover:bg-slate-800 border border-slate-700 flex flex-col items-center justify-center text-center gap-1 transition">
              <span class="text-xl">🛡️</span>
              <span class="font-bold text-white">Google Play 복구 매뉴얼</span>
              <span class="text-[10px] text-slate-400">ID: 8519115145103880120</span>
            </button>
          </div>
        </div>

        <!-- 서랍 4 내용: 4Q 인성학교 & 수료 인증서 -->
        <div id="drawer-cert" class="hidden p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
          <div class="flex items-center justify-between border-b border-slate-800 pb-2">
            <h5 class="text-xs font-bold text-white flex items-center gap-1.5"><span>🎓</span> 글로벌 4Q 인재 균형 레이더 & 수료증 발급소</h5>
            <button type="button" onclick="toggleDrawer('cert')" class="text-slate-400 hover:text-white text-xs">닫기 ✕</button>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div class="flex flex-col items-center justify-center p-3 rounded-xl bg-slate-950 border border-slate-800">
              <span class="text-[11px] text-purple-300 font-bold mb-2">글로벌 4Q 균형 인재 레이더</span>
              <canvas id="compass-radar-canvas" width="220" height="220" class="w-[200px] h-[200px]"></canvas>
            </div>
            <div class="flex flex-col items-center justify-center p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <span class="text-[11px] text-amber-300 font-bold">한걸음씩 품격 마스터 정식 수료증</span>
              <canvas id="cert-canvas" width="280" height="190" class="w-full max-w-[260px] rounded-lg border border-slate-700 shadow-md"></canvas>
            </div>
          </div>
        </div>
      </div>

    </div>
    <!-- 👗 [꿈의 옷장 Ultra-Simple Minimal End] -->
'''

# Supporting Minimal UI JS helper functions to append
js_helpers = '''
    // ── 💎 Ultra-Simple Minimal Luxury UI 헬퍼 스크립트 ──
    function selectStudioVoiceMinimal(id) {
      selectStudioVoice('', id);
      const voiceIds = ['designer', 'highteen', 'gentleman', 'dj', 'future'];
      voiceIds.forEach(k => {
        const btn = document.getElementById('mini-v-' + k);
        if (btn) {
          const ring = btn.querySelector('div');
          const txt = btn.querySelector('span');
          if (k === id) {
            btn.className = 'flex flex-col items-center gap-1 group transition scale-105';
            if (ring) ring.className = 'w-11 h-11 sm:w-12 sm:h-12 rounded-full p-0.5 bg-gradient-to-tr from-amber-400 to-purple-600 shadow-md shadow-purple-900/40 transition ring-2 ring-amber-400';
            if (txt) { txt.className = 'text-[10px] font-bold text-amber-300'; }
          } else {
            btn.className = 'flex flex-col items-center gap-1 group transition opacity-70 hover:opacity-100';
            if (ring) ring.className = 'w-11 h-11 sm:w-12 sm:h-12 rounded-full p-0.5 bg-slate-800 transition';
            if (txt) { txt.className = 'text-[10px] text-slate-400'; }
          }
        }
      });
      // 0.01초 즉시 음성 재생!
      playSelectedStudioVoice('');
    }

    function toggleVoiceTuningBar() {
      const b = document.getElementById('voice-tuning-bar');
      if (b) b.classList.toggle('hidden');
    }

    function toggleQuizPopup() {
      const p = document.getElementById('quiz-popup-card');
      if (p) {
        p.classList.toggle('hidden');
        if (!p.classList.contains('hidden')) {
          renderMainQuizStep(currentQuizStep || 3);
        }
      }
    }

    function toggleDrawer(id) {
      const drawers = ['body', 'voc', 'deploy', 'cert'];
      drawers.forEach(d => {
        const el = document.getElementById('drawer-' + d);
        const btn = document.getElementById('btn-drawer-' + d);
        if (d === id) {
          if (el) {
            const isHidden = el.classList.contains('hidden');
            el.classList.toggle('hidden');
            if (btn) {
              if (isHidden) {
                btn.className = 'p-2.5 rounded-xl bg-purple-600/30 border border-purple-400 text-left transition flex items-center gap-2 ring-1 ring-purple-400';
              } else {
                btn.className = 'p-2.5 rounded-xl bg-slate-900/70 hover:bg-slate-800 border border-slate-800 text-left transition flex items-center gap-2';
              }
            }
          }
        } else {
          if (el) el.classList.add('hidden');
          if (btn) btn.className = 'p-2.5 rounded-xl bg-slate-900/70 hover:bg-slate-800 border border-slate-800 text-left transition flex items-center gap-2';
        }
      });
    }

    // 원터치 룩 캡슐 적용
    function applyQuickLook(lookKey) {
      if (lookKey === 'basic') {
        currentLookId = 'basic';
        document.getElementById('main-look-label').innerText = '👔 화이트 베이직 & 슬림 데님';
        drawMainFittingAvatar();
        speakSmartNeuralDirect('기본이 가장 빛나는 법이죠. 소매 살짝 롤업하고 단정하게 걸어보세요!');
      } else if (lookKey === 'highteen') {
        currentLookId = 'highteen';
        document.getElementById('main-look-label').innerText = '🌸 K-하이틴 & 시티보이 룩';
        drawMainFittingAvatar();
        speakSmartNeuralDirect('와! 하이틴 무드 완전 찰떡이에요! 친구들이 어디서 샀냐고 물어보겠는데요?');
      } else if (lookKey === 'suit') {
        currentLookId = 'suit';
        document.getElementById('main-look-label').innerText = '👔 청담 VIP 수트 & 롱코트';
        drawMainFittingAvatar();
        speakSmartNeuralDirect('대표님, 어깨선부터 V존 비율까지 걸어 다니는 화보 그 자체입니다.');
      } else if (lookKey === 'future_ceo') {
        switchMainFittingSubTab('future');
        applyMainFutureLook('ceo');
      } else if (lookKey === 'family') {
        switchMainFittingSubTab('family');
      } else if (lookKey === 'reform_0') {
        currentLookId = 'reform';
        document.getElementById('main-look-label').innerText = '♻️ 0원 리폼: 3:7 턱인 & 프렌치 롤업 핏';
        drawMainFittingAvatar();
        speakSmartNeuralDirect('돈 한 푼 안 들이고 기본 티셔츠 3:7 비율과 소매 롤업만으로 명품 핏 완성!');
      }
    }

    function speakSmartNeuralDirect(text) {
      if (typeof playSmartNeuralVoice === 'function') {
        playSmartNeuralVoice(text, globalSelectedVoicePersona);
      } else {
        playSelectedStudioVoice('');
      }
    }
'''

# ==============================================================================
# Apply to dashboard/index.html
# ==============================================================================
dash_path = 'dashboard/index.html'
with open(dash_path, 'r', encoding='utf-8') as f:
    dash_html = f.read()

# Replace content inside <div id="tab-daughters" ...> with ultra_simple_html
start_marker = '<div id="tab-daughters"'
end_marker = '<!-- Settings Modal (Quick Edit) -->'

start_pos = dash_html.find(start_marker)
end_pos = dash_html.find(end_marker, start_pos)

if start_pos != -1 and end_pos != -1:
    # preserve opening tag of tab-daughters
    pane_start = dash_html.find('>', start_pos) + 1
    # find where tab-daughters closes before end_marker
    pane_end = dash_html.rfind('</div>', start_pos, end_pos)
    
    dash_html = dash_html[:pane_start] + '\n' + ultra_simple_html + '\n  ' + dash_html[pane_end:]
    print("Replaced tab-daughters in dashboard/index.html with Ultra-Simple 3-Zone UI!")
else:
    print("Could not find tab-daughters range in index.html!")

# Inject js_helpers into index.html
if 'selectStudioVoiceMinimal' not in dash_html:
    script_end = dash_html.rfind('</script>')
    if script_end != -1:
        dash_html = dash_html[:script_end] + js_helpers + '\n  ' + dash_html[script_end:]
        print("Injected js_helpers into dashboard/index.html!")

with open(dash_path, 'w', encoding='utf-8') as f:
    f.write(dash_html)

print("dashboard/index.html successfully updated!")
