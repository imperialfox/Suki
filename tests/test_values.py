"""2.30 Value set (Q26): one named set of look and motion values, and a guard against new strays, as Vocal Sessions has
since its Q40 (the app look skill, 6b). From the UI consistency audit of 2.27, findings 18, 19, 22 and part of 21.

named    the set at the top of css/app.css has the parts kit's names and numbers (kit 1.2.0) and Suki's own; every name
         used is defined (in the set or as a MOTION spring); MOTION.EASE holds the same three curves for code; the names
         resolve in the page;
css      in css/app.css every corner above 6 px (not 999px or 50%), every :active press scale(), every transition and
         animation easing and duration, and every shadow is a named value or on KNOWN; the list may only get shorter
         (a new stray fails, and a stray that's gone but still listed fails too, with a "list can shrink" message);
speed    every stylesheet duration that isn't a spring follows the speed (times var(--mspeed)): Slow motion slows the
         dim, the iPad sheet and the toast's fade, motion off stops them, Reduce Motion's fades keep their length;
js       in js/ every cubic-bezier(, keyword easing and hard-set duration (duration: or ms: with a number) is on its
         known list (MOTION.EASE's own three are the names), with the same rule;
guard    the guard itself works, on copies (a new corner, press, curve, duration, shadow and a duration that ignores
         the speed are caught; named, exempt and removed values handled; new curves, keywords and times in code caught);
retired  the tab bar's padding transition and the tab buttons' max-width and height transitions are gone (Suki never
         had a folding tab bar), and nothing in app.css transitions a size of something blurred.

Exempt: graphic corners of 6 px and under, capsules (999px) and circles (50%); slow loops of 1 s and over (from
naming, not from the speed); delays; 0; the springs (gentle, nav, ripple, published by js/motion.js already at the
speed); rings drawn with box-shadow (every layer without offset or blur: outlines, not shadows).
How to add a value on purpose, and why the lists only shrink: MAINTAINING.md › Value set (Q26).
SUKI_VALUES=named,css,speed,js,guard,retired runs only those parts."""
import os, re, glob, collections
from harness import ROOT

_only = [x for x in os.environ.get('SUKI_VALUES', '').split(',') if x]
wanted = lambda k: not _only or k in _only
CSS = os.path.join(ROOT, 'css', 'app.css')
JSDIR = os.path.join(ROOT, 'js')
# data files, with no motion in them
JS_SKIP = ('towns.js', 'ratesnap.js', 'prices.js', 'typical.js', 'news.js', 'catalog.js', 'register.js')

# the agreed set (Render 5 Nov 2026, 09:17): the parts kit 1.2.0's numbers, and Suki's own. Change a number here and in
# app.css together, on purpose
NAMED = {
    'r-small': '10px', 'r-medium': '14px', 'r-card': '20px', 'r-large': '26px', 'r-sheet': '46px', 'r-alert': '34px',
    'r-actions': '28px',
    'press': '0.93', 'press-row': '0.98',
    'ease-pop': 'cubic-bezier(0.3, 1.7, 0.45, 1)', 'ease-knob': 'cubic-bezier(0.3, 1.35, 0.5, 1)',
    'ease-out': 'cubic-bezier(0.2, 0.8, 0.2, 1)', 'ease-in-out': 'cubic-bezier(0.65, 0, 0.35, 1)',
    'ease-decel': 'cubic-bezier(0.33, 1, 0.68, 1)', 'ease-accel': 'cubic-bezier(0.32, 0, 0.67, 0)',
    'ease-back': 'cubic-bezier(0.34, 1.56, 0.64, 1)', 'ease-lift': 'cubic-bezier(0, 0, 0.58, 1)',
    'ease-linear': 'linear', 'ease-steps': 'steps(8)',
    'dur-quick': '120ms', 'dur-fade': '200ms', 'dur-lift-in': '150ms', 'dur-lift-out': '60ms', 'dur-switch': '380ms',
    'dur-knob': '150ms', 'dur-squish': '450ms', 'dur-appear': '250ms', 'dur-leave': '350ms', 'dur-cover': '500ms',
    'dur-toast-in': '500ms', 'dur-toast-out': '350ms', 'dur-close': '170ms', 'dur-ramp': '260ms', 'dur-reduced': '100ms',
    'dur-glint': '500ms', 'dur-progress': '600ms', 'dur-spin': '1s', 'dur-rise': '350ms',
    'shadow-lifted': '0 8px 24px rgba(0, 0, 0, 0.18)', 'shadow-floating': '0 8px 33px rgba(0, 0, 0, 0.08)',
    'shadow-glow': '0 0 22px rgba(0, 122, 255, 0.35)',
    # Suki's own
    'r-form': '28px', 'press-fade': '0.35', 'r-till': '12px', 'r-cup': '85%',
}
SPRINGS = ('gentle', 'nav', 'ripple')

