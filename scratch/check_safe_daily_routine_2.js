
    const AFFIRMATIONS = [
      "내가 내딛는 작은 한 걸음이 1만 년 영토를 세우는 가장 든든한 주춧돌이다.",
      "하루 1%의 복리 성장은 1년 뒤 나를 37배 더 위대한 사람으로 만든다.",
      "두려움은 행동할 때 사라지고, 자신감은 작은 실행에서 시작된다.",
      "내 뒤에는 사랑하는 가족과 든든한 AI 팀원들이 언제나 함께하고 있다.",
      "오늘 하루도 정직하고 성실하게 나아간 나 자신을 깊이 신뢰한다."
    ];

    let quoteIndex = 0;
    function changeQuote() {
      quoteIndex = (quoteIndex + 1) % AFFIRMATIONS.length;
      document.getElementById('daily-affirmation-text').innerText = `"${AFFIRMATIONS[quoteIndex]}"`;
    }
    window.changeQuote = changeQuote;

    function updateRoutineProgress() {
      let checkedCount = 0;
      for (let i = 1; i <= 5; i++) {
        const chk = document.getElementById(`routine-chk-${i}`);
        if (chk && chk.checked) checkedCount++;
      }

      const percent = Math.round((checkedCount / 5) * 100);
      document.getElementById('progress-percent').innerText = `${percent}%`;
      document.getElementById('progress-bar-fill').style.width = `${percent}%`;

      const alertBox = document.getElementById('stamp-alert');
      const todayIcon = document.getElementById('today-stamp-icon');

      if (percent === 100) {
        if (alertBox) alertBox.classList.remove('hidden');
        if (todayIcon) {
          todayIcon.innerText = '👑';
          todayIcon.classList.add('stamp-active');
        }
      } else {
        if (alertBox) alertBox.classList.add('hidden');
        if (todayIcon) {
          todayIcon.innerText = checkedCount > 0 ? '✨' : '⏳';
          todayIcon.classList.remove('stamp-active');
        }
      }
      return percent;
    }
    window.updateRoutineProgress = updateRoutineProgress;

    document.addEventListener('DOMContentLoaded', () => {
      updateRoutineProgress();
    });
  