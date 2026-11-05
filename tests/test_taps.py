"""2.33 Presses and tap areas (Q29): every button on every screen and sheet in the register reaches the finger over at
least 44 x 44 pt, or is on KNOWN with its reason; neighbours' tap areas never overlap (a tap round a button always
lands on that button, never on its neighbour); text buttons, Cancel, word links and the bin and forget buttons fade
to --press-fade while pressed (S06); calendar days and the Mac sidebar highlight like rows; nothing moves at rest.

How a tap area is measured: the button is scrolled into the middle of its scroller, then elementFromPoint walks out
from its middle, a point at a time, up, down, left and right, while a tap there still lands on the button (or inside
it, or on a twin door with the same action). Up plus down and left plus right must each reach 44 pt. Taps go to
whatever is on top, so a neighbour's area overlapping it shows up as a short reach, with the neighbour named."""
import os
import harness
from test_screens import SHEETS, CLEAR, REG

# Buttons that may be smaller than 44 pt, each with why. Keyed by screen ID (or '*') and the button's data-name.
KNOWN = {
    ('SK-002', 'slot-line'): 'the Till drawer handle is 14 pt on purpose, so it stays out of the way (Q19)',
}

# Extra states a screen shows only after something is done on it, so their buttons are counted too
STATES = {
    'SK-001': ["document.querySelector('[data-a=logSide]') && document.querySelector('[data-a=logSide]').click()"],
    'SK-003': ["(()=>{const q=document.getElementById('q');q.value='rice';q.dispatchEvent(new Event('input',{bubbles:true}))})()"],
}

WIDTHS = [(375, 812), (402, 874)]

BUTTONS = ("button,a[href],[data-a]:not(form):not(input):not(textarea):not(select),label.toggle,input[type=checkbox],"
           "input:not([type=checkbox]):not([type=hidden]),textarea,select")

PROBE = """([roots, sel]) => {
  const out = [];
  const seen = new Set();
  const vis = e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.pointerEvents !== 'none' && !e.closest('[inert],[hidden],.pk-leaving,.sk-covered'); };
  const own = (e, hit) => { if (!hit) return false; if (hit === e || e.contains(hit)) return true;
    const l = e.closest('label'); if (l && (hit === l || l.contains(hit))) return true;
    // a twin door: the same action on the same thing (Home's date line and title both open the calendar)
    const d = hit.closest('[data-a]');
    return !!(d && e.dataset.a && d.dataset.a === e.dataset.a && (d.dataset.v || '') === (e.dataset.v || '') && (d.dataset.k || '') === (e.dataset.k || '')); };
  const els = [];
  roots.forEach(r => document.querySelectorAll(r).forEach(root => root.querySelectorAll(sel).forEach(e => { if (!seen.has(e)) { seen.add(e); els.push(e); } })));
  for (const e of els) {
    if (!vis(e)) continue;
    // a checkbox drawn inside its row is tapped through the row
    if (e.matches('input[type=checkbox]') && e.closest('label.toggle')) continue;
    // something inside a button is tapped through the button
    if (e.parentElement && e.parentElement.closest(sel) && !e.matches('label.toggle')) continue;
    e.scrollIntoView({block: 'center', inline: 'center'});
    const r = e.getBoundingClientRect();
    const x = r.left + r.width / 2, y = r.top + r.height / 2;
    // how far a tap still lands on it, from its middle: up, down, left and right (1 pt steps, 40 at most)
    const reach = (dx, dy) => { let n = 0; for (let i = 1; i <= 40; i++) { const px = x + dx * i, py = y + dy * i;
      if (px < 0 || py < 0 || px >= innerWidth || py >= innerHeight || !own(e, document.elementFromPoint(px, py))) break; n = i; } return n; };
    const up = reach(0, -1), down = reach(0, 1), left = reach(-1, 0), right = reach(1, 0);
    const tall = up + down + 1, wide = left + right + 1;
    if (own(e, document.elementFromPoint(x, y)) && tall >= 44 && wide >= 44) continue;
    const by = [];
    const near = (px, py) => { const h = document.elementFromPoint(px, py); return h ? ((h.closest('[data-name]') || h).dataset.name || h.className || h.tagName) : 'off'; };
    if (tall < 44) by.push(near(x, y - up - 1), near(x, y + down + 1));
    if (wide < 44) by.push(near(x - left - 1, y), near(x + right + 1, y));
    const miss = [`${wide}×${tall}`, ...by.map(String)];
    out.push({name: e.dataset.name || '', a: e.dataset.a || '', cls: typeof e.className === 'string' ? e.className : '',
              w: Math.round(r.width), h: Math.round(r.height), miss: [...new Set(miss)].slice(0, 3).map(String),
              label: (e.getAttribute('aria-label') || e.textContent || '').trim().replace(/\\s+/g, ' ').slice(0, 30)});
  }
  scrollTo(0, 0);
  return out;
}"""


