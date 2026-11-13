"""Q32 PROBE (temporary): what WebKit does differently."""
import json
ON = "localStorage.setItem('suki:motion','1')"


def run(b, t):
    pg = t.page(b, w=402, h=874, init=ON)
    print('    PROBE raf rate', pg.evaluate("""new Promise(r=>{let n=0,ts=[];const t0=performance.now();const f=(x)=>{n++;ts.push(Math.round(x-t0));if(performance.now()-t0<1000)requestAnimationFrame(f);else r({n,first:ts.slice(0,5),last:ts.slice(-3)})};requestAnimationFrame(f)})"""))
    pg.evaluate("go('till')"); pg.fill('#till-bill', '789.50'); pg.fill('#till-cash', '1000'); pg.evaluate("document.activeElement.blur()"); pg.wait_for_timeout(50)
    pg.evaluate("window.__n=0;window.__ts=[];const R=window.requestAnimationFrame.bind(window);window.requestAnimationFrame=f=>R(x=>{__n++;__ts.push([Math.round(x),Math.round(performance.now())]);f(x)})")
    pg.click('#tillHdl')
    for i in range(8):
        pg.wait_for_timeout(150)
        print('    PROBE drawer', i, pg.evaluate("JSON.stringify({h:+DR.h.toFixed(2),raf:DR.raf,n:__n,ts:__ts.slice(-2)})"))
    pg.context.close()
    # a press inside a sheet
    pg = t.page(b, w=402, h=874, init=ON)
    pg.evaluate("openSheet('purchase',{id:'a1'})"); pg.wait_for_timeout(700)
    pg.evaluate("""window.__ev=[];['pointerdown','pointerup','pointercancel','gotpointercapture','lostpointercapture','mousedown','mouseup'].forEach(k=>document.addEventListener(k,e=>__ev.push(k+':'+(e.target.className||e.target.tagName).toString().slice(0,30)),true))""")
    sel = '#layer .sheet .shrow [data-a=close]'
    bx = pg.locator(sel).first.bounding_box()
    pg.mouse.move(bx['x'] + bx['width'] / 2, bx['y'] + bx['height'] / 2); pg.mouse.down(); pg.wait_for_timeout(300)
    print('    PROBE press held', pg.evaluate(f"[document.querySelector('{sel}').className, getComputedStyle(document.querySelector('{sel}')).scale, document.elementFromPoint({bx['x'] + bx['width'] / 2},{bx['y'] + bx['height'] / 2}).className]"))
    pg.evaluate("addEventListener('click', e=>{e.stopPropagation();e.preventDefault()}, {capture:true, once:true})")
    pg.mouse.up(); pg.wait_for_timeout(300)
    print('    PROBE press after', pg.evaluate(f"[document.querySelector('{sel}').className, getComputedStyle(document.querySelector('{sel}')).scale]"), pg.evaluate("__ev"))
    t.ok(True, 'probe ran')
