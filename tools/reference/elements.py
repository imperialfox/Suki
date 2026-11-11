"""Suki · the element sheet (Q30, 2.41): every named part, with its kit part, its values and its decision.

    python3 tools/reference/elements.py           write reference/elements.md (opens the app in a headless browser)
    python3 tools/reference/elements.py --check   exit 1 if reference/elements.md is out of date

The same sheet as Vocal Sessions' (its Q48 and Q55, tools/reference/elements.py there), with the same columns, so the
two apps' sheets read the same, plus a Decision column. It reads the register (js/register.js › REGISTER) for the
parts: the shared parts, the names by action and each screen's own parts, with the screen's ID and name, how the part
is found and its status. It then opens the app (headless Chromium, the tests' sample data, motion off, a fixed date) on
every tab, screen, sheet and alert the sample data reaches, and the toast, and reads each named part from the page:
its parts kit part (gallery number, from its pk- classes, the kit control it sits in or holds, and its press), how it
presses, its corner and its motion, each mapped back to its name in the value set (`--r-card`, `gentle`,
`--dur-fade`). An app's own part (no kit part) takes its reason from REASONS below. The decisions come from
js/parts.settings.js (one line each, with its ID) and DECISIONS below says which parts each one covers. Retired values
(RETIRED below, from tools/parts-kit/REPLACED.md and the value set's retired list) must not come back on any part.
Parts the sample data doesn't reach keep a dash and are listed at the end.
The tests (test_screens.py › reference) collect the same way and fail when the sheet is out of date, when a reached
part has neither a kit part nor a reason, when a named element has no line in the register, or when a part uses a
retired value. See MAINTAINING › Screen IDs › The element sheet.
"""
import os
import re
import sys
import datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SETTINGS = os.path.join(ROOT, 'js', 'parts.settings.js')
OUT = os.path.join(ROOT, 'reference', 'elements.md')

# ---------------------------------------------------------------- the kit's parts, by gallery number
# Each pk- class (or a class starting with it and a hyphen) and the gallery part it belongs to, from
# tools/parts-kit/README.md › Parts. State classes (pk-on, pk-pressed …) and base classes aren't parts.
# The same list as Vocal Sessions' (kit 1.2.0 has every part Suki uses).
KIT_PARTS = [
    ('pk-glass', 1, 'Glass'), ('pk-strong', 1, 'Glass'), ('pk-clear', 1, 'Glass'),
    ('pk-topbar', 2, 'Top bar'), ('pk-bar-slot', 2, 'Top bar'), ('pk-edge', 51, 'Soft edge'),
    ('pk-large-title', 3, 'Large title'), ('pk-date-line', 3, 'Large title'),
    ('pk-dock', 4, 'Tab bar'), ('pk-tabbar', 4, 'Tab bar'), ('pk-tab', 4, 'Tab bar'),
    ('pk-search-circle', 6, 'Tab bar search'), ('pk-search-field', 6, 'Tab bar search'), ('pk-search-close', 6, 'Tab bar search'),
    ('pk-push', 10, 'Pushed page'), ('pk-tinted', 13, 'Prominent button'),
    ('pk-press', 12, 'Glass button'), ('pk-press-solid', 14, 'Solid press'), ('pk-solid', 14, 'Solid press'),
    ('pk-press-bar', 15, 'Buttons on a bar'), ('pk-group', 15, 'Buttons on a bar'),
    ('pk-menu', 16, 'Pull-down menu'), ('pk-chips', 18, 'Chips'), ('pk-chip', 18, 'Chips'),
    ('pk-badged', 19, 'Badges'), ('pk-badge', 19, 'Badges'), ('pk-tag', 19, 'Badges'),
    ('pk-switch', 21, 'Switch'), ('pk-slider', 22, 'Slider'), ('pk-seg', 23, 'Segmented control'),
    ('pk-stepper', 24, 'Stepper'), ('pk-progress', 25, 'Progress'), ('pk-ring', 25, 'Progress'), ('pk-spinner', 25, 'Progress'),
    ('pk-search', 26, 'Search field'), ('pk-field', 27, 'Text field'), ('pk-area', 29, 'Text area'),
    ('pk-container', 33, 'Glass container'), ('pk-card', 34, 'Card'),
    ('pk-row', 35, 'List row'), ('pk-tile', 35, 'List row'), ('pk-chev', 35, 'List row'), ('pk-list', 36, 'Grouped section'),
    ('pk-divider', 38, 'Divider'), ('pk-swipe', 39, 'Swipe actions'), ('pk-reorder', 40, 'Reorderable list'), ('pk-grip', 40, 'Reorderable list'),
    ('pk-sheet', 41, 'Sheet'), ('pk-grabber', 41, 'Sheet'), ('pk-dim', 41, 'Sheet'), ('pk-cover', 43, 'Full-screen cover'),
    ('pk-popover', 44, 'Popover'), ('pk-hold', 46, 'Long-press menu'),
    ('pk-actions', 47, 'Action sheet'), ('pk-action', 47, 'Action sheet'), ('pk-cancel', 47, 'Action sheet'),
    ('pk-alert', 48, 'Alert'), ('pk-toast', 49, 'Toast'),
]
LABEL = {}
for _c, _n, _l in KIT_PARTS: LABEL.setdefault(_n, _l)
# a button inside one of these is that part's (a segment, a tab, an alert's button, a toast's Undo); a row holding
# one of the controls in CONTROLS is that control's (a switch row)
INSIDE = '.pk-seg, .pk-stepper, .pk-chips, .pk-tabbar, .pk-alert, .pk-actions, .pk-menu, .pk-swipe-actions, .pk-search-field, .pk-search, .pk-group, .pk-toast'
CONTROLS = '.pk-switch, .pk-seg, .pk-slider, .pk-stepper'
# how a part presses. Suki has no KITPRESS: a kit press is a class in the markup (Q28), the rest are css/app.css's
# :active rules, sorted by what they use (see READ_JS)
PRESSES = {
    'pk-press': (12, 'Glass, grows'),
    'pk-press-solid': (14, 'Solid, shrinks'),
    'row': (35, 'Row, highlights'),
    'fade': (None, 'Text, fades'),
    'shrink': (None, 'Own, shrinks'),
    'lit': (None, 'Own, highlights'),
}