def census(pg, roots):
    return pg.evaluate(PROBE, [roots, BUTTONS])


def small_buttons(b, t, w, h):
    """Every screen and sheet at this width: buttons whose 44 pt square isn't all theirs."""
    pg = t.page(b, w=w, h=h, touch=True)
    S = pg.evaluate(REG)['screens']
    found = []
    for s in S:
        if s['kind'] in ('Tab', 'Screen'):
            pg.evaluate(CLEAR)
            pg.evaluate(f"go('{s['key'][4:]}')"); pg.wait_for_timeout(80)
            for r in census(pg, ['#app', '#bar', '#dock']):
                found.append((s['id'], r))
            for js in STATES.get(s['id'], []):
                pg.evaluate(js); pg.wait_for_timeout(150)
                for r in census(pg, ['#app', '#bar']):
                    found.append((s['id'], r))
        elif s['kind'] in ('Sheet', 'Alert'):
            pg.evaluate(CLEAR); pg.evaluate("go('home')")
            pg.evaluate(SHEETS[s['key']]); pg.wait_for_timeout(120)
            for r in census(pg, ['#layer']):
                found.append((s['id'], r))
            pg.evaluate(CLEAR); pg.wait_for_timeout(40)
    pg.context.close()
    return found


def taps(b, t):
    ok = t.ok
    for w, h in WIDTHS:
        found = small_buttons(b, t, w, h)
        bad, known = [], set()
        for sid, r in found:
            key = (sid, r['name']) if (sid, r['name']) in KNOWN else ('*', r['name'])
            if key in KNOWN:
                known.add(key); continue
            bad.append(f"{sid} › {r['name'] or r['a'] or r['cls']} ({r['label']}) {r['w']}×{r['h']} misses {r['miss']}")
        if os.environ.get('SUKI_TAPS_LIST'):
            print('\n'.join(f'    {w}: {x}' for x in sorted(set(bad))))
        ok(not bad, f'{w} wide: every button on every screen and sheet has a 44 × 44 pt tap area of its own ({len(set(bad))}: {sorted(set(bad))[:12]})')
        stale = [k for k in KNOWN if k not in known]
        ok(not stale, f'{w} wide: everything on the known list is still small (the list can shrink: {stale})')


PRESS = """async ([sel, prop, pseudo]) => {
  const e = [...document.querySelectorAll(sel)].find(x => x.getBoundingClientRect().width > 0);
  if (!e) return null;
  e.scrollIntoView({block: 'center'});
  const r = e.getBoundingClientRect();
  return [r.left + r.width / 2, r.top + r.height / 2];
}"""
READ = "([sel, prop, pseudo]) => { const e = [...document.querySelectorAll(sel)].find(x => x.getBoundingClientRect().width > 0); return getComputedStyle(e, pseudo || null)[prop]; }"

