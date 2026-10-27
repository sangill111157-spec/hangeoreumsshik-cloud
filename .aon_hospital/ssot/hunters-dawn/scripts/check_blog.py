import urllib.request
import xml.etree.ElementTree as ET
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://connect-ai-shin.blogspot.com/feeds/posts/default'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

with urllib.request.urlopen(req) as resp:
    xml_data = resp.read()
    root = ET.fromstring(xml_data)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    entries = root.findall('atom:entry', ns)
    
    print(f"=== connect-ai-shin.blogspot.com TOTAL POSTS: {len(entries)} ===")
    for idx, e in enumerate(reversed(entries), 1):
        t_elem = e.find('atom:title', ns)
        title = t_elem.text if t_elem is not None and t_elem.text else "(No Title / URL Slug Title)"
        pub = e.find('atom:published', ns).text[:10]
        links = e.findall('atom:link', ns)
        link_href = [l.attrib['href'] for l in links if l.attrib.get('rel') == 'alternate'][0]
        print(f"Post #{idx:02d} [{pub}]: {title}")
        print(f"  URL: {link_href}")
