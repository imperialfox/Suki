"""2.31 The parts kit (Q27): Suki loads imperialfox/parts-kit 1.2.0, the kit runs the motion (D18), and every sheet,
alert and toast is the kit's (parts 41, 48 and 49), as Vocal Sessions' Q41. From the UI consistency audit of 2.27,
findings 3, 6, 10, 11, 12, 14 and 21; decisions in the project note suki_parts_decisions.md.

pin      the copy in css/ and js/ is the kit unchanged (SHA256SUMS.txt), version 1.2.0, with its README, changelog and
         licence in tools/parts-kit/; it loads before app.css and motion.js; the offline cache keeps it;
settings js/parts.settings.js loads with no problems, and every decision has its line with its ID;
motion   the kit runs the motion: Suki's speed and Reduce Motion reach Parts.motion, survive a reload, and slow, stop or
         fade the kit's parts; MOTION reads the kit's springs; land (S02); Reduce Motion fades are 100 ms (D20);
diff     Parts.differences() on each screen and sheet lists only Suki's decisions (none today);
alerts   every yes or no question is the kit's alert and still does what it did (delete a purchase or a price note,
         clear recovered data, put back, restore); Erase all data stays a sheet on kit 1.2.0 (S03);
toasts   toasts are the kit's: 3 s, with or without Undo (D16), Undo works; the sticky warning stays Suki's own (S04);
sheets   iPhone sheets are the kit's: 46 corners (D17), strong glass (D15), a flick or a pull from the content closes
         them, a sheet opened from a sheet stacks over it, a locked sheet stays; iPad and Mac keep Suki's own centred
         sheet (S01, 28 corners); the tab bar stays under the dim;
sizes    a sheet, an alert and a toast at 375, 390 and 402 wide, on its side, iPad and Mac, light and dark: inside the
         screen, no sideways scroll, no errors.
presses  Q28: glass buttons grow 17 pt and light up (part 12) and nothing pressed is cut off; solid capsules shrink to
         --press (part 14); rows and card doors highlight (part 35, D06); the Till's notes keep their own press;
controls Q28: chips (part 18), the four segmented controls (part 23, D04: tap, drag, swell, no squish, no swipe back)
         and the switches (part 21: a row tap, a drag back, a drag over, a tap, Space);
bars     Q28: the tab bar (parts 4 and 15: equal tabs, the highlight sliding and dragged), on its side, iPad's top tabs,
         the Mac sidebar staying Suki's own, and the top bar's soft edge (parts 2 and 51).
SUKI_PARTS=pin,settings,motion,diff,alerts,toasts,sheets,sizes,presses,controls,bars runs only those parts."""
import os, re, hashlib
import harness
from harness import ROOT, READ, BROWSER

_only = [x for x in os.environ.get('SUKI_PARTS', '').split(',') if x]
wanted = lambda k: not _only or k in _only
VERSION = '1.2.0'
# every difference from the kit Suki has decided on: Parts.differences() key → decision ID. None today: Suki's
# timings are the kit's, it has no springs of its own, and its settings are the kit's defaults
DIFFERENCES = {}
# every decision in Suki's register (suki_parts_decisions.md) has its line in js/parts.settings.js
DECISIONS = ['D01', 'D04', 'D06', 'D08', 'D14', 'D15', 'D16', 'D17', 'D18', 'D19', 'D20', 'D21', 'D22', 'D23',
             'S01', 'S02', 'S03', 'S04', 'S05', 'S06']
ALERT = '#layer .pk-alert:not(.pk-leaving)'


def read(*p):
    return open(os.path.join(ROOT, *p), encoding='utf-8').read()


def pin(b, t):
    ok = t.ok
    sums = dict(reversed(l.split()) for l in read('tools', 'parts-kit', 'SHA256SUMS.txt').strip().splitlines())
    got = {f: hashlib.sha256(open(os.path.join(ROOT, d, f), 'rb').read()).hexdigest() for d, f in (('css', 'parts-kit.css'), ('js', 'parts-kit.js'))}
    ok(got == sums, f'the pinned copy matches the kit’s checksums ({[f for f in got if got[f] != sums.get(f)]})')
    ok(f"const VERSION = '{VERSION}'" in read('js', 'parts-kit.js') and f'Current version:** {VERSION}' in read('tools', 'parts-kit', 'README.md'),
       f'it is version {VERSION}, with its README')
    ok(all(os.path.exists(os.path.join(ROOT, 'tools', 'parts-kit', f)) for f in ('CHANGELOG.md', 'LICENSE.txt')), 'its changelog and licence are kept beside it')
    html = read('index.html')
    order = [html.find(x) for x in ('css/parts-kit.css', 'css/app.css', 'js/parts-kit.js', 'js/parts.settings.js', 'js/motion.js')]
    ok(all(i > 0 for i in order) and order[0] < order[1] and order[2] < order[3] < order[4], 'the kit loads before app.css, and its settings before motion.js')
    ok('APP_FILE' in read('sw.js') and '(js|css)' in read('sw.js'), 'the offline cache keeps every css and js file index.html loads, the kit included')
    ok(VERSION in read('MAINTAINING.md') and 'parts-kit' in read('MAINTAINING.md'), 'MAINTAINING notes the kit’s version')
    pg = t.page(b)
    ok(pg.evaluate("Parts.version") == VERSION, 'the page runs it')
    pg.context.close()


def settings(b, t):
    ok = t.ok
    src = read('js', 'parts.settings.js')
    lines = [l for l in src.split('\n') if re.search(r'//.*\b(?:D|S)\d\d\b', l)]
    missing = [d for d in DECISIONS if not any(re.search(r'\b' + d + r'\b', l) for l in lines)]
    ok(not missing, f'every decision has its line in parts.settings.js with its ID ({missing})')
    pg = t.page(b)
    ok(pg.evaluate("Parts.problems.length") == 0, f'the settings load with no problems ({pg.evaluate("Parts.problems")})')
    cur = pg.evaluate("Parts.current")
    ok(cur['motion'] == 'kit' and cur['confirm'] == 'alert' and cur['sheet']['dragShrink'] is False and cur['sheet']['glass'] == 'strong'
       and cur['timing']['toast'] == 3000 and cur['tabBar']['fold'] is False and cur['segmented']['style'] == 'gallery' and cur['row']['press'] == 'highlight',
       'D18 the kit runs the motion, D08 alerts, D14 no shrink, D15 strong glass, D16 3 s toasts, D01, D04, D06')
    own = pg.evaluate("Parts.own()")
    ok(own.get('formSheet') == 'centre' and own.get('erase') == 'sheet' and own.get('stickyToast') == 'own' and own.get('sheetCorners') == 46,
       'Suki’s own decisions are kept in own (S01, S03 and D23, S04, D17)')
    ok(pg.evaluate("document.querySelector('#layer > .pk-layer')!==null||(Parts.toast('x').close(),!!document.querySelector('#layer > .pk-layer'))"), 'the kit’s overlays go in #layer (root)')
    pg.context.close()


