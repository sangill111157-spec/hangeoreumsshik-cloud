# -*- coding: utf-8 -*-
import os

def find_dirs():
    search_bases = [
        r'C:\Users\sangi\OneDrive\Desktop',
        r'C:\Users\sangi\OneDrive\Documents',
        r'C:\Users\sangi\Downloads',
        r'C:\Users\sangi\Documents',
        r'C:\Users\sangi',
        r'C:\\'
    ]
    for sb in search_bases:
        if not os.path.exists(sb):
            continue
        try:
            for item in os.listdir(sb):
                if 'nvda' in item.lower() or 'trading' in item.lower():
                    full_p = os.path.join(sb, item)
                    print(f"Direct match in {sb}: {full_p}")
        except Exception as e:
            pass

    # Desktop/Downloads/Documents 하위 재귀
    for sb in [r'C:\Users\sangi\OneDrive\Desktop', r'C:\Users\sangi\Downloads', r'C:\Users\sangi']:
        if not os.path.exists(sb):
            continue
        for root, dirs, files in os.walk(sb):
            if root.count(os.sep) - sb.count(os.sep) > 3:
                continue
            if 'App.tsx' in files or ('main.py' in files and 'api' in dirs):
                print(f"Potential project root: {root}")
            for d in dirs:
                if 'nvda' in d.lower():
                    print(f"NVDA folder: {os.path.join(root, d)}")

if __name__ == '__main__':
    find_dirs()