# ---------------------------------------------------------------- reading the stylesheet (Vocal Sessions' reader)

AT_SKIP = ('@media', '@supports', '@container', '@layer')


def declarations(css):
    """Every declaration in the stylesheet: (selector, line, property, value, start, end). Comments are skipped; nested
    @media keeps its selector."""
    src = re.sub(r'/\*.*?\*/', lambda m: re.sub(r'[^\n]', ' ', m.group(0)), css, flags=re.S)
    out, stack = [], []
    start, paren = 0, 0
    for i, c in enumerate(src):
        if c == '(':
            paren += 1
        elif c == ')':
            paren -= 1
        elif paren == 0 and c in '{};':
            chunk = src[start:i]
            if c == '{':
                stack.append(' '.join(chunk.split()))
            else:
                d = _decl(stack, chunk, start, src)
                if d:
                    out.append(d)
                if c == '}' and stack:
                    stack.pop()
            start = i + 1
    return out


def _decl(stack, chunk, start, src):
    if ':' not in chunk:
        return None
    k = chunk.index(':')
    p = chunk[:k].strip().lower()
    if not re.fullmatch(r'-?[a-z][a-z-]*', p):
        return None
    lead = len(chunk) - len(chunk.lstrip())
    line = src.count('\n', 0, start + lead) + 1
    sel = ' › '.join(s for s in stack if not s.startswith(AT_SKIP))
    return sel, line, p, ' '.join(src[start + k + 1:start + len(chunk.rstrip())].split()), start + k + 1, start + len(chunk.rstrip())


def split_top(v, sep):
    """Split at sep outside brackets."""
    out, depth, cur = [], 0, ''
    for c in v:
        depth += c == '('
        depth -= c == ')'
        if depth == 0 and (c == sep if sep != ' ' else c.isspace()):
            if cur.strip():
                out.append(cur.strip())
            cur = ''
        else:
            cur += c
    if cur.strip():
        out.append(cur.strip())
    return out


TIME = re.compile(r'^(-?\d*\.?\d+)(ms|s)$')
KEYWORD_EASE = {'ease', 'ease-in', 'ease-out', 'ease-in-out', 'linear', 'step-start', 'step-end'}


def ms(tok):
    m = TIME.match(tok)
    return float(m.group(1)) * (1 if m.group(2) == 'ms' else 1000) if m else None


def is_ease(tok):
    return tok in KEYWORD_EASE or tok.startswith(('cubic-bezier(', 'steps(', 'linear('))


def norm(tok):
    return re.sub(r'\s*,\s*', ', ', re.sub(r'\(\s*', '(', re.sub(r'\s*\)', ')', tok)))


def inner(d):
    """A duration without its speed: calc(0.5s * var(--mspeed, 1)) → 0.5s, calc(var(--dur-fade) * …) → var(--dur-fade)."""
    m = re.fullmatch(r'calc\(\s*(.+?)\s*\*\s*var\(--mspeed(?:,\s*1)?\)\s*\)', d)
    return m.group(1) if m else d


def spring(d):
    return re.match(r'var\(--dur-(%s)\b' % '|'.join(SPRINGS), d) is not None


def ring(v):
    """A box-shadow whose every layer has no offset and no blur: an outline, not a shadow."""
    for layer in split_top(v, ','):
        nums = [t for t in split_top(layer, ' ') if re.fullmatch(r'-?\d*\.?\d+(px)?', t)]
        if len(nums) < 3 or any(float(n.rstrip('px')) != 0 for n in nums[:3]):
            return False
    return True


