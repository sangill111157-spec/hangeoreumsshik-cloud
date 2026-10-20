with open('dashboard/dream_closet_future_master_app.html', 'r', encoding='utf-8') as f:
    app_html = f.read()

# Standalone Ultra-Simple Body Template
standalone_ultra_simple_body = '''
<body class="bg-slate-950 text-slate-100 min-h-screen p-3 sm:p-6 antialiased selection:bg-purple-500 selection:text-white">

  <!-- 👑 [Ultra-Simple Minimal Luxury v3.3 Container] -->
  <div class="max-w-4xl mx-auto space-y-4 pb-16">

    <!-- 👑 Top Minimal Header -->
    <div class="flex items-center justify-between px-3.5 py-2.5 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-md">
      <div class="flex items-center gap-2.5">
        <span class="text-2xl p-1.5 rounded-xl bg-purple-600/30 text-purple-300 border border-purple-500/30">👗</span>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-sm sm:text-base font-black text-white tracking-tight">꿈의 옷장 <span class="text-xs font-normal text-slate-400">Dream Closet</span></h1>
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-400/20 text-amber-300 border border-amber-400/40">
              v3.3 Minimal
            </span>
          </div>
          <p class="text-[10px] text-slate-400 hidden sm:block">창안자: <b>이상일</b> 대표님 · 0원 무료 상생나눔</p>
        </div>
      </div>

      <div class="flex items-center gap-1.5">
        <button type="button" onclick="unlockFreePass()" class="px-2.5 py-1.5 rounded-xl bg-amber-400/20 hover:bg-amber-400/30 text-amber-300 border border-amber-400/40 text-xs font-bold transition flex items-center gap-1 active:scale-95">
          <span>⚡</span><span class="hidden sm:inline">프리패스</span>
        </button>
        <button type="button" onclick="registerCopyright()" class="p-1.5 sm:px-2.5 sm:py-1.5 rounded-xl bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 border border-purple-500/30 text-xs font-medium transition active:scale-95" title="저작권 등기">
          <span>📜</span><span class="hidden sm:inline">등기</span>
        </button>
      </div>
    </div>


    <!-- 🎧 [Zone 1. 상단 1줄 Voice Bar] (ChatGPT Voice / 인스타 스토리형 원형 아이콘 바) -->
    <div class="p-3 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-md space-y-2">
      <div class="flex items-center justify-between gap-2 overflow-x-auto no-scrollbar py-0.5">
        <!-- 5대 성우 원형 아이콘 (터치 즉시 0.01초 Neural MP3 재생!) -->
        <div class="flex items-center gap-2 sm:gap-3 shrink-0" id="voice-circle-bar">
          <button type="button" onclick="selectStudioVoiceMinimalApp('designer')" id="mini-v-designer" class="flex flex-col items-center gap-1 group transition active:scale-90">
            <div class="w-11 h-11 sm:w-12 sm:h-12 rounded-full p-0.5 bg-gradient-to-tr from-amber-400 to-purple-600 shadow-md shadow-purple-900/40 ring-2 ring-amber-400">
              <div class="w-full h-full rounded-full bg-slate-900 flex items-center justify-center text-lg sm:text-xl">👩🎨</div>
            </div>
            <span class="text-[10px] font-bold text-amber-300">디자이너</span>
          </button>

          <button type="button" onclick="selectStudioVoiceMinimalApp('highteen')" id="mini-v-highteen" class="flex flex-col items-center gap-1 group transition active:scale-90 opacity-70 hover:opacity-100">
            <div class="w-11 h-11 sm:w-12 sm:h-12 rounded-full p-0.5 bg-slate-800">
              <div class="w-full h-full rounded-full bg-slate-900 flex items-center justify-center text-lg sm:text-xl">💖</div>
            </div>
            <span class="text-[10px] text-slate-400">하이틴</span>
          </button>

          <button type="button" onclick="selectStudioVoiceMinimalApp('gentleman')" id="mini-v-gentleman" class="flex flex-col items-center gap-1 group transition active:scale-90 opacity-70 hover:opacity-100">
            <div class="w-11 h-11 sm:w-12 sm:h-12 rounded-full p-0.5 bg-slate-800">
              <div class="w-full h-full rounded-full bg-slate-900 flex items-center justify-center text-lg sm:text-xl">🤵</div>
            </div>
            <span class="text-[10px] text-slate-400">젠틀맨</span>
          </button>

          <button type="button" onclick="selectStudioVoiceMinimalApp('dj')" id="mini-v-dj" class="flex flex-col items-center gap-1 group transition active:scale-90 opacity-70 hover:opacity-100">
            <div class="w-11 h-11 sm:w-12 sm:h-12 rounded-full p-0.5 bg-slate-800">
              <div class="w-full h-full rounded-full bg-slate-900 flex items-center justify-center text-lg sm:text-xl">🌙</div>
            </div>
            <span class="text-[10px] text-slate-400">힐링DJ</span>
          </button>

          <button type="button" onclick="selectStudioVoiceMinimalApp('future')" id="mini-v-future" class="flex flex-col items-center gap-1 group transition active:scale-90 opacity-70 hover:opacity-100">
            <div class="w-11 h-11 sm:w-12 sm:h-12 rounded-full p-0.5 bg-slate-800">
              <div class="w-full h-full rounded-full bg-slate-900 flex items-center justify-center text-lg sm:text-xl">🚀</div>
            </div>
            <span class="text-[10px] text-slate-400">2035나</span>
          </button>
        </div>

        <!-- 음성 액션 버튼 -->
        <div class="flex items-center gap-1.5 shrink-0 pl-2 border-l border-slate-800">
          <button type="button" onclick="playSelectedStudioVoice('')" class="w-9 h-9 rounded-xl bg-purple-600/30 hover:bg-purple-600/50 text-purple-200 border border-purple-500/40 flex items-center justify-center text-base transition active:scale-95" title="성우 목소리 듣기">
            <span id="voice-play-icon">🔊</span>
          </button>
          <button type="button" onclick="toggleVoiceSTT()" id="btn-mic-stt" class="w-9 h-9 rounded-xl bg-pink-600/30 hover:bg-pink-600/50 text-pink-200 border border-pink-500/40 flex items-center justify-center text-base transition active:scale-95" title="마이크로 말하기">
            🎙️
          </button>
          <button type="button" onclick="toggleVoiceTuningBarApp()" class="w-9 h-9 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 flex items-center justify-center text-xs transition active:scale-95" title="톤/속도 조절">
            🎛️
          </button>
        </div>
      </div>

      <!-- 미니 튜닝 바 (🎛️ 누를 때만 토글) -->
      <div id="voice-tuning-bar-app" class="hidden pt-2 border-t border-slate-800/80 grid grid-cols-2 gap-3 text-xs">
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
      <div class="flex items-center justify-between flex-wrap gap-2 text-xs">
        <div class="flex items-center gap-1 p-1 rounded-xl bg-slate-950/80 border border-slate-800">
          <button type="button" onclick="setAngle(0)" id="angle-btn-0" class="px-2.5 py-1 rounded-lg bg-purple-600 text-white font-bold text-[11px] transition">정면</button>
          <button type="button" onclick="setAngle(90)" id="angle-btn-90" class="px-2.5 py-1 rounded-lg text-slate-400 hover:text-white text-[11px] transition">좌측</button>
          <button type="button" onclick="setAngle(180)" id="angle-btn-180" class="px-2.5 py-1 rounded-lg text-slate-400 hover:text-white text-[11px] transition">후면</button>
          <button type="button" onclick="setAngle(270)" id="angle-btn-270" class="px-2.5 py-1 rounded-lg text-slate-400 hover:text-white text-[11px] transition">우측</button>
        </div>

        <div class="flex items-center gap-1 p-1 rounded-xl bg-slate-950/80 border border-slate-800">
          <button type="button" onclick="switchFittingSubTab('fitting')" id="tab-sub-fitting" class="px-2.5 py-1 rounded-lg bg-purple-600 text-white font-bold text-[11px] transition">피팅</button>
          <button type="button" onclick="switchFittingSubTab('future')" id="tab-sub-future" class="px-2.5 py-1 rounded-lg text-slate-400 hover:text-white text-[11px] transition">🔮 2035</button>
          <button type="button" onclick="switchFittingSubTab('family')" id="tab-sub-family" class="px-2.5 py-1 rounded-lg text-slate-400 hover:text-white text-[11px] transition">👨‍👧‍👧 가족룩</button>
        </div>

        <label class="px-2.5 py-1 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-[11px] cursor-pointer transition flex items-center gap-1 active:scale-95">
          <span>📸</span><span>내 얼굴</span>
          <input type="file" id="face-upload" accept="image/*" class="hidden">
        </label>
      </div>

      <!-- 풀뷰 캔버스 -->
      <div class="w-full max-w-[420px] mx-auto aspect-[3/4] max-h-[460px] rounded-2xl bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 border border-slate-800 shadow-inner relative overflow-hidden flex items-center justify-center">
        <canvas id="app-fitting-canvas" width="450" height="600" class="w-full h-full object-contain"></canvas>
        <div class="absolute bottom-2.5 left-2.5 right-2.5 px-3 py-1.5 rounded-xl bg-slate-950/85 backdrop-blur-md border border-slate-800/80 flex items-center justify-between text-[11px] text-slate-300 shadow-md">
          <span id="canvas-look-label" class="font-medium truncate">👔 화이트 베이직 & 슬림 데님</span>
          <span id="canvas-angle-label" class="font-mono text-purple-400 shrink-0 ml-2">0° FRONT</span>
        </div>
      </div>

      <!-- 원터치 스타일 캡슐 가로 스크롤 -->
      <div class="space-y-1.5 pt-1">
        <div class="flex items-center justify-between text-[11px] text-slate-400 px-1">
          <span>원터치 스타일 코디</span>
          <span class="text-purple-300 text-[10px]">가로로 밀어서 선택 ➔</span>
        </div>
        <div class="flex items-center gap-2 overflow-x-auto no-scrollbar py-1 text-xs">
          <button type="button" onclick="applyQuickLookApp('basic')" class="px-3.5 py-1.5 rounded-full bg-purple-600/30 hover:bg-purple-600/50 text-white border border-purple-400/50 font-bold shrink-0 transition active:scale-95">
            #기본캐주얼
          </button>
          <button type="button" onclick="applyQuickLookApp('highteen')" class="px-3.5 py-1.5 rounded-full bg-pink-600/20 hover:bg-pink-600/40 text-pink-200 border border-pink-500/30 font-bold shrink-0 transition active:scale-95">
            #하이틴룩
          </button>
          <button type="button" onclick="applyQuickLookApp('suit')" class="px-3.5 py-1.5 rounded-full bg-amber-600/20 hover:bg-amber-600/40 text-amber-200 border border-amber-500/30 font-bold shrink-0 transition active:scale-95">
            #청담VIP수트
          </button>
          <button type="button" onclick="applyQuickLookApp('future_ceo')" class="px-3.5 py-1.5 rounded-full bg-purple-600/20 hover:bg-purple-600/40 text-purple-200 border border-purple-500/30 font-bold shrink-0 transition active:scale-95">
            #2035글로벌CEO
          </button>
          <button type="button" onclick="applyQuickLookApp('family')" class="px-3.5 py-1.5 rounded-full bg-emerald-600/20 hover:bg-emerald-600/40 text-emerald-200 border border-emerald-500/30 font-bold shrink-0 transition active:scale-95">
            #가족시밀러룩
          </button>
          <button type="button" onclick="applyQuickLookApp('reform_0')" class="px-3.5 py-1.5 rounded-full bg-cyan-600/20 hover:bg-cyan-600/40 text-cyan-200 border border-cyan-500/30 font-bold shrink-0 transition active:scale-95">
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
              <span id="step-title" class="text-amber-300 font-extrabold">Step 3. 나눔과 공존 마스터</span>
            </div>
            <p class="text-[10px] text-slate-400">드라마틱 퀴즈를 풀고 특별 코디와 목소리를 해금하세요!</p>
          </div>
        </div>
        <button type="button" onclick="toggleQuizPopupApp()" id="btn-toggle-quiz-app" class="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-bold text-xs shadow-md shadow-purple-900/40 transition active:scale-95 flex items-center gap-1">
          <span>🎓</span><span>인성 퀴즈 풀기</span>
        </button>
      </div>

      <!-- 팝업 퀴즈 카드 -->
      <div id="quiz-popup-card-app" class="hidden p-4 rounded-xl bg-slate-950/95 border border-purple-500/40 space-y-3 transition-all">
        <div class="flex items-center justify-between pb-2 border-b border-slate-800">
          <div class="flex items-center gap-1">
            <button type="button" onclick="selectStep(0)" id="step-tab-0" class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400">Lv.0</button>
            <button type="button" onclick="selectStep(1)" id="step-tab-1" class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400">Step 1</button>
            <button type="button" onclick="selectStep(2)" id="step-tab-2" class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400">Step 2</button>
            <button type="button" onclick="selectStep(3)" id="step-tab-3" class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-600 text-white">Step 3</button>
          </div>
          <button type="button" onclick="toggleQuizPopupApp()" class="text-slate-400 hover:text-white text-base">✕</button>
        </div>

        <div id="quiz-container" class="space-y-2.5">
          <!-- Quiz options injected here -->
        </div>

        <div class="pt-2 border-t border-slate-800 flex items-center justify-between text-xs">
          <span class="text-[11px] text-slate-400">스피치 미션: 긍정 확언 선서</span>
          <button type="button" onclick="triggerAffirmationSuccess()" class="px-3 py-1 rounded-lg bg-pink-600 hover:bg-pink-500 text-white font-bold text-xs transition active:scale-95">
            ✨ 긍정 확언 완료
          </button>
        </div>
      </div>
    </div>


    <!-- 🗂️ [토스 스타일 하단 4대 접이식 서랍 (Drawer)] -->
    <div class="space-y-2 pt-2">
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <button type="button" onclick="toggleDrawerApp('body')" id="btn-drawer-body-app" class="p-2.5 rounded-xl bg-slate-900/70 hover:bg-slate-800 border border-slate-800 text-left transition flex items-center gap-2">
          <span class="text-lg">📏</span>
          <div>
            <div class="text-xs font-bold text-slate-200">체형·컬러</div>
            <div class="text-[10px] text-slate-400">비율/퍼스널컬러</div>
          </div>
        </button>

        <button type="button" onclick="toggleDrawerApp('voc')" id="btn-drawer-voc-app" class="p-2.5 rounded-xl bg-slate-900/70 hover:bg-slate-800 border border-slate-800 text-left transition flex items-center gap-2">
          <span class="text-lg">💬</span>
          <div>
            <div class="text-xs font-bold text-slate-200">전담팀 VOC</div>
            <div class="text-[10px] text-slate-400">4대AI 자동패치</div>
          </div>
        </button>

        <button type="button" onclick="toggleDrawerApp('deploy')" id="btn-drawer-deploy-app" class="p-2.5 rounded-xl bg-slate-900/70 hover:bg-slate-800 border border-slate-800 text-left transition flex items-center gap-2">
          <span class="text-lg">📲</span>
          <div>
            <div class="text-xs font-bold text-slate-200">스토어·복구</div>
            <div class="text-[10px] text-slate-400">GooglePlay 복구</div>
          </div>
        </button>

        <button type="button" onclick="toggleDrawerApp('cert')" id="btn-drawer-cert-app" class="p-2.5 rounded-xl bg-slate-900/70 hover:bg-slate-800 border border-slate-800 text-left transition flex items-center gap-2">
          <span class="text-lg">🎓</span>
          <div>
            <div class="text-xs font-bold text-slate-200">인증서</div>
            <div class="text-[10px] text-slate-400">수료증 발급</div>
          </div>
        </button>
      </div>

      <!-- 서랍 1: 체형/컬러 -->
      <div id="drawer-body-app" class="hidden p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
        <div class="flex items-center justify-between border-b border-slate-800 pb-2">
          <h5 class="text-xs font-bold text-white flex items-center gap-1.5"><span>📏</span> 체형 비율 및 피부톤 설정</h5>
          <button type="button" onclick="toggleDrawerApp('body')" class="text-slate-400 hover:text-white text-xs">닫기 ✕</button>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div class="space-y-2">
            <div>
              <div class="flex justify-between text-[11px] text-slate-400 mb-1">
                <span>키 (Height)</span><span id="height-val" class="text-purple-300 font-bold">168cm</span>
              </div>
              <input type="range" id="slider-height" min="140" max="195" value="168" oninput="updateAvatarProportions()" class="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500">
            </div>
            <div>
              <div class="flex justify-between text-[11px] text-slate-400 mb-1">
                <span>몸무게 (Weight)</span><span id="weight-val" class="text-purple-300 font-bold">62kg</span>
              </div>
              <input type="range" id="slider-weight" min="40" max="110" value="62" oninput="updateAvatarProportions()" class="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500">
            </div>
          </div>
          <div class="space-y-2">
            <span class="text-[11px] text-slate-400 block">피부톤 RGB 스캐너</span>
            <div class="flex items-center gap-2">
              <button type="button" onclick="updateSkinTone('#fbe3d5')" class="w-8 h-8 rounded-full border border-white/20 bg-[#fbe3d5] shadow-sm hover:scale-110 transition" title="화사한 웜톤"></button>
              <button type="button" onclick="updateSkinTone('#f4cfb8')" class="w-8 h-8 rounded-full border border-white/20 bg-[#f4cfb8] shadow-sm hover:scale-110 transition" title="내추럴 뉴트럴"></button>
              <button type="button" onclick="updateSkinTone('#e0ac82')" class="w-8 h-8 rounded-full border border-white/20 bg-[#e0ac82] shadow-sm hover:scale-110 transition" title="건강한 태닝톤"></button>
              <button type="button" onclick="updateSkinTone('#8d5524')" class="w-8 h-8 rounded-full border border-white/20 bg-[#8d5524] shadow-sm hover:scale-110 transition" title="딥 브라운"></button>
            </div>
          </div>
        </div>
      </div>

      <!-- 서랍 2: VOC 건의함 -->
      <div id="drawer-voc-app" class="hidden p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
        <div class="flex items-center justify-between border-b border-slate-800 pb-2">
          <h5 class="text-xs font-bold text-white flex items-center gap-1.5"><span>💬</span> 초격차 관리팀 직통 VOC 건의함</h5>
          <button type="button" onclick="toggleDrawerApp('voc')" class="text-slate-400 hover:text-white text-xs">닫기 ✕</button>
        </div>
        <div class="space-y-2">
          <div class="flex gap-2">
            <input type="text" id="app-voc-input" placeholder="바라는 점이나 코디 아이디어를 적어주세요!" class="flex-1 px-3 py-2 rounded-xl bg-slate-950 border border-slate-700 text-xs text-white placeholder-slate-500">
            <button type="button" onclick="submitAppVoc()" class="px-3.5 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shrink-0 transition">
              제출
            </button>
          </div>
          <div id="voc-response-box" class="hidden p-3 rounded-xl bg-purple-950/30 border border-purple-500/30 text-xs text-purple-200">
            <!-- AI 브리핑 출력 -->
          </div>
        </div>
      </div>

      <!-- 서랍 3: Google Play 복구 -->
      <div id="drawer-deploy-app" class="hidden p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
        <div class="flex items-center justify-between border-b border-slate-800 pb-2">
          <h5 class="text-xs font-bold text-white flex items-center gap-1.5"><span>🛡️</span> Google Play 개발자 계정 복구 가이드</h5>
          <button type="button" onclick="toggleDrawerApp('deploy')" class="text-slate-400 hover:text-white text-xs">닫기 ✕</button>
        </div>
        <div class="text-xs text-slate-300 space-y-2">
          <p>• 계정명: <b>lee sangill</b> | ID: <code class="text-amber-300">8519115145103880120</code></p>
          <button type="button" onclick="openGooglePlayGuideModal()" class="w-full py-2.5 rounded-xl bg-cyan-600/30 hover:bg-cyan-600/50 text-cyan-200 border border-cyan-500/40 font-bold transition">
            3단계 신원 인증 복구 상세 매뉴얼 보기
          </button>
        </div>
      </div>

      <!-- 서랍 4: 인증서 -->
      <div id="drawer-cert-app" class="hidden p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3 text-center">
        <div class="flex items-center justify-between border-b border-slate-800 pb-2">
          <h5 class="text-xs font-bold text-white flex items-center gap-1.5"><span>🎓</span> 품격 마스터 인증서</h5>
          <button type="button" onclick="toggleDrawerApp('cert')" class="text-slate-400 hover:text-white text-xs">닫기 ✕</button>
        </div>
        <div class="p-3 rounded-xl bg-slate-950 border border-slate-800">
          <p class="text-xs text-amber-300 font-bold mb-1">HGS-STYLE-CERT-2026-001</p>
          <p class="text-[11px] text-slate-300">이상일 대표님의 한걸음씩 나눔 품격 마스터 인증이 완료되었습니다.</p>
        </div>
      </div>
    </div>

  </div>
'''

