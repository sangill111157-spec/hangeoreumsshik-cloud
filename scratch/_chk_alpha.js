
    // ═══════════════════════════════════════════════════════════════════
    // 🛰️ [v11.6.1] 르곤-알파 독대실 무중단 스마트 통신 엔진
    //  1단계: 같은 서버(/api) → JSON인지 Content-Type 확인
    //  2단계: tunnel_bridge.json 의 살아있는 5G 터널 주소로 자동 재시도
    //  3단계: 내장 지능 엔진(최신 원장 스냅샷)으로 즉시 응답 — 에러 팝업 0%
    // ═══════════════════════════════════════════════════════════════════
    let isSubmitting = false;
    let tunnelBaseCache = null;
    let lastServerMessages = null;
    let currentMode = 'checking';

    const LS_SERVER_CACHE = 'rgon_alpha_chat_server_cache_v1';
    const LS_OFFLINE_MSGS = 'rgon_alpha_chat_offline_v1';

    // 📦 내장 원장 스냅샷 (2026-10-19 11:20 검수 기준)
    const ALPHA_SNAPSHOT = {
      taken_at: '2026-10-19 11:20',
      button_audit: { screens: 9, total: 210, passed: 210, dummy: 0, stamp: 'RGON_ALPHA_100%_VERIFIED' },
      nvda_mock_asset: '$107,246.38',
      youtube: ['@한걸음씩-r4i', '@Booster_Playlist', '@TheCaféHour'],
      tiktok: '@boosterplaylist 팔로워 2,098명 · 좋아요 8,793개',
      treasury: { in: 0, out: 0, net: 0 },
      sub_agents: {
        'ALPHA-D1': { name: '알파-퀀트', report: 'NVDA 모의자산 $107,246.38 · 4대 혈관 개통' },
        'ALPHA-D2': { name: '알파-바이럴', report: '홍보 카피·BM 시뮬레이터 정상' },
        'ALPHA-D3': { name: '알파-미디어', report: '유튜브 3채널 · 틱톡 2,098명' },
        'ALPHA-D4': { name: '알파-홍익', report: '인성 헌법 100/100점 감찰' },
        'ALPHA-D5': { name: '알파-가디언', report: '보안키 노출 0.00% · 시트 5종 85탭' },
        'ALPHA-D6': { name: '알파-트레저리', report: '실전 금고 0원 / 0원 / 0원' }
      }
    };

    // ── 연결 상태 배지 ──
    function setConnMode(mode) {
      currentMode = mode;
      const label = document.getElementById('conn-label');
      const dot = document.getElementById('conn-dot');
      const wrap = document.getElementById('conn-status');
      if (!label || !dot || !wrap) return;
      const map = {
        checking: ['연결 확인 중...', 'bg-slate-400', 'text-slate-300'],
        direct:   ['🟢 서버 직결 · 실시간 두뇌', 'bg-emerald-400', 'text-emerald-400'],
        tunnel:   ['🟡 5G 터널 경유 · 실시간 두뇌', 'bg-amber-400', 'text-amber-300'],
        offline:  ['📴 내장 지능 모드 (스냅샷)', 'bg-sky-400', 'text-sky-300']
      };
      const [txt, dotCls, txtCls] = map[mode] || map.checking;
      label.textContent = txt;
      dot.className = 'w-2 h-2 rounded-full animate-pulse shrink-0 ' + dotCls;
      wrap.className = 'flex items-center gap-1 font-medium ' + txtCls;
    }

    // ── 타임아웃 fetch ──
    function fetchWithTimeout(url, opts, ms) {
      const ctrl = new AbortController();
      const timer = setTimeout(() => ctrl.abort(), ms);
      return fetch(url, Object.assign({}, opts || {}, { signal: ctrl.signal }))
        .finally(() => clearTimeout(timer));
    }

    // ── tunnel_bridge.json 에서 살아있는 터널 주소 읽기 ──
    async function getTunnelBase() {
      if (tunnelBaseCache !== null) return tunnelBaseCache;
      tunnelBaseCache = '';
      for (const f of ['./tunnel_bridge.json', './active_external_tunnel.json']) {
        try {
          const r = await fetchWithTimeout(f + '?t=' + Date.now(), { cache: 'no-store' }, 5000);
          const ct = (r.headers.get('content-type') || '').toLowerCase();
          if (!r.ok) continue;
          const txt = await r.text();
          if (txt.trim().startsWith('<')) continue;
          const j = JSON.parse(txt);
          const u = (j.active_tunnel_url || j.tunnel_url || '').replace(/\/+$/, '');
          if (u.startsWith('https://') && u !== location.origin) { tunnelBaseCache = u; break; }
        } catch (e) { /* 다음 후보 */ }
      }
      return tunnelBaseCache;
    }

    // ── 응답이 진짜 JSON 일 때만 파싱 (HTML이면 null) ──
    async function parseJsonSafely(res) {
      if (!res || !res.ok) return null;
      const ct = (res.headers.get('content-type') || '').toLowerCase();
      const txt = await res.text();
      if (!ct.includes('application/json') && txt.trim().startsWith('<')) return null;
      try { return JSON.parse(txt); } catch (e) { return null; }
    }

    // ── 1단계(같은 서버) → 2단계(5G 터널) 순차 시도, 실패 시 null ──
    async function smartApi(path, opts, timeoutMs) {
      const isStaticHost = /github\.io$/i.test(location.hostname) || location.protocol === 'file:';
      const bases = [];
      if (!isStaticHost) bases.push({ base: '', mode: 'direct' });
      const tb = await getTunnelBase();
      if (tb) bases.push({ base: tb, mode: 'tunnel' });

      for (const b of bases) {
        try {
          const res = await fetchWithTimeout(b.base + path, opts, timeoutMs || 10000);
          const data = await parseJsonSafely(res);
          if (data) { setConnMode(b.mode); return data; }
        } catch (e) { /* 다음 경로로 */ }
      }
      setConnMode('offline');
      return null;
    }

    // ── localStorage 보존 ──
    function lsGet(key, fallback) {
      try { const v = localStorage.getItem(key); return v ? JSON.parse(v) : fallback; } catch (e) { return fallback; }
    }
    function lsSet(key, val) {
      try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) { /* 저장공간 부족 무시 */ }
    }

    function nowStr() {
      const d = new Date();
      const p = n => String(n).padStart(2, '0');
      return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
    }

    // ── 3단계: 내장 지능 엔진 (스냅샷 기반 즉시 응답) ──
    function localAlphaBrain(text, actionKey) {
      const s = ALPHA_SNAPSHOT;
      const t = (text || '').replace(/\s+/g, '');
      const lines = [];
      if (actionKey === 'SUB_AGENTS_REPORT' || /서브|검수|보고|현황/.test(t)) {
        lines.push('충성! 대표님, 6대 청사 서브에이전트 종합 보고 올립니다.');
        Object.entries(s.sub_agents).forEach(([id, a]) => lines.push(`• ${id} ${a.name}: ${a.report}`));
      } else if (actionKey === 'BUTTON_AUDIT' || /버튼|감사|클릭/.test(t)) {
        const b = s.button_audit;
        lines.push('충성! 최근 버튼 감사 결과입니다.');
        lines.push(`• 점검 화면: ${b.screens}개 · 버튼: ${b.total}개`);
        lines.push(`• 정상: ${b.passed}개 · 무늬만 버튼: ${b.dummy}개`);
        lines.push(`• 결재: ${b.stamp}`);
      } else if (actionKey === 'QUANT_MEDIA_BRIEF' || /엔비디아|NVDA|퀀트|유튜브|틱톡|미디어/i.test(t)) {
        lines.push('충성! 1청사 퀀트 & 3청사 미디어 브리핑입니다.');
        lines.push(`• 📈 NVDA 모의투자 자산: ${s.nvda_mock_asset} (실전 금고와 분리)`);
        lines.push(`• 🎵 유튜브 3채널: ${s.youtube.join(', ')}`);
        lines.push(`• 🎵 틱톡: ${s.tiktok}`);
      } else if (actionKey === 'GRAND_RELAY' || /릴레이|출격|합동/.test(t)) {
        lines.push('대표님, 지금은 서버와 연결이 잠시 끊겨 있어 릴레이를 실제로 출격시키지 못했습니다.');
        lines.push('• 서버(또는 5G 터널)가 다시 연결되면 같은 버튼을 한 번 더 눌러 주십시오. 그때 실제로 출격합니다.');
      } else if (/금고|재무|돈|수입/.test(t)) {
        lines.push(`• 💰 제6청사 실전 금고: 총수입 ${s.treasury.in}원 / 총지출 ${s.treasury.out}원 / 순익 ${s.treasury.net}원 (변동 없음)`);
      } else {
        lines.push('충성! 대표님 말씀 잘 받았습니다.');
        lines.push('• 지금은 서버 두뇌와 연결이 잠시 끊겨, 내장 스냅샷으로만 답변드릴 수 있습니다.');
        lines.push('• 상단 지휘 칩(서브에이전트 보고 · 버튼 감사 · 퀀트/미디어 브리핑)은 바로 답변 가능합니다.');
        lines.push('• 연결이 돌아오면 이 질문을 다시 보내 주시면 실시간 AI 두뇌로 답변드리겠습니다.');
      }
      lines.push('');
      lines.push(`※ 📴 내장 지능 모드 응답 — ${s.taken_at} 기준 스냅샷입니다.`);
      return {
        id: 'LOCAL-' + Date.now(),
        role: 'assistant',
        sender_id: 'RGON-ALPHA',
        timestamp: nowStr(),
        text: lines.join('\n'),
        sub_agents_snapshot: s.sub_agents,
        receipt_id: '#LOCAL-' + Date.now(),
        approval_stamp: '📴 내장 스냅샷',
        offline: true
      };
    }

    // 1. 대화 원장 로드 및 렌더링
    async function loadAlphaChat() {
      const data = await smartApi('/api/rgon-alpha-chat?t=' + Date.now(), { cache: 'no-store' }, 8000);
      if (data && Array.isArray(data.messages)) {
        lastServerMessages = data.messages;
        lsSet(LS_SERVER_CACHE, data.messages.slice(-60));
      }
      const base = lastServerMessages || lsGet(LS_SERVER_CACHE, []);
      const offline = lsGet(LS_OFFLINE_MSGS, []);
      renderChatMessages(base.concat(offline));
    }

    // 2. 메시지 스트림 렌더링
    function renderChatMessages(messages) {
      const stream = document.getElementById('alpha-exclusive-chat-stream');
      if (!stream) return;

      if (!messages || messages.length === 0) {
        stream.innerHTML = `
          <div class="p-8 text-center text-slate-500 space-y-2">
            <span class="text-3xl">🛰️</span>
            <p class="text-xs">대표님과의 1:1 전담 독대실에 오신 것을 환영합니다.<br>상단 지휘 칩을 누르시거나 아래 입력창에 명령을 하달해 주십시오.</p>
          </div>
        `;
        return;
      }

      let html = '';
      messages.forEach(m => {
        const isUser = (m.role === 'user' || m.sender_id === 'COMMANDER-000');

        if (isUser) {
          html += `
            <div class="flex items-start justify-end gap-2.5 ml-auto max-w-[85%] sm:max-w-[75%]">
              <div class="p-3.5 rounded-2xl rounded-tr-none bg-gradient-to-br from-amber-950/80 via-slate-900/90 to-amber-900/60 border border-amber-500/40 text-xs sm:text-sm text-slate-100 space-y-1.5 shadow-lg shadow-amber-950/20">
                <div class="flex items-center justify-end gap-2">
                  <span class="text-[10px] text-amber-400 font-mono">${escapeHtml(m.timestamp || '')}</span>
                  <span class="font-extrabold text-amber-300 text-xs">👑 이상일 대표님</span>
                </div>
                <div class="whitespace-pre-line leading-relaxed font-sans">${escapeHtml(m.text)}</div>
              </div>
              <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-amber-600 to-yellow-500 flex items-center justify-center text-xs shrink-0 shadow-md ring-2 ring-amber-400/40">👑</div>
            </div>
          `;
        } else {
          let snapshotHtml = '';
          if (m.sub_agents_snapshot && Object.keys(m.sub_agents_snapshot).length > 0) {
            snapshotHtml = `
              <div class="mt-2.5 pt-2 border-t border-slate-800 space-y-1.5">
                <div class="text-[10px] font-bold text-indigo-300 flex items-center gap-1">
                  <span>📡</span><span>6대 청사 서브에이전트 보좌 지표</span>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-3 gap-1.5 text-[10px]">
            `;
            for (const [sid, sinfo] of Object.entries(m.sub_agents_snapshot)) {
              snapshotHtml += `
                <div class="p-1.5 rounded bg-slate-950/70 border border-slate-800 min-w-0">
                  <div class="font-bold text-slate-300 font-mono truncate">${escapeHtml(sid)} (${escapeHtml(sinfo.name || '')})</div>
                  <div class="text-emerald-400 text-[9px] truncate">${escapeHtml(sinfo.report || sinfo.metric || '정상 상주')}</div>
                </div>
              `;
            }
            snapshotHtml += `</div></div>`;
          }
          const offlineBadge = m.offline
            ? '<span class="px-1.5 py-0.5 rounded text-[9px] bg-sky-500/20 text-sky-300 border border-sky-500/40" style="white-space:nowrap;">📴 내장 지능</span>'
            : '';

          html += `
            <div class="flex items-start gap-2.5 mr-auto max-w-[90%] sm:max-w-[85%]">
              <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-600 flex items-center justify-center text-xs shrink-0 shadow-md ring-2 ring-indigo-400/40">🛰️</div>
              <div class="p-4 rounded-2xl rounded-tl-none bg-slate-900/90 border border-indigo-500/30 text-xs sm:text-sm text-slate-200 space-y-2 shadow-xl shadow-indigo-950/20 min-w-0">
                <div class="flex items-center justify-between gap-2 border-b border-slate-800 pb-1.5">
                  <div class="flex items-center gap-1.5">
                    <span class="font-extrabold text-indigo-300 text-xs" style="white-space:nowrap;">🛰️ 르곤-알파</span>
                    ${offlineBadge}
                  </div>
                  <span class="text-[10px] text-slate-500 font-mono">${escapeHtml(m.timestamp || '')}</span>
                </div>
                <div class="whitespace-pre-line leading-relaxed font-sans text-slate-200">${escapeHtml(m.text)}</div>
                ${snapshotHtml}
                <div class="pt-1.5 flex items-center justify-between gap-2 text-[10px] text-slate-500 border-t border-slate-800/80 font-mono">
                  <span class="truncate">영수증: ${escapeHtml(m.receipt_id || '-')}</span>
                  <span class="text-amber-400 font-bold shrink-0">${escapeHtml(m.approval_stamp || '')}</span>
                </div>
              </div>
            </div>
          `;
        }
      });

      stream.innerHTML = html;
      stream.scrollTop = stream.scrollHeight;
    }

    // 3. 메시지 전송 처리
    async function handleChatSubmit(e) {
      if (e) e.preventDefault();
      const input = document.getElementById('chat-input-box');
      if (!input || !input.value.trim() || isSubmitting) return;
      const text = input.value.trim();
      input.value = '';
      await sendMessage(text);
    }

    // 4. 원터치 칩 액션 처리
    async function sendChipAction(actionKey) {
      if (isSubmitting) return;
      const actionNames = {
        'SUB_AGENTS_REPORT': '6대 서브에이전트 검수결과 종합보고 받아라',
        'BUTTON_AUDIT': '무늬만 버튼 0% 전수 클릭감사 즉시실행',
        'QUANT_MEDIA_BRIEF': '1청사 엔비디아($107K) & 3청사 유튜브·틱톡 현황 브리핑',
        'GRAND_RELAY': '전 기관(1~6청사) 합동 릴레이 즉시 출격시켜라',
        'CLEAR_CHAT': '대화 내역 깔끔히 비우기'
      };
      const text = actionNames[actionKey] || actionKey;
      await sendMessage(text, actionKey);
    }

    // 5. 공통 전송 함수 (에러 팝업 0% — 실패 시 내장 지능 엔진으로 즉시 응답)
    async function sendMessage(text, actionType = '') {
      isSubmitting = true;
      const sendBtn = document.getElementById('btn-chat-send');
      const oldHtml = sendBtn ? sendBtn.innerHTML : '';
      if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<span>⏳</span><span>알파 처리중...</span>';
      }

      try {
        const result = await smartApi('/api/rgon-alpha-chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, action: actionType })
        }, 45000);

        if (result && (result.success || result.status === 'OK')) {
          if (actionType === 'CLEAR_CHAT') lsSet(LS_OFFLINE_MSGS, []);
          await loadAlphaChat();
        } else {
          // 📴 3단계: 내장 지능 엔진 즉시 응답 (localStorage 보존)
          if (actionType === 'CLEAR_CHAT') {
            lsSet(LS_OFFLINE_MSGS, []);
            lsSet(LS_SERVER_CACHE, []);
            lastServerMessages = [];
          } else {
            const offline = lsGet(LS_OFFLINE_MSGS, []);
            offline.push({ id: 'LOCAL-U-' + Date.now(), role: 'user', sender_id: 'COMMANDER-000', timestamp: nowStr(), text: text, offline: true });
            offline.push(localAlphaBrain(text, actionType));
            lsSet(LS_OFFLINE_MSGS, offline.slice(-40));
          }
          const base = lastServerMessages || lsGet(LS_SERVER_CACHE, []);
          renderChatMessages(base.concat(lsGet(LS_OFFLINE_MSGS, [])));
        }
      } catch (err) {
        console.warn('독대실 전송 예외(화면 팝업 없음):', err);
      } finally {
        isSubmitting = false;
        if (sendBtn) {
          sendBtn.disabled = false;
          sendBtn.innerHTML = oldHtml;
        }
      }
    }

    function escapeHtml(str) {
      if (str === null || str === undefined) return '';
      return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }
    window.sendQuickCommand = sendChipAction;
    window.sendChipAction = sendChipAction;
    window.handleChatSubmit = handleChatSubmit;

    document.addEventListener('DOMContentLoaded', () => {
      loadAlphaChat();
      // 8초 간격 최신 대화 자동 동기화 (전송 중에는 건너뜀)
      setInterval(() => { if (!isSubmitting) loadAlphaChat(); }, 8000);
    });
  