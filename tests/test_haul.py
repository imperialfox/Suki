"""Quick Till: the haul and the maker's mark (Q21). With motion on, using synthetic two-finger pointers in the page (and
real two-finger touches through Chromium's touch input, past the zoom blocker): one finger never starts it, nor two on
a shut or part-open drawer; each 350 pt swipe moves it 12.25 pt, straight; ten reach 120 pt past open and it stops
there; it stays when let go; the holding finger moving up doesn't count, but once only one finger is left, up does;
fingers can swap; a one-finger give springs back to the hauled spot; a swipe up, the line, Enter, typing and a redraw
shut it from any depth, and it reopens to plain open; "Designed by Ivan" (Caption 2, regular, --fg3, hidden from
VoiceOver) is hidden until the ninth swipe peeks it and the tenth shows it whole; notes still land in their
compartments; Reduce Motion still hauls; nothing saved; nothing sideways. Screenshots fully hauled at 375 and 402 px,
light and dark."""
from harness import BROWSER

ON = "localStorage.setItem('suki:motion','1')"
REDUCE = "localStorage.setItem('suki:reduceMotion','on')"
# fingers in the page itself. F(id, type, sel, y) fires one pointer event at a fixed x for that finger
FINGERS = """window.__F=(id,type,sel,y)=>{const el=document.querySelector(sel),r=el.getBoundingClientRect();
  window.__fy=window.__fy||{};if(y===undefined)y=window.__fy[id]!==undefined&&type!=='pointerdown'?window.__fy[id]:r.top+r.height/2;window.__fy[id]=y;
  el.dispatchEvent(new PointerEvent(type,{bubbles:true,cancelable:true,pointerId:id,pointerType:'touch',isPrimary:id===1,clientX:r.left+r.width*(id===1?0.3:0.7),clientY:y,button:0}))};
window.__swipe=async(id,sel,dist,n,lift)=>{const w=(ms)=>new Promise(ok=>setTimeout(ok,ms));
  __F(id,'pointerdown',sel);for(let i=0;i<n;i++){await w(16);__F(id,'pointermove',sel,__fy[id]+dist/n)}if(lift!==false)__F(id,'pointerup',sel)};
window.__haul=async(k,dist)=>{__F(1,'pointerdown','#app .cashbox');for(let i=0;i<k;i++)await __swipe(2,'#tillTray',dist||350,10);__F(1,'pointerup','#app .cashbox')};"""
DRAG = """async ([sel, moves, hold, keep]) => {
  const el = document.querySelector(sel), r = el.getBoundingClientRect(), x = r.left + r.width / 2;
  let y = r.top + r.height / 2;
  const fire = (t) => el.dispatchEvent(new PointerEvent(t, {bubbles: true, cancelable: true, pointerId: 7, pointerType: 'touch', isPrimary: true, clientX: x, clientY: y, button: 0}));
  const wait = (ms) => new Promise((ok) => setTimeout(ok, ms));
  fire('pointerdown');
  for (const [dy, ms] of moves) { await wait(ms); y += dy; fire('pointermove'); }
  await wait(hold || 0);
  if (!keep) fire('pointerup');
  return DR.h;
}"""
UP7 = "document.querySelector('#app .cashbox').dispatchEvent(new PointerEvent('pointerup',{bubbles:true,pointerId:7,pointerType:'touch',isPrimary:true}))"
SETTLED = "!DR.raf && !DR.drag && !DR.fade && !DR.haul && !DR.eat"
H = "DR.h"
NO_SIDEWAYS = "document.scrollingElement.scrollWidth<=innerWidth"
# how much of the mark shows in the opening, 0 to 1
MARK = """(()=>{const m=$('tillMark').getBoundingClientRect(),d=$('tillDrawer').getBoundingClientRect();
  const v=Math.max(0,Math.min(m.bottom,d.bottom)-Math.max(m.top,d.top));return m.height?v/m.height:0})()"""


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


def opened(pg):
    pg.click('#tillHdl')
    settle(pg)
    pg.evaluate("document.activeElement.blur()")


