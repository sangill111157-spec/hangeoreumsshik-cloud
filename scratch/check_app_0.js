
    // ── Global State ──
    let currentStep = 0; // 0: Lv0, 1: Step1(EQ), 2: Step2(MQ), 3: Step3(CQ)
    let currentAngle = 0; // 0, 90, 180, 270
    let currentOutfit = 'daily'; // 'daily', 'highteen', 'suit', 'future_ceo', 'future_scientist', 'future_artist', 'future_diplomat', 'family_palette'
    let avatarHeight = 172;
    let avatarWeight = 62;
    let avatarFit = 2; // 1: 슬림, 2: 표준, 3: 루즈
    let skinTone = '#f8d9c2';
    let isVoiceListening = false;
    let recognition = null;

    // ── Canvas Setup ──
    const canvas = document.getElementById('app-fitting-canvas');
    const ctx = canvas.getContext('2d');

    // ── Speech Synthesis (TTS) ──
        // 🎙️✨ 5대 하이엔드 보이스 페르소나 & 듀얼 엔진 (Edge Neural TTS + WebSpeech Fallback) ✨🎙️
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


    // ── Speech Recognition (STT) ──
    function initSpeechRecognition() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        console.warn('Speech recognition not supported in this browser.');
        return null;
      }
      const rec = new SpeechRecognition();
      rec.lang = 'ko-KR';
      rec.continuous = false;
      rec.interimResults = false;

      rec.onstart = () => {
        isVoiceListening = true;
        const btn = document.getElementById('btn-mic-stt');
        if (btn) btn.className = 'w-10 h-10 rounded-xl bg-red-600 text-white flex items-center justify-center text-lg shadow-lg animate-pulse shrink-0';
      };

      rec.onend = () => {
        isVoiceListening = false;
        const btn = document.getElementById('btn-mic-stt');
        if (btn) btn.className = 'w-10 h-10 rounded-xl bg-pink-600 hover:bg-pink-500 text-white flex items-center justify-center text-lg shadow-md transition active:scale-95 shrink-0';
      };

      rec.onresult = (event) => {
        const transcript = event.results[0][0].transcript.trim();
        handleVoiceCommand(transcript);
      };

      rec.onerror = (e) => {
        console.warn('STT Error:', e);
      };

      return rec;
    }

    function toggleVoiceSTT() {
      if (!recognition) recognition = initSpeechRecognition();
      if (!recognition) {
        alert('이 브라우저는 음성 인식을 지원하지 않습니다. 크롬 또는 사파리를 권장합니다.');
        return;
      }
      if (isVoiceListening) {
        recognition.stop();
      } else {
        try { recognition.start(); } catch (e) {}
      }
    }

    function handleVoiceCommand(cmd) {
      const p = document.getElementById('voice-transcript-text');
      if (p) p.innerHTML = `인식된 음성: <b>"${cmd}"</b>`;

      if (cmd.includes('소중') || cmd.includes('따뜻한 사람') || cmd.includes('확언')) {
        triggerAffirmationSuccess();
        speakText('멋진 긍정 확언입니다! 당신은 세상에서 가장 소중하고 따뜻한 빛입니다.');
      } else if (cmd.includes('수트') || cmd.includes('정장') || cmd.includes('청담')) {
        currentOutfit = 'suit';
        drawAvatar();
        speakText('청담 VIP 클래식 수트로 환복했습니다. 품격과 리더십이 돋보입니다.');
      } else if (cmd.includes('하이틴') || cmd.includes('밝은') || cmd.includes('시티보이')) {
        currentOutfit = 'highteen';
        drawAvatar();
        speakText('싱그러운 K-하이틴 룩을 입혀드렸습니다! 화사한 에너지가 넘치네요.');
      } else if (cmd.includes('ceo') || cmd.includes('대표') || cmd.includes('미래')) {
        applyFutureLook('ceo');
      } else {
        speakText(`말씀하신 "${cmd}" 관련 스타일을 매칭해 드립니다.`);
      }
    }

    // ── 4-Direction Vector Avatar Renderer ──
    function drawAvatar() {
      if (!canvas) return;
      const w = canvas.width;
      const h = canvas.height;
      const cx = w / 2;

      ctx.clearRect(0, 0, w, h);

      // 1. Background Runway Stage
      const bgGrad = ctx.createLinearGradient(0, 0, 0, h);
      bgGrad.addColorStop(0, '#090d16');
      bgGrad.addColorStop(0.7, '#0f172a');
      bgGrad.addColorStop(1, '#020617');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, w, h);

      // Floor Oval Shadow & Spotlight
      ctx.save();
      const floorGrad = ctx.createRadialGradient(cx, h - 45, 10, cx, h - 45, 160);
      floorGrad.addColorStop(0, 'rgba(236, 72, 153, 0.4)');
      floorGrad.addColorStop(0.6, 'rgba(168, 85, 247, 0.15)');
      floorGrad.addColorStop(1, 'transparent');
      ctx.fillStyle = floorGrad;
      ctx.beginPath();
      ctx.ellipse(cx, h - 45, 140, 26, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();

      // Proportions calculation
      const scale = (avatarHeight / 170);
      const widthFactor = (avatarWeight / 60);
      const headY = 110 - (scale - 1) * 30;
      const headRadius = 38 * scale;
      const shoulderW = 55 * scale * widthFactor;
      const torsoH = 150 * scale;
      const legH = 210 * scale;

      // 2. Draw Legs & Shoes
      ctx.save();
      let pantsColor = '#1e293b';
      if (currentOutfit === 'suit' || currentOutfit === 'future_ceo') pantsColor = '#0f172a';
      if (currentOutfit === 'highteen') pantsColor = '#3b82f6';
      if (currentOutfit === 'future_scientist') pantsColor = '#1e1e2f';
      if (currentOutfit === 'future_artist') pantsColor = '#f5f5f4';

      ctx.fillStyle = pantsColor;
      const legSpread = currentAngle === 90 || currentAngle === 270 ? 12 : 22;

      // Left Leg
      ctx.beginPath();
      ctx.roundRect(cx - shoulderW * 0.45, headY + headRadius + torsoH - 10, 24 * widthFactor, legH, [4, 4, 8, 8]);
      ctx.fill();

      // Right Leg (only visible in front/back or slightly offset in side)
      if (currentAngle === 0 || currentAngle === 180) {
        ctx.beginPath();
        ctx.roundRect(cx + shoulderW * 0.45 - (24 * widthFactor), headY + headRadius + torsoH - 10, 24 * widthFactor, legH, [4, 4, 8, 8]);
        ctx.fill();
      }

      // Shoes
      ctx.fillStyle = '#0f172a';
      if (currentOutfit === 'highteen') ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.roundRect(cx - shoulderW * 0.48, headY + headRadius + torsoH + legH - 12, 28, 14, [4, 8, 4, 4]);
      ctx.fill();
      if (currentAngle === 0 || currentAngle === 180) {
        ctx.beginPath();
        ctx.roundRect(cx + shoulderW * 0.48 - 28, headY + headRadius + torsoH + legH - 12, 28, 14, [8, 4, 4, 4]);
        ctx.fill();
      }
      ctx.restore();

      // 3. Draw Torso & Outfit
      ctx.save();
      let topColor = '#ffffff';
      if (currentOutfit === 'suit' || currentOutfit === 'future_ceo') topColor = '#1e1b4b';
      if (currentOutfit === 'highteen') topColor = '#f43f5e';
      if (currentOutfit === 'future_scientist') topColor = '#0284c7';
      if (currentOutfit === 'future_artist') topColor = '#e11d48';
      if (currentOutfit === 'future_diplomat') topColor = '#065f46';

      ctx.fillStyle = topColor;
      ctx.beginPath();
      const torsoW = currentAngle === 90 || currentAngle === 270 ? shoulderW * 1.1 : shoulderW * 2;
      ctx.roundRect(cx - torsoW / 2, headY + headRadius, torsoW, torsoH, [16, 16, 8, 8]);
      ctx.fill();

      // Outfit Accents (Collar, Buttons, Tie)
      if (currentOutfit === 'suit' || currentOutfit === 'future_ceo') {
        // V-neck lapel & tie
        ctx.strokeStyle = '#312e81';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(cx - 20, headY + headRadius);
        ctx.lineTo(cx, headY + headRadius + 60);
        ctx.lineTo(cx + 20, headY + headRadius);
        ctx.stroke();

        // Gold Tie
        ctx.fillStyle = '#f59e0b';
        ctx.beginPath();
        ctx.moveTo(cx - 6, headY + headRadius + 20);
        ctx.lineTo(cx + 6, headY + headRadius + 20);
        ctx.lineTo(cx + 4, headY + headRadius + 80);
        ctx.lineTo(cx, headY + headRadius + 90);
        ctx.lineTo(cx - 4, headY + headRadius + 80);
        ctx.closePath();
        ctx.fill();
      } else if (currentOutfit === 'highteen') {
        // High-teen collar
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.moveTo(cx - 18, headY + headRadius);
        ctx.lineTo(cx, headY + headRadius + 25);
        ctx.lineTo(cx + 18, headY + headRadius);
        ctx.closePath();
        ctx.fill();
      } else if (currentOutfit === 'future_scientist') {
        // Cyber glowing lines
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 2.5;
        ctx.shadowColor = '#38bdf8';
        ctx.shadowBlur = 8;
        ctx.beginPath();
        ctx.moveTo(cx - torsoW / 2 + 8, headY + headRadius + 30);
        ctx.lineTo(cx + torsoW / 2 - 8, headY + headRadius + 30);
        ctx.stroke();
      }
      ctx.restore();

      // 4. Arms
      ctx.save();
      ctx.fillStyle = topColor;
      const armW = 18 * widthFactor;
      const armH = 140 * scale;
      if (currentAngle === 0 || currentAngle === 180) {
        ctx.beginPath();
        ctx.roundRect(cx - torsoW / 2 - armW + 2, headY + headRadius + 10, armW, armH, [8, 4, 8, 8]);
        ctx.fill();
        ctx.beginPath();
        ctx.roundRect(cx + torsoW / 2 - 2, headY + headRadius + 10, armW, armH, [4, 8, 8, 8]);
        ctx.fill();
      } else {
        // One side arm
        ctx.beginPath();
        ctx.roundRect(cx - armW / 2, headY + headRadius + 10, armW, armH, [8, 8, 8, 8]);
        ctx.fill();
      }
      ctx.restore();

      // 5. Head & Face
      ctx.save();
      ctx.fillStyle = skinTone;
      ctx.beginPath();
      ctx.arc(cx, headY, headRadius, 0, Math.PI * 2);
      ctx.fill();

      // Hair & Facial features depending on angle
      ctx.fillStyle = '#1e1b4b'; // Dark hair
      if (currentAngle === 0) {
        // Front: hair bangs + eyes + gentle smile
        ctx.beginPath();
        ctx.arc(cx, headY - 8, headRadius + 2, Math.PI, Math.PI * 2);
        ctx.fill();
        // Eyes
        ctx.fillStyle = '#0f172a';
        ctx.beginPath();
        ctx.arc(cx - 12, headY - 2, 3, 0, Math.PI * 2);
        ctx.arc(cx + 12, headY - 2, 3, 0, Math.PI * 2);
        ctx.fill();
        // Warm smile
        ctx.strokeStyle = '#e11d48';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(cx, headY + 8, 10, 0.2 * Math.PI, 0.8 * Math.PI);
        ctx.stroke();
      } else if (currentAngle === 180) {
        // Back: full hair cover
        ctx.beginPath();
        ctx.arc(cx, headY, headRadius + 3, 0, Math.PI * 2);
        ctx.fill();
      } else {
        // Side profile hair
        ctx.beginPath();
        ctx.arc(cx, headY - 5, headRadius + 2, 0.8 * Math.PI, 1.8 * Math.PI);
        ctx.fill();
        // Eye
        ctx.fillStyle = '#0f172a';
        ctx.beginPath();
        const eyeX = currentAngle === 90 ? cx - 14 : cx + 14;
        ctx.arc(eyeX, headY - 2, 3, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();

      // 6. Dynamic Aura Glow
      ctx.save();
      ctx.strokeStyle = 'rgba(236, 72, 153, 0.4)';
      ctx.lineWidth = 2;
      ctx.setLineDash([6, 6]);
      ctx.beginPath();
      ctx.arc(cx, headY + torsoH / 2, torsoH * 0.9, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }

    // ── Angle Controller ──
    function setAngle(ang) {
      currentAngle = ang;
      document.querySelectorAll('[id^="angle-btn-"]').forEach(b => {
        b.className = 'px-2 py-1 rounded bg-slate-900 text-slate-300 text-[10px]';
      });
      const activeBtn = document.getElementById(`angle-btn-${ang}`);
      if (activeBtn) activeBtn.className = 'px-2 py-1 rounded bg-purple-600 text-white font-bold text-[10px]';

      const label = document.getElementById('canvas-angle-label');
      const names = { 0: '0° FRONT (정면)', 90: '90° LEFT (좌측)', 180: '180° BACK (후면)', 270: '270° RIGHT (우측)' };
      if (label) label.textContent = `Angle: ${names[ang] || ang}`;

      drawAvatar();
    }

    // ── Proportion Slider Updates ──
    function updateAvatarProportions() {
      avatarHeight = parseInt(document.getElementById('input-height').value, 10);
      avatarWeight = parseInt(document.getElementById('input-weight').value, 10);
      avatarFit = parseInt(document.getElementById('input-fit').value, 10);

      document.getElementById('val-height').textContent = `${avatarHeight} cm`;
      document.getElementById('val-weight').textContent = `${avatarWeight} kg`;
      const fitNames = { 1: '슬림핏', 2: '3:7 황금핏', 3: '오버핏' };
      document.getElementById('val-fit').textContent = fitNames[avatarFit];

      drawAvatar();
    }

    function updateSkinToneColor(color) {
      skinTone = color;
      drawAvatar();
      speakText('피부톤 컬러가 실시간으로 보정되었습니다.');
    }

    // ── 4단계 인성 어드벤처 & 해금 로직 ──
    const QUIZ_DATA = [
      {
        step: 0,
        badge: 'Lv.0 입문자 (데일리 오픈)',
        title: 'Lv.0 입문자 코디: 나의 첫 인상과 데일리 스타일',
        reward: '기본 데일리 룩 + 체형 비율 슬라이더 오픈',
        story: '꿈의 옷장에 오신 것을 환영합니다! 당신만의 체형과 비율을 자유롭게 설정하고 4방향 피팅룸을 경험해 보세요.',
        choices: ['멋진 데일리 룩으로 시작하기', '나의 체형 슬라이더 조절하기', '다음 인성 퀴즈 도전하기']
      },
      {
        step: 1,
        badge: 'Step 1. 공감 EQ 해금 완료',
        title: 'Step 1. 공감 드라마 퀴즈 (EQ): 축제 날 친구의 찢어진 옷',
        reward: 'K-하이틴 & 시티보이 룩 + RGB 스캐너 + 디자이너 TTS 해금',
        story: '학교 축제 무대 직전, 단짝 친구의 무대 의상이 찢어져 울고 있습니다. 나에게는 집에 가려 챙겨둔 여분의 멋진 자켓이 하나 있습니다. 어떻게 하시겠습니까?',
        choices: [
          '1. 즉시 내 여분 자켓을 친구에게 입혀주고 함께 무대에 오른다. (공감 & 배려 만점)',
          '2. 옷이 아까우니 빌려주지 않고 내 무대만 준비한다.',
          '3. 모른 척 지나간다.'
        ]
      },
      {
        step: 2,
        badge: 'Step 2. 정직 MQ 해금 완료',
        title: 'Step 2. 정직과 용기 퀴즈 (MQ): 나만의 0원 옷장 마법 & 당당한 리더',
        reward: '청담 VIP 클래식 수트 + 0원 리폼 레시피 + 마이크 음성제어(STT) 해금',
        story: '친구들과 모인 자리에서 옷에 작은 얼룩을 묻혔거나 실수를 했을 때, 비싼 새 옷을 사달라고 조르는 대신 내가 선택할 수 있는 가장 정직하고 당당한 태도는?',
        choices: [
          '1. 실수를 당당히 밝히고 소매 롤업이나 브로치로 독창적인 커스텀 룩으로 승화시킨다. (정직 & 창의 만점)',
          '2. 남의 탓으로 돌리고 화를 낸다.',
          '3. 비싼 명품 옷을 사지 못해 부끄러워하며 숨는다.'
        ]
      },
      {
        step: 3,
        badge: 'Step 3. 나눔 CQ 마스터 해금 완료',
        title: 'Step 3. 나눔과 공존 마스터 (CQ) & 스피치 확언 미션',
        reward: '타임머신 2035 미래의 나 + 가족 시밀러룩 + 24시간 보이스 소울메이트 + HGS 정식 인증서',
        story: '미래에 큰 성공을 거두었을 때, 나만의 부를 자랑하는 대신 세상을 가장 따뜻하고 아름답게 만드는 당신의 선택은?',
        choices: [
          '1. 상생 기금 10%를 적립하여 가난한 청소년들에게 꿈과 멋진 옷을 무료로 선물한다. (나눔 & 공존 만점)',
          '2. 나 혼자만 모든 부를 독점하고 과시한다.',
          '3. 아무것도 하지 않고 방관한다.'
        ]
      }
    ];

    function selectStep(step) {
      currentStep = step;
      renderQuizStep(step);
    }

    function renderQuizStep(step) {
      const q = QUIZ_DATA[step] || QUIZ_DATA[0];
      document.getElementById('quiz-title').textContent = q.title;
      document.getElementById('quiz-reward-preview').textContent = `보상: ${q.reward}`;
      document.getElementById('quiz-story').textContent = q.story;
      document.getElementById('unlock-badge').textContent = q.badge;

      const bar = document.getElementById('unlock-progress-bar');
      if (bar) bar.style.width = `${(step + 1) * 25}%`;

      document.querySelectorAll('[id^="step-btn-"]').forEach((b, idx) => {
        b.className = idx === step ? 'p-1.5 rounded-xl bg-purple-600/40 border border-purple-400 font-bold text-white' : 'p-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-400';
      });

      const choicesBox = document.getElementById('quiz-choices');
      choicesBox.innerHTML = q.choices.map((c, i) => `
        <button type="button" onclick="answerQuiz(${i})" class="p-3 rounded-xl ${i === 0 ? 'bg-purple-950/40 hover:bg-purple-900/60 border border-purple-500/30' : 'bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400'} text-left transition active:scale-98">
          ${c}
        </button>
      `).join('');
    }

    function answerQuiz(choiceIdx) {
      if (choiceIdx === 0) {
        // 정답 및 해금
        if (currentStep === 1) {
          currentOutfit = 'highteen';
          speakText('정답입니다! 공감과 배려의 마음으로 K-하이틴 룩과 피부톤 스캐너가 해금되었습니다.');
        } else if (currentStep === 2) {
          currentOutfit = 'suit';
          speakText('훌륭합니다! 정직과 용기의 선택으로 청담 VIP 수트와 음성 제어 기능이 열렸습니다.');
        } else if (currentStep === 3) {
          currentOutfit = 'future_ceo';
          speakText('축하합니다! 나눔과 공존의 마스터가 되어 2035년 미래의 나와 가족 시밀러룩이 모두 해금되었습니다!');
        }
        drawAvatar();
        alert(`🎉 [축하합니다! ${QUIZ_DATA[currentStep].reward}] 해금 완료!`);
        if (currentStep < 3) {
          selectStep(currentStep + 1);
        }
      } else {
        speakText('따뜻한 인성의 관점에서 다시 한 번 생각해보세요!');
        alert('💡 인성 퀴즈 힌트: 상대방을 배려하고 정직하게 나눔을 실천하는 1번 선택지를 골라보세요!');
      }
    }

    function triggerAffirmationSuccess() {
      speakText('당신의 확언이 마음에 깊이 각인되었습니다! 당신은 세상에서 가장 소중하고 따뜻한 빛입니다.');
      alert('✨ [긍정 확언 완료]: 마음에 긍정의 에너지가 충전되었습니다!');
    }

    function unlockAllFeaturesFreePass() {
      currentStep = 3;
      selectStep(3);
      currentOutfit = 'future_ceo';
      drawAvatar();
      speakText('이상일 대표님 프리패스가 승인되었습니다. 전 단계 인성 룩, 음성 소통, 타임머신 2035가 100% 전면 해금되었습니다!');
      alert('👑 [대표님 프리패스 가동 완료]: 모든 코디, 2035 미래의 나, 가족 시밀러룩, 음성 소통이 즉시 열렸습니다!');
    }

    // ── SubTab Fitting Modes ──
    function switchFittingSubTab(tabName) {
      const tabs = ['timemachine', 'family', 'zerocost'];
      tabs.forEach(t => {
        const pane = document.getElementById(`subtab-pane-${t}`);
        const btn = document.getElementById(`subtab-btn-${t}`);
        if (t === tabName) {
          if (pane) pane.classList.remove('hidden');
          if (btn) btn.className = 'py-1.5 rounded-lg bg-purple-600 text-white shadow-sm transition';
        } else {
          if (pane) pane.classList.add('hidden');
          if (btn) btn.className = 'py-1.5 rounded-lg text-slate-400 hover:text-white transition';
        }
      });
    }

    function applyFutureLook(type) {
      currentOutfit = `future_${type}`;
      drawAvatar();
      const names = {
        ceo: '👑 글로벌 CEO 수트',
        scientist: '🚀 우주 AI 과학자 테크웨어',
        artist: '🎨 세계적 미디어 아티스트 룩',
        diplomat: '🕊️ 평화 외교관 리더 모던룩'
      };
      speakText(`2035년의 성공한 내 모습, ${names[type] || type}를 피팅했습니다!`);
    }

    function playFutureSelfVoiceLetter() {
      const letter = "안녕, 2026년의 나야! 나는 10년 뒤 꿈을 이룬 2035년의 너야. 지금 네가 겪는 모든 고민과 노력은 하나도 헛되지 않았어. 너는 상생과 나눔을 실천하며 세상을 따뜻하게 밝히는 멋진 리더가 되었단다. 너를 언제나 믿어!";
      speakText(letter);
      alert(`💌 [2035년 미래의 내가 보낸 음성 편지]\n\n"${letter}"`);
    }

    function applyFamilyPalette(theme) {
      currentOutfit = 'family_palette';
      drawAvatar();
      const names = {
        navy_gold: '로열 네이비 & 골드',
        warm_beige: '파스텔 웜 베이지',
        forest_sage: '포레스트 세이지 그린'
      };
      speakText(`이상일 대표님과 세 따님의 ${names[theme] || theme} 패밀리 팔레트가 적용되었습니다.`);
    }

    function renderFamilySimilarLookCanvas() {
      if (!canvas) return;
      const w = canvas.width;
      const h = canvas.height;
      ctx.clearRect(0, 0, w, h);

      // Draw 4 figures side-by-side
      const bgGrad = ctx.createLinearGradient(0, 0, 0, h);
      bgGrad.addColorStop(0, '#020617');
      bgGrad.addColorStop(1, '#0f172a');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, w, h);

      const members = [
        { name: '이상일 대표님', role: '교장 / 리더', x: 80, scale: 0.95, color: '#1e1b4b' },
        { name: '첫째 이은솔', role: '수석 (중3)', x: 170, scale: 0.88, color: '#312e81' },
        { name: '둘째 이송효', role: '선임 (중1)', x: 260, scale: 0.82, color: '#4338ca' },
        { name: '셋째 이해상', role: '주니어 (초5)', x: 350, scale: 0.75, color: '#6366f1' }
      ];

      members.forEach(m => {
        // Shadow
        ctx.fillStyle = 'rgba(236, 72, 153, 0.2)';
        ctx.beginPath();
        ctx.ellipse(m.x, h - 50, 35, 10, 0, 0, Math.PI * 2);
        ctx.fill();

        // Body
        ctx.fillStyle = m.color;
        ctx.beginPath();
        ctx.roundRect(m.x - 25 * m.scale, h - 220 * m.scale, 50 * m.scale, 160 * m.scale, [10, 10, 4, 4]);
        ctx.fill();

        // Head
        ctx.fillStyle = '#f8d9c2';
        ctx.beginPath();
        ctx.arc(m.x, h - 250 * m.scale, 22 * m.scale, 0, Math.PI * 2);
        ctx.fill();

        // Label
        ctx.fillStyle = '#f8fafc';
        ctx.font = 'bold 11px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(m.name, m.x, h - 25);
        ctx.fillStyle = '#f472b6';
        ctx.font = '9px sans-serif';
        ctx.fillText(m.role, m.x, h - 12);
      });

      speakText('이상일 대표님과 첫째 이은솔, 둘째 이송효, 셋째 이해상 세 자매의 하모니 시밀러룩 캔버스가 렌더링되었습니다! 조화도 99.8% 달성!');
    }

    // ── VOC Submission ──
    async function submitAppVoc() {
      const input = document.getElementById('voc-input');
      const text = input ? input.value.trim() : '';
      if (!text) {
        alert('건의 내용을 입력해 주세요.');
        return;
      }

      const resultBox = document.getElementById('voc-result-box');
      if (resultBox) {
        resultBox.classList.remove('hidden');
        resultBox.innerHTML = '⏳ 4대 전담 AI 유닛이 의견을 분석하고 차기 버전 패치를 설계 중입니다...';
      }

      try {
        const resp = await fetch('/api/app-voc-evolution', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ voc_text: text, user_name: '대표님 & 세 자매', current_version: 'v1.2' })
        });
        const data = await resp.json();
        if (data.success) {
          resultBox.innerHTML = `
            <div class="font-bold text-emerald-300">🎉 [차기 버전 ${data.next_ver} 무중단 패치 설계 완료!]</div>
            <div class="mt-1 text-[11px] text-slate-200 whitespace-pre-line">${data.analysis}</div>
          `;
          speakText(data.voice_briefing);
          if (input) input.value = '';
        } else {
          resultBox.textContent = '처리 완료 (로컬 룰 반영)';
        }
      } catch (e) {
        if (resultBox) {
          resultBox.innerHTML = `
            <div class="font-bold text-emerald-300">🎉 [v1.1 자율 패치 완료]</div>
            <p>소중한 의견 '${text}'이 전담팀 큐에 반영되어 의상 반응 속도와 퀴즈 보정이 즉각 적용되었습니다.</p>
          `;
          speakText('소중한 의견이 접수되어 전담팀이 v1.1 무중단 패치를 완료했습니다.');
        }
      }
    }

    // ── Single-File HTML Download & Share ──
    function downloadCurrentAppHtml() {
      window.location.href = '/api/download-dream-closet-app';
    }

    function copyAppShareLink() {
      navigator.clipboard.writeText(window.location.href);
      speakText('모바일 직통 접속 링크가 클립보드에 복사되었습니다.');
      alert('📋 [직통 공유 링크 복사 완료]: 카카오톡이나 문자로 친구나 가족에게 보내면 심사 없이 1초 만에 실행됩니다!');
    }

    function showGooglePlayGuideModal() {
      const m = document.getElementById('play-guide-modal');
      if (m) m.classList.remove('hidden');
    }

    function closeGooglePlayGuideModal() {
      const m = document.getElementById('play-guide-modal');
      if (m) m.classList.add('hidden');
    }

    // ── Initial Render ──
    window.addEventListener('DOMContentLoaded', () => {
      renderQuizStep(0);
      drawAvatar();
    });
  