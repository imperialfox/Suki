"""Everyday use: logging, editing and deleting purchases, category chips and the filter, Quick Till, Convert,
Search and price notes, and the CSV export."""
import json
from harness import READ, BAD_TEXT, today, RATE, day

TOUCH = """(a)=>{const [sel,type,x,y]=a;const el=document.querySelector(sel);const t=new Touch({identifier:1,target:el,clientX:x,clientY:y});
  el.dispatchEvent(new TouchEvent(type,{touches:type==='touchend'?[]:[t],changedTouches:[t],bubbles:true,cancelable:true}))}"""


def tab(pg, name):
    """Tap a tab in the tab bar (from the top of the page)."""
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
    # amounts: two dots are refused, spaces read as thousands, and nothing that rounds to ₱0.00 (Q06)
    pg.fill('#home-price', '12.50.5'); pg.click('form[data-form=home] .cta'); pg.wait_for_timeout(100)
    ok('Check the amount' in pg.inner_text('#home-err'), 'an amount with two dots asks you to check it')
    pg.fill('#home-price', '0.001'); pg.click('form[data-form=home] .cta'); pg.wait_for_timeout(100)
    ok('above ₱0' in pg.inner_text('#home-err'), 'an amount that rounds to ₱0.00 is refused')
    ok(pg.evaluate("amount('1 000')") == 1000 and pg.evaluate("amount('₱1,250.50')") == 1250.5 and pg.evaluate("amount('12.50.5')") is None, 'pasted “1 000” reads as ₱1,000')
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
    # the red button's label is readable: white text, not red on red (Q01)
    col = pg.evaluate("(()=>{const s=getComputedStyle(document.querySelector('.sheet .cta.red'));return [s.color,s.backgroundColor]})()")
    ok(col[0] != col[1] and col[0] == 'rgb(255, 255, 255)', f'the Delete button’s label is white on red (got {col})')
    pg.click('.sheet .ghost'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") == 'purchase', 'Cancel goes back to the purchase')
    pg.click('.sheet [data-a=delPurchase]'); pg.click('.sheet [data-a=delPurchaseYes]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sheet") is None and not any(p['id'] == 'a1' for p in pg.evaluate(READ, 'purchases')), 'confirming deletes it and closes the sheets')
    # Undo puts it back where it was (Q03)
    ok(pg.locator('.toast button').inner_text() == 'Undo', 'deleting shows Undo')
    pg.click('.toast button'); pg.wait_for_timeout(200)
    ok(any(p['id'] == 'a1' for p in pg.evaluate(READ, 'purchases')) and pg.locator('#spendList [data-a=openPurchase][data-k=a1]').count() == 1, 'Undo brings the purchase back')

    # ── Spending over time (Q03) ─────────────────────────────────
    ok(pg.evaluate("U.range") == 'all' and 'Since' in pg.inner_text('#spendSum') and pg.locator('#chart .col').count() == 10,
       'Spending starts on All, with a bar for each day since the first purchase')
    amts = [float(a.split('₱')[1].split('\n')[0].replace(',', '')) for a in pg.locator('#spendBrk .row .amt').all_inner_texts()]
    ok(len(amts) >= 4 and amts == sorted(amts, reverse=True), f'the breakdown lists each category, biggest first ({amts})')
    pg.click('#rangeSeg [data-v=week]'); pg.wait_for_timeout(100)
    ok(pg.locator('#chart .col').count() == 7 and 'This week' in pg.inner_text('#spendSum'), 'W shows this week, a bar a day')
    ok(pg.evaluate("getComputedStyle(document.getElementById('rangeSeg')).getPropertyValue('--i').trim()") == '1', 'the knob moves to W')
    wk = pg.locator('#spendList [data-a=openPurchase]').count()
    pg.click('#rangeSeg [data-v=day]'); pg.wait_for_timeout(100)
    ok(pg.locator('#chart').count() == 0 and 'Today' in pg.inner_text('#spendSum') and pg.locator('#spendList [data-a=openPurchase]').count() <= wk, 'D shows today, and the list follows')
    pg.click('#spendSum [data-a=rangeStep][data-v="1"]'); pg.wait_for_timeout(100)
    ok('Yesterday' in pg.inner_text('#spendSum') and '₱1,247.50' in pg.inner_text('#spendSum'), 'the back arrow steps to yesterday')
    ok(pg.locator('#spendSum [data-a=rangeStep][data-v="-1"]').is_enabled(), 'and the forward arrow comes alive')
    pg.click('#rangeSeg [data-v=all]'); pg.wait_for_timeout(100)
    # tap a bar to read that day
    last = pg.locator('#chart .col').last.bounding_box()
    pg.mouse.click(last['x'] + last['width'] / 2, last['y'] + last['height'] - 4); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.bar") == 9 and 'Today' in pg.inner_text('#spendSum .plabel'), 'tapping a bar shows that day in the headline')
    pg.mouse.click(20, 20); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.bar") is None, 'tapping elsewhere goes back to the whole period')
    pg.click('#spendBrk .row:has-text("Groceries")'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.cat") == 'Groceries' and pg.locator('#spendList [data-a=openPurchase]').count() == 1, 'a breakdown row filters the list to that category')
    pg.click('#spendBrk [data-a=cat][data-v=all] >> nth=0'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.cat") == 'all', 'and Show all clears it')
    # Home's date and title open the calendar
    tab(pg, 'home'); pg.click('h1 .hometitle'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") == 'calendar' and pg.locator('.cday.today').count() == 1 and pg.locator('.cday.has').count() >= 2, 'the calendar shows today and the days you spent on')
    y1 = pg.evaluate("localISO(new Date(Date.now()-864e5))")
    if y1[:7] == pg.evaluate("U.calM").replace('-01', '')[:7]:
        pg.click(f'.cday[data-v="{y1}"]'); pg.wait_for_timeout(100)
        ok(pg.locator('.sheet [data-a=openPurchase]').count() == 2, 'tapping a day lists what you bought')
        pg.click('.sheet [data-a=openPurchase] >> nth=0'); pg.wait_for_timeout(150)
        ok(pg.evaluate("U.sheet") == 'purchase', 'a purchase opens from the calendar')
        pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(150)
        ok(pg.evaluate("U.sheet") == 'calendar', 'and closing it goes back to the calendar')
    pg.click('.sheet [data-a=calStep][data-v="-1"]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.calM") < pg.evaluate("localISO().slice(0,8)+'01'"), 'the arrows step through months')
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(100)
    tab(pg, 'spending')
    # a long list draws 60 at a time, while the totals count everything (Q03, from the stress test)
    pg.evaluate("""(()=>{const keep=D.purchases;window.__keep=keep;const many=[];for(let i=0;i<130;i++)many.push({id:'m'+i,item:'Snack '+i,price:10,date:localISO(),category:'Food & drink',location:'',venue:'',payment:'Cash',notes:''});
      D.purchases=many.concat(keep);U.range='all';rerender()})()"""); pg.wait_for_timeout(100)
    n0 = pg.locator('#spendList [data-a=openPurchase]').count()
    ok(n0 == 60 and 'Show 60 more' in pg.inner_text('#spendList'), f'a long list draws the newest 60, then Show more ({n0})')
    tot = float(pg.locator('#spendList .hdr .hint').first.inner_text().replace('₱', '').replace(',', ''))
    ok(tot >= 1300, f'and the day’s total still counts every purchase ({tot})')
    pg.click('[data-a=moreRows]'); pg.wait_for_timeout(100)
    ok(pg.locator('#spendList [data-a=openPurchase]').count() == 120, 'Show more draws the next 60')
    pg.evaluate("D.purchases=window.__keep;U.shown=60;rerender()"); pg.wait_for_timeout(100)
    # a new day redraws in place: here the day is made to look stale
    pg.evaluate("document.querySelector('#app h1').dataset.old='1';drawnDay='2000-01-01'")
    ok(pg.evaluate("dayCheck()") and not pg.evaluate("!!document.querySelector('#app h1[data-old]')"), 'when the date moves on, the screen redraws itself')
    pg.evaluate("drawnDay='2000-01-01';document.getElementById('filter').focus()")
    ok(not pg.evaluate("dayCheck()"), 'but not while you’re typing')
    pg.evaluate("document.activeElement.blur()")

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
    ok('"Halo-halo"' in csv and '"1250.50"' in csv and csv.count('\n') == 4, 'the CSV has every purchase shown')
    t.shot(pg, 'spending')

    # ── Quick Till ────────────────────────────────────────────────
    tab(pg, 'till')
    ok(pg.locator('#tillLog').is_disabled(), 'Log this bill waits for a bill')
    pg.fill('#till-bill', '789.50'); pg.click('[data-a=cashAdd][data-v="500"]'); pg.click('[data-a=cashAdd][data-v="500"]')
    ok(pg.input_value('#till-cash') == '1000' and 'Change due' in pg.inner_text('#tillOut') and '₱210.50' in pg.inner_text('#tillOut'), 'the amount buttons add up and the change shows')
    pg.fill('#till-cash', '500'); pg.wait_for_timeout(50)
    ok('Still to pay' in pg.inner_text('#tillOut') and '₱289.50' in pg.inner_text('#tillOut'), 'short cash shows what’s still to pay')
    pg.fill('#till-bill', '0.001'); pg.wait_for_timeout(50)
    ok(pg.locator('#tillLog').is_disabled(), 'Quick Till won’t log a ₱0.00 bill (Q06)')
    pg.fill('#till-bill', '789.50'); pg.wait_for_timeout(50)
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
    pg.click('[data-a=quickConv][data-v="50"]'); pg.wait_for_timeout(100)
    ok(pg.input_value('#conv-php') == '3,706.00', 'a handy amount fills the converter')
    # the swap button puts pesos on top, and the handy amounts follow (Q01)
    pg.click('[data-a=swapConv]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("[...document.querySelectorAll('#convCard .cbox')].map(b=>b.dataset.c).join()") == 'php,gbp', 'Swap puts pesos on top')
    ok(pg.evaluate("document.activeElement.id") == 'conv-php', 'and the cursor goes to the top box')
    ok(pg.locator('[data-a=quickConv][data-c=php]').count() == 6 and '₱1,000' in pg.inner_text('.grp.quick'), 'handy amounts switch to pesos')
    pg.click('[data-a=quickConv][data-v="1000"]'); pg.wait_for_timeout(100)
    ok(pg.input_value('#conv-gbp') == '13.49', 'a peso handy amount fills in pounds')
    pg.click('[data-a=swapConv]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.conv.top") == 'gbp', 'Swap again puts pounds back on top')
    pg.evaluate("D.rate.cachedAt=new Date(Date.now()-864e5*2).toISOString()")
    pg.click('#refreshRate'); pg.wait_for_timeout(400)
    ok(pg.inner_text('#rateLine') == 'Updated today', 'Refresh loads a new rate, and the line says when in plain words')

    # ── Search and price notes ───────────────────────────────────
    tab(pg, 'search')
    heads = [h.upper() for h in pg.locator('#results .hdr h2').all_inner_texts()]
    ok(heads == ['TRANSPORT', 'FOOD', 'MARKET', 'DRINKS', 'SERVICES', 'ESSENTIALS'] and '₱48.42' in pg.inner_text('#results'), 'Search starts with a few items from each category, official prices included')
    # browsing by category (Q02)
    pg.click('#results [data-a=scat][data-v=transport]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.scat") == 'transport' and pg.locator('#browse .chip.on').inner_text() == 'Transport' and pg.locator('#results .row').count() >= 10, 'Show all opens the whole category, with its chip on')
    ok('₱14–17' in pg.inner_text('#results [data-k=jeepney]'), 'the jeepney shows the new fares')
    pg.click('#results [data-a=openItem][data-k=jeepney]'); pg.wait_for_timeout(150)
    txt = pg.inner_text('.sheet')
    ok('Traditional jeepney' in txt and '₱14' in txt and 'Set fare' in txt and pg.locator('.sheet a.link.src').count() >= 1, 'an item shows its typical prices and where they came from')
    pg.click('.sheet [data-a=logItem]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") == 'edit' and pg.input_value('#edit-item') == 'Jeepney' and pg.input_value('#edit-category') == 'Transport', 'Log what you paid starts the form with the item and its category')
    pg.fill('#edit-price', '14'); pg.click('.sheet .cta'); pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sheet") == 'item' and pg.locator('.sheet [data-a=openPurchase]').count() == 1 and 'YOU PAID' in pg.inner_text('.sheet').upper(),
       'saving goes back to the item, which now lists what you paid')
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(100)
    pg.click('#browse [data-v=all]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.scat") == 'all', 'the All chip goes back to everything')
    for q, want in [('sinigan baboy', 'Sinigang na baboy'), ('1 kilo bigas', 'Bigas'), ('chiken adobo', 'Adobong manok'), ('water', 'Tubig na bottled')]:
        pg.fill('#q', q); pg.wait_for_timeout(60)
        first = pg.locator('#results .row b').first.inner_text()
        ok(first == want, f'searching “{q}” finds {want} first (got {first})')
    # a clear match isn't followed by unrelated items (Q01)
    for q, never in [('water', 'Kwek-kwek'), ('adobo', 'Banana cue'), ('rice', 'Halo-halo'), ('coffe', 'Soft drinks')]:
        pg.fill('#q', q); pg.wait_for_timeout(60)
        ok(never not in pg.inner_text('#results'), f'searching “{q}” doesn’t show {never}')
    pg.fill('#q', 'xqzv'); pg.wait_for_timeout(60)
    ok('No clear match' in pg.inner_text('#results'), 'no match says so')
    pg.click('[data-a=clearQ]'); pg.wait_for_timeout(60)
    ok(pg.input_value('#q') == '' and pg.evaluate("document.activeElement.id") == 'q', 'Clear empties the box and keeps it ready to type')
    for q, want in [('jeepney', 'Dyip'), ('beer', 'Serbesa'), ('jollibee', 'Chickenjoy'), ('sim', 'SIM card'), ('laundry', 'Laba')]:
        pg.fill('#q', q); pg.wait_for_timeout(60)
        first = pg.locator('#results .row b').first.inner_text()
        ok(first == want, f'searching “{q}” finds {want} (got {first})')
    pg.click('#browse [data-v=market]'); pg.fill('#q', 'beer'); pg.wait_for_timeout(60)
    ok('No clear match' in pg.inner_text('#results'), 'a category chip narrows the search too')
    pg.click('#browse [data-v=all]'); pg.wait_for_timeout(60)
    pg.fill('#q', 'bigas'); pg.click('[data-a=openItem][data-k=bigas]'); pg.wait_for_timeout(150)
    txt = pg.inner_text('.sheet')
    ok('Official price' in txt and '₱48.42' in txt and '₱52.00' in txt, 'an item shows its official price and your notes')
    ok(pg.inner_text('.sheet .shead h2') == 'Market', 'its sheet is titled with its category')
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
    ok('£1 = ₱74.12' in pg.inner_text('#app') and 'PHP' not in pg.inner_text('#app'), 'Settings shows the rate in pesos with ₱, like everywhere else')
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
