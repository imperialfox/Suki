"""Everyday use: logging, editing and deleting purchases, category chips and the filter, Quick Till, Convert,
Search and price notes, and the CSV export."""
import json
from harness import READ, BAD_TEXT, today, RATE, day

TOUCH = """(a)=>{const [sel,type,x,y]=a;const el=document.querySelector(sel);const t=new Touch({identifier:1,target:el,clientX:x,clientY:y});
  el.dispatchEvent(new TouchEvent(type,{touches:type==='touchend'?[]:[t],changedTouches:[t],bubbles:true,cancelable:true}))}"""


def tab(pg, name):
    """Tap a tab in the tab bar (scrolling up first, as the bar shrinks to the current tab while you scroll down)."""
    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(80)
    pg.click(f'#dock [data-v={name}]'); pg.wait_for_timeout(120)


def run(b, t):
    ok = t.ok
    pg = t.page(b, touch=True)

    # ── Home: log a purchase ─────────────────────────────────────
    ok(pg.inner_text('.sumcard .big') == '₱3,206.50', 'Home shows the total spent')
    ok('Today' in pg.inner_text('.sumcard') and '₱459.00' in pg.inner_text('.sumcard .stat.r'), 'Home shows today’s spending')
    pg.click('form[data-form=home] .cta'); pg.wait_for_timeout(100)
    ok('Add what you bought' in pg.inner_text('#home-err'), 'saving with nothing typed explains what’s missing')
    pg.fill('#home-item', 'Halo-halo'); pg.click('form[data-form=home] .cta'); pg.wait_for_timeout(100)
    ok('amount' in pg.inner_text('#home-err'), 'saving without an amount asks for one')
    pg.fill('#home-price', '1,250.5')
    pg.click('[data-a=more]'); pg.wait_for_timeout(100)
    ok(pg.locator('#home-location').count() == 1, 'More details opens the extra fields')
    pg.fill('#home-location', 'Baguio'); pg.select_option('#home-venue', 'Street vendor'); pg.select_option('#home-payment', 'Revolut')
    pg.fill('#home-notes', 'Big one')
    # a half-typed purchase survives closing the app
    pg.reload(); pg.wait_for_function("!document.getElementById('splash')")
    ok(pg.input_value('#home-item') == 'Halo-halo' and pg.input_value('#home-location') == 'Baguio', 'a half-typed purchase is still there after reopening')
    pg.click('form[data-form=home] .cta'); pg.wait_for_timeout(200)
    saved = pg.evaluate(READ, 'purchases')
    h = saved[0]
    ok(h['item'] == 'Halo-halo' and h['price'] == 1250.5 and h['location'] == 'Baguio' and h['venue'] == 'Street vendor' and h['payment'] == 'Revolut',
       'the purchase is saved with every detail')
    ok(h['rateAtPurchase'] == RATE and abs(h['gbpAtPurchase'] - 16.87) < 0.01, 'it remembers the pound value at the time')
    ok(pg.input_value('#home-item') == '' and pg.evaluate("localStorage.getItem('suki:draft')") is None, 'the form clears and the draft is gone')
    ok('Halo-halo' in pg.inner_text('.grp.tiled'), 'it shows under Recent')
    t.shot(pg, 'home')

    # ── Spending: chips, filter, details, edit, delete ───────────
    tab(pg, 'spending')
    chips = pg.locator('.chip[data-a=cat]').all_inner_texts()
    ok(chips[0].startswith('All') and any(c.startswith('Groceries') for c in chips) and not any(c.startswith('Shopping') for c in chips),
       'category chips show only categories in use, with counts')
    pg.click('.chip[data-v="Transport"]'); pg.wait_for_timeout(100)
    ok(pg.locator('#spendList .row').count() == 1 and 'Transport' in pg.inner_text('#spendSum') and '₱13.00' in pg.inner_text('#spendSum'),
       'a category chip filters the list and the total')
    pg.click('.chip[data-v=all]'); pg.fill('#filter', 'cubao'); pg.wait_for_timeout(100)
    ok(pg.locator('#spendList .row').count() == 1 and pg.evaluate("document.activeElement.id") == 'filter', 'the filter matches places and keeps typing in the box')
    pg.fill('#filter', 'zzzz'); pg.wait_for_timeout(100)
    ok('No purchases match' in pg.inner_text('#spendList'), 'a filter with no matches says so')
    pg.click('[data-a=clearFilter]'); pg.wait_for_timeout(100)
    heads = pg.locator('#spendList .hdr h2').all_inner_texts()
    ok(heads[:2] == ['TODAY', 'YESTERDAY'] or heads[:2] == ['Today', 'Yesterday'], 'purchases are grouped by day: ' + ', '.join(heads))
    ok(pg.locator('#spendList .hdr .hint').first.inner_text() == '₱1,709.50', 'each day shows its total')

    pg.click('[data-a=openPurchase][data-k=a1]'); pg.wait_for_timeout(150)
    txt = pg.inner_text('.sheet')
    ok('Chickenjoy bucket' in txt and 'SM Megamall' in txt and 'Shared with family' in txt and '≈ £6.19' in txt, 'a purchase opens with all its details')
    pg.click('.sheet [data-a=editPurchase]'); pg.wait_for_timeout(150)
    ok(pg.input_value('#edit-item') == 'Chickenjoy bucket' and pg.input_value('#edit-price') == '459', 'Edit opens with the purchase filled in')
    pg.fill('#edit-price', '0'); pg.click('.sheet .cta'); pg.wait_for_timeout(100)
    ok(pg.locator('.sheet #edit-err').inner_text() != '', 'an edit can’t save a zero amount')
    pg.fill('#edit-price', '499'); pg.fill('#edit-item', 'Chickenjoy bucket (6 pc)'); pg.select_option('#edit-category', 'Shopping')
    pg.click('.sheet .cta'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sheet") == 'purchase' and '₱499.00' in pg.inner_text('.sheet'), 'saving an edit goes back to the purchase')
    a1 = next(p for p in pg.evaluate(READ, 'purchases') if p['id'] == 'a1')
    ok(a1['price'] == 499 and a1['category'] == 'Shopping' and a1['item'] == 'Chickenjoy bucket (6 pc)' and abs(a1['gbpAtPurchase'] - 499 / RATE) < 0.01,
       'the edit is saved, with its pound value worked out again')
    pg.click('.sheet [data-a=delPurchase]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") == 'confirm' and 'Delete this purchase?' in pg.inner_text('.sheet'), 'Delete asks first')
    pg.click('.sheet .ghost'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") == 'purchase', 'Cancel goes back to the purchase')
    pg.click('.sheet [data-a=delPurchase]'); pg.click('.sheet [data-a=delPurchaseYes]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sheet") is None and not any(p['id'] == 'a1' for p in pg.evaluate(READ, 'purchases')), 'confirming deletes it and closes the sheets')

    # swipe to delete
    sel = '#spendList .sw:has([data-k=a2]) .fg'
    box = pg.locator(sel).bounding_box(); y = box['y'] + box['height'] / 2
    pg.evaluate(TOUCH, [sel, 'touchstart', 300, y])
    for x in (280, 240, 200, 180): pg.evaluate(TOUCH, [sel, 'touchmove', x, y])
    pg.evaluate(TOUCH, [sel, 'touchend', 180, y]); pg.wait_for_timeout(300)
    ok(pg.locator('.sw.open').count() == 1, 'swiping a row left shows Delete')
    pg.wait_for_timeout(400)
    pg.click('.sw.open .swdel'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") == 'confirm', 'Delete on a swiped row asks first')
    pg.click('.sheet [data-a=delPurchaseYes]'); pg.wait_for_timeout(200)
    ok(not any(p['id'] == 'a2' for p in pg.evaluate(READ, 'purchases')), 'and deletes the row')

    # CSV
    with pg.expect_download() as dl:
        pg.click('[data-a=csv]')
    path = dl.value.path(); csv = open(path, encoding='utf-8-sig').read()
    ok(dl.value.suggested_filename.startswith('Suki purchases') and csv.splitlines()[0].startswith('"Date","Item","Amount (PHP)"'), 'Export as CSV saves a spreadsheet file')
    ok('"Halo-halo"' in csv and '"1250.50"' in csv and csv.count('\n') == 3, 'the CSV has every purchase shown')
    t.shot(pg, 'spending')

    # ── Quick Till ────────────────────────────────────────────────
    tab(pg, 'till')
    ok(pg.locator('#tillLog').is_disabled(), 'Log this bill waits for a bill')
    pg.fill('#till-bill', '789.50'); pg.click('[data-a=cashAdd][data-v="500"]'); pg.click('[data-a=cashAdd][data-v="500"]')
    ok(pg.input_value('#till-cash') == '1000' and 'Change due' in pg.inner_text('#tillOut') and '₱210.50' in pg.inner_text('#tillOut'), 'the amount buttons add up and the change shows')
    pg.fill('#till-cash', '500'); pg.wait_for_timeout(50)
    ok('Still to pay' in pg.inner_text('#tillOut') and '₱289.50' in pg.inner_text('#tillOut'), 'short cash shows what’s still to pay')
    pg.click('[data-a=cashExact]')
    ok('Exact payment' in pg.inner_text('#tillOut'), 'Exact fills in the bill amount')
    pg.click('[data-a=cashClear]'); ok(pg.input_value('#till-cash') == '', 'Clear empties the cash')
    pg.click('#tillLog'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") == 'edit' and pg.input_value('#edit-price') == '789.5', 'Log this bill opens the form with the amount')
    pg.fill('#edit-item', 'Dinner at Max’s'); pg.click('.sheet .cta'); pg.wait_for_timeout(200)
    ok(pg.evaluate(READ, 'purchases')[0]['item'] == 'Dinner at Max’s' and pg.input_value('#till-bill') == '', 'it’s saved and the till clears')

    # ── Convert ───────────────────────────────────────────────────
    tab(pg, 'convert')
    ok(pg.input_value('#conv-gbp') == '100' and pg.input_value('#conv-php') == '7,412.00', 'the converter starts at £100')
    pg.fill('#conv-php', '1000'); pg.wait_for_timeout(50)
    ok(pg.input_value('#conv-gbp') == '13.49', 'typing pesos fills in pounds')
    pg.fill('#conv-gbp', '20'); pg.wait_for_timeout(50)
    ok(pg.input_value('#conv-php') == '1,482.40', 'typing pounds fills in pesos')
    pg.click('[data-a=copyConv]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("navigator.clipboard.readText()").startswith('£20.00 ≈ ₱1,482.40'), 'Copy conversion copies it')
    pg.click('[data-a=quickGbp][data-v="50"]'); pg.wait_for_timeout(100)
    ok(pg.input_value('#conv-php') == '3,706.00', 'a handy amount fills the converter')
    pg.evaluate("D.rate.cachedAt=new Date(Date.now()-864e5*2).toISOString()")
    pg.click('#refreshRate'); pg.wait_for_timeout(400)
    ok('updated today' in pg.inner_text('#rateLine'), 'Refresh loads a new rate')

    # ── Search and price notes ───────────────────────────────────
    tab(pg, 'search')
    ok('OFFICIAL PRICES' in pg.inner_text('#results').upper() and '₱48.42' in pg.inner_text('#results'), 'Search starts with the official prices')
    for q, want in [('sinigan baboy', 'Sinigang na baboy'), ('1 kilo bigas', 'Bigas'), ('chiken adobo', 'Adobong manok'), ('water', 'Tubig na bottled')]:
        pg.fill('#q', q); pg.wait_for_timeout(60)
        first = pg.locator('#results .row b').first.inner_text()
        ok(first == want, f'searching “{q}” finds {want} first (got {first})')
    pg.fill('#q', 'xqzv'); pg.wait_for_timeout(60)
    ok('No clear match' in pg.inner_text('#results'), 'no match says so')
    pg.click('[data-a=clearQ]'); pg.wait_for_timeout(60)
    ok(pg.is_visible('#examples') and pg.evaluate("document.activeElement.id") == 'q', 'Clear empties the box, keeps it ready to type and brings back the examples')
    pg.click('[data-a=example][data-v="tubig bote"]'); pg.wait_for_timeout(60)
    ok(pg.input_value('#q') == 'tubig bote' and pg.locator('#results .row').count() >= 1, 'an example search fills the box')
    pg.fill('#q', 'bigas'); pg.click('[data-a=openItem][data-k=bigas]'); pg.wait_for_timeout(150)
    txt = pg.inner_text('.sheet')
    ok('Official price' in txt and '₱48.42' in txt and '₱52.00' in txt, 'an item shows its official price and your notes')
    pg.click('.sheet [data-a=obsForm]'); pg.wait_for_timeout(100)
    pg.click('.sheet form button[type=submit]'); pg.wait_for_timeout(100)
    ok(pg.inner_text('#obs-err') != '', 'a price note needs a price')
    pg.fill('#obs-price', '55'); pg.fill('#obs-location', 'Divisoria'); pg.click('.sheet form button[type=submit]'); pg.wait_for_timeout(200)
    obs = pg.evaluate(READ, 'observations')
    ok(any(o['price'] == 55 and o['location'] == 'Divisoria' and o['itemId'] == 'bigas' for o in obs) and '₱55.00' in pg.inner_text('.sheet'), 'the price note is saved and shown')
    pg.click('.sheet [data-a=delObs] >> nth=0'); pg.wait_for_timeout(100)
    pg.click('.sheet [data-a=delObsYes]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sheet") == 'item' and len(pg.evaluate(READ, 'observations')) == 2, 'deleting a note asks first, then returns to the item')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.sheet") is None, 'Escape closes the sheet')

    # an old rate: a quiet note under the pound values, and none while it's fresh
    tab(pg, 'search'); pg.fill('#q', ''); pg.wait_for_timeout(60)
    ok(pg.locator('#staleRate').count() == 0, 'with a fresh rate, Search has no note about its age')
    pg.evaluate("D.rate.cachedAt=new Date(Date.now()-3*864e5).toISOString();rerender()"); pg.wait_for_timeout(60)
    ok('rate from 3 days ago' in pg.inner_text('#results'), 'with a rate three days old, Search says the pound values use it')
    pg.fill('#q', 'bigas'); pg.wait_for_timeout(60)
    ok(pg.locator('#staleRate').count() == 1, 'and it stays under the matches while searching')
    pg.evaluate("D.rate.cachedAt=new Date().toISOString();U.q='';rerender()"); pg.wait_for_timeout(60)

    # ── Settings ──────────────────────────────────────────────────
    tab(pg, 'home'); pg.click('#barR [data-v=settings]'); pg.wait_for_timeout(100)
    ok('Suki ' in pg.inner_text('.ver') and pg.locator('#barL [data-v=home]').count() == 1, 'Settings has the version and a way back')
    pg.click('[data-a=openNotes]'); pg.wait_for_timeout(150)
    ok(pg.locator('.sheet .row').count() == 2, 'Price notes lists every note')
    pg.click('.sheet [data-a=openItem] >> nth=0'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") == 'item', 'a note opens its item')
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") == 'notes', 'closing the item goes back to the notes')
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(100)
    bad = pg.evaluate(BAD_TEXT); ok(not bad, 'no undefined, NaN or null anywhere' + (': ' + bad if bad else ''))
    t.shot(pg, 'settings')
    pg.context.close()

    # an empty app: friendly empty states
    pg = t.page(b, data=None)
    ok('No purchases yet' in pg.inner_text('#app'), 'Home has an empty state')
    tab(pg, 'spending'); ok('appear here' in pg.inner_text('#app') and pg.locator('[data-a=csv]').count() == 0, 'Spending has an empty state and no export')
    gap = pg.evaluate("document.querySelector('#spendList .grp').getBoundingClientRect().top-document.getElementById('spendSum').getBoundingClientRect().bottom")
    ok(gap >= 10, f'the empty state keeps a gap under the total ({gap:.0f}px)')
    tab(pg, 'convert')
    ok(pg.evaluate("!!D.rate"), 'with no saved rate, one loads on opening')
    pg.context.close()

    # with motion on, every tab swaps instantly, Settings included
    pg = t.page(b, init="localStorage.setItem('suki:motion','1')")
    for to in ['settings', 'home', 'search', 'settings', 'convert']:
        pg.evaluate(f"go('{to}')")
        n = pg.evaluate("document.getElementById('app').getAnimations().length")
        ok(n == 0, f'going to {to.title()} is instant ({n} animations)')
    pg.context.close()