# family: where it shows, what is read, the value at rest and while pressed
FADES = [
    ('text button (Show all)', "go('home')", '#app .hdr .tbtn'),
    ('More details', "go('home')", '#app .disclose'),
    ('Smart add pill', "go('home')", '#app .sidepill'),
    ('period label', "go('spending')", '#app .perline .plabel.cal'),
    ('word link (Search)', "openSheet('notes')", '#layer .tlink'),
    ('text link (the DA report)', "openSheet('item',{id:'bigas'})", '#layer .link'),
    ('bin', "openSheet('item',{id:'bigas'})", '#layer .ibtn'),
    ('Cancel', "openSheet('erase')", '#layer .ghost'),
]
ROW_PRESS = 'rgb(209, 209, 214)'


def pressed(pg, sel, prop, pseudo=None):
    """The value at rest, while the mouse holds it down, and once let go."""
    xy = pg.evaluate(PRESS, [sel, prop, pseudo])
    if not xy:
        return None
    pg.mouse.move(2, 2); pg.wait_for_timeout(30)
    rest = pg.evaluate(READ, [sel, prop, pseudo])
    pg.mouse.move(*xy); pg.mouse.down(); pg.wait_for_timeout(30)
    held = pg.evaluate(READ, [sel, prop, pseudo])
    pg.mouse.move(2, 2); pg.mouse.up(); pg.wait_for_timeout(30)
    after = pg.evaluate(READ, [sel, prop, pseudo])
    return rest, held, after


def presses(b, t):
    ok = t.ok
    pg = t.page(b, w=402, h=874)
    fade = pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--press-fade').trim()")
    ok(fade == '0.35', f'--press-fade is 0.35 (S06) ({fade})')
    for name, setup, sel in FADES:
        pg.evaluate(CLEAR); pg.evaluate("go('home')"); pg.evaluate(setup); pg.wait_for_timeout(120)
        got = pressed(pg, sel, 'opacity')
        ok(got == ('1', '0.35', '1'), f'{name} fades to 35% while pressed and comes back ({sel}: {got})')
    # calendar days: the row press colour under the number while pressed
    pg.evaluate(CLEAR); pg.evaluate("go('home')"); pg.evaluate(SHEETS['sheet:calendar']); pg.wait_for_timeout(120)
    for sel in ('#layer .cday:not(.has):not(.on)', '#layer .cday.has'):
        got = pressed(pg, sel, 'opacity', '::before')
        col = pg.evaluate(READ, [sel, 'backgroundColor', '::before'])
        ok(got == ('0', '1', '0') and col == ROW_PRESS, f'a calendar day highlights like a row while pressed ({sel}: {got}, {col})')
    t.shot(pg, 'taps-calendar')
    pg.context.close()
    # the Mac sidebar: a row's highlight, on a lit item too
    pg = t.page(b, w=1440, h=900, ua=None)
    for sel in ('#side .sbi:not(.on)', '#side .sbi.on'):
        pg.evaluate(CLEAR); pg.evaluate("go('home')"); pg.wait_for_timeout(80)
        xy = pg.evaluate(PRESS, [sel, '', None])
        pg.mouse.move(*xy); pg.mouse.down(); pg.wait_for_timeout(30)
        held = pg.evaluate(READ, [sel, 'backgroundColor', None])
        pg.mouse.move(2, 2); pg.mouse.up()
        ok(held == ROW_PRESS, f'a Mac sidebar item highlights like a row while pressed ({sel}: {held})')
    pg.context.close()


def shots(b, t):
    """Screenshots of the screens with the most changes, light and dark, to compare with the version before."""
    for sc in ('light', 'dark'):
        pg = t.page(b, w=402, h=874, sc=sc, touch=True)
        for name, js in (('home', "go('home')"), ('search', "go('search')"), ('spending', "go('spending')"),
                         ('item', "openSheet('item',{id:'bigas'})"), ('calendar', SHEETS['sheet:calendar'])):
            pg.evaluate(CLEAR); pg.evaluate("go('home')"); pg.evaluate(js); pg.wait_for_timeout(150)
            t.shot(pg, f'taps-{name}-{sc}')
        pg.context.close()


def run(b, t):
    taps(b, t)
    presses(b, t)
    shots(b, t)
