"""Quick Till: bigger buttons and the change as cash (Q13). The six 44 pt buttons on one row at 375 and 402 px (Exact,
the ₱20 coin and four notes, with VoiceOver labels), the ✕ in the cash box, the breakdown (20,000 random amounts add
up exactly, no ₱200 and no 50¢), fans, bundles (₱34,750 and ₱999,999 inside the card), the ₱20 and ₱5 coins, note
colours the same in dark mode, Log this bill staying put, and with motion on: new pieces settle in, removed ones
shrink away, the figure and a bundle's count never animate, rapid taps leave no stray pieces, Reduce Motion only
fades. Screenshots at 375 and 402 px, light and dark."""

ON = "localStorage.setItem('suki:motion','1')"
PIECES = "[...document.querySelectorAll('#cashRow [data-k]')].map(e=>e.dataset.k)"
INSIDE = """(()=>{const c=document.querySelector('#app .card.form').getBoundingClientRect();
  return [...document.querySelectorAll('#cashRow .stk, #cashRow .nt, #cashRow .cn')].every(e=>{const r=e.getBoundingClientRect();
  return r.left>=c.left-0.5&&r.right<=c.right+0.5&&r.top>=c.top-0.5&&r.bottom<=c.bottom+0.5})})()"""
NO_SIDEWAYS = "document.scrollingElement.scrollWidth<=innerWidth"
# every piece's running animations, as {k: [[transform, opacity] per keyframe]}
ANIMS = """(sel)=>[...document.querySelectorAll(sel)].map(e=>e.getAnimations().filter(a=>a.playState==='running').map(a=>a.effect.getKeyframes().map(k=>[k.transform||'',k.opacity===undefined?'':String(k.opacity)])))"""


def till(pg, bill, paid):
    pg.evaluate(f"U.till={{bill:'{bill}',cash:'{paid}'}};$('till-bill').value='{bill}';$('till-cash').value='{paid}';updateTill()")