def items(css):
    """Every value the guard looks at: (kind, selector, property, token, line, named?), kind being corner, press, ease,
    duration or shadow. Exempt values aren't listed. Also returns every duration with whether it follows the speed."""
    out, speed = [], []
    for sel, line, p, v, s, e in declarations(css):
        if p.startswith('--'):
            continue
        v = re.sub(r'\s*!important$', '', v)
        if p == 'box-shadow' and v not in ('none', 'inherit', 'initial') and not ring(v):
            out.append(('shadow', sel, p, v, line, re.fullmatch(r'var\(--shadow-[a-z-]+\)', v) is not None))
        if 'radius' in p:
            for tok in split_top(v.replace('/', ' '), ' '):
                if tok.startswith('var('):
                    out.append(('corner', sel, p, tok, line, tok.startswith('var(--r-')))
                    continue
                m = re.fullmatch(r'(\d*\.?\d+)px', tok)
                if tok in ('0', '999px', '50%', 'inherit', 'initial') or (m and float(m.group(1)) <= 6):
                    continue
                out.append(('corner', sel, p, tok, line, False))
        if ':active' in sel and p in ('transform', 'scale'):
            args = re.findall(r'\bscale\(((?:[^()]|\([^()]*\))*)\)', v) if p == 'transform' else [v]
            for a in args:
                a = a.strip()
                if a.startswith('var(--press'):
                    out.append(('press', sel, p, f'scale({a})', line, True))
                elif re.fullmatch(r'\d*\.?\d+', a) and float(a) >= 1:
                    continue
                else:
                    out.append(('press', sel, p, f'scale({a})', line, False))
        if p.startswith(('transition', 'animation')):
            if p.endswith('-delay') or p.endswith(('-name', '-property', '-fill-mode', '-iteration-count',
                                                   '-direction', '-play-state', '-behavior')):
                continue
            for seg in split_top(v, ','):
                toks = split_top(seg, ' ')
                if p.endswith('-timing-function'):
                    durs, eases = [], toks
                elif p.endswith('-duration'):
                    durs, eases = toks, []
                else:
                    times = [t for t in toks if ms(t) is not None or t.startswith(('var(--dur-', 'calc('))]
                    durs = times[:1]  # the second time in a shorthand is a delay
                    eases = [t for t in toks if is_ease(t) or t.startswith('var(--ease-')]
                for d in durs:
                    i = inner(d)
                    if ms(i) == 0:
                        continue
                    speed.append((sel, p, d, line, spring(i) or '--mspeed' in d))
                    if ms(i) is not None and ms(i) >= 1000:
                        continue  # a slow loop: exempt from naming, not from the speed
                    out.append(('duration', sel, p, i, line, ms(i) is None and i.startswith('var(--dur-')))
                for t in eases:
                    out.append(('ease', sel, p, norm(t), line, t.startswith('var(--ease-')))
    return out, speed


def key(it):
    return ' · '.join(it[:4])


# ---------------------------------------------------------------- reading the code

def strip_comments(src):
    src = re.sub(r'/\*.*?\*/', lambda m: re.sub(r'[^\n]', ' ', m.group(0)), src, flags=re.S)
    return '\n'.join(re.sub(r'(^|\s)//.*$', '', ln) for ln in src.split('\n'))


def js_values(files=None):
    """Curves, keyword easings and hard-set durations in js/, as 'file · kind · value'. MOTION.EASE's own three (the
    names, for code) are returned apart."""
    found, names = [], {}
    for f in files or sorted(x for x in glob.glob(os.path.join(JSDIR, '*.js')) if os.path.basename(x) not in JS_SKIP):
        name, src = (os.path.basename(f), open(f, encoding='utf-8').read()) if isinstance(f, str) else f
        src = strip_comments(src)
        ease = re.search(r'const EASE = \{(.*?)\};', src, re.S) if name == 'motion.js' else None
        if ease:
            names = {k: norm(c) for k, c in re.findall(r"(\w+): '(cubic-bezier\([^)]*\))'", ease.group(1))}
            src = src[:ease.start()] + src[ease.end():]
        found += [f'{name} · curve · {norm(c)}' for c in re.findall(r'cubic-bezier\([^)]*\)', src)]
        found += [f'{name} · keyword · {k}' for k in re.findall(r"""['"](ease|ease-in|ease-out|ease-in-out|linear)['"]""", src)]
        found += [f'{name} · duration · {d}' for d in
                  re.findall(r'\b(?:duration|ms)\s*:\s*\(?\s*(?:[\w.]+\s*\|\|\s*)?(\d+(?:\.\d+)?)\b', src)]
    return found, names


def compare(found, known):
    """(new, gone): what's in found but not known, and what's known but no longer found (as multisets)."""
    f, k = collections.Counter(found), collections.Counter(known)
    return list((f - k).elements()), list((k - f).elements())


def same_curve(a, b):
    nums = lambda s: [float(x) for x in re.findall(r'-?\d*\.?\d+', s)]
    return nums(a) == nums(b)


# ---------------------------------------------------------------- the known lists (they may only get shorter)
# Every value here was in the app at Q26 (2.30) and doesn't match a name, or matches a number but not the meaning. They
# leave as their parts move onto the parts kit (Q27 and Q28) or get a name, so nothing is tidied twice. Remove a line
# when its value goes; never add one (MAINTAINING.md › Value set (Q26) says how to add a value on purpose).

