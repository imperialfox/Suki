"""The version agrees in the app, README and CHANGELOG, and every file index.html loads exists (tools/release.py)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))
import release

def run(b, t):
    v, d = release.current()
    probs = release.problems()
    t.ok(not probs, f'version {v} · {d} agrees everywhere' + (': ' + '; '.join(probs) if probs else ''))
    # the look (Q04): every font size is one of Apple's text styles, and colours are tokens, never hex in rules
    import re
    css = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'css', 'app.css'), encoding='utf-8').read()
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    sizes = set(int(x) for x in re.findall(r'font-size:\s*(\d+)px', css))
    t.ok(sizes <= {34, 28, 22, 20, 17, 16, 15, 13, 12, 11, 44, 56, 68}, f'every font size is on Apple’s scale ({sorted(sizes)})')
    hexes = [l.strip() for l in css.splitlines() if re.search(r'#[0-9a-fA-F]{3,8}\b', l) and not l.strip().startswith('--')]
    t.ok(not hexes, 'colours in rules are tokens, not hex' + (': ' + '; '.join(hexes[:3]) if hexes else ''))
