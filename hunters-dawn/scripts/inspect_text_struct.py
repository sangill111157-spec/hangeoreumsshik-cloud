import os
import json
import uuid

def inspect_text_structure():
    # Let's inspect existing text structure if any in CapCut or build proper CapCut text structure
    p_dir = r'C:\Users\sangi\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\0801'
    draft_content_path = os.path.join(p_dir, 'draft_content.json')

    with open(draft_content_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Existing Text Materials:", len(data.get("materials", {}).get("texts", [])))
    print("Existing Tracks:", [t.get("type") for t in data.get("tracks", [])])

if __name__ == '__main__':
    inspect_text_structure()