def motion(b, t):
    ok = t.ok
    pg = t.page(b)
    pg.evaluate("MOTION.setSpeed(1)")
    ok(pg.evaluate("Parts.motion.speed()") == 1 and pg.evaluate("MOTION.speed()") == 1, 'speed 1: Suki and the kit agree')
    sp = pg.evaluate("[MOTION.SPRINGS.gentle, MOTION.SPRINGS.nav, MOTION.SPRINGS.ripple, Object.keys(MOTION.SPRINGS).length]")
    ok(sp[0] == {'z': 0.82, 'f': 1.9} and sp[1] == {'z': 0.86, 'f': 2.2} and sp[2] == {'z': 0.6, 'f': 2.4} and sp[3] >= 12,
       'MOTION reads the kit’s springs (gentle, nav and ripple the same numbers, plus the kit’s own)')
    ok(pg.evaluate("Parts.motion.compare(MOTION.SPRINGS)") == [], 'no spring differs from the kit’s')
    ok(pg.evaluate("typeof MOTION.land==='function'&&MOTION.settle===undefined"), 'Suki’s settle is called land (S02)')
    pg.evaluate("MOTION.setSpeed(4)")
    ok(pg.evaluate("[Parts.motion.speed(),getComputedStyle(document.documentElement).getPropertyValue('--pk-speed').trim(),localStorage.getItem('suki:motion')]") == [4, '4', '4'],
       'Slow motion reaches the kit (--pk-speed 4) and is saved on this device')
    pg.reload(); harness.ready(pg)
    ok(pg.evaluate("Parts.motion.speed()") == 4, 'and survives a reload')
    pg.evaluate("openSheet('purchase',{id:'a1'})"); pg.wait_for_timeout(50)
    d = pg.evaluate("getComputedStyle(document.querySelector('#layer .pk-sheet')).transitionDuration.split(',')[0]")
    ok(d == f'{pg.evaluate("Parts.motion.spring(\'sheet\')") / 1000:g}s', f'a sheet rises at that speed ({d})')
    pg.evaluate("closeSheet()")
    pg.wait_for_function("!document.querySelector('#layer .pk-sheet')", timeout=8000)
    pg.evaluate("MOTION.setSpeed(0)")
    ok(pg.evaluate("document.documentElement.classList.contains('motion-off')&&Parts.motion.speed()===0"), 'motion off stops the kit too')
    pg.evaluate("openSheet('purchase',{id:'a1'})"); pg.evaluate("closeSheet()")
    ok(pg.locator('#layer .pk-sheet').count() == 0, 'with motion off, a closed sheet goes at once')
    pg.evaluate("MOTION.setSpeed(1)")
    pg.evaluate("MOTION.setReduce('on')")
    ok(pg.evaluate("[Parts.motion.reduced(),document.documentElement.classList.contains('motion-reduced'),localStorage.getItem('suki:reduceMotion')]") == [True, True, 'on'],
       'forcing Reduce Motion reaches the kit and is saved on this device')
    pg.reload(); harness.ready(pg)
    ok(pg.evaluate("Parts.motion.reduced()") and pg.evaluate("MOTION.reducePref()") == 'on', 'and survives a reload')
    ok(pg.evaluate("MOTION.reducedMs()") == 100, 'its fades are the kit’s 100 ms (D20)')
    pg.evaluate("MOTION.setSpeed(1)")  # the tests' page starts with motion off after a reload
    pg.evaluate("toast('Hello')"); pg.wait_for_timeout(30)
    tr = pg.evaluate("(e=>[getComputedStyle(e).transitionProperty,getComputedStyle(e).transitionDuration])(document.querySelector('#layer .pk-toast'))")
    ok('translate' not in tr[0] and tr[1].split(',')[0] == '0.1s', f'a toast only fades, over 100 ms ({tr})')
    pg.evaluate("MOTION.setReduce('auto')")
    ok(pg.evaluate("localStorage.getItem('suki:reduceMotion')") is None and not pg.evaluate("Parts.motion.reduced()"), 'Match iPhone hands it back to the device')
    pg.context.close()


def diff(b, t):
    ok = t.ok
    pg = t.page(b)
    seen, bad = 0, []
    for js in ["go('home')", "go('till')", "go('search')", "go('spending')", "go('convert')", "go('settings')", "go('history')",
               "openSheet('purchase',{id:'a1'})", "openSheet('item',{id:'bigas'})", "(U.calD=localISO(),openSheet('calendar'))", "openSheet('access')",
               "ACT.delPurchase({dataset:{k:'a1'}})"]:
        pg.evaluate(js); pg.wait_for_timeout(40)
        found = pg.evaluate("Parts.differences().map(d=>d.key)")
        extra = [k for k in found if k not in DIFFERENCES]
        if extra: bad.append(f'{js}: {extra}')
        seen += 1
        if 'Sheet' in js or 'del' in js: pg.evaluate("U.stack=[];U.sheet=null;U.sd={};render()")
    ok(not bad, f'on {seen} screens and sheets, Parts.differences() lists only Suki’s decisions ({bad})')
    stale = [k for k in DIFFERENCES if k not in pg.evaluate("Parts.differences().map(d=>d.key)")]
    ok(not stale, f'and every listed difference still differs ({stale})')
    pg.context.close()


