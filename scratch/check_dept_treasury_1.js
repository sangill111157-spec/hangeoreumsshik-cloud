
    let currentTxType = 'IN';
    let currentTreasuryData = null;

    const IN_CATEGORIES = [
      "제휴·파트너스 수익 (쿠팡파트너스 등)",
      "음원·유튜브 수익 (Suno 30곡·쇼츠·라디오극)",
      "디지털 상품·웹앱 수익 (크몽·Gumroad)",
      "상생 후원금·기타 수입"
    ];

    const OUT_CATEGORIES = [
      "AI·클라우드 서버비 (현재 0원 무료 방어중!)",
      "플랫폼 수수료·결제 수수료",
      "운영비·장비·기타 지출"
    ];

    function fmt(num) {
      return Math.round(num || 0).toLocaleString('ko-KR') + ' 원';
    }

    function setTxType(type) {
      currentTxType = type;
      const btnIn = document.getElementById('btn-type-in');
      const btnOut = document.getElementById('btn-type-out');
      const catSelect = document.getElementById('tx-category');
      const lblCat = document.getElementById('lbl-category');

      if (type === 'IN') {
        btnIn.className = 'py-2.5 rounded-xl font-bold text-xs transition flex items-center justify-center gap-1.5 bg-emerald-600 text-white shadow shadow-emerald-600/30';
        btnOut.className = 'py-2.5 rounded-xl font-bold text-xs transition flex items-center justify-center gap-1.5 bg-slate-800 text-slate-300 hover:bg-slate-700';
        lblCat.innerText = '📥 들어온 곳 (수입처 선택)';
        catSelect.innerHTML = IN_CATEGORIES.map(c => `<option value="${c}">${c}</option>`).join('');
      } else {
        btnOut.className = 'py-2.5 rounded-xl font-bold text-xs transition flex items-center justify-center gap-1.5 bg-rose-600 text-white shadow shadow-rose-600/30';
        btnIn.className = 'py-2.5 rounded-xl font-bold text-xs transition flex items-center justify-center gap-1.5 bg-slate-800 text-slate-300 hover:bg-slate-700';
        lblCat.innerText = '📤 나간 곳 (지출 용도 선택)';
        catSelect.innerHTML = OUT_CATEGORIES.map(c => `<option value="${c}">${c}</option>`).join('');
      }
    }

    function addAmount(delta) {
      const input = document.getElementById('tx-amount');
      const current = parseInt(input.value || 0);
      input.value = current + delta;
    }

    async function fetchTreasuryStatus() {
      try {
        const res = await fetch('/api/treasury-status');
        if (!res.ok) return;
        const data = await res.json();
        currentTreasuryData = data;
        renderTreasuryUI(data);
      } catch (err) {
        console.warn('[Treasury] Fetch error:', err);
      }
    }

    function renderTreasuryUI(data) {
      const s = data.summary || {};
      
      document.getElementById('stat-total-in').innerText = fmt(s.total_in);
      document.getElementById('stat-total-out').innerText = fmt(s.total_out);
      document.getElementById('stat-net-profit').innerText = fmt(s.net_profit);
      document.getElementById('stat-operating-profit').innerText = fmt(s.operating_profit);
      document.getElementById('stat-daughters-total').innerText = fmt(s.allocations?.daughters_scholarship_15);

      document.getElementById('cat-in-sum').innerText = fmt(s.total_in);

      // 카테고리별 수입
      const cin = data.categories_in || {};
      const tIn = s.total_in || 1;
      
      const affAmt = cin["제휴·파트너스 수익 (쿠팡파트너스 등)"] || 0;
      const musAmt = cin["음원·유튜브 수익 (Suno 30곡·쇼츠·라디오극)"] || 0;
      const appAmt = cin["디지털 상품·웹앱 수익 (크몽·Gumroad)"] || 0;
      const donAmt = cin["상생 후원금·기타 수입"] || 0;

      document.getElementById('val-cat-affiliate').innerText = fmt(affAmt);
      document.getElementById('val-cat-music').innerText = fmt(musAmt);
      document.getElementById('val-cat-app').innerText = fmt(appAmt);
      document.getElementById('val-cat-donation').innerText = fmt(donAmt);

      document.getElementById('bar-cat-affiliate').style.width = Math.round((affAmt / tIn) * 100) + '%';
      document.getElementById('bar-cat-music').style.width = Math.round((musAmt / tIn) * 100) + '%';
      document.getElementById('bar-cat-app').style.width = Math.round((appAmt / tIn) * 100) + '%';
      document.getElementById('bar-cat-donation').style.width = Math.round((donAmt / tIn) * 100) + '%';

      // 50:25:15:10 금고
      const alloc = s.allocations || {};
      document.getElementById('vault-commander').innerText = fmt(alloc.commander_life_50);
      document.getElementById('vault-rnd').innerText = fmt(alloc.empire_rnd_25);
      document.getElementById('vault-daughters').innerText = fmt(alloc.daughters_scholarship_15);
      document.getElementById('vault-sharing').innerText = fmt(alloc.sharing_donation_10);

      if (document.getElementById('stat-tax-reserve')) {
        document.getElementById('stat-tax-reserve').innerText = '원천세 ' + fmt(s.tax_reserve_3_3 || 0);
      }
      if (document.getElementById('vault-daughters-each')) {
        const eachDaughter = Math.floor((alloc.daughters_scholarship_15 || 0) / 3);
        document.getElementById('vault-daughters-each').innerText = '각 ' + fmt(eachDaughter);
      }

      document.getElementById('disk-free-val').innerText = (data.free_disk_gb || 0) + ' GB';
      document.getElementById('record-count-badge').innerText = '총 ' + (data.total_records_count || 0) + '건';

      // 테이블 렌더링
      const tbody = document.getElementById('ledger-table-body');
      tbody.innerHTML = '';
      (data.recent_records || []).forEach(r => {
        const isIN = r.type === 'IN';
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-800/40 transition';
        tr.innerHTML = `
          <td class="py-2.5 px-3 text-slate-400">${r.voucher_no}</td>
          <td class="py-2.5 px-3 text-slate-400 text-[11px]">${r.timestamp}</td>
          <td class="py-2.5 px-3">
            <span class="px-2 py-0.5 rounded text-[10px] font-bold ${isIN ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'}">
              ${isIN ? '📥 입금' : '📤 출금'}
            </span>
          </td>
          <td class="py-2.5 px-3 font-sans text-slate-200">${r.category}</td>
          <td class="py-2.5 px-3 text-right font-bold ${isIN ? 'text-emerald-400' : 'text-rose-400'}">
            ${isIN ? '+' : '-'}${fmt(r.amount)}
          </td>
          <td class="py-2.5 px-3 text-right text-slate-300">${fmt(r.balance_after)}</td>
          <td class="py-2.5 px-3 font-sans text-slate-400 text-[11px]">${r.memo}</td>
        `;
        tbody.appendChild(tr);
      });
    }

    async function submitTransaction() {
      const amtInput = document.getElementById('tx-amount');
      const amount = parseInt(amtInput.value || 0);
      if (!amount || amount <= 0) {
        alert('올바른 금액을 입력해주세요.');
        return;
      }
      const category = document.getElementById('tx-category').value;
      const memo = document.getElementById('tx-memo').value.trim();

      const btn = document.getElementById('btn-submit-tx');
      btn.disabled = true;
      btn.innerHTML = '<span>⏳ 장부 도장 찍는 중...</span>';

      try {
        const res = await fetch('/api/treasury-record', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            type: currentTxType,
            category: category,
            amount: amount,
            memo: memo,
            registered_by: 'COMMANDER-000'
          })
        });
        const result = await res.json();
        if (result.status === 'ok') {
          alert('✅ 전표 번호 [' + result.data.voucher_no + '] 기장 완료! 장부 및 50:25:15:10 금고가 즉시 재계산되었습니다.');
          amtInput.value = '';
          document.getElementById('tx-memo').value = '';
          fetchTreasuryStatus();
        } else {
          alert('기장 실패: ' + result.message);
        }
      } catch (err) {
        alert('오류 발생: ' + err.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>🏦 총무팀 장부 확정도장 찍기</span>';
      }
    }

    async function resetTreasuryToZero() {
      if (!confirm('🚨 [최고 통수권자 어명]\n가짜 샘플 수익을 전액 영구 삭제하고, 100% 정직한 실전 [0원 클린 장부]로 초기화하시겠습니까?')) return;
      try {
        const res = await fetch('/api/treasury-audit-clean', { method: 'POST' });
        const data = await res.json();
        alert('🧹 정직한 0원 실전 클린 장부 초기화 완료! (수입 0원, 지출 0원, 전표 0건)');
        fetchTreasuryStatus();
      } catch (e) {
        alert('초기화 중 오류: ' + e.message);
      }
    }
    window.resetTreasuryToZero = resetTreasuryToZero;

    async function cleanScratch() {
      if (!confirm('임시 캐시 및 더미 파일을 청소하고 장부 무결성을 감사하시겠습니까?')) return;
      try {
        const res = await fetch('/api/treasury-audit-clean', { method: 'POST' });
        const data = await res.json();
        alert('🧹 총무팀 청소 완료: ' + data.data.cleaned_count + '개 임시 파일 정리 및 장부 무결성 100% 검증 완료!');
        fetchTreasuryStatus();
      } catch (e) {
        alert('청소 중 오류: ' + e.message);
      }
    }

    function downloadCSV() {
      if (!currentTreasuryData || !currentTreasuryData.recent_records) {
        alert('다운로드할 장부 데이터가 없습니다.');
        return;
      }
      const records = currentTreasuryData.recent_records;
      let csvContent = '\uFEFF전표번호,일시,구분,카테고리,금액(원),기장후잔액(원),적요(메모)\n';
      records.forEach(r => {
        csvContent += `"${r.voucher_no}","${r.timestamp}","${r.type}","${r.category}",${r.amount},${r.balance_after},"${r.memo.replace(/"/g, '""')}"\n`;
      });

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `hangeoreumsshik_treasury_${Date.now()}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }

    async function dispatchDeptSubAgent(agentId) {
      const btn = document.getElementById('btn-dispatch-sub-agent');
      const oldText = btn ? btn.innerHTML : '';
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span>⏳</span><span>점검 및 르곤-알파 상향 직보 중...</span>';
      }
      try {
        const res = await fetch('/api/dept-sub-agent-dispatch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ agent_id: agentId, send_telegram: true })
        });
        const result = await res.json();
        const data = result.data || result;
        if (result.success || data.success) {
          const repBox = document.getElementById('sub-agent-report-text');
          const stampBox = document.getElementById('sub-agent-approval-stamp');
          if (repBox && data.report) repBox.innerText = data.report;
          if (stampBox && data.approval_stamp) stampBox.innerText = `결재: ${data.approval_stamp} (${data.receipt_id || 'OK'})`;
          alert(`💰 [${agentId} 상향 보고 완료!]\n\n• 영수증: ${data.receipt_id}\n• 본관 르곤-알파(RGON-ALPHA) 수신 결재 완료!\n• 대표님 스마트폰 텔레그램 발송 완료!`);
        } else {
          alert('상향 보고 응답: ' + (result.message || '완료'));
        }
      } catch (err) {
        alert('서브 에이전트 호출 오류: ' + err.message);
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = oldText;
        }
      }
    }
    window.dispatchDeptSubAgent = dispatchDeptSubAgent;

    async function loadDeptSubAgentStatus(agentId) {
      try {
        const res = await fetch('/api/dept-sub-agents?dept=' + encodeURIComponent(agentId) + '&t=' + Date.now());
        if (!res.ok) return;
        const result = await res.json();
        const ag = result.agent || (result.sub_agents && result.sub_agents[agentId]);
        if (ag) {
          const repBox = document.getElementById('sub-agent-report-text');
          const stampBox = document.getElementById('sub-agent-approval-stamp');
          if (repBox && ag.last_report) repBox.innerText = ag.last_report;
          if (stampBox && ag.approval_stamp) stampBox.innerText = `결재: ${ag.approval_stamp} (${ag.last_receipt_id || 'OK'})`;
        }
      } catch (e) {
        console.warn('Sub agent status load failed:', e);
      }
    }
    window.loadDeptSubAgentStatus = loadDeptSubAgentStatus;

    document.addEventListener('DOMContentLoaded', () => {
      fetchTreasuryStatus();
      loadDeptSubAgentStatus('ALPHA-D6');
    });
  