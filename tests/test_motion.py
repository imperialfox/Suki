"""Things arrive and leave (Q11), with motion switched on, on the parts kit's sheets since Q27: a sheet rises from the
bottom on the kit's sheet spring and leaves in 350 ms speeding up (part 41), while the page behind follows it (D21); it
closes by its ✕, the dim, Escape, a flick or a drag from its head or its content, and never takes a tap on its way out;
a sheet opened from a sheet rises over it and the first waits underneath, still open; Delete asks in the kit's alert
(D08); on iPad a centred sheet shrinks and fades over --dur-close (S01); Reduce Motion gives the kit's 100 ms fades
(D20); a saved purchase lands in its list while the rows below move; a deleted row shrinks away and Undo brings it back
the same way; Home's Save button says "Saved"; "Purchase saved" has Undo. Frames at 4× slow motion, light and dark, go
to tests/output."""
from harness import READ, flick

SLOW = "localStorage.setItem('suki:motion','4')"
ON = "localStorage.setItem('suki:motion','1')"

# every running animation on an element, as [keyframes] (offsets dropped)
ANIMS = """(e)=>e?e.getAnimations().filter(a=>a.playState==='running'&&a.effect.getKeyframes).map(a=>a.effect.getKeyframes().map(k=>({t:k.transform||'',o:k.opacity===undefined?'':String(k.opacity),bg:k.backgroundColor||''}))):[]"""
# the kit's sheets on their way out, and Suki's own (iPad and Mac) in #leaving
GHOSTS = "document.querySelectorAll('#layer .pk-sheet.pk-leaving, #leaving .sheet').length"
LEFT = "document.querySelectorAll('#leaving > *, #layer .pk-leaving, #layer .pk-dim:not(.pk-on)').length"
UNIQUE_IDS = "(()=>{const s=[...document.querySelectorAll('[id]')].map(e=>e.id);return s.length===new Set(s).size})()"
TOP = "document.querySelector('#layer .sheet')"
MOVING = "(e=>!!e&&e.getAnimations().some(a=>a.playState==='running'))"


def settled(pg):
    """Wait until nothing in the layer or #leaving is still moving or leaving."""
    pg.wait_for_timeout(40)  # a transition starts on the next frame
    pg.wait_for_function(f"!document.querySelector('#leaving > *, #layer .pk-leaving, #layer .pk-dim:not(.pk-on)')&&![...document.querySelectorAll('#layer .pk-sheet, #layer .sheet, #layer .pk-dim')].some({MOVING})", timeout=8000)


def open_sheet(pg, js):
    pg.evaluate(js)
    pg.wait_for_timeout(40)  # a transition starts on the next frame
    pg.wait_for_function(f"!!{TOP}&&![{TOP}, ...document.querySelectorAll('#layer .pk-dim')].some({MOVING})", timeout=8000)


def ghost_y(pg):
    return pg.evaluate("(()=>{const s=document.querySelector('#layer .pk-sheet.pk-leaving');return s?s.getBoundingClientRect().top:null})()")


def anims(pg, sel):
    return pg.evaluate(f"(s=>({ANIMS})(document.querySelector(s)))", sel)


def drag(pg, sel, dys, pause=0):
    """A pointer pressed on sel and moved down by each of dys in turn, then let go."""
    bb = pg.locator(sel).first.bounding_box()
    x, y = bb['x'] + min(40, bb['width'] / 2), bb['y'] + min(12, bb['height'] / 2)
    pg.mouse.move(x, y); pg.mouse.down()
    for d in dys:
        pg.mouse.move(x, y + d)
        if pause: pg.wait_for_timeout(pause)
    pg.mouse.up()