def alerts(b, t):
    ok = t.ok
    pg = t.page(b)
    q = lambda: pg.evaluate(f"(e=>e?[e.querySelector('.pk-alert-title').innerText,(e.querySelector('.pk-alert-text')||{{}}).innerText||'',e.querySelector('[data-a=yes]').innerText,e.querySelector('[data-a=no]').innerText,e.dataset.screen]:null)(document.querySelector('{ALERT}'))")
    # delete a purchase: Cancel keeps it; Delete deletes it, then Undo
    pg.evaluate("go('spending')"); pg.evaluate("ACT.delPurchase({dataset:{k:'a1'}})"); pg.wait_for_timeout(60)
    a = q()
    ok(a and a[0] == 'Delete this purchase?' and a[1] == 'Chickenjoy bucket, ₱459.00.' and a[2] == 'Delete' and a[3] == 'Cancel' and a[4] == 'SK-011',
       f'Delete a purchase is the kit’s alert, SK-011 ({a})')
    ok(pg.evaluate(f"(e=>e.querySelector('[data-a=yes]').classList.contains('pk-red')&&getComputedStyle(e).borderTopLeftRadius)(document.querySelector('{ALERT}'))") == '34px',
       'with a red action and 34 corners (--r-alert)')
    pg.click(f'{ALERT} [data-a=no]'); pg.wait_for_timeout(60)
    ok(pg.evaluate("U.sheet") is None and pg.evaluate("D.purchases.some(p=>p.id==='a1')"), 'Cancel keeps it')
    pg.evaluate("ACT.delPurchase({dataset:{k:'a1'}})"); pg.wait_for_timeout(60)
    pg.click(f'{ALERT} [data-a=yes]'); pg.wait_for_timeout(100)
    ok(not pg.evaluate("D.purchases.some(p=>p.id==='a1')") and pg.locator('.toast.undo:not(.pk-leaving)').count() == 1, 'Delete deletes it and offers Undo')
    pg.click('.toast.undo:not(.pk-leaving) button'); pg.wait_for_timeout(100)
    ok(pg.evaluate("D.purchases.some(p=>p.id==='a1')"), 'Undo brings it back')
    # Escape is Cancel
    pg.evaluate("ACT.delPurchase({dataset:{k:'a1'}})"); pg.wait_for_timeout(60)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(60)
    ok(pg.evaluate("U.sheet") is None and pg.evaluate("D.purchases.some(p=>p.id==='a1')") and pg.locator(ALERT).count() == 0, 'Escape cancels it')
    # from the purchase sheet: the alert over it, Cancel back to it
    pg.evaluate("openSheet('purchase',{id:'a2'})"); pg.wait_for_timeout(60)
    pg.click('#layer .sheet [data-a=delPurchase]'); pg.wait_for_timeout(60)
    ok(pg.locator(ALERT).count() == 1 and pg.locator('#layer .sheet').count() == 1, 'from the purchase sheet, the alert opens over it')
    pg.click(f'{ALERT} [data-a=no]'); pg.wait_for_timeout(60)
    ok(pg.evaluate("U.sheet") == 'purchase' and pg.locator('#layer .sheet [data-a=delPurchase]').count() == 1, 'and Cancel goes back to it')
    pg.click('#layer .sheet [data-a=delPurchase]'); pg.wait_for_timeout(60); pg.click(f'{ALERT} [data-a=yes]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.sheet") is None and not pg.evaluate("D.purchases.some(p=>p.id==='a2')") and pg.locator('#layer .pk-sheet').count() == 0, 'Delete closes both')
    # a price note: from the item sheet, back to it
    pg.evaluate("openSheet('item',{id:'bigas'})"); pg.wait_for_timeout(60)
    n = pg.evaluate("D.observations.length")
    pg.click('#layer .sheet [data-a=delObs] >> nth=0'); pg.wait_for_timeout(60)
    a = q()
    ok(a and a[0] == 'Delete this price note?' and a[2] == 'Delete' and a[4] == 'SK-012', f'Delete a price note is an alert, SK-012 ({a})')
    pg.click(f'{ALERT} [data-a=yes]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.sheet") == 'item' and pg.evaluate("D.observations.length") == n - 1 and pg.locator('.toast.undo:not(.pk-leaving)').count() == 1,
       'deleting it goes back to the item, with Undo')
    pg.evaluate("U.stack=[];U.sheet=null;render()")
    # Put back what was here
    pg.evaluate("SAFETY={data:{purchases:[],observations:[]},at:Date.now(),why:'erase'};openSheet('putback')"); pg.wait_for_timeout(60)
    a = q()
    ok(a and a[0] == 'Put back what was here?' and a[2] == 'Put them back' and a[4] == 'SK-021' and 'Before your last erase' in a[1], f'Put back is an alert, SK-021 ({a})')
    pg.click(f'{ALERT} [data-a=yes]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("D.purchases.length") == 0 and pg.evaluate("U.sheet") is None, 'and puts back what was there')
    pg.context.close()
    # Clear recovered data, over the Recovered data sheet
    pg = t.page(b)
    pg.evaluate("RESCUE=[{at:Date.now(),items:[{raw:'x'}],saved:true}];openSheet('rescue')"); pg.wait_for_timeout(60)
    pg.click('#layer .sheet [data-a=clearRescue]'); pg.wait_for_timeout(60)
    a = q()
    ok(a and a[0] == 'Clear recovered data?' and a[2] == 'Clear it' and a[4] == 'SK-022' and pg.locator('#layer .sheet').count() == 1, f'Clear recovered data is an alert over its sheet, SK-022 ({a})')
    pg.click(f'{ALERT} [data-a=yes]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("RESCUE.length") == 0 and pg.evaluate("U.sheet") is None, 'and clears it')
    # Restore: the alert says what's here and what's in the backup
    pg.evaluate("openSheet('restore',{data:{purchases:[{id:'r1',item:'x',price:5,date:'2026-11-01'}],observations:[],rate:null,learned:[]},when:'on 4 Nov 2026'})"); pg.wait_for_timeout(60)
    a = q()
    ok(a and a[0] == 'Restore this backup?' and a[4] == 'SK-015' and 'This device has 4 purchases' in a[1] and 'the backup has 1 purchase and 0 price notes' in a[1] and a[2] == 'Replace with this backup',
       f'Restore is an alert that says what’s here and what’s in the backup, SK-015 ({a})')
    pg.click(f'{ALERT} [data-a=no]'); pg.wait_for_timeout(60)
    ok(pg.evaluate("D.purchases.length") == 4 and pg.evaluate("U.sheet") is None, 'Cancel changes nothing')
    # Restore when the safety copy can't be kept: the alert closes and nothing changes
    pg.evaluate("keepSafetyCopy=()=>Promise.resolve(false)")
    pg.evaluate("openSheet('restore',{data:{purchases:[{id:'r1',item:'x',price:5,date:'2026-11-01'}],observations:[],rate:null,learned:[]},when:''})"); pg.wait_for_timeout(60)
    pg.click(f'{ALERT} [data-a=yes]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sheet") is None and pg.evaluate("D.purchases.length") == 4 and pg.locator('.toast.sticky').count() == 1, 'if the safety copy can’t be kept, it says so and nothing changes')
    # Erase all data stays a sheet on kit 1.2.0 (S03)
    pg.evaluate("toast.length;document.querySelectorAll('.toast.sticky').forEach(e=>e.remove());openSheet('erase')"); pg.wait_for_timeout(60)
    ok(pg.locator(ALERT).count() == 0 and pg.locator('#layer .pk-sheet.sheet [data-a=eraseYes]').count() == 1 and pg.locator('#layer .sheet [data-a=exportBackup]').count() == 1,
       'Erase all data stays a sheet, with Export a backup first (S03, until kit 1.3.0)')
    pg.context.close()


def toasts(b, t):
    ok = t.ok
    pg = t.page(b, init="localStorage.setItem('suki:motion','1')")
    for undo in (False, True):
        pg.evaluate("toast('Saved'" + (",()=>{window.UNDONE=1}" if undo else "") + ")")
        pg.wait_for_timeout(2600)
        on = pg.locator('#layer .pk-toast.toast:not(.pk-leaving)').count()
        pg.wait_for_timeout(900)
        off = pg.locator('#layer .pk-toast.toast:not(.pk-leaving)').count()
        ok(on == 1 and off == 0, f'a toast{" with Undo" if undo else ""} stays 3 s (D16)')
        pg.wait_for_timeout(500)
    pg.evaluate("toast('Purchase deleted',()=>{window.UNDONE=1})"); pg.wait_for_timeout(600)
    tr = pg.evaluate("(e=>[getComputedStyle(e).transitionDuration,e.getBoundingClientRect().top,e.dataset.screen,e.querySelector('button').dataset.name])(document.querySelector('#layer .pk-toast'))")
    ok(tr[0].split(',')[0] == '0.5s' and tr[1] >= 0 and tr[2] == 'SK-016' and tr[3] == 'undo-button', f'it drops in over 500 ms, SK-016, its Undo named ({tr})')
    pg.click('#layer .pk-toast .pk-toast-undo'); pg.wait_for_timeout(100)
    ok(pg.evaluate("window.UNDONE") == 1, 'Undo runs')
    pg.evaluate("toast('One')"); pg.evaluate("toast('Two')"); pg.wait_for_timeout(100)
    ok(pg.locator('#layer .pk-toast:not(.pk-leaving)').count() == 1 and pg.inner_text('#layer .pk-toast:not(.pk-leaving)').startswith('Two'), 'one at a time: a new one replaces the last')
    pg.evaluate("toast('Couldn’t reach the rate service, so the saved rate is still in use')"); pg.wait_for_timeout(100)
    ok(pg.evaluate("(e=>e.classList.contains('sk-long')&&e.scrollWidth<=e.clientWidth+1)(document.querySelector('#layer .pk-toast:not(.pk-leaving)'))"), 'a longer message wraps rather than being cut off')
    pg.evaluate("toast('Couldn’t save.',null,true)"); pg.evaluate("toast('Purchase saved',()=>{})"); pg.wait_for_timeout(700)
    st = pg.evaluate("[!!document.querySelector('body > .toast.sticky:not(.pk-toast)'),document.querySelector('.toast.sticky').getBoundingClientRect().bottom,document.querySelector('#layer .pk-toast:not(.pk-leaving)').getBoundingClientRect().top]")
    ok(st[0] and st[2] >= st[1], f'the sticky warning stays Suki’s own (S04), and toasts drop in below it ({st})')
    pg.wait_for_timeout(3600)
    ok(pg.locator('.toast.sticky').count() == 1, 'and it stays until OK')
    pg.context.close()


def sheets(b, t):
    ok = t.ok
    pg = t.page(b, init="localStorage.setItem('suki:motion','1')")
    pg.evaluate("go('spending')")
    pg.evaluate("openSheet('purchase',{id:'a1'})"); pg.wait_for_timeout(100)
    pg.wait_for_function("!document.querySelector('#layer .sheet').getAnimations().length", timeout=8000)
    s = pg.evaluate("(e=>[e.classList.contains('pk-sheet'),getComputedStyle(e).borderTopLeftRadius,e.classList.contains('pk-strong'),e.dataset.screen,!!e.querySelector('.pk-sheet-head .shead'),!!e.querySelector('.pk-grabber')])(document.querySelector('#layer .sheet'))")
    ok(s == [True, '46px', True, 'SK-007', True, True], f'an iPhone sheet is the kit’s: 46 corners, strong glass, Suki’s head in its head, the kit’s grabber ({s})')
    ok(pg.locator('#dock .tabbar').count() == 1, 'the tab bar stays, under the dim')
    # a pull from the content (at the top) closes it
    harness.flick(pg, '#layer .sheet .pk-sheet-body .grp', 12, 4, 30)
    pg.wait_for_timeout(100)
    pg.wait_for_function("!document.querySelector('#layer .sheet').getAnimations().length", timeout=8000)
    ok(pg.evaluate("U.sheet") == 'purchase', 'a slow, short pull from its content (400 pt/s, 48 pt) springs back')
    harness.flick(pg, '#layer .sheet .pk-sheet-body .grp')
    pg.wait_for_timeout(600)
    ok(pg.evaluate("U.sheet") is None and pg.locator('#layer .pk-sheet').count() == 0, 'a flick down from its content (150 pt, past 700 pt/s) closes it')
    # stacking: Edit over the purchase, then back
    pg.evaluate("openSheet('purchase',{id:'a1'})"); pg.wait_for_timeout(700)
    pg.click('#layer .sheet [data-a=editPurchase]'); pg.wait_for_timeout(700)
    st = pg.evaluate("[document.querySelectorAll('#layer .pk-sheet').length,document.querySelectorAll('#layer .sheet').length,!!document.querySelector('#layer .pk-sheet.sk-covered[inert]'),document.querySelectorAll('#layer .pk-dim.pk-on').length]")
    ok(st == [2, 1, True, 2], f'Edit from a purchase stacks over it: two sheets, the purchase underneath and out of reach ({st})')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(700)
    ok(pg.evaluate("U.sheet") == 'purchase' and pg.locator('#layer .pk-sheet').count() == 1 and pg.locator('#layer .sheet[data-screen=SK-007]').count() == 1, 'Escape closes only the top one')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(700)
    # the welcome card is locked: no grabber, and the dim, a drag and Escape leave it be
    pg.evaluate("openSheet('welcome')"); pg.wait_for_timeout(700)
    lk = pg.evaluate("(e=>[e.classList.contains('locked'),getComputedStyle(e.querySelector('.pk-grabber')).display,e.getBoundingClientRect().height])(document.querySelector('#layer .sheet'))")
    ok(lk[0] and lk[1] == 'none' and lk[2] > 600, f'the welcome card is the kit’s sheet, locked, with no grabber, filling the screen ({lk})')
    ok(pg.evaluate("getComputedStyle(document.querySelector('#layer .sheet .pk-sheet-body')).touchAction") == 'pan-y', 'its content scrolls the usual way, even at the top')
    pg.mouse.click(200, 20); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    bb = pg.locator('#layer .sheet .wel').first.bounding_box()
    pg.mouse.move(bb['x'] + 40, bb['y'] + 10); pg.mouse.down()
    for d in (30, 90, 200): pg.mouse.move(bb['x'] + 40, bb['y'] + 10 + d)
    pg.mouse.up(); pg.wait_for_timeout(500)
    ok(pg.evaluate("U.sheet") == 'welcome' and pg.locator('#layer .pk-sheet:not(.pk-leaving)').count() == 1, 'tapping the dim, Escape and a drag leave it open')
    pg.click('#layer .sheet [data-a=welcomeGo]'); pg.wait_for_timeout(600)
    ok(pg.evaluate("U.sheet") is None, 'Continue closes it')
    pg.context.close()
    # iPad and Mac keep Suki's own centred sheet (S01)
    for w, h, name in ((820, 1180, 'iPad'), (1440, 900, 'Mac')):
        pg = t.page(b, w=w, h=h, ua=None)
        pg.evaluate("openSheet('notes')"); pg.wait_for_timeout(60)
        own = pg.evaluate("(e=>e?[e.classList.contains('pk-sheet'),getComputedStyle(e).borderTopLeftRadius,e.dataset.screen]:null)(document.querySelector('#own .scrim .sheet'))")
        ok(own == [False, '28px', 'SK-010'] and pg.locator('#layer .pk-sheet').count() == 0, f'{name}: a sheet is Suki’s own centred sheet, 28 corners (--r-form, S01) ({own})')
        pg.evaluate("ACT.delPurchase({dataset:{k:'a1'}})"); pg.wait_for_timeout(60)
        ok(pg.locator(ALERT).count() == 1, f'{name}: alerts are the kit’s there too')
        pg.context.close()


def sizes(b, t):
    ok = t.ok
    SIZES = [(375, 667, 'iPhone SE'), (390, 844, '390'), (402, 874, '402'), (852, 393, 'on its side'), (820, 1180, 'iPad'), (1440, 900, 'Mac')]
    for sc in ('light', 'dark'):
        for w, h, name in SIZES:
            pg = t.page(b, w=w, h=h, sc=sc, ua=None if w >= 820 else harness.UA_IPHONE)
            pg.evaluate("openSheet('purchase',{id:'a1'})"); pg.wait_for_timeout(60)
            box = pg.evaluate("(e=>{const r=e.getBoundingClientRect();return [r.left,r.top,r.right,r.bottom]})(document.querySelector('#layer .sheet'))")
            inside = box[0] >= 0 and box[1] >= 0 and box[2] <= w + 0.5 and box[3] <= h + 0.5
            if name == 'on its side': inside = inside and box[2] - box[0] <= 561
            t.shot(pg, f'parts-sheet-{name.replace(" ", "-")}-{sc}')
            pg.click('#layer .sheet [data-a=delPurchase]') if pg.locator('#layer .sheet [data-a=delPurchase]').count() else pg.evaluate("ACT.delPurchase({dataset:{k:'a1'}})")
            pg.wait_for_timeout(60)
            abox = pg.evaluate(f"(e=>{{const r=e.getBoundingClientRect();return [r.left,r.top,r.right,r.bottom]}})(document.querySelector('{ALERT}'))")
            t.shot(pg, f'parts-alert-{name.replace(" ", "-")}-{sc}')
            pg.click(f'{ALERT} [data-a=yes]'); pg.wait_for_timeout(80)
            tbox = pg.evaluate("(e=>{const r=e.getBoundingClientRect();return [r.left,r.top,r.right,r.bottom]})(document.querySelector('#layer .pk-toast'))")
            fine = (inside and abox[0] >= 0 and abox[2] <= w and abox[3] <= h and tbox[0] >= 0 and tbox[2] <= w and tbox[1] >= 0
                    and pg.evaluate("document.documentElement.scrollWidth<=innerWidth"))
            ok(fine, f'{sc} {name}: the sheet, the alert and the toast fit the screen, with no sideways scroll ({box} {abox} {tbox})')
            pg.context.close()


# Q28: a press held from a named element, measured while held, let go without a click (the action isn't run)
HELD = """(sel)=>{const el=document.querySelector(sel); if(!el) return null; const r=el.getBoundingClientRect(), cs=getComputedStyle(el);
 let p=el.parentElement, cut=[]; while(p&&p!==document.body){const c=getComputedStyle(p); if(/hidden|auto|scroll|clip/.test(c.overflowX+c.overflowY)){const q=p.getBoundingClientRect(); if(r.left<q.left-0.5||r.right>q.right+0.5||r.top<q.top-0.5||r.bottom>q.bottom+0.5) cut.push((p.id||p.className).toString().slice(0,40));} p=p.parentElement;}
 return {w:el.offsetWidth, h:el.offsetHeight, scale:cs.scale, transform:cs.transform, z:cs.zIndex, lit:getComputedStyle(el,'::after').opacity, bg:cs.backgroundColor, cut, pressed:el.classList.contains('pk-pressed')}}"""
NOCLICK = "addEventListener('click', e=>{e.stopPropagation();e.preventDefault()}, {capture:true, once:true})"


def hold(pg, sel, ms=450):
    el = pg.locator(sel).first
    el.scroll_into_view_if_needed()
    pg.wait_for_timeout(80)
    bx = el.bounding_box()
    pg.mouse.move(bx['x'] + bx['width'] / 2, bx['y'] + bx['height'] / 2)
    pg.mouse.down()
    pg.wait_for_timeout(ms)
    r = pg.evaluate(HELD, sel)
    pg.evaluate(NOCLICK)
    pg.mouse.up()
    pg.wait_for_timeout(ms)
    a = pg.evaluate(f"getComputedStyle(document.querySelector({sel!r})).scale")
    r['after'] = a == 'none' or abs(float(a) - 1) < 0.01
    r['released'] = not pg.evaluate(f"document.querySelector({sel!r}).classList.contains('pk-pressed')")
    return r


def drawn(r, want, lit='1'):
    """Pressed and let go as drawn: Chromium reads the grown size and light mid-press and after. WebKit on GitHub's
    machines draws a glass sheet a few frames a second, so the transition can still be at its start when read: there the
    press is read from the kit's pk-pressed class while held and gone after (Q32)"""
    if BROWSER == 'webkit':
        return r['pressed'] and r['released']
    return abs(float(r['scale']) - want) < 0.01 and r['lit'] == lit and r['after']


def presses(b, t):
    """Q28 parts 12, 14 and 35: glass buttons grow 17 pt and light up, solid capsules shrink to --press, rows and card
    doors highlight; nothing pressed is cut off."""
    ok = t.ok
    pg = t.page(b, w=402, h=874, init="localStorage.setItem('suki:motion','1')")
    glass = []
    def g(name, sel):
        r = hold(pg, sel)
        want = 1 + 17 / max(r['w'], r['h'])
        glass.append((name, r))
        ok(drawn(r, want) and r['z'] == '20' and not r['cut'],
           f'{name}: grows 17 pt (×{want:.3f}) and lights up while pressed, above its neighbours and not cut off, then comes back ({r})')
    g('the gear', '#barR .circ[data-v=settings]')
    pg.evaluate("go('spending')"); pg.wait_for_timeout(200)
    g('Spending’s +', '#barR .circ[data-a=newPurchase]')
    g('Export as CSV (a glass capsule)', '#app .btn.glass.csv')
    pg.evaluate("openSheet('purchase',{id:'a1'})"); pg.wait_for_timeout(700)
    g('a sheet’s ✕', '#layer .sheet .shrow [data-a=close]')
    g('a sheet’s pencil', '#layer .sheet .shrow [data-a=editPurchase]')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(500)
    pg.evaluate("openSheet('calendar')"); pg.wait_for_timeout(700)
    g('the calendar’s arrows', '#layer .sheet .calhead .circ')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(500)
    pg.evaluate("go('convert')"); pg.wait_for_timeout(200)
    g('swap', '#app .swap')
    g('Refresh (a glass capsule)', '#refreshRate')
    pg.evaluate("go('help')"); pg.wait_for_timeout(200)
    g('Back', '#barL .circ')
    # solid capsules shrink to --press (part 14) and come back on the release spring
    pg.evaluate("go('home')"); pg.wait_for_timeout(200)
    r = hold(pg, '#homeSave')
    ok(r['scale'] == '0.93' and r['after'] and 'pk-press-solid' in pg.get_attribute('#homeSave', 'class'),
       f'Save purchase shrinks to --press (0.93) while pressed and comes back ({r})')
    pg.evaluate("go('till')"); pg.wait_for_timeout(200)
    pg.fill('#till-bill', '37')
    pg.wait_for_timeout(200)
    r = hold(pg, '#tillLog')
    ok(r['scale'] == '0.93', f'Log this bill shrinks to --press too ({r["scale"]})')
    trans = pg.evaluate("getComputedStyle(document.getElementById('tillLog')).transitionTimingFunction")
    ok(trans.startswith('linear('), f'it comes back on the release spring, a linear() curve ({trans[:30]})')
    ok(pg.evaluate("[...document.querySelectorAll('#app .dn')].every(d=>!/pk-press/.test(d.className))"),
       'the Till’s notes and Exact keep their own press and tilt (Q18), not the kit’s')
    # rows and card doors highlight (part 35, D06): none shrinks
    press = pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--pk-row-press').trim()")
    pg.evaluate("go('spending')"); pg.wait_for_timeout(200)
    r = hold(pg, '#spendList button.row', 150)
    ok(r['scale'] == 'none' and r['transform'] == 'none' and r['bg'] == pg.evaluate(f"(()=>{{const d=document.createElement('i');d.style.color={press!r};document.body.append(d);const c=getComputedStyle(d).color;d.remove();return c}})()"),
       f'a purchase row highlights with the kit’s row press colour and doesn’t shrink ({r["bg"]}, {r["scale"]}, {r["transform"]})')
    pg.evaluate("go('home')"); pg.wait_for_timeout(200)
    for name, sel in (('Total spent', '#app .sumcard .door[data-v=all]'), ('Today', '#app .sumcard .door[data-v=day]')):
        r = hold(pg, sel, 150)
        ok(r['scale'] == 'none' and r['transform'] == 'none' and r['bg'] != 'rgba(0, 0, 0, 0)', f'Home’s {name} highlights like a row and doesn’t shrink ({r["bg"]})')
    r = hold(pg, '#rateCard', 150)
    ok(r['scale'] == 'none' and r['transform'] == 'none' and r['lit'] == '1', f'the rate card highlights (the row press colour over its own) and doesn’t shrink ({r})')
    t.shot(pg, 'parts-home-pressed-card')
    # nothing moved at rest: the card doors take back the room their highlight reaches into
    sides = pg.evaluate("""[...document.querySelectorAll('#app .sumcard .door')].map(d=>{const c=getComputedStyle(d),n=(p)=>parseFloat(c[p]);
      return [n('marginTop')+n('paddingTop'), n('marginBottom')+n('paddingBottom'), n('marginRight')+n('paddingRight'), n('paddingTop')]})""")
    ok(sides == [[0, 0, 0, 8], [0, 0, 0, 8]], f'Home’s figures sit where they did: each door’s highlight reaches 8 pt round them, with that room taken back ({sides})')
    pg.context.close()


def controls(b, t):
    """Q28 parts 18, 21 and 23: chips, switches and the four segmented controls are the kit's."""
    ok = t.ok
    pg = t.page(b, w=402, h=874, init="localStorage.setItem('suki:motion','1')")
    # chips (part 18): the kit's chip, picked by Suki (.pk-static), no shrink
    pg.evaluate("go('search')"); pg.wait_for_timeout(200)
    ok(pg.evaluate("[...document.querySelectorAll('#browse .chip')].every(c=>c.classList.contains('pk-chip'))") and pg.evaluate("!!document.querySelector('#browse.pk-static')"),
       'Search’s category chips are the kit’s .pk-chip, in a .pk-static row (Suki picks them)')
    r = hold(pg, '#browse .chip:not(.on)', 150)
    ok(r['scale'] == 'none' and r['transform'] == 'none', f'a chip doesn’t shrink while pressed ({r["scale"]}, {r["transform"]})')
    pg.click('#browse .chip:not(.on)'); pg.wait_for_timeout(200)
    ok(pg.evaluate("document.querySelectorAll('#browse .chip.on').length") == 1 and pg.evaluate("U.scat") != 'all',
       f'tapping a chip still picks it, one at a time ({pg.evaluate("U.scat")})')
    # the four segmented controls (part 23, D04)
    segs = {'rangeSeg': "go('spending')", 'hSeg': "go('history')", 'reduceSeg': "go('settings');openSheet('access')", 'noteSeg': "go('settings');openSheet('access')"}
    for sid, how in segs.items():
        pg.evaluate("closeSheet()"); pg.wait_for_timeout(400)
        pg.evaluate(how); pg.wait_for_timeout(700)
        info = pg.evaluate(f"""(()=>{{const s=document.getElementById('{sid}'), k=s.querySelector(':scope > .pk-seg-ind'), on=s.querySelector(':scope > button.on');
          return {{seg:s.classList.contains('pk-seg'), knob:!!k, oldKnob:!!s.querySelector('.knob'), n:s.style.getPropertyValue('--pk-n'), i:s.style.getPropertyValue('--pk-i'),
          on:[...s.querySelectorAll(':scope > button')].indexOf(on), pressed:on&&on.getAttribute('aria-pressed')}}}})()""")
        ok(info['seg'] and info['knob'] and not info['oldKnob'] and info['i'] == str(info['on']) and info['pressed'] == 'true',
           f'#{sid} is the kit’s segmented control: its knob starts on the picked button ({info})')
    ok(pg.evaluate("Parts.settings ? true : true") and pg.evaluate("!document.documentElement.classList.contains('pk-seg-squish')"),
       'no squish: segmented.style is the gallery’s (D04)')
    # Spending's period: a tap slides the knob, a drag picks where it settles, and the knob swells while held
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(400)
    pg.evaluate("go('spending')"); pg.wait_for_timeout(200)
    pg.locator('#rangeSeg').scroll_into_view_if_needed()
    pg.click('#rangeSeg [data-v=week]'); pg.wait_for_timeout(40)
    moving = pg.evaluate("document.querySelector('#rangeSeg .pk-seg-ind').getAnimations().some(a=>a.transitionProperty==='translate')")
    pg.wait_for_timeout(500)
    ok(pg.evaluate("U.range") == 'week' and moving and pg.get_attribute('#rangeSeg [data-v=week]', 'aria-pressed') == 'true',
       f'a tap on W picks Week, and the knob slides there on its spring (sliding {moving})')
    bx = pg.locator('#rangeSeg').bounding_box(); y = bx['y'] + bx['height'] / 2
    pg.mouse.move(bx['x'] + bx['width'] * 0.375, y); pg.mouse.down(); pg.wait_for_timeout(120)
    live = pg.evaluate("document.querySelector('#rangeSeg .pk-seg-ind').classList.contains('pk-live')")
    for k in range(12):
        pg.mouse.move(bx['x'] + bx['width'] * (0.375 + 0.025 * k), y); pg.wait_for_timeout(16)
    pg.mouse.up(); pg.wait_for_timeout(600)
    ok(live, 'the knob swells into glass while it’s held')
    ok(pg.evaluate("U.range") == 'month' and pg.evaluate("document.querySelectorAll('#rangeSeg button.on').length") == 1,
       f'dragging the knob from W to M picks Month ({pg.evaluate("U.range")})')
    ok(pg.evaluate("window.scrollY") >= 0 and not t.errors, 'a drag on the control doesn’t scroll the page or break anything')
    # Rate history's range: dragging it isn't a swipe back
    pg.evaluate("go('history')"); pg.wait_for_timeout(300)
    bx = pg.locator('#hSeg').bounding_box(); y = bx['y'] + bx['height'] / 2
    pg.mouse.move(bx['x'] + bx['width'] * 0.1, y); pg.mouse.down()
    for k in range(15):
        pg.mouse.move(bx['x'] + bx['width'] * (0.1 + 0.05 * k), y); pg.wait_for_timeout(16)
    pg.mouse.up(); pg.wait_for_timeout(700)
    ok(pg.evaluate("U.tab") == 'history' and pg.evaluate("HV.range") != 'M', f'dragging Rate history’s range picks a range and doesn’t swipe back ({pg.evaluate("U.tab")}, {pg.evaluate("HV.range")})')
    # switches (part 21)
    pg.evaluate("go('settings');openSheet('access')"); pg.wait_for_timeout(700)
    sws = pg.evaluate("[...document.querySelectorAll('#layer label.row.toggle')].map(l=>[l.querySelector('input').dataset.a, !!l.querySelector('.pk-switch'), !!l.querySelector('.sw-ui'), l.querySelector('.pk-switch').getAttribute('tabindex')])")
    ok(len(sws) == 2 and all(s[1] and not s[2] and s[3] is None for s in sws), f'Slow motion and Show screen IDs are the kit’s switch, which takes no focus of its own ({sws})')
    SW = "(a=>{const i=document.querySelector('#layer input[data-a='+a+']');return [i.checked, i.parentElement.querySelector('.pk-switch').classList.contains('on')]})"
    pg.click('#layer label.row.toggle:has([data-a=screenIds]) .lbl'); pg.wait_for_timeout(500)
    ok(pg.evaluate(f"{SW}('screenIds')") == [True, True] and pg.evaluate("SCR.idsOn()"), 'a tap on the row turns Show screen IDs on, and its switch slides on')
    sw = pg.locator('#layer label.row.toggle:has([data-a=screenIds]) .pk-switch').bounding_box()
    sy = sw['y'] + sw['height'] / 2
    pg.mouse.move(sw['x'] + 50, sy); pg.mouse.down()
    for k in range(6): pg.mouse.move(sw['x'] + 50 - 3 * k, sy); pg.wait_for_timeout(16)
    for k in range(6): pg.mouse.move(sw['x'] + 35 + 3 * k, sy); pg.wait_for_timeout(16)
    pg.mouse.up(); pg.wait_for_timeout(600)
    ok(pg.evaluate(f"{SW}('screenIds')") == [True, True], 'dragging the knob and letting it go back where it was changes nothing')
    pg.mouse.move(sw['x'] + 50, sy); pg.mouse.down()
    for k in range(10): pg.mouse.move(sw['x'] + 50 - 5 * k, sy); pg.wait_for_timeout(16)
    pg.mouse.up(); pg.wait_for_timeout(600)
    ok(pg.evaluate(f"{SW}('screenIds')") == [False, False] and not pg.evaluate("SCR.idsOn()"), 'dragging the knob to the other side turns it off')
    pg.click('#layer label.row.toggle:has([data-a=screenIds]) .pk-switch'); pg.wait_for_timeout(600)
    ok(pg.evaluate(f"{SW}('screenIds')") == [True, True], 'a tap on the switch itself turns it back on')
    pg.focus('#layer input[data-a=screenIds]'); pg.keyboard.press('Space'); pg.wait_for_timeout(600)
    ok(pg.evaluate(f"{SW}('screenIds')") == [False, False], 'Space on the focused switch turns it off, and the switch follows')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(400)
    pg.evaluate("go('help')"); pg.wait_for_timeout(200)
    tip = pg.locator('label.row.toggle:has([data-a=tipsToggle])')
    if tip.count():
        ok(tip.locator('.pk-switch').count() == 1, 'Show tips is the kit’s switch too')
    t.shot(pg, 'parts-switch')
    pg.context.close()


def bars(b, t):
    """Q28 parts 2, 4, 15 and 51: the tab bar, iPad's top tabs and the top bar's soft edge are the kit's."""
    ok = t.ok
    pg = t.page(b, w=402, h=874, init="localStorage.setItem('suki:motion','1')")
    info = pg.evaluate("""(()=>{const bar=document.querySelector('#dock .tabbar'), k=bar.querySelector(':scope > .pk-tab-ind'), tabs=[...bar.querySelectorAll(':scope > .pk-tab')];
      const kr=k.getBoundingClientRect(), on=bar.querySelector('.pk-tab.on').getBoundingClientRect();
      return {kit:bar.classList.contains('pk-tabbar'), tabs:tabs.length, widths:[...new Set(tabs.map(x=>Math.round(x.getBoundingClientRect().width)))], fit:Math.abs(kr.left-on.left)<1.5&&Math.abs(kr.width-on.width)<1.5, h:Math.round(bar.getBoundingClientRect().height), bg:getComputedStyle(bar.querySelector('.pk-tab.on')).backgroundColor}})()""")
    ok(info['kit'] and info['tabs'] == 5 and len(info['widths']) == 1 and info['fit'] and info['h'] == 64 and info['bg'] == 'rgba(0, 0, 0, 0)',
       f'the tab bar is the kit’s: five equal tabs, 64 pt, the picked one on the kit’s highlight ({info})')
    r = hold(pg, '#dock .pk-tab[data-v=till]', 150)
    ok(r['scale'] in ('none', '1') and r['transform'] == 'none', f'a tab doesn’t shrink while pressed, it only lights up ({r["scale"]}, {r["transform"]})')
    pg.click('#dock .pk-tab[data-v=convert]'); pg.wait_for_timeout(40)
    moving = pg.evaluate("document.querySelector('#dock .pk-tab-ind').getAnimations().some(a=>a.transitionProperty==='translate')")
    pg.wait_for_timeout(600)
    ok(pg.evaluate("U.tab") == 'convert' and moving and pg.evaluate("document.querySelector('#dock .tabbar').style.getPropertyValue('--pk-i')") == '4',
       f'switching tabs: Convert opens and the highlight slides to it (sliding {moving})')
    bx = pg.locator('#dock .tabbar').bounding_box(); y = bx['y'] + bx['height'] / 2
    pg.mouse.move(bx['x'] + bx['width'] * 0.9, y); pg.mouse.down()
    for k in range(14): pg.mouse.move(bx['x'] + bx['width'] * (0.9 - 0.03 * k), y); pg.wait_for_timeout(16)
    pg.mouse.up(); pg.wait_for_timeout(600)
    ok(pg.evaluate("U.tab") == 'search', f'dragging the highlight along the bar opens the tab it settles on ({pg.evaluate("U.tab")})')
    # the top bar's soft edge (parts 2 and 51)
    pg.evaluate("go('spending')"); pg.wait_for_timeout(200)
    e0 = pg.evaluate("(e=>{const c=getComputedStyle(e);return [e.classList.contains('pk-edge'), c.opacity, c.backdropFilter, c.transitionDuration]})(document.querySelector('.edge'))")
    pg.evaluate("window.scrollTo(0,200)"); pg.wait_for_timeout(500)
    e1 = pg.evaluate("[getComputedStyle(document.querySelector('.edge')).opacity, document.getElementById('bar').classList.contains('scrolled')]")
    ok(e0[0] and e0[1] == '0' and e0[2] == 'none' and e0[3] == '0.2s' and e1 == ['1', True],
       f'the soft edge is the kit’s: the page colour fading out, no blur, in over 200 ms after 36 pt of scrolling ({e0} {e1})')
    t.shot(pg, 'parts-edge-scrolled')
    pg.context.close()
    # on its side: still equal tabs in the compact bar, nothing cut short
    pg = t.page(b, w=852, h=393)
    info = pg.evaluate("""(()=>{const bar=document.querySelector('#dock .tabbar'), tabs=[...bar.querySelectorAll(':scope > .pk-tab')];
      return {h:Math.round(bar.getBoundingClientRect().height), widths:[...new Set(tabs.map(x=>Math.round(x.getBoundingClientRect().width)))], cut:tabs.filter(x=>{const s=x.querySelector('span');return s.scrollWidth>s.clientWidth+1}).length}})()""")
    ok(info['h'] == 50 and len(info['widths']) == 1 and info['cut'] == 0, f'on its side: the 50 pt bar, equal tabs, no label cut short ({info})')
    t.shot(pg, 'parts-tabbar-side')
    pg.context.close()
    # iPad's top tabs follow the tab bar; the Mac sidebar stays Suki's own
    pg = t.page(b, w=820, h=1180, ua=None)
    info = pg.evaluate("""(()=>{const bar=document.querySelector('#barT .toptabs'), tabs=[...bar.querySelectorAll(':scope > .pk-tab')], k=bar.querySelector('.pk-tab-ind').getBoundingClientRect(), on=bar.querySelector('.pk-tab.on').getBoundingClientRect();
      return {kit:bar.classList.contains('pk-tabbar'), widths:[...new Set(tabs.map(x=>Math.round(x.getBoundingClientRect().width)))], fit:Math.abs(k.left-on.left)<1.5&&Math.abs(k.width-on.width)<1.5, h:Math.round(bar.getBoundingClientRect().height)}})()""")
    ok(info['kit'] and len(info['widths']) == 1 and info['fit'] and info['h'] == 44, f'iPad’s top tabs are the kit’s tab bar: equal tabs, the highlight under the picked one ({info})')
    pg.click('#barT .pk-tab[data-v=spending]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.tab") == 'spending' and pg.evaluate("document.querySelector('#barT .toptabs').style.getPropertyValue('--pk-i')") == '3', 'a top tab opens its tab and the highlight follows')
    t.shot(pg, 'parts-toptabs-ipad')
    pg.context.close()
    pg = t.page(b, w=1440, h=900, ua=None)
    ok(pg.evaluate("!document.querySelector('#side .pk-tabbar,#side .pk-tab') && !!document.querySelector('#side .sbi.on')"), 'the Mac sidebar stays Suki’s own (no kit tab bar)')
    pg.context.close()


def run(b, t):
    for k, f in (('pin', pin), ('settings', settings), ('motion', motion), ('diff', diff), ('alerts', alerts),
                 ('toasts', toasts), ('sheets', sheets), ('sizes', sizes), ('presses', presses), ('controls', controls),
                 ('bars', bars)):
        if wanted(k):
            f(b, t)
