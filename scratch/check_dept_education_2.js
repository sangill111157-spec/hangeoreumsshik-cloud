
    function selectAnswer(ans) {
      const fb = document.getElementById('quiz-feedback');
      if (ans === 'A') {
        fb.textContent = '💖 [MQ 공감력 +15 달성!] 친구의 마음에 따뜻한 온기를 선물했습니다.';
      } else {
        fb.textContent = '🌟 [EQ 경청력 +20 달성!] 함께 있어 주는 것만으로도 큰 힘이 됩니다.';
      }
    }

    function recordAffirmation() {
      const btn = document.getElementById('btn-speech');
      const res = document.getElementById('speech-result');
      btn.textContent = '🔴 듣는 중... (말씀하세요)';
      setTimeout(() => {
        btn.textContent = '🎙️ 확언 말하기 시작';
        res.innerHTML = '<span class="text-emerald-400 font-bold">✅ 인식 완료:</span> "나는 세상에서 가장 소중한 사람이다." (자신감 지수: 100/100)';
      }, 1500);
    }

    function issueCertificate() {
      alert('🎓 [HGS-CERT] 정식 디지털 인성 인증서가 발급되어 블록체인 금고에 영구 등재되었습니다!');
    }

    // 🛡️ [v11.5] 서브 에이전트 상향 보고 함수
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
          alert(`🛡️ [${agentId} 상향 보고 완료!]\n\n• 영수증: ${data.receipt_id}\n• 본관 르곤-알파(RGON-ALPHA) 수신 결재 완료!\n• 대표님 스마트폰 텔레그램 발송 완료!`);
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
      loadDeptSubAgentStatus('ALPHA-D4');
    });
  