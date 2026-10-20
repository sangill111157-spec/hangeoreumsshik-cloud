
    // 4-7-8 호흡 타이머 시뮬레이션
    let breatheActive = true;
    let bStep = 0; // 0: inhale (4s), 1: hold (7s), 2: exhale (8s)
    let bSec = 4;
    const circle = document.getElementById('breathe-circle');
    const stateText = document.getElementById('breathe-state');
    const subText = document.getElementById('breathe-sub');
    const timerText = document.getElementById('breathe-timer');

    setInterval(() => {
      if (!breatheActive) return;
      bSec--;
      if (bSec <= 0) {
        bStep = (bStep + 1) % 3;
        if (bStep === 0) {
          bSec = 4;
          stateText.innerText = '들이쉬기 (4초)';
          subText.innerText = '코로 깊게 숨을 채웁니다';
        } else if (bStep === 1) {
          bSec = 7;
          stateText.innerText = '숨 멈추기 (7초)';
          subText.innerText = '몸 안의 평온을 가만히 느낍니다';
        } else {
          bSec = 8;
          stateText.innerText = '내쉬기 (8초)';
          subText.innerText = '입으로 천천히 모든 긴장을 비워냅니다';
        }
      }
      timerText.innerText = bSec;
    }, 1000);

    function toggleBreathing() {
      breatheActive = !breatheActive;
      const btn = document.getElementById('btn-breathe-toggle');
      if (breatheActive) {
        circle.style.animationPlayState = 'running';
        btn.innerText = '⏸️ 호흡 가이드 일시정지';
      } else {
        circle.style.animationPlayState = 'paused';
        btn.innerText = '▶️ 호흡 가이드 다시시작';
      }
    }

    // Web Audio API 순수 신디사이저 (외부 오디오 파일 없이 100% 자체 생성)
    let audioCtx = null;
    let osc = null;
    let gainNode = null;
    let isPlaying = false;
    let currentTrack = 'tone432';

    function initAudio() {
      if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        gainNode = audioCtx.createGain();
        gainNode.gain.value = 0.15;
        gainNode.connect(audioCtx.destination);
      }
    }

    function toggleAudio() {
      initAudio();
      if (isPlaying) {
        stopAudio();
      } else {
        startAudio();
      }
    }

    function startAudio() {
      if (!audioCtx) return;
      if (audioCtx.state === 'suspended') {
        audioCtx.resume();
      }
      
      stopAudio(); // 기존 정리

      if (currentTrack === 'tone432') {
        osc = audioCtx.createOscillator();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(432, audioCtx.currentTime); // 432Hz 치유 주파수
        osc.connect(gainNode);
        osc.start();
      } else {
        // 백색/핑크 노이즈 버퍼 합성 (비/바람 효과)
        const bufferSize = audioCtx.sampleRate * 2;
        const noiseBuffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
        const output = noiseBuffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
          output[i] = Math.random() * 2 - 1;
        }
        const whiteNoise = audioCtx.createBufferSource();
        whiteNoise.buffer = noiseBuffer;
        whiteNoise.loop = true;

        const filter = audioCtx.createBiquadFilter();
        filter.type = currentTrack === 'rain' ? 'lowpass' : 'bandpass';
        filter.frequency.value = currentTrack === 'rain' ? 800 : 400;

        whiteNoise.connect(filter);
        filter.connect(gainNode);
        whiteNoise.start();
        osc = whiteNoise;
      }

      isPlaying = true;
      document.getElementById('play-icon').innerText = '⏹️';
      document.getElementById('play-text').innerText = '소리 정지';
    }

    function stopAudio() {
      if (osc) {
        try { osc.stop(); } catch(e){}
        osc.disconnect();
        osc = null;
      }
      isPlaying = false;
      document.getElementById('play-icon').innerText = '▶️';
      document.getElementById('play-text').innerText = '소리 재생';
    }

    function selectTrack(track, btn) {
      currentTrack = track;
      document.querySelectorAll('.track-btn').forEach(b => {
        b.classList.remove('border-purple-500', 'text-purple-300', 'font-bold');
        b.classList.add('border-slate-700', 'text-slate-300');
      });
      btn.classList.add('border-purple-500', 'text-purple-300', 'font-bold');
      btn.classList.remove('border-slate-700', 'text-slate-300');

      if (isPlaying) {
        startAudio();
      }
    }

    function changeVolume(val) {
      if (gainNode) {
        gainNode.gain.setValueAtTime(parseFloat(val) * 0.3, audioCtx ? audioCtx.currentTime : 0);
      }
    }

    function shareHealingSound() {
      const text = `[한걸음씩 432Hz 마음휴식 호흡 가이드]\n깊은 숨 하나로 마음의 짐을 내려놓으세요 🍵\n※ 100% 무료 웰니스 사운드: ${window.location.href}`;
      if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
          alert('📋 힐링 사운드 링크가 복사되었습니다! 소중한 분의 편안한 쉼을 위해 나눠보세요.');
        });
      } else {
        alert(text);
      }
    }
  