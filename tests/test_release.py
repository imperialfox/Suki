"""The version agrees in the app, README and CHANGELOG, and every file index.html loads exists (tools/release.py)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))
import release

def run(b, t):
    v, d = release.current()
    probs = release.problems()
    t.ok(not probs, f'version {v} · {d} agrees everywhere' + (': ' + '; '.join(probs) if probs else ''))
