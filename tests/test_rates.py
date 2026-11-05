"""Pounds at the rate you paid (Q22): totals add each purchase at its own rate, a purchase with no rate counts at
today's and the total says so; a back-dated purchase gets that day's ECB rate (the weekday before a weekend, and
Friday's for a Monday in Manila), from Frankfurter, then Currency API, with bad replies ignored; offline it's saved at
once as "estimated" and corrected when signal returns, with nothing else changed; Save never waits for the lookup;
Smart add's "yesterday" and changing a date; the rate behind "In pounds then"; the new fields through cleaning and a
backup; screenshots at 375 and 402 px, light and dark. Synthetic data only."""
import os, json, tempfile
import datetime as dt
from harness import sample, RATE, READ, day, today, ecb_day

GOT = "([id,r])=>{const p=D.purchases.find(x=>x.id===id);return !!p&&!p.rateEstimated&&p.rateAtPurchase===r}"


def last(weekday, before=1):
    """The latest date with this weekday (Mon 0 … Sun 6) at least `before` days ago."""
    d = today - dt.timedelta(days=before)
    while d.weekday() != weekday: d -= dt.timedelta(days=1)
    return d


def p(id, price, date, rate=None, **kw):
    out = {'id': id, 'item': 'Test ' + id, 'price': price, 'date': date, 'category': 'Transport', 'location': '', 'venue': '',
           'payment': 'Cash', 'notes': '', 'gbpAtPurchase': round(price / rate, 2) if rate else None, 'rateAtPurchase': rate}
    out.update(kw)
    return out


def data(purchases):
    d = sample()
    d['purchases'] = purchases
    return d


def log(pg, item, price, date):
    """Log a purchase with the Home form, on a given date."""
    pg.fill('#home-item', item); pg.fill('#home-price', str(price))
    if pg.locator('#home-date').count() == 0: pg.click('[data-a=more]')
    pg.fill('#home-date', date)
    pg.click('form[data-form=home] .cta')
    pg.wait_for_function("it=>D.purchases.some(p=>p.item===it)", arg=item)
    return pg.evaluate("it=>D.purchases.find(p=>p.item===it).id", item)


