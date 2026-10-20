
    (function() {
      const REQUIRED_VER = 'v3.3';
      const urlParams = new URLSearchParams(window.location.search);
      const urlVer = urlParams.get('v');
      const storedVer = localStorage.getItem('hgs_app_version');
      
      // 구버전(v3.1 등) 묵은 캐시 감지 시 즉시 v960 강제 갱신
      if (!urlVer || !urlVer.includes('96') || storedVer !== REQUIRED_VER) {
        localStorage.setItem('hgs_app_version', REQUIRED_VER);
        if (!urlVer || !urlVer.includes('96')) {
          const tab = urlParams.get('tab') || 'command';
          const newUrl = window.location.pathname + '?v=960_' + Date.now() + '&tab=' + tab + window.location.hash;
          window.location.replace(newUrl);
        }
      }
    })();
  