# ---------------------------------------------------------------- Suki's own part: why it isn't a kit part
# The first selector the part matches gives its reason. Kept short; a part with a kit part needs none.
REASONS = [
    ('.ghost, .tbtn, .link, .textlink, .tlink, .disclose, .ibtn, .sidepill, .plabel', "A text button or word link; the kit has no text button with a press yet (S06)"),
    ('.hometitle', "Home's date line and title, a door to the calendar (Q08); the kit's large title isn't used"),
    ('.locbtn', "The form's own arrow inside the Location field (Q16)"),
    ('.rdoor', "Convert's own rate row, with its own highlight (Q23)"),
    ('input, select, textarea', "Suki's own form field, not kit part 27"),
    ('.sbi', "The Mac sidebar, Suki's own (it highlights like a row)"),
    ('.dn, #tillDrawer, #tillHdl, #tillOut, .cashbox', "The Till's notes, drawer and change, Suki's own (Q13, Q18 to Q21)"),
    ('.cday, .calhead *', "The calendar's own days and arrows, drawn with the calendar (Q03, Q12)"),
    ('#chart, #chart *', "Spending's own chart, drawn with its bars (Q03, Q10)"),
    ('#hchart, #hchart *', "Rate history's own chart (Q23)"),
    ('.nudge', "Home's own notices, drawn with Home (Q05)"),
    ('.sumcard, .sumcard *, .stat, .ratecard, #logwrap', "Home's own cards, drawn with Home (Q03, Q17)"),
    ('.chip', "Suki's own picking chip, not in a kit chip row"),
    ('.toast.sticky, .toast.sticky *', 'The sticky warning stays Suki\'s own (S04)'),
]

# ---------------------------------------------------------------- decisions: which parts each one covers
# The IDs are js/parts.settings.js's (one line each there). A part takes every ID whose rule it meets. Decisions for
# the whole app (D18 the kit runs the motion, D20, D21, D22, S02, S05) are in the Decisions section, on no row.
DECISIONS_BY_KIT = {4: ['D01'], 23: ['D04'], 41: ['D14', 'D15', 'D17'], 48: ['D08'], 49: ['D16']}
DECISIONS_BY_PRESS = {'row': ['D06'], 'fade': ['S06']}
DECISIONS_BY_SEL = [  # (an ancestor or the part itself matches, IDs)
    ('#barL, #barR', ['D19']),
    ('#own', ['S01']),
    ('.toast.sticky', ['S04']),
]
DECISIONS_BY_SCREEN = {'SK-013': ['D23']}  # Erase all data? stays a sheet until kit 1.3.0's three-button alert (S03)