def run(b, t):
    ok = t.ok

    # ── 1 · Totals add each purchase at its own rate ─────────────
    # £10 + £10 + £10 at three rates; the old way (₱2,441.20 ÷ today's ₱74.12) would say £32.94
    three = [p('r1', 800, day(3), 80), p('r2', 900, day(2), 90), p('r3', 741.2, day(1))]
    pg = t.page(b, data=data(three))
    cap = pg.inner_text('.sumcard .stat:not(.r)')
    ok('≈ £30.00' in cap, 'Home’s total in pounds adds each purchase at its own rate (' + cap.replace('\n', ' / ') + ')')
    ok('1 at today’s rate' in cap, 'and says how many have no rate of their own, counted at today’s')
    pg.click('#dock [data-v=spending]')
    pg.wait_for_function("!!document.getElementById('spendSum')")
    pg.evaluate("U.range='all';rerender()")
    pg.wait_for_function("document.getElementById('spendSum').innerText.includes('≈')")
    st = pg.inner_text('#spendSum')
    ok('≈ £30.00' in st and '1 at today’s rate' in st, 'Spending’s total does the same')
    pg.evaluate("U.cat='Transport';rerender()")
    pg.wait_for_function("!!document.getElementById('spendSum')")
    ok('≈ £30.00' in pg.inner_text('#spendSum'), 'and a category’s total too')
    # a picked bar whose purchases all have their own rate keeps the note's line, empty, so clearing it moves nothing (Q10)
    pg.evaluate("d=>{U.cat='all';U.bar=buckets(spendingList(),period()).findIndex(b=>b.from<=d&&b.to>=d);rerender()}", day(3))
    pg.wait_for_function("U.bar!==null&&!!document.querySelector('#spendSum .rn')")
    h1 = pg.evaluate("document.getElementById('spendSum').offsetHeight")
    empty = pg.evaluate("document.querySelector('#spendSum .rn').innerText.trim()") == ''
    pg.evaluate("U.bar=null;rerender()")
    pg.wait_for_function("U.bar===null&&document.querySelector('#spendSum .rn').innerText.includes('today')")
    ok(empty and pg.evaluate("document.getElementById('spendSum').offsetHeight") == h1, 'a picked day with nothing to note keeps the line empty, so the summary keeps its height')
    # all with their own rate: no note
    pg.evaluate("D.purchases.find(p=>p.id==='r3').rateAtPurchase=74.12;rerender()")
    pg.wait_for_function("!document.querySelector('#spendSum .rn')")
    ok('today’s rate' not in pg.inner_text('#spendSum'), 'with every purchase at its own rate there’s no note')
    pg.evaluate("D.rate=null;D.purchases.find(p=>p.id==='r3').rateAtPurchase=null;rerender()")
    pg.wait_for_function("!!document.getElementById('spendSum')")
    ok('≈' not in pg.inner_text('#spendSum'), 'with no rate at all and none saved, no pounds are guessed')
    pg.context.close()

    # ── 2 · A back-dated purchase gets that day's ECB rate ───────
    sun = last(6, 2)
    fri = (sun - dt.timedelta(days=2)).isoformat()
    yday, before_y = day(1), day(2)
    ecb_y = ecb_day(before_y)  # yesterday's purchase asks for the day before, which may be a weekend
    rates = {fri: 81.11}
    rates.setdefault(ecb_y, 79.5)
    y_rate = rates[ecb_y]
    asked = []
    pg = t.page(b, rate_opts={'days': rates, 'log': asked})
    sid = log(pg, 'Sunday trike', 120, sun.isoformat())
    pg.wait_for_function(GOT, arg=[sid, 81.11])
    s = next(x for x in pg.evaluate(READ, 'purchases') if x['id'] == sid)
    ok(s['rateAtPurchase'] == 81.11 and s['rateDate'] == fri and s['rateSource'] == 'Frankfurter (ECB)' and 'rateEstimated' not in s,
       'a purchase on a Sunday gets Friday’s ECB rate (' + str(s.get('rateDate')) + ')')
    ok(abs(s['gbpAtPurchase'] - round(120 / 81.11, 2)) < 0.001, 'and its pounds follow that rate')
    ok(s['price'] == 120 and s['date'] == sun.isoformat() and s['item'] == 'Sunday trike', 'its price, date and words are as typed')
    ok(any('date=' + (sun - dt.timedelta(days=1)).isoformat() in u for u in asked), 'it asked for the day before (Saturday), which the ECB answers with Friday')
    yid = log(pg, 'Yesterday jeep', 14, yday)
    pg.wait_for_function(GOT, arg=[yid, y_rate])
    ok(pg.evaluate("id=>D.purchases.find(p=>p.id===id).rateDate", yid) == ecb_y, 'a purchase for yesterday gets the rate published the day before')
    n = len(asked)
    tid = log(pg, 'Today taho', 25, today.isoformat())
    pg.wait_for_timeout(300)  # proving nothing happens: give a lookup time to start if one wrongly would
    tp = pg.evaluate("id=>D.purchases.find(p=>p.id===id)", tid)
    ok(tp['rateAtPurchase'] == RATE and 'rateEstimated' not in tp and len(asked) == n, 'today’s purchase keeps today’s saved rate, with no lookup')
    fut = (today + dt.timedelta(days=3)).isoformat()
    fid = log(pg, 'Ferry booked', 900, fut)
    fp = pg.evaluate("id=>D.purchases.find(p=>p.id===id)", fid)
    ok(fp['rateAtPurchase'] == RATE and 'rateEstimated' not in fp, 'a future date keeps today’s saved rate too')

    # the details show the rate behind "In pounds then"
    pg.evaluate("id=>openSheet('purchase',{id})", sid)
    pg.wait_for_function("!!document.querySelector('.sheet .ratewhy')")
    why = pg.inner_text('.sheet .ratewhy')
    fd = dt.date.fromisoformat(fri)
    want = '£1 = ₱81.11 · ' + fd.strftime('%a') + ' ' + str(fd.day) + ' ' + fd.strftime('%b') + (' ' + str(fd.year) if fd.year != today.year else '') + ' · ECB'
    ok(why.replace('\xa0', ' ') == want, 'the details say the rate behind it: “' + why + '”')
    pg.evaluate("closeSheet()")

    # changing a purchase's date takes the new day's rate
    pg.evaluate("id=>openSheet('purchase',{id})", tid)
    pg.wait_for_function("!!document.querySelector('.sheet [data-a=editPurchase]')")
    pg.click('.sheet [data-a=editPurchase]')
    pg.wait_for_function("!!document.getElementById('edit-date')")
    pg.fill('#edit-date', yday)
    pg.click('.sheet .cta')
    pg.wait_for_function(GOT, arg=[tid, y_rate])
    e = pg.evaluate("id=>D.purchases.find(p=>p.id===id)", tid)
    ok(e['date'] == yday and e['price'] == 25, 'changing a purchase’s date to yesterday gives it yesterday’s rate')
    pg.context.close()

    # ── 3 · Monday morning in Manila gets Friday's rate ──────────
    mon = last(0, 2)
    fri2 = (mon - dt.timedelta(days=3)).isoformat()
    pg = t.page(b, ctx_args={'timezone_id': 'Asia/Manila'}, rate_opts={'days': {fri2: 82.22}})
    mid = log(pg, 'Monday breakfast', 150, mon.isoformat())
    pg.wait_for_function(GOT, arg=[mid, 82.22])
    m = pg.evaluate("id=>D.purchases.find(p=>p.id===id)", mid)
    ok(m['rateDate'] == fri2, 'a Monday purchase in Manila gets Friday’s rate (Monday’s isn’t out until about 23:00 there)')
    pg.context.close()

    # ── 4 · Smart add's "yesterday" ───────────────────────────────
    pg = t.page(b, rate_opts={'days': {ecb_y: 79.5}})
    pg.evaluate("switchSide('smart')")
    pg.wait_for_function("!!document.getElementById('smartText')")
    pg.fill('#smartText', 'jeepney 14 yesterday')
    pg.wait_for_function("!!document.querySelector('#smartSave')&&!document.querySelector('#smartSave').classList.contains('dim')")
    pg.click('#smartSave')
    pg.wait_for_function("D.purchases.some(p=>p.said==='jeepney 14 yesterday')")
    sm = pg.evaluate("D.purchases.find(p=>p.said==='jeepney 14 yesterday').id")
    pg.wait_for_function(GOT, arg=[sm, 79.5])
    ok(pg.evaluate("id=>D.purchases.find(p=>p.id===id).date", sm) == yday, 'Smart add’s “yesterday” gets yesterday’s rate')
    pg.context.close()

    # ── 5 · Bad replies are ignored; Currency API fills in ───────
    sat = last(5, 3)  # so the Monday after is yesterday at the latest
    fri3 = (sat - dt.timedelta(days=1)).isoformat()
    # asking for Sunday: Frankfurter answers Friday (bad), Currency API answers Sunday's own file (good)
    sun2 = (sat + dt.timedelta(days=1)).isoformat()
    mon2 = (sat + dt.timedelta(days=2)).isoformat()
    pg = t.page(b, rate_opts={'days': {fri3: 500, sun2: 80.5}})
    bid = log(pg, 'Monday ferry', 600, mon2)
    pg.wait_for_function(GOT, arg=[bid, 80.5])
    bp = pg.evaluate("id=>D.purchases.find(p=>p.id===id)", bid)
    ok(bp['rateSource'] == 'Currency API' and bp['rateDate'] == sun2, 'Frankfurter’s out-of-range reply is ignored and Currency API’s rate for that day is used')
    pg.context.close()
    tried = []
    pg = t.page(b, rate_opts={'days': {fri3: 500, sun2: 500}, 'log': tried})
    bid = log(pg, 'Monday ferry', 600, mon2)
    for _ in range(100):  # wait for all four sources to have been asked
        if sum(1 for u in tried if sun2 in u) >= 4: break
        pg.wait_for_timeout(50)
    pg.wait_for_function("!fixBusy")
    ok(sum(1 for u in tried if sun2 in u) == 4, 'all four sources were asked for that day')
    bp = pg.evaluate("id=>D.purchases.find(p=>p.id===id)", bid)
    ok(bp['rateEstimated'] is True and bp['rateAtPurchase'] == RATE, 'when every reply is bad, it stays at today’s rate, marked estimated')
    pg.context.close()

    # ── 6 · Offline: estimated at once, corrected after signal ───
    pg = t.page(b, rate_opts={'days': {ecb_y: 79.5}})
    pg.context.set_offline(True)
    pg.wait_for_function("!navigator.onLine")
    oid = log(pg, 'Offline halo-halo', 120, yday)
    o = next(x for x in pg.evaluate(READ, 'purchases') if x['id'] == oid)
    ok(o['rateEstimated'] is True and o['rateAtPurchase'] == RATE, 'offline, it saves at once with today’s rate, marked estimated')
    ok('1 estimated' in pg.inner_text('.sumcard'), 'and Home’s total says one is estimated')
    pg.evaluate("id=>openSheet('purchase',{id})", oid)
    pg.wait_for_function("!!document.querySelector('.sheet .ratewhy')")
    ok(pg.inner_text('.sheet .ratewhy').endswith('· estimated'), 'its details say “estimated”: ' + pg.inner_text('.sheet .ratewhy').replace('\xa0', ' '))
    pg.wait_for_function("!document.getAnimations().some(a=>a.playState==='running')")
    t.shot(pg, 'estimated-375-light')
    pg.evaluate("closeSheet()")
    before = {k: v for k, v in o.items() if not k.startswith('rate') and k != 'gbpAtPurchase'}
    pg.context.set_offline(False)
    pg.wait_for_function(GOT, arg=[oid, 79.5], timeout=10000)
    o2 = next(x for x in pg.evaluate(READ, 'purchases') if x['id'] == oid)
    ok('rateEstimated' not in o2 and o2['rateDate'] == ecb_y, 'back online, it’s corrected to that day’s rate and no longer estimated')
    ok({k: v for k, v in o2.items() if not k.startswith('rate') and k != 'gbpAtPurchase'} == before, 'and nothing else on the purchase changed')
    pg.wait_for_function("!document.querySelector('.sumcard').innerText.includes('estimated')")
    ok('2 at today’s rate' in pg.inner_text('.sumcard'), 'Home’s note drops “estimated” once it’s corrected, still counting the two with no rate')
    pg.context.close()

    # ── 7 · Save never waits for the lookup ──────────────────────
    pg = t.page(b)
    held = []
    pg.route('**/*frankfurter.dev/**', lambda r: held.append(r) if 'date=' in r.request.url or '/v1/2' in r.request.url else r.fallback())
    wid = log(pg, 'Slow-signal snack', 60, yday)
    w = pg.evaluate("id=>D.purchases.find(p=>p.id===id)", wid)
    ok(w and w['rateEstimated'] is True, 'with the rate service slow, the purchase is saved straight away')
    ok(any(x['id'] == wid for x in pg.evaluate(READ, 'purchases')), 'and is already in storage')
    pg.wait_for_function("()=>fixBusy")
    ok(len(held) >= 1 and pg.evaluate("id=>D.purchases.find(p=>p.id===id).rateEstimated", wid) is True, 'while the lookup is still waiting for its reply')
    for r in held:
        try: r.fulfill(status=200, content_type='application/json', headers={'Access-Control-Allow-Origin': '*'},
                       body=json.dumps({'date': before_y, 'base': 'GBP', 'quote': 'PHP', 'rate': 78.25}))
        except Exception: pass
    pg.wait_for_function(GOT, arg=[wid, 78.25])
    ok(pg.evaluate("id=>D.purchases.find(p=>p.id===id).rateDate", wid) == before_y, 'and gets its day’s rate when the reply arrives')
    pg.context.close()

    # ── 8 · The new fields survive cleaning and a backup ─────────
    keep = p('k1', 300, day(4), 80.25, rateDate=day(5), rateSource='Frankfurter (ECB)', rateEstimated=True, futureField='kept')
    junk = p('k2', 300, day(4), 80.25, rateDate='30 Feb', rateSource={'x': 1}, rateEstimated='yes')
    pg = t.page(b, data=data([keep, junk]), rate_fail=True)
    c = pg.evaluate("[cleanPurchase(%s),cleanPurchase(%s)]" % (json.dumps(keep), json.dumps(junk)))
    ok(c[0]['rateDate'] == day(5) and c[0]['rateSource'] == 'Frankfurter (ECB)' and c[0]['rateEstimated'] is True and c[0]['futureField'] == 'kept',
       'cleaning keeps the rate’s day, source and “estimated”, and fields it doesn’t know')
    ok('rateDate' not in c[1] and 'rateSource' not in c[1] and 'rateEstimated' not in c[1], 'and drops them when they’re junk')
    bk = pg.evaluate("backupJSON(new Date())")
    bk = json.loads(bk) if isinstance(bk, str) else bk
    k1 = next(x for x in bk['purchases'] if x['id'] == 'k1')
    ok(k1['rateDate'] == day(5) and k1['rateEstimated'] is True and k1['rateSource'] == 'Frankfurter (ECB)', 'a backup keeps them')
    tmp = tempfile.mkdtemp(); f = os.path.join(tmp, 'b.json'); json.dump(bk, open(f, 'w'))
    pg.evaluate("D.purchases=[];save('purchases')")
    pg.set_input_files('#importIn', f)
    pg.wait_for_function("U.sheet==='restore'")
    pg.click('#layer .pk-alert [data-a=yes]')
    pg.wait_for_function("D.purchases.some(p=>p.id==='k1')")
    r1 = next(x for x in pg.evaluate(READ, 'purchases') if x['id'] == 'k1')
    ok(r1['rateDate'] == day(5) and r1['rateEstimated'] is True and r1['futureField'] == 'kept', 'and restoring it brings them back')
    # editing without changing the date leaves the rate alone
    pg.evaluate("id=>openSheet('purchase',{id})", 'k1')
    pg.wait_for_function("!!document.querySelector('.sheet [data-a=editPurchase]')")
    pg.click('.sheet [data-a=editPurchase]')
    pg.wait_for_function("!!document.getElementById('edit-item')")
    pg.fill('#edit-item', 'Test k1 renamed'); pg.click('.sheet .cta')
    pg.wait_for_function("D.purchases.find(p=>p.id==='k1').item==='Test k1 renamed'")
    e1 = pg.evaluate("D.purchases.find(p=>p.id==='k1')")
    ok(e1['rateAtPurchase'] == 80.25 and e1['rateDate'] == day(5) and e1['futureField'] == 'kept', 'an edit that keeps the date keeps the rate and every field')
    pg.context.close()

    # ── 9 · Screenshots: 375 and 402 px, light and dark ──────────
    mix = [p('s1', 800, day(3), 80, rateDate=day(4), rateSource='Frankfurter (ECB)'), p('s2', 900, day(2), 90, rateDate=day(3), rateSource='Frankfurter (ECB)'),
           p('s3', 741.2, day(1)), p('s4', 250, day(1), RATE, rateDate=today.isoformat(), rateSource='Frankfurter (ECB)', rateEstimated=True)]
    for w in (375, 402):
        for sc in ('light', 'dark'):
            pg = t.page(b, w=w, sc=sc, data=data(mix), rate_fail=True)
            wide = pg.evaluate("document.documentElement.scrollWidth>document.documentElement.clientWidth+1")
            ok(not wide, f'{w} px {sc}: no sideways scroll on Home')
            t.shot(pg, f'home-{w}-{sc}')
            pg.evaluate("go('spending')"); pg.wait_for_function("!!document.getElementById('spendSum')")
            pg.evaluate("U.range='all';rerender()"); pg.wait_for_function("!!document.querySelector('#spendSum .rn')")
            t.shot(pg, f'spending-{w}-{sc}', clip={'x': 0, 'y': 0, 'width': w, 'height': 420})
            pg.evaluate("openSheet('purchase',{id:'s4'})"); pg.wait_for_function("!!document.querySelector('.sheet .ratewhy')&&!document.getAnimations().some(a=>a.playState==='running')")
            r = pg.evaluate("(()=>{const v=document.querySelector('.sheet .ratewhy').getBoundingClientRect(),s=document.querySelector('.sheet').getBoundingClientRect();return v.right<=s.right+1&&v.left>=s.left-1})()")
            ok(r, f'{w} px {sc}: the rate line fits inside the sheet')
            t.shot(pg, f'details-{w}-{sc}')
            pg.context.close()
