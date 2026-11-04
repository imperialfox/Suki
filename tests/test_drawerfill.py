"""Quick Till: the drawer's contents and fullness (Q20). Each compartment labelled on its front lip; a fullness gauge,
not a count: only the cash handed over decides it, coins first, then 50s and 100s, then 500s, then 1000s, full at
₱20,000; overloaded from ₱50,000 (twelve sheets, the last four tipping out, eight coins with three spilling), the
notes peeking out from under the shut cash box (and on an iPhone on its side) and VoiceOver saying "Till overloaded.
Check the amount."; with the drawer fully open each note lands in its own slot and the ₱20 in its cup (Fly and Slot),
the compartment giving the nod; pieces fading over 0.22 s, ✕ emptying it the same calm way; coins lagging and notes
swaying on open and shut, none with Reduce Motion; a redraw drawing exactly the same; nothing sideways or outside the
drawer at ₱999,999; nothing saved. Screenshots empty, half, full and overloaded (open, and shut with the peek), light
and dark, at 375 and 402 px."""

from harness import BAD_TEXT

ON = "localStorage.setItem('suki:motion','1')"
REDUCE = "localStorage.setItem('suki:reduceMotion','on')"
SLOW = "localStorage.setItem('suki:motion','4')"
COUNTS = """(()=>[[...document.querySelectorAll('#tillTray .tslot')].map(s=>s.querySelectorAll('i:not(.going)').length),
  [...document.querySelectorAll('#tillTray .tcup')].map(c=>c.querySelectorAll('i:not(.going)').length)])()"""
ALL = "document.querySelectorAll('#tillTray i').length"
PEEK = "$('tillPeek').classList.contains('on')"
SAYS = "$('tillOver').textContent"
SETTLED = "!DR.raf && !DR.drag && !DR.fade"
NO_SIDEWAYS = "document.scrollingElement.scrollWidth<=innerWidth"
SHAPE = """(()=>[...document.querySelectorAll('#tillTray i')].map(i=>[i.className,i.style.left,i.style.top,i.style.height,i.style.marginLeft,i.style.transform].join('|')).join(';'))()"""


def settle(pg):
    pg.wait_for_function(SETTLED, timeout=5000)
    pg.wait_for_timeout(30)


def cash(pg, v):
    pg.fill('#till-cash', v)
    pg.evaluate("document.activeElement.blur()")
    pg.wait_for_timeout(40)


def till(pg, v='1000'):
    pg.evaluate("go('till')")
    pg.fill('#till-bill', '789.50')
    cash(pg, v)


def opened(pg):
    pg.click('#tillHdl')
    settle(pg)