# ---------------------------------------------------------------- retired values: none may come back
# Each is a value Suki dropped (tools/parts-kit/REPLACED.md, MAINTAINING › Value set › Retired at Q26). A reached part
# whose motion uses one fails test_screens.py › reference. Easings as the browser writes them.
RETIRED = [
    ('cubic-bezier(0.25, 0.9, 0.3, 1)', "MOTION's fallback curve for a browser without linear() springs", 'the kit\'s own fallback', 'Q27 · 2.31'),
    ('cubic-bezier(0.3, 1.3, 0.5, 1)', 'The page behind a sheet shrinking', 'the `sheet` spring', 'Q27 · 2.31'),
    ('cubic-bezier(0.3, 0, 0.25, 1)', 'A sheet leaving, the page behind coming back', '`--ease-accel` over `--dur-leave`', 'Q27 · 2.31'),
    ('@up', 'The iPhone sheet rising (`@keyframes up`)', 'kit part 41 on the `sheet` spring', 'Q27 · 2.31'),
    ('@squish', 'The segmented control\'s squish (`squish()` in events.js)', 'kit part 23, no squish (D04)', 'Q28 · 2.32'),
    ('padding', "The tab bar's padding transition", 'nothing: Suki never had a folding tab bar (D01)', 'Q26 · 2.30'),
    ('max-width', "The tab buttons' max-width transition", 'nothing (D01)', 'Q26 · 2.30'),
    ('height', "The tab buttons' height transition", 'nothing (D01)', 'Q26 · 2.30'),
    ('width', 'Any size transition', 'nothing transitions a size (Value set)', 'Q26 · 2.30'),
]
RETIRED_KEYS = [r[0] for r in RETIRED]


def part_no(classes):
    """The gallery parts for a list of pk- classes, as {number: label}."""
    out = {}
    for c in classes:
        hits = [(len(p), n, label) for p, n, label in KIT_PARTS if c == p or c.startswith(p + '-')]
        if hits:
            _, n, label = max(hits)  # the longest match: pk-press-solid is 14, not pk-press's 12
            out[n] = label
    return out


def kit(sel):
    """Kit part from a selector's own pk- classes: used for a part the sample data doesn't reach."""
    return kit_cell(part_no(re.findall(r'\.(pk-[a-z-]+)', sel)))


def kit_cell(parts):
    return ', '.join('%d %s' % (n, parts[n]) for n in sorted(parts))


# ---------------------------------------------------------------- reading the app
# The date the sample data and the page's clock use, so what's reached (and so the sheet) never depends on the day
FIXED = dt.datetime(2026, 11, 4, 12, 0)

