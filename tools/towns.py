#!/usr/bin/env python3
"""Make js/towns.js: the outline of every Philippine city and municipality, so Location's arrow (Q16) can
name the town you're in without the internet and without your position leaving the phone.

Source: faeldon/philippines-json-maps, the low-resolution GeoJSON release (geojson-lowres.zip). Its boundaries are
NAMRIA and PSA's, through OCHA's COD-AB (CC BY-IGO), with PSGC names. Download the zip from
https://github.com/faeldon/philippines-json-maps/releases/latest and run:

    python tools/towns.py path/to/geojson-lowres.zip 2026-3q

The second argument is the PSGC quarter the release is built from (its latest/manifest.json says which).

Each town keeps only its outer rings (enough to tell which town a point is in), rounded to about 110 m and stored
as Google's encoded polyline text, which is small and quick to read.
"""
import io
import json
import re
import sys
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'js' / 'towns.js'
PRECISION = 1e3  # about 110 m, finer than the low-resolution outlines themselves


def encode(points):
    """Google's encoded polyline (lat, lng), at PRECISION."""
    out, plat, plng = [], 0, 0
    for lng, lat in points:
        ilat, ilng = round(lat * PRECISION), round(lng * PRECISION)
        for d in (ilat - plat, ilng - plng):
            v = ~(d << 1) if d < 0 else d << 1
            while v >= 0x20:
                out.append(chr((0x20 | (v & 0x1F)) + 63))
                v >>= 5
            out.append(chr(v + 63))
        plat, plng = ilat, ilng
    return ''.join(out)


def tidy(name, provinces):
    """PSGC names as people say them: "City of Makati" is Makati, unless that's also a province ("Cebu City")."""
    n = re.sub(r'\b(De|Del|Dela|De La)\b', lambda m: m.group(1).lower(), name)
    m = re.match(r'^(?:Island Garden )?City of (.+)$', n)
    if m:
        bare = m.group(1)
        clash = any(p == bare or p.startswith(bare + ' ') for p in provinces)
        n = bare + ' City' if clash else bare
    return n


def main(src, psgc=''):
    z = zipfile.ZipFile(src)
    names = z.namelist()
    provinces = set()
    for f in names:
        if '/regions/' in f and f.endswith('.json'):
            for ft in json.load(z.open(f))['features']:
                if ft['properties'].get('adm2_en'):
                    provinces.add(ft['properties']['adm2_en'])
    towns = []
    for f in sorted(names):
        if '/provdists/' not in f or not f.endswith('.json'):
            continue
        for ft in json.load(z.open(f))['features']:
            g = ft['geometry']
            if not g:
                continue
            polys = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
            rings = [encode(p[0]) for p in polys if len(p[0]) >= 4]
            if rings:
                towns.append([tidy(ft['properties']['adm3_en'], provinces), ft['properties']['adm3_psgc'], rings])
    if len(towns) < 1500:
        sys.exit('Only %d towns found: is this the right zip?' % len(towns))
    towns.sort(key=lambda t: t[1])
    manifest = {}
    for f in names:
        if f.endswith('manifest.json'):
            manifest = json.load(z.open(f))
    psgc = manifest.get('psgc', psgc)
    head = (
        '/* Suki · towns.js · made by tools/towns.py, don\'t edit by hand.\n'
        '   The outline of every Philippine city and municipality (Q16), so Location\'s arrow names the town offline.\n'
        '   Boundaries: NAMRIA and PSA, through OCHA\'s COD-AB (CC BY-IGO), with PSGC names (' + (psgc or 'see tools/towns.py') + '),\n'
        '   from faeldon/philippines-json-maps (MIT). Each town: [name, PSGC code, [outer rings as encoded polylines]]. */\n'
    )
    body = json.dumps({'source': 'NAMRIA and PSA, through OCHA (CC BY-IGO)', 'psgc': psgc, 'made': date.today().isoformat(), 'towns': towns}, ensure_ascii=False, separators=(',', ':'))
    OUT.write_text(head + 'window.sukiTowns = ' + body + ';\n', encoding='utf-8')
    print('%d towns, %d KB → %s' % (len(towns), OUT.stat().st_size // 1024, OUT.relative_to(ROOT)))


if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    main(*sys.argv[1:])