# Inject standalone ultra simple body
body_pos = app_html.find('<body')
script_pos = app_html.find('<script', body_pos)

if body_pos != -1 and script_pos != -1:
    app_html = app_html[:body_pos] + standalone_ultra_simple_body + '\n  ' + app_html[script_pos:]
    print("Replaced body in dream_closet_future_master_app.html!")

# Inject JS helpers for Standalone App
app_js_helpers = '''
    // ── 💎 Standalone App Ultra-Simple Minimal Luxury UI 헬퍼 스크립트 ──
    function selectStudioVoiceMinimalApp(id) {
      selectStudioVoice('', id);
      const voiceIds = ['designer', 'highteen', 'gentleman', 'dj', 'future'];
      voiceIds.forEach(k => {
        const btn = document.getElementById('mini-v-' + k);
        if (btn) {
          const ring = btn.querySelector('div');
          const txt = btn.querySelector('span');
          if (k === id) {
            btn.className = 'flex flex-col items-center gap-1 group transition scale-105';
            if (ring) ring.className = 'w-11 h-11 sm:w-12 sm:h-12 rounded-full p-0.5 bg-gradient-to-tr from-amber-400 to-purple-600 shadow-md shadow-purple-900/40 ring-2 ring-amber-400';
            if (txt) { txt.className = 'text-[10px] font-bold text-amber-300'; }
          } else {
            btn.className = 'flex flex-col items-center gap-1 group transition opacity-70 hover:opacity-100';
            if (ring) ring.className = 'w-11 h-11 sm:w-12 sm:h-12 rounded-full p-0.5 bg-slate-800';
            if (txt) { txt.className = 'text-[10px] text-slate-400'; }
          }
        }
      });
      playSelectedStudioVoice('');
    }

    function toggleVoiceTuningBarApp() {
      const b = document.getElementById('voice-tuning-bar-app');
      if (b) b.classList.toggle('hidden');
    }

    function toggleQuizPopupApp() {
      const p = document.getElementById('quiz-popup-card-app');
      if (p) {
        p.classList.toggle('hidden');
        if (!p.classList.contains('hidden')) {
          renderQuizStep(currentQuizStep || 3);
        }
      }
    }

    function toggleDrawerApp(id) {
      const drawers = ['body', 'voc', 'deploy', 'cert'];
      drawers.forEach(d => {
        const el = document.getElementById('drawer-' + d + '-app');
        const btn = document.getElementById('btn-drawer-' + d + '-app');
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

    function applyQuickLookApp(lookKey) {
      if (lookKey === 'basic') {
        currentLookId = 'basic';
        document.getElementById('canvas-look-label').innerText = '👔 화이트 베이직 & 슬림 데님';
        drawFittingAvatar();
        speakSmartNeuralDirect('기본이 가장 빛나는 법이죠. 소매 살짝 롤업하고 단정하게 걸어보세요!');
      } else if (lookKey === 'highteen') {
        currentLookId = 'highteen';
        document.getElementById('canvas-look-label').innerText = '🌸 K-하이틴 & 시티보이 룩';
        drawFittingAvatar();
        speakSmartNeuralDirect('와! 하이틴 무드 완전 찰떡이에요! 친구들이 어디서 샀냐고 물어보겠는데요?');
      } else if (lookKey === 'suit') {
        currentLookId = 'suit';
        document.getElementById('canvas-look-label').innerText = '👔 청담 VIP 수트 & 롱코트';
        drawFittingAvatar();
        speakSmartNeuralDirect('대표님, 어깨선부터 V존 비율까지 걸어 다니는 화보 그 자체입니다.');
      } else if (lookKey === 'future_ceo') {
        switchFittingSubTab('future');
        applyFutureLook('ceo');
      } else if (lookKey === 'family') {
        switchFittingSubTab('family');
      } else if (lookKey === 'reform_0') {
        currentLookId = 'reform';
        document.getElementById('canvas-look-label').innerText = '♻️ 0원 리폼: 3:7 턱인 & 프렌치 롤업 핏';
        drawFittingAvatar();
        speakSmartNeuralDirect('돈 한 푼 안 들이고 기본 티셔츠 3:7 비율과 소매 롤업만으로 명품 핏 완성!');
      }
    }
'''

if 'selectStudioVoiceMinimalApp' not in app_html:
    s_end = app_html.rfind('</script>')
    if s_end != -1:
        app_html = app_html[:s_end] + app_js_helpers + '\n  ' + app_html[s_end:]
        print("Injected app_js_helpers into dream_closet_future_master_app.html!")

with open('dashboard/dream_closet_future_master_app.html', 'w', encoding='utf-8') as f:
    f.write(app_html)

print("dream_closet_future_master_app.html successfully updated!")
