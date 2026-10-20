
    let currentMood = 'peaceful';

    const COLOR_DATABASE = {
      spring: {
        peaceful: { score: 92, color: '에메랄드 그린', hex: '#10b981', tip: '화사한 세이지 그린 톤 셔츠나 머플러가 마음에 봄바람 같은 평온을 선사합니다.', quote: '새싹이 땅을 뚫고 솟아나듯, 대표님의 생각도 오늘 힘차게 피어납니다.' },
        motivated: { score: 98, color: '선샤인 옐로우', hex: '#f59e0b', tip: '생동감 넘치는 옐로우 포인트 양말이나 필기구가 당신의 실행력을 끌어올립니다.', quote: '빛은 어둠을 이깁니다. 오늘 품으신 비전이 그대로 현실이 됩니다.' },
        tired: { score: 85, color: '민트 스카이', hex: '#06b6d4', tip: '시원하고 맑은 민트 블루 티셔츠나 차 한 잔이 머리를 맑게 식혀줍니다.', quote: '잠시 쉬어가는 것도 전진의 일부입니다. 편안한 숨을 들이마셔 보세요.' },
        seeking: { score: 90, color: '스프링 라벤더', hex: '#a855f7', tip: '창의적인 연보라빛 스카프나 배경화면이 새로운 영감을 불어넣어 줍니다.', quote: '작은 호기심 하나가 위대한 혁신의 시작입니다.' }
      },
      summer: {
        peaceful: { score: 91, color: '오션 블루', hex: '#3b82f6', tip: '넓고 깊은 바다 같은 네이비 셔츠가 단단한 내면의 중심을 잡아줍니다.', quote: '깊은 바다는 파도에 흔들리지 않습니다. 당신의 신념은 견고합니다.' },
        motivated: { score: 99, color: '비비드 오렌지', hex: '#f97316', tip: '강렬한 오렌지 계열 액센트가 지치지 않는 열정 에너지를 공급합니다.', quote: '지금 품은 불꽃은 제국의 1만 년 영토를 밝힐 등대입니다.' },
        tired: { score: 84, color: '소프트 아이보리', hex: '#f8fafc', tip: '부드러운 크림 아이보리 린넨이 온몸의 긴장을 사르르 풀어줍니다.', quote: '자연스러운 쉼이 가장 빠른 회복입니다. 오늘도 충분히 잘 해내셨습니다.' },
        seeking: { score: 93, color: '코랄 핑크', hex: '#ec4899', tip: '사랑스럽고 경쾌한 핑크빛 소품이 사람들과의 대화를 즐겁게 만듭니다.', quote: '밝은 미소는 가장 강력한 자석입니다.' }
      },
      autumn: {
        peaceful: { score: 94, color: '어텀 베이지 & 브라운', hex: '#854d0e', tip: '따뜻한 카멜 코트나 우드 브라운 시계가 품격과 신뢰감을 높여줍니다.', quote: '익어가는 곡식처럼 대표님의 지혜는 날마다 무르익고 있습니다.' },
        motivated: { score: 96, color: '딥 버건디', hex: '#991b1b', tip: '차분하면서도 강력한 와인 버건디 넥타이나 가방이 결단력을 돕습니다.', quote: '단단한 결심은 그 어떤 바람에도 흔들리지 않습니다.' },
        tired: { score: 86, color: '웜 그레이', hex: '#64748b', tip: '단정하고 편안한 차콜 그레이 카디건이 마음에 보호막을 쳐줍니다.', quote: '오늘 하루도 당신의 성실함이 든든한 주춧돌을 놓았습니다.' },
        seeking: { score: 91, color: '올리브 카키', hex: '#65a30d', tip: '자연을 품은 올리브 카키 재킷이 도심 속에서도 숲속의 안식을 줍니다.', quote: '자연의 순리대로 한 걸음씩 나아가면 반드시 정상에 닿습니다.' }
      },
      winter: {
        peaceful: { score: 93, color: '클래식 네이비', hex: '#1e3a8a', tip: '정갈하고 깊이 있는 네이비 수트나 니트가 지적인 카리스마를 더합니다.', quote: '침묵 속에서 가장 위대한 생각이 잉태됩니다.' },
        motivated: { score: 97, color: '루비 레드', hex: '#dc2626', tip: '겨울 눈밭 위의 동백꽃처럼 선명한 레드 머플러가 시선을 사로잡습니다.', quote: '추운 겨울을 견뎌낸 씨앗만이 찬란한 봄꽃을 피웁니다.' },
        tired: { score: 87, color: '스노우 화이트', hex: '#ffffff', tip: '순수하고 깨끗한 화이트 셔츠가 모든 잡념을 비워내고 맑음을 선사합니다.', quote: '마음을 비우면 가장 소중한 지혜가 맑게 채워집니다.' },
        seeking: { score: 92, color: '미드나잇 퍼플', hex: '#581c87', tip: '신비롭고 우아한 퍼플빛 액세서리가 예리한 직관을 깨워줍니다.', quote: '당신 안에 이미 모든 해답의 열쇠가 들어있습니다.' }
      }
    };

    function selectMood(mood, btn) {
      currentMood = mood;
      document.querySelectorAll('.mood-btn').forEach(b => {
        b.classList.remove('border-emerald-500', 'bg-emerald-950/40', 'text-emerald-300');
        b.classList.add('bg-slate-800', 'text-slate-200');
      });
      btn.classList.add('border-emerald-500', 'bg-emerald-950/40', 'text-emerald-300');
      btn.classList.remove('bg-slate-800', 'text-slate-200');
    }

    function calculateDailyLucky() {
      const season = document.getElementById('birth-season').value;
      const data = COLOR_DATABASE[season][currentMood] || COLOR_DATABASE.spring.peaceful;

      document.getElementById('vital-score').innerText = data.score + '%';
      document.getElementById('vital-bar').style.width = data.score + '%';
      document.getElementById('color-badge').innerText = data.color;
      document.getElementById('color-preview').style.backgroundColor = data.hex;
      document.getElementById('style-title').innerText = '오늘 당신을 밝혀줄 ' + data.color + ' 스타일';
      document.getElementById('style-tip').innerText = data.tip;
      document.getElementById('quote-text').innerText = '"' + data.quote + '"';
      
      // 제휴 링크 매핑 (실제 대표님 링크로 치환 가능)
      const partnerLink = document.getElementById('partner-link');
      partnerLink.href = 'https://link.coupang.com/a/sample_search?keyword=' + encodeURIComponent(data.color + ' 소품');
    }

    function shareResult() {
      const quote = document.getElementById('quote-text').innerText;
      const color = document.getElementById('color-badge').innerText;
      const text = `[한걸음씩 오늘의 긍정 에너지 가이드]\n🎨 오늘의 행운 컬러: ${color}\n💌 ${quote}\n※ 일상 힐링용 무료 웹앱: ${window.location.href}`;
      
      if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
          alert('📋 오늘의 응원 카드가 복사되었습니다! 소중한 분들에게 따뜻하게 전해보세요.');
        });
      } else {
        alert(text);
      }
    }

    // 초기 실행
    document.addEventListener('DOMContentLoaded', calculateDailyLucky);
  