KNOWN = [
    # corners Suki's look uses that the kit has no name for (18, 16, 12, 8 px); they stay until a part needs a new name
    'corner · .tbtn · border-radius · 8px',
    'corner · .tile.big · border-radius · 18px',
    'corner · .stile · border-radius · 8px',
    'corner · .nudge · border-radius · 16px',
    'corner · .inp · border-radius · 12px',
    'corner · .locbtn · border-radius · 12px',
    'corner · .searchbox · border-radius · 12px',
    'corner · .sbi · border-radius · 12px',
    'corner · .wrow .stile · border-radius · 12px',
    'corner · .appico · border-radius · 8px',
    'corner · #tip · border-radius · 18px',
    'corner · .perline .plabel.cal · border-radius · 8px',
    # sheets: 34 now, the kit's --r-sheet (46, D17) with the kit's sheet at Q27; the page behind follows the sheet (D21)
    'corner · body.sheet-open .wrap · border-radius · 28px',
    'corner · .sheet · border-radius · 34px',
    'corner · .shead · border-radius · 34px',
    'corner · .shead · border-radius · 34px',
    # Home's two figures shrink to 0.96 and fade until D06 makes card doors highlight (Q28)
    'press · .sumcard .door:active · transform · scale(0.96)',
    # the press settle: a 0.5 s pop with no kit name; the kit's press and release springs replace it at Q28
    'duration · .sumcard .door · transition · 0.5s',
    'duration · .ratecard · transition · 0.5s',
    'duration · .cta, .circ, .btn, .chip, .tabbar button, .toptabs button, .sbi · transition · 0.5s',
    'duration · .row · transition · 0.5s',
    'duration · .dn · transition · 0.5s',
    'duration · .tabbar button · transition · 0.5s',
    # the page behind a sheet: its own bouncy curve and timings until it follows the kit's sheet (D21, Q27)
    'ease · .wrap · transition · cubic-bezier(0.3, 1.3, 0.5, 1)',
    'duration · .wrap · transition · 0.45s',
    'duration · .wrap · transition · 0.45s',
    'duration · body.unsheet .wrap · transition-duration · 0.33s',
    'ease · body.unsheet .wrap · transition-timing-function · cubic-bezier(0.3, 0, 0.25, 1)',
    # sheets and toasts: Suki's own until the kit's sheet and toast (Q27)
    'duration · .sheet.back · transition · 0.32s',
    'ease · .sheet.back · transition · cubic-bezier(0.3, 1.2, 0.5, 1)',
    'duration · .toast · transition · 0.22s',
    # iPad and Mac sheets stay Suki's own (S01): their pop has no kit name yet
    'duration · body.reg .sheet · animation · 0.42s',
    'ease · body.reg .sheet · animation · cubic-bezier(0.28, 1.25, 0.45, 1)',
    # the switch knob: 0.3 s until the kit's switch (380 ms, Q28)
    'duration · .sw-ui::after · transition · 0.3s',
    # Reduce Motion's fade: its length moves to --dur-reduced with the kit at Q27 (D20); the keyword goes with it
    'ease · html.motion-reduced .sheet, html.motion-reduced .toast · animation · ease-out',
    # swipe to delete stays Suki's own (Vocal Sessions kept its own too)
    'duration · .sw .fg · transition · 0.22s',
    'ease · .sw .fg · transition · ease',
    # spinners and the location pulse, faster than the kit's 1 s spinner (part 25); named when they move to it
    'duration · .locbtn.busy svg.i · animation · 0.8s',
    'ease · .locbtn.busy svg.i · animation · ease-in-out',
    'duration · .btn.busy svg.i · animation · 0.9s',
    'duration · #ptr.go .spin · animation · 0.8s',
    'duration · .spin i · transition · 0.08s',
    # pull to refresh snapping back, and the launch icon: their own curves
    'duration · main.ptr-snap · transition · 0.42s',
    'ease · main.ptr-snap · transition · cubic-bezier(0.25, 0.8, 0.3, 1)',
    'ease · #splash · transition · ease',
    'duration · #splash img · transition · 0.45s',
    'ease · #splash img · transition · cubic-bezier(0.3, 0.9, 0.4, 1)',
    # onboarding's tip bubble (kit part 50, glass appearing, has no number for it yet)
    'duration · #tip · transition · 0.18s',
    'ease · #tip · transition · ease',
    'duration · #tip · transition · 0.18s',
    'ease · #tip · transition · ease',
    'duration · #tip.on · transition · 0.3s',
    'ease · #tip.on · transition · ease',
]

