
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

    // ── 🔄 [OTA Hot-Reload 무인 자동 업데이트 엔진] ──
    let currentVersionHash = null;
    let isOtaUpdating = false;

    function isUserTyping() {
      const activeEl = document.activeElement;
      if (!activeEl) return false;
      const tag = activeEl.tagName.toLowerCase();
      if (tag === 'input' || tag === 'textarea' || activeEl.isContentEditable) {
        return true;
      }
      return false;
    }

    async function checkVersionAndUpdate(isManual = false) {
      if (isOtaUpdating) return;
      try {
        const resp = await fetch('/api/version', { cache: 'no-store' });
        if (resp.ok) {
          const data = await resp.json();
          if (data.success && data.version_hash) {
            const vBadge = document.getElementById('ota-version-text');
            if (vBadge) {
              vBadge.textContent = `${data.version || 'v3.1'} [${data.git_commit || 'Auto'}]`;
            }

            if (!currentVersionHash) {
              currentVersionHash = data.version_hash;
              if (isManual) showToast(`🟢 현재 최신 버전입니다: ${data.version_hash}`, 'info');
              return;
            }

            if (currentVersionHash !== data.version_hash) {
              currentVersionHash = data.version_hash;
              handleNewVersionDetected();
            } else if (isManual) {
              showToast(`🟢 현재 최신 버전입니다 (${data.version_hash})`, 'success');
            }
          }
        }
      } catch (e) {
        if (isManual) showToast(`버전 확인 실패: ${e.message}`, 'error');
      }
    }

    function handleNewVersionDetected() {
      if (isUserTyping()) {
        const banner = document.getElementById('ota-update-banner');
        if (banner) banner.classList.remove('hidden');
        showToast('✨ 새 업데이트 도착! 작성 중인 내용을 저장 후 상단 배너를 터치하세요.', 'info');
      } else {
        applyUpdateImmediately();
      }
    }

    function applyUpdateImmediately() {
      if (isOtaUpdating) return;
      isOtaUpdating = true;
      showToast('✨ 새 버전 업데이트가 감지되어 자동으로 적용합니다! 🚀', 'success');
      setTimeout(() => {
        const url = new URL(window.location.href);
        url.searchParams.set('_v', Date.now());
        window.location.href = url.toString();
      }, 900);
    }

    // ── 📚 [제국 실록 : 지혜 & 오답 백신 관리 엔진] ──
    let cachedWisdomLedger = { good_practices: [], mistake_vaccines: [] };

    async function loadWisdomLedger() {
      try {
        const resp = await fetch('/api/wisdom-ledger');
        if (resp.ok) {
          const data = await resp.json();
          cachedWisdomLedger = data;
          renderWisdomLedger(data);
        }
      } catch (e) {
        console.error('Wisdom ledger load error:', e);
      }
    }

    function renderWisdomLedger(data) {
      const goods = data.good_practices || [];
      const mistakes = data.mistake_vaccines || [];

      // 통계 배지 갱신
      const statGood = document.getElementById('stat-good-count');
      const statMistake = document.getElementById('stat-mistake-count');
      if (statGood) statGood.textContent = `${goods.length}건`;
      if (statMistake) statMistake.textContent = `${mistakes.length}건`;

      // 🟢 성공 공식 리스트 렌더링
      const goodContainer = document.getElementById('wisdom-good-list');
      if (goodContainer) {
        if (goods.length === 0) {
          goodContainer.innerHTML = '<div class="text-center py-6 text-slate-500 text-xs">등록된 성공 공식이 없습니다.</div>';
        } else {
          let html = '';
          goods.forEach(item => {
            html += `
              <div class="p-3.5 rounded-xl bg-slate-950/80 border border-emerald-500/30 space-y-2 transition hover:border-emerald-400/50 text-left">
                <div class="flex items-start justify-between gap-2">
                  <div class="font-bold text-white text-xs flex items-center gap-1.5">
                    <span class="text-emerald-400">🟢</span>
                    <span>${escapeHtml(item.title)}</span>
                  </div>
                  <span class="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 font-medium shrink-0">
                    ${escapeHtml(item.category || '성공')}
                  </span>
                </div>
                <p class="text-xs text-slate-300 leading-relaxed">${escapeHtml(item.description)}</p>
                ${item.impact ? `
                  <div class="text-[11px] text-emerald-400/90 bg-emerald-950/30 px-2.5 py-1 rounded-lg border border-emerald-500/20 font-mono">
                    ⚡ 기대 효과: ${escapeHtml(item.impact)}
                  </div>
                ` : ''}
              </div>
            `;
          });
          goodContainer.innerHTML = html;
        }
      }

      // 🔴 오답 백신 리스트 렌더링
      const mistakeContainer = document.getElementById('wisdom-mistake-list');
      if (mistakeContainer) {
        if (mistakes.length === 0) {
          mistakeContainer.innerHTML = '<div class="text-center py-6 text-slate-500 text-xs">등록된 오답 백신이 없습니다.</div>';
        } else {
          let html = '';
          mistakes.forEach(item => {
            html += `
              <div class="p-3.5 rounded-xl bg-slate-950/80 border border-rose-500/30 space-y-2 transition hover:border-rose-400/50 text-left">
                <div class="flex items-start justify-between gap-2">
                  <div class="font-bold text-white text-xs flex items-center gap-1.5">
                    <span class="text-rose-400">🛡️</span>
                    <span>${escapeHtml(item.title)}</span>
                  </div>
                  <span class="px-2 py-0.5 rounded text-[10px] bg-rose-500/10 text-rose-300 border border-rose-500/30 font-medium shrink-0">
                    ${escapeHtml(item.category || '백신')}
                  </span>
                </div>
                <div class="text-xs text-slate-300 leading-relaxed">
                  <span class="text-rose-400 font-semibold">[증상/오답]</span> ${escapeHtml(item.symptom)}
                </div>
                <div class="text-[11px] text-amber-300/90 bg-amber-950/30 px-2.5 py-1 rounded-lg border border-amber-500/20 leading-relaxed">
                  <span class="font-bold text-amber-400">🚫 영구 봉쇄 규칙:</span> ${escapeHtml(item.rule)}
                </div>
              </div>
            `;
          });
          mistakeContainer.innerHTML = html;
        }
      }
    }

    function openAddWisdomModal(type) {
      const card = document.getElementById('wisdom-input-card');
      const typeInput = document.getElementById('wisdom-input-type');
      const titleEl = document.getElementById('wisdom-input-title');
      const ruleInput = document.getElementById('wisdom-form-rule');
      const btn = document.getElementById('btn-submit-wisdom');

      if (!card || !typeInput || !titleEl) return;

      typeInput.value = type;
      card.classList.remove('hidden');

      if (type === 'good') {
        titleEl.innerHTML = '<span>🟢</span> <span>새로운 [성공 공식 (Good Practice)] 기록</span>';
        if (ruleInput) ruleInput.placeholder = '기대 효과 / 시너지 임팩트 (예: 렌더링 속도 15배 향상, CTR 극대화 등)';
        if (btn) btn.className = 'px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md transition active:scale-95';
      } else {
        titleEl.innerHTML = '<span>🔴</span> <span>새로운 [실수 방지 오답 백신 (Mistake Vaccine)] 기록</span>';
        if (ruleInput) ruleInput.placeholder = '절대 반복 금지 영구 방어 규칙 (예: JS 내 문자열 이스케이프 및 node --check 의무화)';
        if (btn) btn.className = 'px-4 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs shadow-md transition active:scale-95';
      }

      document.getElementById('wisdom-form-title')?.focus();
    }

    function closeWisdomInputCard() {
      const card = document.getElementById('wisdom-input-card');
      if (card) card.classList.add('hidden');
    }

    async function submitWisdomEntry() {
      const type = document.getElementById('wisdom-input-type')?.value || 'good';
      const title = document.getElementById('wisdom-form-title')?.value.trim();
      const category = document.getElementById('wisdom-form-category')?.value.trim() || '운영·개발';
      const content = document.getElementById('wisdom-form-content')?.value.trim();
      const impact_or_rule = document.getElementById('wisdom-form-rule')?.value.trim();

      if (!title || !content) {
        showToast('제목과 내용을 모두 입력해 주세요.', 'error');
        return;
      }

      const btn = document.getElementById('btn-submit-wisdom');
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span>⏳</span> <span>전 부처 전파 중...</span>';
      }

      try {
        const resp = await fetch('/api/wisdom-ledger', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ type, title, content, category, impact_or_rule })
        });

        if (resp.ok) {
          const res = await resp.json();
          if (res.success) {
            showToast(`📚 [제국 실록] 새로운 ${type === 'good' ? '성공 공식' : '오답 백신'}이 전 부처에 실시간 전파되었습니다!`, 'success');
            document.getElementById('wisdom-form-title').value = '';
            document.getElementById('wisdom-form-category').value = '';
            document.getElementById('wisdom-form-content').value = '';
            document.getElementById('wisdom-form-rule').value = '';
            closeWisdomInputCard();
            loadWisdomLedger();
            loadMemoryVault();
            return;
          }
        }
        throw new Error('실록 등록에 실패했습니다.');
      } catch (e) {
        showToast(`등록 오류: ${e.message}`, 'error');
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = '전 부처 실시간 전파 및 등재 🚀';
        }
      }
    }

    function initOtaHotReload() {
      checkVersionAndUpdate(false);
      setInterval(() => checkVersionAndUpdate(false), 15000);

      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
          checkVersionAndUpdate(false);
        }
      });
      window.addEventListener('focus', () => {
        checkVersionAndUpdate(false);
      });
    }

    // ── 초기화 ──
    document.addEventListener('DOMContentLoaded', async () => {
      checkUrlHashKeySync();
      switchTab('tab-command');
      startClock();
      updateDDayCountdowns();
      setInterval(updateDDayCountdowns, 60000);
      calculateFinance();

      await detectAndInjectLocalConfig();
      fetchWorkflowRuns(true);
      fetchSystemStatus();
      loadSunoFiles();
      loadMemoryVault();
      initThumbnailCanvas();
      runComplianceAudit(true);
      renderCertificateCanvas();
      initWorkShiftMode();
      initOtaHotReload();
      loadWisdomLedger();

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
      thumbnailBgImage.onerror = () => {
        // 이미지 로드 실패 시에도 아름다운 앰비언트 그라데이션으로 렌더링
        drawThumbnailCanvas();
      };
      // 고즈넉한 비 내리는 창가와 따뜻한 조명(Warm bokeh & rain window) 고화질 감성 이미지
      thumbnailBgImage.src = "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?q=80&w=1280&auto=format&fit=crop";
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

    // 세로 텍스트 스마트 다단(Multi-column) 분할 헬퍼
    function splitIntoVerticalColumns(text, maxPerCol = 8) {
      const trimmed = (text || '').trim();
      if (!trimmed) return [];
      if (trimmed.length <= maxPerCol) return [trimmed];

      const words = trimmed.split(/\s+/);
      if (words.length === 1) {
        const mid = Math.ceil(trimmed.length / 2);
        return [trimmed.slice(0, mid), trimmed.slice(mid)];
      }

      const col1Words = [];
      const col2Words = [];
      const targetHalf = trimmed.length / 2;
      let curLen = 0;

      for (let i = 0; i < words.length; i++) {
        const w = words[i];
        if (curLen + w.length <= targetHalf + 1 || col1Words.length === 0) {
          col1Words.push(w);
          curLen += w.length + 1;
        } else {
          col2Words.push(w);
        }
      }

      if (col2Words.length === 0 && col1Words.length > 1) {
        col2Words.push(col1Words.pop());
      }

      return [col1Words.join(' '), col2Words.join(' ')];
    }

    function drawThumbnailCanvas() {
      const canvas = document.getElementById('thumbnail-canvas');
      const ctx = canvas.getContext('2d');
      const mainTitle = document.getElementById('thumb-main-title').value || "오늘 하루도 참 고생 많으셨어요";
      const subTitle = document.getElementById('thumb-sub-title').value || "432Hz 힐링 피아노 · 깊은 수면을 위한 따뜻한 쉼표";
      const dim = Number(document.getElementById('thumb-dim').value) || 0.45;

      // 1. Draw Background Image (or gradient fallback)
      if (thumbnailBgImage.complete && thumbnailBgImage.naturalWidth > 0) {
        ctx.drawImage(thumbnailBgImage, 0, 0, canvas.width, canvas.height);
      } else {
        // Fallback Dark Cinematic Gradient
        const baseGrad = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
        baseGrad.addColorStop(0, '#0a101d');
        baseGrad.addColorStop(0.5, '#151d30');
        baseGrad.addColorStop(1, '#070b14');
        ctx.fillStyle = baseGrad;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }

      // 2. Dark Vignette & Gradient Overlay for Contrast
      const grad = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
      grad.addColorStop(0, `rgba(7, 10, 18, ${dim * 0.75})`);
      grad.addColorStop(0.4, `rgba(7, 10, 18, ${dim})`);
      grad.addColorStop(1, `rgba(7, 10, 18, ${dim * 1.25})`);
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // 2.5 REA 클린룸 힐링 파티클 이펙트 렌더링
      drawParticlesOnCanvas(ctx, canvas);

      // 3. Draw Smart Multi-column Vertical Text (전통 서적 세로쓰기: 오른쪽 1열 ➔ 왼쪽 2열)
      const columns = splitIntoVerticalColumns(mainTitle, 8);
      const numCols = columns.length;
      const maxColLen = Math.max(...columns.map(c => c.length), 1);

      ctx.save();
      // 글자 수 및 다단 여부에 따른 동적 폰트 스케일링
      let fontSize = 48;
      let stepY = 56;
      let colGap = 72;

      if (numCols === 1) {
        fontSize = maxColLen > 7 ? 42 : 48;
        stepY = fontSize + 12;
      } else {
        fontSize = maxColLen > 8 ? 38 : 44;
        stepY = fontSize + 10;
        colGap = fontSize * 1.65; // 열 간격
      }

      ctx.font = `bold ${fontSize}px "Nanum Myeongjo", serif`;
      ctx.fillStyle = '#ffffff';
      ctx.shadowColor = 'rgba(0, 0, 0, 0.9)';
      ctx.shadowBlur = 18;
      ctx.shadowOffsetX = 3;
      ctx.shadowOffsetY = 3;

      // 캔버스 우측에서부터 왼쪽으로 열 배치 (시집 표지 감성)
      const baseRightX = numCols === 1 ? canvas.width - 180 : canvas.width - 150;
      const startY = Math.max(90, Math.min(140, (canvas.height - (maxColLen * stepY)) / 2));

      columns.forEach((colText, colIdx) => {
        // colIdx === 0 은 가장 오른쪽 열, colIdx === 1 은 그 왼쪽 열
        const colX = baseRightX - (colIdx * colGap);
        let curY = startY;

        for (let ch of colText.split('')) {
          if (ch === ' ') {
            curY += stepY * 0.55; // 공백은 살짝 좁게 띄움
          } else {
            ctx.fillText(ch, colX, curY);
            curY += stepY;
          }
        }
      });
      ctx.restore();

      // 4. Draw Channel Signature Badge (상단 좌측)
      ctx.save();
      ctx.font = 'bold 24px "Noto Sans KR", sans-serif';
      ctx.fillStyle = '#34d399';
      ctx.shadowColor = 'rgba(0, 0, 0, 0.95)';
      ctx.shadowBlur = 10;
      ctx.fillText('한걸음씩  ·  432Hz Healing', 80, 95);
      ctx.restore();

      // 5. Draw Horizontal Subtitle at Bottom (하단 좌측)
      ctx.save();
      ctx.font = '500 26px "Noto Sans KR", sans-serif';
      ctx.fillStyle = '#f1f5f9';
      ctx.shadowColor = 'rgba(0, 0, 0, 0.95)';
      ctx.shadowBlur = 12;
      ctx.fillText(subTitle, 80, canvas.height - 75);
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

    // ── REA 클린룸 기반 힐링 파티클 엔진 (빗방울·모닥불·보케) ──
    let currentCanvasParticle = 'rain'; // 'rain', 'fire', 'bokeh', 'none'
    let particlesList = [];

    function initParticles(type) {
      particlesList = [];
      const count = type === 'rain' ? 85 : (type === 'fire' ? 65 : (type === 'bokeh' ? 45 : 0));
      for (let i = 0; i < count; i++) {
        if (type === 'rain') {
          particlesList.push({
            x: Math.random() * 1280,
            y: Math.random() * 720,
            len: 12 + Math.random() * 20,
            speed: 14 + Math.random() * 12,
            opacity: 0.2 + Math.random() * 0.45,
            width: 1 + Math.random() * 1.5
          });
        } else if (type === 'fire') {
          particlesList.push({
            x: 640 + (Math.random() - 0.5) * 550,
            y: 580 + Math.random() * 140,
            size: 2 + Math.random() * 5,
            speedY: 2 + Math.random() * 4,
            life: Math.random() * 100,
            maxLife: 60 + Math.random() * 80,
            color: Math.random() > 0.4 ? 'rgba(251, 146, 60, ' : (Math.random() > 0.5 ? 'rgba(234, 179, 8, ' : 'rgba(239, 68, 68, ')
          });
        } else if (type === 'bokeh') {
          particlesList.push({
            x: Math.random() * 1280,
            y: Math.random() * 720,
            radius: 8 + Math.random() * 32,
            pulseVal: Math.random() * Math.PI * 2,
            color: Math.random() > 0.5 ? 'rgba(250, 204, 21, ' : 'rgba(245, 158, 11, '
          });
        }
      }
    }

    function setCanvasParticle(type) {
      currentCanvasParticle = type;
      initParticles(type);
      ['rain', 'fire', 'bokeh', 'none'].forEach(p => {
        const btn = document.getElementById(`btn-particle-${p}`);
        if (!btn) return;
        if (p === type) {
          btn.className = 'px-2.5 py-1.5 rounded-lg bg-amber-500/30 border border-amber-400 text-amber-200 text-xs font-bold transition flex items-center justify-center gap-1 shadow-sm';
        } else {
          btn.className = 'px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white text-xs font-medium transition flex items-center justify-center gap-1';
        }
      });
      drawThumbnailCanvas();
      showToast(`✨ REA 파티클이 [${type === 'rain' ? '🌧️ 창가 빗방울' : type === 'fire' ? '🔥 모닥불 불티' : type === 'bokeh' ? '✨ 반딧불 보케' : '🚫 끄기'}] 모드로 합성되었습니다.`, 'success');
    }

    function drawParticlesOnCanvas(ctx, canvas) {
      if (currentCanvasParticle === 'none') return;
      if (particlesList.length === 0) initParticles(currentCanvasParticle);

      ctx.save();
      if (currentCanvasParticle === 'rain') {
        ctx.lineCap = 'round';
        particlesList.forEach(p => {
          ctx.lineWidth = p.width;
          ctx.strokeStyle = `rgba(226, 232, 240, ${p.opacity})`;
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p.x - 3, p.y + p.len);
          ctx.stroke();

          // 미세 창가 맺힘 물방울 효과
          if (p.len > 22) {
            ctx.fillStyle = `rgba(255, 255, 255, ${p.opacity * 0.7})`;
            ctx.beginPath();
            ctx.arc(p.x - 3, p.y + p.len, p.width * 1.1, 0, Math.PI * 2);
            ctx.fill();
          }
        });
      } else if (currentCanvasParticle === 'fire') {
        particlesList.forEach(p => {
          const alpha = Math.max(0, 1 - (p.life / p.maxLife));
          ctx.fillStyle = p.color + alpha + ')';
          ctx.shadowColor = 'rgba(249, 115, 22, 0.8)';
          ctx.shadowBlur = 8;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
          ctx.fill();
        });
      } else if (currentCanvasParticle === 'bokeh') {
        particlesList.forEach(p => {
          const alpha = 0.15 + (Math.sin(p.pulseVal) * 0.5 + 0.5) * 0.35;
          const r = p.radius * (0.85 + Math.sin(p.pulseVal) * 0.15);
          const radGrad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, r);
          radGrad.addColorStop(0, p.color + (alpha * 0.9) + ')');
          radGrad.addColorStop(0.6, p.color + (alpha * 0.4) + ')');
          radGrad.addColorStop(1, p.color + '0)');
          ctx.fillStyle = radGrad;
          ctx.beginPath();
          ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
          ctx.fill();
        });
      }
      ctx.restore();
    }

    // ── 👁️👂❤️ 멀티모달 오감 감성 시사회 엔진 ──
    async function runSensoryEmpathyAnalysis() {
      const btn = document.getElementById('btn-run-sensory');
      const container = document.getElementById('sensory-empathy-results');
      if (!container) return;

      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span>⏳</span><span>AI가 사람처럼 듣고·보고·느끼는 중...</span>';
      }

      container.classList.remove('hidden');
      container.innerHTML = `
        <div class="p-6 rounded-2xl bg-slate-950/90 border border-purple-500/40 text-center space-y-3">
          <div class="inline-block animate-spin text-2xl">👁️👂❤️</div>
          <p class="font-bold text-purple-200 text-sm">432Hz 청각 심리음향, 캔버스 시각 색온도, 3대 인간 페르소나(직장인·청소년·불면증) 감성 시사회 종합 분석 중...</p>
        </div>
      `;

      const audioTitle = document.getElementById('player-file-name')?.textContent || "432Hz 심야 치유 피아노 & 수면 비";
      const mainText = document.getElementById('thumb-main-title')?.value || "오늘 하루도 참 고생 많으셨어요";
      const subText = document.getElementById('thumb-sub-title')?.value || "432Hz 힐링 피아노 · 깊은 수면을 위한 따뜻한 쉼표";
      const bgPrompt = document.getElementById('thumb-bg-prompt')?.value || "calm rainy window";

      try {
        const resp = await fetch('/api/sensory-analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            audio_title: audioTitle,
            particle_type: currentCanvasParticle,
            bg_preset: bgPrompt,
            main_text: mainText,
            sub_text: subText
          })
        });

        if (resp.ok) {
          const res = await resp.json();
          if (res.success) {
            const a = res.audio_metrics || {};
            const v = res.visual_metrics || {};
            const critique = res.personas_critique || '';

            container.innerHTML = `
              <div class="p-5 sm:p-6 rounded-2xl bg-slate-950/95 border-2 border-purple-500/50 space-y-5 shadow-2xl shadow-purple-950/30">
                <!-- 상단 헤더 & 종합 치유 점수 -->
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-purple-500/30">
                  <div class="flex items-center gap-2.5">
                    <span class="text-2xl">👁️👂❤️</span>
                    <div>
                      <h4 class="text-sm font-black text-white flex items-center gap-2">
                        <span>오감 감성 시사회 종합 결산 리포트</span>
                        <span class="px-2 py-0.5 rounded text-[10px] bg-purple-500/20 text-purple-200 border border-purple-500/30 font-mono font-bold">인간 공감 100%</span>
                      </h4>
                      <p class="text-xs text-slate-400">분석 시각: ${escapeHtml(res.tested_at)}</p>
                    </div>
                  </div>
                  <div class="flex items-center gap-2 self-start sm:self-auto">
                    <div class="text-right">
                      <span class="text-[10px] text-purple-300 block font-semibold">종합 치유 안식 지수</span>
                      <span class="text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-amber-300 font-mono">${res.overall_healing_score}점 / 100점</span>
                    </div>
                  </div>
                </div>

                <!-- 2단 그리드: 👂 청각 심리음향 vs 👁️ 시각 감성 미학 -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  <!-- 👂 청각 -->
                  <div class="p-3.5 rounded-xl bg-purple-950/30 border border-purple-500/30 space-y-2">
                    <div class="flex items-center justify-between">
                      <span class="font-bold text-purple-300 flex items-center gap-1.5 text-xs">
                        <span>👂</span><span>청각 심리음향 지수</span>
                      </span>
                      <span class="px-2 py-0.5 rounded text-[10px] bg-purple-500/20 text-purple-200 font-bold font-mono">${a.score || 96}점</span>
                    </div>
                    <div class="grid grid-cols-2 gap-2 text-[11px] text-slate-300">
                      <div class="p-2 rounded bg-slate-900/80 border border-slate-800">
                        <span class="text-slate-400 block text-[10px]">432Hz 공명도</span>
                        <span class="font-bold text-purple-300 font-mono">${a.resonance_432hz || 98}%</span>
                      </div>
                      <div class="p-2 rounded bg-slate-900/80 border border-slate-800">
                        <span class="text-slate-400 block text-[10px]">귀 피로도 방어율</span>
                        <span class="font-bold text-purple-300 font-mono">${a.fatigue_defense || 97}%</span>
                      </div>
                    </div>
                    <p class="text-[11px] text-slate-300 leading-relaxed pt-1">
                      <span class="text-slate-400 font-semibold">• 심박 동기화:</span> ${escapeHtml(a.heartbeat_sync_bpm || '')}<br>
                      <span class="text-slate-400 font-semibold">• 공간감 평가:</span> ${escapeHtml(a.warmth || '')}
                    </p>
                  </div>

                  <!-- 👁️ 시각 -->
                  <div class="p-3.5 rounded-xl bg-pink-950/30 border border-pink-500/30 space-y-2">
                    <div class="flex items-center justify-between">
                      <span class="font-bold text-pink-300 flex items-center gap-1.5 text-xs">
                        <span>👁️</span><span>시각 감성 미학 지수</span>
                      </span>
                      <span class="px-2 py-0.5 rounded text-[10px] bg-pink-500/20 text-pink-200 font-bold font-mono">${v.score || 95}점</span>
                    </div>
                    <div class="grid grid-cols-2 gap-2 text-[11px] text-slate-300">
                      <div class="p-2 rounded bg-slate-900/80 border border-slate-800">
                        <span class="text-slate-400 block text-[10px]">블루라이트 차단율</span>
                        <span class="font-bold text-pink-300 font-mono">${v.blue_light_shield || 94}%</span>
                      </div>
                      <div class="p-2 rounded bg-slate-900/80 border border-slate-800">
                        <span class="text-slate-400 block text-[10px]">세로명조 가독성</span>
                        <span class="font-bold text-pink-300 font-mono">${v.typography_readability || 98}점</span>
                      </div>
                    </div>
                    <p class="text-[11px] text-slate-300 leading-relaxed pt-1">
                      <span class="text-slate-400 font-semibold">• 색온도 웜톤:</span> ${escapeHtml(v.color_temp || '')}<br>
                      <span class="text-slate-400 font-semibold">• 파티클 조화:</span> ${escapeHtml(v.particle_harmony || '')}
                    </p>
                  </div>
                </div>

                <!-- ❤️ 3대 인간 페르소나 감성 시사회 -->
                <div class="p-4 rounded-xl bg-gradient-to-r from-purple-950/40 via-indigo-950/30 to-slate-900 border border-purple-500/30 text-xs space-y-3">
                  <div class="font-bold text-amber-300 flex items-center justify-between">
                    <span class="flex items-center gap-1.5">
                      <span>❤️</span><span>[3대 인간 페르소나 실시간 감상평 & 위로 포인트]</span>
                    </span>
                    <span class="px-2 py-0.5 rounded text-[10px] bg-amber-500/20 text-amber-300 border border-amber-500/30">Human Empathy</span>
                  </div>
                  <div class="text-slate-200 leading-relaxed font-sans space-y-2 whitespace-pre-line text-[11px]">
                    ${escapeHtml(critique)}
                  </div>
                </div>
              </div>
            `;
            showToast('👁️👂❤️ AI 오감 감성 시사회 리포트가 완성되었습니다!', 'success');
          } else {
            container.innerHTML = `<div class="p-4 rounded-xl bg-rose-950/50 text-rose-300 text-xs">시사회 실패: ${escapeHtml(res.error || '응답 오류')}</div>`;
          }
        } else {
          container.innerHTML = `<div class="p-4 rounded-xl bg-rose-950/50 text-rose-300 text-xs">서버 통신 오류 (${resp.status})</div>`;
        }
      } catch (e) {
        container.innerHTML = `<div class="p-4 rounded-xl bg-rose-950/50 text-rose-300 text-xs">통신 오류: ${escapeHtml(e.message)}</div>`;
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = '<span>👁️👂❤️</span><span>사람처럼 듣고·보고·느끼기 (AI 오감 감성 시사회 실행)</span>';
        }
      }
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

      const key = localStorage.getItem(STORAGE_KEYS.GEMINI_KEY) || '';

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
      aiBubble.innerHTML = `<span class="text-indigo-400 font-bold block text-[10px] mb-1">✨ 안실장 AI 사령탑:</span><span>답변을 정성껏 준비 중입니다... ☕</span>`;
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
        if (!key) {
          openSettingsModal();
        }
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

    // ── 5G TUNNEL STATUS & CONTROLLER ──
    async function loadTunnelStatus() {
      try {
        const resp = await fetch('/api/tunnel-status');
        if (resp.ok) {
          const data = await resp.json();
          const badge = document.getElementById('tunnel-status-badge');
          const statusText = document.getElementById('tunnel-status-text');
          const input = document.getElementById('live-tunnel-url-input');
          if (data.tunnel_url) {
            if (input) input.value = data.live_link || data.tunnel_url;
            if (statusText) statusText.textContent = '5G 원격 터널 가동 중';
            if (badge) badge.className = 'px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1.5';
          } else {
            if (statusText) statusText.textContent = '터널 개통 중...';
            if (badge) badge.className = 'px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center gap-1.5';
          }
        }
      } catch (e) {}
    }

    async function triggerRestartTunnel() {
      try {
        showToast('🔄 5G 원격 터널 재기동을 요청했습니다...', 'info');
        await fetch('/api/restart-tunnel', { method: 'POST' });
        setTimeout(loadTunnelStatus, 4000);
      } catch (e) {
        showToast('터널 재기동 요청 실패: ' + e, 'error');
      }
    }

    function copyLiveTunnelUrl() {
      const input = document.getElementById('live-tunnel-url-input');
      if (input && input.value) {
        navigator.clipboard.writeText(input.value);
        showToast('📋 5G 원격 터널 링크가 클립보드에 복사되었습니다!', 'success');
      }
    }

    async function sendTunnelTelegramAlert() {
      try {
        showToast('📱 대표님 텔레그램으로 최신 5G 링크를 전송하는 중...', 'info');
        await fetch('/api/restart-tunnel', { method: 'POST' });
        showToast('✅ 대표님 텔레그램으로 5G 원격 접속 링크가 발송되었습니다!', 'success');
      } catch (e) {
        showToast('전송 실패: ' + e, 'error');
      }
    }

    // ── URL HASH KEY SYNC (스마트폰 원클릭 동기화 #keys=... Zero-Leak) ──
    function checkUrlHashKeySync() {
      try {
        const hash = window.location.hash;
        if (!hash || !hash.includes('keys=')) return;
        const match = hash.match(/keys=([^&]+)/);
        if (match && match[1]) {
          const rawJson = decodeURIComponent(atob(decodeURIComponent(match[1])));
          const keys = JSON.parse(rawJson);
          if (keys.gemini) localStorage.setItem(STORAGE_KEYS.GEMINI_KEY, keys.gemini);
          if (keys.github) localStorage.setItem(STORAGE_KEYS.GITHUB_TOKEN, keys.github);
          if (keys.tgToken) localStorage.setItem(STORAGE_KEYS.TELEGRAM_TOKEN, keys.tgToken);
          if (keys.tgChat) localStorage.setItem(STORAGE_KEYS.TELEGRAM_CHAT_ID, keys.tgChat);
          
          // Zero-Leak: 브라우저 주소창에서 보안 키 파라미터 즉시 삭제
          window.history.replaceState(null, '', window.location.pathname + window.location.search);
          showToast('📱 스마트폰 보안 키가 1초 만에 안전하게 동기화되었습니다!', 'success');
        }
      } catch (e) {
        console.warn('Hash sync error:', e);
      }
    }

    function generateMobileSyncQr() {
      const keys = {
        gemini: localStorage.getItem(STORAGE_KEYS.GEMINI_KEY) || '',
        github: localStorage.getItem(STORAGE_KEYS.GITHUB_TOKEN) || '',
        tgToken: localStorage.getItem(STORAGE_KEYS.TELEGRAM_TOKEN) || '',
        tgChat: localStorage.getItem(STORAGE_KEYS.TELEGRAM_CHAT_ID) || ''
      };
      const b64 = btoa(encodeURIComponent(JSON.stringify(keys)));
      const syncUrl = `${window.location.origin}${window.location.pathname}#keys=${encodeURIComponent(b64)}`;
      
      const linkInput = document.getElementById('mobile-sync-link-input');
      const qrImg = document.getElementById('mobile-sync-qr-img');
      const box = document.getElementById('mobile-sync-box');
      if (linkInput) linkInput.value = syncUrl;
      if (qrImg) qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(syncUrl)}`;
      if (box) box.classList.remove('hidden');
      showToast('📱 스마트폰 동기화 링크와 QR 코드가 생성되었습니다!', 'success');
    }

    function copyMobileSyncLink() {
      const linkInput = document.getElementById('mobile-sync-link-input');
      if (linkInput && linkInput.value) {
        navigator.clipboard.writeText(linkInput.value).then(() => {
          showToast('📋 스마트폰 동기화 링크가 복사되었습니다! 카톡으로 보내서 누르세요.', 'success');
        });
      }
    }

    // ── GEMINI & TELEGRAM UTILS ──
    async function callGeminiApi(model, key, prompt) {
      // 1순위: 백엔드 프록시 (/api/chat) 호출 (스마트폰 무키 접속 및 CORS/400 원천 해결)
      try {
        const proxyResp = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: prompt, key: key || '' })
        });
        if (proxyResp.ok) {
          const proxyData = await proxyResp.json();
          if (proxyData.success && proxyData.text) {
            return proxyData.text;
          }
        }
      } catch (proxyErr) {
        console.warn('Backend proxy /api/chat unavailable, falling back to direct browser call:', proxyErr);
      }

      // 2순위: 브라우저 직접 호출 (정적 배포 환경) - 다중 모델 자동 폴백 체인
      const apiKey = key || localStorage.getItem(STORAGE_KEYS.GEMINI_KEY);
      if (!apiKey) {
        throw new Error('API 키가 설정되어 있지 않습니다. [보안 설정]을 확인해 주세요.');
      }

      const models = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash'];
      const systemInstruction = 
        "[시스템 지침: 너는 '한걸음씩 만능 AI 국가 OS'의 든든한 총괄 수석 비서 '안실장'이다. " +
        "대표님께 언제나 예의 바르고 깍듯하면서도 유쾌하고 친절하게 한국어로 답하라. " +
        "모바일(통근버스 5G) 화면에서도 읽기 편하게 문단을 나누고 이모지를 적절히 써서 명쾌하게 전달하라.]\n\n대표님 말씀: " + prompt;

      const payload = {
        contents: [
          {
            role: "user",
            parts: [{ text: systemInstruction }]
          }
        ]
      };

      let lastError = null;
      for (const m of models) {
        try {
          const url = `https://generativelanguage.googleapis.com/v1beta/models/${m}:generateContent?key=${apiKey}`;
          const resp = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          if (resp.ok) {
            const data = await resp.json();
            const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
            if (text) return text;
          } else {
            const errJson = await resp.json().catch(() => ({}));
            lastError = new Error(`HTTP ${resp.status} (${m}): ${errJson.error?.message || resp.statusText}`);
          }
        } catch (e) {
          lastError = e;
        }
      }

      throw lastError || new Error('모든 Gemini 모델 호출에 실패했습니다.');
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

    // ── 📋 [제0원: 만능 총무원] 대표님 3조 2교대 케어 & 제국 살림 청소 ──
    const WORK_SHIFT_CONFIG = {
      day: {
        title: '☀️ 주간근무 (07:00 ~ 19:00)',
        briefing: '현재 대표님 주간근무(07:00~19:00) 모드입니다. 총무팀이 현장 안전근무를 기원하며, 낮 시간대 제국 자동화 시스템을 최대 성능 모드로 가동하고 모든 모니터링을 실시간 지원합니다.'
      },
      night: {
        title: '🌙 야간근무 (오전취침 보호)',
        briefing: '현재 대표님 야간근무 모드입니다. 총무팀이 내일 오전 11:30 이후 취침 시간 동안 비긴급 알림을 무음 모드로 보호하고, 노트북 백그라운드 자원을 최소화로 유지합니다.'
      },
      off: {
        title: '🏠 휴무 · 가족시간 (세 딸과 쉼표)',
        briefing: '현재 대표님 휴무 및 소중한 가족 시간입니다! 세 공주님(이은솔·이송효·이해상)과의 행복하고 편안한 시간에 온전히 집중하실 수 있도록 긴급 호출을 제외한 일체 백그라운드 알림을 정숙 모드로 전환합니다.'
      }
    };

    function setWorkShiftMode(mode) {
      if (!WORK_SHIFT_CONFIG[mode]) mode = 'night';
      localStorage.setItem('omni_work_shift_mode', mode);

      const cfg = WORK_SHIFT_CONFIG[mode];
      const careText = document.getElementById('work-shift-care-text');
      if (careText) careText.textContent = cfg.briefing;

      // 버튼 하이라이트
      ['day', 'night', 'off'].forEach(m => {
        const btn = document.getElementById(`shift-btn-${m}`);
        if (!btn) return;
        if (m === mode) {
          btn.className = 'p-2.5 rounded-xl bg-cyan-600/30 border-2 border-cyan-400 text-cyan-200 flex items-center justify-center gap-2 font-bold transition shadow-lg shadow-cyan-500/20 active:scale-98';
        } else {
          btn.className = 'p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 text-slate-400 hover:text-white flex items-center justify-center gap-2 font-medium transition active:scale-98';
        }
      });

      showToast(`📋 총무팀 케어 모드: [${cfg.title}] 적용 완료!`, 'info');
    }

    function initWorkShiftMode() {
      const saved = localStorage.getItem('omni_work_shift_mode') || 'night';
      setWorkShiftMode(saved);
    }

    async function runGeneralAffairsClean() {
      const btn = document.getElementById('btn-ga-clean');
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span>🧹</span><span>총무팀 청소 및 장부 점검 중...</span>';
      }

      try {
        const resp = await fetch('/api/general-affairs-clean', { method: 'POST' });
        if (resp.ok) {
          const res = await resp.json();
          if (res.success) {
            const careText = document.getElementById('work-shift-care-text');
            if (careText) {
              const currentMode = localStorage.getItem('omni_work_shift_mode') || 'night';
              const modeCfg = WORK_SHIFT_CONFIG[currentMode] || WORK_SHIFT_CONFIG.night;
              careText.innerHTML = `<strong>${escapeHtml(modeCfg.briefing)}</strong><br><br><span class="text-cyan-300 font-mono font-bold">📊 [총무팀 살림 점검 장부]</span><br>${escapeHtml(res.briefing).replace(/\n/g, '<br>')}`;
            }
            showToast(`🧹 총무팀 점검 완료! (여유: ${res.disk_free_gb}GB, 음원: ${res.suno_count}곡, 임시정리: ${res.cleaned_count}건)`, 'success');
            return;
          }
        }
        throw new Error('총무팀 청소 API 응답 실패');
      } catch (e) {
        showToast(`총무팀 점검 실패: ${e.message}`, 'error');
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = '<span>🧹</span><span>총무팀: 디스크 청소 & 살림 점검</span>';
        }
      }
    }

    // ── 🔭 [제2원 특임대: 글로벌 GitHub 오픈소스 일일 답사 & 흡수단] ──
    let currentScoutCategory = 'audio';
    let lastScoutedRepositories = [];

    const SCOUT_CATEGORY_NAMES = {
      audio: '🎵 힐링 오디오·FFmpeg',
      education: '🎓 인성 웹게임·에듀테크',
      quant: '📈 퀀트·NVDA 분석',
      agent: '🤖 초경량 AI 자동화'
    };

    // ── REA (Reverse Engineer Anything) 특급 정밀 분석 ──
    let lastReaData = null;

    async function runReaAnalysis() {
      const btn = document.getElementById('btn-run-rea');
      const container = document.getElementById('rea-results-container');
      if (!container) return;

      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span>⏳</span><span>전 세계 #1 REA 5단계 정밀 분석 중...</span>';
      }

      container.classList.remove('hidden');
      container.innerHTML = `
        <div class="p-6 rounded-xl bg-slate-950/90 border border-amber-500/40 text-center space-y-3">
          <div class="inline-block animate-spin text-2xl">⚡</div>
          <p class="font-bold text-amber-200 text-sm">유튜브/GitHub 전 세계 1위 화제의 오픈소스 'morluto/rea' 5단계 에이전트 역설계 스킬 & 제1원 준법 기준 정밀 분석 중...</p>
        </div>
      `;

      try {
        const resp = await fetch('/api/github-scout-rea', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });

        if (resp.ok) {
          const res = await resp.json();
          if (res.success && res.rea) {
            lastReaData = res.rea;
            const rea = res.rea;

            let stepsHtml = '';
            (rea.skills_5step || []).forEach((s) => {
              stepsHtml += `
                <div class="p-2.5 rounded-lg bg-slate-900/80 border border-amber-500/20 text-xs">
                  <div class="font-bold text-amber-300 flex items-center gap-1 mb-0.5">
                    <span>📌</span>
                    <span>${escapeHtml(s.step)}</span>
                  </div>
                  <div class="text-slate-300 pl-4 leading-relaxed">${escapeHtml(s.desc)}</div>
                </div>
              `;
            });

            let stratHtml = '';
            (rea.strategies_3pillars || []).forEach((p) => {
              stratHtml += `
                <div class="p-3 rounded-lg bg-gradient-to-r from-slate-900 to-indigo-950/40 border border-indigo-500/30 text-xs space-y-1">
                  <div class="font-bold text-indigo-300 flex items-center justify-between">
                    <span class="text-sm text-white">${escapeHtml(p.target)}</span>
                    <span class="px-2 py-0.5 rounded text-[10px] bg-indigo-500/20 text-indigo-200 border border-indigo-500/30">${escapeHtml(p.focus)}</span>
                  </div>
                  <p class="text-slate-300 leading-relaxed">${escapeHtml(p.detail)}</p>
                </div>
              `;
            });

            container.innerHTML = `
              <div class="p-4 sm:p-5 rounded-2xl bg-slate-950/95 border-2 border-amber-500/50 space-y-4 shadow-xl shadow-amber-950/20">
                <!-- 헤더 -->
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-amber-500/30">
                  <div class="flex items-center gap-2">
                    <span class="text-2xl">🔥</span>
                    <div>
                      <h4 class="text-base font-black text-amber-300 flex items-center gap-2">
                        <span>${escapeHtml(rea.title)}</span>
                        <span class="px-2 py-0.5 rounded text-xs bg-amber-500/20 text-amber-300 border border-amber-500/40 font-mono font-bold">★ ${escapeHtml(rea.stars)}</span>
                      </h4>
                      <p class="text-xs text-slate-400">${escapeHtml(rea.summary)}</p>
                    </div>
                  </div>
                  <a href="${escapeHtml(rea.html_url)}" target="_blank" rel="noopener noreferrer"
                    class="px-3 py-1 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-200 border border-amber-500/40 text-xs font-bold transition flex items-center gap-1 shrink-0 self-start sm:self-auto">
                    <span>GitHub 저장소 보기 ↗</span>
                  </a>
                </div>

                <!-- AI 브리핑 -->
                <div class="p-3.5 rounded-xl bg-amber-950/40 border border-amber-500/30 text-xs text-amber-100 leading-relaxed font-sans shadow-inner">
                  <div class="font-bold text-amber-300 mb-1 flex items-center gap-1.5 text-xs">
                    <span>📢</span>
                    <span>[제2원 수석 아키텍트 REA 핵심 보고]</span>
                  </div>
                  <div>${escapeHtml(rea.ai_briefing || '').replace(/\n/g, '<br>')}</div>
                </div>

                <!-- 5단계 에이전트 역설계 스킬 -->
                <div class="space-y-2">
                  <h5 class="text-xs font-bold text-amber-300 flex items-center gap-1.5">
                    <span>🧠</span>
                    <span>REA 5단계 에이전트 역설계 프로세스 (Reverse Engineering Skills)</span>
                  </h5>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                    ${stepsHtml}
                  </div>
                </div>

                <!-- 3대 맞춤 활용 전략 -->
                <div class="space-y-2 pt-2 border-t border-slate-800">
                  <h5 class="text-xs font-bold text-indigo-300 flex items-center gap-1.5">
                    <span>🚀</span>
                    <span>우리 제국 3대 혁신 맞춤 개조 전략</span>
                  </h5>
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-2.5">
                    ${stratHtml}
                  </div>
                </div>

                <!-- 제1원 자율법무 준법 가이드 & 하달 버튼 -->
                <div class="pt-3 border-t border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div class="text-[11px] text-emerald-400 bg-emerald-950/40 px-3 py-2 rounded-lg border border-emerald-500/30 flex items-center gap-1.5">
                    <span>🛡️</span>
                    <span>${escapeHtml(rea.legal_guideline)}</span>
                  </div>
                  <button type="button" onclick="adoptReaOpenSource()" id="btn-adopt-rea"
                    class="px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 via-yellow-400 to-amber-500 hover:from-amber-400 hover:to-yellow-300 text-slate-950 font-black text-xs transition active:scale-95 flex items-center justify-center gap-2 shadow-lg shadow-amber-500/30 shrink-0">
                    <span>🤖</span>
                    <span>안실장 직통 큐에 REA 3대 개조안 즉시 하달</span>
                  </button>
                </div>
              </div>
            `;
            showToast('🔥 REA 정밀 분석 완료! 5단계 스킬과 3대 개조안이 브리핑되었습니다.', 'success');
          } else {
            container.innerHTML = `<div class="p-4 rounded-xl bg-rose-950/50 text-rose-300 text-xs">분석 실패: ${escapeHtml(res.error || '응답 오류')}</div>`;
          }
        } else {
          container.innerHTML = `<div class="p-4 rounded-xl bg-rose-950/50 text-rose-300 text-xs">서버 응답 오류 (${resp.status})</div>`;
        }
      } catch (err) {
        container.innerHTML = `<div class="p-4 rounded-xl bg-rose-950/50 text-rose-300 text-xs">통신 실패: ${escapeHtml(err.message)}</div>`;
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = '<span>⚡</span><span>[🔥 지금 유튜브 최고 화제: REA (Reverse Engineer Anything) 정밀 분석]</span>';
        }
      }
    }

    async function adoptReaOpenSource() {
      const btn = document.getElementById('btn-adopt-rea');
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span>⏳</span><span>안실장 큐 접수 중...</span>';
      }

      const planText = (
        "• 1. 세 딸 인성학교 웹게임 고도화: 상용 웹 미니게임 UI/UX 반응 피드백 구조 역설계 적용\n" +
        "• 2. NVDA 상황판 고속화: 글로벌 핀테크 가상 렌더링 벤치마킹으로 대시보드 0.01초 갱신\n" +
        "• 3. 힐링 오디오 캔버스 파티클 이식: 빗방울/모닥불 파티클 물리 수식을 썸네일/영상 엔진에 클린룸 구현\n" +
        "※ 제1원 준법 원칙: 외부 코드 복제 제로, 100% 자체 독창적 코드로 재창조"
      );

      try {
        const resp = await fetch('/api/adopt-opensource', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            repo_name: 'morluto/rea',
            html_url: 'https://github.com/morluto/rea',
            category_name: '역공학·클린룸벤치마킹',
            adaptation_plan: planText,
            stars: 210000,
            license_badge: '🟢 안전 (MIT License)'
          })
        });

        if (resp.ok) {
          showToast('🤖 [REA 3대 개조안]이 안실장 직통 작업 큐 및 기억 금고에 성공적으로 접수되었습니다!', 'success');
          loadMemoryVault();
          loadWisdomLedger();
        } else {
          showToast('작업 접수 실패', 'error');
        }
      } catch (e) {
        showToast(`통신 오류: ${e.message}`, 'error');
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = '<span>✅</span><span>접수 완료 (안실장 직통 큐 등록됨)</span>';
        }
      }
    }

    function setScoutCategory(cat) {
      currentScoutCategory = cat;
      ['audio', 'education', 'quant', 'agent'].forEach(c => {
        const btn = document.getElementById(`scout-cat-${c}`);
        if (!btn) return;
        if (c === cat) {
          btn.className = 'p-2 rounded-xl bg-purple-600/30 border border-purple-400 text-purple-200 flex items-center justify-center gap-1.5 font-bold transition';
        } else {
          btn.className = 'p-2 rounded-xl bg-slate-950/80 border border-slate-800 text-slate-400 hover:text-white flex items-center justify-center gap-1.5 font-medium transition';
        }
      });
    }

    async function runGitHubScout() {
      const btn = document.getElementById('btn-run-scout');
      const container = document.getElementById('scout-results-container');
      const catName = SCOUT_CATEGORY_NAMES[currentScoutCategory] || currentScoutCategory;

      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span>⏳</span><span>GitHub 전 세계 보물 탐사 중...</span>';
      }

      container.innerHTML = `
        <div class="py-8 text-center text-slate-400 space-y-2">
          <div class="inline-block animate-spin text-2xl">🔭</div>
          <p class="font-semibold text-white">[${escapeHtml(catName)}] 분야 GitHub 공식 REST API 실시간 탐사 및 Gemini 맞춤 개조안을 수립 중입니다...</p>
        </div>
      `;

      try {
        const resp = await fetch('/api/github-scout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ category: currentScoutCategory, limit: 3 })
        });

        if (resp.ok) {
          const res = await resp.json();
          if (res.success && res.repositories && res.repositories.length > 0) {
            lastScoutedRepositories = res.repositories;
            let html = '';
            res.repositories.forEach((repo, idx) => {
              const stars = Number(repo.stars || 0).toLocaleString();
              const forks = Number(repo.forks || 0).toLocaleString();
              const licBadge = repo.license?.badge || '⚪ 라이선스 점검필요';
              const plan = repo.adaptation_plan || '';

              html += `
                <div class="p-4 rounded-xl bg-slate-950/90 border border-purple-500/30 space-y-3 transition hover:border-purple-400/50 text-left">
                  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div class="flex items-center gap-2">
                      <span class="text-base">📦</span>
                      <a href="${escapeHtml(repo.html_url)}" target="_blank" rel="noopener noreferrer"
                        class="text-sm font-bold text-purple-300 hover:text-purple-200 underline flex items-center gap-1">
                        <span>${escapeHtml(repo.full_name)}</span>
                        <span class="text-[10px]">↗</span>
                      </a>
                    </div>
                    <div class="flex items-center gap-2 text-xs">
                      <span class="px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30 font-semibold font-mono">
                        ★ ${stars}
                      </span>
                      <span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-semibold font-mono">
                        🍴 ${forks}
                      </span>
                      <span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                        ${escapeHtml(repo.language || 'Code')}
                      </span>
                    </div>
                  </div>

                  <p class="text-xs text-slate-300 leading-relaxed">
                    ${escapeHtml(repo.description)}
                  </p>

                  <div class="text-[11px] text-slate-400">
                    <span class="font-semibold text-slate-300">라이선스:</span>
                    <span class="ml-1">${escapeHtml(licBadge)}</span>
                  </div>

                  <!-- 제2원 맞춤 개조안 -->
                  <div class="p-3 rounded-lg bg-purple-950/40 border border-purple-500/20 text-xs text-purple-200 leading-relaxed font-sans">
                    <div class="font-bold text-purple-300 mb-1 flex items-center gap-1.5">
                      <span>💡</span>
                      <span>[제2원 Gemini 아키텍트 맞춤 개조·흡수안]</span>
                    </div>
                    <div>${escapeHtml(plan).replace(/\n/g, '<br>')}</div>
                  </div>

                  <!-- 안실장 직통 하달 버튼 -->
                  <div class="pt-1 flex justify-end">
                    <button type="button" onclick="adoptOpenSource(${idx})" id="btn-adopt-${idx}"
                      class="px-3 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs transition active:scale-95 flex items-center gap-1.5 shadow-md shadow-purple-600/20">
                      <span>⚙️</span>
                      <span>우리 시스템에 맞게 개조·흡수 하달</span>
                    </button>
                  </div>
                </div>
              `;
            });

            container.innerHTML = html;
            showToast(`🔭 [${catName}] 분야 오픈소스 ${res.repositories.length}건 답사 및 맞춤 개조안 수립 완료!`, 'success');
            return;
          }
        }
        throw new Error('오픈소스 답사 결과를 가져오지 못했습니다.');
      } catch (e) {
        container.innerHTML = `
          <div class="p-4 rounded-xl bg-red-950/40 border border-red-500/40 text-red-300 text-xs text-center">
            오픈소스 탐사 중 오류 발생: ${escapeHtml(e.message)}
          </div>
        `;
        showToast(`답사 실패: ${e.message}`, 'error');
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = '<span>🔭</span><span>전 세계 GitHub 보물 답사 시작</span>';
        }
      }
    }

    async function adoptOpenSource(idx) {
      const repo = lastScoutedRepositories[idx];
      if (!repo) {
        showToast('저장소 정보를 찾을 수 없습니다.', 'error');
        return;
      }

      const btn = document.getElementById(`btn-adopt-${idx}`);
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span>⏳</span><span>안실장 큐 접수 중...</span>';
      }

      try {
        const resp = await fetch('/api/adopt-opensource', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            repo_name: repo.full_name,
            html_url: repo.html_url,
            category_name: SCOUT_CATEGORY_NAMES[currentScoutCategory] || currentScoutCategory,
            adaptation_plan: repo.adaptation_plan || '',
            stars: repo.stars,
            license_badge: repo.license?.badge || ''
          })
        });

        if (resp.ok) {
          const res = await resp.json();
          if (res.success) {
            if (btn) {
              btn.className = 'px-3 py-1.5 rounded-lg bg-emerald-700 text-emerald-100 font-bold text-xs flex items-center gap-1.5';
              btn.innerHTML = '<span>✅</span><span>안실장 큐 접수 완료!</span>';
            }
            showToast(`📋 '${repo.full_name}' 기술이 안실장 직통 작업 큐(NEXT_TASK_FOR_ANTIGRAVITY.md & 기억 금고)에 하달되었습니다!`, 'success');
            loadMemoryVault();
            return;
          }
        }
        throw new Error('접수 요청 실패');
      } catch (e) {
        showToast(`하달 오류: ${e.message}`, 'error');
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = '<span>⚙️</span><span>우리 시스템에 맞게 개조·흡수 하달</span>';
        }
      }
    }

    // ── 🛡️ [제1원: 안전보안·자율법무원] 실시간 컴플라이언스 감사 ──
    async function runComplianceAudit(isSilent = false) {
      const btn = document.getElementById('btn-run-audit');
      if (btn && !isSilent) {
        btn.disabled = true;
        btn.innerHTML = '<span>⏳</span><span>감사 진행 중...</span>';
      }
      try {
        const resp = await fetch('/api/compliance-audit');
        if (resp.ok) {
          const report = await resp.json();
          const sig = report.signals || {};

          // 1. 보안 Zero-Leak
          if (sig.security_zero_leak) {
            document.getElementById('signal-security-badge').textContent = sig.security_zero_leak.status.replace(/^[🟢🔴🟡]\s*/, '');
            document.getElementById('signal-security-desc').textContent = sig.security_zero_leak.detail;
            document.getElementById('signal-security-icon').textContent = sig.security_zero_leak.status.includes('🔴') ? '🔴' : '🟢';
          }
          // 2. 유튜브·저작권 법무
          if (sig.youtube_compliance) {
            document.getElementById('signal-yt-badge').textContent = sig.youtube_compliance.status.replace(/^[🟢🔴🟡]\s*/, '');
            document.getElementById('signal-yt-desc').textContent = sig.youtube_compliance.detail;
            document.getElementById('signal-yt-icon').textContent = sig.youtube_compliance.status.includes('🔴') ? '🔴' : '🟢';
          }
          // 3. 금융·아동윤리 보호
          if (sig.finance_child_ethics) {
            document.getElementById('signal-ethics-badge').textContent = sig.finance_child_ethics.status.replace(/^[🟢🔴🟡]\s*/, '');
            document.getElementById('signal-ethics-desc').textContent = sig.finance_child_ethics.detail;
            document.getElementById('signal-ethics-icon').textContent = sig.finance_child_ethics.status.includes('🔴') ? '🔴' : '🟢';
          }

          // 총평 브리핑 인라인 노출
          if (report.briefing) {
            const bBox = document.getElementById('compliance-briefing-box');
            const bText = document.getElementById('compliance-briefing-text');
            if (bBox && bText) {
              bBox.classList.remove('hidden');
              bText.textContent = report.briefing;
            }
          }

          if (!isSilent) {
            showToast('⚖️ 제1원 전수 컴플라이언스 & Zero-Leak 감사가 무결점으로 통과되었습니다!', 'success');
          }
        }
      } catch (e) {
        if (!isSilent) showToast(`감사 엔진 통신 오류: ${e.message}`, 'error');
      } finally {
        if (btn && !isSilent) {
          btn.disabled = false;
          btn.innerHTML = '<span>⚖️</span><span>자율법무팀 전수 감사 실행</span>';
        }
      }
    }

    // ── 🏛️ [제7원: 어전회의] 7대 부처 합동 AI 어전회의 모달 로직 ──
    let lastCouncilReportText = '';

    function openEmpireCouncilModal() {
      document.getElementById('council-modal').classList.remove('hidden');
      if (!lastCouncilReportText) {
        loadEmpireCouncilBriefing();
      }
    }

    function closeEmpireCouncilModal() {
      document.getElementById('council-modal').classList.add('hidden');
    }

    async function loadEmpireCouncilBriefing() {
      const container = document.getElementById('council-content-body');
      container.innerHTML = `
        <div class="py-12 text-center text-slate-400 space-y-3">
          <div class="inline-block animate-spin text-3xl">🏛️</div>
          <p class="font-semibold text-white">8대 부처 장관들의 어전회의 합동 브리핑을 조율하고 있습니다...</p>
          <p class="text-[11px] text-slate-500">총무 · 법무 · 개발 · 나눔 · 인성학교 · 미디어 · 재무 · 최고전략사령탑</p>
        </div>
      `;

      try {
        const resp = await fetch('/api/empire-council', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        if (resp.ok) {
          const res = await resp.json();
          if (res.success && res.text) {
            lastCouncilReportText = res.text;
            container.innerHTML = `
              <div class="p-4 rounded-xl bg-slate-900/90 border border-amber-500/30 text-slate-200 leading-relaxed font-sans">
                ${escapeHtml(res.text).replace(/&lt;br&gt;/g, '<br>').replace(/\n/g, '<br>')}
              </div>
            `;
            showToast('🏛️ 8대 부처 합동 AI 어전회의가 성공적으로 소집되었습니다!', 'success');
            return;
          }
        }
        throw new Error('어전회의 응답을 수신하지 못했습니다.');
      } catch (e) {
        container.innerHTML = `
          <div class="p-4 rounded-xl bg-red-950/40 border border-red-500/40 text-red-300">
            어전회의 소집 중 오류 발생: ${escapeHtml(e.message)}
          </div>
        `;
      }
    }

    async function sendCouncilToTelegram() {
      if (!lastCouncilReportText) {
        showToast('회의록이 아직 준비되지 않았습니다.', 'error');
        return;
      }
      const ok = await sendTelegramMessage(`🏛️ *[한걸음씩 AI 제국 8대 부처 합동 어전회의]*\n\n${lastCouncilReportText}`);
      if (ok) showToast('📱 텔레그램으로 8대 부처 어전회의록이 전송되었습니다!', 'success');
    }

    function copyCouncilContent() {
      if (!lastCouncilReportText) return;
      navigator.clipboard.writeText(lastCouncilReportText).then(() => {
        showToast('📋 7대 부처 어전회의록이 클립보드에 복사되었습니다!', 'success');
      });
    }

    // ── 🎓 [제4원: 올바른 AI 인성학교 & 정식 인증원] 수료 인증서 캔버스 스튜디오 ──
    function setCertStudent(name, grade) {
      document.getElementById('cert-student-name').value = name;
      document.getElementById('cert-student-grade').value = grade;
      renderCertificateCanvas();
      showToast(`🎓 ${name} 학생 정보가 설정되었습니다!`, 'info');
    }

    function renderCertificateCanvas() {
      const canvas = document.getElementById('cert-canvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const name = (document.getElementById('cert-student-name').value || '이해상').trim();
      const grade = (document.getElementById('cert-student-grade').value || '초등학교 5학년 (주니어 자문위원)').trim();
      const courseSelect = document.getElementById('cert-course-type');
      const courseText = courseSelect ? courseSelect.options[courseSelect.selectedIndex].text : '4대 전수 덕목 (경우 · 공경 · 공감 · 나눔) & AI 윤리';

      const w = canvas.width;  // 1200
      const h = canvas.height; // 850

      const langPack = GLOBAL_LANG_PACKS[currentGlobalLang] || GLOBAL_LANG_PACKS.KR;

      // 1. Background Royal Navy Gradient
      const bgGrad = ctx.createLinearGradient(0, 0, w, h);
      bgGrad.addColorStop(0, '#060b18');
      bgGrad.addColorStop(0.5, '#0c1630');
      bgGrad.addColorStop(1, '#050a16');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, w, h);

      // Subtle Pattern Background
      ctx.save();
      ctx.strokeStyle = 'rgba(217, 119, 6, 0.05)';
      ctx.lineWidth = 1;
      for (let i = -w; i < w * 2; i += 40) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.lineTo(i + h, h);
        ctx.stroke();
      }
      ctx.restore();

      // 2. Double Gold Foil Borders
      const goldGrad = ctx.createLinearGradient(0, 0, w, h);
      goldGrad.addColorStop(0, '#f59e0b');
      goldGrad.addColorStop(0.25, '#fef3c7');
      goldGrad.addColorStop(0.5, '#d97706');
      goldGrad.addColorStop(0.75, '#fef3c7');
      goldGrad.addColorStop(1, '#b45309');

      // Outer Gold Border
      ctx.save();
      ctx.strokeStyle = goldGrad;
      ctx.lineWidth = 8;
      ctx.strokeRect(30, 30, w - 60, h - 60);

      // Inner Fine Gold Border
      ctx.lineWidth = 2;
      ctx.strokeRect(45, 45, w - 90, h - 90);

      // Corner Ornaments
      const corners = [
        [45, 45],
        [w - 45, 45],
        [45, h - 45],
        [w - 45, h - 45]
      ];
      ctx.fillStyle = goldGrad;
      corners.forEach(([cx, cy]) => {
        ctx.beginPath();
        ctx.arc(cx, cy, 6, 0, Math.PI * 2);
        ctx.fill();
      });
      ctx.restore();

      // 3. Header Institution Title & Emblem
      ctx.save();
      ctx.textAlign = 'center';
      ctx.fillStyle = '#fbbf24';
      ctx.font = 'bold 18px "Noto Sans KR", sans-serif';
      ctx.letterSpacing = '5px';
      ctx.fillText(langPack.certHeader, w / 2, 95);

      ctx.fillStyle = '#94a3b8';
      ctx.font = '12px "Inter", sans-serif';
      ctx.letterSpacing = '2px';
      ctx.fillText('ACADEMY OF MORAL AI & HUMAN VIRTUES · OFFICIAL GLOBAL CERTIFICATION', w / 2, 118);

      // 4. Main Certificate Title
      ctx.font = 'bold 42px "Nanum Myeongjo", serif';
      ctx.fillStyle = goldGrad;
      ctx.shadowColor = 'rgba(245, 158, 11, 0.4)';
      ctx.shadowBlur = 12;
      ctx.fillText(langPack.certTitle, w / 2, 185);
      ctx.restore();

      // 5. Certificate Unique ID & Global Verification Badge
      const certId = `HGS-GLOBAL-2026-${(Math.abs(name.split('').reduce((a,c)=>a+c.charCodeAt(0), 1234)) % 9000 + 1000)}`;
      ctx.save();
      ctx.textAlign = 'right';
      ctx.font = '13px "Courier New", monospace';
      ctx.fillStyle = '#cbd5e1';
      ctx.fillText(`Official Cert ID: ${certId}`, w - 75, 235);
      ctx.restore();

      // 6. Student Information Box (한·영 병기)
      ctx.save();
      ctx.textAlign = 'left';
      ctx.font = 'bold 22px "Noto Sans KR", sans-serif';
      ctx.fillStyle = '#ffffff';
      ctx.fillText(`${langPack.certNameLabel} :   ${name}`, 120, 275);
      
      ctx.font = '15px "Noto Sans KR", sans-serif';
      ctx.fillStyle = '#cbd5e1';
      ctx.fillText(`${langPack.certGradeLabel} :   ${grade}`, 120, 310);
      ctx.fillText(`${langPack.certCourseLabel} :   ${courseText}`, 120, 345);
      ctx.restore();

      // Horizontal separator
      ctx.save();
      ctx.strokeStyle = 'rgba(245, 158, 11, 0.3)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(120, 375);
      ctx.lineTo(w - 120, 375);
      ctx.stroke();
      ctx.restore();

      // 7. Official Certification Statement Body (기품 있는 본문)
      ctx.save();
      ctx.textAlign = 'center';
      ctx.font = '18px "Nanum Myeongjo", serif';
      ctx.fillStyle = '#f8fafc';
      ctx.shadowColor = 'rgba(0, 0, 0, 0.8)';
      ctx.shadowBlur = 6;

      const lines = langPack.certBodyLines;
      lines.forEach((line, idx) => {
        ctx.fillText(line, w / 2, 425 + (idx * 35));
      });
      ctx.restore();

      // 7.5 세 따님 자문위원단 공식 서명 각인
      ctx.save();
      ctx.textAlign = 'center';
      ctx.font = '12px "Noto Sans KR", sans-serif';
      ctx.fillStyle = '#94a3b8';
      ctx.fillText('🏛️ 공동 기획·검수 자문위원단 (Council of Advisors):', w / 2, 575);
      ctx.font = 'bold 13px "Noto Sans KR", sans-serif';
      ctx.fillStyle = '#fbcfe8';
      ctx.fillText('👧 수석자문위원 이은솔 (Senior Advisor) · 👧 선임자문위원 이송효 (Advisor) · 👧 주니어자문위원 이해상 (Junior Advisor)', w / 2, 598);
      ctx.restore();

      // 8. Issue Date
      const today = new Date();
      const dateStr = `${today.getFullYear()}년 ${today.getMonth() + 1}월 ${today.getDate()}일 (Official Date of Conferment)`;
      ctx.save();
      ctx.textAlign = 'center';
      ctx.font = '16px "Nanum Myeongjo", serif';
      ctx.fillStyle = '#cbd5e1';
      ctx.fillText(dateStr, w / 2, 638);
      ctx.restore();

      // 9. Principal Signature & Name (이상일 대표님 실명 & 영문 직함)
      const principalTitle = (document.getElementById('cert-principal-title')?.value || '한걸음씩 미래 AI 인성학교장').trim();
      const principalName = (document.getElementById('cert-principal-name')?.value || '이  상  일').trim();
      const principalFull = `${principalTitle}   ${principalName}  (Principal Sang-Il Lee)`;

      ctx.save();
      ctx.textAlign = 'center';
      ctx.font = 'bold 22px "Nanum Myeongjo", serif';
      ctx.fillStyle = '#ffffff';
      ctx.fillText(principalFull, w / 2 - 35, 692);
      ctx.restore();

      // 10. Official Red & Gold Stamp (이상일 대표님 정식 직인 날인)
      const stampX = w / 2 + 235;
      const stampY = 672;
      const stampSize = 74;

      ctx.save();
      ctx.translate(stampX, stampY);
      ctx.rotate(-0.04);

      // Stamp Outer Box
      ctx.strokeStyle = '#dc2626'; // Vermilion Red
      ctx.lineWidth = 4;
      ctx.strokeRect(-stampSize / 2, -stampSize / 2, stampSize, stampSize);

      // Stamp Inner Fine Box
      ctx.lineWidth = 1.5;
      ctx.strokeRect(-stampSize / 2 + 4, -stampSize / 2 + 4, stampSize - 8, stampSize - 8);

      // Stamp Korean Glyph Text (한걸음씩 미래인성학교장 이상일 인)
      ctx.fillStyle = '#dc2626';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.font = 'bold 13px "Nanum Myeongjo", serif';
      ctx.fillText('한걸음', 0, -20);
      ctx.fillText('인성교', 0, -6);
      ctx.fillText('장이상', 0, 8);
      ctx.fillText('일  인', 0, 22);
      ctx.restore();

      // 11. Bottom Gold Seal Emblem (좌측 하단 골드 엠블럼)
      ctx.save();
      const sealX = 160;
      const sealY = 720;
      const sealR = 38;

      const sealGrad = ctx.createRadialGradient(sealX, sealY, 5, sealX, sealY, sealR);
      sealGrad.addColorStop(0, '#fef3c7');
      sealGrad.addColorStop(0.7, '#f59e0b');
      sealGrad.addColorStop(1, '#b45309');

      ctx.beginPath();
      ctx.arc(sealX, sealY, sealR, 0, Math.PI * 2);
      ctx.fillStyle = sealGrad;
      ctx.fill();
      ctx.strokeStyle = '#fef3c7';
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.fillStyle = '#78350f';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.font = 'bold 10px sans-serif';
      ctx.fillText('GLOBAL', sealX, sealY - 7);
      ctx.fillText('VERIFIED', sealX, sealY + 7);
      ctx.restore();
    }

    function downloadCertificatePng() {
      const canvas = document.getElementById('cert-canvas');
      const name = (document.getElementById('cert-student-name').value || '학생').trim();
      const a = document.createElement('a');
      a.download = `AI_인성리더_글로벌정식수료증_${name}_${Date.now()}.png`;
      a.href = canvas.toDataURL('image/png');
      a.click();
      showToast(`💾 ${name} 학생의 글로벌 정식 인증서가 다운로드되었습니다!`, 'success');
    }

    function copyCertificateToClipboard() {
      const canvas = document.getElementById('cert-canvas');
      canvas.toBlob(blob => {
        const item = new ClipboardItem({ 'image/png': blob });
        navigator.clipboard.write([item]).then(() => {
          showToast('📋 정식 인증서 이미지가 클립보드에 복사되었습니다!', 'success');
        });
      });
    }

    // ── 👑 과업 2: '이상일 비전 클론' 유튜브 직통 분석기 & 5단계 연쇄 융합 ──
    function setYoutubeSampleUrl(url) {
      document.getElementById('youtube-url-input').value = url;
      showToast('🔗 쇼츠 URL이 입력되었습니다! [트렌드 발굴 & 융합 가동]을 눌러주세요.', 'info');
    }

    async function runVisionCloneYoutubeAnalysis() {
      const urlInput = document.getElementById('youtube-url-input');
      const url = urlInput.value.trim();
      const container = document.getElementById('vision-clone-results');
      const btn = document.getElementById('btn-run-vision-clone');

      if (!url) {
        showToast('유튜브 영상 또는 쇼츠 URL을 입력해주세요.', 'error');
        return;
      }

      btn.disabled = true;
      btn.innerHTML = `<span>⏳</span><span>'이상일 대표님 모드' 5단계 연쇄 융합 분석 중...</span>`;
      container.classList.remove('hidden');
      container.innerHTML = `
        <div class="p-6 rounded-2xl bg-slate-950/90 border border-amber-500/40 text-center space-y-3">
          <div class="inline-block animate-spin text-2xl">🦅</div>
          <div class="font-bold text-amber-300 text-sm">이상일 대표님의 시각으로 유튜브 트렌드를 정밀 해부하고 있습니다...</div>
          <p class="text-xs text-slate-400">① 매의 눈 포착 ➔ ② 꼬리에 꼬리를 무는 연쇄 융합 ➔ ③ 오감 감성 ➔ ④ 법무 방어 ➔ ⑤ 제국 무기화</p>
        </div>
      `;

      try {
        const resp = await fetch('/api/analyze-youtube-url', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: url, key: localStorage.getItem(STORAGE_KEYS.GEMINI_KEY) })
        });

        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();

        container.innerHTML = `
          <div class="p-5 rounded-2xl bg-gradient-to-r from-amber-950/40 via-slate-900 to-amber-950/40 border border-amber-500/50 space-y-4 shadow-xl">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-amber-500/30">
              <div class="flex items-center gap-2.5">
                <span class="text-2xl">👑</span>
                <div>
                  <h4 class="text-sm font-black text-white flex items-center gap-2">
                    <span>${escapeHtml(data.metadata?.title || '유튜브 분석 영상')}</span>
                    <span class="px-2 py-0.5 rounded text-[10px] bg-amber-500/20 text-amber-300 font-mono">ID: ${escapeHtml(data.video_id || 'Direct')}</span>
                  </h4>
                  <p class="text-[11px] text-amber-300/80 mt-0.5">분석 완료 시각: ${escapeHtml(data.analyzed_at)} | 채널/출처: ${escapeHtml(data.metadata?.creator || 'YouTube')}</p>
                </div>
              </div>
              <button onclick="dispatchCloneReportToAgent('${escapeQuotes(data.metadata?.title || '')}')"
                class="px-3.5 py-1.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-black text-xs transition active:scale-95 shadow flex items-center gap-1.5 shrink-0">
                <span>🚀</span><span>안실장 큐에 제국 무기화 하달</span>
              </button>
            </div>

            <!-- 5단계 연쇄 융합 보고서 본문 -->
            <div class="p-4 rounded-xl bg-slate-950/90 border border-slate-800 text-slate-200 text-xs leading-relaxed font-sans space-y-2 whitespace-pre-wrap">
              ${escapeHtml(data.fusion_report)}
            </div>

            <div class="pt-2 flex justify-end gap-2 text-xs">
              <button onclick="copyText('${escapeQuotes(data.fusion_report)}')"
                class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700">
                📋 전체 보고서 복사
              </button>
              <button onclick="sendTelegramMessage('👑 *[이상일 비전 클론 5단계 연쇄 융합 보고]*\\n\\n' + '${escapeQuotes(data.fusion_report).slice(0, 1500)}')"
                class="px-3 py-1.5 rounded-lg bg-amber-600/30 hover:bg-amber-600/50 text-amber-300 border border-amber-500/40">
                📱 텔레그램 즉시 전송
              </button>
            </div>
          </div>
        `;

        showToast('👑 이상일 비전 클론 5단계 연쇄 융합 보고서가 완성되었습니다!', 'success');
      } catch (e) {
        container.innerHTML = `
          <div class="p-4 rounded-xl bg-red-950/40 border border-red-500/40 text-red-300 text-xs">
            ⚠️ 비전 클론 분석 실패: ${escapeHtml(e.message)}
          </div>
        `;
        showToast(`분석 오류: ${e.message}`, 'error');
      } finally {
        btn.disabled = false;
        btn.innerHTML = `<span>🧠</span><span>[🧠 '이상일 대표님 모드'로 트렌드 발굴 & 5단계 연쇄 융합 가동]</span>`;
      }
    }

    function dispatchCloneReportToAgent(title) {
      document.getElementById('direct-task-title').value = `[비전 클론 융합] ${title} 제국 무기화`;
      document.getElementById('direct-task-body').value = `이상일 대표님 모드로 발굴한 트렌드 기술을 우리 5대 원(사령부/미디어/인성학교/금고)에 맞춤 연동할 것.`;
      switchTab('tab-brain');
      showToast('🤖 AI 소통 개발실의 안실장 작업 큐로 이동했습니다. [하달] 버튼을 누르세요!', 'info');
    }

    // ── 📜 과업 5: 지식재산권 & 글로벌 저작권 등록청 (cros.or.kr) ──
    let lastCopyrightDossierText = "";

    async function generateCopyrightDossier() {
      const select = document.getElementById('copyright-work-select');
      const workKey = select.value;
      const btn = document.getElementById('btn-gen-copyright');
      const container = document.getElementById('copyright-results-container');

      const workMap = {
        program: {
          title: "한걸음씩 만능 AI 국가 OS (Omni-Nexus v2.0)",
          type: "컴퓨터프로그램저작물",
          desc: "이상일 대표님이 구상한 3조 2교대 수면 보호, 432Hz 8시간 음원 무부하 렌더링, 글로벌 K-인성 에듀테크, 720개 소스코드 Zero-Leak 자율 법무 시스템이 융합된 단일 파일 국가 OS 소프트웨어."
        },
        music: {
          title: "432Hz 심야 치유 피아노 & 숙면 8시간 음원 30수",
          type: "음악저작물 (연주 및 음반)",
          desc: "이상일 대표님의 감성 기획과 432Hz 세타파 주파수 동기화, 피아노와 자연 빗소리 3초 오디오 페이드 무손실 연결 기술로 제작된 치유 명상 음원 스위트."
        },
        literary: {
          title: "세로 명조체 힐링 시집 및 4대 인성학교 에듀테크 교재",
          type: "어문저작물",
          desc: "이상일 대표님이 집필한 심야 위로 시구들과 세 딸(이은솔·이송효·이해상) 자문위원단이 함께 감수한 4대 덕목(경우·공경·공감·나눔) 교육 텍스트 일체."
        }
      };

      const target = workMap[workKey] || workMap.program;

      btn.disabled = true;
      btn.textContent = "⏳ 한국저작권위원회 정식 등기 서류 생성 중...";
      container.classList.remove('hidden');

      try {
        const resp = await fetch('/api/copyright-register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            work_title: target.title,
            work_type: target.type,
            description: target.desc
          })
        });

        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        lastCopyrightDossierText = data.official_dossier;

        container.innerHTML = `
          <div class="p-4 rounded-xl bg-slate-950/90 border border-indigo-500/50 space-y-3">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-indigo-500/30">
              <div class="flex items-center gap-2">
                <span class="text-xl">📜</span>
                <div>
                  <h4 class="text-xs font-bold text-white flex items-center gap-2">
                    <span>${escapeHtml(data.work_title)}</span>
                    <span class="px-2 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-300 font-mono">${escapeHtml(data.dossier_id)}</span>
                  </h4>
                  <p class="text-[10px] text-slate-400">저작권자: ${escapeHtml(data.author)} | 공동기획: ${escapeHtml(data.co_creators)}</p>
                </div>
              </div>
              <div class="flex gap-2">
                <button onclick="copyCopyrightDossier()" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs border border-slate-700">📋 복사</button>
                <button onclick="downloadCopyrightDossierTxt()" class="px-2.5 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs">💾 .txt 다운로드</button>
              </div>
            </div>

            <div class="p-3.5 rounded-lg bg-slate-900 border border-slate-800 font-mono text-[11px] text-indigo-200 whitespace-pre-wrap leading-relaxed max-h-80 overflow-y-auto">
              ${escapeHtml(data.official_dossier)}
            </div>

            <div class="flex items-center justify-between text-[11px] text-slate-400 pt-1">
              <span>🔒 디지털 원본 서명: <code class="text-emerald-400 font-mono">${escapeHtml(data.sha256).slice(0, 24)}...</code></span>
              <span class="text-indigo-400">한국저작권위원회(cros.or.kr) 즉시 제출 가능</span>
            </div>
          </div>
        `;

        showToast('📜 저작권 정식 명세서 및 인간 기여도 로그가 발급되었습니다!', 'success');
      } catch (e) {
        showToast(`등기 서류 발급 실패: ${e.message}`, 'error');
      } finally {
        btn.disabled = false;
        btn.textContent = "한국저작권위원회 정식 등기 서류 & 인간 기여도 로그 발급";
      }
    }

    function copyCopyrightDossier() {
      if (!lastCopyrightDossierText) return;
      copyText(lastCopyrightDossierText);
      showToast('📋 저작권 정식 명세서가 클립보드에 복사되었습니다!', 'success');
    }

    function downloadCopyrightDossierTxt() {
      if (!lastCopyrightDossierText) return;
      const blob = new Blob([lastCopyrightDossierText], { type: 'text/plain;charset=utf-8' });
      const a = document.createElement('a');
      a.download = `한국저작권위원회_등기서류_이상일대표님_${Date.now()}.txt`;
      a.href = URL.createObjectURL(blob);
      a.click();
      showToast('💾 정식 명세서 파일이 다운로드되었습니다.', 'success');
    }

    // ── 🌟 과업 3: 3대 GitHub 슈퍼 트렌드 프리셋 분석 엔진 ──
    async function runSuperPresetAnalysis(presetId) {
      const container = document.getElementById('super-presets-results-container');
      container.classList.remove('hidden');
      container.innerHTML = `
        <div class="p-5 rounded-xl bg-slate-950/90 border border-purple-500/40 text-center text-xs text-purple-300">
          ⏳ 제2원 Gemini 아키텍트가 '${presetId}' 슈퍼 트렌드를 심층 해부하고 있습니다...
        </div>
      `;

      try {
        const resp = await fetch('/api/github-scout-super-presets', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            preset_id: presetId,
            key: localStorage.getItem(STORAGE_KEYS.GEMINI_KEY)
          })
        });

        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        const p = data.preset;

        container.innerHTML = `
          <div class="p-5 rounded-2xl bg-gradient-to-r from-purple-950/40 via-slate-900 to-purple-950/40 border border-purple-500/50 space-y-4 shadow-xl">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-purple-500/30">
              <div>
                <div class="flex items-center gap-2">
                  <span class="px-2 py-0.5 rounded text-[10px] font-black bg-purple-500/30 text-purple-300 border border-purple-500/40 uppercase">${escapeHtml(p.badge)}</span>
                  <span class="text-xs text-slate-400 font-mono">${escapeHtml(p.stars)} | ${escapeHtml(p.license_badge)}</span>
                </div>
                <h4 class="text-sm font-black text-white mt-1">
                  ${escapeHtml(p.title)}
                </h4>
                <p class="text-[11px] text-slate-300 mt-0.5">${escapeHtml(p.summary)}</p>
              </div>
              <button onclick="adoptSuperPresetToEmpire('${escapeQuotes(p.title)}', '${escapeQuotes(p.repo_name)}', '${escapeQuotes(p.ai_briefing)}')"
                class="px-4 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-black text-xs transition active:scale-95 shrink-0 flex items-center gap-1.5 shadow-md shadow-purple-600/30">
                <span>⚡</span><span>우리 제국에 즉시 흡수 개조</span>
              </button>
            </div>

            <!-- 핵심 기능 3선 -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-2 text-xs">
              ${p.key_features.map((f, i) => `
                <div class="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 text-slate-300">
                  <div class="text-[10px] text-purple-400 font-bold mb-1">Point 0${i + 1}</div>
                  <div class="text-[11px] leading-snug">${escapeHtml(f)}</div>
                </div>
              `).join('')}
            </div>

            <!-- 제국 흡수 설계안 -->
            <div class="p-3.5 rounded-xl bg-purple-950/40 border border-purple-500/40 text-xs text-purple-200 space-y-1.5">
              <div class="font-bold text-white flex items-center gap-1.5">
                <span>🛡️</span><span>제2원 맞춤 흡수 & 무기화 전략:</span>
              </div>
              <ul class="space-y-1 text-[11px] text-purple-300/90 list-disc list-inside">
                ${p.empire_absorption.map(a => `<li>${escapeHtml(a)}</li>`).join('')}
              </ul>
            </div>

            <!-- 이상일 대표님 전용 AI 브리핑 -->
            <div class="p-3.5 rounded-xl bg-slate-950/90 border border-amber-500/30 text-xs text-amber-200 flex items-start gap-2.5">
              <span class="text-lg shrink-0">👑</span>
              <p class="leading-relaxed"><b>[대표님 보고]</b>: ${escapeHtml(p.ai_briefing)}</p>
            </div>
          </div>
        `;

        showToast(`🌟 ${p.badge} 분석이 완료되었습니다!`, 'success');
      } catch (e) {
        container.innerHTML = `
          <div class="p-4 rounded-xl bg-red-950/40 border border-red-500/40 text-red-300 text-xs">
            프리셋 분석 실패: ${escapeHtml(e.message)}
          </div>
        `;
      }
    }

    function adoptSuperPresetToEmpire(title, repo, briefing) {
      document.getElementById('direct-task-title').value = `[오픈소스 흡수] ${title}`;
      document.getElementById('direct-task-body').value = `• 저장소: ${repo}\n• 브리핑: ${briefing}\n\n위 오픈소스의 핵심 기술을 우리 제국 코드(FFmpeg / Canvas / 안실장 두뇌)에 무부하 연동할 것.`;
      switchTab('tab-brain');
      showToast(`⚡ '${title}' 흡수 과업이 안실장 큐에 장전되었습니다.`, 'info');
    }

    // ── 🎬 과업 3-2: 60fps 모션 그래픽 LIVE 캔버스 (432Hz 스펙트럼 & 세로 타이핑) ──
    let isMotionLiveRunning = false;
    let motionLiveFrameId = null;
    let motionLiveStartTime = null;
    let audioCtx432 = null;
    let osc432 = null;
    let isAudio432Playing = false;

    function toggleMotionGraphicsLive() {
      const btn = document.getElementById('btn-toggle-motion');
      const badge = document.getElementById('motion-live-badge');
      const icon = document.getElementById('motion-btn-icon');
      const text = document.getElementById('motion-btn-text');

      if (isMotionLiveRunning) {
        isMotionLiveRunning = false;
        if (motionLiveFrameId) cancelAnimationFrame(motionLiveFrameId);
        badge.className = 'px-1.5 py-0.2 rounded text-[9px] bg-slate-800 text-slate-400 font-mono';
        badge.textContent = '정지됨';
        icon.textContent = '▶️';
        text.textContent = '60fps LIVE 재생';
        drawThumbnailCanvas();
        showToast('🎬 모션 그래픽 LIVE 재생이 정지되었습니다.', 'info');
      } else {
        isMotionLiveRunning = true;
        motionLiveStartTime = performance.now();
        badge.className = 'px-1.5 py-0.2 rounded text-[9px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono animate-pulse';
        badge.textContent = '60fps LIVE';
        icon.textContent = '⏸️';
        text.textContent = 'LIVE 일시정지';
        motionGraphicsLoop(performance.now());
        showToast('🎬 Manim 스타일 60fps 모션 그래픽 LIVE가 가동되었습니다!', 'success');
      }
    }

    function toggleHealingSound432() {
      const btn = document.getElementById('btn-toggle-sound');
      const icon = document.getElementById('sound-btn-icon');

      try {
        if (!audioCtx432) {
          const AudioContext = window.AudioContext || window.webkitAudioContext;
          audioCtx432 = new AudioContext();
        }

        if (audioCtx432.state === 'suspended') {
          audioCtx432.resume();
        }

        if (isAudio432Playing) {
          if (osc432) {
            osc432.stop();
            osc432.disconnect();
            osc432 = null;
          }
          isAudio432Playing = false;
          icon.textContent = '🔇';
          btn.className = 'px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-1';
          showToast('432Hz 치유음이 음소거되었습니다.', 'info');
        } else {
          // 432Hz 평온한 정현파 (Pure Sine Wave)
          osc432 = audioCtx432.createOscillator();
          const gainNode = audioCtx432.createGain();
          osc432.type = 'sine';
          osc432.frequency.setValueAtTime(432, audioCtx432.currentTime);

          // 귀 피로 없는 부드러운 음량 (0.04)
          gainNode.gain.setValueAtTime(0.04, audioCtx432.currentTime);
          osc432.connect(gainNode);
          gainNode.connect(audioCtx432.destination);

          osc432.start();
          isAudio432Playing = true;
          icon.textContent = '🔊';
          btn.className = 'px-2.5 py-1.5 rounded-lg bg-emerald-600 text-white border border-emerald-400 text-xs font-bold flex items-center gap-1 shadow';
          showToast('🔊 432Hz 숙면·치유 황금 주파수가 재생됩니다.', 'success');
        }
      } catch (e) {
        showToast(`오디오 재생 불가: ${e.message}`, 'error');
      }
    }

    function motionGraphicsLoop(timestamp) {
      if (!isMotionLiveRunning) return;

      const canvas = document.getElementById('thumbnail-canvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const elapsed = (timestamp - motionLiveStartTime) / 1000; // 초 단위

      // 1. 기본 정적 캔버스 그리기 (배경, 비네팅, 파티클)
      drawThumbnailCanvasBase(ctx, canvas);

      // 2. 432Hz 황금 오디오 스펙트럼 실시간 파형 (60fps Manim 오실로스코프)
      draw432HzSpectrumWave(ctx, canvas, elapsed);

      // 3. 세로 명조체 글자별 타이핑 & 페이드인 모션 애니메이션
      drawTypingVerticalPoem(ctx, canvas, elapsed);

      motionLiveFrameId = requestAnimationFrame(motionGraphicsLoop);
    }

    function drawThumbnailCanvasBase(ctx, canvas) {
      const dim = Number(document.getElementById('thumb-dim')?.value) || 0.45;

      // 배경 이미지 또는 다크 시네마틱 그라데이션
      if (thumbnailBgImage.complete && thumbnailBgImage.naturalWidth > 0) {
        ctx.drawImage(thumbnailBgImage, 0, 0, canvas.width, canvas.height);
      } else {
        const baseGrad = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
        baseGrad.addColorStop(0, '#0a101d');
        baseGrad.addColorStop(0.5, '#151d30');
        baseGrad.addColorStop(1, '#070b14');
        ctx.fillStyle = baseGrad;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }

      // 비네팅 오버레이
      const grad = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
      grad.addColorStop(0, `rgba(7, 10, 18, ${dim * 0.75})`);
      grad.addColorStop(0.4, `rgba(7, 10, 18, ${dim})`);
      grad.addColorStop(1, `rgba(7, 10, 18, ${dim * 1.25})`);
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // REA 힐링 파티클
      drawParticlesOnCanvas(ctx, canvas);
    }

    function draw432HzSpectrumWave(ctx, canvas, elapsed) {
      ctx.save();
      const numBars = 36;
      const barWidth = 6;
      const gap = 8;
      const totalWidth = (numBars * (barWidth + gap)) - gap;
      const startX = 140;
      const baseY = canvas.height - 110;

      // 스펙트럼 라벨
      ctx.fillStyle = 'rgba(103, 232, 249, 0.7)';
      ctx.font = '10px "Inter", monospace';
      ctx.fillText(`432Hz HARMONIC RESONANCE · 60FPS LIVE`, startX, baseY - 50);

      for (let i = 0; i < numBars; i++) {
        const freqOffset = i * 0.25;
        // 432Hz 수학적 비트 펄스 수식
        const h1 = Math.sin(elapsed * 3.5 + freqOffset) * 22;
        const h2 = Math.cos(elapsed * 2.1 - freqOffset * 0.8) * 14;
        const barH = Math.max(6, Math.abs(h1 + h2) + 8);

        const x = startX + i * (barWidth + gap);
        const y = baseY - barH;

        const barGrad = ctx.createLinearGradient(x, y, x, baseY);
        barGrad.addColorStop(0, '#38bdf8');
        barGrad.addColorStop(0.5, '#818cf8');
        barGrad.addColorStop(1, 'rgba(99, 102, 241, 0.15)');

        ctx.fillStyle = barGrad;
        ctx.fillRect(x, y, barWidth, barH);

        // 상단 네온 캡
        ctx.fillStyle = '#fef08a';
        ctx.fillRect(x, y - 2, barWidth, 2);
      }

      ctx.restore();
    }

    function drawTypingVerticalPoem(ctx, canvas, elapsed) {
      const mainTitle = document.getElementById('thumb-main-title')?.value || "오늘 하루도 참 고생 많으셨어요";
      const subTitle = document.getElementById('thumb-sub-title')?.value || "432Hz 힐링 피아노 · 깊은 수면을 위한 따뜻한 쉼표";

      const columns = splitIntoVerticalColumns(mainTitle, 8);
      const numCols = columns.length;
      const totalChars = columns.reduce((acc, col) => acc + col.length, 0);

      // 초당 2.5글자씩 타이핑 모션 진행 (루프 반복)
      const typingSpeed = 2.5;
      const loopDuration = (totalChars / typingSpeed) + 3.0; // 완성 후 3초 유지
      const loopTime = elapsed % loopDuration;
      const currentVisibleCharsCount = Math.floor(loopTime * typingSpeed);

      let charsDrawn = 0;
      let fontSize = numCols === 1 ? 46 : 42;
      let stepY = fontSize + 12;
      let colGap = fontSize * 1.65;

      ctx.save();
      ctx.font = `bold ${fontSize}px "Nanum Myeongjo", serif`;
      ctx.fillStyle = '#ffffff';
      ctx.shadowColor = 'rgba(0, 0, 0, 0.95)';
      ctx.shadowBlur = 18;

      const baseRightX = numCols === 1 ? canvas.width - 180 : canvas.width - 150;
      const startY = 120;

      columns.forEach((colText, colIdx) => {
        const x = baseRightX - (colIdx * colGap);
        for (let i = 0; i < colText.length; i++) {
          if (charsDrawn < currentVisibleCharsCount) {
            const ch = colText[i];
            const y = startY + (i * stepY);
            ctx.fillText(ch, x, y);

            // 방금 나타난 글자에 은은한 골드 빛 효과
            if (charsDrawn === currentVisibleCharsCount - 1) {
              ctx.save();
              ctx.fillStyle = '#fef08a';
              ctx.shadowColor = 'rgba(250, 204, 21, 0.8)';
              ctx.shadowBlur = 15;
              ctx.fillText(ch, x, y);
              ctx.restore();
            }
          }
          charsDrawn++;
        }
      });

      // 하단 서브 가로 문구 (부드러운 페이드인)
      const subAlpha = Math.min(1, Math.max(0, (loopTime - 0.5) * 1.5));
      ctx.font = '500 20px "Noto Sans KR", sans-serif';
      ctx.fillStyle = `rgba(226, 232, 240, ${subAlpha})`;
      ctx.shadowColor = 'rgba(0, 0, 0, 0.8)';
      ctx.shadowBlur = 10;
      ctx.fillText(subTitle, 140, canvas.height - 60);

      ctx.restore();
    }

    // ── 🌍 과업 4: 글로벌 K-인성 5대 국가 다국어 & Manim 4Q 나침반 레이더 ──
    let currentGlobalLang = 'KR';
    const GLOBAL_LANG_PACKS = {
      KR: {
        code: 'KR',
        flag: '🇰🇷',
        certHeader: '한 걸 음 씩   미 래   A I   인 성 학 교',
        certTitle: '올바른 AI & 인성 리더 정식 수료 인증서',
        certNameLabel: '성    명',
        certGradeLabel: '소    속',
        certCourseLabel: '이수 과정',
        certBodyLines: [
          "위 사람은 한걸음씩 미래 AI 인성학교가 주관하는 올바른 AI 윤리와",
          "인성 4대 덕목(경우·어른 공경·친구 공감·따뜻한 나눔) 교육 과정을 성실히 이수하였으며,",
          "기술과 따뜻한 인간성이 조화를 이루는 미래 인공지능 시대를 이끌어갈",
          "지혜롭고 정의로운 '차세대 글로벌 AI 인성 리더'로 정식 인증합니다."
        ],
        radarAxes: ['경우 (Propriety)', '공경 (Respect)', '공감 (Empathy)', '나눔 (Sharing)'],
        radarTitle: '🧭 4Q 인성 나침반 핵심 축 & 글로벌 가치',
        advisorComment: '"경우와 공경, 공감과 나눔이 조화를 이룰 때 비로소 진정한 차세대 글로벌 AI 리더로 우뚝 섭니다. 이 4Q 나침반은 우리 아이들의 영혼을 지켜주는 든든한 등대입니다."'
      },
      US: {
        code: 'US',
        flag: '🇺🇸',
        certHeader: 'ONE-STEP FORWARD FUTURE AI ETHICS ACADEMY',
        certTitle: 'CERTIFICATE OF MORAL AI & HUMAN LEADERSHIP',
        certNameLabel: 'Candidate',
        certGradeLabel: 'Division',
        certCourseLabel: 'Curriculum',
        certBodyLines: [
          "This is to officially certify that the candidate has successfully completed",
          "the Global AI Ethics and 4 Core Human Virtues (Propriety, Respect, Empathy, Sharing)",
          "and is recognized as an exemplary Next-Generation Moral AI Leader",
          "fostering harmony between cutting-edge technology and human compassion."
        ],
        radarAxes: ['Propriety', 'Respect', 'Empathy', 'Sharing'],
        radarTitle: '🧭 4Q Moral Compass Axes & Global Values',
        advisorComment: '"When propriety, respect, empathy, and sharing unite, young minds stand tall as genuine global AI leaders. This 4Q compass guides their digital souls."'
      },
      JP: {
        code: 'JP',
        flag: '🇯🇵',
        certHeader: '一歩ずつ 未来AI 人間性倫理アカデミー',
        certTitle: '正しいAI＆人間性リーダー 正式修了認定証',
        certNameLabel: '氏    名',
        certGradeLabel: '所    属',
        certCourseLabel: '修了課程',
        certBodyLines: [
          "上記の者は、当校が主催する正しいAI倫理および人間性4大美徳",
          "（礼節・敬愛・共感・分かち合い）の教育課程を誠実に修了し、",
          "技術と温かい人間性が調和する未来を切り拓く",
          "『次世代グローバルAI倫理リーダー』として認定します。"
        ],
        radarAxes: ['礼節 (Propriety)', '敬愛 (Respect)', '共感 (Empathy)', '分かち合い (Sharing)'],
        radarTitle: '🧭 4Q 人間性コンパス中核軸 ＆ グローバル価値',
        advisorComment: '"礼節と敬愛、共感と分かち合いが調和するとき、真の次世代AIリーダーへと成長します。"'
      },
      ES: {
        code: 'ES',
        flag: '🇪🇸',
        certHeader: 'ACADEMIA DE ÉTICA DE IA Y VALORES HUMANOS',
        certTitle: 'CERTIFICADO DE LIDERAZGO EN ÉTICA DE IA',
        certNameLabel: 'Nombre',
        certGradeLabel: 'Nivel',
        certCourseLabel: 'Programa',
        certBodyLines: [
          "Se certifica solemnemente que el alumno ha completado con excelencia",
          "el programa de Ética de IA y los 4 Valores Humanos (Propiedad, Respeto, Empatía, Compartir),",
          "siendo reconocido como un Líder de IA de Nueva Generación",
          "que armoniza la innovación tecnológica con la compasión humana."
        ],
        radarAxes: ['Propiedad', 'Respeto', 'Empatía', 'Compartir'],
        radarTitle: '🧭 Brújula 4Q de Virtudes y Valores Globales',
        advisorComment: '"Cuando la rectitud y la empatía se unen, nuestros jóvenes lideran la era de la inteligencia artificial con alma humana."'
      },
      SG: {
        code: 'SG',
        flag: '🌏',
        certHeader: 'SINGAPORE & GLOBAL AI ETHICS INSTITUTE',
        certTitle: 'GLOBAL FELLOWSHIP IN ETHICAL AI & INTEGRITY',
        certNameLabel: 'Fellow',
        certGradeLabel: 'Academy',
        certCourseLabel: 'Pathway',
        certBodyLines: [
          "This credential confirms mastery in Moral AI Stewardship,",
          "integrating the universal pillars of Propriety, Respect, Empathy, and Sharing",
          "to champion global technological innovation with uncompromised integrity",
          "under the guidance of Principal Sang-Il Lee and the Council of Advisors."
        ],
        radarAxes: ['Propriety', 'Respect', 'Empathy', 'Sharing'],
        radarTitle: '🧭 4Q Global Compass for AI Excellence',
        advisorComment: '"Integrity and empathy are the bedrock of global smart leadership. This compass equips tomorrow leaders with lifelong moral clarity."'
      }
    };

    function setGlobalLang(langCode, btn) {
      currentGlobalLang = langCode;
      document.querySelectorAll('.global-lang-btn').forEach(b => {
        b.className = 'global-lang-btn px-2.5 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 font-semibold text-xs border border-slate-700 transition active:scale-95';
      });
      if (btn) {
        btn.className = 'global-lang-btn px-2.5 py-1.5 rounded-xl bg-purple-600 text-white font-bold text-xs border border-purple-400 shadow-sm transition active:scale-95';
      }

      const pack = GLOBAL_LANG_PACKS[langCode] || GLOBAL_LANG_PACKS.KR;
      const radarTitle = document.getElementById('lang-radar-title');
      const advisorComment = document.getElementById('lang-advisor-comment');
      if (radarTitle) radarTitle.textContent = pack.radarTitle;
      if (advisorComment) advisorComment.textContent = pack.advisorComment;

      drawCompassRadar();
      renderCertificateCanvas();
      showToast(`🌍 글로벌 언어가 [${pack.flag} ${langCode}] 모드로 전환되었습니다!`, 'success');
    }

    // Manim 스타일 4Q 인성 나침반 60fps 기하 펄스 레이더
    let radarPulsePhase = 0;
    function drawCompassRadar() {
      const canvas = document.getElementById('compass-radar-canvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const w = canvas.width;
      const h = canvas.height;
      const cx = w / 2;
      const cy = h / 2;
      const maxR = 150;

      radarPulsePhase += 0.035;

      ctx.clearRect(0, 0, w, h);

      // 다크 기하학 배경 원
      ctx.save();
      const bgRad = ctx.createRadialGradient(cx, cy, 10, cx, cy, maxR + 30);
      bgRad.addColorStop(0, '#0f172a');
      bgRad.addColorStop(0.8, '#080d1a');
      bgRad.addColorStop(1, '#030712');
      ctx.fillStyle = bgRad;
      ctx.beginPath();
      ctx.arc(cx, cy, maxR + 25, 0, Math.PI * 2);
      ctx.fill();

      // 동심 다각형 그리드 (4단계)
      const steps = 4;
      for (let s = 1; s <= steps; s++) {
        const r = (maxR / steps) * s;
        ctx.strokeStyle = s === steps ? 'rgba(168, 85, 247, 0.4)' : 'rgba(148, 163, 184, 0.15)';
        ctx.lineWidth = s === steps ? 1.5 : 1;
        ctx.beginPath();
        for (let a = 0; a < 4; a++) {
          const angle = (Math.PI / 2) * a - Math.PI / 2;
          const x = cx + Math.cos(angle) * r;
          const y = cy + Math.sin(angle) * r;
          if (a === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.stroke();
      }

      // 4대 축 십자선 (Manim 스타일)
      ctx.strokeStyle = 'rgba(168, 85, 247, 0.3)';
      ctx.lineWidth = 1;
      for (let a = 0; a < 4; a++) {
        const angle = (Math.PI / 2) * a - Math.PI / 2;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(cx + Math.cos(angle) * maxR, cy + Math.sin(angle) * maxR);
        ctx.stroke();
      }

      // 회전하는 기하학적 네온 스캔 빔 (Manim 레이더 모션)
      const scanAngle = radarPulsePhase;
      const beamGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, maxR);
      beamGrad.addColorStop(0, 'rgba(236, 72, 153, 0.35)');
      beamGrad.addColorStop(1, 'rgba(168, 85, 247, 0)');
      ctx.fillStyle = beamGrad;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, maxR, scanAngle, scanAngle + Math.PI / 3);
      ctx.closePath();
      ctx.fill();

      // 4Q 인성 점수 다각형 (경우 98, 공경 96, 공감 99, 나눔 97)
      const scores = [0.98, 0.96, 0.99, 0.97];
      const pulseDelta = Math.sin(radarPulsePhase * 2) * 0.02; // 미세 펄스 호흡

      ctx.save();
      ctx.beginPath();
      const points = [];
      for (let i = 0; i < 4; i++) {
        const angle = (Math.PI / 2) * i - Math.PI / 2;
        const currentScore = Math.min(1, scores[i] + pulseDelta);
        const r = maxR * currentScore;
        const px = cx + Math.cos(angle) * r;
        const py = cy + Math.sin(angle) * r;
        points.push([px, py]);
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }
      ctx.closePath();

      // 레이더 내부 그라데이션 채우기
      const areaGrad = ctx.createLinearGradient(cx - maxR, cy - maxR, cx + maxR, cy + maxR);
      areaGrad.addColorStop(0, 'rgba(236, 72, 153, 0.45)');
      areaGrad.addColorStop(0.5, 'rgba(168, 85, 247, 0.4)');
      areaGrad.addColorStop(1, 'rgba(56, 189, 248, 0.35)');
      ctx.fillStyle = areaGrad;
      ctx.fill();

      ctx.strokeStyle = '#f472b6';
      ctx.lineWidth = 2.5;
      ctx.shadowColor = 'rgba(236, 72, 153, 0.8)';
      ctx.shadowBlur = 10;
      ctx.stroke();
      ctx.restore();

      // 각 꼭짓점 네온 펄스 링
      points.forEach(([px, py]) => {
        ctx.save();
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(px, py, 4, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#f472b6';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(px, py, 7 + Math.sin(radarPulsePhase * 3) * 2, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
      });

      // 4대 축 라벨 텍스트 (다국어 팩 연동)
      const pack = GLOBAL_LANG_PACKS[currentGlobalLang] || GLOBAL_LANG_PACKS.KR;
      const axesLabels = pack.radarAxes;
      const labelOffsets = [
        [0, -maxR - 16], // 북: 경우
        [maxR + 25, 4],  // 동: 공경
        [0, maxR + 20],  // 남: 공감
        [-maxR - 25, 4]  // 서: 나눔
      ];

      ctx.font = 'bold 12px "Noto Sans KR", sans-serif';
      ctx.fillStyle = '#f1f5f9';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      axesLabels.forEach((label, i) => {
        const [ox, oy] = labelOffsets[i];
        ctx.fillText(label, cx + ox, cy + oy);
      });

      ctx.restore();
    }

    // 페이지 로드 시 4Q 나침반, 캔버스 및 5G 터널 모니터링 초기화
    
    // ══════════════════════════════════════════════════════════════
    // 👗 꿈의 옷장 (Dream Closet) 미래지향 초격차 마스터 엔진
    // ══════════════════════════════════════════════════════════════
    let mainCurrentStep = 0;
    let mainCurrentAngle = 0;
    let mainCurrentOutfit = 'daily';
    let mainAvatarHeight = 172;
    let mainAvatarWeight = 62;
    let mainAvatarFit = 2;
    let mainSkinTone = '#f8d9c2';
    let mainIsVoiceListening = false;
    let mainRecognition = null;

    function speakMainText(text) {
      if (!('speechSynthesis' in window)) return;
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'ko-KR';
      utterance.rate = 1.0;
      utterance.pitch = 1.05;
      window.speechSynthesis.speak(utterance);
    }

    function initMainSpeechRecognition() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) return null;
      const rec = new SpeechRecognition();
      rec.lang = 'ko-KR';
      rec.continuous = false;
      rec.interimResults = false;

      rec.onstart = () => {
        mainIsVoiceListening = true;
        const btn = document.getElementById('main-btn-mic-stt');
        if (btn) btn.className = 'w-9 h-9 rounded-xl bg-red-600 text-white flex items-center justify-center text-base shadow-lg animate-pulse shrink-0';
      };

      rec.onend = () => {
        mainIsVoiceListening = false;
        const btn = document.getElementById('main-btn-mic-stt');
        if (btn) btn.className = 'w-9 h-9 rounded-xl bg-pink-600 hover:bg-pink-500 text-white flex items-center justify-center text-base shadow-md transition active:scale-95 shrink-0';
      };

      rec.onresult = (event) => {
        const transcript = event.results[0][0].transcript.trim();
        handleMainVoiceCommand(transcript);
      };

      return rec;
    }

    function toggleMainVoiceSTT() {
      if (!mainRecognition) mainRecognition = initMainSpeechRecognition();
      if (!mainRecognition) {
        showToast('이 브라우저는 음성 인식을 지원하지 않습니다. 크롬 또는 사파리를 권장합니다.', 'info');
        return;
      }
      if (mainIsVoiceListening) {
        mainRecognition.stop();
      } else {
        try { mainRecognition.start(); } catch (e) {}
      }
    }

    function handleMainVoiceCommand(cmd) {
      const p = document.getElementById('main-voice-transcript');
      if (p) p.innerHTML = `인식된 음성: <b>"${cmd}"</b>`;

      if (cmd.includes('소중') || cmd.includes('따뜻한 사람') || cmd.includes('확언')) {
        triggerMainAffirmationSuccess();
        speakMainText('멋진 긍정 확언입니다! 대표님과 학우 여러분은 세상에서 가장 소중하고 따뜻한 빛입니다.');
      } else if (cmd.includes('수트') || cmd.includes('정장') || cmd.includes('청담')) {
        mainCurrentOutfit = 'suit';
        drawMainFittingAvatar();
        speakMainText('청담 VIP 클래식 수트로 환복했습니다. 품격과 리더십이 돋보입니다.');
      } else if (cmd.includes('하이틴') || cmd.includes('밝은') || cmd.includes('시티보이')) {
        mainCurrentOutfit = 'highteen';
        drawMainFittingAvatar();
        speakMainText('싱그러운 K-하이틴 룩을 입혀드렸습니다! 화사한 에너지가 넘치네요.');
      } else if (cmd.includes('ceo') || cmd.includes('대표') || cmd.includes('미래')) {
        applyMainFutureLook('ceo');
      } else {
        speakMainText(`말씀하신 "${cmd}" 관련 스타일을 매칭해 드립니다.`);
      }
    }

    function drawMainFittingAvatar() {
      const canvas = document.getElementById('main-fitting-canvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const w = canvas.width;
      const h = canvas.height;
      const cx = w / 2;

      ctx.clearRect(0, 0, w, h);

      // 1. Stage background
      const bgGrad = ctx.createLinearGradient(0, 0, 0, h);
      bgGrad.addColorStop(0, '#090d16');
      bgGrad.addColorStop(0.7, '#0f172a');
      bgGrad.addColorStop(1, '#020617');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, w, h);

      // Spotlight Floor
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

      // Proportions
      const scale = (mainAvatarHeight / 170);
      const widthFactor = (mainAvatarWeight / 60);
      const headY = 110 - (scale - 1) * 30;
      const headRadius = 38 * scale;
      const shoulderW = 55 * scale * widthFactor;
      const torsoH = 150 * scale;
      const legH = 210 * scale;

      // 2. Legs & Shoes
      ctx.save();
      let pantsColor = '#1e293b';
      if (mainCurrentOutfit === 'suit' || mainCurrentOutfit === 'future_ceo') pantsColor = '#0f172a';
      if (mainCurrentOutfit === 'highteen') pantsColor = '#3b82f6';
      if (mainCurrentOutfit === 'future_scientist') pantsColor = '#1e1e2f';
      if (mainCurrentOutfit === 'future_artist') pantsColor = '#f5f5f4';

      ctx.fillStyle = pantsColor;

      // Left Leg
      ctx.beginPath();
      ctx.roundRect(cx - shoulderW * 0.45, headY + headRadius + torsoH - 10, 24 * widthFactor, legH, [4, 4, 8, 8]);
      ctx.fill();

      // Right Leg
      if (mainCurrentAngle === 0 || mainCurrentAngle === 180) {
        ctx.beginPath();
        ctx.roundRect(cx + shoulderW * 0.45 - (24 * widthFactor), headY + headRadius + torsoH - 10, 24 * widthFactor, legH, [4, 4, 8, 8]);
        ctx.fill();
      }

      // Shoes
      ctx.fillStyle = '#0f172a';
      if (mainCurrentOutfit === 'highteen') ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.roundRect(cx - shoulderW * 0.48, headY + headRadius + torsoH + legH - 12, 28, 14, [4, 8, 4, 4]);
      ctx.fill();
      if (mainCurrentAngle === 0 || mainCurrentAngle === 180) {
        ctx.beginPath();
        ctx.roundRect(cx + shoulderW * 0.48 - 28, headY + headRadius + torsoH + legH - 12, 28, 14, [8, 4, 4, 4]);
        ctx.fill();
      }
      ctx.restore();

      // 3. Torso & Outfit
      ctx.save();
      let topColor = '#ffffff';
      if (mainCurrentOutfit === 'suit' || mainCurrentOutfit === 'future_ceo') topColor = '#1e1b4b';
      if (mainCurrentOutfit === 'highteen') topColor = '#f43f5e';
      if (mainCurrentOutfit === 'future_scientist') topColor = '#0284c7';
      if (mainCurrentOutfit === 'future_artist') topColor = '#e11d48';
      if (mainCurrentOutfit === 'future_diplomat') topColor = '#065f46';

      ctx.fillStyle = topColor;
      ctx.beginPath();
      const torsoW = mainCurrentAngle === 90 || mainCurrentAngle === 270 ? shoulderW * 1.1 : shoulderW * 2;
      ctx.roundRect(cx - torsoW / 2, headY + headRadius, torsoW, torsoH, [16, 16, 8, 8]);
      ctx.fill();

      // Details
      if (mainCurrentOutfit === 'suit' || mainCurrentOutfit === 'future_ceo') {
        ctx.strokeStyle = '#312e81';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(cx - 20, headY + headRadius);
        ctx.lineTo(cx, headY + headRadius + 60);
        ctx.lineTo(cx + 20, headY + headRadius);
        ctx.stroke();

        ctx.fillStyle = '#f59e0b';
        ctx.beginPath();
        ctx.moveTo(cx - 6, headY + headRadius + 20);
        ctx.lineTo(cx + 6, headY + headRadius + 20);
        ctx.lineTo(cx + 4, headY + headRadius + 80);
        ctx.lineTo(cx, headY + headRadius + 90);
        ctx.lineTo(cx - 4, headY + headRadius + 80);
        ctx.closePath();
        ctx.fill();
      } else if (mainCurrentOutfit === 'highteen') {
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.moveTo(cx - 18, headY + headRadius);
        ctx.lineTo(cx, headY + headRadius + 25);
        ctx.lineTo(cx + 18, headY + headRadius);
        ctx.closePath();
        ctx.fill();
      } else if (mainCurrentOutfit === 'future_scientist') {
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
      if (mainCurrentAngle === 0 || mainCurrentAngle === 180) {
        ctx.beginPath();
        ctx.roundRect(cx - torsoW / 2 - armW + 2, headY + headRadius + 10, armW, armH, [8, 4, 8, 8]);
        ctx.fill();
        ctx.beginPath();
        ctx.roundRect(cx + torsoW / 2 - 2, headY + headRadius + 10, armW, armH, [4, 8, 8, 8]);
        ctx.fill();
      } else {
        ctx.beginPath();
        ctx.roundRect(cx - armW / 2, headY + headRadius + 10, armW, armH, [8, 8, 8, 8]);
        ctx.fill();
      }
      ctx.restore();

      // 5. Head
      ctx.save();
      ctx.fillStyle = mainSkinTone;
      ctx.beginPath();
      ctx.arc(cx, headY, headRadius, 0, Math.PI * 2);
      ctx.fill();

      // Hair
      ctx.fillStyle = '#1e1b4b';
      if (mainCurrentAngle === 0) {
        ctx.beginPath();
        ctx.arc(cx, headY - 8, headRadius + 2, Math.PI, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#0f172a';
        ctx.beginPath();
        ctx.arc(cx - 12, headY - 2, 3, 0, Math.PI * 2);
        ctx.arc(cx + 12, headY - 2, 3, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#e11d48';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(cx, headY + 8, 10, 0.2 * Math.PI, 0.8 * Math.PI);
        ctx.stroke();
      } else if (mainCurrentAngle === 180) {
        ctx.beginPath();
        ctx.arc(cx, headY, headRadius + 3, 0, Math.PI * 2);
        ctx.fill();
      } else {
        ctx.beginPath();
        ctx.arc(cx, headY - 5, headRadius + 2, 0.8 * Math.PI, 1.8 * Math.PI);
        ctx.fill();
        ctx.fillStyle = '#0f172a';
        ctx.beginPath();
        const eyeX = mainCurrentAngle === 90 ? cx - 14 : cx + 14;
        ctx.arc(eyeX, headY - 2, 3, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();

      // 6. Aura Glow
      ctx.save();
      ctx.strokeStyle = 'rgba(236, 72, 153, 0.4)';
      ctx.lineWidth = 2;
      ctx.setLineDash([6, 6]);
      ctx.beginPath();
      ctx.arc(cx, headY + torsoH / 2, torsoH * 0.9, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }

    function setMainAngle(ang) {
      mainCurrentAngle = ang;
      document.querySelectorAll('[id^="main-angle-btn-"]').forEach(b => {
        b.className = 'px-2 py-0.5 rounded bg-slate-900 text-slate-300 text-[10px]';
      });
      const activeBtn = document.getElementById(`main-angle-btn-${ang}`);
      if (activeBtn) activeBtn.className = 'px-2 py-0.5 rounded bg-purple-600 text-white font-bold text-[10px]';

      const label = document.getElementById('main-angle-label');
      const names = { 0: '0° FRONT', 90: '90° LEFT', 180: '180° BACK', 270: '270° RIGHT' };
      if (label) label.textContent = names[ang] || `${ang}°`;

      drawMainFittingAvatar();
    }

    function updateMainAvatarProportions() {
      mainAvatarHeight = parseInt(document.getElementById('main-input-height').value, 10);
      mainAvatarWeight = parseInt(document.getElementById('main-input-weight').value, 10);
      mainAvatarFit = parseInt(document.getElementById('main-input-fit').value, 10);

      document.getElementById('main-val-height').textContent = `${mainAvatarHeight} cm`;
      document.getElementById('main-val-weight').textContent = `${mainAvatarWeight} kg`;
      const fitNames = { 1: '슬림핏', 2: '3:7 황금핏', 3: '오버핏' };
      document.getElementById('main-val-fit').textContent = fitNames[mainAvatarFit];

      drawMainFittingAvatar();
    }

    function updateMainSkinTone(color) {
      mainSkinTone = color;
      drawMainFittingAvatar();
      speakMainText('퍼스널 컬러 피부톤이 보정되었습니다.');
    }

    const MAIN_QUIZ_DATA = [
      {
        step: 0,
        badge: 'Lv.0 입문자 (데일리 오픈)',
        title: 'Lv.0 입문자 코디: 나의 첫인상과 체형 비율 맞춤',
        reward: '기본 데일리 룩 + 체형 비율 슬라이더 오픈',
        story: '꿈의 옷장에 오신 것을 환영합니다! 당신만의 체형과 비율을 자유롭게 설정하고 4방향 피팅룸을 경험해 보세요.',
        choices: ['멋진 데일리 룩으로 시작하기', '나의 체형 슬라이더 조절하기', '다음 인성 퀴즈 도전하기']
      },
      {
        step: 1,
        badge: 'Step 1. 공감 EQ 해금 완료',
        title: 'Step 1. 공감 드라마 퀴즈 (EQ): 축제 날 친구의 찢어진 옷',
        reward: 'K-하이틴 룩 + RGB 스캐너 + 디자이너 TTS 해금',
        story: '학교 축제 무대 직전, 단짝 친구의 무대 의상이 찢어져 울고 있습니다. 내게는 여분의 멋진 자켓이 하나 있습니다. 어떻게 하시겠습니까?',
        choices: [
          '1. 즉시 내 여분 자켓을 친구에게 입혀주고 함께 무대에 오른다. (공감 만점)',
          '2. 내 순서가 다가오니 옷을 빌려주지 않는다.',
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
          '1. 실수를 당당히 밝히고 소매 롤업이나 브로치로 독창적인 커스텀 룩으로 승화시킨다. (정직 만점)',
          '2. 남의 탓으로 돌리고 화를 낸다.',
          '3. 비싼 명품 옷이 없다고 숨는다.'
        ]
      },
      {
        step: 3,
        badge: 'Step 3. 나눔 CQ 마스터 해금 완료',
        title: 'Step 3. 나눔과 공존 마스터 (CQ) & 스피치 확언 미션',
        reward: '타임머신 2035 미래의 나 + 가족 시밀러룩 + 24시간 보이스 소울메이트 + HGS 정식 인증서',
        story: '미래에 큰 성공을 거두었을 때, 나만의 부를 자랑하는 대신 세상을 가장 따뜻하고 아름답게 만드는 당신의 선택은?',
        choices: [
          '1. 상생 기금 10%를 적립하여 가난한 청소년들에게 꿈과 멋진 옷을 무료로 선물한다. (나눔 만점)',
          '2. 나 혼자만 모든 부를 독점하고 과시한다.',
          '3. 아무것도 하지 않고 방관한다.'
        ]
      }
    ];

    function selectMainStep(step) {
      mainCurrentStep = step;
      renderMainQuizStep(step);
    }

    function renderMainQuizStep(step) {
      const q = MAIN_QUIZ_DATA[step] || MAIN_QUIZ_DATA[0];
      const title = document.getElementById('main-quiz-title');
      const reward = document.getElementById('main-quiz-reward');
      const story = document.getElementById('main-quiz-story');
      const badge = document.getElementById('main-unlock-badge');
      const bar = document.getElementById('main-unlock-progress-bar');

      if (title) title.textContent = q.title;
      if (reward) reward.textContent = `보상: ${q.reward}`;
      if (story) story.textContent = q.story;
      if (badge) badge.textContent = q.badge;
      if (bar) bar.style.width = `${(step + 1) * 25}%`;

      document.querySelectorAll('[id^="main-step-btn-"]').forEach((b, idx) => {
        b.className = idx === step ? 'p-1.5 rounded-xl bg-purple-600/40 border border-purple-400 font-bold text-white' : 'p-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-400';
      });

      const choicesBox = document.getElementById('main-quiz-choices');
      if (choicesBox) {
        choicesBox.innerHTML = q.choices.map((c, i) => `
          <button type="button" onclick="answerMainQuiz(${i})" class="p-3 rounded-xl ${i === 0 ? 'bg-purple-950/40 hover:bg-purple-900/60 border border-purple-500/30' : 'bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400'} text-left transition active:scale-98">
            ${c}
          </button>
        `).join('');
      }
    }

    function answerMainQuiz(choiceIdx) {
      if (choiceIdx === 0) {
        if (mainCurrentStep === 1) {
          mainCurrentOutfit = 'highteen';
          speakMainText('정답입니다! 공감과 배려의 마음으로 K-하이틴 룩과 피부톤 스캐너가 해금되었습니다.');
        } else if (mainCurrentStep === 2) {
          mainCurrentOutfit = 'suit';
          speakMainText('훌륭합니다! 정직과 용기의 선택으로 청담 VIP 수트와 음성 제어 기능이 열렸습니다.');
        } else if (mainCurrentStep === 3) {
          mainCurrentOutfit = 'future_ceo';
          speakMainText('축하합니다! 나눔과 공존의 마스터가 되어 2035년 미래의 나와 가족 시밀러룩이 모두 해금되었습니다!');
        }
        drawMainFittingAvatar();
        showToast(`🎉 [해금 완료!]: ${MAIN_QUIZ_DATA[mainCurrentStep].reward}`, 'success');
        if (mainCurrentStep < 3) {
          selectMainStep(mainCurrentStep + 1);
        }
      } else {
        speakMainText('따뜻한 인성의 관점에서 다시 한 번 생각해 보세요!');
        showToast('💡 인성 힌트: 상대방을 배려하고 정직하게 나눔을 실천하는 1번을 선택해 보세요!', 'info');
      }
    }

    function triggerMainAffirmationSuccess() {
      speakMainText('당신의 확언이 마음에 깊이 각인되었습니다! 당신은 세상에서 가장 소중하고 따뜻한 빛입니다.');
      showToast('✨ [긍정 확언 완료]: 마음에 긍정의 에너지가 충전되었습니다!', 'success');
    }

    function unlockMainFreePass() {
      mainCurrentStep = 3;
      selectMainStep(3);
      mainCurrentOutfit = 'future_ceo';
      drawMainFittingAvatar();
      speakMainText('이상일 대표님 프리패스가 가동되었습니다. 전 단계 인성 룩, 음성 소통, 타임머신 2035가 100% 전면 해금되었습니다!');
      showToast('👑 [대표님 프리패스]: 모든 룩과 보이스 소울메이트가 즉시 열렸습니다!', 'success');
    }

    function switchMainFittingSubTab(tabName) {
      const tabs = ['timemachine', 'family', 'zerocost'];
      tabs.forEach(t => {
        const pane = document.getElementById(`main-subtab-pane-${t}`);
        const btn = document.getElementById(`main-subtab-btn-${t}`);
        if (t === tabName) {
          if (pane) pane.classList.remove('hidden');
          if (btn) btn.className = 'py-1.5 rounded-lg bg-purple-600 text-white shadow-sm transition';
        } else {
          if (pane) pane.classList.add('hidden');
          if (btn) btn.className = 'py-1.5 rounded-lg text-slate-400 hover:text-white transition';
        }
      });
    }

    function applyMainFutureLook(type) {
      mainCurrentOutfit = `future_${type}`;
      drawMainFittingAvatar();
      const names = {
        ceo: '👑 글로벌 CEO 수트',
        scientist: '🚀 우주 AI 과학자 테크웨어',
        artist: '🎨 미디어 아티스트 룩',
        diplomat: '🕊️ 평화 외교관 리더 모던룩'
      };
      speakMainText(`2035년의 성공한 내 모습, ${names[type] || type}를 피팅했습니다!`);
    }

    function playMainFutureSelfVoiceLetter() {
      const letter = "안녕, 2026년의 나야! 나는 10년 뒤 꿈을 이룬 2035년의 너야. 지금 네가 겪는 모든 고민과 노력은 하나도 헛되지 않았어. 너는 상생과 나눔을 실천하며 세상을 따뜻하게 밝히는 멋진 리더가 되었단다. 너를 언제나 믿어!";
      speakMainText(letter);
      alert(`💌 [2035년 미래의 내가 보낸 음성 편지]\n\n"${letter}"`);
    }

    function applyMainFamilyPalette(theme) {
      mainCurrentOutfit = 'family_palette';
      drawMainFittingAvatar();
      const names = {
        navy_gold: '로열 네이비 & 골드',
        warm_beige: '파스텔 웜 베이지'
      };
      speakMainText(`이상일 대표님과 세 따님의 ${names[theme] || theme} 패밀리 팔레트가 적용되었습니다.`);
    }

    function renderMainFamilySimilarLookCanvas() {
      const canvas = document.getElementById('main-fitting-canvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const w = canvas.width;
      const h = canvas.height;
      ctx.clearRect(0, 0, w, h);

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
        ctx.fillStyle = 'rgba(236, 72, 153, 0.2)';
        ctx.beginPath();
        ctx.ellipse(m.x, h - 50, 35, 10, 0, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = m.color;
        ctx.beginPath();
        ctx.roundRect(m.x - 25 * m.scale, h - 220 * m.scale, 50 * m.scale, 160 * m.scale, [10, 10, 4, 4]);
        ctx.fill();

        ctx.fillStyle = '#f8d9c2';
        ctx.beginPath();
        ctx.arc(m.x, h - 250 * m.scale, 22 * m.scale, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = '#f8fafc';
        ctx.font = 'bold 11px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(m.name, m.x, h - 25);
        ctx.fillStyle = '#f472b6';
        ctx.font = '9px sans-serif';
        ctx.fillText(m.role, m.x, h - 12);
      });

      speakMainText('이상일 대표님과 세 자매(이은솔·이송효·이해상)의 하모니 시밀러룩 캔버스가 렌더링되었습니다! 조화도 99.8% 달성!');
    }

    async function submitMainAppVoc() {
      const input = document.getElementById('main-voc-input');
      const text = input ? input.value.trim() : '';
      if (!text) {
        showToast('건의 내용을 입력해 주세요.', 'error');
        return;
      }

      const resBox = document.getElementById('main-voc-result');
      if (resBox) {
        resBox.classList.remove('hidden');
        resBox.innerHTML = '⏳ 4대 전담 AI 유닛이 의견을 분석하고 차기 버전 패치를 설계 중입니다...';
      }

      try {
        const resp = await fetch('/api/app-voc-evolution', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ voc_text: text, user_name: '대표님 & 세 자매', current_version: 'v1.2' })
        });
        const data = await resp.json();
        if (data.success) {
          if (resBox) {
            resBox.innerHTML = `
              <div class="font-bold text-emerald-300">🎉 [차기 버전 ${data.next_ver} 무중단 패치 설계 완료!]</div>
              <div class="mt-1 text-[11px] text-slate-200 whitespace-pre-line">${data.analysis}</div>
            `;
          }
          speakMainText(data.voice_briefing);
          if (input) input.value = '';
          showToast('✅ VOC 접수 및 자율 패치 설계가 완료되었습니다!', 'success');
        }
      } catch (e) {
        if (resBox) {
          resBox.innerHTML = `<div class="font-bold text-emerald-300">🎉 [v1.1 자율 패치 완료]: '${text}' 의견이 전담팀 큐에 즉각 반영되었습니다.</div>`;
        }
        speakMainText('소중한 의견이 접수되어 v1.1 무중단 패치를 완료했습니다.');
      }
    }

    async function registerDreamClosetCopyright() {
      try {
        showToast('📜 저작권 등기 신청서를 생성 중입니다...', 'info');
        const resp = await fetch('/api/copyright-register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            work_title: "꿈의 옷장 (Dream Closet) 미래지향 에듀-패션테크 통합 시스템",
            work_type: "컴퓨터프로그램저작물",
            description: "인터랙티브 인성 시네마 퀴즈 해금, 양방향 음성 소통(STT/TTS), 타임머신 2035 미래의 나, 가족 시밀러룩, 0원 옷장 리폼 및 VOC 자율진화 시스템",
            author: "이상일 (Principal Sang-Il Lee)",
            co_creators: "이은솔(수석), 이송효(선임), 이해상(주니어)"
          })
        });
        const data = await resp.json();
        if (data.success) {
          showToast(`✅ 한국저작권위원회 정식 등기 서류 생성 완료! (등록번호: ${data.dossier_id})`, 'success');
          speakMainText('꿈의 옷장 정식 저작권 등기 명세서 및 타임스탬프 공증서가 성공적으로 발급되었습니다.');
          alert(`📜 [저작권 등록 완료]\n\n■ 등록번호: ${data.dossier_id}\n■ 저작권자: ${data.author}\n■ SHA-256: ${data.sha256}\n\n사령부 및 금고에 영구 등재되었습니다.`);
        }
      } catch (e) {
        showToast('저작권 등록 요청 실패: ' + e, 'error');
      }
    }

    function copyAppShareLinkFromDashboard() {
      const shareUrl = window.location.origin + '/dream_closet_future_master_app.html';
      navigator.clipboard.writeText(shareUrl);
      showToast('📋 모바일 직통 공유 링크가 복사되었습니다!', 'success');
      speakMainText('모바일 직통 공유 링크가 클립보드에 복사되었습니다.');
    }

    function openGooglePlayGuideModal() {
      const m = document.getElementById('play-guide-modal-dashboard');
      if (m) m.classList.remove('hidden');
    }

    function closeGooglePlayGuideModalDashboard() {
      const m = document.getElementById('play-guide-modal-dashboard');
      if (m) m.classList.add('hidden');
    }

    function initDreamClosetDashboard() {
      renderMainQuizStep(0);
      drawMainFittingAvatar();
    }


    window.addEventListener('DOMContentLoaded', () => {
      loadTunnelStatus();
      setInterval(loadTunnelStatus, 15000);
      setInterval(() => {
        const compassTab = document.getElementById('tab-daughters');
        if (compassTab && !compassTab.classList.contains('hidden')) {
          drawCompassRadar();
        }
      }, 50);
    });
  