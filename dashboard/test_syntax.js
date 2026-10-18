
    const STORAGE_KEYS = {
      GITHUB_TOKEN: 'hg_github_token',
      GEMINI_KEY: 'hg_gemini_key',
      TELEGRAM_TOKEN: 'hg_telegram_token',
      TELEGRAM_CHAT_ID: 'hg_telegram_chat_id',
      GITHUB_REPO: 'hg_github_repo'
    };

    const DEFAULT_REPO = 'sangill111157-spec/hangeoreumsshik-cloud';
    const TARGET_AUTUMN = new Date('2026-11-06T00:00:00+09:00').getTime();
    const TARGET_AFTERIMAGE = new Date('2026-11-27T00:00:00+09:00').getTime();

    let currentSunoChannel = 'hangeoreum';
    let currentVirtue = 'courtesy';
    let lastBrainAiResponseText = '';
    let speechRecognition = null;
    let isRecordingSpeech = false;
    let currentEpisodeData = null;
    let cachedVault = [];

    // ── 초기화 ──
    document.addEventListener('DOMContentLoaded', async () => {
      startClock();
      updateDDayCountdowns();
      setInterval(updateDDayCountdowns, 60000);

      await detectAndInjectLocalConfig();
      fetchWorkflowRuns(true);
      fetchSystemStatus();
      loadSunoFiles();
      loadMemoryVault();
      initThumbnailCanvas();

      // 시스템 상태 주기적 갱신
      setInterval(fetchSystemStatus, 15000);
      setInterval(() => fetchWorkflowRuns(true), 30000);
    });

    // ── 탭 전환 로직 ──
    function switchTab(tabId) {
      document.querySelectorAll('.tab-pane').forEach(el => el.classList.add('hidden'));
      const activePane = document.getElementById(tabId);
      if (activePane) activePane.classList.remove('hidden');

      // Update Nav buttons desktop
      document.querySelectorAll('.nav-tab-btn').forEach(btn => {
        btn.classList.remove('bg-emerald-500/10', 'text-emerald-300', 'border', 'border-emerald-500/30');
        btn.classList.add('text-slate-300');
      });
      const activeNav = document.getElementById('nav-' + tabId);
      if (activeNav) {
        activeNav.classList.add('bg-emerald-500/10', 'text-emerald-300', 'border', 'border-emerald-500/30');
        activeNav.classList.remove('text-slate-300');
      }

      // Update Mobile Tab
      document.querySelectorAll('.mob-tab-btn').forEach(btn => {
        btn.classList.replace('text-emerald-400', 'text-slate-400');
      });
      const activeMob = document.getElementById('mob-' + tabId);
      if (activeMob) activeMob.classList.replace('text-slate-400', 'text-emerald-400');

      const titles = {
        'tab-command': '🎛️ 1. 통합 관제 사령부',
        'tab-suno': '🎹 2. Suno & 비주얼 스튜디오',
        'tab-brain': '💬 3. AI 소통 & OSMU 개발실',
        'tab-daughters': '👨‍👧‍👧 4. 세 딸 인성 게임 연구소',
        'tab-vault': '🧠 5. 기억 금고 & 보안 설정'
      };
      document.getElementById('top-workspace-title').textContent = titles[tabId] || '사령부';
    }

    // ── 시스템 상태 조회 (NVDA, 디스크, 렌더러) ──
    async function fetchSystemStatus() {
      try {
        const resp = await fetch('/api/system-status');
        if (resp.ok) {
          const data = await resp.json();
          // NVDA Badge
          const nvdaBadge = document.getElementById('nvda-status-badge');
          if (data.nvda?.alive) {
            nvdaBadge.textContent = '● Online (8000)';
            nvdaBadge.className = 'px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/20 text-emerald-400 font-mono font-bold';
          } else {
            nvdaBadge.textContent = '○ Offline';
            nvdaBadge.className = 'px-2 py-0.5 rounded-full text-[10px] bg-slate-800 text-slate-500 font-mono';
          }

          // Disk Info
          if (data.disk) {
            document.getElementById('disk-free-text').textContent = `${data.disk.free_gb} GB (${data.disk.free_pct}%)`;
            document.getElementById('disk-free-bar').style.width = `${Math.min(100, data.disk.free_pct)}%`;
          }

          // Render Status Check
          if (data.render_status?.is_rendering) {
            document.getElementById('suno-render-banner').classList.remove('hidden');
            document.getElementById('suno-render-banner-text').textContent = data.render_status.message;
          } else {
            document.getElementById('suno-render-banner').classList.add('hidden');
          }
        }
      } catch (e) {}
    }

    // ── 시계 및 D-Day ──
    function startClock() {
      const clock = document.getElementById('sidebar-clock');
      function update() {
        const now = new Date();
        clock.textContent = now.toLocaleTimeString('ko-KR', {
          timeZone: 'Asia/Seoul', hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit'
        });
      }
      update();
      setInterval(update, 1000);
    }

    function updateDDayCountdowns() {
      const now = Date.now();
      calcDDay(TARGET_AUTUMN, 'dday-autumn-badge', 'dday-autumn-detail');
      calcDDay(TARGET_AFTERIMAGE, 'dday-afterimage-badge', 'dday-afterimage-detail');
    }

    function calcDDay(targetTime, badgeId, detailId) {
      const diff = targetTime - Date.now();
      const badge = document.getElementById(badgeId);
      const detail = document.getElementById(detailId);
      if (diff > 0) {
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        badge.textContent = `D-${days}`;
        detail.textContent = `${days}일 ${hours}시간 남음`;
      } else {
        badge.textContent = 'D-DAY / 발매됨!';
        badge.className = 'px-3 py-1 rounded-xl bg-amber-500/20 text-amber-300 font-extrabold font-mono text-sm border border-amber-500/40';
        detail.textContent = '현재 전세계 스트리밍 중 🎉';
      }
    }

    // ── 재정 헌법 계산기 (50:25:15:10) ──
    function calculateFinance() {
      const rev = Number(document.getElementById('calc-revenue-input').value) || 0;
      const home = Math.round(rev * 0.50);
      const reinvest = Math.round(rev * 0.25);
      const kids = Math.round(rev * 0.15);
      const donation = Math.round(rev * 0.10);

      document.getElementById('alloc-home').textContent = home.toLocaleString() + ' 원';
      document.getElementById('alloc-reinvest').textContent = reinvest.toLocaleString() + ' 원';
      document.getElementById('alloc-kids').textContent = kids.toLocaleString() + ' 원';
      document.getElementById('alloc-donation').textContent = donation.toLocaleString() + ' 원';
    }

    function copyFinanceReport() {
      const rev = Number(document.getElementById('calc-revenue-input').value) || 0;
      const text = `⚖️ [한걸음씩 신생국가 재정 헌법 배분 보고]\n\n• 총 수익: ${rev.toLocaleString()}원\n• 🏠 가정의 안식 (50%): ${(rev*0.5).toLocaleString()}원\n• ⚡ 시스템 재투자 (25%): ${(rev*0.25).toLocaleString()}원\n• 👨‍👧‍👧 세 딸 교육/자립 (15%): ${(rev*0.15).toLocaleString()}원\n• 🤝 선한 영향력 기부 (10%): ${(rev*0.1).toLocaleString()}원`;
      navigator.clipboard.writeText(text).then(() => showToast('📋 재정 배분 내역이 복사되었습니다!', 'success'));
    }

    async function sendFinanceToTelegram() {
      const rev = Number(document.getElementById('calc-revenue-input').value) || 0;
      const text = `⚖️ *[신생국가 재정 헌법 배분 보고]*\n\n• 총 수익금: *${rev.toLocaleString()}원*\n• 🏠 가정의 안식 (50%): ${(rev*0.5).toLocaleString()}원\n• ⚡ 시스템 재투자 (25%): ${(rev*0.25).toLocaleString()}원\n• 👨‍👧‍👧 세 딸 교육 (15%): ${(rev*0.15).toLocaleString()}원\n• 🤝 선한 기부 (10%): ${(rev*0.1).toLocaleString()}원\n\n_— 헌법 원칙에 따라 투명하게 자동 분배_`;
      const ok = await sendTelegramMessage(text);
      if (ok) showToast('📱 텔레그램으로 재정 보고가 발송되었습니다!', 'success');
    }

    // ── TAB 2: Suno 스튜디오 프롬프트 빌더 ──
    const SUNO_PRESETS = {
      hangeoreum: {
        title: "한걸음씩 (432Hz 수면 피아노)",
        defaultTheme: "비 내리는 밤 창가의 위로, 432Hz 고요한 피아노, 깊은 수면",
        stylePrompt: "calm 432hz acoustic solo piano, peaceful rainy ambient soundscape, emotional neoclassical melody, slow tempo 60bpm, gentle touch, deeply relaxing sleep music",
        structure: "[Intro - Soft Piano Drops]\n[Theme - Gentle Lullaby Melody]\n[Interlude - Quiet Rain Ambient]\n[Climax - Warm Emotional Harmony]\n[Outro - Slow Fading Note]",
        negative: "drums, percussion, brass, electric guitar, fast tempo, loud vocals, distorted synth",
        titles: ["비와 밤의 쉼표", "내일의 당신에게", "한걸음씩 쉬어가요"]
      },
      booster: {
        title: "부스터 플리 (출근길/에너지 로파이)",
        defaultTheme: "신나는 출근길, 활기찬 레트로 시티팝 로파이 비트, 딥포커스",
        stylePrompt: "upbeat lofi hip hop beat, chill synthwave groove, bright electric piano rhodes, smooth bassline, energetic coffee morning focus music 85bpm",
        structure: "[Intro - Vinyl Crackle & Rhodes]\n[Drop - Chill Lofi Groove]\n[Verse - Melodic Synth Melody]\n[Hook - Catchy Rhythm Loop]\n[Outro - Smooth Fade]",
        negative: "heavy metal distortion, screaming, gloomy slow tempo, acoustic guitar solo",
        titles: ["모닝 에스프레소 부스터", "출근길 푸른 신호등", "오늘도 원더풀"]
      },
      cafehour: {
        title: "카페 아워 (재즈/어쿠스틱)",
        defaultTheme: "오후 2시 따뜻한 햇살 창가, 어쿠스틱 기타와 부드러운 보사노바",
        stylePrompt: "warm acoustic guitar, gentle bossa nova jazz rhythm, upright double bass, cozy cafe background ambience, afternoon sunlight feel, relaxing 72bpm",
        structure: "[Intro - Fingerstyle Guitar]\n[A-Section - Bossa Nova Swing]\n[B-Section - Mellow Bass Walk]\n[Solo - Gentle Guitar Improvisation]\n[Outro - Soft Ending Chords]",
        negative: "synthesizer, autotune, heavy 808 drums, harsh noise, rap",
        titles: ["햇살이 머무는 테이블", "창가 자리 2시 15분", "따뜻한 바닐라 라떼"]
      },
      kidsgame: {
        title: "세 딸 인성게임 (힐링 오르골)",
        defaultTheme: "마음 편의점 과자 마을, 귀엽고 따뜻한 패밀리 타이쿤 BGM",
        stylePrompt: "cute magical music box celesta, warm acoustic marimba, playful strings pizzicato, cheerful family tycoon game soundtrack, whimsical and heartfelt melody 105bpm",
        structure: "[Intro - Cute Music Box Wind-up]\n[Theme A - Cheerful Bell Melody]\n[Theme B - Bouncing Pizzicato Strings]\n[Bridge - Whimsical Harp Flutter]\n[Outro - Sparkle Chime Ending]",
        negative: "horror sound, sad crying, dark heavy bass, aggressive drums",
        titles: ["마음 편의점의 하루", "세 자매의 보물상자", "우리가 함께 나누는 온기"]
      }
    };

    function selectSunoChannel(ch, btn) {
      currentSunoChannel = ch;
      document.querySelectorAll('.suno-channel-btn').forEach(b => {
        b.className = 'suno-channel-btn p-2 rounded-lg bg-slate-900 text-slate-300 border border-slate-800 text-left font-semibold text-xs';
      });
      btn.className = 'suno-channel-btn p-2 rounded-lg bg-emerald-950/60 text-emerald-300 border border-emerald-500/50 text-left font-semibold text-xs';
      document.getElementById('suno-theme-input').value = SUNO_PRESETS[ch].defaultTheme;
    }

    async function generateSunoPrompt() {
      const theme = document.getElementById('suno-theme-input').value.trim() || SUNO_PRESETS[currentSunoChannel].defaultTheme;
      const key = localStorage.getItem(STORAGE_KEYS.GEMINI_KEY);
      const container = document.getElementById('suno-prompt-results');
      const openBar = document.getElementById('suno-open-bar');

      container.innerHTML = `<div class="p-4 text-center text-slate-400">✨ Gemini AI가 Suno 황금 프롬프트 4종을 조율하고 있습니다...</div>`;

      if (!key) {
        renderSunoPromptCards(SUNO_PRESETS[currentSunoChannel]);
        openBar.classList.remove('hidden');
        showToast('로컬 프리셋 프롬프트가 로드되었습니다.', 'info');
        return;
      }

      try {
        const prompt = `당신은 Suno AI v3.5/v4 음악 프롬프트 최고 전문가입니다.
채널: ${SUNO_PRESETS[currentSunoChannel].title}
주제: ${theme}

아래 형식의 유효한 JSON으로만 답하세요 (마크다운 백틱 없이):
{
  "stylePrompt": "영문 120~200자 최적화 Style of music",
  "structure": "[Intro] [Verse] [Outro] 등 메타태그 구조",
  "negative": "제외할 악기 및 부정 프롬프트",
  "titles": ["추천 제목1", "추천 제목2", "추천 제목3"]
}`;
        const rawJson = await callGeminiApi('gemini-2.5-flash', key, prompt);
        const parsed = JSON.parse(rawJson.replace(/```json/g, '').replace(/```/g, '').trim());
        renderSunoPromptCards(parsed);
        openBar.classList.remove('hidden');
        showToast('🎵 Suno 황금 프롬프트가 완성되었습니다!', 'success');
      } catch (err) {
        console.warn('Gemini 프롬프트 생성 폴백:', err);
        renderSunoPromptCards(SUNO_PRESETS[currentSunoChannel]);
        openBar.classList.remove('hidden');
      }
    }

    function renderSunoPromptCards(data) {
      window.lastSunoStyle = data.stylePrompt;
      const container = document.getElementById('suno-prompt-results');
      container.innerHTML = `
        <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5">
          <div class="flex justify-between items-center text-slate-400 font-bold text-[11px]">
            <span>① Style of Music (영문 최적화)</span>
            <button onclick="copyText('${escapeQuotes(data.stylePrompt)}')" class="text-purple-400 hover:text-purple-300">📋 복사</button>
          </div>
          <p class="font-mono text-purple-200 text-xs bg-slate-950 p-2 rounded leading-relaxed">${escapeHtml(data.stylePrompt)}</p>
        </div>

        <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5">
          <div class="flex justify-between items-center text-slate-400 font-bold text-[11px]">
            <span>② 메타태그 구조 (Lyrics / Custom)</span>
            <button onclick="copyText('${escapeQuotes(data.structure)}')" class="text-cyan-400 hover:text-cyan-300">📋 복사</button>
          </div>
          <pre class="font-mono text-cyan-200 text-xs bg-slate-950 p-2 rounded whitespace-pre-wrap">${escapeHtml(data.structure)}</pre>
        </div>

        <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5">
          <div class="flex justify-between items-center text-slate-400 font-bold text-[11px]">
            <span>③ Negative Prompt (제외 악기)</span>
            <button onclick="copyText('${escapeQuotes(data.negative || '')}')" class="text-amber-400 hover:text-amber-300">📋 복사</button>
          </div>
          <p class="font-mono text-amber-200 text-xs bg-slate-950 p-2 rounded">${escapeHtml(data.negative || '')}</p>
        </div>

        <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5">
          <div class="flex justify-between items-center text-slate-400 font-bold text-[11px]">
            <span>④ 감성 곡 제목 추천 3선</span>
          </div>
          <div class="flex flex-wrap gap-1.5">
            ${(data.titles || []).map(t => `<button onclick="copyText('${escapeQuotes(t)}')" class="px-2.5 py-1 rounded bg-slate-950 hover:bg-slate-800 text-white font-medium border border-slate-800 flex items-center gap-1"><span>${escapeHtml(t)}</span><span class="text-slate-500">📋</span></button>`).join('')}
          </div>
        </div>
      `;
    }

    function copyStyleAndOpenSuno() {
      if (window.lastSunoStyle) {
        navigator.clipboard.writeText(window.lastSunoStyle).then(() => {
          showToast('📋 Style of Music 복사 완료! Suno.com으로 이동합니다.', 'success');
          window.open('https://suno.com/create', '_blank');
        });
      } else {
        window.open('https://suno.com/create', '_blank');
      }
    }

    // ── TAB 2: 로컬 오디오 스캔 및 스트리밍 플레이어 ──
    async function loadSunoFiles() {
      const select = document.getElementById('suno-file-select');
      try {
        const resp = await fetch('/api/suno-files');
        if (resp.ok) {
          const data = await resp.json();
          window.sunoAudioFiles = data.files || [];
          if (window.sunoAudioFiles.length === 0) {
            select.innerHTML = '<option value="">다운로드 폴더에 오디오 파일이 없습니다.</option>';
            return;
          }
          select.innerHTML = window.sunoAudioFiles.map((f, i) => `
            <option value="${escapeHtml(f.path)}">[${f.folder}] ${escapeHtml(f.name)} (${f.size_mb} MB - ${f.mtime_str})</option>
          `).join('');
          onSunoFileSelected();
        }
      } catch (e) {
        select.innerHTML = '<option value="">로컬 오디오 스캔 실패</option>';
      }
    }

    function onSunoFileSelected() {
      const select = document.getElementById('suno-file-select');
      const player = document.getElementById('dashboard-audio-player');
      const path = select.value;
      if (!path) return;

      const fileObj = (window.sunoAudioFiles || []).find(f => f.path === path);
      if (fileObj) {
        document.getElementById('player-file-name').textContent = fileObj.name;
        document.getElementById('player-file-size').textContent = `${fileObj.size_mb} MB (${fileObj.mtime_str})`;
        // 스트리밍 엔드포인트 연결
        player.src = `/api/audio?path=${encodeURIComponent(path)}`;
      }
    }

    async function launchSunoRender() {
      const select = document.getElementById('suno-file-select');
      const filePath = select.value;
      const hours = Number(document.getElementById('render-hours').value) || 8;
      const ambientVol = Number(document.getElementById('render-ambient-vol').value) || 0.25;
      const shortsText = document.getElementById('render-shorts-text').value.trim();

      if (!filePath) {
        showToast('렌더링할 오디오 파일을 선택하세요.', 'error');
        return;
      }

      const banner = document.getElementById('suno-render-banner');
      const bannerText = document.getElementById('suno-render-banner-text');
      banner.classList.remove('hidden');
      bannerText.textContent = `[${hours}시간 롱폼] 렌더링 백그라운드 엔진 가동 중...`;

      try {
        const resp = await fetch('/api/render-suno', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            file_path: filePath,
            hours: hours,
            ambient_vol: ambientVol,
            shorts_text: shortsText
          })
        });

        if (resp.ok) {
          const res = await resp.json();
          showToast(`🎬 ${res.message}`, 'success');
        } else {
          const err = await resp.json().catch(() => ({}));
          showToast(`오류: ${err.error || resp.statusText}`, 'error');
        }
      } catch (e) {
        showToast(`통신 오류: ${e.message}`, 'error');
      }
    }

    // ── TAB 2: Canvas Studio 실시간 썸네일 합성기 ──
    let thumbnailBgImage = new Image();
    thumbnailBgImage.crossOrigin = "anonymous";

    function initThumbnailCanvas() {
      thumbnailBgImage.onload = () => drawThumbnailCanvas();
      thumbnailBgImage.src = "https://images.unsplash.com/photo-1518495973542-4542c06a5843?q=80&w=1280&auto=format&fit=crop";
    }

    function generateAiThumbnailBg() {
      const prompt = document.getElementById('thumb-bg-prompt').value.trim();
      const btn = document.getElementById('btn-gen-bg');
      btn.textContent = '⏳ 배경 생성 중...';
      btn.disabled = true;

      const aiUrl = `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}?width=1280&height=720&nologo=true&seed=${Date.now()}`;
      const newImg = new Image();
      newImg.crossOrigin = "anonymous";
      newImg.onload = () => {
        thumbnailBgImage = newImg;
        drawThumbnailCanvas();
        btn.textContent = '✨ AI 배경 생성';
        btn.disabled = false;
        showToast('🖼️ 새로운 AI 감성 배경이 합성되었습니다!', 'success');
      };
      newImg.onerror = () => {
        btn.textContent = '✨ AI 배경 생성';
        btn.disabled = false;
        showToast('배경 생성 지연, 기본 배경을 유지합니다.', 'info');
      };
      newImg.src = aiUrl;
    }

    function drawThumbnailCanvas() {
      const canvas = document.getElementById('thumbnail-canvas');
      const ctx = canvas.getContext('2d');
      const mainTitle = document.getElementById('thumb-main-title').value || "오늘 하루도 참 고생 많으셨어요";
      const subTitle = document.getElementById('thumb-sub-title').value || "432Hz 힐링 피아노 · 깊은 수면";
      const dim = Number(document.getElementById('thumb-dim').value) || 0.45;

      // 1. Draw Background Image
      ctx.drawImage(thumbnailBgImage, 0, 0, canvas.width, canvas.height);

      // 2. Dark Vignette & Gradient Overlay
      const grad = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
      grad.addColorStop(0, `rgba(7, 10, 18, ${dim * 0.8})`);
      grad.addColorStop(0.5, `rgba(7, 10, 18, ${dim})`);
      grad.addColorStop(1, `rgba(7, 10, 18, ${dim * 1.2})`);
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // 3. Draw Vertical Text ('한걸음씩' 시그니처 세로 명조체)
      ctx.save();
      ctx.font = 'bold 52px "Nanum Myeongjo", serif';
      ctx.fillStyle = '#ffffff';
      ctx.shadowColor = 'rgba(0, 0, 0, 0.85)';
      ctx.shadowBlur = 16;
      ctx.shadowOffsetX = 3;
      ctx.shadowOffsetY = 3;

      const chars = mainTitle.split('');
      const startX = canvas.width - 200;
      let startY = 120;
      for (let ch of chars) {
        ctx.fillText(ch, startX, startY);
        startY += 62;
      }
      ctx.restore();

      // 4. Draw Channel Signature Badge
      ctx.save();
      ctx.font = 'bold 24px "Noto Sans KR", sans-serif';
      ctx.fillStyle = '#34d399';
      ctx.shadowColor = 'rgba(0, 0, 0, 0.9)';
      ctx.shadowBlur = 8;
      ctx.fillText('한걸음씩  ·  432Hz Healing', 80, 100);
      ctx.restore();

      // 5. Draw Horizontal Subtitle at Bottom
      ctx.save();
      ctx.font = '500 28px "Noto Sans KR", sans-serif';
      ctx.fillStyle = '#f1f5f9';
      ctx.shadowColor = 'rgba(0, 0, 0, 0.9)';
      ctx.shadowBlur = 10;
      ctx.fillText(subTitle, 80, canvas.height - 80);
      ctx.restore();
    }

    function downloadThumbnailPng() {
      const canvas = document.getElementById('thumbnail-canvas');
      const a = document.createElement('a');
      a.download = `hangeoreum_thumbnail_${Date.now()}.png`;
      a.href = canvas.toDataURL('image/png');
      a.click();
      showToast('💾 1280x720 고화질 썸네일이 다운로드되었습니다!', 'success');
    }

    function copyThumbnailToClipboard() {
      const canvas = document.getElementById('thumbnail-canvas');
      canvas.toBlob(blob => {
        const item = new ClipboardItem({ 'image/png': blob });
        navigator.clipboard.write([item]).then(() => {
          showToast('📋 썸네일 이미지가 클립보드에 복사되었습니다!', 'success');
        });
      });
    }

    // ── TAB 3: AI 소통 (음성인식 마이크 & 안실장 큐 & OSMU) ──
    function toggleVoiceRecognition() {
      const micBtn = document.getElementById('btn-voice-mic');
      const micIcon = document.getElementById('mic-icon');
      const inputEl = document.getElementById('brain-chat-input');

      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        showToast('이 브라우저는 음성 인식을 지원하지 않습니다. Chrome/Edge를 사용해 주세요.', 'error');
        return;
      }

      if (isRecordingSpeech) {
        speechRecognition.stop();
        isRecordingSpeech = false;
        micBtn.classList.remove('bg-red-600', 'animate-pulse');
        micIcon.textContent = '🎙️';
        showToast('음성 인식을 종료했습니다.', 'info');
        return;
      }

      speechRecognition = new SpeechRecognition();
      speechRecognition.lang = 'ko-KR';
      speechRecognition.interimResults = true;
      speechRecognition.continuous = false;

      speechRecognition.onstart = () => {
        isRecordingSpeech = true;
        micBtn.classList.add('bg-red-600', 'animate-pulse');
        micIcon.textContent = '🔴';
        showToast('🎙️ 듣고 있습니다... 말씀해 주세요!', 'info');
      };

      speechRecognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          transcript += event.results[i][0].transcript;
        }
        inputEl.value = transcript;
      };

      speechRecognition.onerror = (e) => {
        isRecordingSpeech = false;
        micBtn.classList.remove('bg-red-600', 'animate-pulse');
        micIcon.textContent = '🎙️';
        showToast(`음성 인식 오류: ${e.error}`, 'error');
      };

      speechRecognition.onend = () => {
        isRecordingSpeech = false;
        micBtn.classList.remove('bg-red-600', 'animate-pulse');
        micIcon.textContent = '🎙️';
      };

      speechRecognition.start();
    }

    async function sendBrainMessage() {
      const inputEl = document.getElementById('brain-chat-input');
      const text = inputEl.value.trim();
      if (!text) return;

      const key = localStorage.getItem(STORAGE_KEYS.GEMINI_KEY);
      if (!key) {
        showToast('Gemini API 키가 없습니다. [보안 설정]을 열어주세요.', 'error');
        openSettingsModal();
        return;
      }

      const chatBox = document.getElementById('brain-chat-box');
      const actionBar = document.getElementById('brain-action-bar');
      const btn = document.getElementById('btn-brain-send');

      // Add user bubble
      const uBubble = document.createElement('div');
      uBubble.className = 'p-3 rounded-xl bg-slate-800 text-white ml-6 text-xs';
      uBubble.innerHTML = `<span class="text-slate-400 font-bold block text-[10px] mb-1">🙋 대표님:</span>${escapeHtml(text).replace(/\n/g, '<br>')}`;
      chatBox.appendChild(uBubble);
      inputEl.value = '';
      chatBox.scrollTop = chatBox.scrollHeight;

      // Add AI bubble
      const aiBubble = document.createElement('div');
      aiBubble.className = 'p-3 rounded-xl bg-indigo-950/40 text-indigo-100 border border-indigo-500/30 mr-6 text-xs';
      aiBubble.innerHTML = `<span class="text-indigo-400 font-bold block text-[10px] mb-1">✨ 안실장 AI 사령탑:</span><span>생각 중...</span>`;
      chatBox.appendChild(aiBubble);
      chatBox.scrollTop = chatBox.scrollHeight;

      btn.disabled = true;

      try {
        const resp = await callGeminiApi('gemini-2.5-flash', key, text);
        lastBrainAiResponseText = resp;
        aiBubble.innerHTML = `
          <div class="flex justify-between items-center text-[10px] text-indigo-400 font-bold mb-1">
            <span>✨ 안실장 AI 사령탑</span>
            <span class="text-slate-500 font-normal">방금</span>
          </div>
          <div class="whitespace-pre-wrap leading-relaxed">${escapeHtml(resp)}</div>
        `;
        actionBar.classList.remove('hidden');
      } catch (e) {
        aiBubble.innerHTML = `<span class="text-red-400 text-xs">오류: ${escapeHtml(e.message)}</span>`;
      } finally {
        btn.disabled = false;
        chatBox.scrollTop = chatBox.scrollHeight;
      }
    }

    function clearBrainChat() {
      document.getElementById('brain-chat-box').innerHTML = `
        <div class="p-3 rounded-lg bg-indigo-950/40 border border-indigo-500/20 text-indigo-200">
          <p class="font-bold text-white mb-1">대화창이 비워졌습니다.</p>
        </div>
      `;
      document.getElementById('brain-action-bar').classList.add('hidden');
      lastBrainAiResponseText = '';
    }

    function copyLastBrainAiResponse() {
      if (lastBrainAiResponseText) {
        navigator.clipboard.writeText(lastBrainAiResponseText).then(() => showToast('📋 클립보드에 복사되었습니다!', 'success'));
      }
    }

    async function sendLastBrainResponseToTelegram() {
      if (!lastBrainAiResponseText) return;
      const ok = await sendTelegramMessage(`✨ *[사령부 AI 브리핑]*\n\n${lastBrainAiResponseText}`);
      if (ok) showToast('📱 텔레그램 전송 완료!', 'success');
    }

    async function dispatchLastBrainToAgentQueue() {
      if (!lastBrainAiResponseText) return;
      await dispatchTaskToAgent("AI 브리핑 기반 기획 지시", lastBrainAiResponseText, "AI소통");
    }

    async function submitDirectTaskToAgent() {
      const title = document.getElementById('direct-task-title').value.trim() || "대표님 직통 작업 지시";
      const body = document.getElementById('direct-task-body').value.trim();
      if (!body) {
        showToast('작업 지시 내용을 입력하세요.', 'error');
        return;
      }
      await dispatchTaskToAgent(title, body, "대표지시");
      document.getElementById('direct-task-title').value = '';
      document.getElementById('direct-task-body').value = '';
    }

    async function dispatchTaskToAgent(title, content, category) {
      try {
        const resp = await fetch('/api/dispatch-to-agent', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title, content, category })
        });
        if (resp.ok) {
          showToast('🤖 안실장 직통 큐(NEXT_TASK_FOR_ANTIGRAVITY.md)에 안전하게 등록되었습니다!', 'success');
          loadMemoryVault();
        } else {
          showToast('작업 등록 실패', 'error');
        }
      } catch (e) {
        showToast(`통신 오류: ${e.message}`, 'error');
      }
    }

    // ── OSMU 콘텐츠 생성 ──
    async function generateOsmuContent() {
      const topic = document.getElementById('osmu-topic-input').value.trim() || "432Hz 힐링 피아노와 불면증 극복";
      const key = localStorage.getItem(STORAGE_KEYS.GEMINI_KEY);
      const box = document.getElementById('osmu-result-box');
      box.classList.remove('hidden');
      box.textContent = "✍️ 네이버 블로그용 감성 원고와 유튜브 커뮤니티 투표 포스팅을 동시에 조율 중입니다...";

      if (!key) {
        showToast('Gemini API 키가 필요합니다.', 'error');
        return;
      }

      const prompt = `주제: ${topic}
당신은 최고 수준의 OSMU(One Source Multi Use) 콘텐츠 전략가입니다.
아래 두 가지 포스팅을 명확히 구분하여 작성해 주세요:

[1. 네이버/티스토리 감성 블로그 포스팅 원고]
- 검색 유입을 위한 제목 및 소제목 3개
- 지친 마음을 다독이는 따뜻한 본문 (공감 유도)
- 추천 해시태그 5개

[2. 유튜브 커뮤니티 투표 & 소통 포스팅]
- 구독자의 댓글 참여를 유도하는 질문과 따뜻한 인사
- 선택지 4개 (A, B, C, D) 투표 질문`;

      try {
        const res = await callGeminiApi('gemini-2.5-flash', key, prompt);
        box.textContent = res;
        showToast('OSMU 원고 작성이 완료되었습니다!', 'success');
      } catch (e) {
        box.textContent = `생성 실패: ${e.message}`;
      }
    }

    // ── TAB 4: 세 딸 인성 교육 게임 연구소 ──
    const DAUGHTER_PROFILES = {
      first: { name: "첫째 딸", grade: "중학교 3학년", focus: "진로 고민, 친구 관계의 깊이, 배려 있는 대화" },
      second: { name: "둘째 딸", grade: "중학교 1학년", focus: "사춘기 감정 조절, 어른 공경, 양보와 자존감" },
      third: { name: "셋째 딸", grade: "초등학교 5학년", focus: "약자 배려, 정직한 태도, 따뜻한 나눔" }
    };

    function selectVirtue(v, btn) {
      currentVirtue = v;
      document.querySelectorAll('.virtue-btn').forEach(b => {
        b.className = 'virtue-btn p-2 rounded-lg bg-slate-900 text-slate-300 border border-slate-800 font-semibold text-center text-xs';
      });
      btn.className = 'virtue-btn p-2 rounded-lg bg-pink-950/60 text-pink-300 border border-pink-500/50 font-semibold text-center text-xs';
    }

    async function generateGameEpisode() {
      const dKey = document.getElementById('game-target-daughter').value;
      const daughter = DAUGHTER_PROFILES[dKey];
      const key = localStorage.getItem(STORAGE_KEYS.GEMINI_KEY);
      const btn = document.getElementById('btn-gen-episode');

      btn.disabled = true;
      btn.textContent = '⏳ 에피소드 작성 중...';

      const prompt = `당신은 아동·청소년 인성 심리 게임 기획자입니다.
대상: ${daughter.name} (${daughter.grade})
중점 덕목: ${currentVirtue} (경우/어른공경/친구공감/나눔)
세계관: 〈마음 편의점 : 선택형 인성 밸런스 게임〉

반드시 아래 JSON 형식으로만 응답하세요 (마크다운 백틱 없이):
{
  "title": "에피소드 제목",
  "situation": "상황 제시문 (3~4문장, 현실적인 학교/가정 상황)",
  "choices": [
    {
      "id": 1,
      "text": "선택지 1 (약간 이기적이거나 섭섭한 선택)",
      "outcomeTitle": "나비효과 결과",
      "outcomeDesc": "상대방의 반응과 아쉬운 점",
      "heart": -5
    },
    {
      "id": 2,
      "text": "선택지 2 (무난하지만 아쉬운 선택)",
      "outcomeTitle": "나비효과 결과",
      "outcomeDesc": "상황이 해결되었으나 온기가 부족함",
      "heart": 5
    },
    {
      "id": 3,
      "text": "선택지 3 (진심 어린 배려와 지혜로운 선택)",
      "outcomeTitle": "최고의 나비효과!",
      "outcomeDesc": "상대방이 큰 감동을 받고 가족/친구의 온기가 번짐",
      "heart": 20
    }
  ]
}`;

      try {
        let resJson;
        if (key) {
          const raw = await callGeminiApi('gemini-2.5-flash', key, prompt);
          resJson = JSON.parse(raw.replace(/```json/g, '').replace(/```/g, '').trim());
        } else {
          // Fallback Sample Episode
          resJson = {
            title: "비 내리는 하굣길, 우산이 하나뿐일 때",
            situation: "방과 후 갑자기 소나기가 쏟아지는데, 옆 반 친구가 우산이 없어 발을 동동 구르고 있습니다. 내 가방에는 작은 2단 우산 하나만 있습니다. 학원 셔틀 시간은 10분 남았습니다.",
            choices: [
              { id: 1, text: "학원에 늦으면 안 되니 모르는 척 뛰어나간다.", outcomeTitle: "조금 무거워진 발걸음", outcomeDesc: "친구의 쓸쓸한 뒷모습이 마음에 걸려 학원 수업에 집중하기 어려웠습니다.", heart: -5 },
              { id: 2, text: "'너 우산 없어?' 물어만 보고 내 갈 길을 간다.", outcomeTitle: "어색한 위로", outcomeDesc: "친구에게 큰 도움이 되지 못해 아쉬움이 남았습니다.", heart: 5 },
              { id: 3, text: "'우리 학원 방향까지 같이 쓰고 가자!'며 어깨를 내어준다.", outcomeTitle: "따뜻한 우산 속 기적!", outcomeDesc: "비는 내렸지만 둘의 마음은 활짝 개었습니다. 친구가 다음날 따뜻한 메모와 간식을 건넸습니다.", heart: 20 }
            ]
          };
        }

        currentEpisodeData = resJson;
        renderGameSimulator(resJson);
        document.getElementById('btn-export-game').classList.remove('hidden');
        showToast('🎮 새로운 인성 게임 에피소드가 준비되었습니다!', 'success');
      } catch (e) {
        showToast(`에피소드 생성 오류: ${e.message}`, 'error');
      } finally {
        btn.disabled = false;
        btn.textContent = '🎮 새 에피소드 생성';
      }
    }

    function renderGameSimulator(ep) {
      document.getElementById('sim-title').textContent = ep.title;
      document.getElementById('sim-situation-box').textContent = ep.situation;
      document.getElementById('sim-outcome-box').classList.add('hidden');

      const container = document.getElementById('sim-choices-container');
      container.innerHTML = ep.choices.map((c, idx) => `
        <button onclick="pickChoice(${idx})"
          class="p-4 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-pink-500/60 text-left transition active:scale-[0.98] space-y-2">
          <div class="flex justify-between items-center text-[10px] text-pink-400 font-bold">
            <span>선택 ${c.id}</span>
            <span>+? Heart</span>
          </div>
          <p class="text-white font-medium text-xs leading-relaxed">${escapeHtml(c.text)}</p>
        </button>
      `).join('');
    }

    function pickChoice(idx) {
      if (!currentEpisodeData) return;
      const choice = currentEpisodeData.choices[idx];
      const outcomeBox = document.getElementById('sim-outcome-box');
      const ptsEl = document.getElementById('sim-warmth-points');
      
      let curPts = Number(ptsEl.textContent) || 100;
      curPts += choice.heart;
      ptsEl.textContent = curPts;

      document.getElementById('sim-outcome-title').textContent = `${choice.outcomeTitle} (${choice.heart >= 0 ? '+' : ''}${choice.heart} Heart)`;
      document.getElementById('sim-outcome-desc').textContent = choice.outcomeDesc;
      outcomeBox.classList.remove('hidden');
      outcomeBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function exportHeartGameHtml() {
      if (!currentEpisodeData) return;
      const tailwindTag = '<scr' + 'ipt src="https://cdn.tailwindcss.com"></scr' + 'ipt>';
      const htmlContent = '<!DOCTYPE html>\n' +
'<html lang="ko">\n' +
'<head>\n' +
'  <meta charset="UTF-8">\n' +
'  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n' +
'  <title>마음 편의점 | ' + escapeHtml(currentEpisodeData.title) + '</title>\n' +
'  ' + tailwindTag + '\n' +
'</head>\n' +
'<body class="bg-slate-950 text-slate-100 min-h-screen p-4 flex items-center justify-center font-sans">\n' +
'  <div class="max-w-md w-full bg-slate-900 p-6 rounded-3xl border border-pink-500/30 shadow-2xl space-y-5">\n' +
'    <div class="flex justify-between items-center">\n' +
'      <span class="text-2xl">🏪</span>\n' +
'      <span class="text-xs font-bold text-pink-400 bg-pink-950/60 px-3 py-1 rounded-full border border-pink-500/40">세 딸 인성 밸런스 게임</span>\n' +
'    </div>\n' +
'    <h2 class="text-lg font-bold text-white">' + escapeHtml(currentEpisodeData.title) + '</h2>\n' +
'    <div class="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 text-sm text-slate-300 leading-relaxed">\n' +
'      ' + escapeHtml(currentEpisodeData.situation) + '\n' +
'    </div>\n' +
'    <div class="space-y-3">\n' +
      currentEpisodeData.choices.map((c, i) =>
'        <button onclick="alert(\'' + escapeQuotes(c.outcomeTitle) + '\\n\\n' + escapeQuotes(c.outcomeDesc) + '\')" ' +
'          class="w-full p-4 rounded-2xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-left text-sm text-white font-medium transition">\n' +
'          <span class="text-xs text-pink-400 font-bold block mb-1">선택지 ' + c.id + '</span>\n' +
'          ' + escapeHtml(c.text) + '\n' +
'        </button>'
      ).join('\n') + '\n' +
'    </div>\n' +
'    <p class="text-[11px] text-center text-slate-500">사랑하는 아빠가 세 딸을 위해 만든 마음 편의점 💕</p>\n' +
'  </div>\n' +
'</body>\n' +
'</html>';

      const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
      const a = document.createElement('a');
      a.download = `heart_game_${Date.now()}.html`;
      a.href = URL.createObjectURL(blob);
      a.click();
      showToast('📲 스마트폰 단독 실행용 웹게임(.html)이 저장되었습니다!', 'success');
    }

    // ── TAB 5: 기억 금고 & 보안 설정 ──
    async function loadMemoryVault() {
      const container = document.getElementById('vault-memories-list');
      try {
        const resp = await fetch('/api/memory-vault');
        if (resp.ok) {
          const data = await resp.json();
          cachedVault = data.memories || [];
          renderVaultList(cachedVault);
        }
      } catch (e) {
        container.innerHTML = '<div class="text-center py-4">기억 금고 로드 실패</div>';
      }

      // Populate credentials
      document.getElementById('vault-gh-token').value = localStorage.getItem(STORAGE_KEYS.GITHUB_TOKEN) || '';
      document.getElementById('vault-gemini-key').value = localStorage.getItem(STORAGE_KEYS.GEMINI_KEY) || '';
      document.getElementById('vault-tg-token').value = localStorage.getItem(STORAGE_KEYS.TELEGRAM_TOKEN) || '';
      document.getElementById('vault-tg-chat-id').value = localStorage.getItem(STORAGE_KEYS.TELEGRAM_CHAT_ID) || '';
    }

    function renderVaultList(list) {
      const container = document.getElementById('vault-memories-list');
      if (list.length === 0) {
        container.innerHTML = '<div class="text-center py-6 text-slate-500">저장된 기억이 없습니다.</div>';
        return;
      }
      container.innerHTML = list.map(item => `
        <div class="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5 hover:border-slate-700 transition">
          <div class="flex justify-between items-center">
            <span class="font-bold text-white text-xs">${escapeHtml(item.title)}</span>
            <span class="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">${escapeHtml(item.category || '기억')} · ${escapeHtml(item.timestamp || '')}</span>
          </div>
          <p class="text-slate-300 text-xs whitespace-pre-wrap">${escapeHtml(item.content)}</p>
        </div>
      `).join('');
    }

    function filterVaultMemories() {
      const q = document.getElementById('vault-search-input').value.toLowerCase();
      const filtered = cachedVault.filter(m => (m.title + m.content).toLowerCase().includes(q));
      renderVaultList(filtered);
    }

    function saveVaultSettings() {
      const gh = document.getElementById('vault-gh-token').value.trim();
      const gem = document.getElementById('vault-gemini-key').value.trim();
      const tg = document.getElementById('vault-tg-token').value.trim();
      const chat = document.getElementById('vault-tg-chat-id').value.trim();

      if (gh) localStorage.setItem(STORAGE_KEYS.GITHUB_TOKEN, gh);
      if (gem) localStorage.setItem(STORAGE_KEYS.GEMINI_KEY, gem);
      if (tg) localStorage.setItem(STORAGE_KEYS.TELEGRAM_TOKEN, tg);
      if (chat) localStorage.setItem(STORAGE_KEYS.TELEGRAM_CHAT_ID, chat);

      showToast('🔒 보안 연결 설정이 브라우저 금고에 저장되었습니다!', 'success');
      fetchWorkflowRuns(true);
    }

    // ── GITHUB ACTIONS DISPATCH & RUNS ──
    async function dispatchWorkflow(cmd, name) {
      const token = localStorage.getItem(STORAGE_KEYS.GITHUB_TOKEN);
      const repo = localStorage.getItem(STORAGE_KEYS.GITHUB_REPO) || DEFAULT_REPO;

      if (!token) {
        showToast('GitHub 토큰이 필요합니다. 보안 설정을 열어주세요.', 'error');
        openSettingsModal();
        return;
      }

      const banner = document.getElementById('dispatch-banner');
      const bText = document.getElementById('dispatch-banner-text');
      banner.classList.remove('hidden');
      bText.textContent = `[${name}] 클라우드 러너 가동 요청 중...`;

      try {
        const resp = await fetch(`https://api.github.com/repos/${repo}/actions/workflows/hangeoreumsshik_cloud.yml/dispatches`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ ref: 'main', inputs: { command: cmd } })
        });

        if (resp.status === 204) {
          showToast(`🚀 [${name}] 클라우드 발사 성공!`, 'success');
          bText.textContent = `🚀 [${name}] 러너 가동 시작! 상태를 추적합니다...`;
          setTimeout(() => {
            fetchWorkflowRuns(true);
            banner.classList.add('hidden');
          }, 6000);
        } else {
          showToast(`발사 실패 (${resp.status})`, 'error');
          banner.classList.add('hidden');
        }
      } catch (e) {
        showToast(`통신 오류: ${e.message}`, 'error');
        banner.classList.add('hidden');
      }
    }

    async function fetchWorkflowRuns(silent = false) {
      const token = localStorage.getItem(STORAGE_KEYS.GITHUB_TOKEN);
      const repo = localStorage.getItem(STORAGE_KEYS.GITHUB_REPO) || DEFAULT_REPO;
      const container = document.getElementById('runs-list-container');
      if (!token) {
        container.innerHTML = '<div class="py-4 text-center">GitHub 토큰을 등록해주세요.</div>';
        return;
      }

      try {
        const resp = await fetch(`https://api.github.com/repos/${repo}/actions/runs?per_page=5`, {
          headers: { 'Authorization': `Bearer ${token}`, 'Accept': 'application/vnd.github.v3+json' }
        });
        if (resp.ok) {
          const data = await resp.json();
          const runs = data.workflow_runs || [];
          if (runs.length === 0) {
            container.innerHTML = '<div class="py-4 text-center text-slate-500">실행 내역이 없습니다.</div>';
            return;
          }
          container.innerHTML = runs.map(r => {
            let badge = 'bg-slate-700 text-slate-300';
            if (r.status === 'in_progress') badge = 'bg-amber-500/20 text-amber-300 animate-pulse';
            else if (r.conclusion === 'success') badge = 'bg-emerald-500/20 text-emerald-300';
            else if (r.conclusion === 'failure') badge = 'bg-red-500/20 text-red-300';

            return `
              <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                <div>
                  <div class="font-bold text-white flex items-center gap-2">
                    <span>${escapeHtml(r.name || 'Pipeline')}</span>
                    <span class="text-[10px] text-slate-500">#${r.run_number}</span>
                  </div>
                  <div class="text-[10px] text-slate-400 mt-0.5">${new Date(r.created_at).toLocaleString('ko-KR')}</div>
                </div>
                <div class="flex items-center gap-2">
                  <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${badge}">${r.conclusion || r.status}</span>
                  <a href="${r.html_url}" target="_blank" rel="noopener" class="text-slate-400 hover:text-white">↗</a>
                </div>
              </div>
            `;
          }).join('');
        }
      } catch (e) {}
    }

    // ── CONFIG AUTO-INJECT ──
    async function detectAndInjectLocalConfig() {
      try {
        const resp = await fetch('/api/config');
        if (resp.ok) {
          const cfg = await resp.json();
          if (cfg.github_token && !localStorage.getItem(STORAGE_KEYS.GITHUB_TOKEN)) localStorage.setItem(STORAGE_KEYS.GITHUB_TOKEN, cfg.github_token);
          if (cfg.gemini_key && !localStorage.getItem(STORAGE_KEYS.GEMINI_KEY)) localStorage.setItem(STORAGE_KEYS.GEMINI_KEY, cfg.gemini_key);
          if (cfg.telegram_token && !localStorage.getItem(STORAGE_KEYS.TELEGRAM_TOKEN)) localStorage.setItem(STORAGE_KEYS.TELEGRAM_TOKEN, cfg.telegram_token);
          if (cfg.telegram_chat_id && !localStorage.getItem(STORAGE_KEYS.TELEGRAM_CHAT_ID)) localStorage.setItem(STORAGE_KEYS.TELEGRAM_CHAT_ID, cfg.telegram_chat_id);
          if (cfg.repo) localStorage.setItem(STORAGE_KEYS.GITHUB_REPO, cfg.repo);
        }
      } catch (e) {}
    }

    // ── GEMINI & TELEGRAM UTILS ──
    async function callGeminiApi(model, key, prompt) {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${key}`;
      const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] })
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      return data.candidates?.[0]?.content?.parts?.[0]?.text || '';
    }

    async function sendTelegramMessage(text) {
      const tok = localStorage.getItem(STORAGE_KEYS.TELEGRAM_TOKEN);
      const chat = localStorage.getItem(STORAGE_KEYS.TELEGRAM_CHAT_ID);
      if (!tok || !chat) {
        showToast('텔레그램 설정이 필요합니다.', 'error');
        return false;
      }
      try {
        const resp = await fetch(`https://api.telegram.org/bot${tok}/sendMessage`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ chat_id: chat, text: text, parse_mode: 'Markdown' })
        });
        return resp.ok;
      } catch (e) {
        return false;
      }
    }

    // ── MODAL SETTINGS ──
    function openSettingsModal() {
      document.getElementById('modal-gh-token').value = localStorage.getItem(STORAGE_KEYS.GITHUB_TOKEN) || '';
      document.getElementById('modal-gemini-key').value = localStorage.getItem(STORAGE_KEYS.GEMINI_KEY) || '';
      document.getElementById('modal-tg-token').value = localStorage.getItem(STORAGE_KEYS.TELEGRAM_TOKEN) || '';
      document.getElementById('modal-tg-chat-id').value = localStorage.getItem(STORAGE_KEYS.TELEGRAM_CHAT_ID) || '';
      document.getElementById('settings-modal').classList.remove('hidden');
    }

    function closeSettingsModal() {
      document.getElementById('settings-modal').classList.add('hidden');
    }

    function saveModalSettings() {
      const gh = document.getElementById('modal-gh-token').value.trim();
      const gem = document.getElementById('modal-gemini-key').value.trim();
      const tg = document.getElementById('modal-tg-token').value.trim();
      const chat = document.getElementById('modal-tg-chat-id').value.trim();
      if (gh) localStorage.setItem(STORAGE_KEYS.GITHUB_TOKEN, gh);
      if (gem) localStorage.setItem(STORAGE_KEYS.GEMINI_KEY, gem);
      if (tg) localStorage.setItem(STORAGE_KEYS.TELEGRAM_TOKEN, tg);
      if (chat) localStorage.setItem(STORAGE_KEYS.TELEGRAM_CHAT_ID, chat);
      closeSettingsModal();
      showToast('보안 설정이 저장되었습니다!', 'success');
      fetchWorkflowRuns(true);
    }

    // ── GENERAL UTILS ──
    function refreshAll() {
      fetchWorkflowRuns();
      fetchSystemStatus();
      loadSunoFiles();
      loadMemoryVault();
      showToast('모든 데이터가 새로고침되었습니다.', 'info');
    }

    function copyText(str) {
      navigator.clipboard.writeText(str).then(() => showToast('📋 복사되었습니다!', 'success'));
    }

    function showToast(msg, type = 'info') {
      const c = document.getElementById('toast-container');
      const t = document.createElement('div');
      let bg = 'bg-slate-900 border-slate-700 text-slate-200';
      if (type === 'success') bg = 'bg-emerald-950 border-emerald-500/50 text-emerald-200';
      if (type === 'error') bg = 'bg-red-950 border-red-500/50 text-red-200';
      t.className = `p-3 rounded-xl border shadow-2xl text-xs flex items-center gap-2 pointer-events-auto transition transform translate-y-2 opacity-0 ${bg}`;
      t.innerHTML = `<span>${escapeHtml(msg)}</span>`;
      c.appendChild(t);
      requestAnimationFrame(() => t.classList.remove('translate-y-2', 'opacity-0'));
      setTimeout(() => {
        t.classList.add('opacity-0');
        setTimeout(() => t.remove(), 300);
      }, 4000);
    }

    function escapeHtml(s) {
      if (!s) return '';
      return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }
    function escapeQuotes(s) {
      if (!s) return '';
      return String(s).replace(/'/g, "\\'").replace(/"/g, '\\"').replace(/\n/g, '\\n');
    }
  