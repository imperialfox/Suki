"""Q33 · other windows and an error notice. The audit's two-window case (F2, M02), kept: two tabs of Suki share one
storage, and before 2.35 the second to save wrote away the first one's purchases (each kept the list it loaded). Now a
window reloads when another saves, with a toast, and a save from a window that missed that checks first, reloads and
keeps only what it added itself. Also the global error notice (M16) and the delete alerts' "Delete" (M15)."""
from harness import READ, url, ready

TOAST = "[...document.querySelectorAll('.toast:not(.pk-leaving)')].map(e=>e.innerText).join('|')"


def log(pg, item, price):
    pg.evaluate("go('home')")
    pg.fill('#home-item', item); pg.fill('#home-price', price); pg.click('form[data-form=home] .cta')
    pg.wait_for_function("n=>D.purchases.some(p=>p.item===n)", arg=item)


def stored(pg):
    return sorted(p['item'] for p in pg.evaluate(READ, 'purchases'))


def second(t, pg, tag):
    """Another window of the same Suki (same storage), as a second Safari tab would be."""
    p2 = pg.context.new_page()
    p2.on('pageerror', lambda e: t.errors.append(f'{tag}: {str(e).splitlines()[0]}'))
    p2.goto(url()); ready(p2)
    return p2


def windows(b, t):
    ok = t.ok
    a = t.page(b, w=375, h=812)
    bb = second(t, a, 'windows second')
    ok(a.evaluate("D.purchases.length") == 4 and bb.evaluate("D.purchases.length") == 4, 'two windows each load the 4 saved purchases')

    # 1. each logs one: both are kept, and each window shows the other's
    log(a, 'Halo-halo', '95')
    bb.wait_for_function("D.purchases.some(p=>p.item==='Halo-halo')", timeout=5000)
    ok('Updated from another window' in bb.evaluate(TOAST), 'the other window reloads straight away, with "Updated from another window"')
    ok('Halo-halo' in bb.inner_text('#app'), 'and its Home shows the new purchase')
    ok('Updated from another window' not in a.evaluate(TOAST), 'the window that saved gets no such toast')
    log(bb, 'Taho', '20')
    a.wait_for_function("D.purchases.some(p=>p.item==='Taho')", timeout=5000)
    names = stored(a)
    ok(len(names) == 6 and 'Halo-halo' in names and 'Taho' in names, f'two windows each logging a purchase keep both (6 saved: {names})')
    a.reload(); ready(a)
    ok(a.evaluate("D.purchases.length") == 6, 'and both are there after a reload')

    # 2. a window that missed the message (asleep, say) checks before it saves
    bb.evaluate("CHAN.close();CHAN=null")
    log(a, 'Balut', '25')
    bb.wait_for_timeout(300)
    ok(not bb.evaluate("D.purchases.some(p=>p.item==='Balut')"), 'a window that missed the message still has the old list')
    log(bb, 'Buko juice', '40')
    bb.wait_for_function("D.purchases.some(p=>p.item==='Balut')", timeout=5000)
    names = stored(a)
    ok('Balut' in names and 'Buko juice' in names and len(names) == 8,
       f'its save finds the other window saved first, reloads and keeps both (8 saved: {names})')
    ok('Updated from another window' in bb.evaluate(TOAST), 'and says it was updated from another window')
    ok(bb.evaluate("D.purchases[0].item") == 'Buko juice' and bb.evaluate("D.purchases.length") == 8,
       'its own purchase stays first, newest first, with nothing doubled')
    bb.reload(); ready(bb)

    # 3. a delete in one window shows in the other, and isn't undone by the other's next save
    gone = a.evaluate("D.purchases.find(p=>p.item==='Taho').id")
    bb.evaluate("k=>{go('spending');ACT.delPurchase({dataset:{k}})}", gone)
    bb.click('#layer .pk-alert [data-a=yes]')
    a.wait_for_function("k=>!D.purchases.some(p=>p.id===k)", arg=gone, timeout=5000)
    ok(True, 'a purchase deleted in one window goes from the other')
    log(a, 'Fishball', '15')
    names = stored(a)
    ok('Taho' not in names and 'Fishball' in names, 'and the other window’s next save doesn’t bring it back')

    # 4. a price note and a learned word from another window
    bb.wait_for_function("D.purchases.some(p=>p.item==='Fishball')", timeout=5000)
    bb.evaluate("D.observations.push({id:'w2',itemId:'bigas',itemName:'Bigas',price:55,date:localISO(),location:'',venue:'',note:''});save('observations')")
    a.wait_for_function("D.observations.some(o=>o.id==='w2')", timeout=5000)
    ok(True, 'a price note saved in one window reaches the other')

    # 5. only the rate changed: quietly taken, no toast
    a.wait_for_timeout(3600)
    bb.evaluate("D.rate=Object.assign({},D.rate,{value:75.5,cachedAt:new Date().toISOString()});save('rate')")
    a.wait_for_function("D.rate&&D.rate.value===75.5", timeout=5000)
    ok('Updated from another window' not in a.evaluate(TOAST), 'a newer rate from another window is taken quietly, with no toast')

    # 6. one window open on its own changes nothing: a save writes once, with no reload
    bb.close()
    n = a.evaluate("async()=>{let r=0;const f=readData;readData=async e=>{r++;return f(e)};D.purchases.unshift({id:'solo',item:'Solo',price:9,date:localISO(),category:'Other'});await save('purchases');readData=f;return r}")
    ok(n == 0 and 'Solo' in stored(a), 'on its own, a save just writes, with no extra reload')
    a.context.close()


