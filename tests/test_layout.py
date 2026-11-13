"""Every screen at every size: iPhone (three sizes, upright and on its side), iPad both ways and Mac, light and dark.
Also the details pane on iPad and Mac, the tab bar staying clear of every page, keyboard shortcuts and pull to refresh.
Screenshots of each go to tests/output/."""
import os
from harness import READ, MKTOUCH

SIZES = [('iphone', 390, 844, True), ('iphone-small', 375, 667, True), ('iphone-se', 320, 568, True), ('landscape', 852, 393, True),
         ('ipad', 820, 1180, True), ('ipad-landscape', 1180, 820, True), ('mac', 1440, 900, False)]

# SUKI_LAYOUT_SIZES=iphone,mac checks only those sizes (the runner uses this to check sizes side by side)
_only = [x for x in os.environ.get('SUKI_LAYOUT_SIZES', '').split(',') if x]
if _only: SIZES = [x for x in SIZES if x[0] in _only]

FITS = "document.documentElement.scrollWidth<=innerWidth"
TABS_IN = """(()=>{const b=[...document.querySelectorAll('.tabbar button,.toptabs button,.side-nav .sbi')];if(!b.length)return 'no tabs';
 const off=b.filter(e=>{const r=e.getBoundingClientRect();return r.width&&(r.left<0||r.right>innerWidth+0.5||r.bottom>innerHeight+0.5||r.top<0)});return off.length?'tabs off screen':''})()"""
INSIDE = "sel=>{const e=document.querySelector(sel);if(!e)return false;const r=e.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+0.5&&r.top>=0&&r.bottom<=innerHeight+0.5}"
CLIPPED = """(()=>{const out=[];document.querySelectorAll('#app .row,#app .card,#app .chip:not(.scroller .chip),.sheet .row,.sheet .card').forEach(e=>{
 if(e.closest('.scroller'))return;const r=e.getBoundingClientRect(),p=(e.closest('.sheet')||document.documentElement).getBoundingClientRect();
 if(r.width&&(r.right>p.right+1||r.left<p.left-1))out.push(e.className)});return out.slice(0,3).join(', ')})()"""
TOUCH = """(a)=>{""" + MKTOUCH + """const [type,y]=a;const h=document.querySelector('#app h1'),e=mkTouch(type,h,200,y);h.dispatchEvent(e);return e.defaultPrevented}"""


