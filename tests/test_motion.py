"""Things arrive and leave (Q11), with motion switched on: a closing sheet slides down (or shrinks on iPad, or fades with
Reduce Motion) and is still on screen mid-way, then gone with no stray copies, by every way of closing it; going back to
a sheet underneath finds it simply there; a saved purchase settles into its list while the rows below move; a deleted
row shrinks away and Undo brings it back the same way; Home's Save button says "Saved"; "Purchase saved" has Undo;
Slow motion slows the page behind too. Frames at 4× slow motion, light and dark, go to tests/output."""
from harness import READ

SLOW = "localStorage.setItem('suki:motion','4')"
ON = "localStorage.setItem('suki:motion','1')"

# a finger on a sheet's header, dragging it down
DRAG = """(a)=>{const [type,y]=a;const h=document.querySelector('#layer .sheet .shead h2');const t=new Touch({identifier:1,target:h,clientX:200,clientY:y});
  const e=new TouchEvent(type,{touches:type==='touchend'?[]:[t],changedTouches:[t],bubbles:true,cancelable:true});h.dispatchEvent(e);return true}"""
# every running animation on an element, as [keyframes] (offsets dropped)
ANIMS = """(e)=>e?e.getAnimations().filter(a=>a.playState==='running').map(a=>a.effect.getKeyframes().map(k=>({t:k.transform||'',o:k.opacity===undefined?'':String(k.opacity),bg:k.backgroundColor||''}))):[]"""
GHOSTS = "document.querySelectorAll('#leaving .sheet').length"
LEFT = "document.querySelectorAll('#leaving > *').length"
UNIQUE_IDS = "(()=>{const s=[...document.querySelectorAll('[id]')].map(e=>e.id);return s.length===new Set(s).size})()"


def settled(pg):
    """Wait until nothing in the layer or #leaving is still moving."""
    pg.wait_for_function("!document.querySelector('#leaving > *')&&!document.body.classList.contains('unsheet')&&!document.querySelector('#layer .sheet')?.getAnimations().some(a=>a.playState==='running')", timeout=8000)


def open_sheet(pg, js):
    pg.evaluate(js)
    pg.wait_for_function("!!document.querySelector('#layer .sheet')&&!document.querySelector('#layer .sheet').getAnimations().some(a=>a.playState==='running')", timeout=8000)


def ghost_y(pg):
    return pg.evaluate("(()=>{const s=document.querySelector('#leaving .sheet');return s?s.getBoundingClientRect().top:null})()")


def anims(pg, sel):
    return pg.evaluate(f"(s=>({ANIMS})(document.querySelector(s)))", sel)