def errors(b, t):
    ok = t.ok
    for w in (375, 402):
        pg = t.page(b, w=w, h=812)
        before = pg.evaluate(READ, 'purchases')
        pg.evaluate("setTimeout(()=>{throw new Error('Test fault')})")
        pg.wait_for_selector('.toast.sticky.sk-error', timeout=5000)
        ok(pg.inner_text('.toast.sticky') .startswith('Something went wrong. Your records are safe.'),
           f'{w}: an unexpected error shows the sticky notice, "Something went wrong. Your records are safe."')
        ok(pg.get_attribute('.toast.sticky', 'role') == 'alert' and pg.locator('.toast.sticky button').inner_text() == 'OK',
           f'{w}: it’s an alert with OK, Suki’s own sticky warning (S04)')
        log_ = pg.evaluate("JSON.parse(localStorage.getItem('suki:errors'))")
        ok(len(log_) == 1 and 'Test fault' in log_[0]['msg'] and log_[0]['version'] == pg.evaluate("APP_VERSION") and log_[0]['at'],
           f'{w}: the error is kept on this device under suki:errors, with when and the version')
        ok(pg.evaluate(READ, 'purchases') == before and pg.evaluate("D.purchases.length") == 4, f'{w}: nothing saved or lost')
        ok('errors' not in pg.evaluate("backupJSON(new Date())"), f'{w}: suki:errors isn’t in a backup')
        t.shot(pg, f'error-{w}-light')
        pg.click('.toast.sticky button')
        ok(pg.locator('.toast.sticky').count() == 0, f'{w}: OK closes it')
        if w == 375:
            pg.evaluate("setTimeout(()=>{Promise.reject(new Error('Test reject'))})")
            pg.wait_for_selector('.toast.sticky.sk-error', timeout=5000)
            last = pg.evaluate("JSON.parse(localStorage.getItem('suki:errors')).pop()")
            ok('Test reject' in last['msg'] and last['where'] == 'promise', 'a promise that fails with nobody catching it shows the notice too')
            pg.click('.toast.sticky button')
            pg.evaluate("for(let i=0;i<25;i++)setTimeout(()=>{throw new Error('Fault '+i)})")
            pg.wait_for_function("JSON.parse(localStorage.getItem('suki:errors')).some(e=>e.msg.includes('Fault 24'))")
            kept = pg.evaluate("JSON.parse(localStorage.getItem('suki:errors'))")
            ok(len(kept) == 20 and 'Fault 24' in kept[-1]['msg'], 'only the last 20 are kept')
            ok(pg.locator('.toast.sticky').count() == 1, 'many at once show one notice')
            pg.click('.toast.sticky button')
            pg.evaluate("for(let i=0;i<30;i++)setTimeout(()=>{throw new Error('Same fault')})")
            pg.wait_for_function("(JSON.parse(localStorage.getItem('suki:errors')).pop().n||0)>=30")
            ok(pg.evaluate("JSON.parse(localStorage.getItem('suki:errors')).filter(e=>e.msg.includes('Same fault')).length") == 1,
               'the same error over and over is counted once, not kept twenty times')
            pg.click('.toast.sticky button')
            pg.evaluate("toast('Couldn’t save. Your device may be out of space, so back up soon.', null, true);setTimeout(()=>{throw new Error('Later fault')})")
            pg.wait_for_function("JSON.parse(localStorage.getItem('suki:errors')).some(e=>e.msg.includes('Later fault'))")
            ok(pg.inner_text('.toast.sticky').startswith('Couldn’t save') and pg.locator('.toast.sticky').count() == 1,
               'a "Couldn’t save" warning on screen stays, as it matters more')
            pg.click('.toast.sticky button')
            # after an error the app still works
            log(pg, 'After fault', '10')
            ok('After fault' in stored(pg), 'after an error Suki still saves')
        pg.context.close()
    # the expected errors were thrown on purpose: they're not faults
    t.errors[:] = [e for e in t.errors if not any(s in e for s in ('Test fault', 'Test reject', 'Fault ', 'Same fault', 'Later fault'))]


def delete_label(b, t):
    ok = t.ok
    for w in (375, 402):
        pg = t.page(b, w=w, h=812)
        pg.evaluate("go('spending')")
        pg.evaluate("ACT.delPurchase({dataset:{k:'a1'}})")
        pg.wait_for_selector('#layer .pk-alert [data-a=yes]')
        y = pg.locator('#layer .pk-alert [data-a=yes]')
        h = pg.evaluate("""(()=>{const y=document.querySelector('#layer .pk-alert [data-a=yes]'),n=document.querySelector('#layer .pk-alert [data-a=no]');
          const r=document.createRange();r.selectNodeContents(y);const lines=new Set([...r.getClientRects()].map(x=>Math.round(x.top)));return [lines.size,y.getBoundingClientRect().height,n.getBoundingClientRect().height]})()""")
        ok(y.inner_text().strip() == 'Delete' and h[0] == 1 and abs(h[1] - h[2]) < 1,
           f'{w}: delete a purchase: the red button says "Delete" on one line ({h})')
        t.shot(pg, f'delete-{w}-light')
        pg.click('#layer .pk-alert [data-a=no]')
        pg.evaluate("go('search')")
        pg.evaluate("ACT.delObs({dataset:{k:'o1'}})")
        pg.wait_for_selector('#layer .pk-alert [data-a=yes]')
        ok(pg.locator('#layer .pk-alert [data-a=yes]').inner_text().strip() == 'Delete', f'{w}: delete a price note: "Delete" too')
        pg.context.close()


def run(b, t):
    windows(b, t)
    errors(b, t)
    delete_label(b, t)
