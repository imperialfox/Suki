"""Onboarding (Q07): the Home Screen steps in Safari, the welcome card on a fresh install, tips next to the hidden
gestures, and Settings › Help. An existing install never sees the welcome, and backups leave all of it alone."""
import json, os, tempfile
from harness import READ, ready, sample

FRESH = "localStorage.setItem('test:fresh','1');localStorage.removeItem('suki:onboard')"
SAFARI = "Object.defineProperty(navigator,'standalone',{value:false,configurable:true})"
OB = "JSON.parse(localStorage.getItem('suki:onboard')||'null')"
# a tip never covers a main button or the tab bar
CLEAR = """(()=>{const t=document.getElementById('tip');if(!t)return 'no tip';const r=t.getBoundingClientRect();
 const bad=[...document.querySelectorAll('#app .cta,#layer .cta,#dock .tabbar')].filter(e=>{const b=e.getBoundingClientRect();
 return b.width&&!(b.right<r.left||b.left>r.right||b.bottom<r.top||b.top>r.bottom)});return bad.length?'covers '+bad.map(e=>e.className).join(','):''})()"""
TOUCH = """(a)=>{const [sel,type,x,y]=a;const el=document.querySelector(sel);const t=new Touch({identifier:1,target:el,clientX:x,clientY:y});
  el.dispatchEvent(new TouchEvent(type,{touches:type==='touchend'?[]:[t],changedTouches:[t],bubbles:true,cancelable:true}))}"""


def fresh(t, b, data=None, init=None, touch=True):
    """Suki as someone new opens it: nothing seen yet."""
    pg = t.page(b, data=data, touch=touch, init=init)
    pg.evaluate(FRESH); pg.reload(); ready(pg); pg.wait_for_timeout(150)
    return pg