# shadows, written out by hand: the kit names three and Suki uses none of them exactly
KNOWN_SHADOWS = [
    # Liquid Glass and the solid buttons: their own light until the kit's glass and press parts (Q27, Q28)
    'shadow · .glass · box-shadow · inset 0 -0.5px 0 var(--glass-lo), inset 0 0 16px var(--glass-glow), 0 12px 32px var(--glass-shadow)',
    'shadow · .cta · box-shadow · inset 0 1px 0 rgba(255, 255, 255, 0.45), inset 0 0 0 0.5px rgba(0, 0, 0, 0.12), 0 8px 24px var(--glass-shadow)',
    'shadow · .sw-ui::after · box-shadow · 0 3px 8px var(--glass-shadow)',
    'shadow · .segc .knob · box-shadow · 0 3px 8px var(--glass-shadow)',
    # icon tiles' top light, the rate card's navy (Q17) and the launch icon
    'shadow · .tile · box-shadow · inset 0 1px 0 rgba(255, 255, 255, 0.3)',
    'shadow · .ratecard · box-shadow · inset 0 0 0 0.5px var(--suki-rim), 0 8px 24px var(--suki-shadow)',
    'shadow · #splash img · box-shadow · 0 10px 30px rgba(10, 30, 80, 0.3)',
    # the page under a push and a swipe back (Q24)
    'shadow · #over > .wrap · box-shadow · -8px 0 24px var(--glass-shadow)',
    'shadow · body.pushing > .wrap, body.swiping > .wrap · box-shadow · -8px 0 24px var(--glass-shadow)',
    # Quick Till's notes and coins, the drawer's walls, lip and cups: Suki's own drawing, lit from the top left (Q18 to Q21)
    'shadow · #app .cashbox::after · box-shadow · 0 7px 10px -5px var(--dr-occlude), 0 2px 3px -2px var(--dr-occlude)',
    'shadow · .cashrow .nt · box-shadow · inset 0 0 0 1px color-mix(in srgb, var(--ni) 35%, transparent), 0 1px 1.5px color-mix(in srgb, var(--coin-ink) 14%, transparent)',
    'shadow · .cashrow .cn · box-shadow · inset 0 0 0 0.5px color-mix(in srgb, var(--coin-ink) 30%, transparent), 0 1.5px 0 var(--coin-edge), 0 0 0 1.5px var(--surface)',
    'shadow · .cashrow .cn.c20 · box-shadow · 0 1.5px 0 var(--ring-edge), 0 0 0 1.5px var(--surface)',
    'shadow · .tray · box-shadow · inset 5px 0 6px -5px var(--dr-wall), inset -5px 0 6px -5px var(--dr-wall), inset 0 -1px 0 var(--dr-lip)',
    'shadow · .tslot · box-shadow · inset 0 3px 4px -3px var(--dr-wall), 0 0.5px 0 var(--dr-lip)',
    'shadow · .tcup · box-shadow · inset 0 3px 4px -3px var(--dr-wall), inset 0 -4px 5px -3px var(--dr-lip), 0 0.5px 0 var(--dr-lip)',
    'shadow · .tslot i · box-shadow · 0 0 0 0.5px color-mix(in srgb, var(--ni) 35%, transparent), -0.5px 0 0 color-mix(in srgb, var(--ni) 30%, transparent)',
    'shadow · .tcup i · box-shadow · 0 1.2px 0 var(--coin-edge), inset 0 0 0 0.5px color-mix(in srgb, var(--coin-ink) 25%, transparent)',
    'shadow · .tcup i.r · box-shadow · 0 1.2px 0 var(--ring-edge), inset 0 0 0 2px var(--coin-ring)',
]

