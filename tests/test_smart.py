"""Smart add (Q14): the reader on the made-up phrases in fixtures/smart_phrases.json; Home's two sides and the
remembered side; each ask (How much?, What was it?), the either/or and learning a word; Your usual, suggestions and the
typical note; saving one and several (with Undo), the Saved button and new rows settling; Edit in the form; checking a
batch purchase in the Log sheet; "You typed" in a purchase's details; the town from earlier that day; the form's amount
box taking P50, "50 pesos" and 2k; "You paid" using whole words; Words Suki has learned (Settings, forgetting one, a
backup round trip, and an older backup keeping them); with motion on, the fade's hinge and blur, rapid switching
leaving no stray copy, Reduce Motion's crossfade and frames at 4×; screenshots at 375 and 402 px, light and dark."""
import os, json, tempfile, datetime as dt
from harness import sample, READ, ROOT, BAD_TEXT

PHRASES = json.load(open(os.path.join(ROOT, 'tests', 'fixtures', 'smart_phrases.json'), encoding='utf-8'))
ON = "localStorage.setItem('suki:motion','1')"
SLOW = "localStorage.setItem('suki:motion','4')"
SMART = "localStorage.setItem('suki:logSide','smart')"
today = dt.date.today()
iso = lambda n=0: (today - dt.timedelta(days=n)).isoformat()


def typed(pg, text):
    pg.fill('#smartText', text)
    pg.wait_for_timeout(30)


