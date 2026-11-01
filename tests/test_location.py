"""Location when logging (Q16): a new purchase starts from that day's town (today, or a calendar day), the arrow in
Location fills the town you're in from the outlines kept in the app (allowed, denied, nothing near), typing stops the
filling, editing never changes a place, and nothing asks for the position at launch.

The position is a stand-in for navigator.geolocation (window.__geo), so the tests know exactly what the phone says
and how often it was asked."""
from harness import day, today, BAD_TEXT

GEO = """(()=>{window.__geo={mode:'ok',lat:15.7906,lng:120.992,calls:0,delay:30};
 const g={getCurrentPosition(ok,err){const m=window.__geo;m.calls++;setTimeout(()=>{if(m.mode==='ok')ok({coords:{latitude:m.lat,longitude:m.lng,accuracy:30}});
  else err({code:m.mode==='deny'?1:3,message:m.mode})},m.delay)},watchPosition(){window.__geo.calls++;return 0},clearWatch(){}};
 Object.defineProperty(Navigator.prototype,'geolocation',{get:()=>g,configurable:true})})()"""

# real places, and the town each is in
PLACES = [
    ('San Jose City hall', 15.7906, 120.9920, 'San Jose City'),
    ('CLSU, Muñoz', 15.7370, 120.9300, 'Science City of Muñoz'),
    ('Lupao', 15.8794, 120.8969, 'Lupao'),
    ('Cubao', 14.6195, 121.0518, 'Quezon City'),
    ('Intramuros', 14.5906, 120.9750, 'Manila'),
    ('Cebu IT Park', 10.3300, 123.9050, 'Cebu City'),
    ('Mactan airport', 10.3075, 123.9790, 'Lapu-Lapu'),
    ('Session Road, Baguio', 16.4120, 120.5980, 'Baguio'),
    ('White Beach, Boracay (just off the outline)', 11.9580, 121.9270, 'Malay'),
    ('Alona Beach', 9.5490, 123.7740, 'Panglao'),
    ('Davao', 7.0700, 125.6100, 'Davao City'),
]


def toast_text(pg):
    return ' '.join(pg.locator('.toast').all_inner_texts())


