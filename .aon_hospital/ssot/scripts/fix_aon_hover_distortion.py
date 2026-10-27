# -*- coding: utf-8 -*-
import re
from pathlib import Path

files = [
    Path("index.html"),
    Path("dashboard/index.html"),
    Path("docs/index.html"),
    Path("rgon_alpha_chat.html"),
    Path("dashboard/rgon_alpha_chat.html"),
    Path("docs/rgon_alpha_chat.html"),
    Path("rgon_alpha_audience.html"),
]

for f in files:
    if not f.exists():
        continue
    content = f.read_text(encoding="utf-8")
    
    # 1. R36 PLAYGROUND 내 aonEl: rgyt-wrap 절대 반환 금지! 오직 aon-roamer 만 반환
    # 기존: function aonEl(){return document.getElementById("rgyt-wrap")||document.getElementById("aon-roamer")}
    # 또는: function aonEl(){return document.getElementById("aon-roamer")||document.getElementById("rgyt-wrap");}
    content = re.sub(
        r'function\s+aonEl\(\)\s*\{\s*return\s+document\.getElementById\("rgyt-wrap"\)\|\|document\.getElementById\("aon-roamer"\)\s*\}',
        'function aonEl(){return document.getElementById("aon-roamer")||null}',
        content
    )
    content = re.sub(
        r'function\s+aonEl\(\)\s*\{\s*return\s+document\.getElementById\("aon-roamer"\)\|\|document\.getElementById\("rgyt-wrap"\);\s*\}',
        'function aonEl(){return document.getElementById("aon-roamer")||null;}',
        content
    )
    
    # 2. pointermove 스침 감지 제거: 스치기만 해도 뒤틀리는 버그 근원 차단!
    # 기존:
    # el.addEventListener("pointermove",function(e){
    #   var now=Date.now();
    #   if(now-drag.t<350&&Math.abs(e.clientX-drag.x)>18){drag.pets++;drag.x=e.clientX;drag.t=now;if(drag.pets>=3){drag.pets=0;petSpoil();}}
    #   else if(now-drag.t>=350){drag.t=now;drag.x=e.clientX;drag.pets=0;}
    # });
    old_pointermove = re.search(r'el\.addEventListener\("pointermove",function\(e\)\{[\s\S]*?\}\);\s*\}', content)
    if old_pointermove:
        # dblclick이나 명시적 클릭에만 반응하도록 pointermove 완전 비활성화
        content = content.replace(
            old_pointermove.group(0),
            '/* pointermove removed to prevent accidental spoil on hover */ }'
        )
        
    # 3. bubble(msg) 함수에서 rgyt-wrap 위에 뜬금없이 떠서 일거리 보드 가리는 문제 방어
    # el이 없거나 aon-roamer가 숨겨져 있을 때의 기본 위치를 화면 우하단 안전구역 또는 rgyt-head 근처로 조정
    content = content.replace(
        'var el=aonEl(),r=el?el.getBoundingClientRect():{left:140,top:140,width:80};',
        'var el=aonEl(),r=(el&&el.offsetWidth>0)?el.getBoundingClientRect():null;if(!r){var h=document.getElementById("rgyt-head");r=h?h.getBoundingClientRect():{left:140,top:window.innerHeight-120,width:80};}'
    )
    
    # 4. #rgyt-wrap 컨테이너 보호 CSS 추가 (절대 transform 되거나 rotate 되지 않도록)
    css_guard = '#rgyt-wrap{transform:none!important;rotate:none!important;}'
    if css_guard not in content:
        content = content.replace('</head>', f'<style>{css_guard}</style></head>')
        
    f.write_text(content, encoding="utf-8")
    print(f"Surgery done: {f}")

print("ALL SURGERY COMPLETED")