def run(b, t):
    ok = t.ok

    # ── the reader, on the made-up phrases (read on Sunday 1 Nov 2026 at noon, £1 = ₱76.12) ──
    pg = t.page(b)
    got = pg.evaluate("(C)=>C.map(c=>READER.read(c.text,new Date(2026,10,1,12,0),{},76.12))", PHRASES)
    base, misses, fields = dt.date(2026, 11, 1), [], 0
    for c, g in zip(PHRASES, got):
        if len(g) != len(c['expect']):
            misses.append(f"{c['text']!r}: {len(g)} purchases, not {len(c['expect'])}")
            continue
        for want, p in zip(c['expect'], g):
            for k, v in want.items():
                fields += 1
                if k == 'd': k, v = 'date', (base - dt.timedelta(days=v)).isoformat()
                gv = p.get(k)
                if k == 'match': gv = gv and gv['id']
                good = all(f in gv for f in v) if k == 'flags' else (not gv) if v is None and k == 'payment' else gv == v
                if not good: misses.append(f"{c['text']!r}: {k} {gv!r}, not {v!r}")
    ok(not misses, f'the reader gets all {len(PHRASES)} phrases right ({fields} fields)' + ('' if not misses else ': ' + '; '.join(misses[:6])))
    ok(len(PHRASES) >= 120, f'there are about 120 phrases ({len(PHRASES)})')
    ok(pg.evaluate("READER.read('x '.repeat(3000)+' 50').length") == 1 and pg.evaluate("READER.read('jeep 14\\n'.repeat(300)).length") == 300, 'a long line and 300 lines are read')
    ms = pg.evaluate("(()=>{const s=performance.now();READER.read('jeep 14\\n'.repeat(300));return performance.now()-s})()")
    ok(ms < 1500, f'300 lines take well under a second or so ({ms:.0f} ms)')
    # learned words come first
    ok(pg.evaluate("READER.read('mystery thing 99',new Date(),{'mystery thing':'Shopping'},0)[0].category") == 'Shopping', 'a learned word picks the category first')
    ok(pg.evaluate("READER.read('hotel 45 pounds',new Date(),{},0)[0].price") is None, 'pounds with no saved rate leave the amount to ask for')

    # ── Home's two sides ──────────────────────────────────────────
    ok(pg.locator('#app form[data-form=home]').count() == 1 and pg.inner_text('#sidePill').strip() == 'Smart add', 'Home starts on the form, with a Smart add pill on the heading')
    pg.click('#sidePill'); pg.wait_for_timeout(50)
    ok(pg.locator('#smartText').count() == 1 and pg.locator('#app form[data-form=home]').count() == 0, 'the pill switches to Smart add')
    ok(pg.inner_text('#sidePill').strip() == 'Full form' and pg.get_attribute('#sidePill', 'aria-label') == 'Switch to the full form', 'and then offers the full form')
    ok(pg.evaluate("document.activeElement.id") == 'smartText', 'the box has the cursor')
    ok(pg.evaluate("localStorage.getItem('suki:logSide')") == 'smart', 'the side is remembered on this device')
    pg.reload(); pg.wait_for_function("!document.getElementById('splash')&&!!document.getElementById('smartText')")
    ok(True, 'and is there after reopening')
    ok('Words Suki has learned' in pg.inner_text('#smartOut') and 'picks out the amount' in pg.inner_text('#smartOut'), 'empty, it says what it does and offers the learned words')

    # typing never redraws the page: the same box keeps the cursor
    pg.evaluate("window.__box=document.getElementById('smartText')")
    pg.click('#smartText'); pg.keyboard.type('jeep to cubao 14')
    ok(pg.evaluate("window.__box===document.getElementById('smartText')&&document.activeElement===window.__box"), 'typing updates the preview in place, keeping the cursor')
    out = pg.inner_text('#smartOut')
    ok('suki read' in out.lower() and 'Jeepney' in out and '₱14' in out and 'Transport' in out and 'Cubao' in out, 'the preview shows the item, amount, category and place')
    ok('Within the typical ₱14–17' in out and 'Jeepney prices' in out, 'a whole-word price-list match gets the typical note')
    ok(pg.evaluate("localStorage.getItem('suki:smart')") == 'jeep to cubao 14', 'the half-typed line is kept on this device')
    typed(pg, 'jeep to cubao 40')
    ok('More than the typical ₱14–17' in pg.inner_text('#smartOut'), 'more than the range says so plainly')
    ok(pg.locator('#smartOut .warn').count() == 0, 'and isn’t in a warning colour')
    typed(pg, 'jeep to cubao 5')
    ok('Less than the typical ₱14–17' in pg.inner_text('#smartOut'), 'and so does less')
    typed(pg, 'jeep to cubao and back 14')
    ok('typical' not in pg.inner_text('#smartOut').split('Save')[0] and 'Jeepney prices' in pg.inner_text('#smartOut'), 'no note when the name isn’t the whole item, just the prices door')
    pg.click('#smartOut [data-a=openItem]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.sheet") == 'item' and pg.evaluate("U.sd.id") == 'jeepney', 'the prices door opens the item')
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(80)

    # ── each ask ──────────────────────────────────────────────────
    typed(pg, 'mystery snack')
    ok(pg.locator('#smartPrice').count() == 1 and 'How much?' in pg.inner_text('#smartOut'), 'no amount: it asks How much?')
    ok('dim' in pg.get_attribute('#smartSave', 'class'), 'and Save looks unready')
    pg.click('#smartSave')
    ok(pg.inner_text('#smartErr') == 'Add how much it was.', 'tapping it says what’s missing')
    pg.fill('#smartPrice', '45')
    ok('dim' not in pg.get_attribute('#smartSave', 'class') and pg.inner_text('#smartErr') == '', 'an amount makes it ready, in place')
    typed(pg, '150')
    ok(pg.locator('#smartItem').count() == 1 and 'What was it?' in pg.inner_text('#smartOut'), 'no name: it asks What was it?')
    typed(pg, 'mystery thing 99')
    ok(pg.locator('#smartOut .row.kv.guess').count() == 1 and 'no clue for the category' in pg.inner_text('#smartOut'), 'no clue: the category is tinted, with a line saying so')
    typed(pg, 'taho 20 on the 30th of december')
    ok('In the future' in pg.inner_text('#smartOut') and pg.locator('#smartOut .row.kv.warn').count() >= 1, 'a date in the future is flagged')
    typed(pg, 'hotel 45 pounds')
    out = pg.inner_text('#smartOut')
    ok('£45 at £1 = ₱' in out and pg.locator('#smartOut .row.kv.warn').count() == 1, 'pounds are changed at the saved rate, with a note')

    # either/or, and learning
    typed(pg, '7-eleven 85')
    ok('Food & drink or Groceries?' in pg.inner_text('#smartOut'), 'a tie asks which: Food & drink or Groceries?')
    pg.click('#smartOut [data-a=smartPick][data-k=Groceries]'); pg.wait_for_timeout(50)
    ok(pg.evaluate("document.querySelector('#smartOut [data-smart-cat]').value") == 'Groceries', 'picking one sets the category')
    ok(pg.evaluate("D.learned.map(w=>[w.word,w.category])") == [['7 eleven', 'Groceries']], 'and Suki learns the word')
    ok('Suki will remember “7-Eleven” as Groceries' in pg.inner_text('.toast'), 'and says so')
    pg.wait_for_timeout(100)
    ok(pg.evaluate(READ, 'learned')[0]['category'] == 'Groceries', 'the learned word is saved')
    typed(pg, 'mystery thing 99')
    pg.select_option('#smartOut [data-smart-cat]', 'Shopping'); pg.wait_for_timeout(50)
    typed(pg, 'mystery thing 120')
    ok(pg.evaluate("document.querySelector('#smartOut [data-smart-cat]').value") == 'Shopping' and 'from a word Suki has learned' in pg.inner_text('#smartOut'), 'changing a category teaches the word for next time')

    # ── saving one ────────────────────────────────────────────────
    typed(pg, '')
    pg.evaluate("localStorage.removeItem('suki:smart')")
    n0 = pg.evaluate("D.purchases.length")
    typed(pg, 'tricycle fifty pesos from bulakan to barrio')
    pg.click('#smartSave'); pg.wait_for_timeout(100)
    p = pg.evaluate("D.purchases[0]")
    ok(pg.evaluate("D.purchases.length") == n0 + 1 and p['item'] == 'Tricycle' and p['price'] == 50 and p['location'] == 'Bulakan to Barrio' and p['category'] == 'Transport', 'Save purchase saves what the preview showed')
    ok(p['said'] == 'tricycle fifty pesos from bulakan to barrio' and p['rateAtPurchase'] and p['date'] == iso(), 'with his words, the rate and today’s date')
    ok(pg.input_value('#smartText') == '' and pg.evaluate("localStorage.getItem('suki:smart')") is None, 'the box empties')
    ok(pg.locator('#homeSave.saved').count() == 1 and 'Saved' in pg.inner_text('#homeSave'), 'the button says Saved where he tapped')
    ok('Purchase saved' in pg.inner_text('.toast') and pg.locator('.toast button').inner_text() == 'Undo', '“Purchase saved” offers Undo')
    pg.wait_for_function("!document.querySelector('#homeSave.saved')", timeout=4000)
    ok('picks out the amount' in pg.inner_text('#smartOut'), 'then the empty line’s hint comes back')
    pg.wait_for_timeout(150)
    ok(pg.evaluate(READ, 'purchases')[0]['said'] == p['said'], 'his words are saved with it')

    # You typed, in its details
    pg.click(f"#app [data-a=openPurchase][data-k='{p['id']}']"); pg.wait_for_timeout(80)
    ok('You typed: “tricycle fifty pesos from bulakan to barrio”' in pg.inner_text('.sheet'), 'its details show You typed: …')
    pg.click('.sheet [data-a=editPurchase]'); pg.wait_for_timeout(80)
    pg.fill('#edit-price', '45'); pg.click('.sheet .cta'); pg.wait_for_timeout(100)
    ok(pg.evaluate(f"D.purchases.find(x=>x.id==='{p['id']}').said") == p['said'], 'editing it keeps his words')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(80)

    # Your usual and suggestions (the tricycle just saved, and the sample's jeepney)
    typed(pg, 'jeep')
    sug = pg.inner_text('#smartSugg')
    ok('from your purchases' in sug.lower() and 'Jeepney' in sug and pg.locator('#smartSugg .row').count() == 1, 'typing words shows his own purchases to finish from')
    ok(pg.input_value('#smartPrice') == '13' and 'Your usual' in pg.inner_text('#smartOut'), 'with no amount, Your usual fills it, editable')
    typed(pg, 'jeep 14')
    ok(pg.inner_text('#smartSugg') == '', 'suggestions go once a number is typed')
    typed(pg, 'tric')
    pg.click('#smartSugg .row'); pg.wait_for_timeout(50)
    ok(pg.input_value('#smartText') == 'tricycle fifty pesos from bulakan to barrio', 'tapping one fills the line with what he said then')
    pg.evaluate("D.purchases.unshift({id:'u1',item:'Tricycle',price:30,date:'" + iso(1) + "',category:'Transport',location:'Bulakan to Barrio'},{id:'u2',item:'Tricycle',price:20,date:'" + iso(2) + "',category:'Transport',location:'San Jose City'},{id:'u3',item:'Tricycle',price:60,date:'" + iso(3) + "',category:'Transport',location:'Bulakan to Barrio'})")
    typed(pg, 'tricycle from bulakan to barrio')
    ok(pg.input_value('#smartPrice') == '45' and 'from your last 3' in pg.inner_text('#smartOut'), 'Your usual is the middle of the last three, at the same place first (₱30, ₱45, ₱60 → ₱45)')
    typed(pg, 'tricycle to somewhere new')
    ok(pg.input_value('#smartPrice') == '30', f"[{pg.input_value('#smartPrice')}] " + 'with none at that place, the last three anywhere (₱20, ₱30, ₱45 → ₱30)')
    pg.evaluate("D.purchases=D.purchases.filter(x=>!/^u\\d$/.test(x.id))")

    # the town from earlier today, when the line names no place
    pg.evaluate("D.purchases.unshift({id:'t1',item:'Halo-halo',price:95,date:'" + iso() + "',category:'Food & drink',location:'San Jose City'})")
    typed(pg, 'taho 20')
    out = pg.inner_text('#smartOut')
    ok('San Jose City' in out and 'from earlier today' in out, 'with no place said, today’s town fills Location')
    typed(pg, 'taho 20 kahapon')
    ok('San Jose City' not in pg.inner_text('#smartOut'), 'a day with no town leaves it empty')
    pg.evaluate("D.purchases=D.purchases.filter(x=>x.id!=='t1')")

    # ── several at once ───────────────────────────────────────────
    typed(pg, 'taho 20\ngrab to airport 380\nsim load 99 also water 25\nlunch kahapon')
    out = pg.inner_text('#smartOut')
    ok('5 purchases found' in out.lower() and pg.locator('#smartOut [data-a=smartCheck]').count() == 5 and 'Save 5 purchases' in out, 'several lines show a list, and Save 5 purchases')
    ok('How much?' in pg.inner_text('#smartOut [data-a=smartCheck][data-v="4"]') and 'Edit in the form' not in out, 'a row says what it’s missing; no Edit in the form for a list')
    pg.click('#smartSave')
    ok('Check the purchases marked' in pg.inner_text('#smartErr'), 'saving with one missing says which to check')
    # checking one in the usual Log sheet
    pg.click('#smartOut [data-a=smartCheck][data-v="4"]'); pg.wait_for_timeout(80)
    ok(pg.evaluate("U.sheet") == 'edit' and 'Check purchase' in pg.inner_text('.sheet h2') and pg.inner_text('.sheet .cta') == 'Done', 'a row opens the usual Log sheet, to check it')
    ok(pg.input_value('#edit-item') == 'Lunch' and pg.input_value('#edit-date') == iso(1) and 'You typed: “lunch kahapon”' in pg.inner_text('.sheet'), 'filled in from the line, with his words')
    pg.fill('#edit-price', '180'); pg.select_option('#edit-category', 'Other'); pg.click('.sheet .cta'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.sheet") is None and 'Lunch' in pg.inner_text('#smartOut') and '₱180' in pg.inner_text('#smartOut'), 'Done puts it back in the list, unsaved')
    ok(any(w['word'] == 'lunch' and w['category'] == 'Other' for w in pg.evaluate("D.learned")), 'changing its category there teaches the word too')
    n0 = pg.evaluate("D.purchases.length")
    pg.click('#smartSave'); pg.wait_for_timeout(120)
    ok(pg.evaluate("D.purchases.length") == n0 + 5 and '5 purchases saved' in pg.inner_text('.toast'), 'Save 5 purchases saves all five')
    saved = pg.evaluate("D.purchases.slice(0,5).map(p=>[p.item,p.price,p.said])")
    ok(['Lunch', 180, 'lunch kahapon'] in saved and ['Water', 25, 'water 25'] in saved and ['Taho', 20, 'taho 20'] in saved, 'each with its own words: ' + str(saved[:2]))
    pg.click('.toast button'); pg.wait_for_timeout(120)
    ok(pg.evaluate("D.purchases.length") == n0 and '5 purchases removed' in pg.inner_text('.toast'), 'Undo removes all five')
    pg.wait_for_timeout(120)
    ok(len(pg.evaluate(READ, 'purchases')) == n0, 'and that’s saved')

    # ── Edit in the form ──────────────────────────────────────────
    typed(pg, 'carinderia ulam 70 yesterday with revolut')
    pg.click('#smartOut [data-a=smartToForm]'); pg.wait_for_timeout(60)
    ok(pg.locator('#app form[data-form=home]').count() == 1 and pg.inner_text('#sidePill').strip() == 'Smart add', 'Edit in the form switches to the form')
    ok(pg.input_value('#home-item') == 'Ulam' and pg.input_value('#home-price') == '70' and pg.input_value('#home-date') == iso(1) and pg.input_value('#home-venue') == 'Carinderia' and pg.input_value('#home-payment') == 'Revolut', 'filled in, with More details open')
    pg.click('#homeSave'); pg.wait_for_timeout(100)
    ok(pg.evaluate("D.purchases[0].item") == 'Ulam' and pg.evaluate("D.purchases[0].said") == 'carinderia ulam 70 yesterday with revolut', 'saved from the form, it keeps his words')
    pg.click('#sidePill'); pg.wait_for_timeout(50)
    ok(pg.input_value('#smartText') == '', 'and Smart add is empty again')

    # ── the form's amount box ─────────────────────────────────────
    pg.click('#sidePill'); pg.wait_for_timeout(50)
    for typed_amt, want in (('P50', 50), ('50 pesos', 50), ('2k', 2000), ('₱1.5k', 1500), ('PHP 1,250', 1250)):
        pg.fill('#home-item', 'Test'); pg.fill('#home-price', typed_amt); pg.click('#homeSave'); pg.wait_for_timeout(60)
        ok(pg.evaluate("D.purchases[0].item==='Test'&&D.purchases[0].price") == want, f'the form’s amount box reads {typed_amt} as ₱{want}')
        pg.evaluate("D.purchases.shift();rerender()")
    pg.fill('#home-item', 'Test'); pg.fill('#home-price', '12.50.5'); pg.click('#homeSave'); pg.wait_for_timeout(60)
    ok('Check the amount' in pg.inner_text('#home-err'), 'and still refuses 12.50.5')
    t.shot(pg, 'form-402-light')

    # ── Words Suki has learned ────────────────────────────────────
    pg.click('#barR [data-v=settings]'); pg.wait_for_timeout(60)
    row = pg.locator('#app [data-a=openLearned]')
    ok(row.count() == 1 and '3 words' in row.inner_text(), 'Settings › Your data lists Words Suki has learned')
    row.click(); pg.wait_for_timeout(80)
    txt = pg.inner_text('.sheet')
    ok('7-Eleven' in txt and 'Groceries' in txt and 'Mystery thing' in txt and 'Lunch' in txt and 'kept in backups' in txt, 'the sheet lists each word and its category')
    pg.click('.sheet [data-a=forgetWord][data-k="mystery thing"]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("D.learned.length") == 2 and 'Mystery thing' not in pg.inner_text('.sheet') and 'forgot' in pg.inner_text('.toast'), 'a word can be forgotten')
    pg.wait_for_timeout(100)
    ok(len(pg.evaluate(READ, 'learned')) == 2, 'and that’s saved')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(80)

    # a backup round trip
    pg.click('[data-a=exportBackup]'); pg.wait_for_timeout(450)
    with pg.expect_download() as dl:
        pg.click('.sheet .cta')
    data = json.load(open(dl.value.path(), encoding='utf-8'))
    ok(len(data['learned']) == 2 and any(p.get('said') == 'carinderia ulam 70 yesterday with revolut' for p in data['purchases']), 'a backup holds the learned words and his words')
    pg.click('[data-a=erase]'); pg.wait_for_timeout(80)
    ok('2 learned words' in pg.inner_text('.sheet'), 'Erase says the learned words go too')
    pg.click('.sheet [data-a=eraseYes]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("D.learned.length") == 0 and pg.evaluate(READ, 'learned') == [], 'and empties them')
    tmp = tempfile.mkdtemp()
    f = os.path.join(tmp, 'b.json'); json.dump(data, open(f, 'w'))
    pg.set_input_files('#importIn', f); pg.wait_for_timeout(300)
    ok('the backup has 1 purchase, 0 price notes and 2 learned words' in pg.inner_text('#layer .pk-alert') or '2 learned words' in pg.inner_text('#layer .pk-alert'), 'the restore alert says the backup’s learned words')
    pg.click('#layer .pk-alert [data-a=yes]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("D.learned.length") == 2 and pg.evaluate("D.purchases.some(p=>p.said==='carinderia ulam 70 yesterday with revolut')"), 'restoring brings the words and his words back')
    pg.wait_for_timeout(100)
    ok(len(pg.evaluate(READ, 'learned')) == 2, 'saved again')
    old = sample(); f2 = os.path.join(tmp, 'old.json'); json.dump(dict(old, app='Suki'), open(f2, 'w'))
    pg.set_input_files('#importIn', f2); pg.wait_for_timeout(300)
    pg.click('#layer .pk-alert [data-a=yes]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("D.learned.length") == 2 and pg.evaluate("D.purchases.length") == 4, 'an older backup with no learned words keeps the ones on the phone')
    pg.reload(); pg.wait_for_function("!document.getElementById('splash')&&typeof U!=='undefined'")
    pg.wait_for_timeout(100)
    ok(pg.evaluate("D.learned.length") == 2, 'and they’re still there after reopening')
    ok(not pg.evaluate(BAD_TEXT), 'no undefined, NaN or null on screen')

    # "You paid" uses whole words: a mango purchase is never Mang Inasal's
    pg.evaluate("D.purchases.unshift({id:'m1',item:'Mangoes',price:120,date:'" + iso() + "',category:'Groceries',location:''},{id:'m2',item:'Inasal',price:139,date:'" + iso() + "',category:'Food & drink',location:''});rerender()")
    pg.evaluate("ACT.openItem({dataset:{k:'pm1'}})"); pg.wait_for_timeout(80)
    paid = pg.inner_text('.sheet')
    ok('Mangoes' not in paid and '₱139' in paid, 'You paid on Mang Inasal lists Inasal, never Mangoes')
    pg.keyboard.press('Escape')
    pg.context.close()

    # ── motion: the fade ──────────────────────────────────────────
    pg = t.page(b, init=SLOW)
    pg.click('#sidePill'); pg.wait_for_timeout(500)
    f = pg.evaluate("""(()=>{const g=document.querySelector('#logwrap .lghost');const rows=[...document.querySelectorAll('#smartCard > *, #smartOut > *')];
      const blur=rows.map(r=>getComputedStyle(r).filter).filter(x=>/blur/.test(x)).length;
      const card=getComputedStyle(document.querySelector('#smartCard')).filter;
      const hinge=document.getElementById('smartText').getAnimations().length;return {g:!!g,blur,card,hinge}})()""")
    ok(f['g'] and f['blur'] >= 1 and f['card'] in ('none', '') and f['hinge'] >= 1, f'mid-way at 4×: the old side is a copy fading out, rows are blurred, the card isn’t, the box slides ({f})')
    t.shot(pg, 'fade-midway-4x')
    pg.wait_for_function("!document.querySelector('#logwrap .lghost')", timeout=8000)
    ok(pg.locator('#logwrap .lghost').count() == 0 and pg.locator('#logwrap .face').count() == 1, 'afterwards only the new side is left')
    for _ in range(7):
        pg.click('#sidePill'); pg.wait_for_timeout(60)
    ok(pg.locator('#logwrap .lghost').count() <= 1 and pg.locator('#logwrap .face:not(.lghost)').count() == 1, 'switching quickly keeps at most one fading copy')
    pg.wait_for_function("!document.querySelector('#logwrap .lghost')", timeout=8000)
    ok(pg.locator('#logwrap > *').count() == 1 and pg.evaluate("[...document.querySelectorAll('[id]')].map(e=>e.id).length===new Set([...document.querySelectorAll('[id]')].map(e=>e.id)).size"), 'rapid switching leaves no stray copy and no repeated ids')
    # wait for the fades themselves to end, not just the copy: a timer can take the copy away before the page draws
    # its next frame, so the new side's own fade could still read part way (Q32: the old flaky fold check)
    pg.wait_for_function("document.getElementById('logwrap').getAnimations({subtree:true}).every(a=>a.playState!=='running')", timeout=8000)
    ok(pg.evaluate("getComputedStyle(document.querySelector('#logwrap .face')).opacity") == '1', 'and the side showing is fully there')
    # a redraw mid-way (a rate arriving) also leaves nothing behind
    pg.click('#sidePill'); pg.wait_for_timeout(100); pg.evaluate("rerender()")
    ok(pg.locator('#logwrap .lghost').count() == 0, 'a redraw mid-way leaves no copy')
    # frames at 4×, light and dark
    for i, ms in enumerate((150, 400, 900)):
        pg.click('#sidePill'); pg.wait_for_timeout(ms)
        pg.locator('#logwrap').screenshot(path=os.path.join(ROOT, 'tests', 'output', f'smart-fade-frame{i}-4x.png'))
        pg.wait_for_function("!document.querySelector('#logwrap .lghost')", timeout=8000)
    pg.context.close()

    pg = t.page(b, init=ON, ctx_args={'reduced_motion': 'reduce'})
    # switch and look in the same step: the crossfade is 100 ms, so on a busy machine a separate look could come after
    # the copy has gone (Q32: the old flaky Reduce Motion check)
    r = pg.evaluate("""(()=>{document.getElementById('sidePill').click();const w=document.getElementById('logwrap'),g=w.querySelector('.lghost');
      return {a:[...w.querySelectorAll('*')].flatMap(e=>e.getAnimations()).map(a=>a.effect.getKeyframes().map(k=>(k.filter||'')+(k.transform||'')).join('')),g:g?g.getAnimations().length:0}})()""")
    a, g = r['a'], r['g']
    ok(all(x == '' for x in a) and g >= 1, 'Reduce Motion: a plain crossfade, nothing blurs or moves')
    pg.context.close()

    # with motion on, saved rows settle into Recent
    pg = t.page(b, init=ON + ';' + SMART)
    typed(pg, 'taho 20\njeep 14')
    pg.click('#smartSave'); pg.wait_for_timeout(30)
    ok(pg.evaluate("[...document.querySelectorAll('#app .row[data-a=openPurchase]')].slice(0,2).some(r=>r.getAnimations().length)"), 'new rows settle into Recent')
    pg.context.close()

    # ── screenshots, 375 and 402 px, light and dark ───────────────
    for w, h in ((375, 667), (402, 874)):
        for sc in ('light', 'dark'):
            pg = t.page(b, w=w, h=h, sc=sc, init=SMART)
            typed(pg, '7-eleven 85 revolut')
            pg.locator('#smartOut').scroll_into_view_if_needed()
            ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), f'no sideways scroll at {w} px, {sc}')
            t.shot(pg, f'one-{w}-{sc}', full_page=True)
            typed(pg, 'taho 20\ngrab to airport 380\nsim load 99 also water 25\nlunch kahapon')
            t.shot(pg, f'many-{w}-{sc}', full_page=True)
            typed(pg, '')
            t.shot(pg, f'empty-{w}-{sc}')
            pg.context.close()