def run(b, t):
    ok = t.ok

    # ── 1 · The buttons, at iPhone SE width ──────────────────────────────────────────────────────────────
    for w, h in [(375, 667), (402, 874)]:
        pg = t.page(b, w=w, h=h)
        pg.evaluate("go('till')")
        keys = pg.evaluate("""[...document.querySelectorAll('#app .denoms .dn')].map(e=>{const r=e.getBoundingClientRect();
          return {t:e.textContent,l:e.getAttribute('aria-label'),a:e.dataset.a,v:e.dataset.v||'',top:Math.round(r.top),h:r.height,w:r.width,
          fits:e.scrollWidth<=e.clientWidth,ta:getComputedStyle(e).textAlign}})""")
        ok([k['t'] for k in keys] == ['Exact', '20', '50', '100', '500', '1000'], f'{w} px: Exact, 20, 50, 100, 500 and 1000, labelled like the notes')
        ok(len({k['top'] for k in keys}) == 1, f'{w} px: all six sit on one row')
        ok(all(k['ta'] == 'center' for k in keys), f'{w} px: each label is centred on its button')
        ok(all(k['h'] >= 44 for k in keys), f'{w} px: every button is 44 pt tall ({sorted({k["h"] for k in keys})})')
        ok(all(k['w'] >= 44 and k['fits'] for k in keys), f'{w} px: every button is at least 44 pt wide and its label fits ({min(k["w"] for k in keys):.0f} pt)')
        card = pg.evaluate("(()=>{const c=document.querySelector('#app .card.form').getBoundingClientRect(),d=document.querySelector('#app .denoms').getBoundingClientRect();return d.left>=c.left&&d.right<=c.right})()")
        ok(card and pg.evaluate(NO_SIDEWAYS), f'{w} px: the row stays inside the card, with no sideways scroll')
        if w == 375:
            ok([k['l'] for k in keys] == ['Cash is exactly the bill', 'Add a ₱20 coin', 'Add a ₱50 note', 'Add a ₱100 note', 'Add a ₱500 note', 'Add a ₱1,000 note'],
               'VoiceOver says what each button is (“Add a ₱1,000 note”, “Add a ₱20 coin”)')
            ok(pg.get_attribute('#app .denoms', 'aria-label') == 'Notes you hand over' and pg.locator('#app .denoms').count() == 1,
               'the row keeps its .denoms class, so the Till tip still points at it')
            ok(pg.locator('#app .denoms [data-v="200"]').count() == 0, 'no ₱200 button (the BSP stopped making them)')
            ring = pg.evaluate("getComputedStyle(document.querySelector('.dn.c20b')).boxShadow")
            ok('inset' in ring and '3px' in ring, 'the ₱20 button looks like the coin, with its bronze ring')
            ok('Tap each note or ₱20 coin you hand over: 20 + 20 makes ₱40.' in pg.inner_text('#app .foot'), 'the foot line explains the buttons')
            # the ✕ inside the cash box replaces Clear
            ok(pg.locator('#app .denoms .chip').count() == 0 and 'Clear' not in pg.inner_text('#app .denoms'), 'there’s no Clear chip any more')
            ok(pg.locator('#cashClear').is_hidden(), 'the ✕ is hidden while the cash box is empty')
            pg.fill('#till-bill', '37'); pg.click('[data-a=cashAdd][data-v="20"]'); pg.click('[data-a=cashAdd][data-v="20"]')
            ok(pg.input_value('#till-cash') == '40' and '₱3.00' in pg.inner_text('#tillFig'), '20 + 20 makes ₱40, and ₱3.00 change for a ₱37 bill')
            x = pg.evaluate("(()=>{const b=document.querySelector('#cashClear').getBoundingClientRect(),i=document.querySelector('#till-cash').getBoundingClientRect();return {w:b.width,h:b.height,inside:b.left>=i.left&&b.right<=i.right&&b.top>=i.top-1&&b.bottom<=i.bottom+1}})()")
            ok(pg.locator('#cashClear').is_visible() and x['inside'] and x['w'] >= 44 and x['h'] >= 44, 'with cash typed, the ✕ shows inside the box, 44 pt to tap')
            ok(pg.get_attribute('#cashClear', 'aria-label') == 'Clear cash', 'VoiceOver calls it “Clear cash”')
            pg.focus('#till-cash'); pg.click('#cashClear')
            ok(pg.input_value('#till-cash') == '' and pg.locator('#cashClear').is_hidden(), 'tapping it empties the cash and hides it again')
            ok(pg.evaluate("document.activeElement.id") == 'till-cash', 'and the keyboard stays where it was')
            ok(pg.locator('#cashRow [data-k]').count() == 0 and pg.get_attribute('#cashRow', 'aria-hidden') == 'true', 'with no change, there’s no cash to show')
        pg.context.close()

    pg = t.page(b, w=402, h=874)
    pg.evaluate("go('till')")

    # ── 2 · The breakdown ───────────────────────────────────────────────────────────────────────────────
    r = pg.evaluate("""(()=>{const N=[1000,500,100,50],C=[2000,1000,500,100,25,5,1];let bad=[],seed=7;
      const rnd=()=>(seed=(seed*1103515245+12345)%2147483648)/2147483648;
      for(let i=0;i<20000;i++){const c=1+Math.floor(rnd()*(i<10000?200000:100000000));const b=asCash(c);
        const total=b.notes.reduce((s,n)=>s+n*100,0)+b.coins.reduce((s,[k,m])=>s+k*m,0);
        const ok=total===c&&b.notes.every(n=>N.includes(n))&&b.coins.every(([k])=>C.includes(k))
          &&b.notes.every((n,j)=>j===0||b.notes[j-1]>=n)&&b.coins.every(([k],j)=>j===0||b.coins[j-1][0]>k);
        if(!ok&&bad.length<3)bad.push(c)}return bad})()""")
    ok(r == [], f'20,000 random amounts break down exactly, largest first, using only real notes and coins ({r})')
    g = pg.evaluate("(()=>{const f=c=>{const b=asCash(c);return [b.notes,b.coins]};return {a:f(21050),b:f(50),c:f(2000),d:f(5000)}})()")
    ok(g['a'] == [[100, 100], [[1000, 1], [25, 2]]], f'₱210.50 is two ₱100s, a ₱10 coin and two 25¢ ({g["a"]})')
    ok(g['b'] == [[], [[25, 2]]], 'there’s no 50¢ coin, so 50¢ is two 25¢')
    ok(g['c'] == [[], [[2000, 1]]] and g['d'] == [[50], []], '₱20 is a coin and ₱50 a note')

    # ── 3 · Drawn as cash ───────────────────────────────────────────────────────────────────────────────
    till(pg, '789.50', '1000')
    ok(pg.evaluate(PIECES) == ['n100.0', 'n100.1', 'c1000.0', 'c25.0', 'c25.1'], 'the change shows as notes first, then coins')
    ok(pg.get_attribute('#cashRow', 'role') == 'img' and pg.get_attribute('#cashRow', 'aria-label') == 'As cash: ₱100 note × 2, ₱10 coin, 25¢ coin × 2',
       'VoiceOver reads the cash as one line (“As cash: ₱100 note × 2, ₱10 coin, 25¢ coin × 2”)')
    edge = pg.evaluate("(()=>{const b=document.querySelector('#cashRow .nt b'),s=getComputedStyle(b);return {wm:s.writingMode,t:b.textContent}})()")
    ok(edge['wm'] == 'vertical-rl' and edge['t'] == '100', 'each note shows its number up its left edge')
    ok(pg.evaluate("document.querySelectorAll('#cashRow .pile').length") == 2 and pg.evaluate("document.querySelector('#cashRow .pile[data-den=\"25\"]').children.length") == 2,
       'matching coins sit together in a small pile')
    over = pg.evaluate("(()=>{const c=[...document.querySelectorAll('#cashRow .pile[data-den=\"25\"] .cn')].map(e=>e.getBoundingClientRect());return c[0].right-c[1].left})()")
    ok(abs(over - 8) < 1, f'overlapping by 8 px, so every label stays readable ({over:.1f})')
    till(pg, '0.50', '50')
    ok(pg.locator('#cashRow .fan .nt').count() == 0 and pg.locator('#cashRow .cn.c20 i').count() == 2, 'the ₱20 coin is two-tone (a ring round a centre)')
    till(pg, '95', '100')
    ok('polygon' in pg.evaluate("getComputedStyle(document.querySelector('#cashRow .cn.c5')).clipPath"), 'the ₱5 coin has nine sides')
    till(pg, '1000', '5000')
    ok(pg.evaluate(PIECES) == ['n1000.0', 'n1000.1', 'n1000.2', 'n1000.3'], 'up to four of a note fan out, so the edges can be counted')
    till(pg, '1000', '6000')
    ok(pg.evaluate(PIECES) == ['s1000'] and pg.inner_text('#cashRow .stk em') == '×5', 'five or more become one bundle, with the count on the front')
    ok(pg.locator('#cashRow .stk > i.nt').count() == 2, 'two notes peek out behind the bundle')
    till(pg, '789.50', '500')
    ok(pg.locator('#cashRow [data-k]').count() == 0 and 'Still to pay' in pg.inner_text('#tillOut'), 'short cash shows what’s still to pay, and no cash')
    till(pg, '789.50', '789.50')
    ok(pg.locator('#cashRow [data-k]').count() == 0 and 'Exact payment' in pg.inner_text('#tillOut'), 'an exact payment shows no cash')

    # ── 4 · Big amounts stay inside the card, and Log this bill stays put ───────────────────────────────
    for w, h in [(375, 667), (402, 874)]:
        pg.set_viewport_size({'width': w, 'height': h})
        till(pg, '250', '35000')
        ok(pg.evaluate(PIECES) == ['s1000', 'n500.0', 'n100.0', 'n100.1', 'n50.0'] and pg.inner_text('#cashRow .stk em') == '×34',
           f'{w} px: ₱34,750 is a bundle of 34 ₱1,000s, then ₱500, ₱100 × 2 and ₱50')
        ok(pg.evaluate(INSIDE) and pg.evaluate(NO_SIDEWAYS), f'{w} px: ₱34,750 stays inside the card')
        till(pg, '1', '1000000')
        ok(pg.inner_text('#cashRow .stk em') == '×999' and pg.evaluate(INSIDE) and pg.evaluate(NO_SIDEWAYS), f'{w} px: ₱999,999 stays inside the card too')
    pg.set_viewport_size({'width': 402, 'height': 874})
    tops = []
    for bill, paid in [('', ''), ('789.50', '789.50'), ('789.50', '1000'), ('789.50', '500'), ('137', '500')]:
        till(pg, bill, paid)
        tops.append(round(pg.evaluate("document.getElementById('tillLog').getBoundingClientRect().top")))
    ok(len(set(tops)) == 1, f'Log this bill doesn’t jump as the change changes ({tops})')
    till(pg, '1', '1000')
    ok(round(pg.evaluate("document.getElementById('tillLog').getBoundingClientRect().top")) >= tops[0], 'it only moves down when the coins wrap onto a second line')

    # ── 5 · Colours: tokens, the same in light and dark ─────────────────────────────────────────────────
    till(pg, '1', '2000')
    light = pg.evaluate("['.dn.n1000','.dn.n50','.dn.c20b','#cashRow .nt.n1000'].map(s=>getComputedStyle(document.querySelector(s)).backgroundColor)")
    pg.context.close()
    pg = t.page(b, w=402, h=874, sc='dark')
    pg.evaluate("go('till')"); till(pg, '1', '2000')
    dark = pg.evaluate("['.dn.n1000','.dn.n50','.dn.c20b','#cashRow .nt.n1000'].map(s=>getComputedStyle(document.querySelector(s)).backgroundColor)")
    ok(light == dark and len(set(light)) == 3, f'notes and coins keep their colours in dark mode, like cards in Wallet ({dark})')
    pg.context.close()

    # ── 6 · Motion on ───────────────────────────────────────────────────────────────────────────────────
    pg = t.page(b, w=402, h=874, init=ON)
    pg.evaluate("go('till')")
    pg.fill('#till-bill', '789.50')
    pg.click('[data-a=cashAdd][data-v="1000"]')
    pg.wait_for_function("document.querySelectorAll('.nfly').length===0")  # the note lands first (Q18)
    pg.wait_for_timeout(30)
    a = pg.evaluate(ANIMS, '#cashRow [data-k]')
    ok(len(a) == 5 and all(x and x[0][0][0] == 'translateY(-10px)' and x[0][0][1] == '0' for x in a), 'new pieces settle in: a 10 px drop as they fade in')
    d = pg.evaluate("[...document.querySelectorAll('#cashRow [data-k]')].map(e=>e.getAnimations()[0]?.effect.getTiming().delay)")
    ok(d == [0, 45, 90, 135, 180], f'45 ms apart ({d})')
    ok(pg.evaluate("document.getElementById('tillFig').getAnimations().length") == 0, 'the figure itself never animates')
    pg.wait_for_function("!document.querySelector('#cashRow [data-k]').getAnimations().some(a=>a.playState==='running')")
    pg.evaluate("document.querySelector('#cashRow [data-k=\"n100.0\"]').dataset.mark='kept'")
    pg.fill('#till-bill', '889.50')  # ₱110.50: one ₱100 goes, the coins stay
    pg.wait_for_timeout(20)
    gh = pg.evaluate("[...document.querySelectorAll('#cashRow .cghost')].map(g=>g.getAnimations().map(a=>[a.effect.getTiming().duration,a.effect.getKeyframes().at(-1).transform]))")
    ok(len(gh) == 1 and gh[0] and gh[0][0] == [160, 'scale(0.6)'], f'a removed note shrinks away where it was, in 160 ms ({gh})')
    ok(pg.evaluate("document.querySelector('#cashRow [data-k=\"n100.0\"]').dataset.mark") == 'kept', 'pieces that stay are the same pieces, not redrawn')
    pg.wait_for_function("!document.querySelector('#cashRow .cghost')")
    ok(True, 'and its copy is gone after')
    # staying pieces glide when a note before them comes or goes
    pg.fill('#till-bill', '789.50')
    pg.wait_for_timeout(20)
    glide = pg.evaluate("document.querySelector('#cashRow [data-k=\"c1000.0\"]').getAnimations().filter(a=>a.playState==='running').map(a=>a.effect.getKeyframes()[0].transform)")
    ok(any(x.startswith('translate(') for x in glide), f'coins that stay glide to their new place ({glide})')
    # a bundle's count changes in place
    pg.fill('#till-bill', '1000'); pg.fill('#till-cash', '6000')
    pg.wait_for_function("!!document.querySelector('#cashRow .stk')&&!document.querySelector('#cashRow .stk').getAnimations().some(a=>a.playState==='running')")
    pg.evaluate("document.querySelector('#cashRow .stk').dataset.mark='b'")
    pg.click('[data-a=cashAdd][data-v="1000"]')
    pg.wait_for_function("document.querySelectorAll('.nfly').length===0")  # the note lands first (Q18)
    pg.wait_for_timeout(20)
    stk = pg.evaluate("(()=>{const s=document.querySelector('#cashRow .stk');return {m:s.dataset.mark,t:s.querySelector('em').textContent,n:s.getAnimations({subtree:true}).filter(a=>a.playState==='running').length}})()")
    ok(stk == {'m': 'b', 't': '×6', 'n': 0}, f'a bundle’s count changes in place, without moving ({stk})')
    # rapid taps: nothing left behind
    pg.fill('#till-bill', '137.25'); pg.fill('#till-cash', '')
    for v in ['20', '1000', '50', '100', '20', '500', '1000', '100', '20', '50', '1000', '20'] * 2:
        pg.click(f'[data-a=cashAdd][data-v="{v}"]', delay=0)
    pg.click('[data-a=cashExact]'); pg.click('[data-a=cashAdd][data-v="1000"]'); pg.click('[data-a=cashAdd][data-v="20"]')
    pg.wait_for_function("!document.querySelector('.nfly')&&!document.querySelector('#cashRow .cghost')&&![...document.querySelectorAll('#cashRow *')].some(e=>e.getAnimations().some(a=>a.playState==='running'))", timeout=8000)
    want = pg.evaluate("cashWant(tillView().cash).map(w=>w.k)")
    ok(len(want) > 0 and pg.evaluate(PIECES) == want, f'rapid taps leave exactly the pieces for the change, with no strays ({want})')
    ok(len(set(pg.evaluate(PIECES))) == len(want) and pg.evaluate("document.querySelectorAll('#cashRow .pile').length") == len({k.split('.')[0] for k in want if k.startswith('c')}),
       'no doubled pieces and no empty piles')
    ok(pg.evaluate(NO_SIDEWAYS), 'and no sideways scroll')
    # leaving the tab mid-animation leaves nothing behind
    pg.click('[data-a=cashAdd][data-v="500"]'); pg.evaluate("go('home')"); pg.evaluate("go('till')")
    ok(pg.locator('#cashRow .cghost').count() == 0 and pg.evaluate(PIECES) == pg.evaluate("cashWant(tillView().cash).map(w=>w.k)"), 'switching tabs mid-way redraws the cash cleanly')
    pg.context.close()

    # ── 7 · Reduce Motion: fades only ───────────────────────────────────────────────────────────────────
    pg = t.page(b, w=402, h=874, init=ON, ctx_args={'reduced_motion': 'reduce'})
    pg.evaluate("go('till')")
    pg.fill('#till-bill', '789.50'); pg.click('[data-a=cashAdd][data-v="1000"]')
    pg.wait_for_timeout(20)
    a = pg.evaluate(ANIMS, '#cashRow [data-k]')
    ok(a and all(x and all(k[0] in ('', 'none') for k in x[0]) and x[0][0][1] == '0' for x in a), 'with Reduce Motion, new pieces only fade in')
    pg.fill('#till-bill', '889.50'); pg.wait_for_timeout(20)
    gh = pg.evaluate("[...document.querySelectorAll('#cashRow .cghost')].map(g=>g.getAnimations().map(a=>a.effect.getKeyframes().map(k=>k.transform||'')))")
    ok(gh and all(all(tr in ('', 'none') for tr in x[0]) for x in gh), 'and a removed one only fades out')
    pg.fill('#till-bill', '789.50'); pg.wait_for_timeout(20)
    ok(not any(a.startswith('translate(') for a in pg.evaluate("document.querySelector('#cashRow [data-k=\"c1000.0\"]').getAnimations().map(a=>a.effect.getKeyframes()[0].transform||'')")),
       'and nothing glides')
    pg.context.close()

    # ── 8 · Screenshots ─────────────────────────────────────────────────────────────────────────────────
    for w, h in [(375, 667), (402, 874)]:
        for sc in ['light', 'dark']:
            pg = t.page(b, w=w, h=h, sc=sc)
            pg.evaluate("go('till')")
            for name, bill, paid in [('change', '789.50', '1000'), ('bundle', '250', '35000')]:
                till(pg, bill, paid)
                pg.evaluate("document.getElementById('cashRow').scrollIntoView({block:'center'})")
                ok(pg.evaluate("document.body.innerText.match(/\\bundefined\\b|\\bNaN\\b/)") is None, f'{w} px {sc}, {name}: nothing reads undefined or NaN')
                t.shot(pg, f'{w}-{sc}-{name}')
            pg.context.close()