# Run on one screen or sheet: every visible part with a data-name inside the roots, with the register line it comes
# from and what the page says about it. The named values are read once, by applying each name to a probe element,
# so a computed value maps back to the name that gives it. A named element with no register line comes back with
# key null (the test fails on it).
READ_JS = r"""(arg) => {
  if (!window.__REF) {
    const probe = document.createElement('div');
    probe.style.position = 'absolute';
    document.body.appendChild(probe);
    const names = new Set(), sheets = [...document.styleSheets];
    const rulesOf = (sh) => { try { return [...sh.cssRules] } catch (e) { return [] } };
    for (const sh of sheets) for (const r of rulesOf(sh)) if (r.selectorText === ':root' || r.selectorText === 'html') for (const p of r.style) if (p.startsWith('--')) names.add(p);
    for (const p of document.documentElement.style) if (p.startsWith('--')) names.add(p); // the kit writes the springs here
    const read = (prop, n) => { probe.style[prop] = 'var(' + n + ')'; return getComputedStyle(probe)[prop] };
    const springs = Object.keys(Parts.motion.springs());
    const ease = {}, corner = {}, dur = {};
    [...names].sort().forEach((n) => {
      if (n.startsWith('--ease-')) { const v = read('transitionTimingFunction', n), k = n.slice(7); if (!(v in ease) || springs.includes(k)) ease[v] = springs.includes(k) ? k : n }
      if (n.startsWith('--r-')) { const v = read('borderTopLeftRadius', n); if (v !== '0px' && !(v in corner)) corner[v] = n }
      if (n.startsWith('--dur-')) { const v = read('transitionDuration', n); if (v !== '0s' && !(v in dur)) dur[v] = n }
    });
    probe.remove();
    // Suki's presses in css/app.css, by what each :active rule uses: the kit's row press colour (D06, also through a
    // ::before or ::after), the text fade (--press-fade, S06), a shrink, or its own highlight
    const base = (s) => s.split(',').map((x) => x.replace(/::?(after|before)\b/g, '').replace(/:(active|hover)/g, '').trim()).filter(Boolean).join(', ');
    const kinds = { row: [], fade: [], shrink: [], lit: [] };
    const app = sheets.find((sh) => (sh.href || '').includes('/css/app.css'));
    for (const r of app ? rulesOf(app) : []) {
      if (!r.selectorText) continue;
      const t = r.style.cssText;
      if (t.includes('--pk-row-press')) kinds.row.push(base(r.selectorText));
      else if (!r.selectorText.includes(':active')) continue;
      else if (t.includes('--press-fade')) kinds.fade.push(base(r.selectorText));
      else if (/scale\(/.test(r.style.transform)) kinds.shrink.push(base(r.selectorText));
      else if (r.style.background || r.style.backgroundColor) kinds.lit.push(base(r.selectorText));
    }
    for (const k in kinds) kinds[k] = kinds[k].join(', ');
    window.__REF = { ease, corner, dur, kinds };
  }
  const N = window.__REF, live = (p) => !p.status || p.status === 'Live';
  const scr = REGISTER.screens.find((s) => s.id === arg.screen), own = scr ? scr.parts.filter(live) : [];
  const shared = REGISTER.shared.filter(live), acts = REGISTER.actions.filter(live);
  const is = (el, sel) => { try { return !!sel && el.matches(sel) } catch (e) { return false } };
  const line = (el) => {
    const n = el.dataset.name;
    let p = own.find((p) => p.name === n && is(el, p.sel)); if (p) return [arg.screen, n, p.sel];
    p = shared.find((p) => p.name === n && is(el, p.sel)); if (p) return ['shared', n, p.sel];
    p = acts.find((p) => p.name === n && is(el, p.sel)); if (p) return ['action', n, p.sel];
    return null;
  };
  const pk = (el) => (el ? [...el.classList].filter((c) => c.startsWith('pk-')) : []);
  const els = new Set();
  arg.roots.forEach((q) => document.querySelectorAll(q).forEach((r) => { if (r.dataset.name) els.add(r); r.querySelectorAll('[data-name]').forEach((e) => els.add(e)) }));
  const out = [];
  els.forEach((el) => {
    // the kit labels its own containers in words ("Overlays", "Dim", a sheet's title): those aren't Suki's names
    if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(el.dataset.name) || !el.getClientRects().length || el.closest('.pk-leaving, #leaving, .sk-covered')) return;
    const key = line(el);
    if (!key) { out.push({ key: null, name: el.dataset.name, screen: arg.screen }); return }
    const cs = getComputedStyle(el), b = el.getBoundingClientRect();
    const kit = pk(el).concat(pk(el.parentElement && el.parentElement.closest(arg.inside)), pk(el.querySelector(arg.controls)));
    const press = ['pk-press-solid', 'pk-press'].find((c) => el.classList.contains(c)) || ['row', 'fade', 'shrink', 'lit'].find((k) => is(el, N.kinds[k])) || null;
    const r = cs.borderTopLeftRadius, px = parseFloat(r);
    let corner = 'none';
    // a named corner first (so a size that changes with the font never changes the answer), then a capsule or circle
    if (px) corner = N.corner[r] || ((r.endsWith('%') ? px >= 50 : px >= Math.min(b.width, b.height) / 2 - 0.5) ? (Math.abs(b.width - b.height) < 1 ? 'circle' : 'capsule') : r);
    const props = cs.transitionProperty.split(', '), durs = cs.transitionDuration.split(', '), eases = cs.transitionTimingFunction.split(/, (?![^(]*\))/);
    const motion = new Set(), moved = new Set();
    props.forEach((p, i) => {
      const d = durs[i % durs.length], e = eases[i % eases.length];
      if ((p === 'all' || p === 'none') && d === '0s') return;
      moved.add(p);
      if (N.ease[e]) motion.add(N.ease[e]);
      if (d !== '0s') motion.add(N.dur[d] || d);
      if (!N.ease[e] && d !== '0s') motion.add(e);
    });
    if (cs.animationName !== 'none') cs.animationName.split(', ').forEach((a) => motion.add('@' + a));
    const reason = arg.reasons.findIndex((s) => is(el, s) || !!el.closest(s));
    const dec = arg.decisions.map((s, i) => (el.closest(s) ? i : -1)).filter((i) => i >= 0);
    out.push({ key, kit, press, corner, motion: [...motion].sort(), props: [...moved].sort(), reason, dec });
  });
  return out;
}"""