def run(b, t):
    ok = t.ok
    pg = t.page(b, init=GEO)
    T0 = today.isoformat()

    # ── 1 · Nothing asks at launch ───────────────────────────────
    for name in ('spending', 'search', 'till', 'home'):
        pg.click(f'#dock [data-v={name}]'); pg.wait_for_timeout(80)
    pg.click('#dock [data-v=spending]'); pg.wait_for_timeout(80)
    pg.click('#barR [data-a=newPurchase]'); pg.wait_for_timeout(120)
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(100)
    pg.click('#dock [data-v=home]'); pg.wait_for_timeout(80)
    ok(pg.evaluate("window.__geo.calls") == 0, 'nothing asks for the position at launch, or when moving around and opening forms')

    # ── 2 · The town from earlier today ──────────────────────────
    ok(pg.evaluate("F.home.location") == 'SM Megamall', 'Home’s new purchase starts with the place of today’s purchase')
    disc = pg.inner_text('#app .disclose')
    ok('More details' in disc and '· SM Megamall' in disc, 'with More details closed, it shows beside it: “More details · SM Megamall”')
    pg.click('#app .disclose'); pg.wait_for_timeout(100)
    ok(pg.inner_text('label[for=home-location]').replace('\n', ' ') == 'Location · from earlier today' and pg.input_value('#home-location') == 'SM Megamall',
       'opened, the label says “Location · from earlier today”')
    loc, ven = pg.locator('#home-location').bounding_box(), pg.locator('#home-venue').bounding_box()
    form = pg.locator('#app form[data-form=home]').bounding_box()
    ok(loc['width'] > form['width'] * 0.8 and abs(loc['width'] - ven['width']) < 2 and ven['y'] > loc['y'] + loc['height'],
       'Location has the full width, with Where bought underneath')
    pg.fill('#home-item', 'Buko juice'); pg.fill('#home-price', '45')
    pg.reload(); pg.wait_for_function("!document.getElementById('splash')&&typeof U!=='undefined'"); pg.wait_for_timeout(150)
    ok(pg.evaluate("F.home.location==='SM Megamall'&&F.home.locFrom==='auto'&&F.home.item==='Buko juice'"), 'a half-typed purchase keeps its place, and still knows Suki filled it')
    pg.click('#homeSave'); pg.wait_for_timeout(150)
    ok(pg.evaluate("D.purchases[0].item==='Buko juice'&&D.purchases[0].location==='SM Megamall'"), 'saving keeps the place')
    # the newest one wins
    pg.evaluate("U.more=true;rerender()"); pg.wait_for_timeout(80)
    pg.fill('#home-item', 'Taho'); pg.fill('#home-price', '30'); pg.fill('#home-location', 'Quezon City')
    pg.click('#homeSave'); pg.wait_for_timeout(150)
    ok(pg.evaluate("F.home.location") == 'Quezon City' and pg.input_value('#home-location') == 'Quezon City',
       'after a purchase in Quezon City, the next one starts there: the newest purchase that day wins')

    # ── 3 · Spending's + and a calendar day ──────────────────────
    pg.click('#dock [data-v=spending]'); pg.wait_for_timeout(100)
    pg.click('#barR [data-a=newPurchase]'); pg.wait_for_timeout(120)
    ok(pg.input_value('#edit-location') == 'Quezon City' and 'from earlier today' in pg.inner_text('label[for=edit-location]'),
       'Spending’s + starts from today’s town too, “from earlier today”')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(100)
    for n, want in ((1, 'Cubao'), (9, 'El Nido')):
        pg.evaluate(f"(()=>{{const b=document.createElement('button');b.dataset.v='{day(n)}';ACT.newPurchase(b)}})()")
        pg.wait_for_timeout(100)
        ok(pg.input_value('#edit-location') == want and pg.inner_text('label[for=edit-location]').replace('\n', ' ') == 'Location · from that day',
           f'logging on a day {n} back starts from that day’s place ({want}), “from that day”')
        pg.evaluate("closeSheet()"); pg.wait_for_timeout(100)
    pg.evaluate(f"(()=>{{const b=document.createElement('button');b.dataset.v='{day(5)}';ACT.newPurchase(b)}})()"); pg.wait_for_timeout(100)
    ok(pg.input_value('#edit-location') == '' and pg.inner_text('label[for=edit-location]') == 'Location', 'a day with no place leaves Location empty, with no note')

    # ── 4 · The arrow ────────────────────────────────────────────
    btn = '.sheet .locbtn'
    ok(pg.locator(btn).count() == 1 and pg.get_attribute(btn, 'aria-label') == 'Fill in the town you’re in', 'Location has an arrow inside it, with a VoiceOver label')
    bb, ib = pg.locator(btn).bounding_box(), pg.locator('#edit-location').bounding_box()
    ok(bb['width'] >= 44 and bb['height'] >= 44 and bb['x'] + bb['width'] <= ib['x'] + ib['width'] + 1, 'it’s a 44 pt target inside the box')
    pg.click(btn); pg.wait_for_function("F.edit.location==='San Jose City'")
    pg.wait_for_timeout(60)
    ok(pg.input_value('#edit-location') == 'San Jose City' and pg.inner_text('label[for=edit-location]').replace('\n', ' ') == 'Location · near you',
       'tapping it fills the town you’re in (San Jose City), “near you”')
    ok(pg.evaluate("window.__geo.calls") == 1, 'the position was asked for once, on the tap')
    pg.fill('#edit-item', 'Tricycle'); pg.fill('#edit-price', '50'); pg.click('.sheet .cta'); pg.wait_for_timeout(150)
    ok(pg.evaluate(f"D.purchases.some(p=>p.item==='Tricycle'&&p.location==='San Jose City'&&p.date==='{day(5)}')"), 'and it’s saved with the purchase')
    # each place to its town
    for lab, lat, lng, want in PLACES:
        got = pg.evaluate(f"townAt({lat},{lng})")
        ok(got == want, f'{lab} is in {want} (got {got})')
    ok(pg.evaluate("window.sukiTowns.towns.length") == 1642, 'every city and municipality is in the list (1,642)')
    ok(pg.evaluate("townAt(55.8642,-4.2518)") is None, 'Glasgow is no town in the Philippines')
    # nothing near, denied, failed
    pg.evaluate("ACT.newPurchase(document.createElement('button'))"); pg.wait_for_timeout(100)
    before = pg.input_value('#edit-location')
    pg.evaluate("window.__geo.lat=55.8642;window.__geo.lng=-4.2518")
    pg.click(btn); pg.wait_for_timeout(200)
    ok('No town found near you. Type it in instead.' in toast_text(pg) and pg.input_value('#edit-location') == before, 'with no town within 40 km: “No town found near you. Type it in instead.”')
    pg.evaluate("window.__geo.mode='deny'")
    pg.click(btn); pg.wait_for_timeout(200)
    ok('Location is off for Suki. Type the town, or allow it in Settings.' in toast_text(pg) and pg.input_value('#edit-location') == before,
       'denied: “Location is off for Suki. Type the town, or allow it in Settings.”, and the box is left alone')
    pg.evaluate("window.__geo.mode='timeout'")
    pg.click(btn); pg.wait_for_timeout(200)
    ok('Couldn’t find where you are' in toast_text(pg), 'no answer from the phone: “Couldn’t find where you are…”')
    # typing while it looks keeps what he typed
    pg.evaluate("window.__geo.mode='ok';window.__geo.lat=14.5906;window.__geo.lng=120.975;window.__geo.delay=300")
    pg.click(btn); pg.wait_for_timeout(40)
    ok(pg.locator(btn + '.busy').count() == 1, 'the arrow shows it’s looking')
    pg.fill('#edit-location', 'Binondo'); pg.wait_for_timeout(450)
    ok(pg.input_value('#edit-location') == 'Binondo' and pg.locator(btn + '.busy').count() == 0, 'typing while it looks keeps what he typed')
    # closing the sheet while it looks fills nothing
    pg.click(btn); pg.wait_for_timeout(40); pg.evaluate("closeSheet()"); pg.wait_for_timeout(450)
    ok(pg.evaluate("U.sheet") is None and pg.evaluate("window.__geo.calls") >= 5, 'closing the sheet while it looks leaves nothing behind')
    pg.evaluate("window.__geo.delay=30")

    # ── 5 · Typing or clearing stops the filling ─────────────────
    pg.click('#dock [data-v=home]'); pg.wait_for_timeout(100)
    pg.evaluate("U.more=true;rerender()"); pg.wait_for_timeout(80)
    pg.fill('#home-location', ''); pg.evaluate("rerender()"); pg.wait_for_timeout(80)
    ok(pg.input_value('#home-location') == '' and pg.inner_text('label[for=home-location]') == 'Location', 'clearing Location keeps it clear: Suki stops filling it in for this purchase')
    pg.fill('#home-item', 'Pandesal'); pg.fill('#home-price', '25'); pg.click('#homeSave'); pg.wait_for_timeout(150)
    ok(pg.evaluate("D.purchases[0].item==='Pandesal'&&D.purchases[0].location===''"), 'that purchase is saved with no place')
    ok(pg.input_value('#home-location') == 'Quezon City', 'the next purchase starts from today’s town again')
    pg.fill('#home-location', 'Jollibee Cubao'); pg.evaluate("rerender()"); pg.wait_for_timeout(80)
    ok(pg.input_value('#home-location') == 'Jollibee Cubao' and pg.inner_text('label[for=home-location]') == 'Location', 'a typed place stays as typed, with no note')

    # ── 6 · Editing never changes a place ────────────────────────
    pg.evaluate("(()=>{const b=document.createElement('button');b.dataset.k='a3';ACT.editPurchase(b)})()"); pg.wait_for_timeout(120)
    ok(pg.evaluate("U.sheet") == 'edit' and pg.input_value('#edit-location') == '' and pg.inner_text('label[for=edit-location]') == 'Location',
       'editing an old purchase with no place leaves it empty, though its day has one')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(100)
    pg.evaluate("(()=>{const b=document.createElement('button');b.dataset.k='a2';ACT.editPurchase(b)})()"); pg.wait_for_timeout(120)
    ok(pg.input_value('#edit-location') == 'Cubao' and pg.inner_text('label[for=edit-location]') == 'Location', 'and keeps an old place as it was, with no note')
    pg.evaluate("closeSheet()"); pg.wait_for_timeout(100)

    # ── 7 · Settings credits the outlines ────────────────────────
    pg.evaluate("go('settings')"); pg.wait_for_timeout(120)
    s = pg.inner_text('#app')
    ok('Towns for Location' in s and 'NAMRIA and PSA' in s and 'CC BY-IGO' in s and 'never sent anywhere' in s, 'Settings › About credits the town outlines and says they never leave the phone')
    ok(pg.evaluate(BAD_TEXT) == '', 'no undefined, NaN or null anywhere')

    # ── 8 · How it looks ─────────────────────────────────────────
    for sc in ('light', 'dark'):
        p2 = t.page(b, w=375, h=812, sc=sc, init=GEO)
        p2.evaluate("ACT.newPurchase(document.createElement('button'))"); p2.wait_for_timeout(150)
        p2.click('.sheet .locbtn'); p2.wait_for_function("F.edit.location==='San Jose City'"); p2.wait_for_timeout(100)
        ok(p2.evaluate("document.documentElement.scrollWidth<=innerWidth"), f'no sideways scroll at 375 px ({sc})')
        t.shot(p2, f'log-sheet-375-{sc}')
        p2.evaluate("closeSheet()"); p2.wait_for_timeout(150)
        t.shot(p2, f'home-375-{sc}')
        p2.context.close()
    pg.context.close()
