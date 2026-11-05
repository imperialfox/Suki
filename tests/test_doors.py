"""Navigation doors (Q08): Home's two figures, Spending's +, logging on a calendar day, a purchase leading to its
item's prices (whole words only), words that name a place, and Settings rows that open what they name.
Door rules (Q24): Home's Show all doors, the gear, Help and Rate history and their Back, the delete message, Mac's
Settings section and the zooms on iPad and Mac."""
import datetime as dt
from harness import sample, day, today, RATE


def tab(pg, name):
    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(80)
    pg.click(f'#dock [data-v={name}]'); pg.wait_for_timeout(120)


def data():
    d = sample()
    extra = [('w1', 'Spaghetti', 2), ('w2', 'Mangoes', 2), ('w3', 'Fish balls', 3), ('w4', 'Banana', 3), ('w5', 'Jeepney to Cubao', 4)]
    for i, name, n in extra:
        d['purchases'].append({'id': i, 'item': name, 'price': 50, 'date': day(n), 'category': 'Food & drink', 'location': '', 'venue': '',
                               'payment': 'Cash', 'notes': '', 'gbpAtPurchase': None, 'rateAtPurchase': None})
    return d


def run(b, t):
    run_q08(b, t)
    run_q24(b, t)


def run_q08(b, t):
    ok = t.ok
    pg = t.page(b, data=data())
    n0 = pg.evaluate("D.purchases.length")

    # ── 1 · Home's card is two doors ─────────────────────────────
    ok(pg.locator('.sumcard .door').count() == 2 and pg.locator('.sumcard[data-a]').count() == 0, 'Home’s summary card holds two doors, not one')
    ok(pg.inner_text('.sumcard .door[data-v=all] .cap').endswith('›') and pg.inner_text('.sumcard .door[data-v=day] .cap').endswith('›'),
       'each caption ends in a small ›')
    pg.evaluate("U.range='week';U.roff=2;U.cat='Transport';U.filter='zzz'")
    pg.click('.sumcard .door[data-v=all]'); pg.wait_for_timeout(120)
    ok(pg.evaluate("U.tab==='spending'&&U.range==='all'&&U.cat==='all'&&U.filter===''"), 'Total spent opens Spending on All, with no filter left over')
    tab(pg, 'home')
    pg.click('.sumcard .door[data-v=day]'); pg.wait_for_timeout(120)
    ok(pg.evaluate("U.tab==='spending'&&U.range==='day'&&U.roff===0") and pg.inner_text('#spendSum .plabel') == 'Today',
       'Today opens Spending on D, for today')
    ok('Chickenjoy bucket' in pg.inner_text('#spendList') and 'Jeepney' not in pg.inner_text('#spendList'), 'and the list shows only today’s purchases')

    # ── 2 · Spending's + opens the same Log sheet ────────────────
    ok(pg.locator('#barR [data-a=newPurchase]').count() == 1, 'Spending’s top bar has a + circle')
    pg.click('#barR [data-a=newPurchase]'); pg.wait_for_timeout(120)
    ok(pg.evaluate("U.sheet") == 'edit' and pg.inner_text('.sheet h2') == 'Log a purchase' and pg.input_value('#edit-date') == today.isoformat(),
       'the + opens the Log sheet, dated today')
    pg.fill('#edit-item', 'Halo-halo'); pg.fill('#edit-price', '120'); pg.click('.sheet .cta'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") is None and pg.evaluate("D.purchases.length") == n0 + 1 and 'Halo-halo' in pg.inner_text('#spendList'),
       'saving closes it and the purchase is in the list')
    tab(pg, 'search')
    ok(pg.locator('#barR [data-a=newPurchase]').count() == 0, 'the + is only on Spending')

    # ── 3 · Logging on a calendar day ────────────────────────────
    tab(pg, 'home')
    pg.click('#app h1 .hometitle'); pg.wait_for_timeout(120)
    ok('Log a purchase on today' in pg.inner_text('.sheet'), 'today, picked in the calendar, offers “Log a purchase on today”')
    past = day(6)
    pg.evaluate(f"U.calM='{past[:8]}01';U.calD=null;rerender()"); pg.wait_for_timeout(80)
    pg.click(f'.sheet .cday[data-v="{past}"]'); pg.wait_for_timeout(100)
    label = pg.evaluate(f"shortDate('{past}')")
    ok('Nothing logged on this day' in pg.inner_text('.sheet') and f'Log a purchase on {label}' in pg.inner_text('.sheet'),
       f'an empty past day offers “Log a purchase on {label}”')
    pg.click('.sheet [data-a=newPurchase]'); pg.wait_for_timeout(120)
    ok(pg.evaluate("U.sheet==='edit'&&U.stack.length===1&&U.stack[0].sheet==='calendar'") and pg.input_value('#edit-date') == past,
       'it opens the Log sheet over the calendar, with that date')
    pg.fill('#edit-item', 'Turon'); pg.fill('#edit-price', '20'); pg.click('.sheet .cta'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") == 'calendar' and 'Turon' in pg.inner_text('.sheet') and pg.evaluate(f"D.purchases.some(p=>p.item==='Turon'&&p.date==='{past}')"),
       'saving goes back to the calendar, where the day now lists it')
    fut = (today + dt.timedelta(days=3)).isoformat()
    pg.evaluate(f"U.calM='{fut[:8]}01';U.calD='{fut}';rerender()"); pg.wait_for_timeout(80)
    ok(pg.locator('.sheet [data-a=newPurchase]').count() == 0, 'a day in the future has no Log row')
    pg.evaluate("U.calD=null;rerender()"); pg.wait_for_timeout(60)
    ok(pg.locator('.sheet [data-a=newPurchase]').count() == 0, 'nor does the calendar with no day picked')
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(100)

    # ── 4 · A purchase leads to its prices (whole words only) ────
    pg.evaluate("openSheet('purchase',{id:'a2'})"); pg.wait_for_timeout(100)
    row = pg.locator('.sheet [data-a=openItem]')
    ok(row.count() == 1 and 'Jeepney prices' in row.inner_text() and 'Usually ₱14' in row.inner_text() and 'first 4 km' in row.inner_text(),
       'a Jeepney purchase shows “Jeepney prices · Usually ₱14–… · first 4 km”')
    row.click(); pg.wait_for_timeout(120)
    ok(pg.evaluate("U.sheet==='item'&&U.sd.id==='jeepney'&&U.stack.length===1"), 'it opens the item over the purchase')
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.sheet==='purchase'&&U.sd.id==='a2'"), 'closing the item goes back to the purchase')
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(80)
    for k, name, want in [('a1', 'Chickenjoy bucket', 'Jollibee fried chicken prices'), ('w3', 'Fish balls', 'Fish ball'), ('w5', 'Jeepney to Cubao', 'Jeepney prices')]:
        pg.evaluate(f"openSheet('purchase',{{id:'{k}'}})"); pg.wait_for_timeout(60)
        got = pg.inner_text('.sheet [data-a=openItem]') if pg.locator('.sheet [data-a=openItem]').count() else ''
        ok(want in got, f'“{name}” shows {want} ({got.splitlines()[0] if got else "no row"})')
    for k, name in [('w1', 'Spaghetti'), ('w2', 'Mangoes'), ('w4', 'Banana'), ('a3', 'Groceries'), ('a4', 'Island hopping tour')]:
        pg.evaluate(f"openSheet('purchase',{{id:'{k}'}})"); pg.wait_for_timeout(60)
        ok(pg.locator('.sheet [data-a=openItem]').count() == 0, f'“{name}” shows no prices row (no whole-word match)')
    loose = pg.evaluate("['Spaghetti','Mangoes','Banana'].map(s=>[itemFor(s),strictItemFor(s)])")
    ok(all(a and b is None for a, b in loose), f'the loose matches the rule guards against are real ({loose})')
    ok(pg.evaluate("strictItemFor('Jeepneys')==='jeepney'&&strictItemFor('halo halo')==='halo'&&strictItemFor('Tricycle to Alona Beach')==='tricycle'"),
       'plurals and other spellings of the whole name still match')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(60)

    # ── 5 · Words that name a place ──────────────────────────────
    tab(pg, 'search')
    pg.fill('#q', 'xqzv'); pg.wait_for_timeout(80)
    log = pg.locator('#results [data-a=newPurchase]')
    ok('No clear match' in pg.inner_text('#results') and log.count() == 1 and log.inner_text().startswith('Log “xqzv” as a purchase'),
       'Search with no match offers “Log “xqzv” as a purchase”')
    log.click(); pg.wait_for_timeout(250)
    ok(pg.evaluate("U.sheet") == 'edit' and pg.input_value('#edit-item') == 'xqzv' and pg.evaluate("document.activeElement.id") == 'edit-price',
       'it opens the Log sheet with the name filled in and the cursor in the amount')
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(80)
    pg.fill('#q', 'jeepney'); pg.wait_for_timeout(80)
    ok(pg.locator('#results [data-a=newPurchase]').count() == 0, 'a search with matches has no Log row')
    # notes: the footer and the empty sheet link to Search
    pg.evaluate("go('settings')"); pg.wait_for_timeout(80)
    pg.click('#app [data-a=openNotes]'); pg.wait_for_timeout(100)
    pg.click('.sheet .foot [data-a=goSearch]'); pg.wait_for_timeout(120)
    ok(pg.evaluate("U.sheet===null&&U.tab==='search'"), 'Price notes’ footer links to Search, closing the sheet')
    pg.evaluate("D.observations=[];openSheet('notes')"); pg.wait_for_timeout(80)
    link = pg.locator('.sheet .empty [data-a=goSearch]')
    ok(link.count() == 1 and link.inner_text() == 'Open Search', 'empty Price notes says “Open Search” as a link')
    link.click(); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.sheet===null&&U.tab==='search'"), 'and it goes to Search')

    # ── 6 · Settings rows open what they name ────────────────────
    pg.evaluate("go('settings')"); pg.wait_for_timeout(80)
    pg.click('#app .row:has-text("Last backed up")'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") == 'backup', 'Last backed up opens Export a backup')
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(80)
    ok('The steps, for a new phone' in pg.inner_text('#app'), 'About’s Home Screen row says “The steps, for a new phone”')
    pg.click('#app .row:has-text("Add to your Home Screen")'); pg.wait_for_timeout(120)
    ok(pg.evaluate("U.sheet") == 'ahs' and pg.locator('.sheet [data-a=close]').count() == 1, 'and opens the same steps sheet as Help, which can be closed')
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(80)
    pg.click('#app .row:has-text("Saved exchange rate")'); pg.wait_for_timeout(120)
    ok(pg.evaluate("U.tab") == 'convert', 'Saved exchange rate opens Convert')
    pg.evaluate("go('settings')"); pg.wait_for_timeout(80)
    ok(pg.locator('#app button.row:has-text("Storage used"), #app button.row:has-text("Works offline")').count() == 0, 'Storage used and Works offline stay plain rows')
    pg.context.close()

    # stale rate: "Refresh it on Convert" goes there and refreshes
    pg = t.page(b, data=data())
    # Suki refreshes the rate on opening, so make the saved one three days old afterwards
    pg.evaluate("D.rate.cachedAt=new Date(Date.now()-3*864e5).toISOString()")
    tab(pg, 'search'); pg.fill('#q', 'jeepney'); pg.wait_for_timeout(80)
    btn = pg.locator('#staleRate [data-a=goRefresh]')
    ok(btn.count() == 1 and btn.inner_text() == 'Refresh it on Convert', 'the old-rate note’s “Refresh it on Convert” is a link')
    btn.click()
    pg.wait_for_function("Date.now()-new Date(D.rate.cachedAt)<60000", timeout=8000)
    ok(pg.evaluate("U.tab") == 'convert', 'it opens Convert and refreshes the rate')
    pg.context.close()

    # iPad: the prices row in the details pane opens the item
    pg = t.page(b, w=1180, h=820, ua=None, data=data())
    pg.evaluate("go('spending')"); pg.wait_for_timeout(100)
    pg.click('#app .sl [data-a=openPurchase][data-k=a2]'); pg.wait_for_timeout(100)
    pg.click('#app .pane [data-a=openItem]'); pg.wait_for_timeout(120)
    ok(pg.evaluate("U.sheet==='item'&&U.sd.id==='jeepney'"), 'on iPad, the prices row in the details pane opens the item')
    pg.context.close()


# ===== Door rules (Q24) =====
APP_ANIMS = "(()=>{const a=document.getElementById('app');return a?a.getAnimations().map(x=>JSON.stringify(x.effect.getKeyframes().map(k=>k.transform||'')+'|'+x.effect.getKeyframes().map(k=>k.opacity))):[]})()"
LIT = "[...document.querySelectorAll('#side .sbi.on')].map(e=>e.dataset.v)"


def run_q24(b, t):
    ok = t.ok
    pg = t.page(b, data=data())
    n = pg.evaluate("D.purchases.length")

    # Home's Show all doors open All, with every purchase, after leaving Spending on Day with a category and a filter
    for sel, name in [('#app .tbtn[data-a=toSpend]', 'Show all'), ('#app .row.more[data-a=toSpend]', f'Show all {n} purchases')]:
        pg.evaluate("go('spending');U.range='day';U.roff=1;U.cat='Transport';U.filter='zzz';U.bar=2;go('home')"); pg.wait_for_timeout(80)
        ok(pg.locator(sel).count() == 1, f'Home’s “{name}” is a door to All')
        pg.click(sel); pg.wait_for_timeout(120)
        ok(pg.evaluate("U.tab==='spending'&&U.range==='all'&&U.roff===0&&U.cat==='all'&&U.filter===''&&U.bar===null"),
           f'“{name}” opens Spending on All, with no category, filter or picked bar left over')
        ok(pg.locator('#spendList [data-a=openPurchase]').count() == n, f'and lists every purchase ({n})')
    ok(pg.locator('#app [data-a=tab][data-v=spending]').count() == 0, 'no Show all door goes to the last period any more')

    # the gear pushes Settings, Back pops it to Home; Help and Rate history the same
    pg.evaluate("go('home')"); pg.wait_for_timeout(60)
    pg.click('#barR [aria-label=Settings]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.tab") == 'settings' and pg.locator('#barL [aria-label="Back to Home"]').count() == 1, 'the gear opens Settings, with Back to Home')
    pg.click('#app [data-a=openHelp]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.tab") == 'help', 'Settings › Help opens Help')
    pg.click('#barL [aria-label="Back to Settings"]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.tab") == 'settings', 'Back from Help lands on Settings')
    pg.click('#barL [aria-label="Back to Home"]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.tab") == 'home' and pg.locator('#dock .on[data-v=home]').count() == 1, 'Back from Settings lands on Home, the tab it came from')
    pg.evaluate("go('convert')"); pg.wait_for_timeout(60)
    pg.click('[data-a=openHistory]'); pg.wait_for_timeout(100)
    pg.click('#barL [aria-label="Back to Convert"]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.tab") == 'convert', 'Back from Rate history lands on Convert')
    ok(pg.locator('#under, #over').count() == 0, 'with motion off, no still copy is left behind')

    # the delete message says what goes, with no promise about backups
    pg.evaluate("go('spending')"); pg.wait_for_timeout(60)
    pg.evaluate("ACT.delPurchase({dataset:{k:'a1'}})"); pg.wait_for_timeout(80)
    txt = pg.inner_text('#layer .pk-alert')
    ok('Chickenjoy bucket, ₱459.00.' in txt and 'backup' not in txt.lower(), 'Delete says “Chickenjoy bucket, ₱459.00.” and nothing about backups')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(60)
    pg.evaluate("ACT.delObs({dataset:{k:'o1'}})"); pg.wait_for_timeout(80)
    ok('Bigas, ₱52' in pg.inner_text('#layer .pk-alert') and 'backup' not in pg.inner_text('#layer .pk-alert').lower(), 'a price note’s says “Bigas, ₱52 on …”')
    pg.context.close()

    # Mac: Settings is a sidebar section; Help lights only Settings and zooms
    pg = t.page(b, w=1440, h=900, ua=None, data=data(), init="localStorage.setItem('suki:motion','1')")
    pg.evaluate("go('spending')"); pg.wait_for_timeout(500)
    pg.click('#side .sbi[data-v=settings]'); pg.wait_for_timeout(30)
    ok(pg.evaluate("U.tab") == 'settings' and pg.evaluate(LIT) == ['settings'], 'Mac: the sidebar’s Settings opens Settings and only Settings is lit')
    ok(pg.inner_html('#barL').strip() == '', 'Mac: Settings shows no Back button')
    ok(pg.evaluate(APP_ANIMS) == [] and pg.locator('#under, #over').count() == 0, 'Mac: it switches like a tab, with nothing moving')
    pg.click('#app [data-a=openHelp]'); pg.wait_for_timeout(30)
    a = pg.evaluate(APP_ANIMS)
    ok(pg.evaluate(LIT) == ['settings'], 'Mac: Help lights only Settings')
    ok(any('scale(0.94)' in x for x in a), f'Mac: Help zooms in ({a})')
    ok(pg.locator('#barL [aria-label="Back to Settings"]').count() == 1, 'Mac: Help keeps its Back to Settings')
    pg.wait_for_timeout(900)
    pg.click('#barL [aria-label="Back to Settings"]'); pg.wait_for_timeout(30)
    a = pg.evaluate(APP_ANIMS)
    ok(any('scale(1.04)' in x for x in a), f'Mac: and zooms out going back ({a})')
    pg.wait_for_timeout(900)
    pg.click('#side .sbi[data-v=home]'); pg.wait_for_timeout(30)
    ok(pg.evaluate("U.tab") == 'home' and pg.evaluate(LIT) == ['home'] and pg.evaluate(APP_ANIMS) == [], 'Mac: Home from the sidebar switches back like a tab')
    pg.context.close()

    # iPad: the gear and Help zoom, like Rate history
    pg = t.page(b, w=820, h=1180, data=data(), init="localStorage.setItem('suki:motion','1')")
    pg.wait_for_timeout(400)
    pg.click('#barR [aria-label=Settings]'); pg.wait_for_timeout(30)
    a = pg.evaluate(APP_ANIMS)
    ok(pg.evaluate("U.tab") == 'settings' and any('scale(0.94)' in x for x in a), f'iPad: the gear zooms Settings in ({a})')
    pg.wait_for_timeout(900)
    pg.click('#app [data-a=openHelp]'); pg.wait_for_timeout(30)
    ok(any('scale(0.94)' in x for x in pg.evaluate(APP_ANIMS)), 'iPad: Help zooms in')
    pg.wait_for_timeout(900)
    pg.click('#barL [aria-label="Back to Settings"]'); pg.wait_for_timeout(30)
    ok(any('scale(1.04)' in x for x in pg.evaluate(APP_ANIMS)), 'iPad: Help zooms out going back')
    pg.wait_for_timeout(900)
    pg.click('#barL [aria-label="Back to Home"]'); pg.wait_for_timeout(30)
    ok(pg.evaluate("U.tab") == 'home' and any('scale(1.04)' in x for x in pg.evaluate(APP_ANIMS)), 'iPad: Back zooms Settings out to Home')
    ok(pg.locator('#under, #over').count() == 0, 'iPad: no still copy (zooms only)')
    pg.context.close()