def run(b, t):
    ok = t.ok

    # ── the welcome card: first Home Screen launch with nothing saved ──
    pg = fresh(t, b)
    ok(pg.evaluate("U.sheet") == 'welcome' and 'Welcome to Suki' in pg.inner_text('.sheet') and pg.locator('.sheet .wrow').count() == 3,
       'a fresh install opens with the welcome card and its three rows')
    ok(pg.locator('.sheet [data-a=close]').count() == 0 and pg.locator('.sheet .grab').count() == 0, 'it has no ✕ and no grab handle')
    pg.keyboard.press('Escape'); pg.mouse.click(5, 5); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") == 'welcome', 'Escape and tapping outside don’t dismiss it')
    sel = '.sheet .shead, .sheet .wel'
    pg.evaluate(TOUCH, ['.sheet .wel', 'touchstart', 200, 300]); pg.evaluate(TOUCH, ['.sheet .wel', 'touchmove', 200, 500]); pg.evaluate(TOUCH, ['.sheet .wel', 'touchend', 200, 500]); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") == 'welcome', 'and it can’t be dragged away')
    pg.click('.sheet [data-a=welcomeGo]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sheet") is None and pg.evaluate(OB)['welcome'] is True and pg.evaluate(OB)['tips'] is True, 'Continue closes it for good, with tips on for a new user')
    pg.reload(); ready(pg); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") is None, 'it doesn’t come back')

    # ── tips, one at a time, next to what they explain ──
    pg.evaluate("go('home')"); pg.wait_for_timeout(200)
    ok(pg.evaluate("TIPCUR") == 'pull' and 'Pull down to refresh' in pg.inner_text('#tip'), 'Home shows the pull-to-refresh tip')
    ok(pg.evaluate(CLEAR) == '', 'it doesn’t cover a main button or the tab bar: ' + pg.evaluate(CLEAR))
    pg.click('#tip [data-a=tipX]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("TIPCUR") is None and pg.evaluate(OB)['seen'].get('pull') is True, '✕ puts it away for good')
    pg.evaluate("go('till')"); pg.wait_for_timeout(200)
    ok(pg.evaluate("TIPCUR") == 'till', 'Quick Till shows the amount-chips tip')
    ok(pg.evaluate(CLEAR) == '', 'which stays clear of Log this bill and the tab bar: ' + pg.evaluate(CLEAR))
    pg.click('[data-a=cashAdd][data-v="100"]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("TIPCUR") is None and pg.evaluate(OB)['seen'].get('till') is True, 'using the chips is enough to make it go')
    pg.fill('#till-bill', '50'); pg.click('#tillLog'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sheet") == 'edit' and pg.locator('#tip.on').count() == 0, 'tips wait while a sheet is open')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
    pg.evaluate("go('till')"); pg.wait_for_timeout(200)
    ok(pg.evaluate("TIPCUR") is None, 'a tip that’s been done doesn’t return')
    pg.context.close()

    # with a few purchases: the swipe tip, and the drag-down tip on the first details sheet
    pg = fresh(t, b, data=sample())
    ok(pg.evaluate("U.sheet") is None and pg.evaluate(OB) == {'welcome': True, 'tips': False, 'seen': {}}, 'an install that already has data never sees the welcome, and tips start off')
    pg.evaluate(f"localStorage.setItem('suki:onboard',JSON.stringify({{welcome:true,tips:true,seen:{{pull:true}}}}))"); pg.reload(); ready(pg)
    pg.evaluate("go('spending')"); pg.wait_for_timeout(200)
    pg.evaluate("document.querySelector('#spendList .sw').scrollIntoView({block:'center'})"); pg.wait_for_timeout(300)
    ok(pg.evaluate("TIPCUR") == 'swipe', 'Spending shows the swipe tip once the first purchase is in view')
    ok(pg.evaluate(CLEAR) == '', 'clear of buttons and the tab bar: ' + pg.evaluate(CLEAR))
    s = '#spendList .sw .fg'
    box = pg.locator(s).first.bounding_box(); y = box['y'] + box['height'] / 2
    pg.evaluate(TOUCH, [s, 'touchstart', 300, y])
    for x in (280, 240, 200, 180): pg.evaluate(TOUCH, [s, 'touchmove', x, y])
    pg.evaluate(TOUCH, [s, 'touchend', 180, y]); pg.wait_for_timeout(300)
    ok(pg.evaluate("TIPCUR") is None and pg.evaluate(OB)['seen'].get('swipe') is True, 'swiping a purchase puts the tip away')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(400)
    pg.click('[data-a=openPurchase][data-k=a1]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("TIPCUR") == 'sheet' and 'Drag down' in pg.inner_text('#tip'), 'the first details sheet shows the drag-down tip')
    # the kit's sheet follows a pointer (Q27): drag its head down past the snap point and let go
    hd = '#layer .sheet .shead h2'
    hb = pg.locator(hd).bounding_box(); x0, y0 = hb['x'] + 20, hb['y'] + hb['height'] / 2
    pg.mouse.move(x0, y0); pg.mouse.down()
    for dy in (10, 60, 160, 320, 420): pg.mouse.move(x0, y0 + dy)
    pg.mouse.up(); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.sheet") is None and pg.evaluate(OB)['seen'].get('sheet') is True and pg.evaluate("TIPCUR") is None, 'dragging the sheet down closes it and the tip')

    # ── Settings › Help ──
    pg.evaluate("go('settings')"); pg.wait_for_timeout(100)
    pg.click('[data-a=openHelp]'); pg.wait_for_timeout(150)
    txt = pg.inner_text('#app')
    ok(pg.evaluate("U.tab") == 'help' and 'Show welcome' in txt and 'HIDDEN GESTURES' in txt.upper() and 'Add Suki to your Home Screen' in txt and pg.locator('#barL [data-v=settings]').count() == 1,
       'Help has Show welcome, Show tips, the hidden gestures, the Home Screen steps and a way back')
    ok(pg.locator('[data-a=tipsToggle]').is_checked(), 'the Show tips switch is on')
    pg.click('.row.toggle'); pg.wait_for_timeout(100)
    ok(pg.evaluate(OB)['tips'] is False, 'turning it off saves')
    pg.click('.row.toggle'); pg.wait_for_timeout(100)
    ok(pg.evaluate(OB)['tips'] is True and pg.evaluate(OB)['seen'] == {}, 'turning it on shows every tip again')
    pg.click('[data-a=showWelcome]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") == 'welcome', 'Show welcome plays it again')
    pg.click('.sheet [data-a=welcomeGo]'); pg.wait_for_timeout(150)
    pg.click('[data-a=openAhs]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") == 'ahs' and pg.locator('.sheet [data-a=close]').count() == 1 and pg.locator('.sheet [data-a=ahsGot]').count() == 0,
       'the Home Screen steps open from Help with a ✕, and no Got it')
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(100)
    pg.click('#barL [data-v=settings]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.tab") == 'settings', 'back goes to Settings')

    # ── backups leave all of it alone ──
    before = pg.evaluate(OB)
    pg.click('[data-a=exportBackup]'); pg.wait_for_timeout(400)
    with pg.expect_download() as dl:
        pg.click('.sheet .cta')
    raw = open(dl.value.path(), encoding='utf-8').read()
    ok('onboard' not in raw and 'welcome' not in raw and 'tips' not in raw, 'a backup doesn’t include what’s been seen')
    pg.evaluate("localStorage.setItem('suki:onboard',JSON.stringify({welcome:true,tips:false,seen:{till:true}}))")
    pg.set_input_files('#importIn', dl.value.path()); pg.wait_for_timeout(300)
    pg.click('#layer .pk-alert [data-a=yes]'); pg.wait_for_timeout(300)
    ok(pg.evaluate(OB) == {'welcome': True, 'tips': False, 'seen': {'till': True}}, 'and restoring one leaves this device’s settings as they were')
    pg.context.close()

    # ── in a Safari tab: the Home Screen steps, every time ──
    pg = fresh(t, b, init=SAFARI)
    ok(pg.evaluate("U.sheet") == 'ahs' and 'Add to Home Screen' in pg.inner_text('.sheet') and 'Open as Web App' in pg.inner_text('.sheet'),
       'opened in Safari, Suki shows the steps to add it to the Home Screen')
    ok(pg.locator('.sheet [data-a=close]').count() == 0 and pg.locator('.sheet [data-a=ahsGot]').count() == 1 and pg.locator('.sheet [data-a=ahsLater]').count() == 1,
       'with Got it and Not now, and no ✕')
    pg.click('.sheet [data-a=ahsLater]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") is None and 'next time' in pg.inner_text('.toast'), 'Not now says it’ll show again')
    ok(pg.evaluate("TIPCUR") is None and pg.evaluate(OB)['welcome'] is False, 'no welcome card or tips in Safari')
    pg.reload(); ready(pg); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") == 'ahs', 'and it shows again the next time')
    pg.click('.sheet [data-a=ahsGot]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") is None, 'Got it closes it')
    pg.context.close()

    # on a Mac (no touch, not iOS): no Home Screen steps, and no tips for touch gestures
    pg = fresh(t, b, touch=False, init=SAFARI)
    ok(pg.evaluate("U.sheet") == 'welcome', 'a computer browser gets the welcome card, not the Home Screen steps')
    pg.click('.sheet [data-a=welcomeGo]'); pg.wait_for_timeout(200)
    pg.evaluate("go('home')"); pg.wait_for_timeout(200)
    ok(pg.evaluate("TIPCUR") is None, 'and no pull-to-refresh tip without a touch screen')
    pg.context.close()
