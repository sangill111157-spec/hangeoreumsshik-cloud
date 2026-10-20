import re

path = 'dashboard/index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Auto Cache Sentinel Script
sentinel_script = '''
  <!-- ⚡ [v3.3 Minimal 자동 캐시 파괴 센티넬] ⚡ -->
  <script>
    (function() {
      const REQUIRED_VER = 'v3.3';
      const urlParams = new URLSearchParams(window.location.search);
      const urlVer = urlParams.get('v');
      const storedVer = localStorage.getItem('hgs_app_version');
      
      // 구버전(v3.1 등) 묵은 캐시 감지 시 즉시 v330 강제 갱신
      if (!urlVer || !urlVer.includes('33') || storedVer !== REQUIRED_VER) {
        localStorage.setItem('hgs_app_version', REQUIRED_VER);
        if (!urlVer || !urlVer.includes('33')) {
          const tab = urlParams.get('tab') || 'daughters';
          const newUrl = window.location.pathname + '?v=330_' + Date.now() + '&tab=' + tab + window.location.hash;
          window.location.replace(newUrl);
        }
      }
    })();
  </script>
'''

if 'v3.3 Minimal 자동 캐시 파괴 센티넬' not in html:
    # insert right after <head>
    html = html.replace('<head>', '<head>\n' + sentinel_script, 1)
    print("Injected Auto Cache Sentinel into dashboard/index.html!")

# Ensure live tunnel link in run_dashboard.py returns the exact tunnel
with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print("dashboard/index.html updated!")