def run(b, t):
    ok = t.ok

    # ── 1 · Labels on each front lip ────────────────────────────────────────────────────────────────
    pg = t.page(b, w=402, h=874)
    till(pg, '')
    labels = pg.evaluate("[...document.querySelectorAll('#tillTray .tslot > span, #tillTray .tcup > span')].map(s=>s.textContent)")
    ok(labels == ['1000', '500', '100', '50', '20', '10', '5', '1', '25¢'], f'every compartment is labelled on its front lip ({labels})')
    ok(pg.evaluate(ALL) == 0, 'nothing handed over: the drawer is empty')
    ok(pg.evaluate("[...document.querySelectorAll('#tillTray .tslot')].map(s=>getComputedStyle(s).getPropertyValue('--n').trim()!=='').every(Boolean)"),
       'each note slot carries its note’s colour')

    # ── 2 · A fullness gauge, not a count ─────────────────────────────────────────────────────────
    want = {'20': ([0, 0, 0, 0], [3, 3, 3, 3, 3]), '100': ([0, 0, 1, 4], [4, 4, 5, 5, 5]), '1000': ([0, 3, 8, 10], [4, 4, 5, 5, 5]),
            '5000': ([5, 7, 10, 10], [4, 4, 5, 5, 5]), '20000': ([10, 10, 10, 10], [4, 4, 5, 5, 5])}
    for v, (sl, cu) in want.items():
        cash(pg, v)
        got = pg.evaluate(COUNTS)
        ok(got == [list(sl), list(cu)], f'₱{v}: slots {sl}, cups {cu} (got {got})')
    ok(pg.evaluate(ALL) == 63, 'full at ₱20,000: ten sheets in each slot and every cup heaped (63 pieces)')
    last, rising = -1, True
    for v in ('1', '9', '40', '75', '300', '800', '1500', '3000', '7000', '12000', '18000', '20000', '35000', '49999.99'):
        cash(pg, v)
        n = pg.evaluate("document.querySelectorAll('#tillTray i:not(.going)').length")
        rising = rising and n >= last
        last = n
    ok(rising and last == 63, 'more cash never looks emptier, and it stays full up to ₱49,999.99')
    cash(pg, '5000')
    a = pg.evaluate(COUNTS)
    pg.fill('#till-bill', '4999'); pg.wait_for_timeout(40)
    ok(pg.evaluate(COUNTS) == a, 'only the cash handed over decides it: changing the bill changes nothing')
    sheet = pg.evaluate("document.querySelector('#tillTray .tslot i').getAttribute('style')")
    ok('rotateX(-26deg)' in sheet, f'notes stand on edge against the floor’s tilt ({sheet})')
    ok(pg.evaluate("[...document.querySelectorAll('#tillTray .tcup')][0].querySelector('i').classList.contains('r')")
       and not pg.evaluate("[...document.querySelectorAll('#tillTray .tcup')][1].querySelector('i').classList.contains('r')"),
       'the ₱20 cup’s coins have the bronze ring, the others don’t')
    ok(pg.evaluate("getComputedStyle(document.querySelector('#tillTray .tslot')).transformStyle") == 'preserve-3d', 'the slots keep 3D, so notes stand up')

    # ── 3 · A redraw draws exactly what was there ─────────────────────────────────────────────────
    cash(pg, '60000')
    s1 = pg.evaluate(SHAPE)
    pg.evaluate("render()"); pg.wait_for_timeout(40)
    ok(pg.evaluate(SHAPE) == s1, 'a redraw draws the same pieces in the same places')

    # ── 4 · Overloaded from ₱50,000 ───────────────────────────────────────────────────────────────
    cash(pg, '49999.99')
    ok(not pg.evaluate(PEEK) and pg.evaluate(SAYS) == '', 'just under ₱50,000: no peek, nothing said')
    cash(pg, '50000')
    ok(pg.evaluate(COUNTS) == [[12] * 4, [8] * 5], 'at ₱50,000: twelve sheets in each slot and eight coins in each cup')
    tips = pg.evaluate("[...document.querySelector('#tillTray .tslot').querySelectorAll('i')].map(i=>i.style.transform)")
    ok(all('rotateZ' in x for x in tips[8:]) and not any('rotateZ' in x for x in tips[:8]), 'the last four sheets tip out of the slot')
    tops = pg.evaluate("[...document.querySelector('#tillTray .tcup').querySelectorAll('i')].map(i=>parseFloat(i.style.top))")
    ok(min(tops[5:]) > max(tops[:5]), f'three coins spill out past the heap ({tops})')
    ok(pg.evaluate(PEEK), 'shut and overloaded: notes peek out from under the cash box')
    ok(pg.evaluate(SAYS) == 'Till overloaded. Check the amount.' and pg.get_attribute('#tillOver', 'aria-live') == 'polite',
       'VoiceOver says "Till overloaded. Check the amount."')
    ok(pg.evaluate("$('tillOver').getBoundingClientRect().width") <= 1, 'the VoiceOver line isn’t seen')
    ok(pg.evaluate("getComputedStyle($('tillPeek')).pointerEvents") == 'none' and pg.get_attribute('#tillPeek', 'aria-hidden') == 'true',
       'the peek never takes a touch, and VoiceOver skips it')
    pk = pg.evaluate("(()=>{const p=$('tillPeek').getBoundingClientRect(),c=document.querySelector('#app .cashbox').getBoundingClientRect();return [p.top,c.bottom,p.bottom]})()")
    ok(pk[0] < pk[1] < pk[2], f'the peek sits under the cash box’s bottom edge ({pk})')
    opened(pg)
    ok(not pg.evaluate(PEEK), 'open, the peek goes: the notes are in the drawer')
    pg.click('#tillHdl'); settle(pg)
    ok(pg.evaluate(PEEK), 'shut again, it’s back')
    pg.evaluate("render()"); pg.wait_for_timeout(40)
    ok(pg.evaluate(PEEK) and pg.evaluate(SAYS).startswith('Till overloaded'), 'a redraw keeps the peek and the words')
    cash(pg, '20000')
    ok(not pg.evaluate(PEEK) and pg.evaluate(SAYS) == '', 'back under ₱50,000: the peek and the words go')

    # ── 5 · Nothing escapes at ₱999,999 ───────────────────────────────────────────────────────────
    for w in (375, 402):
        p2 = t.page(b, w=w, h=812 if w == 375 else 874)
        till(p2, '999999')
        opened(p2)
        out = p2.evaluate("""(()=>{const d=$('tillDrawer').getBoundingClientRect();return [...document.querySelectorAll('#tillTray i')]
          .filter(i=>{const r=i.getBoundingClientRect();return r.left<d.left-0.5||r.right>d.right+0.5}).length})()""")
        ok(out == 0 and p2.evaluate(NO_SIDEWAYS), f'{w} px, ₱999,999: every piece stays inside the drawer, nothing sideways')
        ok(p2.evaluate(BAD_TEXT) == '', f'{w} px: nothing broken on screen')
        p2.close()
    pg.close()

    # ── 6 · Calm changes: fades, and ✕ empties it ────────────────────────────────────────────────
    pg = t.page(b, w=402, h=874, init=ON)
    till(pg, '')
    pg.fill('#till-cash', '1000')
    d = pg.evaluate("[...document.querySelectorAll('#tillTray i')].map(i=>i.getAnimations().map(a=>a.effect.getTiming().duration)).flat()")
    ok(len(d) == 44 and all(abs(x - 220) < 1 for x in d), f'new pieces fade in over 0.22 s ({len(d)} pieces)')
    pg.wait_for_timeout(300)
    pg.fill('#till-cash', '100')
    g = pg.evaluate("document.querySelectorAll('#tillTray i.going').length")
    ok(g > 0, f'pieces no longer needed fade out ({g})')
    pg.wait_for_timeout(350)
    ok(pg.evaluate("document.querySelectorAll('#tillTray i.going').length") == 0, 'and are gone after the fade')
    pg.fill('#till-cash', '5000'); pg.evaluate("document.activeElement.blur()"); pg.wait_for_timeout(300)
    n0 = pg.evaluate(ALL)
    pg.click('#cashClear')
    mid = pg.evaluate("(()=>{const i=document.querySelector('#tillTray i.going');return i?+getComputedStyle(i).opacity:-1})()")
    ok(pg.evaluate("document.querySelectorAll('#tillTray i.going').length") == n0 and pg.evaluate("U.till.cash") == '',
       f'✕ empties the drawer: all {n0} pieces fade out together')
    pg.wait_for_timeout(350)
    ok(pg.evaluate(ALL) == 0, '✕: after the fade the drawer is empty')
    ok(0 <= mid <= 1, f'✕ fades rather than snapping ({mid})')

    # ── 7 · Notes land in the right compartment ───────────────────────────────────────────────────
    till(pg, '')
    opened(pg)
    FLY = """v=>{const b=document.querySelector('#app .denoms .dn[data-v="'+v+'"]');b.click();const f=[...flights].pop();
      const k=f.a.effect.getKeyframes().pop().transform.match(/translate\\(([-\\d.]+)px,\\s*([-\\d.]+)px/);
      const r=f.comp?f.comp.getBoundingClientRect():null,w=v===20?20:40;
      return {comp:f.comp?(f.comp.dataset.n||f.comp.dataset.c):null,inside:!!r&&+k[1]+w/2>r.left&&+k[1]+w/2<r.right&&+k[2]>r.top-12&&+k[2]<r.bottom}}"""
    for v, want_c in ((1000, '1000'), (500, '500'), (100, '100'), (50, '50'), (20, '20')):
        r = pg.evaluate(FLY, v)
        ok(r['comp'] == want_c and r['inside'], f'Fly, drawer open: the ₱{v} heads for its own compartment ({r})')
        pg.wait_for_function("!flights.size", timeout=3000)
    ok(pg.evaluate("amount(U.till.cash)") == 1670, f'each landed note still adds once ({pg.evaluate("U.till.cash")})')
    ok(pg.evaluate("DR.open && DR.h===106"), 'the drawer stays open while notes land in it')
    NODS = """window.__nods=[];(()=>{const A=Element.prototype.animate;Element.prototype.animate=function(f,o){
      if(this.classList&&(this.classList.contains('tslot')||this.classList.contains('tcup')))window.__nods.push(this.dataset.n||this.dataset.c);return A.call(this,f,o)}})()"""
    pg.evaluate(NODS)
    pg.evaluate("document.querySelector('#app .denoms .dn[data-v=\"500\"]').click()")
    pg.wait_for_function("!flights.size", timeout=3000)
    ok(pg.evaluate("window.__nods") == ['500'], f'the compartment it lands in gives the nod ({pg.evaluate("window.__nods")})')
    pg.evaluate("setNoteAnim('slot')")
    r = pg.evaluate(FLY, 100)
    ok(r['comp'] == '100' and r['inside'] and not pg.evaluate("$('tillSlot').classList.contains('show')"),
       f'Slot, drawer open: it goes into its compartment, not the slot line ({r})')
    pg.wait_for_function("!flights.size", timeout=3000)
    pg.evaluate("setNoteAnim('fly')")
    pg.click('#tillHdl'); settle(pg)
    pg.evaluate("document.querySelector('#app .denoms .dn[data-v=\"100\"]').click()")
    ok(pg.evaluate("[...flights].pop().comp") is None, 'drawer shut: notes go into the cash box as before')
    pg.wait_for_function("!flights.size", timeout=3000)

    # ── 8 · The contents feel the drawer move ─────────────────────────────────────────────────────
    JIG = """window.__jig=[];(()=>{const A=Element.prototype.animate;Element.prototype.animate=function(f,o){
      if(this.tagName==='I'&&this.closest&&this.closest('#tillTray')&&f.length===2&&/translateY|rotateZ/.test(f[0].transform||''))window.__jig.push(f[0].transform);return A.call(this,f,o)}})()"""
    cash(pg, '5000')
    pg.wait_for_timeout(300)
    pg.evaluate(JIG)
    opened(pg)
    j = pg.evaluate("window.__jig")
    coins = [x for x in j if 'translateY(-1.6px)' in x]
    notes = [x for x in j if 'rotateZ(1.6deg)' in x or 'rotateZ(-1.6deg)' in x]
    ok(len(coins) == 23 and len(notes) == 32, f'opening: every coin lags and settles, every note sways 1.6° ({len(coins)} coins, {len(notes)} notes)')
    ok(all(x.startswith('rotateX(-26deg)') for x in notes), 'the sway sits on top of the notes’ upright turn')
    pg.evaluate("window.__jig=[]")
    pg.click('#tillHdl'); settle(pg)
    ok(any('translateY(1.6px)' in x for x in pg.evaluate("window.__jig")), 'shutting: the coins lag the other way')
    pg.close()
    pg = t.page(b, w=402, h=874, init=ON + ';' + REDUCE)
    till(pg, '5000')
    pg.evaluate(JIG)
    opened(pg)
    ok(pg.evaluate("window.__jig") == [] and pg.evaluate("DR.h") == 106, 'Reduce Motion: no jiggle')
    pg.fill('#till-cash', '100')
    ok(pg.evaluate("document.querySelectorAll('#tillTray i.going').length") > 0, 'Reduce Motion: pieces still fade (a fade, not movement)')
    pg.close()

    # ── 9 · On its side, and nothing saved ────────────────────────────────────────────────────────
    pg = t.page(b, w=852, h=393, init=ON)
    till(pg, '60000')
    ok(pg.evaluate(PEEK) and pg.evaluate("getComputedStyle($('tillDrawer')).display") == 'none',
       'iPhone on its side: no drawer, but the overload peek still shows')
    ok(pg.evaluate(NO_SIDEWAYS), 'on its side: nothing sideways')
    t.shot(pg, 'overloaded-land')
    pg.close()
    pg = t.page(b, w=402, h=874)
    keys0 = pg.evaluate("Object.keys(localStorage).sort()")
    till(pg, '60000')
    opened(pg)
    pg.evaluate("render()")
    ok(pg.evaluate("Object.keys(localStorage).sort()") == keys0, 'nothing new is saved: the drawer only shows the cash')
    pg.close()

    # ── 10 · Screenshots: empty, half, full and overloaded, light and dark ───────────────────────
    for w in (375, 402):
        for sc in ('light', 'dark'):
            pg = t.page(b, w=w, h=874 if w == 402 else 812, sc=sc)
            for name, v in (('empty', ''), ('half', '2000'), ('full', '20000'), ('over', '60000')):
                till(pg, v)
                opened(pg)
                ok(pg.evaluate(NO_SIDEWAYS), f'{w} px {sc}, {name}: open, nothing sideways')
                t.shot(pg, f'{name}-{w}-{sc}', clip={'x': 0, 'y': 0, 'width': w, 'height': 560})
                pg.click('#tillHdl'); settle(pg)
            t.shot(pg, f'over-shut-{w}-{sc}', clip={'x': 0, 'y': 0, 'width': w, 'height': 560})
            pg.close()