def haul(pg, k, dist=350):
    pg.evaluate(f"__haul({k},{dist})")
    settle(pg)
    return pg.evaluate(H)


def near(a, b, d=0.05):
    return abs(a - b) <= d


def run(b, t):
    ok = t.ok

    # ── 1 · One finger never starts it ──────────────────────────────────────────────────────────────────
    pg = t.page(b, w=402, h=874, init=ON + ';' + FINGERS)
    till(pg)
    ok(pg.evaluate("$('tillMark').textContent") == 'Designed by Ivan' and pg.get_attribute('#tillMark', 'aria-hidden') == 'true',
       'the mark reads "Designed by Ivan", hidden from VoiceOver (the tray is too)')
    st = pg.evaluate("(()=>{const s=getComputedStyle($('tillMark'));return [s.fontSize,s.fontWeight,s.color,s.position,s.bottom]})()")
    fg3 = pg.evaluate("(()=>{const e=document.createElement('i');e.style.color='var(--fg3)';document.body.appendChild(e);const c=getComputedStyle(e).color;e.remove();return c})()")
    ok(st[:2] == ['11px', '400'] and st[2] == fg3, f'plain Caption 2: 11 pt, regular, in the faint grey --fg3 ({st[:3]})')
    ok(st[3:] == ['absolute', '224px'], f'placed 224 pt from the tray’s front ({st[3:]})')
    ok(pg.evaluate("document.querySelectorAll('#tillTray .tslot #tillMark, #tillTray .tcup #tillMark').length") == 0,
       'the mark sits outside the compartments, so Q20’s fill and jiggle leave it alone')

    # shut: two fingers do nothing
    pg.evaluate("__F(1,'pointerdown','#app .cashbox')")
    pg.evaluate("__swipe(2,'#tillTray',350,10)"); pg.wait_for_timeout(400)
    ok(pg.evaluate("DR.haul") is None and pg.evaluate(H) == 0, 'shut, a second finger does nothing: no haul')
    pg.evaluate("__F(1,'pointerup','#app .cashbox')"); settle(pg)
    pg.evaluate("document.activeElement.blur()")

    opened(pg)
    ok(pg.evaluate(H) == 106, 'opened with the line, to 106 pt')
    ok(pg.evaluate(MARK) == 0, 'open, the mark is out of sight')
    h = pg.evaluate(DRAG, ['#tillTray', frames(350, 10), 0, True])
    ok(106 < h < 146, f'one finger pulling 350 pt only stretches it, as before ({h:.1f})')
    pg.evaluate(UP7); settle(pg)
    ok(pg.evaluate(H) == 106 and pg.evaluate("DR.rest") == 106, 'let go, it springs back to open: one finger never hauls')
    bb = pg.locator('#tillTray').bounding_box()
    x, y = bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] / 2
    pg.mouse.move(x, y); pg.mouse.down()
    for i in range(1, 30):
        pg.mouse.move(x, y + i * 12); pg.wait_for_timeout(16)
    pg.mouse.up(); settle(pg)
    ok(pg.evaluate(H) == 106, 'a mouse has one pointer, so it can’t haul either')

    # ── 2 · Heavy and steady ────────────────────────────────────────────────────────────────────────────
    pg.evaluate("__F(1,'pointerdown','#app .cashbox')")
    pg.evaluate("__swipe(2,'#tillTray',175,5,false)"); pg.wait_for_function("DR.haul && __fy[2]>0", timeout=3000); pg.wait_for_timeout(150)
    mid = pg.evaluate(H)
    ok(pg.evaluate("!!DR.haul") and near(mid, 106 + 175 * 0.035), f'held with one finger, a second finger hauls it: half a swipe (175 pt) is 6.1 pt ({mid - 106:.3f})')
    pg.evaluate("(async()=>{for(let i=0;i<5;i++){await new Promise(ok=>setTimeout(ok,16));__F(2,'pointermove','#tillTray',__fy[2]+35)}})()"); pg.wait_for_timeout(200)
    one = pg.evaluate(H)
    ok(near(one, 106 + 12.25), f'straight, not eased: the rest of the swipe adds the same again ({one - 106:.3f})')
    before = pg.evaluate(H)
    pg.evaluate("(async()=>{for(let i=0;i<5;i++){await new Promise(ok=>setTimeout(ok,16));__F(1,'pointermove','#app .cashbox',__fy[1]-30)}})()"); pg.wait_for_timeout(200)
    ok(pg.evaluate(H) == before, 'with two fingers down, the holding finger moving up takes nothing off')
    pg.evaluate("(async()=>{for(let i=0;i<5;i++){await new Promise(ok=>setTimeout(ok,16));__F(1,'pointermove','#app .cashbox',__fy[1]+40)}})()"); pg.wait_for_timeout(200)
    ok(near(pg.evaluate(H), before + 200 * 0.035), 'and moving down, any finger adds')
    # swap: the first finger lifts, comes back down and pulls while the second stays
    pg.evaluate("__F(1,'pointerup','#app .cashbox')"); pg.wait_for_timeout(50)
    ok(pg.evaluate("!!DR.haul"), 'one finger still down: the haul carries on')
    b2 = pg.evaluate(H)
    pg.evaluate("__swipe(1,'#tillTray',350,10,false)"); pg.wait_for_timeout(400)
    ok(near(pg.evaluate(H), b2 + 12.25), 'hand over hand: a finger coming back down pulls again (12.25 pt a swipe)')
    pg.evaluate("__F(2,'pointerup','#tillTray')"); pg.wait_for_timeout(50)
    b3 = pg.evaluate(H)
    pg.evaluate("(async()=>{for(let i=0;i<5;i++){await new Promise(ok=>setTimeout(ok,16));__F(1,'pointermove','#tillTray',__fy[1]-20)}})()"); pg.wait_for_timeout(200)
    ok(near(pg.evaluate(H), b3 - 100 * 0.035), 'once a single finger is left, moving up counts too')
    pg.evaluate("__F(1,'pointerup','#tillTray')"); settle(pg)
    left = pg.evaluate(H)
    pg.wait_for_timeout(600)
    ok(pg.evaluate(H) == left and left > 106 and pg.evaluate("DR.rest") == left and pg.evaluate("DR.open"), f'let go, it stays where it was left ({left - 106:.2f} pt out)')
    ok(pg.evaluate("$('tillHdl').getAttribute('aria-label')") == 'Close till drawer', 'still open: the line says "Close till drawer"')

    # ── 3 · Ten swipes to the back, and the mark ────────────────────────────────────────────────────────
    pg.click('#tillHdl'); settle(pg)
    ok(pg.evaluate(H) == 0 and pg.evaluate("DR.rest") == 106, 'the line shuts it from any depth, and the haul is forgotten')
    opened(pg)
    ok(pg.evaluate(H) == 106, 'reopened, it’s back to plain open')
    seen = []
    for k in range(1, 11):
        h = haul(pg, 1)
        seen.append((k, round(h - 106, 2), round(pg.evaluate(MARK), 2)))
    ok([s[1] for s in seen] == [12.25, 24.5, 36.75, 49.0, 61.25, 73.5, 85.75, 98.0, 110.25, 120.0], f'each 350 pt swipe moves it 12.25 pt; ten reach 120 pt ({[s[1] for s in seen]})')
    ok(all(s[2] == 0 for s in seen[:8]), f'the mark is out of sight for the first eight swipes ({[s[2] for s in seen[:8]]})')
    ok(0 < seen[8][2] < 1, f'it peeks on the ninth ({seen[8][2]})')
    ok(seen[9][2] == 1, f'and is whole on the tenth ({seen[9][2]})')
    haul(pg, 2)
    ok(pg.evaluate(H) == 226, 'a hard stop: more swipes add nothing past 120 pt')
    ok(pg.evaluate(NO_SIDEWAYS), 'fully hauled, nothing sideways')
    t.shot(pg, 'hauled-402-light')

    # a one-finger give springs back to the hauled spot, not to plain open
    h = pg.evaluate(DRAG, ['#tillTray', frames(120, 8), 0, True])
    ok(h > 226, f'a one-finger pull on a hauled drawer gives a little ({h - 226:.1f} pt)')
    pg.evaluate(UP7); settle(pg)
    ok(near(pg.evaluate(H), 226, 0.01), 'and springs back to where it was left')
    pg.evaluate(DRAG, ['#tillTray', [[0, 40]], 0, False]); settle(pg)
    ok(near(pg.evaluate(H), 226, 0.01), 'a tap on the tray leaves it there too')

    # notes still land in their compartments
    pg.click('.denoms .dn[data-v="100"]'); pg.wait_for_function("!document.querySelector('.nfly')", timeout=5000); settle(pg)
    ok(pg.evaluate("U.till.cash") == '1100' and near(pg.evaluate(H), 226, 0.01), 'a note tapped in still lands, and the drawer stays hauled')

    # a swipe up shuts it from the back
    pg.evaluate(DRAG, ['#tillTray', frames(-320, 6), 0, False]); settle(pg)
    ok(pg.evaluate(H) == 0 and not pg.evaluate("DR.open"), 'a swipe up shuts it from the very back')
    opened(pg)
    ok(pg.evaluate(H) == 106, 'and it reopens to plain open')

    # a push up that doesn't shut it leaves it there
    haul(pg, 4)
    pg.evaluate(DRAG, ['#tillTray', frames(-20, 10, 30), 300, False]); settle(pg)
    ok(near(pg.evaluate(H), 106 + 49 - 20, 0.01), f'a slow one-finger push up that doesn’t shut it leaves it where the push ended ({pg.evaluate(H) - 106:.2f})')

    # typing, Enter and a redraw shut it from any depth
    pg.fill('#till-cash', '2000'); settle(pg)
    ok(pg.evaluate(H) == 0, 'typing shuts it from any depth')
    opened(pg); haul(pg, 3)
    pg.focus('#tillHdl'); pg.keyboard.press('Enter'); settle(pg)
    ok(pg.evaluate(H) == 0, 'Enter on the line shuts it')
    pg.keyboard.press('Enter'); settle(pg)
    ok(pg.evaluate(H) == 106, 'and opens it again to plain open')
    haul(pg, 3)
    pg.evaluate("__F(1,'pointerdown','#app .cashbox')"); pg.evaluate("__swipe(2,'#tillTray',200,5,false)"); pg.wait_for_timeout(200)
    pg.evaluate("render()")
    ok(pg.evaluate("DR.haul") is None and pg.evaluate(H) == 0 and pg.evaluate("$('tillDrawer').offsetHeight") == 0, 'a redraw mid-haul brings it back shut, with the haul dropped')
    pg.evaluate("__F(2,'pointermove','#tillTray',__fy[2]+200)"); pg.wait_for_timeout(100)
    ok(pg.evaluate(H) == 0, 'and the fingers still down move nothing')
    pg.evaluate("__F(1,'pointerup','#app .cashbox');__F(2,'pointerup','#tillTray')"); pg.wait_for_timeout(100)
    opened(pg)
    ok(pg.evaluate(H) == 106, 'opened again: plain open')

    # nothing is saved
    keys = pg.evaluate("Object.keys(localStorage).sort().join(',')")
    haul(pg, 2)
    ok(pg.evaluate("Object.keys(localStorage).sort().join(',')") == keys, 'the haul saves nothing')
    pg.reload(); pg.wait_for_function("typeof DR!=='undefined' && !document.querySelector('.launch')", timeout=8000)
    pg.evaluate("go('till')"); pg.wait_for_timeout(100)
    ok(pg.evaluate(H) == 0, 'after a reload it starts shut')
    pg.close()

    # ── 4 · Real two-finger touches, past the zoom blocker ──────────────────────────────────────────────
    if BROWSER == 'chromium':
        pg = t.page(b, w=402, h=874, touch=True, init=ON + ';' + FINGERS)
        till(pg)
        opened(pg)
        cdp = pg.context.new_cdp_session(pg)
        box = pg.locator('#app .cashbox').bounding_box()
        tray = pg.locator('#tillDrawer').bounding_box()
        hx, hy = box['x'] + 40, box['y'] + box['height'] / 2
        sx, sy = tray['x'] + tray['width'] * 0.7, tray['y'] + tray['height'] / 2

        def touch(kind, pts):
            cdp.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': [{'x': x, 'y': y, 'id': i} for i, x, y in pts]})

        touch('touchStart', [(1, hx, hy)])
        for _ in range(2):
            touch('touchStart', [(1, hx, hy), (2, sx, sy)])
            for i in range(1, 11):
                touch('touchMove', [(1, hx, hy), (2, sx, sy + i * 35)]); pg.wait_for_timeout(16)
            touch('touchEnd', [(1, hx, hy)])
            pg.wait_for_timeout(30)
        touch('touchEnd', [])
        settle(pg)
        h = pg.evaluate(H)
        ok(near(h, 106 + 24.5, 0.6), f'real two-finger touches haul it: the zoom blocker doesn’t swallow the second finger (two swipes, {h - 106:.2f} pt)')
        ok(pg.evaluate("document.activeElement.id") != 'till-cash' and pg.evaluate("DR.open"), 'the holding finger in the cash box leaves no cursor there and doesn’t shut it')
        ok(pg.evaluate("visualViewport.scale") == 1, 'and nothing zoomed')
        pg.close()
    else:  # Chrome's own touch input (CDP); WebKit has none, and sections 1 to 3 cover the haul with made-up fingers
        t.skip('real two-finger touches past the zoom blocker: they go through Chrome’s own touch input (CDP)')

    # ── 5 · Reduce Motion: it still hauls (it follows the fingers); it shuts with a fade ─────────────────
    pg = t.page(b, w=402, h=874, init=ON + ';' + REDUCE + ';' + FINGERS)
    till(pg)
    opened(pg)
    ok(near(haul(pg, 2), 106 + 24.5), 'Reduce Motion: the haul still follows the fingers')
    pg.click('#tillHdl'); settle(pg)
    ok(pg.evaluate(H) == 0, 'and shuts from depth with its fade')
    pg.close()

    # ── 6 · iPad: two fingers there too ─────────────────────────────────────────────────────────────────
    pg = t.page(b, w=820, h=1180, ua=None, init=ON + ';' + FINGERS)
    till(pg)
    opened(pg)
    ok(pg.evaluate(H) == 106 and near(haul(pg, 10), 226), 'iPad: ten swipes reach the back too')
    ok(pg.evaluate(MARK) == 1 and pg.evaluate(NO_SIDEWAYS), 'iPad: the mark whole, nothing sideways')
    t.shot(pg, 'hauled-ipad')
    pg.close()

    # ── 7 · Screenshots: fully hauled, 375 and 402 px, light and dark ───────────────────────────────────
    for w in (375, 402):
        for sc in ('light', 'dark'):
            pg = t.page(b, w=w, h=874 if w == 402 else 812, sc=sc, init=ON + ';' + FINGERS)
            till(pg)
            opened(pg)
            haul(pg, 10)
            ok(pg.evaluate(H) == 226 and pg.evaluate(MARK) == 1 and pg.evaluate(NO_SIDEWAYS), f'{w} px {sc}: fully hauled, the mark whole, nothing sideways')
            if (w, sc) == (375, 'light'):
                pos = "[Math.round(document.querySelector('#app .tillout').getBoundingClientRect().top+scrollY),Math.round(document.querySelector('#dock .tabbar').getBoundingClientRect().top)]"
                deep = pg.evaluate(pos)
                pg.click('#tillHdl'); settle(pg); pg.evaluate("window.scrollTo(0,0)"); opened(pg)
                plain = pg.evaluate(pos)
                ok(deep[0] - plain[0] == 120 and deep[1] == plain[1], f'hauled, the change below is pushed down 120 pt more and the tab bar stays put ({deep} vs {plain})')
                haul(pg, 10)
            t.shot(pg, f'hauled-{w}-{sc}')
            pg.close()
