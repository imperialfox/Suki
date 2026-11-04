"""Quick Till: the till drawer (Q19). With motion on: hidden at rest (the line too), shown on touch; it follows the
finger and decides by where it would coast to (a 45 pt held pull shuts, 55 pt opens, a tiny flick shuts, a flick
whose last frame stalls opens); it stretches past open and springs back; it's caught mid-movement; a swipe up shuts it
and the rest scrolls the page, gliding on after a flick until a new touch; the knock only on a hard shut, only on the
cash box, at the instant it hits; the cash box's shadow follows the opening; typing, a redraw, a tab switch and a
sheet leave it shut with nothing left running; a hold or a sideways drag in the box is left to the text; the handle's
labels, Enter and Space; Reduce Motion fades only; motion off jumps; no drawer on its side; the card's width, click,
keys and a mouse drag on iPad and Mac; notes still fly with it open; nothing sideways. Screenshots open and shut at
375 and 402 px, light and dark, iPad and Mac."""

ON = "localStorage.setItem('suki:motion','1')"
REDUCE = "localStorage.setItem('suki:reduceMotion','on')"
# every animation on the cash box is logged with the drawer's height at that instant (the knock)
KNOCKS = """window.__knocks=[];(()=>{const A=Element.prototype.animate;Element.prototype.animate=function(f,o){
  if(this.classList&&this.classList.contains('cashbox'))window.__knocks.push({h:DR.h,f:JSON.stringify(f)});return A.call(this,f,o)}})()"""
# a finger in the page itself, so the timing of each frame is the page's own (touch, one pointer)
DRAG = """async ([sel, moves, hold, keep, dx]) => {
  const el = document.querySelector(sel), r = el.getBoundingClientRect(), x0 = r.left + r.width / 2, y0 = r.top + r.height / 2;
  let x = x0, y = y0;
  const fire = (t) => el.dispatchEvent(new PointerEvent(t, {bubbles: true, cancelable: true, pointerId: 7, pointerType: 'touch', isPrimary: true, clientX: x, clientY: y, button: 0}));
  const wait = (ms) => new Promise((ok) => setTimeout(ok, ms));
  fire('pointerdown');
  for (const [dy, ms] of moves) { await wait(ms); y += dy; x += dx || 0; fire('pointermove'); }
  await wait(hold || 0);
  if (!keep) fire('pointerup');
  return DR.h;
}"""
UP = "document.querySelector('#app .cashbox').dispatchEvent(new PointerEvent('pointerup',{bubbles:true,pointerId:7,pointerType:'touch',isPrimary:true}))"
SETTLED = "!DR.raf && !DR.drag && !DR.fade"
H = "DR.h"
NO_SIDEWAYS = "document.scrollingElement.scrollWidth<=innerWidth"
LABEL = "$('tillHdl').getAttribute('aria-label')"


def frames(total, n, ms=16):
    return [[total / n, ms] for _ in range(n)]


def settle(pg):
    pg.wait_for_function(SETTLED, timeout=5000)
    pg.wait_for_timeout(30)


def till(pg):
    pg.evaluate("go('till')")
    pg.fill('#till-bill', '789.50')
    pg.fill('#till-cash', '1000')
    pg.evaluate("document.activeElement.blur()")
    pg.wait_for_timeout(50)


def drag(pg, moves, sel='#app .cashbox', hold=0, keep=False, dx=0):
    return pg.evaluate(DRAG, [sel, moves, hold, keep, dx])


def opened(pg):
    pg.click('#tillHdl')
    settle(pg)


