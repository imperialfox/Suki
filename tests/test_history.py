"""Rate history (Q23): the page pushed from Convert's rate row; the four history layers (saved on the phone, Frankfurter's
ECB series v2 then v1, the snapshot shipped with the app, Suki's own daily record), each failing alone and all at
once; a bad reply refused whole; asking only for missing days; older years only for All; the news file's rules; the
headline, the year strip, the chart's sentence, "Why it moved" (hiding with a missing end), the trip line, Convert's
swap followed; every gap saying why (weekends, Monday morning in Manila, offline, no signal yet, a Currency API rate);
scrubbing, snapping to a news dot and opening it, the redraw waiting for the finger; the news and central bank sheets;
swipe back (and not from the chart); Reduce Motion; Settings › Last rate check; screenshots at 375 and 402 px, light
and dark, on its side, iPad and Mac. Synthetic rates only (beyond the shipped snapshot)."""
import re, json, datetime as dt
from harness import sample, day, today, series, series_route, SNAP_END, RATE_HOSTS

TODAY = today.isoformat()
AFTER = (dt.date.fromisoformat(SNAP_END) + dt.timedelta(days=1)).isoformat()
NEW = series(AFTER, TODAY)  # made-up days from the snapshot's end to today
HREAD = """async k=>{const db=await new Promise(res=>{const r=indexedDB.open('suki-rates',1);r.onupgradeneeded=()=>{if(!r.result.objectStoreNames.contains('kv'))r.result.createObjectStore('kv')};r.onsuccess=()=>res(r.result)});
 return await new Promise(res=>{const r=db.transaction('kv','readonly').objectStore('kv').get(k);r.onsuccess=()=>{res(r.result===undefined?null:r.result);db.close()}})}"""
HPUT = """async ([k,v])=>{const db=await new Promise(res=>{const r=indexedDB.open('suki-rates',1);r.onupgradeneeded=()=>{if(!r.result.objectStoreNames.contains('kv'))r.result.createObjectStore('kv')};r.onsuccess=()=>res(r.result)});
 await new Promise(res=>{const t=db.transaction('kv','readwrite');t.objectStore('kv').put(v,k);t.oncomplete=res});db.close()}"""
SETTLED = "!H.busy&&!H.olderBusy&&!!document.getElementById('hbody')"


def open_hist(pg):
    pg.evaluate("go('convert')")
    pg.click('[data-a=openHistory]')
    pg.wait_for_function("U.tab==='history'")
    pg.wait_for_timeout(80)
    pg.wait_for_function(SETTLED, timeout=15000)
    pg.wait_for_timeout(60)


def page(t, b, days=NEW, down=(), bad=None, log=None, w=390, h=844, sc='light', data='sample', touch=False, init=None, ua='default', before=None, ctx_args=None):
    kw = {} if ua == 'default' else {'ua': ua}
    pg = t.page(b, w, h, sc, data=data, touch=touch, init=init, ctx_args=ctx_args, **kw)
    series_route(pg.context, days, down=down, bad=bad, log=log)
    if before: before(pg)
    return pg


def status(pg):
    return pg.inner_text('#hStatus')


