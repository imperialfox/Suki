"""Saved data: older and damaged data, backups (export, restore, damaged files), erasing everything,
the backup reminder and the rate failing to load."""
import json, os, tempfile, datetime as dt
from harness import READ, SEED, sample, ready, day, RATE, BAD_TEXT


def run(b, t):
    ok = t.ok

    # ── older and damaged records are tidied, not fatal ──────────
    messy = sample()
    messy['purchases'] += [
        {'id': 7, 'item': 'Taho', 'price': '25', 'date': day(4), 'category': 'Snacks'},  # number id, text price, unknown category
        {'id': 'x1', 'item': '', 'price': 50, 'date': day(1)},  # no name: dropped
        {'id': 'x2', 'item': 'Free sample', 'price': 0, 'date': day(1)},  # no amount: dropped
        {'id': 'a3', 'item': 'Duplicate id', 'price': 10, 'date': 'not a date', 'category': 'Other', 'future': 'kept'},
        'junk', None, [1, 2],
    ]
    messy['observations'] += [{'id': 'o9', 'itemId': 'itlog', 'price': 'abc'}, {'itemId': 'itlog', 'price': 9, 'date': day(1)}]
    messy['rate'] = {'value': -3}
    pg = t.page(b, data=messy, rate_fail=True)
    D = pg.evaluate("D")
    ok(len(D['purchases']) == 6, f'damaged purchases are left out, the rest kept ({len(D["purchases"])} of 6)')
    taho = next((p for p in D['purchases'] if p['item'] == 'Taho'), None)
    ok(taho and taho['id'] == '7' and taho['price'] == 25 and taho['category'] == 'Other', 'old records are tidied: text ids, text amounts, unknown categories')
    dup = next((p for p in D['purchases'] if p['item'] == 'Duplicate id'), None)
    ok(dup and dup['id'] != 'a3' and dup['date'] == dt.date.today().isoformat() and dup['future'] == 'kept',
       'a repeated id gets a new one, a bad date becomes today, and unknown fields are kept')
    ok(len(D['observations']) == 3 and D['rate'] is None, 'bad price notes and a bad rate are left out')
    ok(not pg.evaluate(BAD_TEXT), 'nothing odd shows on screen')
    pg.context.close()

    # storage holding the wrong kind of thing entirely
    pg = t.page(b, data={'purchases': {'oops': 1}, 'observations': 'text', 'rate': [1]})
    ok(pg.evaluate("D.purchases.length===0&&D.observations.length===0") and 'No purchases yet' in pg.inner_text('#app'), 'damaged storage still opens, empty')
    pg.context.close()

    # ── backup reminder ──────────────────────────────────────────
    pg = t.page(b)
    ok(pg.locator('#app .nudge').count() == 1, 'Home reminds you to back up when you never have')
    pg.click('#barR [data-v=settings]'); pg.wait_for_timeout(100)
    ok('Not backed up yet' in pg.inner_text('#app'), 'Settings says it hasn’t been backed up')

    # ── export ────────────────────────────────────────────────────
    pg.click('[data-a=exportBackup]'); pg.wait_for_timeout(50)
    ok(pg.locator('.sheet .cta').is_disabled(), 'Export shows Preparing first')
    pg.wait_for_timeout(400)
    with pg.expect_download() as dl:
        pg.click('.sheet .cta')
    name = dl.value.suggested_filename
    data = json.load(open(dl.value.path(), encoding='utf-8'))
    ok(name.startswith('Suki backup · ' + dt.date.today().strftime('%Y-%m')) and name.endswith('.json'), 'the backup is named by month and device: ' + name)
    ok(data['app'] == 'Suki' and len(data['purchases']) == 4 and len(data['observations']) == 2 and data['rate']['value'] == RATE, 'it holds every purchase, note and the rate')
    pg.wait_for_timeout(200)
    ok(pg.evaluate("U.sheet") is None and 'Today at' in pg.inner_text('#app'), 'Last backed up now says today')
    pg.click('#barL [data-v=home]'); pg.wait_for_timeout(100)
    ok(pg.locator('#app .nudge').count() == 0, 'and the reminder goes')
    pg.evaluate("localStorage.setItem('suki:lastBackup',new Date(Date.now()-864e5*20).toISOString());rerender()")
    ok(pg.locator('#app .nudge').count() == 1, 'it comes back after two weeks')

    # ── erase ─────────────────────────────────────────────────────
    pg.click('#barR [data-v=settings]'); pg.click('[data-a=erase]'); pg.wait_for_timeout(100)
    ok('4 purchases' in pg.inner_text('.sheet') and pg.locator('.sheet [data-a=exportBackup]').count() == 1, 'Erase says what goes and offers a backup first')
    pg.click('.sheet [data-a=exportBackup]'); pg.wait_for_timeout(400)
    ok(pg.evaluate("U.sheet") == 'backup', 'Export a backup first opens the backup')
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.sheet") == 'erase', 'closing it goes back to Erase')
    pg.click('.sheet [data-a=eraseYes]'); pg.wait_for_timeout(200)
    ok(pg.evaluate(READ, 'purchases') == [] and pg.evaluate(READ, 'observations') == [] and pg.evaluate(READ, 'rate') is None, 'Erase empties everything')

    # ── restore ───────────────────────────────────────────────────
    tmp = tempfile.mkdtemp()
    good = os.path.join(tmp, 'good.json'); json.dump(data, open(good, 'w'))
    pg.set_input_files('#importIn', good); pg.wait_for_timeout(300)
    txt = pg.inner_text('#layer .pk-alert')
    ok(pg.evaluate("U.sheet") == 'restore' and '4 purchases' in txt and 'the backup has 4 purchases' in txt, f'restoring asks first, with what’s in the backup (an alert since Q27: {txt!r})')
    pg.click('#layer .pk-alert [data-a=yes]'); pg.wait_for_timeout(300)
    ok(len(pg.evaluate(READ, 'purchases')) == 4 and pg.evaluate("U.tab") == 'home' and '₱3,206.50' in pg.inner_text('#app'), 'replacing brings everything back')

    bad = os.path.join(tmp, 'bad.json'); open(bad, 'w').write('{not json')
    pg.set_input_files('#importIn', bad); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") is None and 'isn’t a Suki backup' in pg.inner_text('.toast'), 'a damaged file is refused with a message')
    other = os.path.join(tmp, 'other.json'); json.dump({'hello': 'world'}, open(other, 'w'))
    pg.set_input_files('#importIn', other); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") is None, 'another app’s file is refused')
    # a backup from Suki 2.0 (no README or device) restores too, leaving out damaged records
    old = {'app': 'Suki', 'schemaVersion': 1, 'exportedAt': '2026-10-17T09:00:00Z', 'purchases': data['purchases'] + [{'item': 'x'}], 'observations': [], 'rate': None}
    p2 = os.path.join(tmp, 'old.json'); json.dump(old, open(p2, 'w'))
    pg.set_input_files('#importIn', p2); pg.wait_for_timeout(300)
    ok('1 damaged record' in pg.inner_text('#layer .pk-alert') and '17 Oct 2026' in pg.inner_text('#layer .pk-alert'), 'a 2.0 backup restores, saying what it leaves out')
    pg.click('#layer .pk-alert [data-a=no]'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.sheet") is None and len(pg.evaluate(READ, 'observations')) == 2, 'Cancel changes nothing')

    # ── Q05: a restore can always be undone, and a backup with nothing usable is refused ──
    allbad = os.path.join(tmp, 'allbad.json'); json.dump({'app': 'Suki', 'purchases': [{'item': ''}, 'junk', {'price': 5}], 'observations': [], 'rate': None}, open(allbad, 'w'))
    pg.set_input_files('#importIn', allbad); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") is None and 'nothing has changed' in pg.inner_text('.toast.sticky') and len(pg.evaluate(READ, 'purchases')) == 4,
       'a backup where every record is damaged is refused, and nothing changes')
    pg.click('.toast.sticky button'); pg.wait_for_timeout(100)
    ok(pg.locator('.toast.sticky').count() == 0, 'the warning stays until OK is tapped')
    empty = os.path.join(tmp, 'empty.json'); json.dump({'app': 'Suki', 'purchases': [], 'observations': [], 'rate': None}, open(empty, 'w'))
    pg.set_input_files('#importIn', empty); pg.wait_for_timeout(300)
    ok(pg.evaluate("U.sheet") is None and 'empty' in pg.inner_text('.toast.sticky') and len(pg.evaluate(READ, 'purchases')) == 4, 'an empty backup is refused too')
    pg.click('.toast.sticky button')
    small = os.path.join(tmp, 'small.json'); json.dump({'app': 'Suki', 'purchases': [{'id': 's1', 'item': 'Only this', 'price': 5, 'date': day(0)}], 'observations': [], 'rate': None}, open(small, 'w'))
    pg.set_input_files('#importIn', small); pg.wait_for_timeout(300)
    pg.click('#layer .pk-alert [data-a=yes]'); pg.wait_for_timeout(300)
    ok(len(pg.evaluate(READ, 'purchases')) == 1 and pg.evaluate(READ, 'safety')['why'] == 'restore' and len(pg.evaluate(READ, 'safety')['data']['purchases']) == 4,
       'before a restore, what was on the phone is kept as a safety copy')
    ok(pg.locator('.toast button').inner_text() == 'Undo', 'and the restore offers Undo')
    pg.click('.toast button'); pg.wait_for_timeout(300)
    ok(len(pg.evaluate(READ, 'purchases')) == 4 and len(pg.evaluate(READ, 'safety')['data']['purchases']) == 1, 'Undo puts everything back, keeping the restored copy in its place')
    pg.evaluate("go('settings')"); pg.wait_for_timeout(100)
    ok('Before your last restore' in pg.inner_text('#app'), 'Settings offers to put back what was there before')
    pg.click('[data-a=putBack]'); pg.wait_for_timeout(150); pg.click('#layer .pk-alert [data-a=yes]'); pg.wait_for_timeout(300)
    ok(len(pg.evaluate(READ, 'purchases')) == 1, 'and it swaps back and forth')
    pg.evaluate("go('settings')"); pg.click('[data-a=putBack]'); pg.wait_for_timeout(150); pg.click('#layer .pk-alert [data-a=yes]'); pg.wait_for_timeout(300)
    pg.evaluate("go('settings')"); pg.click('[data-a=erase]'); pg.wait_for_timeout(150); pg.click('.sheet [data-a=eraseYes]'); pg.wait_for_timeout(300)
    ok(pg.evaluate(READ, 'purchases') == [] and pg.locator('.toast button').inner_text() == 'Undo', 'Erase offers Undo too')
    pg.click('.toast button'); pg.wait_for_timeout(300)
    ok(len(pg.evaluate(READ, 'purchases')) == 4, 'and Undo after Erase brings everything back')
    pg.context.close()

    # ── Q05: saved data that can't be read is kept safe, never quietly lost ──
    pg = t.page(b, data={'purchases': 'oops, a string', 'observations': [{'id': 'o1', 'itemId': 'bigas', 'price': 52, 'date': day(1)}, {'nope': 1}], 'rate': None})
    rs = pg.evaluate(READ, 'rescue')
    ok(isinstance(rs, list) and len(rs) == 1 and len(rs[0]['items']) == 2 and rs[0]['items'][0]['raw'] == 'oops, a string', 'unreadable saved data is copied somewhere safe as it loads')
    ok(pg.locator('#app .nudge.warn').count() == 1 and 'couldn’t be read' in pg.inner_text('#app'), 'and Home says so')
    pg.fill('#home-item', 'Coffee'); pg.fill('#home-price', '120'); pg.click('form[data-form=home] .cta'); pg.wait_for_timeout(300)
    ok(len(pg.evaluate(READ, 'purchases')) == 1 and pg.evaluate(READ, 'rescue')[0]['items'][0]['raw'] == 'oops, a string', 'saving afterwards keeps the copy')
    pg.click('#app .nudge.warn'); pg.wait_for_timeout(150)
    ok(pg.evaluate("U.sheet") == 'rescue' and '2 records' in pg.inner_text('.sheet'), 'the notice opens Recovered data')
    with pg.expect_download() as dl:
        pg.click('.sheet [data-a=saveRescue]')
    saved = json.load(open(dl.value.path(), encoding='utf-8'))
    ok(saved['kind'] == 'recovered' and saved['recovered'][0]['items'][0]['raw'] == 'oops, a string', 'Save a copy saves exactly what couldn’t be read')
    pg.wait_for_timeout(200)
    ok(pg.locator('#app .nudge.warn').count() == 0, 'once saved, the notice goes')
    pg.click('.sheet [data-a=close]'); pg.wait_for_timeout(100)
    pg.evaluate("go('settings')"); pg.wait_for_timeout(100); pg.click('[data-a=openRescue]'); pg.wait_for_timeout(150)
    pg.click('.sheet [data-a=clearRescue]'); pg.wait_for_timeout(150); pg.click('#layer .pk-alert [data-a=yes]'); pg.wait_for_timeout(200)
    ok(pg.evaluate(READ, 'rescue') == [] and 'Recovered data' not in pg.inner_text('#app'), 'and it can be cleared after that')
    pg.context.close()
    pg = t.page(b, data={'purchases': [{'id': 'p1', 'item': 'Chickenjoy', 'price': '₱459', 'date': day(0)}, {'id': 'p2', 'item': 'Load', 'price': 'PHP 1,250', 'date': day(0)}]})
    ok(pg.evaluate("D.purchases.map(p=>p.price).join()") == '459,1250', 'amounts written as “₱459” or “PHP 1,250” are read, not dropped')
    pg.context.close()

    # ── Q06: odd values in saved data or a backup ──
    pg = t.page(b, data={'purchases': [{'id': 'h', 'item': 'Huge', 'price': 1e12, 'date': day(0)}, {'id': 't', 'item': 'Tiny', 'price': 0.001, 'date': day(0)},
                                       {'id': 'f', 'item': 'Feb 30', 'price': 50, 'date': '2026-02-30'}, {'id': 'k', 'item': 'Kept', 'price': 9999999, 'date': day(1)}]})
    D = pg.evaluate("D")
    ok([p['item'] for p in D['purchases']] == ['Feb 30', 'Kept'], 'a price above ₱10,000,000 or below ₱0.01 is treated as damaged (and kept safe, not lost)')
    ok(D['purchases'][0]['date'] == dt.date.today().isoformat(), 'an impossible date like 30 Feb becomes today')
    ok(len(pg.evaluate(READ, 'rescue')[0]['items']) == 2, 'the damaged ones are in Recovered data')
    pg.context.close()

    # ── Q06: with no signal, the rate refresh gives up after two timeouts ──
    pg = t.page(b)
    pg.evaluate("rateFrom=()=>new Promise((_,rej)=>setTimeout(()=>rej(new Error('timed out')),30));go('convert')")
    pg.click('#refreshRate'); pg.wait_for_function("!rateBusy"); pg.wait_for_timeout(100)
    ok(pg.evaluate("RATE_CHECK.fails.length===3&&RATE_CHECK.fails[2].source==='the rest'"), 'after two sources time out, the rest aren’t tried')
    ok(pg.evaluate(f"D.rate.value==={RATE}") and 'saved rate is still in use' in pg.inner_text('.toast'), 'and the saved rate keeps working')
    pg.context.close()

    # ── Q05: when the storage database won't open ──
    BREAK = ("(()=>{const o=indexedDB.open.bind(indexedDB);indexedDB.open=function(){"
             "if(localStorage.getItem('test:break')==='1')throw new Error('broken');return o.apply(null,arguments)}})()")
    pg = t.page(b, init=BREAK)
    pg.evaluate("localStorage.setItem('test:break','1')"); pg.reload(); ready(pg)
    ok(pg.evaluate("STORE_WARN") and 'couldn’t open its main storage' in pg.inner_text('#app'), 'Home says when its storage won’t open')
    pg.fill('#home-item', 'Saved while broken'); pg.fill('#home-price', '77'); pg.click('form[data-form=home] .cta'); pg.wait_for_timeout(300)
    ok(any(p['item'] == 'Saved while broken' for p in json.loads(pg.evaluate("localStorage.getItem('suki:purchases')"))), 'purchases still save, to the smaller spot')
    pg.evaluate("localStorage.removeItem('test:break')"); pg.reload(); ready(pg)
    items = [p['item'] for p in pg.evaluate(READ, 'purchases')]
    ok('Saved while broken' in items and len(items) == 5 and not pg.evaluate("STORE_WARN"), 'once it opens again, those purchases are merged back in, none hidden')
    ok(pg.evaluate("localStorage.getItem('suki:purchases')") is None, 'and the smaller spot is cleared after they’re safely moved')
    pg.context.close()

    # ── Q05: "Couldn't save" stays up, and an Undo message doesn't hide it ──
    pg = t.page(b)
    pg.evaluate("putKey=putChecked=()=>Promise.resolve(false);go('spending')")
    pg.click('[data-a=openPurchase][data-k=a1]'); pg.wait_for_timeout(150)
    pg.click('.sheet [data-a=delPurchase]'); pg.click('#layer .pk-alert [data-a=yes]'); pg.wait_for_timeout(300)
    ok(pg.locator('.toast.sticky').count() == 1 and pg.locator('.toast.undo').count() == 1, 'a failed save shows a warning, and Undo is still there below it')
    pg.wait_for_timeout(5000)
    ok(pg.locator('.toast.sticky').count() == 1 and 'Couldn’t save' in pg.inner_text('.toast.sticky'), 'the warning is still up after the Undo message has gone')
    pg.context.close()

    # ── the rate can't load ───────────────────────────────────────
    pg = t.page(b, data={**sample(), 'rate': None}, rate_fail=True)
    pg.evaluate("go('convert')"); pg.wait_for_timeout(200)
    ok(pg.locator('#conv-gbp').is_disabled() and 'No rate yet' in pg.inner_text('#app'), 'with no rate, Convert says so')
    pg.click('#refreshRate'); pg.wait_for_function("!rateBusy"); pg.wait_for_timeout(100)
    ok('Couldn’t reach the rate service. Try again in a moment.' in pg.inner_text('.toast'), 'a failed refresh explains, without blaming the connection')
    ok(pg.evaluate("D.rate===null&&RATE_CHECK&&!RATE_CHECK.ok&&RATE_CHECK.fails.length===4"), 'it tried all four sources')
    pg.evaluate("go('settings')"); pg.wait_for_timeout(100)
    txt = pg.inner_text('#app')
    ok('Couldn’t load a rate' in txt and 'frankfurter.dev: error 503' in txt and 'currency-api.pages.dev: error 503' in txt, 'Settings says which sources failed and why')
    pg.context.close()

    # ── rate sources: falls back, keeps a good rate, rejects nonsense ──
    pg = t.page(b, data={**sample(), 'rate': None}, rate_opts={'down': ['api.frankfurter.dev', 'api.frankfurter.app']})
    pg.evaluate("go('convert')"); pg.click('#refreshRate'); pg.wait_for_function("!rateBusy"); pg.wait_for_timeout(100)
    ok(pg.evaluate(f"D.rate&&D.rate.value==={RATE}&&D.rate.source==='Currency API'"), 'with Frankfurter down, the rate comes from the Currency API')
    ok('Rate updated' in pg.inner_text('.toast'), 'and the refresh says it worked')
    pg.evaluate("go('settings')"); pg.wait_for_timeout(100)
    txt = pg.inner_text('#app')
    ok('From Currency API' in txt and 'Loaded from Currency API' in txt and 'Tried first' in txt, 'Settings names the source and what was tried first')
    pg.context.close()

    pg = t.page(b, rate_opts={'values': {'api.frankfurter.dev': 0.0128}})
    pg.evaluate("D.rate.cachedAt='2000-01-01T00:00:00Z';go('convert')"); pg.click('#refreshRate'); pg.wait_for_function("!rateBusy"); pg.wait_for_timeout(100)
    ok(pg.evaluate(f"D.rate.value==={RATE}&&D.rate.source.startsWith('Frankfurter')&&/out of range/.test(RATE_CHECK.fails[0].why)"),
       'a rate the wrong way round (0.0128) is rejected and the next source used')
    pg.context.close()

    pg = t.page(b, rate_opts={'values': {'api.frankfurter.dev': 9999, 'api.frankfurter.app': -1, 'cdn.jsdelivr.net': 0, 'currency-api.pages.dev': 'abc'}})
    before = pg.evaluate("D.rate.value")
    pg.evaluate("go('convert')"); pg.click('#refreshRate'); pg.wait_for_function("!rateBusy"); pg.wait_for_timeout(100)
    ok(pg.evaluate(f"D.rate.value==={before}") and pg.evaluate(READ, 'rate')['value'] == before, 'bad replies from every source never replace the saved rate')
    ok('the saved rate is still in use' in pg.inner_text('.toast'), 'and the refresh says the saved rate is still in use')
    pg.context.close()

    # ── Q34: a live rate far from the saved one needs a second source to agree ──
    # the audit's case: Frankfurter says ₱119 against a saved ₱74.12, which 2.35 took as "Rate updated"
    FR = {'api.frankfurter.dev': 119, 'api.frankfurter.app': 119}
    def refresh(pg, manual=True):
        if manual: pg.evaluate("go('convert')"); pg.click('#refreshRate')
        else: pg.evaluate("refreshRate(false)")
        pg.wait_for_function("!rateBusy"); pg.wait_for_timeout(100)
    LIVE = lambda u: u.endswith('/rate/GBP/PHP') or 'latest' in u  # the live rate's addresses, not history or day lookups
    def kept(pg): return pg.evaluate(f"D.rate.value==={RATE}") and pg.evaluate(READ, 'rate')['value'] == RATE

    asked = []
    pg = t.page(b, rate_opts={'values': FR, 'log': asked})
    pg.wait_for_function("!rateBusy"); asked.clear()
    refresh(pg)
    ok(kept(pg), '₱119 against a saved ₱74.12 is refused when the Currency API says ₱74.12, and the saved rate stays')
    ok('The new rate looked wrong, so the saved rate is still in use' in pg.inner_text('.toast'), 'and the refresh says the new rate looked wrong')
    ok(any('jsdelivr' in u for u in asked) and not any('frankfurter.app' in u for u in asked), 'the second opinion comes from the Currency API, not Frankfurter’s other address')
    ok(pg.evaluate("!RATE_CHECK.ok&&/looked wrong: ₱119\\.00 against the saved ₱74\\.12, and Currency API said ₱74\\.12/.test(RATE_CHECK.fails.at(-1).why)"),
       'the last rate check keeps why: the new rate, the saved one and what the second source said')
    pg.evaluate("go('settings')"); pg.wait_for_timeout(100)
    ok('looked wrong' in pg.inner_text('#app'), 'and Settings › Last rate check shows it')
    pg.evaluate("go('home')"); pg.wait_for_timeout(100)
    pg.fill('#home-item', 'After the odd rate'); pg.fill('#home-price', '741.20'); pg.click('form[data-form=home] .cta')
    pg.wait_for_function("D.purchases.some(p=>p.item==='After the odd rate')")
    ok(pg.evaluate(f"(p=>p.rateAtPurchase==={RATE}&&p.gbpAtPurchase===10)(D.purchases.find(p=>p.item==='After the odd rate'))"),
       'a purchase logged after it is saved at the saved rate (£10.00), never at ₱119')
    refresh(pg, manual=False)
    ok(kept(pg), 'the quiet refresh on opening refuses it too')
    pg.context.close()

    pg = t.page(b, rate_opts={'value': 119})
    refresh(pg)
    ok(pg.evaluate("D.rate.value===119&&D.rate.source.startsWith('Frankfurter')") and 'Rate updated' in pg.inner_text('.toast'),
       'when the Currency API agrees (₱119 too), the new rate is taken')
    pg.context.close()

    pg = t.page(b, rate_opts={'values': {**FR, 'cdn.jsdelivr.net': 119.9}})
    refresh(pg)
    ok(pg.evaluate("D.rate.value===119"), 'a second source within 1% (₱119.90) counts as agreeing')
    pg.context.close()

    pg = t.page(b, rate_opts={'values': {**FR, 'cdn.jsdelivr.net': 117.5, 'currency-api.pages.dev': 117.5}})
    refresh(pg)
    ok(kept(pg) and pg.evaluate("/Currency API said ₱117\\.50/.test(RATE_CHECK.fails.at(-1).why)"), 'one more than 1% away (₱117.50) doesn’t, and the saved rate stays')
    pg.context.close()

    pg = t.page(b, rate_opts={'values': FR, 'down': ['cdn.jsdelivr.net', 'currency-api.pages.dev']})
    refresh(pg)
    ok(kept(pg) and pg.evaluate("/no second source to confirm it/.test(RATE_CHECK.fails.at(-1).why)"), 'with no second source answering, the saved rate stays')
    pg.context.close()

    asked = []
    pg = t.page(b, rate_opts={'values': {'cdn.jsdelivr.net': 119}, 'down': ['api.frankfurter.dev', 'api.frankfurter.app'], 'log': asked})
    pg.wait_for_function("!rateBusy"); asked.clear()  # the page may refresh once as it opens
    refresh(pg)
    ok(kept(pg) and sum('frankfurter' in u for u in asked if LIVE(u)) == 2, 'Frankfurter down and the Currency API at ₱119: refused, without asking Frankfurter again')
    pg.context.close()

    asked = []
    pg = t.page(b, rate_opts={'value': 76.34, 'log': asked})
    pg.wait_for_function("!rateBusy"); pg.evaluate(f"D.rate.value={RATE}"); asked.clear()
    refresh(pg)
    ok(pg.evaluate("D.rate.value===76.34") and 'Rate updated' in pg.inner_text('.toast') and len([u for u in asked if LIVE(u)]) == 1,
       'a 3% move (₱76.34) updates as usual, with no second source asked')
    pg.context.close()

    pg = t.page(b, data={**sample(), 'rate': None}, rate_opts={'value': 119})
    refresh(pg)
    ok(pg.evaluate("D.rate&&D.rate.value===119"), 'with no saved rate yet, only the 30 to 120 range applies')
    pg.context.close()

    # the audit's Wi-Fi login page: a web page where the rate should be
    LOGIN = lambda route: route.fulfill(status=200, content_type='text/html', body='<html><body>Sign in to Wi-Fi</body></html>', headers={'Access-Control-Allow-Origin': '*'})
    pg = t.page(b, rate_opts={'value': 76.34})
    pg.context.route('**/*api.frankfurter.dev/**', LOGIN)
    refresh(pg)
    ok(pg.evaluate("D.rate.value===76.34&&RATE_CHECK.fails[0].why==='unreadable reply'"), 'a Wi-Fi login page from one source is skipped and the next used')
    pg.context.close()
    pg = t.page(b)
    for h in ('api.frankfurter.dev', 'api.frankfurter.app', 'cdn.jsdelivr.net', 'currency-api.pages.dev'): pg.context.route(f'**/*{h}/**', LOGIN)
    refresh(pg)
    ok(kept(pg) and 'the saved rate is still in use' in pg.inner_text('.toast'), 'a Wi-Fi login page from every source leaves the saved rate in use')
    pg.context.close()

    pg = t.page(b)
    pg.context.set_offline(True); pg.wait_for_timeout(100)
    pg.evaluate("go('convert')"); pg.click('#refreshRate'); pg.wait_for_timeout(200)
    ok('You’re offline. Using your saved rate.' in pg.inner_text('.toast'), 'offline, the refresh says so and keeps the saved rate')
    pg.context.set_offline(False)
    pg.context.close()

    # ── updating from Suki 2.0: what the old app saved is all there ──
    import shutil
    from harness import ROOT, url, ready as _ready
    tmp2 = tempfile.mkdtemp()
    old_app = os.path.join(ROOT, 'tests', 'fixtures', 'app-2.0.0')
    for f in os.listdir(old_app): shutil.copy(os.path.join(old_app, f), tmp2)
    page = os.path.join(tmp2, 'index.html')
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', timezone_id='Europe/London', locale='en-GB')
    from harness import rate_route as _rr
    _rr(ctx)
    pg = ctx.new_page()
    pg.goto(url(page)); pg.wait_for_timeout(800)
    pg.fill('#pItem', 'Sorbetes'); pg.fill('#pPrice', '35'); pg.select_option('#pCat', 'Food & drink'); pg.click('#purchaseForm button[type=submit]'); pg.wait_for_timeout(300)
    pg.evaluate("go('search')"); pg.fill('#query', 'bigas'); pg.wait_for_timeout(100); pg.click('[data-item=bigas]'); pg.wait_for_timeout(200)
    pg.fill('#oPrice', '50'); pg.click('#obsForm button'); pg.wait_for_timeout(300)
    # now publish this version over it, at the same address
    for f in os.listdir(old_app): os.remove(os.path.join(tmp2, f))
    for f in ['index.html', 'sw.js', 'manifest.json', 'icon.svg', 'icon-512.png', 'apple-touch-icon.png']: shutil.copy(os.path.join(ROOT, f), tmp2)
    for d in ['js', 'css']: shutil.copytree(os.path.join(ROOT, d), os.path.join(tmp2, d))
    pg.add_init_script("try{localStorage.setItem('suki:motion','0')}catch(e){}")
    pg.reload(); _ready(pg)
    ok(pg.evaluate("D.purchases.length===1&&D.purchases[0].item==='Sorbetes'&&D.purchases[0].price===35") and 'Sorbetes' in pg.inner_text('#app'),
       'a purchase saved by Suki 2.0 is there after updating')
    ok(pg.evaluate("D.observations.length===1&&D.observations[0].itemId==='bigas'&&D.observations[0].price===50"), 'and so is a price note')
    ok(pg.evaluate("!!D.rate"), 'and the saved rate')
    ctx.close()
    shutil.rmtree(tmp2, ignore_errors=True)
