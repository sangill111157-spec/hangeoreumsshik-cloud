
    function fmt(num) {
      return Math.round(num).toLocaleString('ko-KR') + ' 원';
    }

    function calculateSalaryAndSavings() {
      const gross = parseFloat(document.getElementById('monthly-salary').value) || 0;
      const meal = parseFloat(document.getElementById('tax-free-meal').value) || 0;
      const years = parseFloat(document.getElementById('work-years').value) || 1;

      const taxable = Math.max(0, gross - meal);

      // 2026년 기준 공제 요율
      const pension = Math.min(taxable * 0.045, 265500); // 국민연금 상한 적용
      const health = taxable * 0.03545;
      const care = health * 0.1295;
      const employ = taxable * 0.009;

      // 간이세액 추정 (소득 구간별 근사치)
      let incomeTax = 0;
      if (taxable > 5000000) incomeTax = taxable * 0.06;
      else if (taxable > 3000000) incomeTax = taxable * 0.03;
      else if (taxable > 1500000) incomeTax = taxable * 0.015;
      else incomeTax = taxable * 0.005;

      const localTax = incomeTax * 0.1;
      const totalDeduction = pension + health + care + employ + incomeTax + localTax;
      const net = Math.max(0, gross - totalDeduction);

      // 퇴직금 계산 (1년 이상 근무 시 1년당 1개월분 급여)
      const severance = gross * years;

      document.getElementById('net-salary').innerText = fmt(net);
      document.getElementById('total-deduction').innerText = fmt(totalDeduction);
      document.getElementById('deduct-pension').innerText = fmt(pension);
      document.getElementById('deduct-health').innerText = fmt(health);
      document.getElementById('deduct-care').innerText = fmt(care);
      document.getElementById('deduct-employ').innerText = fmt(employ);

      document.getElementById('label-years').innerText = years;
      document.getElementById('severance-pay').innerText = fmt(severance);

      // 50:25:15:10 가계 배분
      document.getElementById('ratio-50').innerText = fmt(net * 0.50);
      document.getElementById('ratio-25').innerText = fmt(net * 0.25);
      document.getElementById('ratio-15').innerText = fmt(net * 0.15);
      document.getElementById('ratio-10').innerText = fmt(net * 0.10);
    }

    function copySalarySummary() {
      const net = document.getElementById('net-salary').innerText;
      const sev = document.getElementById('severance-pay').innerText;
      const text = `[2026 한걸음씩 급여·퇴직금 계산 요약]\n• 예상 월 실수령액: ${net}\n• 예상 법정 퇴직금: ${sev}\n• 저축 황금비율: 생활 50% / 투자 25% / 비상금 15% / 나눔 10%\n※ 일상 참고용 무료 계산기: ${window.location.href}`;
      
      if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
          alert('📋 계산 요약이 복사되었습니다! 가계부나 메모장에 붙여넣어 활용하세요.');
        });
      } else {
        alert(text);
      }
    }

    document.addEventListener('DOMContentLoaded', calculateSalaryAndSavings);
  