def open_app(b, w=390, h=844):
    """The app with the tests' sample data, motion off, the clock at FIXED (an iPhone unless w is wider)."""
    sys.path.insert(0, os.path.join(ROOT, 'tests'))
    import harness
    ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2 if w < 500 else 1, color_scheme='light',
                        timezone_id='Europe/London', locale='en-GB', user_agent=harness.UA_IPHONE if w < 500 else None)
    harness.rate_route(ctx)
    ctx.clock.install(time=FIXED)
    ctx.add_init_script("try{localStorage.setItem('suki:motion','0');localStorage.setItem('suki:onboard',JSON.stringify({welcome:true,tips:false,seen:{}}))}catch(e){}")
    pg = ctx.new_page()
    pg.goto(harness.url())
    harness.ready(pg)
    was, harness.today = harness.today, FIXED.date()  # sample() dates its records from harness.today; put back after
    try:
        data = harness.sample()
    finally:
        harness.today = was
    data['rate']['cachedAt'] = FIXED.replace(tzinfo=dt.timezone.utc).isoformat()
    pg.evaluate(harness.SEED, data)
    pg.reload()
    harness.ready(pg)
    return pg


def collect(b):
    """Every reached part's values, read from the app: {(scope, name, sel): [what the page says, one per time seen]},
    plus the named elements with no register line. scope is 'shared', 'action' or the screen's ID. Three passes, each
    opening every tab and screen: the iPhone (then every sheet and alert the tests open, and the toast and the sticky
    warning), the iPad and the Mac. Later passes only add parts the first didn't show, so the values are the iPhone's
    wherever it has the part."""
    sys.path.insert(0, os.path.join(ROOT, 'tests'))
    from test_screens import SHEETS, CLEAR, REG
    arg = {'inside': INSIDE, 'controls': CONTROLS, 'reasons': [s for s, _ in REASONS], 'decisions': [s for s, _ in DECISIONS_BY_SEL]}
    seen, unlisted, R = {}, set(), None
    for w, h in ((390, 844), (820, 1180), (1440, 900)):
        pg = open_app(b, w, h)
        R = pg.evaluate(REG)
        got = {}

        def read(sid, roots):
            for r in pg.evaluate(READ_JS, dict(arg, screen=sid, roots=roots)):
                if r['key'] is None: unlisted.add('%s › %s' % (r['screen'], r['name']))
                else: got.setdefault(tuple(r['key']), []).append(r)
        for s in R['screens']:
            if s['kind'] not in ('Tab', 'Screen') or s['status'] != 'Live': continue
            pg.evaluate("go('%s')" % s['key'][4:]); pg.wait_for_timeout(60)
            if pg.evaluate("document.getElementById('app').dataset.screen") == s['id']:
                read(s['id'], ['#app', '#bar', '#dock', '#side'])
        if w < 500:
            for s in R['screens']:
                if s['kind'] not in ('Sheet', 'Alert') or s['status'] != 'Live' or s['key'] not in SHEETS: continue
                pg.evaluate("go('home')")
                pg.evaluate(SHEETS[s['key']]); pg.wait_for_timeout(60)
                if pg.evaluate("(()=>{const t=SCR.top();return t?t.dataset.screen:null})()") == s['id']:
                    read(s['id'], ['#layer'])
                pg.evaluate(CLEAR); pg.wait_for_timeout(30)
            pg.evaluate("go('home')")
            pg.evaluate("toast('Purchase deleted',()=>{})"); pg.wait_for_timeout(60)
            read('SK-016', ['#layer', 'body > .toast'])
            pg.evaluate("toast('Couldn’t save',null,true)"); pg.wait_for_timeout(60)
            read('SK-016', ['body > .toast.sticky', '#layer .toast.sticky', '.toast.sticky'])
        pg.context.close()
        for k, recs in got.items(): seen.setdefault(k, recs)
    return seen, sorted(unlisted), R