def run(b, t):
    ok = t.ok

    # ── 1 · At rest: hidden, and nothing points to it ───────────────────────────────────────────────────
    pg = t.page(b, w=402, h=874, init=ON + ';' + KNOCKS)
    till(pg)
    ok(pg.evaluate("$('tillDrawer').offsetHeight") == 0 and pg.evaluate(H) == 0, 'the drawer starts shut: no height at all')
    ok(pg.evaluate("getComputedStyle($('tillSlot')).opacity") == '0' and not pg.evaluate("$('tillHdl').classList.contains('on')"),
       'the slot line is hidden at rest')
    ok(pg.evaluate(LABEL) == 'Open till drawer' and pg.get_attribute('#tillHdl', 'aria-expanded') == 'false' and pg.evaluate("$('tillHdl').tagName") == 'BUTTON',
       'the line is a real button: "Open till drawer", not expanded')
    ok(pg.get_attribute('#tillTray', 'aria-hidden') == 'true', 'the tray itself is hidden from VoiceOver')
    ok(pg.evaluate("document.querySelectorAll('#tillTray .tslot').length") == 4 and pg.evaluate("document.querySelectorAll('#tillTray .tcup').length") == 5
       and pg.evaluate("document.querySelectorAll('#tillTray .tslot > span, #tillTray .tcup > span').length") == 9,
       'inside: four note slots and five coin cups, each labelled (Q20 fills them: test_drawerfill.py)')
    ok('drawer' not in pg.evaluate("scrHelp()").lower() and 'drawer' not in pg.evaluate("JSON.stringify(TIPS)").lower(),
       'no tip and nothing in Help: it’s an Easter egg')
    gap = pg.evaluate("""(()=>{const i=$('till-cash').getBoundingClientRect(),d=document.querySelector('#app .denoms').getBoundingClientRect(),h=$('tillHdl').getBoundingClientRect();
      return [Math.round(d.top-i.bottom), Math.round(h.top-i.bottom), Math.round(h.height)]})()""")
    ok(gap == [14, 0, 14], f'shut, the Till is laid out as before: the handle is the 14 pt gap above the buttons ({gap})')
    ok(pg.evaluate("getComputedStyle(document.querySelector('#app .cashbox')).touchAction") == 'none', 'the cash box takes the pull itself')
    t.shot(pg, 'shut-402-light')

    # touching the cash box shows the line; a tap still types, and the line goes again
    bb = pg.locator('#till-cash').bounding_box()
    pg.mouse.move(bb['x'] + 40, bb['y'] + bb['height'] / 2); pg.mouse.down()
    ok(pg.evaluate("$('tillHdl').classList.contains('on')"), 'touching the cash box shows the line')
    pg.mouse.up()
    ok(pg.evaluate("document.activeElement.id") == 'till-cash' and pg.evaluate(H) == 0, 'a tap still types: the box has the cursor, the drawer stays shut')
    pg.wait_for_function("!$('tillHdl').classList.contains('on')", timeout=3000)
    ok(True, 'and the line hides again a moment later')
    pg.evaluate("document.activeElement.blur()")

    # ── 2 · Open or shut: by where it would coast to ────────────────────────────────────────────────────
    h = drag(pg, frames(45, 9), hold=260, keep=True)
    ok(abs(h - 45) < 0.5, f'it follows the finger exactly: 45 pt pulled is 45 pt open ({h:.1f})')
    v = pg.evaluate("getComputedStyle(document.querySelector('#app .cashbox')).getPropertyValue('--open')")
    ok(abs(float(v) - 45 / 106) < 0.01, f'the cash box’s shadow deepens with it (--open {v})')
    pg.evaluate(UP); settle(pg)
    ok(pg.evaluate(H) == 0 and not pg.evaluate("DR.open"), 'a 45 pt pull held still springs back shut (short of halfway)')
    ok(pg.evaluate("__knocks.length") == 0, 'gently, with no knock')
    drag(pg, frames(55, 11), hold=260); settle(pg)
    ok(pg.evaluate(H) == 106 and pg.evaluate("DR.open"), 'a 55 pt pull held still opens it, to 106 pt')
    ok(pg.evaluate(LABEL) == 'Close till drawer' and pg.get_attribute('#tillHdl', 'aria-expanded') == 'true', 'open, the button says "Close till drawer"')
    ok(pg.evaluate("getComputedStyle($('tillSlot')).opacity") == '1', 'the line stays while it’s open')
    ok(pg.evaluate("getComputedStyle(document.querySelector('#app .cashbox')).getPropertyValue('--open')").strip() == '1.000', 'the shadow is full when open')
    t.shot(pg, 'open-402-light')
    pg.click('#tillHdl'); settle(pg)
    ok(pg.evaluate(H) == 0 and pg.evaluate(LABEL) == 'Open till drawer', 'tapping the line shuts it')
    ok(pg.evaluate("__knocks.length") == 0, 'a tap shuts it quietly: no knock')
    pg.wait_for_function("!$('tillHdl').classList.contains('on')", timeout=3000)
    ok(True, 'shut, the line hides again')

    drag(pg, frames(12, 4)); settle(pg)
    ok(pg.evaluate(H) == 0, 'a tiny flick (12 pt) shuts')
    drag(pg, frames(36, 3) + [[0.5, 45]]); settle(pg)
    ok(pg.evaluate(H) == 106, 'a 36 pt flick whose last frame stalls opens: its speed is read over the last tenth of a second')
    pg.click('#tillHdl'); settle(pg)

    # a real mouse drag works the same
    bb = pg.locator('#app .cashbox').bounding_box()
    x, y = bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2
    pg.mouse.move(x, y); pg.mouse.down()
    for i in range(1, 12):
        pg.mouse.move(x, y + i * 7); pg.wait_for_timeout(16)
    pg.wait_for_timeout(260); pg.mouse.up(); settle(pg)
    ok(pg.evaluate(H) == 106 and pg.evaluate("document.activeElement.id") != 'till-cash', 'a mouse drag opens it too, and doesn’t leave the cursor in the box')

    # past open it stretches, then springs back
    h = drag(pg, frames(200, 10), keep=True)
    ok(106 < h < 146, f'pulled past open, it stretches with iOS’s rubber band, never more than 40 pt ({h:.1f})')
    ok(pg.evaluate(NO_SIDEWAYS), 'nothing sideways while stretched')
    pg.evaluate(UP); settle(pg)
    ok(pg.evaluate(H) == 106, 'let go, it springs back to open')

    # caught mid-movement
    pg.click('#tillHdl'); pg.wait_for_timeout(90)
    mid = pg.evaluate(H)
    ok(5 < mid < 100, f'shutting, it’s on its way ({mid:.1f})')
    drag(pg, [], sel='#tillTray', keep=True)
    a = pg.evaluate(H); pg.wait_for_timeout(150); b2 = pg.evaluate(H)
    ok(abs(a - b2) < 0.5 and 5 < a < 100, f'caught mid-movement: it stops where the finger lands ({a:.1f} → {b2:.1f})')
    pg.evaluate("$('tillTray').dispatchEvent(new PointerEvent('pointerup',{bubbles:true,pointerId:7,pointerType:'touch',isPrimary:true}))"); settle(pg)
    ok(pg.evaluate(H) == 0, 'let go without moving, it carries on to where it was going')

    # ── 3 · The knock: only a hard shut, only the cash box, at the instant it hits ──────────────────────
    pg.evaluate("__knocks.length=0")
    opened(pg)
    drag(pg, [[-4, 16]] * 15, hold=200); settle(pg)
    ok(pg.evaluate(H) == 0 and pg.evaluate("__knocks.length") == 0, 'pushed shut slowly: no knock')
    opened(pg)
    drag(pg, frames(-60, 4)); settle(pg)
    k = pg.evaluate("__knocks")
    ok(pg.evaluate(H) == 0 and len(k) == 1, f'flicked shut from 46 pt: it carries on shut and knocks once ({len(k)})')
    if k:
        import re, json
        ys = [float(m) for m in re.findall(r'translateY\((-?[\d.]+)px\)', k[0]['f'])]
        ok(k[0]['h'] == 0, 'the knock comes the instant the drawer hits shut')
        ok(ys and 1 <= -min(ys) <= 2.2, f'the cash box nudges up 1–2.2 pt ({ys})')
    ok(pg.evaluate("document.querySelectorAll('#app .card.form .denoms, #tillOut').length") == 2
       and pg.evaluate("[...document.querySelectorAll('#app .denoms, #tillOut, #tillDrawer')].every(e=>!e.getAnimations().length)"),
       'only the cash box moves: nothing else animates')

    # ── 4 · The chain: shut, then the rest of the swipe scrolls the page ───────────────────────────────
    pg.close()
    pg = t.page(b, w=402, h=620, init=ON + ';' + KNOCKS)
    till(pg)
    opened(pg)
    ok(pg.evaluate("window.scrollY") == 0, 'the page starts at the top')
    drag(pg, frames(-186, 6), keep=True)
    y = pg.evaluate("window.scrollY")
    ok(pg.evaluate(H) == 0 and 70 <= y <= 90, f'a swipe up 186 pt shuts it (106) and the other 80 scrolls the page ({y})')
    ok(len(pg.evaluate("__knocks")) == 1, 'swiped shut fast on the way into the scroll: one knock')
    pg.evaluate(UP); pg.wait_for_timeout(250)
    y2 = pg.evaluate("window.scrollY")
    ok(y2 > y + 30, f'let go mid-flick, the page glides on ({y} → {y2})')
    pg.wait_for_function("!DR.glide", timeout=4000)
    ok(not pg.evaluate("DR.open") and pg.evaluate(LABEL) == 'Open till drawer', 'and the drawer is shut')
    pg.evaluate("window.scrollTo(0,0)")
    drag(pg, frames(-150, 5))
    pg.wait_for_timeout(60)
    pg.evaluate("document.body.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true}))")
    s1 = pg.evaluate("window.scrollY"); pg.wait_for_timeout(150); s2 = pg.evaluate("window.scrollY")
    ok(s1 > 100 and s1 == s2 and pg.evaluate("!DR.glide"), f'shut, a swipe up on the cash box scrolls the page; a new touch stops the glide ({s1} → {s2})')
    pg.evaluate("document.body.dispatchEvent(new PointerEvent('pointerup',{bubbles:true}))")
    pg.evaluate("window.scrollTo(0,0)")

    # ── 5 · It starts shut every time ───────────────────────────────────────────────────────────────────
    opened(pg)
    pg.click('#till-cash'); pg.keyboard.type('5')
    settle(pg)
    ok(pg.evaluate(H) == 0 and '5' in pg.input_value('#till-cash'), 'typing in the cash box shuts it')
    pg.evaluate("document.activeElement.blur()")
    opened(pg)
    pg.focus('#till-bill'); settle(pg)
    ok(pg.evaluate(H) == 0, 'so does starting to type in the bill')
    pg.evaluate("document.activeElement.blur()")
    opened(pg)
    pg.evaluate("rerender()")
    ok(pg.evaluate("$('tillDrawer').offsetHeight") == 0 and pg.evaluate(LABEL) == 'Open till drawer' and not pg.evaluate("DR.open"),
       'a redraw brings it back shut')
    pg.click('#tillHdl'); pg.wait_for_timeout(60)
    pg.evaluate("rerender()"); pg.wait_for_timeout(500)
    ok(pg.evaluate("$('tillDrawer').offsetHeight") == 0 and pg.evaluate("DR.raf") == 0, 'a redraw mid-opening leaves no frames running: it stays shut')
    opened(pg)
    pg.evaluate("go('home')"); pg.evaluate("go('till')")
    ok(pg.evaluate("$('tillDrawer').offsetHeight") == 0 and pg.evaluate(H) == 0, 'switching tabs and back: shut')
    opened(pg)
    pg.click('#tillLog')
    pg.wait_for_selector('.sheet')
    ok(pg.evaluate("DR.h") == 0 and not pg.evaluate("DR.open"), 'Log this bill opens its sheet, and the drawer behind it is shut')
    ok(pg.evaluate("drawerOK()") is False, 'with a sheet open, the drawer takes no gestures')
    pg.keyboard.press('Escape'); pg.wait_for_function("!U.sheet", timeout=3000)
    ok(pg.evaluate("$('tillDrawer').offsetHeight") == 0, 'back from the sheet, still shut')

    # a hold, or a sideways drag, in the box is left to the text (2.24.1's cursor and selection)
    drag(pg, [[0, 600], [20, 16], [20, 16]], sel='#till-cash')
    ok(pg.evaluate(H) == 0, 'held still first, a drag in the box is left to the cursor')
    drag(pg, [[2, 16], [2, 16], [2, 16]], sel='#till-cash', dx=10)
    ok(pg.evaluate(H) == 0, 'a sideways drag in the box is left to selecting')

    # notes still fly in with it open
    opened(pg)
    pg.click('#cashClear')
    pg.click('[data-a=cashAdd][data-v="100"]')
    pg.wait_for_function("document.querySelectorAll('.nfly').length===0", timeout=5000)
    ok(pg.evaluate("U.till.cash") == '100' and pg.evaluate(H) == 106, 'tapping a note with it open: the note lands, and the drawer stays open')
    pg.close()

    # ── 6 · Keys and VoiceOver ──────────────────────────────────────────────────────────────────────────
    pg = t.page(b, w=402, h=874, init=ON)
    till(pg)
    pg.focus('#till-cash')
    for _ in range(4):
        pg.keyboard.press('Tab')
        if pg.evaluate("document.activeElement.id") == 'tillHdl':
            break
    ok(pg.evaluate("document.activeElement.id") == 'tillHdl', 'Tab reaches the line')
    pg.wait_for_timeout(300)
    ok(pg.evaluate("getComputedStyle($('tillSlot')).opacity") == '1', 'focused from the keyboard, the line shows')
    pg.keyboard.press('Enter'); settle(pg)
    ok(pg.evaluate(H) == 106 and pg.evaluate(LABEL) == 'Close till drawer', 'Enter opens it')
    pg.keyboard.press('Space'); settle(pg)
    ok(pg.evaluate(H) == 0 and pg.evaluate(LABEL) == 'Open till drawer', 'Space shuts it')
    pg.close()

    # ── 7 · Reduce Motion: a 0.2 s fade, no spring, no knock ────────────────────────────────────────────
    pg = t.page(b, w=402, h=874, init=ON + ';' + REDUCE + ';' + KNOCKS)
    till(pg)
    pg.click('#tillHdl')
    ok(pg.evaluate(H) == 106, 'Reduce Motion: it’s open at once, with no spring')
    an = pg.evaluate("$('tillTray').getAnimations().map(a=>a.effect.getKeyframes().map(k=>[k.opacity,k.transform||'']))")
    ok(len(an) == 1 and an[0][0][0] == '0' and an[0][-1][0] == '1' and not any(f[1] for f in an[0]), f'the tray fades in, and nothing moves ({an})')
    pg.wait_for_timeout(300)
    drag(pg, frames(-60, 4)); pg.wait_for_timeout(30)
    ok(pg.evaluate(H) == 46 and pg.evaluate("!!DR.fade"), 'flicked shut: it fades out first, with no spring')
    settle(pg)
    ok(pg.evaluate(H) == 0 and pg.evaluate("__knocks.length") == 0, 'then it’s shut, with no knock')
    pg.close()

    pg = t.page(b, w=402, h=874)  # motion off, as every other test
    till(pg)
    pg.click('#tillHdl')
    ok(pg.evaluate(H) == 106 and pg.evaluate("$('tillTray').getAnimations().length") == 0, 'motion off: it jumps open, nothing animates')
    pg.click('#tillHdl')
    ok(pg.evaluate(H) == 0, 'and jumps shut')
    pg.close()

    # ── 8 · Devices ─────────────────────────────────────────────────────────────────────────────────────
    pg = t.page(b, w=852, h=393, init=ON)
    till(pg)
    ok(pg.evaluate("getComputedStyle($('tillHdl')).visibility") == 'hidden' and pg.evaluate("getComputedStyle($('tillDrawer')).display") == 'none',
       'iPhone on its side: no drawer and no line, so VoiceOver and the keyboard skip it')
    drag(pg, frames(80, 8), hold=100)
    ok(pg.evaluate(H) == 0 and pg.evaluate("getComputedStyle(document.querySelector('#app .cashbox')).touchAction") == 'manipulation',
       'pulling the cash box does nothing, and it scrolls like anything else')
    pg.close()

    pg = t.page(b, w=402, h=874, init=ON)
    till(pg)
    opened(pg)
    pg.set_viewport_size({'width': 874, 'height': 402}); pg.wait_for_timeout(200)
    ok(pg.evaluate(H) == 0 and not pg.evaluate("DR.open") and pg.evaluate(LABEL) == 'Open till drawer', 'turned on its side while open: it shuts at once')
    pg.close()

    for w, h, name in [(820, 1180, 'ipad'), (1440, 900, 'mac')]:
        pg = t.page(b, w=w, h=h, ua=None, init=ON)
        till(pg)
        wd = pg.evaluate("[$('tillDrawer').getBoundingClientRect().width, document.querySelector('#app .denoms').getBoundingClientRect().width]")
        ok(abs(wd[0] - wd[1]) < 1, f'{name}: the drawer is the card’s width ({wd})')
        pg.click('#tillHdl'); settle(pg)
        ok(pg.evaluate(H) == 106, f'{name}: a click on the line opens it')
        ok(pg.evaluate(NO_SIDEWAYS), f'{name}: nothing sideways')
        t.shot(pg, f'open-{name}')
        pg.keyboard.press('Enter'); settle(pg)
        ok(pg.evaluate(H) == 0, f'{name}: Enter on the focused line shuts it')
        bb = pg.locator('#app .cashbox').bounding_box()
        x, y = bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2
        pg.mouse.move(x, y); pg.mouse.down()
        for i in range(1, 12):
            pg.mouse.move(x, y + i * 7); pg.wait_for_timeout(16)
        pg.wait_for_timeout(260); pg.mouse.up(); settle(pg)
        ok(pg.evaluate(H) == 106, f'{name}: a mouse drag opens it')
        pg.close()

    # ── 9 · Screenshots: open and shut, 375 and 402 px, light and dark ─────────────────────────────────
    for w in (375, 402):
        for sc in ('light', 'dark'):
            pg = t.page(b, w=w, h=874 if w == 402 else 812, sc=sc)
            till(pg)
            t.shot(pg, f'shut-{w}-{sc}')
            pg.click('#tillHdl')
            ok(pg.evaluate(H) == 106 and pg.evaluate(NO_SIDEWAYS), f'{w} px {sc}: open, nothing sideways')
            if sc == 'dark':
                c = pg.evaluate("[getComputedStyle(document.documentElement).getPropertyValue('--dr-wall'),getComputedStyle(document.documentElement).getPropertyValue('--dr-occlude')]")
                ok(c[0].strip() == 'rgba(0, 0, 0, 0.36)' and c[1].strip() == 'rgba(0, 0, 0, 0.55)', 'dark mode has its own walls and shadow')
            t.shot(pg, f'open-{w}-{sc}')
            pg.close()