def run(b, t):
    ok = t.ok

    # ── 1 · Closing a sheet slides it down while the page grows back (iPhone, 4× slow motion) ──────────────
    pg = t.page(b, touch=True, init=SLOW)
    pg.evaluate("go('spending')")
    ok(pg.evaluate("getComputedStyle(document.querySelector('.wrap')).transitionDuration").startswith('1.8s'),
       'Slow motion slows the page behind a sheet too (0.45 s × 4)')
    open_sheet(pg, "openSheet('purchase',{id:'a1'})")
    ok(pg.evaluate("document.body.classList.contains('sheet-open')"), 'with a sheet open, the page behind is shrunk')
    pg.click('#layer .sheet [data-a=close]')
    pg.wait_for_timeout(150)
    y1 = ghost_y(pg)
    ok(pg.evaluate(GHOSTS) == 1 and pg.evaluate("document.querySelectorAll('#layer .sheet').length") == 0,
       'mid-way, the closing sheet is still on screen (in #leaving), and the layer is already free')
    ok(pg.evaluate("U.sheet") is None and pg.locator('#dock .tabbar').count() == 1, 'the app has already moved on: no sheet, and the tab bar is back')
    ok(pg.evaluate("document.body.classList.contains('unsheet')") and pg.evaluate("getComputedStyle(document.querySelector('.wrap')).transitionDuration").startswith('1.32s'),
       'the page behind grows back on the quicker curve (0.33 s × 4)')
    a = anims(pg, '#leaving .sheet')
    ok(len(a) == 1 and 'translateY(115%)' in a[0][-1]['t'], f'the sheet slides down off the screen ({a[:1]})')
    a = anims(pg, '#leaving .scrim')
    ok(len(a) == 1 and a[0][-1]['bg'] in ('rgba(0, 0, 0, 0)', 'rgba(0,0,0,0)'), 'and the dim fades away with it')
    pg.wait_for_timeout(450)
    y2 = ghost_y(pg)
    ok(y1 is not None and y2 is not None and y2 > y1 + 20, f'it really moves down ({y1} → {y2})')
    ok(pg.evaluate(UNIQUE_IDS), 'the copy on its way out has no ids, so nothing is found twice')
    t.shot(pg, 'close-mid-light')
    settled(pg)
    ok(pg.evaluate(LEFT) == 0 and not pg.evaluate("document.body.classList.contains('unsheet')"), 'afterwards nothing is left behind')

    # taps are never blocked mid-way: the row under the leaving sheet opens straight away
    pg.evaluate("document.querySelector('#spendList [data-k=a2]').scrollIntoView({block:'center'})")
    open_sheet(pg, "openSheet('purchase',{id:'a1'})")
    pg.click('#layer .sheet [data-a=close]')
    pg.wait_for_timeout(120)
    box = pg.locator('#spendList [data-a=openPurchase][data-k=a2]').bounding_box()
    hit = pg.evaluate("([x,y])=>{const e=document.elementFromPoint(x,y);return !!e&&!e.closest('#leaving')}", [box['x'] + 40, box['y'] + box['height'] / 2])
    ok(hit, 'the sheet on its way out never takes a tap')
    pg.mouse.click(box['x'] + 40, box['y'] + box['height'] / 2)
    pg.wait_for_function("U.sheet==='purchase'&&U.sd.id==='a2'")
    ok(pg.evaluate(GHOSTS) == 1, 'tapping a row mid-way opens it while the last one finishes leaving')
    settled(pg)
    ok(pg.evaluate("document.querySelectorAll('#layer .sheet').length") == 1 and pg.evaluate(LEFT) == 0, 'then exactly one sheet is left')

    # every way of closing: Escape, the dim, Cancel, dragging it down
    pg.keyboard.press('Escape')
    pg.wait_for_timeout(100)
    ok(pg.evaluate(GHOSTS) == 1 and pg.evaluate("U.sheet") is None, 'Escape: it slides away')
    settled(pg)
    open_sheet(pg, "openSheet('purchase',{id:'a1'})")
    pg.mouse.click(200, 30)
    pg.wait_for_timeout(100)
    ok(pg.evaluate(GHOSTS) == 1 and pg.evaluate("U.sheet") is None, 'tapping the dim: it slides away')
    settled(pg)
    open_sheet(pg, "ACT.delPurchase({dataset:{k:'a1'}})")
    pg.click('#layer .sheet .ghost[data-a=close]')
    pg.wait_for_timeout(100)
    ok(pg.evaluate(GHOSTS) == 1 and pg.evaluate("U.sheet") is None, 'Cancel: it slides away')
    settled(pg)
    open_sheet(pg, "openSheet('purchase',{id:'a1'})")
    y0 = pg.evaluate("document.querySelector('#layer .sheet .shead h2').getBoundingClientRect().top")
    pg.evaluate(DRAG, ['touchstart', y0])
    for i in range(1, 11): pg.evaluate(DRAG, ['touchmove', y0 + 15 * i])
    pg.evaluate(DRAG, ['touchend', y0 + 150])
    pg.wait_for_timeout(60)
    a = anims(pg, '#leaving .sheet')
    ok(pg.evaluate(GHOSTS) == 1 and pg.evaluate("U.sheet") is None and len(a) == 1 and 'matrix' in a[0][0]['t'],
       'dragging it down: it lets go and carries on from where the finger left it')
    settled(pg)
    open_sheet(pg, "openSheet('purchase',{id:'a1'})")
    y0 = pg.evaluate("document.querySelector('#layer .sheet .shead h2').getBoundingClientRect().top")
    pg.evaluate(DRAG, ['touchstart', y0]); pg.evaluate(DRAG, ['touchmove', y0 + 40]); pg.evaluate(DRAG, ['touchend', y0 + 40])
    pg.wait_for_timeout(100)
    ok(pg.evaluate("U.sheet") == 'purchase' and pg.evaluate(GHOSTS) == 0, 'a short drag still springs back and stays open')
    pg.evaluate("closeSheet()"); settled(pg)

    # going back to the sheet underneath: it's simply there (no second rise), and the top one slides off over it
    pg.set_viewport_size({'width': 390, 'height': 560})
    open_sheet(pg, "openSheet('purchase',{id:'a1'})")
    pg.evaluate("document.querySelector('#layer .sheet').scrollTop=60")
    top = pg.evaluate("document.querySelector('#layer .sheet').scrollTop")
    open_sheet(pg, "ACT.editPurchase({dataset:{k:'a1'}})")
    pg.click('#layer .sheet [data-a=close]')
    pg.wait_for_timeout(100)
    under = pg.evaluate("(()=>{const s=document.querySelector('#layer .sheet');return {still:s.classList.contains('still'),moving:s.getAnimations().some(a=>a.playState==='running'),top:s.scrollTop}})()")
    ok(pg.evaluate("U.sheet") == 'purchase' and under['still'] and not under['moving'], 'back to the purchase: it is simply there, with no second rise')
    ok(under['top'] == top, f'and scrolled where it was ({top} → {under["top"]})')
    ok(pg.evaluate(GHOSTS) == 1 and pg.evaluate("getComputedStyle(document.querySelector('#leaving .scrim')).backgroundColor") in ('rgba(0, 0, 0, 0)', 'transparent'),
       'the edit sheet slides off over it without a second dim')
    ok(pg.evaluate("getComputedStyle(document.querySelector('#leaving .scrim')).zIndex") == '41', 'the leaving sheet sits above the one underneath')
    ok(pg.evaluate("document.body.classList.contains('sheet-open')"), 'the page behind stays shrunk while a sheet is still open')
    settled(pg)

    # a second close mid-way still works: both go, and nothing is left
    pg.evaluate("ACT.editPurchase({dataset:{k:'a1'}})")
    pg.wait_for_timeout(200)
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(80); pg.evaluate("closeSheet()"); pg.wait_for_timeout(80)
    ok(pg.evaluate(GHOSTS) == 2 and pg.evaluate("U.sheet") is None, 'two quick closes: both sheets leave, and no sheet is left open')
    settled(pg)
    ok(pg.evaluate(LEFT) == 0 and pg.evaluate("document.querySelectorAll('#layer *').length") == 0, 'then nothing is left anywhere')
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
    ok(len(a) == 1 and 'translateY(-12px)' in a[0][0]['t'] and a[0][0]['o'] == '0', f'the new purchase settles into the list (a 12 px drop and a fade) ({a})')
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
    pg.click('#layer .sheet .cta.red')
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
    ok(not pg.evaluate(f"D.purchases.some(p=>p.id==='{new_id}')") and pg.locator('.toast').first.inner_text().startswith('Purchase removed'), 'Undo removes it again')
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
    cal = pg.evaluate("(()=>{const s=document.querySelector('#layer .sheet');return {still:s.classList.contains('still'),moving:s.getAnimations().some(a=>a.playState==='running')}})()")
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
    ok(pg.evaluate(LEFT) == 0, 'with motion off, a sheet simply goes')
    ok(pg.evaluate("getComputedStyle(document.querySelector('.wrap')).transitionDuration").startswith('0s'), 'and the page behind doesn’t animate')
    pg.context.close()

    # ── 5 · iPad: a sheet shrinks to .94 and fades ───────────────────────────────────────────────────────
    pg = t.page(b, w=820, h=1180, touch=True, init=SLOW)
    open_sheet(pg, "openSheet('purchase',{id:'a1'})")
    pg.click('#layer .sheet [data-a=close]')
    pg.wait_for_timeout(60)
    a = anims(pg, '#leaving .sheet')
    ok(len(a) == 1 and 'scale(0.94)' in a[0][-1]['t'] and a[0][-1]['o'] == '0', f'iPad: the sheet shrinks to .94 and fades ({a})')
    dur = pg.evaluate("document.querySelector('#leaving .sheet').getAnimations()[0].effect.getTiming().duration")
    ok(dur == 880, f'in 220 ms (× 4 in slow motion: {dur})')
    settled(pg)
    ok(pg.evaluate(LEFT) == 0, 'and nothing is left')
    pg.context.close()

    # ── 6 · Reduce Motion: only fades ────────────────────────────────────────────────────────────────────
    pg = t.page(b, touch=True, init=ON, ctx_args={'reduced_motion': 'reduce'})
    pg.evaluate("go('spending')")
    open_sheet(pg, "openSheet('purchase',{id:'a1'})")
    pg.click('#layer .sheet [data-a=close]')
    pg.wait_for_timeout(30)
    a_sc, a_sh = anims(pg, '#leaving .scrim'), anims(pg, '#leaving .sheet')
    ok(len(a_sc) == 1 and a_sc[0][-1]['o'] == '0' and not any(k['t'] for k in a_sc[0]) and not a_sh,
       'Reduce Motion: a closing sheet only fades')
    dur = pg.evaluate("document.querySelector('#leaving .scrim')?.getAnimations()[0]?.effect.getTiming().duration")
    ok(dur == 200, f'over 200 ms ({dur})')
    settled(pg)
    pg.evaluate("document.getElementById('spendList').scrollIntoView({block:'start'});window.scrollBy(0,-120)")
    pg.click('#barR [data-a=newPurchase]'); pg.wait_for_function("U.sheet==='edit'")
    pg.fill('#edit-item', 'Lumpia'); pg.fill('#edit-price', '35'); pg.click('#layer .sheet .cta')
    pg.wait_for_timeout(20)
    nid = pg.evaluate("D.purchases[0].id")
    a = pg.evaluate(f"(s=>({ANIMS})(document.querySelector(s)?.closest('.sw')||document.querySelector(s)))", f'#spendList [data-k="{nid}"]')
    ok(len(a) == 1 and a[0][0]['o'] == '0' and not any(k['t'] for k in a[0]), f'a new row only fades in ({a})')
    moved = pg.evaluate("[...document.querySelectorAll('#spendList .sw')].filter(e=>e.getAnimations().some(a=>a.effect.getKeyframes().some(k=>k.transform))).length")
    ok(moved == 0, 'and nothing slides')
    settled(pg)
    pg.wait_for_timeout(300)
    pg.evaluate(f"ACT.delPurchase({{dataset:{{k:'{nid}'}}}})"); pg.wait_for_function("U.sheet==='confirm'"); pg.wait_for_timeout(300)
    pg.click('#layer .sheet .cta.red'); pg.wait_for_timeout(20)
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

    # a sheet over a sheet keeps the dim at 4×, and the old sheet waits behind until it's covered
    SAMPLE = """()=>{window.DIMS=[];window.UNDER=[];const t0=performance.now();const f=()=>{let m=0;document.querySelectorAll('#layer .scrim, #leaving .scrim').forEach(s=>{const c=getComputedStyle(s).backgroundColor,p=c.match(/[\\d.]+/g)||[];const al=c==='transparent'?0:p.length>3?+p[3]:1;m=Math.max(m,al*+getComputedStyle(s).opacity)});DIMS.push(m);UNDER.push(!!document.querySelector('#leaving .scrim.under .sheet'));if(performance.now()-t0<3300)requestAnimationFrame(f)};requestAnimationFrame(f)}"""
    for sc in ['light', 'dark']:
        pg = t.page(b, sc=sc, touch=True, init=SLOW)
        pg.evaluate("go('spending')")
        open_sheet(pg, "openSheet('purchase',{id:'a1'})")
        pg.evaluate(SAMPLE.replace('t0<3300', 't0<200')); pg.wait_for_timeout(300)
        base = min(pg.evaluate("DIMS"))
        pg.evaluate(SAMPLE)
        pg.click('#layer .sheet [data-a=editPurchase]')
        pg.wait_for_timeout(700)
        t.shot(pg, f'q24-sheet-over-{sc}')
        pg.wait_for_timeout(2800)
        dims, under = pg.evaluate("DIMS"), pg.evaluate("UNDER")
        ok(pg.evaluate("U.sheet") == 'edit' and base > 0 and min(dims) >= base * 0.97, f'{sc}: Edit from a purchase never shows the page undimmed (lowest {min(dims):.3f}, before {base:.3f})')
        ok(max(dims) <= base * 1.03, f'{sc}: and the dim is never doubled (highest {max(dims):.3f})')
        ok(any(under) and not under[-1], f'{sc}: the purchase sheet waits behind it until covered, then goes ({sum(under)} of {len(under)} frames)')
        ok(pg.evaluate("getComputedStyle(document.querySelector('#layer .scrim')).animationName") == 'none', f'{sc}: the dim doesn’t fade in again')
        pg.context.close()
    # the other doors of the same shape: item › Log what you paid, Price notes › a note, Delete from a sheet
    pg = t.page(b, touch=True, init=SLOW)
    open_sheet(pg, "openSheet('item',{id:'jeepney'})")
    pg.evaluate(SAMPLE); pg.click('#layer .sheet [data-a=logItem]'); pg.wait_for_timeout(3400)
    ok(pg.evaluate("U.sheet") == 'edit' and min(pg.evaluate("DIMS")) > 0 and any(pg.evaluate("UNDER")), 'item › Log what you paid: over the item sheet, the dim kept')
    pg.evaluate("U.stack=[];U.sheet=null;rerender()"); pg.wait_for_timeout(1500)
    open_sheet(pg, "openSheet('purchase',{id:'a1'})")
    pg.evaluate(SAMPLE); pg.evaluate("ACT.delPurchase({dataset:{k:'a1'}})"); pg.wait_for_timeout(3400)
    ok(pg.evaluate("U.sheet") == 'confirm' and min(pg.evaluate("DIMS")) > 0 and any(pg.evaluate("UNDER")), 'Delete from a purchase: over it, the dim kept')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(1800)
    ok(pg.evaluate("U.sheet") == 'purchase' and pg.locator('#leaving .scrim').count() == 0, 'and going back is unchanged (Q11)')
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
    pg.click('#layer .sheet .cta.red'); pg.wait_for_timeout(300)
    t.shot(pg, 'delete-mid-dark')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'no sideways scroll while things move')
    pg.context.close()