def values(seen):
    """One row of values per register line: {(scope, name, sel): {kit, press, corner, motion, reason, decision, retired}}.
    A part seen in more than one place lists each different value once, so the sheet shows where it varies."""
    out = {}
    many = lambda xs: ' · '.join(sorted(set(xs))) if len(set(xs)) <= 3 else 'varies (%d)' % len(set(xs))
    for key, recs in seen.items():
        parts = {}
        for r in recs: parts.update(part_no(r['kit']))
        press = {r['press'] for r in recs if r['press']}
        for p in press:
            if PRESSES[p][0]: parts.setdefault(PRESSES[p][0], LABEL[PRESSES[p][0]])
        reasons = [REASONS[r['reason']][1] for r in recs if r['reason'] >= 0]
        dec = set(DECISIONS_BY_SCREEN.get(key[0], []))
        for n in parts: dec.update(DECISIONS_BY_KIT.get(n, []))
        for p in press: dec.update(DECISIONS_BY_PRESS.get(p, []))
        for r in recs:
            for i in r['dec']: dec.update(DECISIONS_BY_SEL[i][1])
        used = {m for r in recs for m in r['motion']} | {p for r in recs for p in r['props']}
        out[key] = {
            'kit': kit_cell(parts),
            'press': many([PRESSES[r['press']][1] if r['press'] else 'none' for r in recs]),
            'corner': many(['`' + r['corner'] + '`' if r['corner'].startswith('--') else r['corner'] for r in recs]),
            'motion': many([', '.join('`' + m + '`' for m in r['motion']) or 'none' for r in recs]),
            'reason': '' if parts else (reasons[0] if reasons else ''),
            'decision': ', '.join(sorted(dec)),
            'retired': sorted(k for k in RETIRED_KEYS if k in used),
            'presses': sorted(press),
        }
    return out


def status(st):
    return 'In use' if not st or st == 'Live' else st.replace('Retired in', 'Retired ·')


def register(R):
    """Every part in the register, in order: (scope, name, sel, status, was, group). scope is 'shared', 'action' or
    the screen's ID; group is 'SK-001 · Home' for a screen's own parts."""
    p = lambda x: (x['name'], x['sel'], status(x.get('status')), ', '.join(x.get('was', [])))
    out = [('shared',) + p(x)[:2] + (p(x)[2], p(x)[3], '') for x in R['shared']]
    out += [('action',) + p(x)[:2] + (p(x)[2], p(x)[3], '') for x in R['actions']]
    for s in R['screens']:
        group = s['id'] + ' · ' + s['name'] + ('' if s['status'] == 'Live' else ' (' + s['status'] + ')')
        out += [(s['id'],) + p(x)[:2] + (p(x)[2], p(x)[3], group) for x in s['parts']]
    return out


def decisions():
    """Every decision in js/parts.settings.js: (ID, setting, what it says), in the file's order."""
    out = []
    for line in open(SETTINGS, encoding='utf-8').read().split('\n'):
        m = re.match(r"\s*([A-Za-z]+): .*?// ((?:D|S)\d\d) (.+)$", line)
        if m: out.append((m.group(2), m.group(1), m.group(3).strip()))
    return out


def problems(vals, reg):
    """The sheet's rule: every part the sample data reaches has a kit part or a reason. The parts that break it."""
    return ['%s › %s' % (p[0], p[1]) for p in reg if (p[0], p[1], p[2]) in vals
            and not vals[(p[0], p[1], p[2])]['kit'] and not vals[(p[0], p[1], p[2])]['reason']]


def retired(vals, reg):
    """Parts that use a retired value, with the value."""
    return ['%s › %s (%s)' % (p[0], p[1], ', '.join(vals[(p[0], p[1], p[2])]['retired'])) for p in reg
            if (p[0], p[1], p[2]) in vals and vals[(p[0], p[1], p[2])]['retired']]


def unknown_decisions(vals):
    """Decision IDs on the sheet's rows that js/parts.settings.js doesn't have."""
    have = {d[0] for d in decisions()}
    return sorted({d for v in vals.values() for d in v['decision'].split(', ') if d and d not in have})


