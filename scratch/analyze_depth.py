with open('dashboard/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

import re

def analyze_div_depth(start_marker, end_marker):
    start_pos = c.find(start_marker)
    end_pos = c.find(end_marker, start_pos)
    segment = c[start_pos:end_pos]
    
    tokens = re.findall(r'<div[^>]*>|</div>', segment)
    depth = 0
    min_depth = 0
    zero_positions = []
    
    for i, token in enumerate(tokens):
        if token == '</div>':
            depth -= 1
        else:
            depth += 1
        if depth < min_depth:
            min_depth = depth
        if depth == 0:
            zero_positions.append(i)
            
    print(f"[{start_marker} -> {end_marker}]")
    print(f"Total tokens: {len(tokens)}, Final depth: {depth}, Min depth: {min_depth}")
    print(f"Zero depth reached at tokens: {zero_positions}")
    return segment, tokens

analyze_div_depth('id="tab-command"', 'id="tab-suno"')
analyze_div_depth('id="tab-suno"', 'id="tab-brain"')
analyze_div_depth('id="tab-brain"', 'id="tab-daughters"')
