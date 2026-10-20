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
    txt = pg.inner_text('.sheet')
    ok(pg.evaluate("U.sheet") == 'restore' and 'Purchases' in txt and '4' in txt, 'restoring shows what’s in the backup first')
    pg.click('.sheet [data-a=restoreYes]'); pg.wait_for_timeout(300)
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
    ok('1 damaged record' in pg.inner_text('.sheet') and '17 Oct 2026' in pg.inner_text('.sheet'), 'a 2.0 backup restores, saying what it leaves out')
    pg.click('.sheet .ghost'); pg.wait_for_timeout(100)
    ok(pg.evaluate("U.sheet") is None and len(pg.evaluate(READ, 'observations')) == 2, 'Cancel changes nothing')
    pg.context.close()

    # ── the rate can't load ───────────────────────────────────────
    pg = t.page(b, data={**sample(), 'rate': None}, rate_fail=True)
    pg.evaluate("go('convert')"); pg.wait_for_timeout(200)
    ok(pg.locator('#conv-gbp').is_disabled() and 'No rate yet' in pg.inner_text('#app'), 'with no rate, Convert says so')
    pg.click('#refreshRate'); pg.wait_for_timeout(400)
    ok('Couldn’t load a rate' in pg.inner_text('.toast'), 'a failed refresh explains')
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
