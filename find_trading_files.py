# -*- coding: utf-8 -*-
import os

def find_file(filename):
    for root_dir in [r'C:\Users\sangi', 'D:\\', r'C:\workspace', r'C:\trading', r'C:\tmp', r'C:\Temp']:
        if not os.path.exists(root_dir):
            continue
        print(f"Scanning {root_dir}...")
        for root, dirs, files in os.walk(root_dir):
            # exclude node_modules and .git for speed
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '.venv', 'venv', '__pycache__', 'AppData', 'Application Data']]
            if filename in files:
                print(f"FOUND: {os.path.join(root, filename)}")

if __name__ == '__main__':
    find_file('App.tsx')
    find_file('master.py')
