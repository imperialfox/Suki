"""Home's exchange rate card (Q17): today's rate above the summary card, how old it is in plain words, the whole card as
one door to Convert (with no refresh), the card with no rate yet, an old rate staying white, the one-off navy colours
(the same in dark mode, white passing 4.5:1), iPhone on its side and iPad, and screenshots at 375 and 402 px."""
import os
import re
import datetime as dt
from harness import sample, RATE, ROOT

CSS = open(os.path.join(ROOT, 'css', 'app.css'), encoding='utf-8').read()


def token(name):
    m = re.search(r'--' + name + r':\s*([^;]+);', CSS)
    return m.group(1).strip() if m else ''


def rgb(v):
    """'#173874' or 'rgba(75, 132, 255, 0.35)' → (r, g, b, a)."""
    if v.startswith('#'):
        h = v[1:]
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (1.0,)
    n = [float(x) for x in re.findall(r'[\d.]+', v)]
    return (n[0], n[1], n[2], n[3] if len(n) > 3 else 1.0)


def over(top, under):
    a = top[3]
    return tuple(top[i] * a + under[i] * (1 - a) for i in range(3)) + (1.0,)


def lum(c):
    f = lambda x: (x / 255) / 12.92 if x / 255 <= 0.03928 else (((x / 255) + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def ago(**kw):
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(**kw)).isoformat()


def at_age(pg, iso):
    pg.evaluate("iso=>{D.rate.cachedAt=iso;rerender()}", iso)
    pg.wait_for_timeout(60)
    return pg.inner_text('#rateAge')


WIDE = "document.documentElement.scrollWidth>document.documentElement.clientWidth+1"


def run(b, t):
    ok = t.ok

    # ── 1 · The card above the total spent card ─────────────────
    pg = t.page(b)
    ok(pg.locator('#app .ratecard').count() == 1, 'Home has one exchange rate card')
    order = pg.evaluate("(()=>{const r=document.querySelector('.ratecard'),s=document.querySelector('.sumcard');return !!(r.compareDocumentPosition(s)&Node.DOCUMENT_POSITION_FOLLOWING)&&r.getBoundingClientRect().bottom<=s.getBoundingClientRect().top})()")
    ok(order, 'it sits above the total spent card')
    ok(pg.inner_text('.ratecard .rk') == 'Exchange rate', 'it’s labelled “Exchange rate”')
    ok(pg.inner_text('.ratecard .rv') == '£1 = ₱' + f'{RATE:.2f}', 'it shows £1 = ₱74.12')
    ok(pg.inner_text('#rateAge') == 'Updated just now', 'a rate just fetched reads “Updated just now”')
    look = pg.evaluate("(()=>{const s=getComputedStyle(document.querySelector('.ratecard .rv')),k=getComputedStyle(document.querySelector('.ratecard .rk')),c=getComputedStyle(document.querySelector('.ratecard'));return [s.fontSize,s.fontWeight,k.fontSize,c.borderTopLeftRadius,s.color]})()")
    ok(look[:4] == ['22px', '700', '13px', '20px'], 'the rate is Title 2 bold, the label Footnote, and the card’s corners 20 pt')
    ok(look[4] == 'rgb(255, 255, 255)', 'the rate is white')
    ok(pg.evaluate("document.querySelector('.ratecard').tagName") == 'BUTTON' and pg.locator('.ratecard button').count() == 0,
       'the whole card is one button')

    # ── 2 · How old it is, in plain words ───────────────────────
    ok(at_age(pg, ago(minutes=5)) == 'Updated 5 min ago', '5 minutes old reads “Updated 5 min ago”')
    ok(at_age(pg, ago(hours=2, minutes=10)) == 'Updated 2h ago', '2 hours old reads “Updated 2h ago”')
    noon_yday = dt.datetime.combine(dt.date.today() - dt.timedelta(days=1), dt.time(0, 5)).astimezone()
    if (dt.datetime.now().astimezone() - noon_yday) >= dt.timedelta(hours=24):
        ok(at_age(pg, noon_yday.isoformat()) == 'Updated yesterday', 'over a day old, from yesterday, reads “Updated yesterday”')
    ok(at_age(pg, ago(days=3)) == 'Updated 3 days ago', '3 days old reads “Updated 3 days ago”')
    old = dt.date.today() - dt.timedelta(days=10)
    want = 'Updated ' + str(old.day) + ' ' + old.strftime('%b') + ('' if old.year == dt.date.today().year else ' ' + str(old.year))
    ok(at_age(pg, ago(days=10)) == want, 'after a week it gives the date (“' + want + '”)')
    ok(pg.evaluate("getComputedStyle(document.querySelector('.ratecard .rv')).color") == 'rgb(255, 255, 255)'
       and pg.evaluate("getComputedStyle(document.querySelector('#rateAge')).color") == pg.evaluate("getComputedStyle(document.querySelector('.ratecard .rk')).color"),
       'an old rate keeps its white text, never red')
    at_age(pg, ago(days=3))
    ok(pg.get_attribute('.ratecard', 'aria-label') == 'Exchange rate £1 = ₱74.12, updated 3 days ago. Open Convert', 'the VoiceOver label reads in full')

    # the age moves on in place, with no redraw
    at_age(pg, ago(minutes=1, seconds=5))
    pg.evaluate("window.__card=document.getElementById('rateCard');D.rate.cachedAt=new Date(Date.now()-7*6e4).toISOString();tickRateAge()")
    ok(pg.inner_text('#rateAge') == 'Updated 7 min ago' and pg.evaluate("window.__card===document.getElementById('rateCard')"),
       'the age moves on in place while Home is open')
    ok(pg.get_attribute('.ratecard', 'aria-label').endswith('updated 7 min ago. Open Convert'), 'and so does its VoiceOver label')

    # two decimals, always
    pg.evaluate("D.rate.value=76.1;rerender()")
    ok(pg.inner_text('.ratecard .rv') == '£1 = ₱76.10', 'the rate always has two decimals (₱76.10)')
    pg.evaluate("D.rate.value=76.1249;rerender()")
    ok(pg.inner_text('.ratecard .rv') == '£1 = ₱76.12', 'and rounds to two (₱76.12)')

    # ── 3 · Tapping opens Convert, with no refresh ──────────────
    pg.evaluate("D.rate.value=%s;D.rate.cachedAt=new Date().toISOString();rerender();window.__refresh=0;const o=refreshRate;refreshRate=function(){window.__refresh++;return o.apply(this,arguments)};0" % RATE)
    pg.click('.ratecard'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.tab") == 'convert' and pg.locator('#conv-gbp').count() == 1, 'tapping the card opens Convert')
    ok(pg.evaluate("window.__refresh") == 0, 'tapping it doesn’t refresh the rate (Convert’s own Refresh stays)')
    pg.click('#dock [data-v=home]'); pg.wait_for_timeout(120)
    pg.focus('.ratecard'); pg.keyboard.press('Enter'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.tab") == 'convert', 'it opens Convert from the keyboard too')
    pg.click('#dock [data-v=home]'); pg.wait_for_timeout(120)

    # ── 4 · A refreshed rate shows on the card ──────────────────
    pg.evaluate("D.rate.cachedAt=new Date(Date.now()-3*864e5).toISOString();rerender()")
    pg.evaluate("refreshRate(true)")
    pg.wait_for_function("document.getElementById('rateAge')&&document.getElementById('rateAge').textContent==='Updated just now'", timeout=8000)
    ok(True, 'after a refresh (pull to refresh or Convert) the card reads “Updated just now”')
    pg.context.close()

    # ── 5 · No saved rate yet ───────────────────────────────────
    d = sample(); d['rate'] = None
    pg = t.page(b, data=d, rate_fail=True)
    ok(pg.evaluate("D.rate") is None and pg.locator('.ratecard.none').count() == 1, 'with no saved rate there’s still a card')
    ok(pg.inner_text('.ratecard .rk') == 'Exchange rate' and pg.inner_text('.ratecard .rget') == 'Get today’s rate on Convert',
       'it reads “Exchange rate · Get today’s rate on Convert”')
    ok(pg.locator('#rateAge').count() == 0 and '£1' not in pg.inner_text('.ratecard'), 'with no rate and no age')
    pg.click('.ratecard'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.tab") == 'convert', 'and tapping it opens Convert')
    pg.context.close()
    # a brand new install: the rate card and the "Nothing spent yet" card
    pg = t.page(b, data=None, rate_fail=True)
    ok(pg.locator('.ratecard.none').count() == 1 and pg.locator('.sumcard.none').count() == 1, 'a fresh install shows the rate card above “Nothing spent yet”')
    pg.context.close()

    # ── 6 · The navy: the same in dark mode, and white passes 4.5:1 ──
    top, bottom, glow, fg, fg2 = (rgb(token(n)) for n in ('suki-top', 'suki-bottom', 'suki-glow', 'suki-fg', 'suki-fg2'))
    ok(token('suki-top') == '#173874' and token('suki-bottom') == '#06102b' and glow[:3] == (75, 132, 255),
       'the tokens are the icon’s navy (#173874 → #06102b) and its blue glow (#4b84ff)')
    lit = over(glow, top)  # the brightest spot: the glow over the top end
    worst = min(contrast(fg, top), contrast(fg, bottom), contrast(fg, lit))
    ok(worst >= 4.5, f'white passes 4.5:1 on both navy ends and under the glow (lowest {worst:.1f}:1)')
    soft = min(contrast(over(fg2, c), c) for c in (top, bottom, lit))
    ok(soft >= 4.5, f'the softer white (label and age) passes 4.5:1 too (lowest {soft:.1f}:1)')
    users = [sel.strip() for sel, body in re.findall(r'([^{}]+)\{([^{}]*)\}', re.sub(r'/\*.*?\*/', '', CSS, flags=re.S)) if 'var(--suki-' in body]
    ok(users and all(sel.startswith('.ratecard') for sel in users), 'the navy tokens are used by the rate card only')

    looks = {}
    for sc in ('light', 'dark'):
        for w in (375, 402):
            pg = t.page(b, w=w, h=874 if w == 402 else 812, sc=sc)
            looks.setdefault(sc, pg.evaluate("(()=>{const c=getComputedStyle(document.querySelector('.ratecard'));return c.backgroundImage+'|'+c.color})()"))
            ok(not pg.evaluate(WIDE), f'no sideways scroll at {w} px, {sc}')
            fits = pg.evaluate("(()=>{const c=document.querySelector('.ratecard').getBoundingClientRect(),v=document.querySelector('.ratecard .rv').getBoundingClientRect();return v.right<=c.right&&c.left>=0&&c.right<=innerWidth})()")
            ok(fits, f'the rate fits inside the card at {w} px, {sc}')
            t.shot(pg, f'home-{w}-{sc}', clip={'x': 0, 'y': 0, 'width': w, 'height': 420})
            if w == 375:
                pg.evaluate("D.rate=null;rerender()")
                t.shot(pg, f'norate-{w}-{sc}', clip={'x': 0, 'y': 0, 'width': w, 'height': 420})
            pg.context.close()
    ok(looks['light'] == looks['dark'], 'the card looks the same in light and dark, like a card in Wallet')

    # ── 7 · iPhone on its side and iPad: it heads the left column ──
    for w, h, name in ((852, 393, 'iPhone on its side'), (820, 1180, 'iPad'), (1180, 820, 'iPad on its side')):
        pg = t.page(b, w=w, h=h)
        first = pg.evaluate("(()=>{const c=document.querySelector('.dash > div:first-child');return !!c&&c.firstElementChild&&c.firstElementChild.classList.contains('ratecard')&&!!c.querySelector('.sumcard')})()")
        ok(first, f'{name}: the card heads the left column, above the summary card')
        ok(not pg.evaluate(WIDE), f'{name}: no sideways scroll')
        t.shot(pg, f'dash-{w}x{h}')
        pg.context.close()
