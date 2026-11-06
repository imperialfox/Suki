"""Q31 · a slow start never loses data. The audit's slow-storage case (F1, M01), kept: Suki's storage takes 4 s to answer
after a reload, longer than the launch screen waits (BOOT.CAP, 2.5 s). Home must say it's loading, not that nothing is
spent; a purchase logged meanwhile is added to the loaded ones, never saved over them; the open tab redraws when the
data lands; and a restore or Erase changes nothing until then."""
from harness import READ, ready

# 'test:slowdb' (milliseconds): reads from Suki's storage made in that time after the page starts answer only when it's
# up, as on a phone just restarted. Storage itself opens at once and writes go straight in, so on 2.33 a save in that
# time replaced the stored list (4 purchases became 1)
SLOW = """(()=>{let ms=0;try{ms=+localStorage.getItem('test:slowdb')||0}catch(e){}if(!ms)return;
 const get=IDBObjectStore.prototype.get;
 IDBObjectStore.prototype.get=function(){const r=get.apply(this,arguments);
  if(this.transaction.db.name!=='suki-db'||performance.now()>=ms)return r;
  let fn=null;Object.defineProperty(r,'onsuccess',{configurable:true,get(){return fn},set(f){fn=f}});
  r.addEventListener('success',e=>setTimeout(()=>fn&&fn.call(r,e),Math.max(0,ms-performance.now())));return r}})()"""
# counts every moment Home's empty state shows, from when the launch screen has gone
WATCH = """()=>{window.__empty=0;setInterval(()=>{const a=document.getElementById('app');if(a&&/Nothing spent yet|No purchases yet/.test(a.innerText))window.__empty++},50)}"""


def slow_reload(pg, ms=4000):
    pg.evaluate(f"localStorage.setItem('test:slowdb','{ms}')")
    pg.reload()
    ready(pg)
    pg.evaluate(WATCH)


def run(b, t):
    ok = t.ok
    pg = t.page(b, w=375, h=812, init=SLOW)
    ok(pg.evaluate("READY&&D.purchases.length") == 4, 'a normal start loads the 4 saved purchases at once')

    # 1. Home while loading, and a purchase logged meanwhile
    slow_reload(pg)
    ok(pg.evaluate("!READY"), 'the launch screen goes before the slow storage has answered')
    ok(pg.locator('.sumcard.loading').count() == 1 and 'Loading your purchases' in pg.inner_text('.sumcard'),
       'Home’s card says it’s loading your purchases')
    ok('Nothing spent yet' not in pg.inner_text('#app') and 'No purchases yet' not in pg.inner_text('#app'),
       'and never shows the empty state while loading')
    t.shot(pg, 'loading-375-light')
    ok(pg.evaluate("keepSafetyCopy('erase')") is False, 'a restore or Erase can’t start while loading, so nothing changes')
    pg.fill('#home-item', 'Halo-halo'); pg.fill('#home-price', '95'); pg.click('form[data-form=home] .cta')
    pg.wait_for_function("D.purchases.some(p=>p.item==='Halo-halo')")
    pg.evaluate("()=>{window.__held=null;save('purchases').then(ok=>window.__held=ok)}")
    pg.wait_for_timeout(200)
    ok(pg.evaluate("window.__held") is None, 'a save while loading is held, not written')
    pg.wait_for_function("READY", timeout=10000)
    pg.wait_for_function("window.__held===true", timeout=5000)
    ok(True, 'and answers once the real save has happened')
    pg.wait_for_function("!document.querySelector('.sumcard.loading')", timeout=5000)
    ok(pg.evaluate("D.purchases.length") == 5 and pg.evaluate("D.purchases[0].item") == 'Halo-halo',
       'when the data lands, the purchase logged meanwhile is added to the 4 saved ones, newest first')
    ok(pg.locator('.sumcard .door').count() == 2 and '₱3,301.50' in pg.inner_text('.sumcard'), 'and Home redraws with the full total')
    ok(pg.evaluate("window.__empty") == 0, 'Home never showed the empty state on the way')
    ok(len(pg.evaluate(READ, 'purchases')) == 5, 'storage holds all 5')
    pg.evaluate("localStorage.removeItem('test:slowdb')")
    pg.reload(); ready(pg)
    items = pg.evaluate("D.purchases.map(p=>p.item)")
    ok(len(items) == 5 and 'Halo-halo' in items and 'Chickenjoy bucket' in items, 'after a reload: 4 saved purchases plus 1 logged during the delay are 5')

    # 2. Undo while loading takes it back out, and nothing is added twice
    slow_reload(pg)
    pg.fill('#home-item', 'Taho'); pg.fill('#home-price', '20'); pg.click('form[data-form=home] .cta')
    pg.wait_for_function("D.purchases.some(p=>p.item==='Taho')")
    pg.evaluate("undoSave(D.purchases.find(p=>p.item==='Taho').id)")
    pg.wait_for_function("READY", timeout=10000)
    pg.wait_for_timeout(300)
    items = pg.evaluate("D.purchases.map(p=>p.item)")
    ok(len(items) == 5 and 'Taho' not in items and len(pg.evaluate(READ, 'purchases')) == 5, 'Undo while loading leaves the 5, with no copy')

    # 3. The open tab redraws when the data lands: Spending, and Home while a box has the cursor
    slow_reload(pg)
    pg.evaluate("go('spending')")
    pg.wait_for_function("READY", timeout=10000)
    pg.wait_for_function("document.getElementById('app').innerText.includes('Chickenjoy bucket')", timeout=5000)
    ok(True, 'Spending, opened while loading, redraws with your purchases when they land')
    pg.evaluate("go('home')")
    slow_reload(pg)
    pg.focus('#home-item'); pg.keyboard.type('Ube')
    pg.wait_for_function("READY", timeout=10000)
    pg.wait_for_function("!document.querySelector('.sumcard.loading')", timeout=5000)
    ok(pg.input_value('#home-item') == 'Ube' and pg.evaluate("document.activeElement.id") == 'home-item',
       'typing while the data lands keeps the cursor and what was typed')
    pg.keyboard.type(' halaya')
    ok(pg.input_value('#home-item') == 'Ube halaya', 'and typing carries on in the same box')

    # 4. Loading still in progress after the redraw is in place: a price note and a learned word are kept too
    slow_reload(pg)
    pg.evaluate("""D.observations.push({id:'oq',itemId:'bigas',itemName:'Bigas',price:50,date:localISO(),location:'',venue:'',note:''});
      D.learned.push({id:'kalesa',word:'kalesa',category:'Transport',label:'kalesa'});save('observations','learned')""")
    pg.wait_for_function("READY", timeout=10000)
    pg.wait_for_timeout(300)
    ok(pg.evaluate("D.observations.length") == 3 and len(pg.evaluate(READ, 'observations')) == 3, 'a price note added while loading joins the 2 saved ones')
    ok(pg.evaluate("D.learned.some(w=>w.word==='kalesa')") and any(w['word'] == 'kalesa' for w in pg.evaluate(READ, 'learned')), 'and so does a learned word')
    pg.evaluate("localStorage.removeItem('test:slowdb')")
    pg.context.close()

    # 5. Dark mode screenshot of the loading line, for the phone check's comparison
    pg = t.page(b, w=375, h=812, sc='dark', init=SLOW)
    slow_reload(pg)
    t.shot(pg, 'loading-375-dark')
    pg.wait_for_function("READY", timeout=10000)
    pg.context.close()
