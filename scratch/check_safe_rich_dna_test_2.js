
    const ARCHETYPES = {
      A: {
        badge: "👑",
        title: "황금 복리 설계자형 (The Compound Master)",
        dna: "DNA-COMPOUND-GOLD",
        desc: "시간의 마법과 원칙을 깊이 신뢰하는 현자형 자산가입니다. 단기 유행이나 소음에 흔들리지 않고 우량한 자산을 꾸준히 모아가며, 마침내 거대한 복리의 기적을 맛보게 됩니다. 2026년은 그동안 다져온 주춧돌 위에서 기하급수적 성장이 시작되는 황금기입니다!"
      },
      B: {
        badge: "🚀",
        title: "혁신 시너지 개척자형 (The Pioneer Builder)",
        dna: "DNA-LEVERAGE-GROWTH",
        desc: "새로운 기술과 AI 자동화 시스템의 잠재력을 한발 앞서 꿰뚫어보는 모험가형 자산가입니다. 작은 자본이라도 지혜와 레버리지를 결합하여 10배, 100배의 부가가치를 창출해내는 천재적인 사업가 DNA를 가지고 있습니다!"
      },
      C: {
        badge: "🛡️",
        title: "무결점 금고 수호자형 (The Fortress Guardian)",
        dna: "DNA-ZERO-RISK-SHIELD",
        desc: "공격보다 완벽한 방어가 위대한 승리를 만든다는 워런 버핏의 제1원칙을 체화한 수호자형 자산가입니다. 들어오는 돈과 나가는 돈을 1원 단위까지 꼼꼼히 살피고 새는 구멍을 완벽히 차단하여 어떤 경제 위기에도 흔들리지 않는 1만 년 철옹성을 구축합니다!"
      }
    };

    let latestResultText = "";

    function runRichDnaAnalysis() {
      const q1 = document.querySelector('input[name="q1"]:checked')?.value || 'A';
      const q2 = document.querySelector('input[name="q2"]:checked')?.value || 'A';
      const q3 = document.querySelector('input[name="q3"]:checked')?.value || 'A';
      const q4 = document.querySelector('input[name="q4"]:checked')?.value || 'A';
      const q5 = document.querySelector('input[name="q5"]:checked')?.value || 'A';

      const counts = { A: 0, B: 0, C: 0 };
      [q1, q2, q3, q4, q5].forEach(v => counts[v] = (counts[v] || 0) + 1);

      let primaryType = 'A';
      if (counts.B > counts.A && counts.B >= counts.C) primaryType = 'B';
      else if (counts.C > counts.A && counts.C > counts.B) primaryType = 'C';

      const result = ARCHETYPES[primaryType] || ARCHETYPES.A;

      document.getElementById('result-badge').innerText = result.badge;
      document.getElementById('result-title').innerText = result.title;
      document.getElementById('result-dna-code').innerText = result.dna;
      document.getElementById('result-desc').innerText = result.desc;

      document.getElementById('quiz-container').classList.add('hidden');
      document.getElementById('result-card').classList.remove('hidden');

      latestResultText = `[💎 2026 나의 부자 DNA 결과]\n유형: ${result.badge} ${result.title}\n코드: ${result.dna}\n설명: ${result.desc}\n※ 무료 클린룸 테스트: ${window.location.href}`;
    }
    window.runRichDnaAnalysis = runRichDnaAnalysis;

    function copyResultToClipboard() {
      if (!latestResultText) return;
      if (navigator.clipboard) {
        navigator.clipboard.writeText(latestResultText).then(() => {
          alert('📋 결과 카드가 클립보드에 복사되었습니다! 카카오톡이나 SNS에 공유해보세요.');
        }).catch(() => {
          alert(latestResultText);
        });
      } else {
        alert(latestResultText);
      }
    }
    window.copyResultToClipboard = copyResultToClipboard;

    function resetTest() {
      document.getElementById('quiz-container').classList.remove('hidden');
      document.getElementById('result-card').classList.add('hidden');
    }
    window.resetTest = resetTest;
  