def run(b, t):
    ok = t.ok

    # ===== the door, the page, the range pill =====
    log = []
    pg = page(t, b, log=log)
    pg.evaluate("go('convert')")
    ok(pg.locator('.raterow [data-a=openHistory]').count() == 1 and 'Rate history' in pg.inner_text('.raterow') and pg.locator('#refreshRate').count() == 1,
       "Convert's rate row is the door to Rate history, with Refresh still beside it")
    pg.evaluate("go('home')")
    pg.click('#rateCard'); pg.wait_for_timeout(80)
    ok(pg.evaluate("U.tab") == 'convert', "Home's rate card still opens Convert")
    open_hist(pg)
    ok(pg.inner_text('#app h1') == 'Rate history' and pg.evaluate("tabOf(U.tab)") == 'convert', 'the page opens, and belongs to Convert')
    ok(pg.get_attribute('#hSeg [data-v=Y]', 'aria-pressed') == 'true' and [x.inner_text() for x in pg.locator('#hSeg button').all()] == ['M', '6M', 'Y', '5Y', 'All'],
       'the range pill is M · 6M · Y · 5Y · All, opening on Y')
    ok(len(log) == 1 and log[0][0] == 'v2' and log[0][1] == AFTER, f'it asks only for the days after the snapshot ({log})')
    ok(pg.evaluate("histSeries().slice(-1)[0].d") == max(NEW) if NEW else True, 'the new days join the history')
    saved = pg.evaluate(HREAD, 'ecb')
    ok(saved and sorted(saved['days']) == sorted(NEW), 'and are saved on the phone, in their own database')
    head = pg.inner_text('#hHead')
    ok(re.search(r'^₱\d+\.\d\d\s*per £1 · \w{3} \d{1,2} \w{3}', head) and re.search(r'£100 buys ₱[\d,]+, ₱[\d,]+ (more|less) than a year ago', head),
       f'the big figure with its day, and "£100 buys…" against a year ago ({head[:90]!r})')
    ok(re.match(r'(Near the high|Near the low|In the middle) of the year', pg.inner_text('.hstrip b')) and 'Low ₱' in pg.inner_text('.hends') and 'High ₱' in pg.inner_text('.hends'),
       'the year strip says where today sits, with the low and high and their dates')
    ok(pg.inner_text('.hdir') == 'Higher means your pound buys more pesos.', 'which way is good')
    lab = pg.get_attribute('#hsvg', 'aria-label')
    ok(re.match(r'(Up|Down) \d+\.\d% in a year\. High ₱[\d.]+ on \d{1,2} \w+ \d{4}\. Low ₱[\d.]+ on', lab or ''), f'VoiceOver reads the chart as a sentence ({lab!r})')
    ok(pg.locator('#hsvg .hline').count() == 1 and pg.locator('#hsvg .hdot').count() >= 3, 'the line is drawn, with news dots under it')
    ok(pg.locator('#hsvg .hdot.peso').count() >= 1 and pg.locator('#hsvg .hdot.pound').count() >= 1, 'filled dots for peso news and hollow ones for pound news')
    fill = pg.evaluate("[getComputedStyle(document.querySelector('.hdot.peso')).fill,getComputedStyle(document.querySelector('.hdot.pound')).fill,getComputedStyle(document.querySelector('#app')).backgroundColor]")
    ok(fill[0] != fill[1], 'the two kinds differ by shape, in grey')
    ok('Mostly the peso' in pg.inner_text('.hwhy') or re.search(r'Mostly the pound|Both moved|Barely moved', pg.inner_text('.hwhy')), 'the "Why it moved" card')
    ok(re.search(r'the peso (weakened|strengthened) \d+\.\d% and the pound (gained|lost) \d+\.\d%', pg.inner_text('.hwhy')), 'it says how each moved against the dollar')
    rows = pg.locator('#hNews .evrow').count()
    ok(rows == 4 and 'Show all' in pg.inner_text('#hNews'), f'"What happened" shows four rows, then Show all ({rows})')
    pg.click('[data-a=hShowAll]'); pg.wait_for_timeout(60)
    ok(pg.locator('#hNews .evrow').count() > 4, 'Show all shows the rest of the year')
    ok('News checked' in pg.inner_text('#hAge') and 'European Central Bank' in pg.inner_text('.hfoot') and 'No forecasts' in pg.inner_text('.hfoot'),
       'the news age and the sources footer')
    t.shot(pg, 'year-390-light', full_page=True)
    # the pill: the knob slides in place, then the page below changes
    pg.click('#hSeg [data-v=M]'); pg.wait_for_timeout(60)
    ok(pg.evaluate("getComputedStyle(document.getElementById('hSeg')).getPropertyValue('--pk-i').trim()") == '0' and 'a month ago' in pg.inner_text('#hHead'),
       'M: the knob moves and the figures follow')
    pg.click('#hSeg [data-v="5Y"]'); pg.wait_for_timeout(60)
    ok('5 years ago' in pg.inner_text('#hHead') and 'past 5 years' in pg.inner_text('#hbody').lower(), '5Y works from the snapshot')
    # Convert's swap is followed
    pg.evaluate("U.conv.top='php';histRedraw()")
    ok('per ₱100' in pg.inner_text('#hHead') and '₱1,000 buys £' in pg.inner_text('#hHead') and pg.inner_text('.hdir') == 'Higher means your pesos buy more pounds.',
       "with pesos on top in Convert, it shows ₱100 = £… and which way is good for pesos")
    pg.evaluate("U.conv.top='gbp';histRedraw()")
    # back, and opening again lands on Y
    pg.click('#barL [data-v=convert]'); pg.wait_for_timeout(60)
    ok(pg.evaluate("U.tab") == 'convert', 'the back button goes to Convert')
    n0 = len(log); open_hist(pg)
    ok(pg.get_attribute('#hSeg [data-v=Y]', 'aria-pressed') == 'true' and len(log) == n0, 'opening again starts on Y, and asks for nothing new')
    # Settings › Help has the central bank page
    pg.evaluate("go('help')")
    pg.click('[data-a=openCbRate]'); pg.wait_for_timeout(60)
    ok(pg.evaluate("U.sheet") == 'cbrate' and 'Bank of England' in pg.inner_text('.sheet'), "Help › What's a central bank rate?")
    pg.evaluate("closeSheet()")
    pg.context.close()

    # ===== a reload uses the saved history and asks only for what's missing =====
    log = []
    pg = page(t, b, days=series(AFTER, TODAY), log=log)
    open_hist(pg)
    pg.evaluate(HPUT, ['ecb', {'v': 1, 'days': {d: list(v) for d, v in list(NEW.items())[:-1]}, 'older': False}])
    pg.reload(); pg.wait_for_timeout(200)
    from harness import ready
    ready(pg); log.clear(); open_hist(pg)
    if len(NEW) > 1:
        ok(len(log) == 1 and log[0][1] == (dt.date.fromisoformat(sorted(NEW)[-2]) + dt.timedelta(days=1)).isoformat(),
           f'with history saved, only the day after the newest saved one is asked for ({log})')
    pg.evaluate(HPUT, ['ecb', {'v': 1, 'days': {'2026-10-31': [500, 1.3]}}])
    pg.reload(); ready(pg); log.clear(); open_hist(pg)
    ok(pg.evaluate("H.threw") and pg.evaluate(HREAD, 'ecb') is not None and '2026-10-31' not in (pg.evaluate(HREAD, 'ecb') or {}).get('days', {}),
       'saved history that can\'t be read is thrown away and loaded again')
    pg.context.close()

    # ===== each layer failing alone =====
    log = []
    pg = page(t, b, down=('v2',), log=log)
    open_hist(pg)
    ok([x[0] for x in log] == ['v2', 'v1'] and pg.evaluate("Object.keys(H.ecb).length") == len(NEW), 'Frankfurter v2 down: v1 fills in the days')
    pg.context.close()

    pg = page(t, b, down=('v2', 'v1'))
    open_hist(pg)
    ok(pg.locator('#hsvg .hline').count() == 1 and pg.evaluate("histSeries()[0].d") == '2016-01-04', 'Frankfurter down: the chart still draws from the snapshot')
    if TODAY > '2026-11-03':
        ok('Couldn’t reach Frankfurter' in status(pg) and 'History up to 30 Oct' in status(pg), 'and says how far it goes and why')
    else:
        ok('Couldn’t reach Frankfurter' in status(pg) or 'comes at' in status(pg) or 'Rates come' in status(pg), 'and says why the newest days are missing')
    pg.evaluate("go('settings')")
    ok('History: couldn’t load' in pg.inner_text('#app') and 'frankfurter.dev (v2): error 503' in pg.inner_text('#app'), 'Settings › Last rate check says why')
    pg.context.close()

    # the snapshot missing (as if the file never loaded): a year from Frankfurter comes first
    log = []
    year = series((today - dt.timedelta(days=366)).isoformat(), TODAY, php=80, step=0.002)
    pg = page(t, b, days=year, log=log, init="Object.defineProperty(window,'sukiRateSnap',{value:null,writable:false})")
    pg.reload()
    from harness import ready as rd
    rd(pg); log.clear(); open_hist(pg)
    ok(log and log[0][1] == (today - dt.timedelta(days=366)).isoformat() and pg.locator('#hsvg .hline').count() == 1,
       f'no snapshot: one year loads first from Frankfurter ({log[:1]})')
    pg.context.close()

    # all at once: no snapshot, nothing saved, Frankfurter down
    pg = page(t, b, down=('v2', 'v1'), init="Object.defineProperty(window,'sukiRateSnap',{value:null,writable:false})")
    open_hist(pg)
    ok('Connect once to load the history' in pg.inner_text('#hbody') and pg.locator('#hsvg').count() == 0, 'every layer down: "Connect once to load the history", never an empty chart')
    ok(pg.locator('#hNews .evrow').count() >= 1, 'and the news notes, which come with the app, still show')
    pg.context.close()

    # ===== a bad reply is refused whole =====
    for spoil in ['rate', 'order', 'jump', 'shape']:
        log = []
        pg = page(t, b, bad={'v2': spoil, 'v1': spoil}, log=log)
        open_hist(pg)
        ok(pg.evaluate("Object.keys(H.ecb).length") == 0 and len(log) == 2 and pg.evaluate("HIST_CHECK&&!HIST_CHECK.ok"),
           f'a reply with {"a bad rate" if spoil == "rate" else "dates out of order" if spoil == "order" else "a 20% jump" if spoil == "jump" else "the wrong shape"} is refused whole, from both')
        pg.context.close()
    pg = page(t, b, bad={'v2': 'jump'})
    open_hist(pg)
    ok(pg.evaluate("Object.keys(H.ecb).length") == len(NEW), 'a bad v2 reply is thrown away and v1 is used instead')
    pg.context.close()

    # ===== the "Why it moved" card hides with a missing end =====
    nousd = dict(NEW)
    if nousd:
        k = max(nousd); nousd[k] = (nousd[k][0], None)
        pg = page(t, b, days=nousd)
        open_hist(pg)
        ok(pg.locator('.hwhy').count() == 0 and pg.locator('#hsvg .hline').count() == 1, 'with no dollar rate at one end, "Why it moved" hides; it never guesses')
        pg.context.close()

    # ===== Suki's own record: a rate from Currency API is its own hollow dot, with its source =====
    d = sample(); d['rate'] = dict(d['rate'], value=85.9, date=TODAY, source='Currency API')
    pg = page(t, b, days={}, data=d)
    open_hist(pg)
    ok(pg.locator('#hsvg .hown').count() == 1 and 'is from Currency API, not the ECB' in status(pg), "today's saved rate from Currency API: a hollow dot, and a line saying so")
    pg.evaluate("go('convert')")
    pg.evaluate("RATE_CHECK=null;refreshRate(false)"); pg.wait_for_timeout(400)
    own = pg.evaluate(HREAD, 'own')
    ok(own and any(v['src'].startswith('Frankfurter') for v in own['days'].values()), 'every rate Suki loads is kept in its own record, with its source')
    pg.context.close()

    # ===== the trip line =====
    trip = [{'id': 'old', 'item': 'Test entry', 'price': 10, 'date': day(40), 'category': 'Other'},
            {'id': 't1', 'item': 'Jeep', 'price': 14, 'date': day(12), 'category': 'Transport'},
            {'id': 't2', 'item': 'Jeep', 'price': 14, 'date': day(3), 'category': 'Transport'}]
    d = sample(); d['purchases'] = trip
    pg = page(t, b, data=d)
    open_hist(pg)
    start = (today - dt.timedelta(days=12))
    want = f'Since {start.day} {start.strftime("%b")}'
    ok(want in pg.inner_text('#hHead') and pg.locator('#hsvg .htrip').count() == 1, f'the trip starts at the first purchase of the latest unbroken stretch, not a test entry weeks before ({want})')
    pg.evaluate("D.purchases=D.purchases.filter(p=>p.id==='old');histRedraw()")
    ok('Since' not in pg.inner_text('#hHead') and pg.locator('#hsvg .htrip').count() == 0, 'with no purchase in the last 14 days, no trip line')
    pg.evaluate("D.purchases=[];histRedraw()")
    ok('Since' not in pg.inner_text('#hHead'), 'and none with nothing logged')
    pg.context.close()

    # ===== every gap says why =====
    # a Saturday: no new rate at weekends
    pg = page(t, b, days={}, before=lambda p: (p.clock.set_fixed_time(dt.datetime(2026, 10, 31, 12, 0)), p.reload()))
    rd(pg); open_hist(pg)
    ok('No new rate at weekends. Last: Friday 30 Oct.' in status(pg), 'at the weekend: no new rate, and the last one was Friday')
    pg.context.close()
    # Monday morning in Manila: Monday's rate comes at 11 pm there
    pg = page(t, b, days={}, ctx_args={'timezone_id': 'Asia/Manila'}, before=lambda p: (p.clock.set_fixed_time(dt.datetime(2026, 11, 2, 1, 0)), p.reload()))
    rd(pg); open_hist(pg)
    ok('Monday’s rate comes at about 4 pm UK time, 11 pm in Manila.' in status(pg), "Monday morning: Monday's rate comes at 4 pm UK time, 11 pm in Manila")
    pg.context.close()
    # offline after a load, and offline on the first open
    pg = page(t, b)
    open_hist(pg)
    pg.context.set_offline(True); pg.wait_for_timeout(150)
    ok('Offline. The history is saved on your phone.' in status(pg), 'offline: the history is saved on the phone')
    pg.click('#hSeg [data-v=All]'); pg.wait_for_timeout(100)
    ok('From 4 Jan 2016. Older years load when you’re back online.' in status(pg) and pg.locator('#hsvg .hline').count() == 1, 'All offline: from 2016, and older years load later')
    pg.context.close()
    pg = page(t, b, init="Object.defineProperty(navigator,'onLine',{get:()=>false})")
    open_hist(pg)
    ok('Connect once to load the history since 30 Oct' in status(pg) and pg.locator('#hsvg .hline').count() == 1, 'first open with no signal: the snapshot, and "Connect once to load the history"')
    pg.context.close()

    # ===== older years only when All is tapped =====
    log = []
    old = series('2005-04-01', '2015-12-31', php=90, step=0.0)
    pg = page(t, b, days=dict(old, **NEW), log=log)
    open_hist(pg)
    ok(all(x[1] >= '2016' for x in log), 'the years before 2016 aren\'t asked for until All is tapped')
    pg.click('#hSeg [data-v=All]')
    ok(pg.locator('.hload').count() == 1 or pg.evaluate("H.older"), '"Loading older years…" while they come')
    pg.wait_for_function(SETTLED + "&&H.older", timeout=15000)
    ok(pg.evaluate("histSeries()[0].d") == '2005-04-01' and 'in April 2005' in pg.inner_text('#hHead'), 'then All goes back to April 2005')
    ok(pg.evaluate(HREAD, 'ecb')['older'] is True, 'and the older years are saved too')
    pg.click('#hNews [data-a=hShowAll]') if pg.locator('#hNews [data-a=hShowAll]').count() else None
    ok('UK votes to leave the EU' in pg.inner_text('#hNews') and 'Bank of England cuts its rate as the crisis spreads' in pg.inner_text('#hNews'), 'with the older news notes')
    pg.context.close()

    # ===== the news file's rules =====
    pg = page(t, b)
    nw = pg.evaluate("window.sukiNews")
    notes = nw['notes']
    dates_ok = all(re.match(r'^\d{4}-\d{2}-\d{2}$', n['date']) and dt.date.fromisoformat(n['date']) <= today for n in notes)
    ok(dates_ok and dt.date.fromisoformat(nw['checked']) <= today, 'every news note has a real date, none in the future, and a checked date')
    ok(all(n['side'] in ('peso', 'pound') for n in notes), 'every note has a side: peso or pound')
    ok(all(0 < len(n['title']) <= 60 for n in notes), 'every title is under about 60 characters')
    ok(all(re.match(r'^https://(www\.)?(bsp\.gov\.ph|bankofengland\.co\.uk|psa\.gov\.ph)/', n['url']) for n in notes), 'every note links to the BSP, the Bank of England or the PSA')
    keys = [n['date'] + n['side'] for n in notes]
    ok(len(keys) == len(set(keys)), 'no two notes on the same day and side')
    ok(all(n.get('body') and n.get('tag') and n.get('src') for n in notes), 'each has a plain explanation, a tag and its source')
    pg.evaluate("window.sukiNews.checked='2026-08-01'")
    open_hist(pg)
    ok('over a month ago' in pg.inner_text('#hAge') and pg.locator('#hsvg .hlate').count() == 1, 'old news says so plainly, and the news lane is greyed after that date')
    ok(all(r <= '2026-08-01' for r in pg.evaluate("[...document.querySelectorAll('#hNews .evrow')].map(e=>e.dataset.k.slice(0,10))")), 'notes after the checked date aren\'t shown')
    pg.context.close()

    # ===== scrubbing, snapping to a news dot, and opening it =====
    pg = page(t, b)
    open_hist(pg)
    box = pg.locator('#hchart').bounding_box()
    x = pg.evaluate("(()=>{const n=hNotesIn(HGEO.pts).find(n=>n.date==='2026-09-17');return HGEO.X(n.date)})()")
    y = box['y'] + 80
    pg.mouse.move(box['x'] + 40, y); pg.mouse.down()
    ok(pg.evaluate("!!HSCRUB&&!!HSCRUB.d") and re.search(r'^₱\d+\.\d\d', pg.inner_text('#hHead')) and re.search(r'\w+day \d{1,2} \w+ \d{4}', pg.inner_text('#hHead')),
       'a finger on the chart: the headline follows it, with the long date')
    pg.evaluate("rerender()")
    ok(pg.evaluate("HPEND") and pg.locator('#hcur').is_visible(), 'a redraw waits while the finger is down, so the chart doesn\'t snap away')
    pg.mouse.move(box['x'] + x + 9, y, steps=4)
    ok('Bank of England holds at 3.75% · let go to read' in pg.inner_text('#hHead'), 'within 12 pt of a news dot it snaps to it and shows its title')
    pg.mouse.up(); pg.wait_for_timeout(80)
    ok(pg.evaluate("U.sheet") == 'news' and 'Bank of England holds at 3.75%' in pg.inner_text('.sheet'), 'letting go there opens its news sheet')
    ok(re.search(r'£1 that week\s*₱[\d.]+ → ₱[\d.]+', pg.inner_text('.sheet')) and pg.locator('.sheet a[href*="bankofengland.co.uk"]').count() == 1,
       'the sheet has £1 that week and the link to the official statement')
    pg.wait_for_timeout(400)
    pg.click('.sheet [data-a=openCbRate]'); pg.wait_for_timeout(60)
    ok(pg.evaluate("U.sheet") == 'cbrate', "What's a central bank rate? opens over it")
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(60)
    ok(pg.evaluate("U.sheet") == 'news', 'and closing it goes back to the news sheet')
    pg.evaluate("closeSheet()")
    pg.mouse.move(box['x'] + 30, y); pg.mouse.down(); pg.mouse.move(box['x'] + 60, y, steps=3); pg.mouse.up(); pg.wait_for_timeout(60)
    ok(pg.evaluate("U.sheet") is None and not pg.locator('#hcur').is_visible() and 'let go' not in pg.inner_text('#hHead'), 'letting go away from a dot opens nothing and puts the headline back')
    pg.click('#hNews .evrow >> nth=0'); pg.wait_for_timeout(60)
    ok(pg.evaluate("U.sheet") == 'news', 'a row in What happened opens its sheet too')
    pg.evaluate("closeSheet()")
    pg.context.close()

    # ===== swipe back =====
    pg = page(t, b)
    open_hist(pg)
    h1 = pg.locator('#app h1').bounding_box()
    sy = h1['y'] + h1['height'] / 2
    pg.mouse.move(20, sy); pg.mouse.down(); pg.mouse.move(60, sy, steps=4)
    ok(pg.locator('#under').count() == 1 and 'translateX' in pg.evaluate("document.querySelector('body > .wrap').style.transform"), 'swiping right: the page follows the finger, with Convert underneath')
    pg.mouse.move(50, sy, steps=2); pg.mouse.up(); pg.wait_for_timeout(80)
    ok(pg.evaluate("U.tab") == 'history' and pg.locator('#under').count() == 0, 'a short swipe springs back')
    pg.mouse.move(20, sy); pg.mouse.down(); pg.mouse.move(260, sy, steps=8); pg.mouse.up(); pg.wait_for_timeout(120)
    ok(pg.evaluate("U.tab") == 'convert' and pg.locator('#under').count() == 0 and pg.evaluate("document.querySelector('body > .wrap').style.transform") == '',
       'past a fifth of the screen it goes back to Convert, leaving nothing behind')
    pg.wait_for_timeout(400)
    open_hist(pg)
    box = pg.locator('#hchart').bounding_box()
    pg.mouse.move(box['x'] + 10, box['y'] + 60); pg.mouse.down(); pg.mouse.move(box['x'] + 300, box['y'] + 60, steps=8); pg.mouse.up(); pg.wait_for_timeout(80)
    ok(pg.evaluate("U.tab") == 'history', 'dragging on the chart scrubs; it never swipes back')
    pg.context.close()

    # with motion on: the push slides in over Convert (Q24); Reduce Motion fades it
    pg = page(t, b, init="localStorage.setItem('suki:motion','1')")
    pg.evaluate("go('convert')")
    pg.evaluate("(()=>{window.KF=[];const a=Element.prototype.animate;Element.prototype.animate=function(k,o){if(this.matches&&this.matches('body > .wrap'))KF.push(JSON.stringify(k));return a.call(this,k,o)}})()")
    pg.click('[data-a=openHistory]'); pg.wait_for_timeout(30)
    kf = pg.evaluate("KF")
    ok(any('translateX(390px)' in k for k in kf) and pg.locator('#under').count() == 1, 'with motion on, the page slides in from the right, over a still copy of Convert')
    pg.wait_for_function("!document.querySelector('#under')", timeout=6000)
    # swipe back: Convert moves a third and lifts its 10% dim with the finger, and letting go is on the nav spring (Q24)
    h1 = pg.locator('#app h1').bounding_box()
    sy = h1['y'] + h1['height'] / 2
    pg.mouse.move(20, sy); pg.mouse.down(); pg.mouse.move(215, sy, steps=6)
    cx = pg.evaluate("new DOMMatrix(getComputedStyle(document.querySelector('#under > .wrap')).transform).m41")
    dim = pg.evaluate("+getComputedStyle(document.querySelector('#under .pdim')).opacity")
    k = pg.evaluate("parseFloat(document.querySelector('body > .wrap').style.transform.slice(11))") / 390
    ok(abs(cx - (-0.33 * 390 * (1 - k))) < 2 and abs(dim - 0.1 * (1 - k)) < 0.005, f'swiping: Convert sits {cx:.0f} pt left and dimmed {dim:.3f}, following the finger')
    pg.mouse.up(); pg.wait_for_timeout(20)
    tm = pg.evaluate("document.querySelector('body > .wrap').getAnimations().map(a=>[a.effect.getTiming().easing,a.effect.getTiming().duration])")
    nav = pg.evaluate("MOTION.dur('nav')")
    ok(tm and tm[0][0].startswith('linear(0 0%, 0.0147') and tm[0][1] == nav and print('   ', tm[0][0][:60], tm[0][1], nav) is None, f'letting go runs on the nav spring ({tm[0][1] if tm else None} ms), not its own 280 ms curve')
    pg.wait_for_function("U.tab==='convert'&&!document.querySelector('#under')", timeout=6000)
    ok(pg.evaluate("document.querySelector('body > .wrap').style.transform") == '', 'and it lands on Convert with nothing left behind')
    pg.context.close()
    pg = page(t, b, init="localStorage.setItem('suki:motion','1');localStorage.setItem('suki:reduceMotion','on')")
    pg.evaluate("go('convert')")
    pg.evaluate("(()=>{window.KF=[];const a=Element.prototype.animate;Element.prototype.animate=function(k,o){if(this.id==='app')KF.push(JSON.stringify(k));return a.call(this,k,o)}})()")
    pg.click('[data-a=openHistory]'); pg.wait_for_timeout(30)
    kf = pg.evaluate("KF")
    ok(kf and all('translate' not in k and 'opacity' in k for k in kf), 'with Reduce Motion, it fades instead')
    pg.wait_for_function(SETTLED)
    pg.click('#hSeg [data-v=M]'); pg.wait_for_timeout(60)
    ok('a month ago' in pg.inner_text('#hHead'), 'and the range pill still works')
    pg.context.close()

    # ===== screenshots, sizes and devices =====
    for w, h in [(375, 812), (402, 874)]:
        for sc in ['light', 'dark']:
            pg = page(t, b, w=w, h=h, sc=sc)
            open_hist(pg)
            fits = pg.evaluate("document.documentElement.scrollWidth<=innerWidth")
            ok(fits, f'{w} px {sc}: nothing scrolls sideways')
            t.shot(pg, f'page-{w}-{sc}', full_page=True)
            pg.click('#hNews .evrow >> nth=1'); pg.wait_for_timeout(80)
            t.shot(pg, f'news-{w}-{sc}')
            pg.context.close()
    for name, w, h, ua in [('side', 852, 393, 'default'), ('ipad', 820, 1180, 'default'), ('ipad-land', 1180, 820, 'default'), ('mac', 1440, 900, None)]:
        pg = page(t, b, w=w, h=h, ua=ua)
        open_hist(pg)
        two = pg.evaluate("(()=>{const a=document.querySelector('.hmain').getBoundingClientRect(),b=document.querySelector('.hside').getBoundingClientRect();return b.left>=a.right-1&&Math.abs(a.top-b.top)<40})()")
        ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth") and (two if name != 'side' else True),
           f'{name}: fits' + (', with the chart and the news side by side' if name != 'side' else ''))
        t.shot(pg, f'page-{name}', full_page=True)
        pg.context.close()