# in code: 'file · curve | keyword | duration · value'
KNOWN_JS = [
    # the note press and Fly (Q18): named once in PRESS and FLIGHT, Suki's own
    'events.js · curve · cubic-bezier(.3, 1.6, .5, 1)',
    'events.js · curve · cubic-bezier(.45, 0, .25, 1)',
    # the Till's press, slot and pulse, the segmented squish (450, the kit's --dur-squish in CSS) and the period
    # total's fade; the drawer's fades (named in FILL and DRAWER) and the location flash. They go with Q27's motion
    # (D18, D20) or stay Suki's own (the Till)
    'events.js · keyword · ease-out',
    'events.js · keyword · ease-out',
    'events.js · keyword · ease-out',
    'events.js · keyword · ease-out',
    'events.js · keyword · ease-out',
    'events.js · keyword · ease-out',
    'events.js · keyword · ease-out',
    'events.js · keyword · ease-out',
    'events.js · duration · 450',
    'events.js · duration · 180',
    'events.js · duration · 180',
    'gestures.js · keyword · ease-out',
    'gestures.js · keyword · ease-out',
    'gestures.js · keyword · ease-out',
    'locate.js · keyword · ease-out',
    'locate.js · duration · 700',
    # MOTION's fallback for a browser without linear() springs, and the Smart add fold's hinge (Q14, Suki's own)
    'motion.js · curve · cubic-bezier(.25, .9, .3, 1)',
    'motion.js · curve · cubic-bezier(.3, 1.25, .5, 1)',
    # Reduce Motion's fades (180 and 200; they move to --dur-reduced with the kit at Q27, D20), leave (220, ease-in) and
    # the Smart add fold's timings (Q14)
    'motion.js · keyword · ease-out',
    'motion.js · keyword · ease-out',
    'motion.js · keyword · ease-in',
    'motion.js · keyword · ease-out',
    'motion.js · keyword · ease-out',
    'motion.js · keyword · ease-in',
    'motion.js · duration · 180',
    'motion.js · duration · 200',
    'motion.js · duration · 220',
    'motion.js · duration · 150',
    'motion.js · duration · 200',
    'motion.js · duration · 420',
    'motion.js · duration · 120',
    'motion.js · duration · 140',
    'motion.js · duration · 240',
    'motion.js · duration · 260',
    'motion.js · duration · 440',
    # a sheet leaving: its own curve and the dim's fade, until the kit's sheet (Q27)
    'ui.js · curve · cubic-bezier(.3, 0, .25, 1)',
    'ui.js · keyword · ease-out',
    'ui.js · keyword · ease-in',
    'ui.js · keyword · ease-out',
]


# ---------------------------------------------------------------- the checks

def root_block(css):
    a = css.index(':root {')
    return css[a:css.index('\n}', a)]


def named(b, t):
    ok = t.ok
    css = open(CSS, encoding='utf-8').read()
    root = root_block(css)
    got = {k: ' '.join(v.split()) for k, v in re.findall(r'--([a-z0-9-]+):\s*([^;]+);', root)}
    bad = {k: got.get(k) for k, v in NAMED.items() if got.get(k) != v}
    ok(not bad, f'the set at the top of app.css has the agreed values ({bad})')
    ok(root.index('--r-small') < root.index('--bg:'), 'it sits at the very top, before the colours')
    defined = set(got) | {f'{a}-{s}' for s in SPRINGS for a in ('ease', 'dur')}
    used = set(re.findall(r'var\(--((?:r|ease|dur|shadow)-[a-z0-9-]+|press(?:-[a-z]+)?)\b', css))
    ok(used <= defined, f'every named value used is defined, in the set or as a MOTION spring ({used - defined})')
    _, names = js_values()
    ok(set(names) == {'pop', 'knob', 'out'} and all(same_curve(names[k], NAMED['ease-' + k]) for k in names),
       f'MOTION.EASE holds the same three curves as --ease-pop, --ease-knob and --ease-out ({names})')
    pg = t.page(b)
    vals = pg.evaluate("ks=>ks.map(k=>getComputedStyle(document.documentElement).getPropertyValue('--'+k).trim())", list(NAMED))
    got = dict(zip(NAMED, vals))
    ok(all(norm(got[k]) == norm(v) for k, v in NAMED.items()), f'the names resolve in the page ({ {k: v for k, v in got.items() if norm(v) != norm(NAMED[k])} })')
    ok(pg.evaluate("MOTION.EASE.out") == "cubic-bezier(.2,.8,.2,1)", 'MOTION.EASE.out is reachable from code')
    pg.context.close()


def css_strays(b, t):
    ok = t.ok
    css = open(CSS, encoding='utf-8').read()
    its, _ = items(css)
    stray = [i for i in its if not i[5] and i[0] != 'shadow']
    shadows = [i for i in its if not i[5] and i[0] == 'shadow']
    for found, known, what in ((stray, KNOWN, 'KNOWN'), (shadows, KNOWN_SHADOWS, 'KNOWN_SHADOWS')):
        new, gone = compare([key(i) for i in found], known)
        lines = collections.defaultdict(list)
        for i in found:
            lines[key(i)].append(i[4])
        label = 'shadows' if what == 'KNOWN_SHADOWS' else 'values'
        ok(not new, f'no new stray {label} in app.css' + ('' if not new else ': use a named value, or add one on purpose (MAINTAINING › Value set): '
           + '; '.join(f'line {lines[k][0]}: {k}' for k in new[:8]) + (f' … and {len(new) - 8} more' if len(new) > 8 else '')))
        ok(not gone, f'every known stray {label[:-1]} is still in app.css' + ('' if not gone else f': the list can shrink, so take these off {what} in '
           'tests/test_values.py: ' + '; '.join(gone[:8]) + (f' … and {len(gone) - 8} more' if len(gone) > 8 else '')))
    use = collections.Counter(i[0] for i in its if i[5])
    left = collections.Counter(k.split(' · ')[0] for k in KNOWN)
    jsleft = collections.Counter(k.split(' · ')[1] for k in KNOWN_JS)
    print(f'  ····  named uses: corners {use["corner"]}, presses {use["press"]}, easings {use["ease"]}, '
          f'durations {use["duration"]}, shadows {use["shadow"]}')
    print(f'  ····  known strays: corners {left["corner"]}, presses {left["press"]}, easings {left["ease"]}, '
          f'durations {left["duration"]}, shadows {len(KNOWN_SHADOWS)}; in code: curves {jsleft["curve"]}, '
          f'keywords {jsleft["keyword"]}, durations {jsleft["duration"]}')


