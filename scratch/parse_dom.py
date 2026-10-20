from html.parser import HTMLParser
import sys
sys.stdout.reconfigure(encoding='utf-8')

class TabTreeParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tag_stack = []
        self.tab_info = {}
        self.current_tab = None
        self.line_num = 0

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        tag_id = attr_dict.get('id', '')
        tag_class = attr_dict.get('class', '')
        
        self.tag_stack.append((tag, tag_id, self.getpos()))
        
        if tag == 'div' and tag_id.startswith('tab-') and 'tab-pane' in tag_class:
            self.current_tab = tag_id
            self.tab_info[tag_id] = {
                'start_pos': self.getpos(),
                'start_depth': len(self.tag_stack),
                'elements': []
            }
            print(f"\n>>> FOUND TAB: {tag_id} at line {self.getpos()[0]} (stack depth: {len(self.tag_stack)})")
        elif self.current_tab:
            # record notable children
            if tag_id or 'glass-panel' in tag_class:
                depth_in_tab = len(self.tag_stack) - self.tab_info[self.current_tab]['start_depth']
                self.tab_info[self.current_tab]['elements'].append((tag_id or tag_class[:30], self.getpos()[0], depth_in_tab))

    def handle_endtag(self, tag):
        if not self.tag_stack:
            return
        popped_tag, popped_id, pos = self.tag_stack.pop()
        
        if popped_id and popped_id == self.current_tab:
            print(f"<<< CLOSED TAB: {popped_id} at line {self.getpos()[0]} (stack depth now: {len(self.tag_stack)})")
            self.current_tab = None

with open('dashboard/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

parser = TabTreeParser()
try:
    parser.feed(content)
except Exception as e:
    print("Parser error:", e)

print("\n--- Summary of Tabs ---")
for tid, info in parser.tab_info.items():
    print(f"Tab: {tid}, started at line {info['start_pos'][0]}, notable elements: {len(info['elements'])}")
    for el, line, depth in info['elements'][:8]:
        print(f"   line {line:4d} (depth {depth}): {el}")
