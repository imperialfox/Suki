"""Quick Till: the note press (Q18). With motion on: each button tips towards the finger while held and springs back;
a tapped note flies (or slots) into the cash box and the amount changes only when it lands, once per tap, also when
tapped fast; a redraw or a tab switch lands it at once and leaves nothing behind; typing, ✕ and Exact drop notes still
in the air; Slot's line is hidden at rest, shows for the slot and fades after. The setting in Settings › Accessibility
(Fly · Slot) switches, survives a reload and isn't in backups. Only the two boxes can be selected on the Till (2.24.1). Reduce Motion and motion off: no tilt, no flight, the
amount changes at once. The new materials on the notes and coins, the same in dark mode. Screenshots at 375 and 402 px,
light and dark."""

ON = "localStorage.setItem('suki:motion','1')"
SLOW = "localStorage.setItem('suki:motion','4')"
SLOT = "localStorage.setItem('suki:noteAnim','slot')"
FLYING = "document.querySelectorAll('.nfly').length"
CASH = "U.till.cash"
# the running animations' keyframe transforms on one element
KEYS = """(sel)=>{const e=document.querySelector(sel);return e?e.getAnimations().map(a=>a.effect.getKeyframes().map(k=>k.transform||'')):[]}"""
NO_SIDEWAYS = "document.scrollingElement.scrollWidth<=innerWidth"


def landed(pg, timeout=6000):
    pg.wait_for_function(FLYING + "===0", timeout=timeout)
    pg.wait_for_timeout(30)