SPEED_JS = """async s=>{MOTION.setSpeed(s);
 const L=document.getElementById('layer');ACT.openPurchase({dataset:{k:'a1'}});
 await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
 const sc=L.querySelector('.scrim'), sh=L.querySelector('.sheet');
 const t=document.createElement('div');t.className='toast';document.body.appendChild(t);
 const o={dim:getComputedStyle(sc).animationDuration, toast:getComputedStyle(t).transitionDuration,
   sheet:getComputedStyle(sh).animationDuration};
 t.remove();return o}"""


def speed(b, t):
    ok = t.ok
    css = open(CSS, encoding='utf-8').read()
    _, sp = items(css)
    deaf = [f'line {l}: {s} · {p} · {d}' for s, p, d, l, f in sp if not f]
    ok(not deaf, 'every stylesheet duration follows the speed: a spring, or times var(--mspeed, 1)'
       + ('' if not deaf else f' ({"; ".join(deaf[:6])})'))
    ok(len(sp) > 40, f'the speed check found the durations ({len(sp)})')
    sec = lambda v: [round(float(x[:-1]), 3) for x in v.split(',')]
    pg = t.page(b)
    one = pg.evaluate(SPEED_JS, 1)
    pg.context.close()
    pg = t.page(b)
    slow = pg.evaluate(SPEED_JS, 4)
    pg.context.close()
    ok(sec(one['dim']) == [0.2] and sec(slow['dim']) == [0.8], f'Slow motion slows the sheet dim, 0.2 s to 0.8 s ({one["dim"]} → {slow["dim"]})')
    ok(sec(one['toast'])[0] == 0.22 and sec(slow['toast'])[0] == 0.88, f'… and the toast’s fade, 0.22 s to 0.88 s ({one["toast"]} → {slow["toast"]})')
    pg = t.page(b, w=820, h=1180, ua=None)
    ipad = pg.evaluate(SPEED_JS, 4)
    pg.context.close()
    ok(sec(ipad['sheet']) == [1.68], f'… and the iPad sheet’s pop, 0.42 s to 1.68 s ({ipad["sheet"]})')
    pg = t.page(b)
    off = pg.evaluate(SPEED_JS, 0)
    ok(sec(off['dim']) == [0] and sec(off['toast'])[0] == 0, f'motion off stops the dim and the toast’s fade ({off})')
    ok(pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--mspeed').trim()") == '0', '--mspeed is 0 with motion off')
    pg.context.close()
    pg = t.page(b, init="localStorage.setItem('suki:reduceMotion','on')")
    rm = pg.evaluate(SPEED_JS, 1)
    tr = pg.evaluate("getComputedStyle(document.querySelector('.row')).transitionDuration")
    ok(sec(rm['dim']) == [0.2] and sec(rm['sheet']) == [0.2] and set(sec(tr)) == {0.2},
       f'Reduce Motion keeps its 0.2 s fades at speed 1 (dim {rm["dim"]}, sheet {rm["sheet"]}, a row {tr})')
    pg.evaluate("MOTION.setSpeed(4)")
    tr4 = pg.evaluate("getComputedStyle(document.querySelector('.row')).transitionDuration")
    ok(set(sec(tr4)) == {0.8}, f'… and Slow motion slows them too ({tr4})')
    pg.context.close()


def js_strays(b, t):
    ok = t.ok
    found, _ = js_values()
    new, gone = compare(found, KNOWN_JS)
    ok(not new, 'no new curves, keyword easings or hard-set durations in js/' + (f': use a MOTION spring, MOTION.EASE or a named constant ({new})' if new else ''))
    ok(not gone, 'every known one in code is still there' + (f': the list can shrink, so take these off KNOWN_JS in tests/test_values.py ({gone})' if gone else ''))
    ok(len(found) > 20, f'the code reader found them ({len(found)})')


def guard(b, t):
    """The guard catches what it should, on copies (the real files aren't touched)."""
    ok = t.ok
    css = open(CSS, encoding='utf-8').read()
    extra = ('\n.vtest:active { transform: scale(0.91); border-radius: 11px; box-shadow: 0 2px 9px red; '
             'transition: opacity calc(0.3s * var(--mspeed, 1)) cubic-bezier(0.1, 0.2, 0.3, 1); }\n')
    its, _ = items(css + extra)
    new, gone = compare([key(i) for i in its if not i[5]], KNOWN + KNOWN_SHADOWS)
    kinds = sorted(k.split(' · ')[0] for k in new)
    ok(kinds == ['corner', 'duration', 'ease', 'press', 'shadow'] and not gone,
       f'a new corner, press, curve, duration and shadow are each caught ({new})')
    _, sp = items(css + '\n.vtest { transition: opacity var(--dur-fade) var(--ease-out), color 0.3s; }\n')
    deaf = [d for s, p, d, l, f in sp if not f]
    ok(deaf == ['var(--dur-fade)', '0.3s'], f'a duration that ignores the speed is caught, named or not ({deaf})')
    named_extra = ('\n.vtest:active { transform: scale(var(--press)); border-radius: var(--r-card); box-shadow: var(--shadow-lifted); '
                   'transition: opacity calc(var(--dur-fade) * var(--mspeed, 1)) var(--ease-out), transform var(--dur-gentle) var(--ease-gentle); '
                   'animation: spin calc(2s * var(--mspeed, 1)) linear infinite; border-radius: 4px 999px 50%; }\n'
                   '.vtest2 { box-shadow: inset 0 0 0 1.5px var(--fg), 0 0 0 3px var(--bg); }\n')
    its, sp = items(css + named_extra)
    new, _ = compare([key(i) for i in its if not i[5]], KNOWN + KNOWN_SHADOWS)
    ok(new == ['ease · .vtest:active · animation · linear'],
       f'named values, springs, small corners, capsules, circles, rings and a slow loop’s length pass; its keyword doesn’t ({new})')
    if KNOWN:
        k = KNOWN[0].split(' · ')
        its, _ = items(css)
        line = next(i[4] for i in its if key(i) == KNOWN[0])
        src = css.splitlines(True)
        src[line - 1] = src[line - 1].replace(k[3], 'var(--r-card)', 1)
        its, _ = items(''.join(src))
        new, gone = compare([key(i) for i in its if not i[5] and i[0] != 'shadow'], KNOWN)
        ok(gone == [KNOWN[0]] and not new, f'a stray taken away is noticed, so the list must shrink ({gone})')
    files = [(os.path.basename(f), open(f, encoding='utf-8').read()) for f in glob.glob(os.path.join(JSDIR, '*.js'))
             if os.path.basename(f) not in JS_SKIP]
    found, _ = js_values(files + [('new.js', "el.animate(f, {duration: 310, easing: 'cubic-bezier(.1,.2,.3,1)'});\n"
                                             "el.animate(f, {ms: X.fade, easing: 'ease-in'}); // duration: 99, 'linear'")])
    new, _ = compare(found, KNOWN_JS)
    ok(sorted(new) == ['new.js · curve · cubic-bezier(.1, .2, .3, 1)', 'new.js · duration · 310', 'new.js · keyword · ease-in'],
       f'a new curve, keyword easing and hard-set time in code are caught; named times and comments aren’t ({new})')


def retired(b, t):
    ok = t.ok
    css = open(CSS, encoding='utf-8').read()
    sizes = [(l, s, v) for s, l, p, v, a, e in declarations(css)
             if p.startswith('transition') and re.search(r'(^|,\s*|\s)(max-width|max-height|height|width|padding)\b', v)]
    ok(not sizes, f'nothing transitions a size or padding (the folding tab bar’s leftovers are gone) ({sizes[:4]})')
    pg = t.page(b)
    tb = pg.evaluate("[getComputedStyle(document.querySelector('.tabbar')).transitionProperty, getComputedStyle(document.querySelector('.tabbar button')).transitionProperty]")
    ok(tb[0] == 'all' and 'max-width' not in tb[1] and 'height' not in tb[1],
       f'the tab bar has no padding transition and its buttons no max-width or height ({tb})')
    pg.context.close()


def run(b, t):
    if wanted('named'): named(b, t)
    if wanted('css'): css_strays(b, t)
    if wanted('speed'): speed(b, t)
    if wanted('js'): js_strays(b, t)
    if wanted('guard'): guard(b, t)
    if wanted('retired'): retired(b, t)