def presses(vals, reg):
    """The Presses section: each kind of press, its kit part and decision, and how many reached parts press that way."""
    count = {k: 0 for k in PRESSES}
    for p in reg:
        v = vals.get((p[0], p[1], p[2]))
        for k in (v or {}).get('presses', []): count[k] += 1
    rows = [('Glass button', '12 · `.pk-press`', 'pk-press', 'Grows 17 pt on its longest side and lights up, on the kit\'s `press` and `release` springs (Q28)', ''),
            ('Solid capsule', '14 · `.pk-press-solid`', 'pk-press-solid', 'Shrinks to `--press` (0.93) over `--dur-quick`, back on `release` (Q28)', ''),
            ('Row and card door', '35 · the kit\'s `--pk-row-press`', 'row', 'Highlights at once, fades out over `--dur-fade`; no shrink', 'D06'),
            ('Text button and word link', 'Suki\'s own', 'fade', 'Fades to `--press-fade` (0.35) at once, back over `--dur-fade`', 'S06'),
            ('The Till\'s notes', 'Suki\'s own', 'shrink', 'Shrinks to `--press`, back over 0.5 s on `--ease-pop`, with its own tilt (Q18)', ''),
            ('Own highlight', 'Suki\'s own', 'lit', 'Its own fill while pressed', '')]
    L = ['## Presses', '',
         'How each kind of part presses. A kit press is a class in the markup (Q28); the rest are `css/app.css`\'s `:active` '
         'rules. A new button with one of these classes gets the press for free. Chips (part 18) don\'t press; the segmented '
         'control\'s knob (part 23, D04) and the switch (part 21) swell to glass while held.', '',
         '| Kind | Kit part | Press | Parts | Decision | Status |', '|---|---|---|---|---|---|']
    L += ['| %s | %s | %s | %d | %s | In use |' % (k, part, d, count[key], dec) for k, part, key, d, dec in rows]
    return L + ['']


