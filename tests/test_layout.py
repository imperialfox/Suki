"""Every screen at every size: iPhone (three sizes, upright and on its side), iPad both ways and Mac, light and dark.
Also the details pane on iPad and Mac, the shrinking tab bar, keyboard shortcuts and pull to refresh.
Screenshots of each go to tests/output/."""
import os
from harness import READ

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
TOUCH = """(a)=>{const [type,y]=a;const t=new Touch({identifier:1,target:document.querySelector('#app h1'),clientX:200,clientY:y});
  const e=new TouchEvent(type,{touches:type==='touchend'?[]:[t],changedTouches:[t],bubbles:true,cancelable:true});document.querySelector('#app h1').dispatchEvent(e);return e.defaultPrevented}"""


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
            for tab in ['home', 'till', 'search', 'spending', 'convert', 'settings']:
                pg.evaluate(f"go('{tab}')"); check(tab)
            pg.evaluate("go('home');U.more=true;rerender()"); check('home-more')
            pg.evaluate("go('spending');openSheet('purchase',{id:'a1'})"); check('purchase')
            pg.click('.sheet [data-a=editPurchase]'); check('edit')
            pg.evaluate("U.stack=[];U.sheet=null;rerender();go('search');openSheet('item',{id:'bigas'})"); check('item')
            pg.click('.sheet [data-a=obsForm]'); check('item-note')
            pg.evaluate("U.sheet=null;U.obsFor=null;rerender();openSheet('erase')"); check('erase')
            pg.evaluate("U.sheet=null;rerender();go('till');U.till={bill:'789.5',cash:'500'};rerender()"); check('till-short')
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
                ok(pg.evaluate("U.sheet") is None and '₱8.25' in pg.inner_text('.pane'), f'{name}: an item opens beside the results')
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
    # the tab bar shrinks while you scroll down, centred, and comes back
    pg = t.page(b, touch=True)
    pg.evaluate("go('search')"); pg.evaluate("window.scrollTo(0,300)"); pg.wait_for_timeout(100); pg.evaluate("window.scrollTo(0,700)"); pg.wait_for_timeout(500)
    r = pg.evaluate("(()=>{const b=document.querySelector('.tabbar');const r=b.getBoundingClientRect();return {min:b.classList.contains('min'),c:r.left+r.width/2,w:r.width}})()")
    ok(r['min'] and abs(r['c'] - 195) < 2 and r['w'] < 70, f'the tab bar shrinks to the current tab, centred ({r})')
    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(500)
    ok(not pg.evaluate("document.querySelector('.tabbar').classList.contains('min')"), 'and comes back at the top')
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
    pg.evaluate("go('spending');openSheet('purchase',{id:'a1'})")
    an = pg.evaluate("document.querySelector('.sheet').getAnimations().map(a=>a.animationName)")
    ok('up' in an, f'with motion on, a sheet rises ({an})')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(50)
    ok(pg.evaluate("!document.querySelector('#layer .sheet')&&!document.body.classList.contains('sheet-open')"), 'closing mid-rise leaves nothing behind')
    pg.context.close()
    pg = t.page(b, touch=True, init="localStorage.setItem('suki:motion','1')", ctx_args={'reduced_motion': 'reduce'})
    pg.evaluate("go('spending');openSheet('purchase',{id:'a1'})"); pg.wait_for_timeout(30)
    tr = pg.evaluate("getComputedStyle(document.querySelector('.sheet')).transform")
    ok(tr in ('none', 'matrix(1, 0, 0, 1, 0, 0)') and pg.evaluate("getComputedStyle(document.querySelector('.wrap')).transform") == 'none',
       'Reduce Motion: the sheet fades in without moving, and the page behind stays still')
    pg.context.close()