def run(b, t):
    ok = t.ok
    for name, w, h, touch in SIZES:
        for sc in ['light', 'dark']:
            pg = t.page(b, w, h, sc, touch=touch, **({'ua': None} if name == 'mac' else {}))
            tag = f'{name}-{sc}'
            bad = []
            def check(screen):
                pg.wait_for_timeout(120)
                if not pg.evaluate(FITS): bad.append(screen + ' scrolls sideways')
                if pg.evaluate("!!U.sheet"):
                    if not pg.evaluate(INSIDE, '.sheet'): bad.append(screen + ' sheet off screen')
                else:
                    m = pg.evaluate(TABS_IN)
                    if m: bad.append(screen + ' ' + m)
                c = pg.evaluate(CLIPPED)
                if c: bad.append(screen + ' cut off: ' + c)
                t.shot(pg, f'{tag}-{screen}', full_page=not pg.evaluate("!!U.sheet"))
            for tab in ['home', 'till', 'search', 'spending', 'convert', 'history', 'settings', 'help']:
                pg.evaluate(f"go('{tab}')"); check(tab)
            pg.evaluate("go('home');U.more=true;rerender()"); check('home-more')
            pg.evaluate("go('spending');openSheet('purchase',{id:'a1'})"); check('purchase')
            pg.click('.sheet [data-a=editPurchase]'); check('edit')
            pg.evaluate("U.stack=[];U.sheet=null;rerender();go('search');openSheet('item',{id:'bigas'})"); check('item')
            pg.click('.sheet [data-a=obsForm]'); check('item-note')
            pg.evaluate("U.sheet=null;U.obsFor=null;rerender();openSheet('erase')"); check('erase')
            pg.evaluate("U.sheet=null;rerender();go('till');U.till={bill:'789.5',cash:'500'};rerender()"); check('till-short')
            pg.evaluate("U.sheet=null;rerender();go('history');openSheet('news',{id:'2026-10-22|peso'})"); check('news')
            pg.evaluate("openSheet('cbrate',{},true)"); check('central-bank')
            pg.evaluate("U.stack=[];U.sheet=null;rerender()")
            pg.evaluate("openSheet('welcome')"); check('welcome')
            pg.evaluate("U.sheet=null;rerender();openSheet('ahs',{safari:true})"); check('home-screen-steps')
            pg.evaluate("U.sheet=null;rerender()")
            ok(not bad, f'{tag}: every screen fits' + (' — ' + '; '.join(bad) if bad else ''))

            if name in ('ipad', 'ipad-landscape', 'mac') and sc == 'light':
                pg.evaluate("U.sheet=null;go('spending')")
                pg.click('[data-a=openPurchase][data-k=a3]'); pg.wait_for_timeout(150)
                ok(pg.evaluate("U.sheet") is None and 'Groceries' in pg.inner_text('.pane') and pg.locator('.row.sel').count() == 1,
                   f'{name}: a purchase opens beside the list')
                pg.click('.pane [data-a=editPurchase]'); pg.wait_for_timeout(150)
                ok(pg.evaluate("U.sheet") == 'edit' and pg.evaluate(INSIDE, '.sheet'), f'{name}: Edit opens in the middle of the screen')
                pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
                pg.evaluate("go('search')"); pg.click('[data-a=openItem][data-k=itlog]'); pg.wait_for_timeout(150)
                ok(pg.evaluate("U.sheet") is None and '₱8.23' in pg.inner_text('.pane'), f'{name}: an item opens beside the results')
                pg.evaluate("go('home')"); pg.wait_for_timeout(100)
                ok(pg.locator('.dash > div').count() == 2, f'{name}: Home is two columns')
                if name != 'mac':
                    ok(pg.locator('.toptabs').count() == (1 if name == 'ipad' else 0) and pg.locator('#dock .tabbar').count() == 0,
                       f'{name}: tabs move to the top (or the sidebar)')
            if name == 'mac' and sc == 'light':
                ok(pg.is_visible('.side-nav') and pg.locator('.side-nav [data-v=settings]').count() == 1, 'Mac: a sidebar with Settings')
                pg.keyboard.press('Control+4'); pg.wait_for_timeout(150)
                ok(pg.evaluate("U.tab") == 'spending', 'Mac: Cmd/Ctrl+4 opens Spending')
            if name == 'landscape' and sc == 'light':
                pg.evaluate("go('home')")
                ok(pg.locator('.dash > div').count() == 2 and pg.evaluate("document.querySelector('.tabbar button').getBoundingClientRect().height") <= 44,
                   'iPhone on its side: two columns and a compact tab bar')
            pg.context.close()

    if not any(x[0] == 'iphone' for x in SIZES): return
    # the tab bar stays full size however far you scroll, and the end of every page clears it
    pg = t.page(b, touch=True)
    pg.evaluate("go('search')"); pg.evaluate("window.scrollTo(0,300)"); pg.wait_for_timeout(100); pg.evaluate("window.scrollTo(0,700)"); pg.wait_for_timeout(500)
    r = pg.evaluate("(()=>{const b=document.querySelector('.tabbar');return {min:b.classList.contains('min'),w:b.getBoundingClientRect().width,n:[...b.querySelectorAll('button')].filter(x=>x.getBoundingClientRect().width>40).length}})()")
    ok(not r['min'] and r['n'] == 5 and r['w'] > 300, f'scrolling down leaves the tab bar full size with all five tabs ({r})')
    for w, h in [(390, 844), (844, 390)]:
        pg.set_viewport_size({'width': w, 'height': h}); pg.wait_for_timeout(300)
        for tb in ['home', 'till', 'search', 'spending', 'convert', 'settings']:
            pg.evaluate(f"go('{tb}')"); pg.evaluate("window.scrollTo(0,1e6)"); pg.wait_for_timeout(150)
            gap = pg.evaluate("""(()=>{const top=document.querySelector('#dock .tabbar').getBoundingClientRect().top;let last=0;
              for(const e of document.querySelectorAll('main *')){const r=e.getBoundingClientRect();if(r.width&&r.height&&r.bottom>last)last=r.bottom}return Math.round(top-last)})()""")
            ok(16 <= gap, f'{w}x{h} {tb}: the end of the page sits clear of the tab bar ({gap}px)')
    pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(300)
    # the tab bar sits where Apple's does on iPhone upright: 21pt from the bottom edge, 21pt sides (Q04)
    pg.evaluate("go('home')"); pg.wait_for_timeout(100)
    r = pg.evaluate("(()=>{const b=document.querySelector('#dock .tabbar').getBoundingClientRect();return [Math.round(innerHeight-b.bottom),Math.round(b.left),Math.round(innerWidth-b.right)]})()")
    ok(r[0] == 21 and r[1] >= 21 and r[2] >= 21, f'the tab bar sits 21pt from the bottom with 21pt sides ({r})')
    # the top bar has no card; once you scroll, the soft edge shows with the compact title
    pg.evaluate("go('search')"); pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(500)
    ok(not pg.evaluate("document.getElementById('bar').classList.contains('glass')") and pg.evaluate("getComputedStyle(document.querySelector('.edge')).opacity") == '0', 'at the top there’s no bar, just the title')
    pg.evaluate("window.scrollTo(0,400)"); pg.wait_for_timeout(300)
    ok(pg.evaluate("getComputedStyle(document.querySelector('.edge')).opacity") == '1' and pg.evaluate("getComputedStyle(document.getElementById('barT')).opacity") == '1', 'scrolling shows the soft edge and the compact title')
    pg.evaluate("window.scrollTo(0,0)")
    # every catalogue item has its own picture
    pg.wait_for_timeout(100)
    g = pg.evaluate("['jeepney','bigas','itlog','beer','haircut'].map(id=>tile('', false, id))")
    ok(len(set(g)) == 5, 'items get their own glyphs')
    # a very long total on Home steps down a size instead of breaking across lines (Q06)
    pg.set_viewport_size({'width': 320, 'height': 568}); pg.wait_for_timeout(200)
    pg.evaluate("D.purchases[0].price=30000000;go('home')"); pg.wait_for_timeout(100)
    lines = pg.evaluate("document.querySelector('.sumcard .big').getClientRects().length===1&&document.querySelector('.sumcard .big').getBoundingClientRect().height<40")
    ok(lines and pg.evaluate("document.querySelector('.sumcard').classList.contains('long')"), 'a ₱30,000,000 total fits on one line on a small iPhone')
    pg.evaluate("D.purchases[0].price=459;rerender()"); pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(200)
    # pull to refresh on Home
    pg.evaluate("go('home')")
    def drag(y0, y1, steps=10):
        pg.evaluate(TOUCH, ['touchstart', y0])
        for i in range(1, steps + 1): pg.evaluate(TOUCH, ['touchmove', y0 + (y1 - y0) * i / steps])
    drag(200, 330)
    ok(pg.evaluate("parseFloat((document.getElementById('app').style.transform||'').replace(/[^0-9.]/g,''))||0") > 0, 'pull to refresh: the page follows your finger')
    pg.evaluate(TOUCH, ['touchend', 330]); pg.wait_for_timeout(500)
    ok(not pg.evaluate("PTR.busy") and pg.evaluate("document.getElementById('app').style.transform") == '', 'a short pull springs back')
    pg.evaluate("""(async()=>{const db=await new Promise(r=>{const q=indexedDB.open('suki-db',1);q.onsuccess=()=>r(q.result)});
      const p=D.purchases.concat([{id:'zz',item:'From another tab',price:5,date:D.purchases[0].date,category:'Other'}]);
      await new Promise(r=>{const t=db.transaction('kv','readwrite');t.objectStore('kv').put(p,'purchases');t.oncomplete=r});db.close()})()""")
    drag(200, 520); pg.evaluate(TOUCH, ['touchend', 520]); pg.wait_for_timeout(300); ok(pg.evaluate("PTR.busy"), 'a long pull refreshes')
    pg.wait_for_timeout(1300)
    ok(not pg.evaluate("PTR.busy") and pg.evaluate("D.purchases.some(p=>p.id==='zz')"), 'refreshing re-reads saved data')
    pg.evaluate("go('till')"); drag(200, 520); pg.evaluate(TOUCH, ['touchend', 520]); pg.wait_for_timeout(200)
    ok(not pg.evaluate("PTR.busy"), 'no pull to refresh on Quick Till')
    pg.context.close()

    # motion on: sheets rise and can be closed mid-way; Reduce Motion only fades
    pg = t.page(b, touch=True, init="localStorage.setItem('suki:motion','1')")
    pg.evaluate("go('spending');openSheet('purchase',{id:'a1'})"); pg.wait_for_timeout(30)
    an = pg.evaluate("document.querySelector('.sheet').getAnimations().map(a=>a.transitionProperty||a.animationName)")
    ok('translate' in an, f'with motion on, a sheet rises (the kit’s sheet, Q27: {an})')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(50)
    ok(pg.evaluate("!document.querySelector('#layer .sheet')&&!document.body.classList.contains('sheet-open')"), 'closing mid-rise leaves nothing behind')
    pg.context.close()
    pg = t.page(b, touch=True, init="localStorage.setItem('suki:motion','1')", ctx_args={'reduced_motion': 'reduce'})
    pg.evaluate("go('spending');openSheet('purchase',{id:'a1'})"); pg.wait_for_timeout(30)
    tr = pg.evaluate("(e=>[getComputedStyle(e).translate,e.getAnimations().map(a=>a.transitionProperty)])(document.querySelector('.sheet'))")
    ok(tr[0] in ('none', '0px', '0px 0px') and 'translate' not in tr[1] and pg.evaluate("getComputedStyle(document.querySelector('.wrap')).transform") == 'none',
       f'Reduce Motion: the sheet fades in without moving, and the page behind stays still ({tr})')
    pg.context.close()
    # Settings › Accessibility: Reduce Motion can be turned on in the app, whatever the iPhone says, and it stays on this device (Q04)
    pg = t.page(b, touch=True, init="localStorage.setItem('suki:motion','1')")
    pg.evaluate("go('settings')"); pg.click('[data-a=openAccess]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") == 'access' and pg.locator('#reduceSeg [aria-pressed=true]').inner_text() == 'Match iPhone', 'Accessibility starts on Match iPhone')
    pg.click('#reduceSeg [data-v=on]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("document.documentElement.classList.contains('motion-reduced')") and pg.evaluate("localStorage.getItem('suki:reduceMotion')") == 'on', 'turning it on reduces motion now')
    pg.reload(); pg.wait_for_function("!document.getElementById('splash')")
    ok(pg.evaluate("document.documentElement.classList.contains('motion-reduced')"), 'and after reopening')
    pg.evaluate("openSheet('purchase',{id:'a1'})"); pg.wait_for_timeout(30)
    an = pg.evaluate("(e=>[getComputedStyle(e).translate,e.getAnimations().map(a=>a.transitionProperty)])(document.querySelector('.sheet'))")
    ok(an[0] in ('none', '0px', '0px 0px') and 'translate' not in an[1], f'with it on, sheets fade in instead of rising ({an})')
    pg.evaluate("closeSheet();openSheet('access')"); pg.wait_for_timeout(100)
    pg.click('#reduceSeg [data-v=auto]'); pg.wait_for_timeout(100)
    ok(not pg.evaluate("document.documentElement.classList.contains('motion-reduced')") and pg.evaluate("localStorage.getItem('suki:reduceMotion')") is None, 'Match iPhone goes back to following the iPhone')
    pg.click('.sheet .toggle'); pg.wait_for_timeout(100)
    ok(pg.evaluate("MOTION.speed()") == 4, 'Slow motion plays things four times slower')
    pg.click('.sheet .toggle'); pg.wait_for_timeout(100)
    ok(pg.evaluate("MOTION.speed()") == 1, 'and turns off again')
    bk = pg.evaluate("String(backupJSON(new Date()))")
    ok(len(bk) > 100 and 'reduceMotion' not in bk and 'suki:motion' not in bk, 'neither setting is in backups')
    pg.context.close()
