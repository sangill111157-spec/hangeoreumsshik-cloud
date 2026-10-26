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
    
    # 1. rgyt-wrap-data JSON skills 27->47, antibodies 31->51
    content = re.sub(r'"skills":\s*\d+', '"skills": 47', content)
    content = re.sub(r'"antibodies":\s*\d+', '"antibodies": 51', content)
    
    # 2. JS default variables: var SK=D.skills||...,AB=D.antibodies||...
    content = re.sub(r'var\s+SK\s*=\s*D\.skills\|\|\d+', 'var SK=D.skills||47', content)
    content = re.sub(r'AB\s*=\s*D\.antibodies\|\|\d+', 'AB=D.antibodies||51', content)
    
    # 3. button 보유 스킬 (42) or (27) or (38) -> (47)
    content = re.sub(r'보유\s*스킬\s*\(\d+\)', '보유 스킬 (47)', content)
    
    # 4. rgk-headtxt 기본 텍스트도 최신화
    content = re.sub(r'🛡️\s*R1~R\d+', '🛡️R1~R51', content)
    content = re.sub(r'🍯\s*스킬\s*\d+개', '🍯스킬 47개', content)
    content = re.sub(r'📦\s*스킬\s*\d+개', '🍯스킬 47개', content)
    
    # 5. updHead 렌더링 문자열에서 아이콘 통일 (📦 -> 🍯)
    content = content.replace("' · 📦스킬 '", "' · 🍯스킬 '")
    content = content.replace("' · 📦 스킬 '", "' · 🍯스킬 '")
    
    # 6. 제15기관 아온 올인원 대화 허브 태그 버튼 강화: [/변신] [/3D] [/임페커블] [/토큰]
    old_tags = '<button class="rgnlu-tag" data-cmd="/기억">/기억</button>'
    new_tags = (
        '<button class="rgnlu-tag" data-cmd="/기억">/기억</button>'
        ' <button class="rgnlu-tag" data-cmd="/변신">/변신</button>'
        ' <button class="rgnlu-tag" data-cmd="/3D">/3D</button>'
        ' <button class="rgnlu-tag" data-cmd="/임페커블">/임페커블</button>'
        ' <button class="rgnlu-tag" data-cmd="/토큰">/토큰</button>'
    )
    if old_tags in content and '/변신' not in content:
        content = content.replace(old_tags, new_tags)
    
    f.write_text(content, encoding="utf-8")
    print(f"Updated: {f}")
print("ALL DONE")