def build(vals, reg):
    """The sheet's text, from the register's parts (register(R)) and the values read from the app (values(...))."""
    esc = lambda s: s.replace('|', '\\|')
    DASH = {'kit': '', 'press': '—', 'corner': '—', 'motion': '—', 'reason': '', 'decision': ''}

    def cells(p):
        v = vals.get((p[0], p[1], p[2]))
        if not v: v = dict(DASH, kit=kit(p[2]), decision=', '.join(DECISIONS_BY_SCREEN.get(p[0], [])))
        return '%s | %s | %s | %s | %s | %s' % (v['kit'], v['press'], v['corner'], v['motion'], v['reason'], v['decision'])
    live = [p for p in reg if p[3] == 'In use']
    missed = [p for p in live if (p[0], p[1], p[2]) not in vals]
    sh = [p for p in reg if p[0] == 'shared']
    ac = [p for p in reg if p[0] == 'action']
    on = [p for p in reg if p[0] not in ('shared', 'action')]
    head = '| Name | Found by | Kit part | Press | Corner | Motion | Reason | Decision | Status |'
    rule = '|---|---|---|---|---|---|---|---|---|'
    L = ['# Element sheet · Suki', '',
         'Every named part in the app: its name, where it is named, how the app finds it, the parts kit part it is (by its '
         'gallery number), how it presses, its corner and its motion, the decision behind it, and its status. Suki\'s own '
         'part, with no kit part, says why. Written by `tools/reference/elements.py` from `js/register.js`, '
         '`js/parts.settings.js` and the app itself (headless, the tests\' sample data, motion off), so the values are what '
         'the page really uses, mapped back to their names in the value set; don\'t edit by hand. The same columns as '
         'Vocal Sessions\' element sheet, plus Decision. The naming rules: '
         '[MAINTAINING › Screen IDs › Naming rules](../MAINTAINING.md#naming-rules).', '',
         'A note points at a part as `SK-001 › log-card`; a shared or by-action part is named the same on every screen it shows on.', '',
         '**How to read the values.** Kit part: the gallery number in `tools/parts-kit/README.md` › Parts. Press: how it '
         'presses ([Presses](#presses)). Corner: a named corner (`--r-card` …), `capsule`, `circle` or `none`. Motion: the '
         'springs and named timings its own transitions use (`gentle`, `--ease-out`, `--dur-fade` …), `none` when it '
         'doesn\'t move at rest; a press\'s own motion is in Presses. Decision: the IDs in `js/parts.settings.js` '
         '([Decisions](#decisions)). A part that shows in more than one place lists each value it has (`a · b`). A dash: '
         'the sample data doesn\'t reach it ([Not reached](#not-reached)). Statuses: In use · Phasing out · Retired.', '',
         '**%d shared parts, %d names by action, %d parts named on their screens. %d of %d in use read from the app.**'
         % (len(sh), len(ac), len(on), len(live) - len(missed), len(live)), '']
    L += ['## Shared', '', 'Named wherever they show: the tab bar, Back, Close, the standard roles, fields and links.', '',
          head, rule]
    L += ['| `%s` | `%s` | %s | %s |' % (p[1], esc(p[2]), cells(p), p[3]) for p in sh] + ['']
    L += ['## By action', '', 'Wherever the action shows, its button gets this name. A screen\'s own parts and the shared ones win over these.', '',
          head, rule]
    L += ['| `%s` | `%s` | %s | %s |' % (p[1], esc(p[2]), cells(p), p[3]) for p in ac] + ['']
    L += presses(vals, reg)
    L += ['## Decisions', '',
          'Every decision in `js/parts.settings.js`, in its order. A row above names the ones that cover it; the rest '
          'cover the whole app. The register of them, with dates and reasons, is the project note `suki_parts_decisions.md`.', '',
          '| Decision | Setting | What it says |', '|---|---|---|']
    L += ['| %s | `%s` | %s |' % (i, k, esc(t)) for i, k, t in decisions()] + ['']
    L += ['## Retired values', '',
          'Values Suki dropped. None may come back on a part: `test_screens.py` › `reference` fails if one does. Where each '
          'came from: `tools/parts-kit/REPLACED.md` and MAINTAINING › Value set.', '',
          '| Value | Was | Now | Status |', '|---|---|---|---|']
    L += ['| `%s` | %s | %s | Retired · %s |' % (esc(k), w, n, s) for k, w, n, s in RETIRED] + ['']
    L += ['## On their screens', '']
    group = None
    for p in on:
        if p[5] != group:
            if group: L.append('')
            group = p[5]
            L += ['### ' + group, '', head + ' Was |', rule + '---|']
        L.append('| `%s` | `%s` | %s | %s | %s |' % (p[1], esc(p[2]), cells(p), p[3], p[4]))
    L += ['', '## Not reached', '',
          'Parts in use that the sample data doesn\'t show (a state such as a full drawer, an empty list or a tip), so their '
          'values are a dash. Their kit part, if any, is read from how they\'re found. Reaching more of them is a change to '
          '`collect()` in `tools/reference/elements.py`.', '',
          '<details><summary>Not reached (%d)</summary>' % len(missed), '']
    L += ['- `%s`' % (p[1] if p[0] in ('shared', 'action') else p[0] + ' › ' + p[1]) + (' (by action: `%s`)' % esc(p[2]) if p[0] == 'action' else '') for p in missed]
    L += ['', '</details>']
    return '\n'.join(L).rstrip() + '\n'


def sheet(b=None):
    """Collect from the app and build the sheet's text: (text, values, register parts, unlisted named elements).
    Opens its own headless Chromium when b is None."""
    if b is not None:
        seen, unlisted, R = collect(b)
        v, reg = values(seen), register(R)
        return build(v, reg), v, reg, unlisted
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        try:
            return sheet(br)
        finally:
            br.close()


if __name__ == '__main__':
    text, vals, reg, unlisted = sheet()
    for msg, bad in (('no kit part and no reason (add one to REASONS)', problems(vals, reg)),
                     ('named on the page but not in the register', unlisted),
                     ('a retired value', retired(vals, reg)),
                     ('a decision js/parts.settings.js doesn\'t have', unknown_decisions(vals))):
        if bad: print(msg + ': ' + ', '.join(bad))
    if '--check' in sys.argv:
        same = os.path.exists(OUT) and open(OUT, encoding='utf-8').read() == text
        print('reference/elements.md is ' + ('up to date' if same else 'out of date: run python3 tools/reference/elements.py'))
        sys.exit(0 if same else 1)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write(text)
    print('wrote reference/elements.md')