def run(b, t):
    ok = t.ok

    # ── 1 · A sheet rises and leaves the kit's way while the page behind follows it (iPhone, 4× slow motion) ──────
    pg = t.page(b, touch=True, init=SLOW)
    pg.evaluate("go('spending')")
    ok(pg.evaluate("getComputedStyle(document.querySelector('.wrap')).transitionDuration").startswith('1.4s'),
       'Slow motion slows the page behind a sheet too (it comes back on the leave timing, 0.35 s × 4)')
    pg.evaluate("openSheet('purchase',{id:'a1'})")
    pg.wait_for_timeout(150)
    sheet_ms = pg.evaluate("Parts.motion.spring('sheet')")
    rise = pg.evaluate(f"(e=>{{const c=getComputedStyle(e);return [c.transitionProperty,c.transitionDuration,e.getBoundingClientRect().top]}})({TOP})")
    ok('translate' in rise[0] and rise[1].split(',')[0] == f'{sheet_ms / 1000:g}s', f'it rises on the kit’s sheet spring ({rise[1].split(",")[0]}, {sheet_ms} ms at × 4)')
    wrap = pg.evaluate("getComputedStyle(document.querySelector('.wrap')).transitionDuration").split(',')[0]
    ok(wrap == f'{sheet_ms / 1000:g}s', f'the page behind shrinks on the same spring (D21: {wrap})')
    settled(pg)
    end = pg.evaluate(f"{TOP}.getBoundingClientRect().top")
    ok(rise[2] > end + 20, f'from below: mid-way it was lower down ({rise[2]:.0f} → {end:.0f})')
    ok(pg.evaluate("document.body.classList.contains('sheet-open')"), 'with a sheet open, the page behind is shrunk')
    look = pg.evaluate(f"(e=>{{const c=getComputedStyle(e);return [c.borderTopLeftRadius,e.classList.contains('pk-strong'),e.classList.contains('pk-sheet')]}})({TOP})")
    ok(look == ['46px', True, True], f'the kit’s sheet: 46 corners (D17) and strong glass (D15) ({look})')
    tb = pg.locator('#dock .tabbar').bounding_box()
    under = pg.evaluate("([x,y])=>{const e=document.elementFromPoint(x,y);return e?e.className:''}", [tb['x'] + tb['width'] / 2, tb['y'] + tb['height'] / 2]) if tb else None
    ok(tb is not None and under is not None and 'tabbar' not in under, f'the tab bar stays, under the dim (shared default 6: {under})')
    t.shot(pg, 'sheet-open-light')
    pg.click('#layer .sheet [data-a=close]')
    pg.wait_for_timeout(150)
    y1 = ghost_y(pg)
    leave = pg.evaluate("(e=>e?[getComputedStyle(e).transitionDuration,getComputedStyle(e).transitionTimingFunction,e.inert,e.classList.contains('sheet')]:null)(document.querySelector('#layer .pk-sheet.pk-leaving'))")
    ok(pg.evaluate(GHOSTS) == 1 and pg.evaluate("document.querySelectorAll('#layer .sheet').length") == 0,
       'mid-way, the closing sheet is still on screen, and nothing else is “the sheet” any more')
    ok(pg.evaluate("U.sheet") is None and pg.locator('#dock .tabbar').count() == 1, 'the app has already moved on: no sheet, the tab bar there')
    ok(leave and leave[0].split(',')[0] == '1.4s' and 'cubic-bezier(0.32, 0, 0.67, 0)' in leave[1] and leave[2] and not leave[3],
       f'it leaves in 350 ms × 4, speeding up (--ease-accel), and can’t be reached on its way ({leave})')
    ok(not pg.evaluate("document.body.classList.contains('sheet-open')") and pg.evaluate("getComputedStyle(document.querySelector('.wrap')).transitionDuration").startswith('1.4s'),
       'the page behind grows back on the same leave timing')
    ok(pg.locator('#layer .pk-dim:not(.pk-on)').count() == 1, 'and the dim fades away with it')
    pg.wait_for_timeout(450)
    y2 = ghost_y(pg)
    ok(y1 is not None and y2 is not None and y2 > y1 + 20, f'it really moves down ({y1} → {y2})')
    ok(pg.evaluate(UNIQUE_IDS), 'nothing is found twice on the way out')
    t.shot(pg, 'close-mid-light')
    settled(pg)
    ok(pg.evaluate(LEFT) == 0 and pg.locator('#layer .pk-sheet').count() == 0, 'afterwards nothing is left behind')

    # taps are never blocked mid-way: the row under the leaving sheet opens straight away
    pg.evaluate("document.querySelector('#spendList [data-k=a2]').scrollIntoView({block:'center'})")
    open_sheet(pg, "openSheet('purchase',{id:'a1'})")
    pg.click('#layer .sheet [data-a=close]')
    pg.wait_for_timeout(120)
    box = pg.locator('#spendList [data-a=openPurchase][data-k=a2]').bounding_box()
    hit = pg.evaluate("([x,y])=>{const e=document.elementFromPoint(x,y);return !!e&&!e.closest('#layer')}", [box['x'] + 40, box['y'] + box['height'] / 2])
    ok(hit, 'the sheet and dim on their way out never take a tap')
    pg.mouse.click(box['x'] + 40, box['y'] + box['height'] / 2)
    pg.wait_for_function("U.sheet==='purchase'&&U.sd.id==='a2'")
    ok(pg.evaluate(GHOSTS) == 1, 'tapping a row mid-way opens it while the last one finishes leaving')
    settled(pg)
    ok(pg.evaluate("document.querySelectorAll('#layer .sheet').length") == 1 and pg.evaluate(LEFT) == 0, 'then exactly one sheet is left')

    # every way of closing: Escape, the dim, a flick from the head, a drag from the content; a short drag stays
    pg.keyboard.press('Escape')
    pg.wait_for_timeout(100)
    ok(pg.evaluate(GHOSTS) == 1 and pg.evaluate("U.sheet") is None, 'Escape: it leaves')
    settled(pg)
    open_sheet(pg, "openSheet('purchase',{id:'a1'})")
    pg.mouse.click(200, 30)
    pg.wait_for_timeout(100)
    ok(pg.evaluate(GHOSTS) == 1 and pg.evaluate("U.sheet") is None, 'tapping the dim: it leaves')
    settled(pg)
    open_sheet(pg, "openSheet('purchase',{id:'a1'})")
    flick(pg, '#layer .sheet .shead h2')
    pg.wait_for_timeout(80)
    ok(pg.evaluate(GHOSTS) == 1 and pg.evaluate("U.sheet") is None, 'a flick down from its head (past 700 pt/s) closes it')
    settled(pg)
    open_sheet(pg, "openSheet('purchase',{id:'a1'})")
    flick(pg, '#layer .sheet .pk-sheet-body .grp')
    pg.wait_for_timeout(80)
    ok(pg.evaluate(GHOSTS) == 1 and pg.evaluate("U.sheet") is None, 'a flick down from its content, at the top, closes it too')
    settled(pg)
    open_sheet(pg, "openSheet('purchase',{id:'a1'})")
    drag(pg, '#layer .sheet .shead h2', (10, 20, 30, 40), pause=120)
    pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sheet") == 'purchase' and pg.evaluate(GHOSTS) == 0, 'a short, slow drag springs back and it stays open')
    settled(pg)
    pg.evaluate("ACT.delPurchase({dataset:{k:'a1'}})")
    pg.wait_for_timeout(300)
    al = pg.evaluate("(e=>e?[e.querySelector('.pk-alert-title').innerText,!!document.querySelector('#layer .sheet')]:null)(document.querySelector('#layer .pk-alert'))")
    ok(al is not None and al[0] == 'Delete this purchase?' and al[1], f'Delete asks in the kit’s alert, over the purchase sheet (D08: {al})')
    pg.click('#layer .pk-alert [data-a=no]')
    pg.wait_for_timeout(100)
    ok(pg.evaluate("U.sheet") == 'purchase' and pg.locator('#layer .pk-alert.pk-leaving').count() == 1, 'Cancel: the alert leaves and the purchase is still there')
    settled(pg)
    pg.evaluate("closeSheet()"); settled(pg)

    # going back to the sheet underneath: it never went (it waited, still open), and the top one leaves over it
    pg.set_viewport_size({'width': 390, 'height': 560})
    open_sheet(pg, "openSheet('purchase',{id:'a1'})")
    pg.evaluate(f"(e=>{{e.dataset.mark='1';e.querySelector('.pk-sheet-body').scrollTop=60}})({TOP})")
    top = pg.evaluate(f"{TOP}.querySelector('.pk-sheet-body').scrollTop")
    pg.evaluate("ACT.editPurchase({dataset:{k:'a1'}})")
    pg.wait_for_timeout(300)
    mid = pg.evaluate("(()=>{const u=document.querySelector('#layer .pk-sheet[data-mark]');return u?[u.classList.contains('sk-covered'),u.inert,getComputedStyle(u).translate]:null})()")
    ok(mid is not None and mid[0] and mid[1], f'Edit from a purchase rises over it; the purchase waits underneath, out of reach ({mid})')
    settled(pg)
    pg.click('#layer .sheet [data-a=close]')
    pg.wait_for_timeout(100)
    back = pg.evaluate(f"(e=>e?{{mark:e.dataset.mark||'',moving:{MOVING}(e),top:e.querySelector('.pk-sheet-body').scrollTop}}:null)({TOP})")
    ok(pg.evaluate("U.sheet") == 'purchase' and back and back['mark'] == '1' and not back['moving'], f'back to the purchase: the same sheet, simply there ({back})')
    ok(back and back['top'] == top, f'and scrolled where it was ({top} → {back and back["top"]})')
    ok(pg.evaluate(GHOSTS) == 1, 'the edit sheet leaves over it')
    ok(pg.evaluate("document.body.classList.contains('sheet-open')"), 'the page behind stays shrunk while a sheet is still open')
    settled(pg)

    # a second close mid-way still works: both go, and nothing is left
    pg.evaluate("ACT.editPurchase({dataset:{k:'a1'}})")
    pg.wait_for_timeout(200)
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(80); pg.evaluate("closeSheet()"); pg.wait_for_timeout(80)
    ok(pg.evaluate(GHOSTS) == 2 and pg.evaluate("U.sheet") is None, 'two quick closes: both sheets leave, and no sheet is left open')
    settled(pg)
    ok(pg.evaluate(LEFT) == 0 and pg.evaluate("document.querySelectorAll('#layer .pk-layer > *, #own > *').length") == 0, 'then nothing is left anywhere')
    pg.set_viewport_size({'width': 390, 'height': 844})

    # ── 2 · Saving: the Log sheet slides away and the new purchase settles into Spending ─────────────────
    # rows off screen deliberately don't move, so the list is scrolled into view first
    pg.evaluate("document.getElementById('spendList').scrollIntoView({block:'start'});window.scrollBy(0,-120)")
    pg.click('#barR [data-a=newPurchase]')
    pg.wait_for_function("U.sheet==='edit'")
    pg.fill('#edit-item', 'Halo-halo'); pg.fill('#edit-price', '120')
    pg.click('#layer .sheet .cta')
    pg.wait_for_timeout(60)
    new_id = pg.evaluate("D.purchases[0].id")
    a = pg.evaluate(f"(s=>({ANIMS})(document.querySelector(s)))", f'#spendList [data-k="{new_id}"]')
    a = a or pg.evaluate(f"(s=>({ANIMS})(document.querySelector(s)?.closest('.sw')))", f'#spendList [data-k="{new_id}"]')
    ok(pg.evaluate(GHOSTS) == 1, 'saving from the Log sheet: the sheet slides away')
    ok(len(a) == 1 and 'translateY(-12px)' in a[0][0]['t'] and a[0][0]['o'] == '0', f'the new purchase lands in the list (MOTION.land: a 12 px drop and a fade) ({a})')
    moving = pg.evaluate("[...document.querySelectorAll('#spendList .sw, #spendList > .grp > .row')].filter(e=>e.getAnimations().some(a=>a.playState==='running')).length")
    ok(moving >= 2, f'the rows below move to make room ({moving} moving)')
    t.shot(pg, 'save-mid-light')
    settled(pg)
    pg.wait_for_timeout(200)

    # ── 3 · Deleting: the row shrinks away, the rest close the gap; Undo plays the arrival again ─────────
    rows_before = pg.locator('#spendList [data-a=openPurchase]').evaluate_all("els=>els.map(e=>e.dataset.k)")
    victim = rows_before[1]
    pg.evaluate(f"ACT.delPurchase({{dataset:{{k:'{victim}'}}}})")
    pg.wait_for_function("U.sheet==='confirm'"); pg.wait_for_timeout(1200)
    pg.click('#layer .pk-alert [data-a=yes]')
    pg.wait_for_timeout(60)
    ok(pg.evaluate("document.querySelectorAll('#leaving .rowghost').length") == 1, 'the deleted row fades and shrinks where it was')
    a = anims(pg, '#leaving .rowghost')
    ok(len(a) == 1 and 'scale(0.94)' in a[0][-1]['t'] and a[0][-1]['o'] == '0', f'it shrinks to .94 as it fades ({a})')
    nxt = rows_before[2]
    # it moves itself, or with its day's group when that whole group moves up
    a = pg.evaluate(f"(s=>{{const r=document.querySelector(s);const h=r.closest('.sw')||r;const f={ANIMS};return f(h).concat(f(h.closest('.grp')))}})", f'#spendList [data-k="{nxt}"]')
    ok(len(a) >= 1 and 'translateY(' in a[0][0]['t'], 'the row below glides up into the gap')
    ok(pg.evaluate("!document.elementFromPoint(200,400)?.closest('#leaving')"), 'and the copy never takes a tap')
    t.shot(pg, 'delete-mid-light')
    settled(pg)
    pg.wait_for_function("!document.querySelector('.rowghost')", timeout=6000)
    ok(True, 'the copy goes once it has faded')
    pg.click('.toast button')
    pg.wait_for_timeout(60)
    a = pg.evaluate(f"(s=>({ANIMS})(document.querySelector(s)?.closest('.sw')||document.querySelector(s)))", f'#spendList [data-k="{victim}"]')
    ok(len(a) == 1 and 'translateY(-12px)' in a[0][0]['t'], 'Undo: the row settles back in, the same way a new one arrives')
    pg.context.close()

    # ── 4 · Home: Save confirms where you tapped, the new row settles in, and Undo removes it again ───────
    pg = t.page(b, touch=True, init=SLOW)
    pg.evaluate("F.home={item:'Turon',price:'20',category:'Food & drink'};rerender();window.scrollTo(0,document.body.scrollHeight)")
    pg.wait_for_timeout(100)
    last = pg.evaluate("[...document.querySelectorAll('#app .row[data-a=openPurchase]')].pop().dataset.k")
    pg.click('#homeSave')
    pg.wait_for_timeout(60)
    btn = pg.locator('#homeSave')
    ok(btn.inner_text().strip() == 'Saved' and btn.locator('svg').count() == 1, 'the button itself says “✓ Saved”')
    new_id = pg.evaluate("D.purchases[0].id")
    a = pg.evaluate(f"(s=>({ANIMS})(document.querySelector(s)))", f'#app [data-k="{new_id}"]')
    ok(len(a) == 1 and 'translateY(-12px)' in a[0][0]['t'], 'the purchase settles into Recent')
    ok(pg.evaluate(f"!document.querySelector('#app [data-k=\"{last}\"]')") and pg.evaluate("document.querySelectorAll('#leaving .rowghost').length") == 1,
       'the row pushed out of Recent fades away where it was')
    t.shot(pg, 'home-save-mid-light')
    ok(pg.locator('.toast button').inner_text() == 'Undo', '“Purchase saved” offers Undo')
    pg.wait_for_timeout(1500)
    pg.click('.toast button')
    pg.wait_for_timeout(60)
    ok(not pg.evaluate(f"D.purchases.some(p=>p.id==='{new_id}')") and pg.locator('.toast:not(.pk-leaving)').first.inner_text().startswith('Purchase removed'), 'Undo removes it again')
    ok(pg.evaluate("document.querySelectorAll('#leaving .rowghost').length") >= 1, 'and it shrinks out of Recent')
    pg.wait_for_function("document.getElementById('homeSave').innerText.trim()==='Save purchase'", timeout=9000)
    ok(True, 'the button goes back to Save purchase (after 1.4 s, × 4 in slow motion)')
    pg.wait_for_timeout(400)
    stored = pg.evaluate(READ, 'purchases')
    ok(stored is not None and not any(p['id'] == new_id for p in stored), 'and it’s gone from what’s saved')

    # logging on a calendar day: back to the calendar, simply there, with the new row settling into that day
    settled(pg)
    pg.evaluate("U.calM=localISO().slice(0,8)+'01';U.calD=localISO();openSheet('calendar')")
    pg.wait_for_timeout(2600)
    pg.click('#layer .sheet [data-a=newPurchase]')
    pg.wait_for_function("U.sheet==='edit'"); pg.wait_for_timeout(2600)
    pg.fill('#edit-item', 'Taho'); pg.fill('#edit-price', '25')
    pg.click('#layer .sheet .cta')
    pg.wait_for_timeout(60)
    tid = pg.evaluate("D.purchases[0].id")
    cal = pg.evaluate(f"(s=>({{still:!s.classList.contains('pk-leaving'),moving:{MOVING}(s)}}))({TOP})")
    a = pg.evaluate(f"(s=>({ANIMS})(document.querySelector(s)))", f'#layer [data-k="{tid}"]')
    ok(pg.evaluate("U.sheet") == 'calendar' and cal['still'] and not cal['moving'], 'saving on a calendar day goes back to the calendar, simply there')
    ok(len(a) == 1 and 'translateY(-12px)' in a[0][0]['t'], 'and the purchase settles into that day’s list')
    others = pg.evaluate(f"[...document.querySelectorAll('#layer .row[data-a=openPurchase]')].filter(e=>e.dataset.k!=='{tid}'&&e.getAnimations().some(a=>a.effect.getKeyframes()[0].opacity===0)).length")
    ok(others == 0, 'the rows already there don’t settle in again')
    pg.context.close()

    # Save's tick doesn't depend on motion: with motion off it still shows, then goes back
    pg = t.page(b)
    pg.fill('#home-item', 'Buko'); pg.fill('#home-price', '40'); pg.click('#homeSave')
    ok(pg.locator('#homeSave').inner_text().strip() == 'Saved', 'with motion off, Save still says Saved')
    ok(pg.evaluate(LEFT) == 0 and pg.evaluate("[...document.querySelectorAll('#app .row')].every(e=>!e.getAnimations().length)"), 'but nothing moves')
    pg.wait_for_function("document.getElementById('homeSave').innerText.trim()==='Save purchase'", timeout=4000)
    ok(True, 'and goes back after about 1.4 s')
    pg.evaluate("openSheet('purchase',{id:'a1'})"); pg.evaluate("closeSheet()")
    ok(pg.evaluate(LEFT) == 0 and pg.locator('#layer .pk-sheet').count() == 0, 'with motion off, a sheet simply goes')
    ok(pg.evaluate("getComputedStyle(document.querySelector('.wrap')).transitionDuration").startswith('0s'), 'and the page behind doesn’t animate')
    pg.context.close()

    # ── 5 · iPad: a sheet shrinks to .94 and fades ───────────────────────────────────────────────────────
    pg = t.page(b, w=820, h=1180, touch=True, init=SLOW)
    open_sheet(pg, "openSheet('purchase',{id:'a1'})")
    pg.click('#layer .sheet [data-a=close]')
    pg.wait_for_timeout(60)
    a = anims(pg, '#leaving .sheet')
    ok(len(a) == 1 and 'scale(0.94)' in a[0][-1]['t'] and a[0][-1]['o'] == '0', f'iPad: Suki’s own centred sheet (S01) shrinks to .94 and fades ({a})')
    dur = pg.evaluate("document.querySelector('#leaving .sheet').getAnimations()[0].effect.getTiming().duration")
    ok(dur == 680, f'over --dur-close, 170 ms (× 4 in slow motion: {dur})')
    ok(pg.locator('#layer .pk-sheet').count() == 0 and pg.evaluate("getComputedStyle(document.querySelector('#leaving .sheet')).borderTopLeftRadius") == '28px', 'it isn’t the kit’s sheet, and keeps its 28 corners (--r-form)')
    settled(pg)
    ok(pg.evaluate(LEFT) == 0, 'and nothing is left')
    pg.context.close()

    # ── 6 · Reduce Motion: only fades ────────────────────────────────────────────────────────────────────
    pg = t.page(b, touch=True, init=ON, ctx_args={'reduced_motion': 'reduce'})
    pg.evaluate("go('spending')")
    open_sheet(pg, "openSheet('purchase',{id:'a1'})")
    pg.click('#layer .sheet [data-a=close]')
    pg.wait_for_timeout(30)
    rm = pg.evaluate("(e=>e?[getComputedStyle(e).opacity,getComputedStyle(e).transitionProperty,getComputedStyle(e).transitionDuration,getComputedStyle(e).translate]:null)(document.querySelector('#layer .pk-sheet.pk-leaving'))")
    ok(rm is not None and 'opacity' in rm[1] and 'translate' not in rm[1] and rm[3] in ('none', '0px', '0px 0px'),
       f'Reduce Motion: a closing sheet only fades, where it is ({rm})')
    ok(rm is not None and set(x.strip() for x in rm[2].split(',')) == {'0.1s'}, f'over the kit’s 100 ms (D20: {rm and rm[2]})')
    settled(pg)
    pg.evaluate("document.getElementById('spendList').scrollIntoView({block:'start'});window.scrollBy(0,-120)")
    pg.click('#barR [data-a=newPurchase]'); pg.wait_for_function("U.sheet==='edit'")
    pg.fill('#edit-item', 'Lumpia'); pg.fill('#edit-price', '35'); pg.click('#layer .sheet .cta')
    pg.wait_for_timeout(20)
    nid = pg.evaluate("D.purchases[0].id")
    a = pg.evaluate(f"(s=>({ANIMS})(document.querySelector(s)?.closest('.sw')||document.querySelector(s)))", f'#spendList [data-k="{nid}"]')
    ok(len(a) == 1 and a[0][0]['o'] == '0' and not any(k['t'] for k in a[0]), f'a new row only fades in ({a})')
    d = pg.evaluate(f"(s=>{{const e=document.querySelector(s);const h=e&&(e.closest('.sw')||e);const a=h&&h.getAnimations()[0];return a?a.effect.getTiming().duration:null}})", f'#spendList [data-k="{nid}"]')
    ok(d == 100, f'over the kit’s 100 ms ({d})')
    moved = pg.evaluate("[...document.querySelectorAll('#spendList .sw')].filter(e=>e.getAnimations().some(a=>a.effect.getKeyframes().some(k=>k.transform))).length")
    ok(moved == 0, 'and nothing slides')
    settled(pg)
    pg.wait_for_timeout(300)
    pg.evaluate(f"ACT.delPurchase({{dataset:{{k:'{nid}'}}}})"); pg.wait_for_function("U.sheet==='confirm'"); pg.wait_for_timeout(300)
    pg.click('#layer .pk-alert [data-a=yes]'); pg.wait_for_timeout(20)
    a = anims(pg, '#leaving .rowghost')
    ok(len(a) == 1 and not any(k['t'] for k in a[0]), 'a deleted row only fades out')
    pg.context.close()

    # ── 7 · Kept still: tabs switch instantly, and Settings and Convert don't move (Settings opened from another tab;
    #      from Home's gear it's pushed since Q24, section 8) ──────────────────────────────────────────────────────
    pg = t.page(b, touch=True, init=ON)
    for tab in ['till', 'convert', 'settings', 'spending']:
        pg.evaluate(f"go('{tab}')")
        n = pg.evaluate("document.getAnimations().filter(a=>a.playState==='running'&&a.effect&&a.effect.target&&document.getElementById('app').contains(a.effect.target)).length")
        ok(n == 0, f'switching to {tab} moves nothing')
    pg.context.close()

    # ── 8 · Door rules (Q24): pushes over a still page, pops, and a sheet over a sheet keeping its dim ────────────
    WRAPX = "(()=>{const m=new DOMMatrix(getComputedStyle(document.querySelector('body > .wrap')).transform);return m.m41})()"
    STILLX = "(s=>{const e=document.querySelector(s+' > .wrap');return e?new DOMMatrix(getComputedStyle(e).transform).m41:null})"
    DIMO = "(s=>{const e=document.querySelector(s+' .pdim');return e?+getComputedStyle(e).opacity:null})"
    GONE = "!document.querySelector('#under,#over')&&!document.body.classList.contains('pushing')"
    pg = t.page(b, touch=True, init=SLOW)
    pg.wait_for_timeout(300)
    pg.click('#barR [aria-label=Settings]'); pg.wait_for_timeout(500)
    ux, wx, d = pg.evaluate(STILLX + "('#under')"), pg.evaluate(WRAPX), pg.evaluate(DIMO + "('#under')")
    ok(pg.evaluate("U.tab") == 'settings' and pg.locator('#under').count() == 1 and pg.evaluate("document.body.classList.contains('pushing')"),
       'the gear: Settings slides in over a still copy of Home')
    ok(pg.locator('#under [id], #under [data-a]').count() == 0 and 'recent' in pg.inner_text('#under').lower(), 'the copy is Home, with no ids or actions')
    ok(wx > 0 and ux is not None and ux < 0 and d is not None and 0 < d <= 0.1001, f'mid-way: Settings is coming in ({wx:.0f}), Home is moving left ({ux:.0f}) and dimming ({d})')
    pg.wait_for_function(GONE, timeout=8000)
    ok(pg.evaluate(WRAPX) == 0, 'once it lands, the copy goes and Settings sits in place')
    t.shot(pg, 'q24-settings-landed')
    pg.click('#barL [aria-label="Back to Home"]'); pg.wait_for_timeout(500)
    ox, wx, d = pg.evaluate(STILLX + "('#over')"), pg.evaluate(WRAPX), pg.evaluate(DIMO + "('#over')")
    ok(pg.evaluate("U.tab") == 'home' and pg.locator('#over').count() == 1 and 'Settings' in pg.inner_text('#over'), 'Back: a still copy of Settings lies over Home')
    ok(ox is not None and ox > 0 and wx < 0 and d is not None and 0 < d < 0.1001, f'mid-way: Settings is leaving right ({ox:.0f}), Home coming from the left ({wx:.0f}) under the dim ({d})')
    pg.wait_for_function(GONE, timeout=8000)
    ok(pg.evaluate(WRAPX) == 0, 'and once it lands, nothing is left')
    # Help from Settings and back, and Rate history from Convert, move the same way
    pg.evaluate("go('settings')"); pg.wait_for_function(GONE, timeout=8000)
    pg.click('#app [data-a=openHelp]'); pg.wait_for_timeout(400)
    ok(pg.locator('#under').count() == 1 and 'Settings' in pg.inner_text('#under') and pg.evaluate(WRAPX) > 0, 'Help slides in over Settings')
    pg.wait_for_function(GONE, timeout=8000)
    pg.click('#barL [aria-label="Back to Settings"]'); pg.wait_for_timeout(400)
    ok(pg.locator('#over').count() == 1 and pg.evaluate(WRAPX) < 0, 'Back from Help: Settings comes from under it')
    pg.wait_for_function(GONE, timeout=8000)
    pg.evaluate("go('convert')"); pg.wait_for_timeout(200)
    pg.click('[data-a=openHistory]'); pg.wait_for_timeout(400)
    ok(pg.locator('#under').count() == 1 and pg.evaluate(STILLX + "('#under')") < 0, 'Rate history slides in over Convert, the same')
    pg.wait_for_function(GONE, timeout=8000)
    # interrupting: Back mid-push leaves one copy at most, and none once it lands
    pg.evaluate("go('home')"); pg.wait_for_function(GONE, timeout=8000)
    pg.click('#barR [aria-label=Settings]'); pg.wait_for_timeout(250)
    pg.click('#barL [aria-label="Back to Home"]'); pg.wait_for_timeout(100)
    ok(pg.locator('#under, #over').count() == 1, 'Back mid-push: only one still copy at a time')
    pg.wait_for_function(GONE, timeout=8000)
    ok(pg.evaluate("U.tab") == 'home' and pg.evaluate(WRAPX) == 0, 'and nothing is left once it lands')
    # tabs and the tab bar still switch at once
    pg.click('#dock [data-v=spending]'); pg.wait_for_timeout(30)
    ok(pg.locator('#under, #over').count() == 0, 'a tab switches with no push')
    pg.context.close()

    # Reduce Motion: a short fade, no still copy
    pg = t.page(b, touch=True, init=ON + ";localStorage.setItem('suki:reduceMotion','on')")
    pg.wait_for_timeout(300)
    pg.click('#barR [aria-label=Settings]'); pg.wait_for_timeout(30)
    a = anims(pg, '#app')
    ok(pg.locator('#under, #over').count() == 0 and a and all(not k['t'] for k in a[0]), 'Reduce Motion: the gear fades Settings in, with nothing sliding')
    pg.context.close()

    # a sheet over a sheet (Q24, on the kit since Q27): the first stays, dimmed, and the new one rises over it
    SAMPLE = """()=>{window.DIMS=[];window.UNDER=[];const t0=performance.now();const f=()=>{const d=document.querySelector('#layer .pk-dim');DIMS.push(d?+getComputedStyle(d).opacity:0);const u=document.querySelector('#layer .pk-sheet.sk-covered:not(.pk-leaving)');UNDER.push(!!u);if(performance.now()-t0<3300)requestAnimationFrame(f)};requestAnimationFrame(f)}"""
    for sc in ['light', 'dark']:
        pg = t.page(b, sc=sc, touch=True, init=SLOW)
        pg.evaluate("go('spending')")
        open_sheet(pg, "openSheet('purchase',{id:'a1'})")
        pg.evaluate(SAMPLE)
        pg.click('#layer .sheet [data-a=editPurchase]')
        pg.wait_for_timeout(700)
        t.shot(pg, f'q24-sheet-over-{sc}')
        pg.wait_for_timeout(2800)
        dims, under = pg.evaluate("DIMS"), pg.evaluate("UNDER")
        ok(pg.evaluate("U.sheet") == 'edit' and min(dims) >= 0.99, f'{sc}: Edit from a purchase never shows the page undimmed (the first dim stays on: lowest {min(dims):.3f})')
        i = under.index(True) if True in under else len(under)
        ok(i < len(under) and all(under[i:]), f'{sc}: once covered, the purchase sheet stays underneath, all the way ({sum(under)} of {len(under)} frames)')
        ok(pg.locator('#layer .pk-sheet').count() == 2 and pg.locator('#layer .pk-dim.pk-on').count() == 2, f'{sc}: two sheets, each with its dim (the kit’s stacking)')
        pg.context.close()
    # the other doors of the same shape: item › Log what you paid, Delete from a sheet (now an alert over it)
    pg = t.page(b, touch=True, init=SLOW)
    open_sheet(pg, "openSheet('item',{id:'jeepney'})")
    pg.evaluate(SAMPLE); pg.click('#layer .sheet [data-a=logItem]'); pg.wait_for_timeout(3400)
    u = pg.evaluate("UNDER"); i = u.index(True) if True in u else len(u)
    ok(pg.evaluate("U.sheet") == 'edit' and min(pg.evaluate("DIMS")) >= 0.99 and i < len(u) and all(u[i:]), 'item › Log what you paid: over the item sheet, which stays')
    pg.evaluate("U.stack=[];U.sheet=null;rerender()"); settled(pg)
    open_sheet(pg, "openSheet('purchase',{id:'a1'})")
    pg.evaluate("ACT.delPurchase({dataset:{k:'a1'}})"); pg.wait_for_timeout(1500)
    ok(pg.evaluate("U.sheet") == 'confirm' and pg.locator('#layer .pk-alert').count() == 1 and pg.locator('#layer .sheet').count() == 1, 'Delete from a purchase: the alert over it, the purchase still there')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(1800)
    ok(pg.evaluate("U.sheet") == 'purchase' and pg.locator('#layer .pk-alert').count() == 0, 'and going back leaves the purchase as it was')
    pg.context.close()

    # ── 9 · Frames in dark mode, at 4× slow motion ───────────────────────────────────────────────────────
    pg = t.page(b, sc='dark', touch=True, init=SLOW)
    pg.evaluate("go('spending')")
    open_sheet(pg, "openSheet('purchase',{id:'a1'})")
    pg.click('#layer .sheet [data-a=close]')
    pg.wait_for_timeout(400)
    t.shot(pg, 'close-mid-dark')
    settled(pg)
    pg.evaluate("ACT.delPurchase({dataset:{k:'a2'}})"); pg.wait_for_function("U.sheet==='confirm'"); pg.wait_for_timeout(1200)
    t.shot(pg, 'alert-dark')
    pg.click('#layer .pk-alert [data-a=yes]'); pg.wait_for_timeout(300)
    t.shot(pg, 'delete-mid-dark')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'no sideways scroll while things move')
    pg.context.close()
