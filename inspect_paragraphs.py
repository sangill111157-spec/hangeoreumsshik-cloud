# -*- coding: utf-8 -*-
import json

with open('posts_raw_content.json', 'r', encoding='utf-8') as f:
    posts = json.load(f)

with open('paragraphs_detail.txt', 'w', encoding='utf-8') as out:
    out.write("=== 비대표글 내 '걷기' 및 '견과류' 관련 단락 상세 확인 ===\n")
    for p in posts:
        idx = p['index']
        content = p['content']
        
        # 걷기 관련 (14번 대표글 제외)
        if idx != 14 and ('걷기' in content or '산책' in content or '걸었' in content):
            out.write(f"\n--- [걷기 관련 / {idx:02d}번 글: {p['title']}] (ID: {p['id']}) ---\n")
            paras = [line.strip() for line in content.replace('</p>', '</p>\n').replace('</li>', '</li>\n').replace('</div>', '</div>\n').split('\n') if line.strip()]
            for para in paras:
                if any(k in para for k in ['걷기', '산책', '걸었', '걸으', '걸음']):
                    out.write(f"[WALK] {para}\n")

        # 견과류 관련 (09번 대표글 제외)
        if idx != 9 and ('견과' in content):
            out.write(f"\n--- [견과류 관련 / {idx:02d}번 글: {p['title']}] (ID: {p['id']}) ---\n")
            paras = [line.strip() for line in content.replace('</p>', '</p>\n').replace('</li>', '</li>\n').replace('</div>', '</div>\n').split('\n') if line.strip()]
            for para in paras:
                if '견과' in para:
                    out.write(f"[NUTS] {para}\n")

print("Saved paragraphs_detail.txt")