def run(b, t):
    ok = t.ok

    # ── 1 · Fly, at full speed ──────────────────────────────────────────────────────────────────────────
    pg = t.page(b, w=402, h=874, init=ON)
    pg.evaluate("go('till')")
    pg.fill('#till-bill', '789.50')
    ok(pg.evaluate("getComputedStyle($('tillSlot')).opacity") == '0', 'the slot line is hidden at rest')
    gap = pg.evaluate("""(()=>{const s=$('tillSlot').getBoundingClientRect(),i=$('till-cash').getBoundingClientRect(),d=document.querySelector('#app .denoms').getBoundingClientRect();
      return s.top>=i.bottom&&s.bottom<=d.top&&Math.abs((s.left+s.right)/2-(i.left+i.right)/2)<1})()""")
    ok(gap, 'it sits centred in the gap under the cash box, above the buttons, so nothing moves for it')
    pg.click('[data-a=cashAdd][data-v="1000"]')
    ok(pg.evaluate(FLYING) == 1 and pg.evaluate(CASH) == '', 'a tapped ₱1,000 is in the air, and the amount hasn’t changed yet')
    k = pg.evaluate("[...document.querySelector('.nfly').getAnimations()[0].effect.getKeyframes()].map(k=>k.transform)")
    ok(len(k) == 13 and 'rotateY' not in ''.join(k), 'Fly: the note arcs in (13 steps), with no spin')
    ok(pg.evaluate("document.querySelector('.nfly').classList.contains('n1000')"), 'it’s the ₱1,000’s colour')
    mid = pg.evaluate("$('tillFig').textContent")
    ok(mid == '—', 'the change waits for the note')
    landed(pg)
    ok(pg.evaluate(CASH) == '1000' and pg.input_value('#till-cash') == '1000' and pg.inner_text('#tillFig') == '₱210.50',
       'it lands: the amount becomes 1000 and the change shows ₱210.50')
    ok(pg.locator('#cashRow [data-k]').count() > 0, 'and the change row settles in straight after')
    ok(pg.evaluate("getComputedStyle($('tillSlot')).opacity") == '0', 'Fly never shows the slot line')
    pg.click('[data-a=cashAdd][data-v="20"]')
    k = pg.evaluate("[...document.querySelector('.nfly').getAnimations()[0].effect.getKeyframes()].map(k=>k.transform)")
    ok(pg.evaluate("document.querySelector('.nfly').classList.contains('coinf')") and 'rotateY(720deg)' in k[-1],
       'the ₱20 flies as a coin, spinning twice like a tossed coin')
    landed(pg)
    ok(pg.evaluate(CASH) == '1020', '₱20 lands on top: 1020')

    # each tap adds once, also when tapped fast
    pg.click('#cashClear')
    for v in ['20'] * 5 + ['1000'] * 3 + ['50', '500']:
        pg.click(f'[data-a=cashAdd][data-v="{v}"]', delay=0)
    ok(pg.evaluate(FLYING) >= 2, f'tapped fast, several notes are in the air at once ({pg.evaluate(FLYING)})')
    landed(pg)
    ok(pg.evaluate(CASH) == '3650', f'ten fast taps add up exactly once each: ₱3,650 ({pg.evaluate(CASH)})')
    ok(pg.evaluate("document.querySelectorAll('body > .nfly').length") == 0, 'and no flying note is left on screen')

    # a redraw, or switching tabs, lands notes still in the air
    pg.click('#cashClear')
    pg.click('[data-a=cashAdd][data-v="500"]'); pg.click('[data-a=cashAdd][data-v="100"]')
    pg.evaluate("render()")
    ok(pg.evaluate(FLYING) == 0 and pg.evaluate(CASH) == '600' and pg.input_value('#till-cash') == '600',
       'a redraw mid-flight lands both notes at once: 600, with nothing left behind')
    pg.click('[data-a=cashAdd][data-v="1000"]')
    pg.evaluate("go('home')")
    ok(pg.evaluate(FLYING) == 0, 'switching tabs mid-flight leaves nothing on screen')
    pg.wait_for_timeout(700)
    pg.evaluate("go('till')")
    ok(pg.input_value('#till-cash') == '1600', 'and the note still counted: 1600 back on Till')

    # what you did last wins
    pg.click('[data-a=cashAdd][data-v="1000"]'); pg.click('#cashClear')
    pg.wait_for_timeout(700)
    ok(pg.evaluate(FLYING) == 0 and pg.evaluate(CASH) == '', '✕ mid-flight drops the note: the box stays empty')
    pg.click('[data-a=cashAdd][data-v="1000"]'); pg.fill('#till-cash', '50')
    pg.wait_for_timeout(700)
    ok(pg.evaluate(FLYING) == 0 and pg.input_value('#till-cash') == '50', 'typing mid-flight drops it too: what you typed stays')
    pg.click('[data-a=cashAdd][data-v="1000"]'); pg.click('[data-a=cashExact]')
    pg.wait_for_timeout(700)
    ok(pg.evaluate(FLYING) == 0 and pg.input_value('#till-cash') == '789.50', 'and so does Exact')
    # the keyboard: Enter on a button flies the note too
    pg.fill('#till-bill', '137'); pg.click('#cashClear')
    pg.focus('[data-a=cashAdd][data-v="100"]'); pg.keyboard.press('Enter')
    landed(pg)
    ok(pg.evaluate(CASH) == '100', 'Enter on a focused button sends its note once')
    ok(not t.errors, 'no JavaScript errors so far')
    pg.context.close()

    # ── 2 · Finger tilt ─────────────────────────────────────────────────────────────────────────────────
    pg = t.page(b, w=402, h=874, init=ON)
    pg.evaluate("go('till')")
    bb = pg.locator('[data-a=cashAdd][data-v="500"]').bounding_box()
    pg.mouse.move(bb['x'] + bb['width'] * 0.9, bb['y'] + bb['height'] * 0.1); pg.mouse.down()
    pg.wait_for_timeout(250)
    tr = pg.evaluate("getComputedStyle(document.querySelector('[data-v=\"500\"]')).transform")
    k = pg.evaluate(KEYS, '[data-v="500"]')
    held = k and k[0][-1]
    ok(tr not in ('none', '') and held and 'rotateX(' in held and 'rotateY(' in held and 'scale(0.94)' in held,
       f'held, the ₱500 tips and dips to .94 ({held})')
    rx = float(held.split('rotateX(')[1].split('deg')[0]); ry = float(held.split('rotateY(')[1].split('deg')[0])
    ok(rx > 10 and ry > 10, f'towards the thumb: pressed at its top right, the top tips back and the right side in ({rx}°, {ry}°)')
    pg.wait_for_timeout(300)
    tr2 = pg.evaluate("getComputedStyle(document.querySelector('[data-v=\"500\"]')).transform")
    ok(tr2 == tr, f'it stays tipped while held ({tr} then {tr2})')
    pg.mouse.up()
    pg.wait_for_timeout(60)
    k = pg.evaluate(KEYS, '[data-v="500"]')
    ok(any(x[-1] in ('none', '') for x in k), 'let go, it springs back')
    pg.wait_for_timeout(800)
    ok(pg.evaluate("document.querySelector('[data-v=\"500\"]').getAnimations().filter(a=>a.effect.getKeyframes().some(k=>(k.transform||'').includes('rotateX'))).length") == 0
       and pg.evaluate("getComputedStyle(document.querySelector('[data-v=\"500\"]')).transform") in ('none', 'matrix(1, 0, 0, 1, 0, 0)'),
       'and ends flat')
    bb = pg.locator('[data-a=cashExact]').bounding_box()
    pg.mouse.move(bb['x'] + bb['width'] * 0.1, bb['y'] + bb['height'] * 0.9); pg.mouse.down(); pg.wait_for_timeout(150)
    k = pg.evaluate(KEYS, '[data-a=cashExact]')
    ok(k and 'rotateX(-' in k[0][-1] and 'rotateY(-' in k[0][-1], 'Exact tips too: pressed at its bottom left, towards that corner')
    pg.mouse.move(bb['x'] + bb['width'] * 0.5, bb['y'] + 200); pg.wait_for_timeout(60)
    ok(any(x[-1] in ('none', '') for x in pg.evaluate(KEYS, '[data-a=cashExact]')), 'sliding off a held button springs it back')
    pg.mouse.up()
    pg.context.close()

    # ── 3 · Slot ────────────────────────────────────────────────────────────────────────────────────────
    pg = t.page(b, w=402, h=874, init=ON + ';' + SLOT)
    pg.evaluate("go('till')")
    pg.fill('#till-bill', '789.50')
    ok(pg.evaluate("$('tillSlot').classList.contains('show')") is False, 'Slot: the line is hidden at rest')
    pg.click('[data-a=cashAdd][data-v="1000"]')
    ok(pg.evaluate("$('tillSlot').classList.contains('show')") and pg.evaluate(CASH) == '', 'tapped, the line fades in for the note, and the amount waits')
    k = pg.evaluate("[...document.querySelector('.nfly').getAnimations()[0].effect.getKeyframes()].map(k=>k.transform)")
    ok(len(k) == 3 and 'scaleY(0.04)' in k[-1], 'the note slides up and into the slot')
    sl = pg.evaluate("(()=>{const s=$('tillSlot').getBoundingClientRect();return [s.left+s.width/2,s.top+s.height/2]})()")
    end = pg.evaluate("(()=>{const m=new DOMMatrix(document.querySelector('.nfly').getAnimations()[0].effect.getKeyframes().slice(-1)[0].transform);return [m.e+20,m.f]})()")
    ok(abs(end[0] - sl[0]) < 1.5 and abs(end[1] - sl[1]) < 1.5, f'it ends on the slot line ({end} vs {sl})')
    landed(pg)
    ok(pg.evaluate(CASH) == '1000' and pg.inner_text('#tillFig') == '₱210.50', 'it lands: 1000, ₱210.50 change')
    ok(pg.evaluate("$('tillSlot').classList.contains('show')"), 'the line stays a moment after')
    pg.wait_for_function("!$('tillSlot').classList.contains('show')", timeout=3000)
    ok(True, 'then fades out about a second later')
    for v in ['100', '100', '50', '20']:
        pg.click(f'[data-a=cashAdd][data-v="{v}"]', delay=0)
    landed(pg)
    ok(pg.evaluate(CASH) == '1270', f'fast taps in Slot add once each: 1270 ({pg.evaluate(CASH)})')
    pg.click('[data-a=cashAdd][data-v="500"]'); pg.evaluate("render()")
    ok(pg.evaluate(FLYING) == 0 and pg.evaluate(CASH) == '1770', 'a redraw mid-slot lands it at once')
    ok(pg.evaluate("$('tillSlot').classList.contains('show')") is False, 'and the redrawn line is hidden again')
    pg.click('[data-a=cashAdd][data-v="500"]'); pg.click('#cashClear')
    ok(pg.evaluate("$('tillSlot').classList.contains('show')") is False, '✕ mid-slot hides the line with the note')
    pg.context.close()

    # ── 4 · The setting ─────────────────────────────────────────────────────────────────────────────────
    pg = t.page(b, w=402, h=874)
    pg.evaluate("go('settings')"); pg.click('[data-a=openAccess]')
    pg.wait_for_selector('#noteSeg')
    ok('note animation' in pg.inner_text('.sheet').lower(), 'Settings › Accessibility has “Note animation”')
    seg = pg.evaluate("[...document.querySelectorAll('#noteSeg button')].map(b=>[b.textContent,b.getAttribute('aria-pressed')])")
    ok(seg == [['Fly', 'true'], ['Slot', 'false']], f'Fly · Slot, with Fly as the starting setting ({seg})')
    ok(pg.get_attribute('#noteSeg', 'aria-label') == 'Note animation', 'VoiceOver reads the group as “Note animation”')
    pg.click('#noteSeg [data-v=slot]')
    ok(pg.evaluate("localStorage.getItem('suki:noteAnim')") == 'slot' and pg.evaluate("noteAnim()") == 'slot', 'choosing Slot keeps it on this device')
    ok(pg.get_attribute('#noteSeg [data-v=slot]', 'aria-pressed') == 'true' and pg.evaluate("$('noteSeg').style.getPropertyValue('--pk-i')") == '1',
       'the knob moves to Slot in place')
    ok(pg.evaluate("$('reduceSeg').style.getPropertyValue('--pk-i')") in ('0', ''), 'Reduce motion is left alone')
    pg.reload(); pg.wait_for_function("typeof U!=='undefined'&&!document.getElementById('splash')")
    pg.evaluate("go('settings')"); pg.click('[data-a=openAccess]'); pg.wait_for_selector('#noteSeg')
    ok(pg.get_attribute('#noteSeg [data-v=slot]', 'aria-pressed') == 'true', 'Slot survives a reload')
    bk = pg.evaluate("backupJSON(new Date())")
    ok('noteAnim' not in bk and '"slot"' not in bk, 'it isn’t in backups')
    ok('aren’t saved in backups' in pg.inner_text('.sheet'), 'the page says these settings stay on this device')
    pg.click('#noteSeg [data-v=fly]')
    ok(pg.evaluate("localStorage.getItem('suki:noteAnim')") is None and pg.evaluate("noteAnim()") == 'fly', 'back to Fly, the key is removed')
    pg.evaluate("localStorage.setItem('suki:noteAnim','sideways')")
    ok(pg.evaluate("noteAnim()") == 'fly', 'anything else saved there counts as Fly')
    pg.context.close()

    # ── 5 · Reduce Motion, and motion off ───────────────────────────────────────────────────────────────
    for label, kw in [('Reduce Motion', dict(init=ON, ctx_args={'reduced_motion': 'reduce'})), ('Reduce motion in Suki’s settings', dict(init=ON + ";localStorage.setItem('suki:reduceMotion','on')")),
                      ('motion off', {})]:
        for mode in ['fly', 'slot']:
            kw2 = dict(kw)
            if mode == 'slot': kw2['init'] = (kw2.get('init') or '') + ';' + SLOT
            pg = t.page(b, w=402, h=874, **kw2)
            pg.evaluate("go('till')")
            pg.fill('#till-bill', '789.50')
            bb = pg.locator('[data-a=cashAdd][data-v="1000"]').bounding_box()
            pg.mouse.move(bb['x'] + bb['width'] / 2, bb['y'] + 10); pg.mouse.down(); pg.wait_for_timeout(120)
            k = pg.evaluate(KEYS, '[data-v="1000"]')
            tilt = any('rotate' in x for a in k for x in a)
            pg.mouse.up()
            ok(not tilt, f'{label}, {mode}: no tilt')
            ok(pg.evaluate(FLYING) == 0 and pg.evaluate(CASH) == '1000' and pg.inner_text('#tillFig') == '₱210.50', f'{label}, {mode}: no flight, the amount changes at once')
            ok(pg.evaluate("$('tillSlot').classList.contains('show')") is False, f'{label}, {mode}: the slot line stays hidden')
            pg.context.close()

    # ── 6 · The materials ───────────────────────────────────────────────────────────────────────────────
    looks = {}
    for sc in ['light', 'dark']:
        pg = t.page(b, w=402, h=874, sc=sc)
        pg.evaluate("go('till')")
        pg.evaluate("U.till={bill:'1',cash:'1190.25'};$('till-bill').value='1';$('till-cash').value='1190.25';updateTill()")
        looks[sc] = pg.evaluate("""(()=>{const g=s=>{const e=document.querySelector(s),c=getComputedStyle(e);return [c.backgroundImage,c.backgroundColor,c.boxShadow]};
          const r=getComputedStyle(document.documentElement);
          return {note:g('#cashRow .nt.n100'),coin:g('#cashRow .cn:not(.c20)'),c20:g('#cashRow .cn.c20'),c20i:g('#cashRow .cn.c20 i'),
            tok:['--coin-hi','--coin-lo','--coin-edge','--ring-edge'].map(k=>r.getPropertyValue(k).trim())}})()""")
        pg.context.close()
    L = looks['light']
    ok('linear-gradient' in L['note'][0], 'notes in the change row are a block of paper (a lit gradient)')
    ok('radial-gradient' in L['coin'][0] and 'radial-gradient' in L['c20'][0] and 'radial-gradient' in L['c20i'][0], 'coins, and both parts of the ₱20, have a hint of metal')
    ok(L['note'][1] == 'rgb(201, 178, 220)', f'the ₱100 keeps its colour underneath ({L["note"][1]})')
    ok(L['coin'][2].count('rgb') >= 3, 'coins have a thin edge, so a pile has thickness')
    ok(all(L['tok']), f'the material tokens are set ({L["tok"]})')
    same = lambda x: {k: (v if k == 'tok' else v[:2]) for k, v in x.items()}  # shadows keep the card's colour as a gap ring
    ok(same(looks['light']) == same(looks['dark']), 'notes, coins and their tokens look the same in dark mode, like cards in Wallet')

    pg = t.page(b, w=402, h=874, init=SLOW)
    pg.evaluate("go('till')"); pg.fill('#till-bill', '789.50')
    pg.click('[data-a=cashAdd][data-v="1000"]'); pg.wait_for_timeout(300)
    f = pg.evaluate("(()=>{const c=getComputedStyle(document.querySelector('.nfly'));return [c.backgroundImage,c.pointerEvents,c.position]})()")
    ok('linear-gradient' in f[0] and f[1] == 'none' and f[2] == 'fixed', 'a note in flight is made of the same paper, and never takes a tap')
    pg.click('[data-a=cashAdd][data-v="20"]'); pg.wait_for_timeout(300)
    ok('radial-gradient' in pg.evaluate("getComputedStyle(document.querySelector('.nfly.coinf')).backgroundImage"), 'a ₱20 in flight is metal too')
    t.shot(pg, '402-light-flying')
    pg.context.close()

    # ── 7 · Only the two boxes can be selected (Q18 fix, 2.24.1) ───────────────────────────────────────
    pg = t.page(b, w=402, h=874, init=ON)
    pg.evaluate("go('till')")
    pg.evaluate("U.till={bill:'789.50',cash:'1000'};$('till-bill').value='789.50';$('till-cash').value='1000';updateTill()")
    for name, sel in [('a note button', '[data-a=cashAdd][data-v="500"]'), ('Exact', '[data-a=cashExact]'), ('a label', '#app .fld label'),
                      ('the change figure', '#tillFig'), ('the cash row', '#cashRow'), ('the title', '#app h1')]:
        pg.evaluate("U.till={bill:'789.50',cash:'1000'};$('till-bill').value='789.50';$('till-cash').value='1000';updateTill();getSelection().removeAllRanges()")
        pg.locator(sel).first.scroll_into_view_if_needed()
        pg.locator(sel).first.click(click_count=3)
        landed(pg)
        us = pg.evaluate(f"(s=>s.userSelect||s.webkitUserSelect)(getComputedStyle(document.querySelector('{sel}')))")
        ok(pg.evaluate("getSelection().toString()") == '' and us == 'none', f'holding or triple-tapping {name} selects nothing ({us})')
    ok(pg.evaluate("(s=>s.userSelect||s.webkitUserSelect)(getComputedStyle($('tillLog')))") == 'none', 'Log this bill can’t be selected either')
    pg.evaluate("U.till={bill:'789.50',cash:'1000'};$('till-bill').value='789.50';$('till-cash').value='1000';updateTill()")
    for box in ['#till-bill', '#till-cash']:
        pg.click(box, click_count=3)
        r = pg.evaluate(f"(()=>{{const e=document.querySelector('{box}');return [(s=>s.userSelect||s.webkitUserSelect)(getComputedStyle(e)),e.selectionEnd-e.selectionStart,e.value.length]}})()")
        ok(r[0] in ('text', 'auto') and r[1] == r[2] > 0, f'{box[1:]} still selects its text ({r})')
    pg.fill('#till-cash', '500')
    ok(pg.inner_text('#tillFig') == '₱289.50', 'and still takes typing')
    pg.evaluate("go('convert')")
    ok(pg.evaluate("(s=>s.userSelect||s.webkitUserSelect)(getComputedStyle(document.getElementById('app')))") != 'none', 'other pages are left alone')
    import os
    css = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'css', 'app.css'), encoding='utf-8').read()
    rule = css.split('#app.tab-till {', 1)[1].split('}', 1)[0] if '#app.tab-till {' in css else ''
    ok('-webkit-touch-callout: none' in rule, 'and the iPhone’s long-press menu is off on the Till')
    pg.context.close()

    # ── 8 · Screenshots ─────────────────────────────────────────────────────────────────────────────────
    for w, h in [(375, 667), (402, 874)]:
        for sc in ['light', 'dark']:
            pg = t.page(b, w=w, h=h, sc=sc)
            pg.evaluate("go('till')")
            pg.evaluate("U.till={bill:'789.50',cash:'1000'};$('till-bill').value='789.50';$('till-cash').value='1000';updateTill()")
            pg.evaluate("document.getElementById('cashRow').scrollIntoView({block:'center'})")
            ok(pg.evaluate(NO_SIDEWAYS), f'{w} px {sc}: no sideways scroll')
            t.shot(pg, f'{w}-{sc}-change')
            pg.evaluate("U.till={bill:'1',cash:'1190.25'};$('till-bill').value='1';$('till-cash').value='1190.25';updateTill()")
            t.shot(pg, f'{w}-{sc}-coins')
            pg.context.close()
        pg = t.page(b, w=w, h=h, init=SLOW + ';' + SLOT, sc='dark')
        pg.evaluate("go('till')"); pg.fill('#till-bill', '789.50')
        pg.click('[data-a=cashAdd][data-v="500"]'); pg.wait_for_timeout(1100)
        t.shot(pg, f'{w}-dark-slotting')
        pg.context.close()
