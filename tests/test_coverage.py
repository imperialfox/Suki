"""Q37: what Search can answer. The 85 realistic searches from the 6 Nov 2026 audit (audit_search.py, kept word for word)
and how many of them show a price; the line can only go up. Then the new prices themselves: the DA week of 26 Oct to
1 Nov 2026 (fish, beef, more vegetables, fruit), the medicines from PhilHealth's GAMOT list, and the line for what
Suki doesn't keep (hotels, flights, boats) with Log still offered. Q38: toiletries, the ATM fee, the money changer's margin,
Intramuros and a haircut, each from its own source; the 13 dishes priced as one carinderia plate; every one of the 85 giving
an honest answer. Screenshots at 375 px, light and dark."""

# the audit's 85 searches, in its order (transport, food and market, services and essentials, spelling and language)
SEARCHES = [
    'jeep', 'jeepney fare', 'tricycle', 'trike', 'bus to san jose', 'baliwag', 'cabanatuan bus', 'grab', 'taxi from airport', 'mrt', 'lrt', 'train', 'ferry', 'bangka', 'boat', 'plane ticket', 'toll',
    'adobo', 'chicken', 'rice', '1 kilo bigas', 'bigas', 'egg', 'eggs dozen', 'pork', 'fish', 'tilapia', 'bangus', 'mango', 'banana', 'saging', 'coconut', 'buko', 'lechon', 'sisig', 'pancit', 'balut', 'kwek kwek', 'halo halo', 'jollibee', 'mcdo', 'starbucks', 'coffee', 'water', 'beer', 'red horse', 'coke', 'milk', 'bread', 'pandesal',
    'sim card', 'load', 'data', 'laundry', 'haircut', 'massage', 'hotel', 'room', 'airbnb', 'entrance fee', 'island hopping', 'diving', 'medicine', 'paracetamol', 'pharmacy', 'sunscreen', 'mosquito repellent', 'diapers', 'toilet paper', 'cigarettes', 'atm fee', 'money changer', 'tip',
    'sinigan', 'tinola manok', 'kanin', 'tubig', 'softdrinks', 'gatas', 'sabon', 'kape', 'isda', 'gulay', 'prutas', 'karne',
]
# How many show a price (the top result has one). 50 on 2.38; Q37 (2.39) made it 59; Q38 (2.40) 67. Raise it when more
# are priced; never lower it. The other 18 are below (UNPRICED): each says something true.
PRICED_FLOOR = 67
# Q38: the 18 searches with no price, and what the top result is (None: No clear match, or Suki doesn't keep this).
# Sisig finds its own item, which has no price yet. The rest aren't in the price list (out of Q38's scope).
UNPRICED = {'ferry': None, 'bangka': None, 'boat': None, 'plane ticket': None, 'hotel': None, 'room': None, 'airbnb': None,
            'toll': None, 'coconut': None, 'buko': None, 'lechon': None, 'sisig': 'sisig', 'balut': None, 'island hopping': None,
            'diving': None, 'cigarettes': None, 'tip': None, 'kanin': None}
# Q38: what the eight newly priced searches find
Q38_TOPS = {'sunscreen': 'sunscreen', 'mosquito repellent': 'repellent', 'diapers': 'diaper', 'toilet paper': 'tisyu',
            'atm fee': 'atm-fee', 'money changer': 'money-changer', 'entrance fee': 'intramuros', 'haircut': 'haircut'}
PLATE = 'adobo-p adobo-c sinigang-p sinigang-h tinola menudo afritada karekare paksiw giniling laing pinakbet talong'.split()
# the seven with no price that now say Suki doesn't keep them
NOT_KEPT = ['ferry', 'bangka', 'boat', 'plane ticket', 'hotel', 'room', 'airbnb']

COUNT = """qs => qs.map(q => { const h = searchItems(q, 12); return {q, top: h.length ? h[0].id : null, priced: !!(h.length && priceOf(h[0].id)), nk: notKept(q)}; })"""


def tab(pg, name):
    pg.evaluate("window.scrollTo(0,0)")
    pg.click(f'#dock [data-v={name}]')
    pg.wait_for_function(f"U.tab==='{name}'")


def search(pg, q):
    pg.fill('#q', q)
    pg.wait_for_function("q=>U.q===q", arg=q)


def run(b, t):
    ok = t.ok
    pg = t.page(b, w=375, h=812)

    # ── The audit's 85 searches ──────────────────────────────────
    ok(len(SEARCHES) == 85 and len(set(SEARCHES)) == 85, f'the list is the audit’s 85 searches ({len(SEARCHES)})')
    res = pg.evaluate(COUNT, SEARCHES)
    priced = [r['q'] for r in res if r['priced']]
    print(f'      {len(priced)} of 85 searches show a price')
    ok(len(priced) >= PRICED_FLOOR, f'at least {PRICED_FLOOR} of the 85 show a price ({len(priced)})')
    ok(len(priced) <= PRICED_FLOOR, f'{len(priced)} now show a price: raise PRICED_FLOOR to it')
    for q in ['fish', 'isda', 'tilapia', 'bangus', 'mango', 'prutas', 'medicine', 'paracetamol', 'pharmacy']:
        ok(q in priced, f'“{q}” shows a price now')
    nk = [r['q'] for r in res if r['nk'] and not r['priced'] and r['top'] is None]
    ok(sorted(nk) == sorted(NOT_KEPT), f'the seven hotel, flight and boat searches say Suki doesn’t keep them ({nk})')
    # Q38: every one of the 85 gives an honest answer: a price, or no result at all (No clear match or the not-kept line),
    # or its own item with no price yet, never another item standing in for it
    unp = {r['q']: r['top'] for r in res if not r['priced']}
    ok(unp == UNPRICED, f'the 18 with no price are the known ones, each with no stand-in result ({unp})')
    tops = {r['q']: r['top'] for r in res if r['q'] in Q38_TOPS}
    ok(tops == Q38_TOPS and all(r['priced'] for r in res if r['q'] in Q38_TOPS), f'Q38: the eight new searches find their own priced item ({tops})')

    # ── The DA week ──────────────────────────────────────────────
    R = pg.evaluate("sukiPriceReferences")
    ok(R['periodEnd'] == '2026-11-01' and R['period'] == '26 October – 1 November 2026' and R['marketCount'] == 36,
       f'the DA snapshot is the week of 26 Oct to 1 Nov 2026, 36 markets ({R["period"]}, {R["marketCount"]})')
    ok(R['sourceUrl'].endswith('Weekly-Average-Prices-October-26-November-1-2026.pdf'), 'its link is that week’s bulletin')
    want = {'bangus': [272.70, 245.60], 'tilapia': [157.12], 'mangga': [257.98], 'baka': [447.07, 504.25], 'saging': [66.36, 77.85, 95.99],
            'isda': [212.22, 289.51, 301.52, 341.09], 'bigas': [49.08], 'kamatis': [99.58], 'pusit': [512.94]}
    got = {}
    for r in R['records']:
        got.setdefault(r['itemId'], []).append(r['price'])
    for k, v in want.items():
        ok(got.get(k) == v, f'{k}: the bulletin’s figures ({got.get(k)})')
    ok(len(R['records']) == 47 and len(got) == 33, f'47 records on 33 items ({len(R["records"])}, {len(got)})')
    tops = pg.evaluate("""() => ['bangus', 'mango', 'tilapia', 'banana', 'beef', 'fish'].map(q => { const it = searchItems(q)[0]; const p = priceOf(it.id); return [q, it.id, p.official, p.low]; })""")
    ok(tops == [['bangus', 'bangus', True, 245.6], ['mango', 'mangga', True, 257.98], ['tilapia', 'tilapia', True, 157.12],
                ['banana', 'saging', True, 66.36], ['beef', 'baka', True, 447.07], ['fish', 'isda', True, 212.22]],
       f'bangus, mango, tilapia, banana, beef and fish each find their item with its official price ({tops})')
    ok(pg.evaluate("searchItems('milk').map(i => i.id).join()") == 'gatas' and pg.evaluate("searchItems('milkfish')[0].id") == 'bangus',
       '“milk” finds only Gatas, not Milkfish, and “milkfish” finds Bangus')
    ok(pg.evaluate("searchItems('banana cue')[0].id") == 'bananacue' and pg.evaluate("searchItems('corned beef')[0].id") == 'cornedbeef'
       and pg.evaluate("searchItems('tortang talong')[0].id") == 'talong', 'banana cue, corned beef and tortang talong still find their own items')
    ok(pg.evaluate("['bangus','tilapia','pusit','baka','mangga','saging','paracetamol','ors','cetirizine','loperamide','ampalaya','repolyo'].every(id => glyphFor[id])"),
       'the new items have their own pictures')
    ok(pg.evaluate("['bangus','mangga','repolyo'].every(id => browseOf(itemById(id)) === 'market') && ['paracetamol','ors','cetirizine','loperamide'].every(id => browseOf(itemById(id)) === 'essentials')"),
       'fish, fruit and vegetables sit under Market; the medicines under Essentials')

    # ── Q38: toiletries, money costs, Intramuros, a haircut ──────
    q38 = pg.evaluate("""() => ['tisyu', 'sunscreen', 'repellent', 'diaper', 'shampoo'].map(id => { const r = typicalFor(id);
      return [id, r.length, [...new Set(r.map(x => x.unit))].join(), r.every(x => x.source === 'Watsons' && x.kind === 'listed' && x.url.startsWith('https://www.watsons.com.ph/') && x.date === '2026-11-11')]; })""")
    ok(q38 == [['tisyu', 2, 'per roll', True], ['sunscreen', 2, 'per bottle', True], ['repellent', 2, 'per bottle', True],
               ['diaper', 3, 'per piece', True], ['shampoo', 2, 'per sachet', True]],
       f'toilet paper, sunscreen, repellent, nappies and shampoo come from Watsons’ own pages, one unit each ({q38})')
    pr = pg.evaluate("['tisyu','sunscreen','repellent','diaper','shampoo','atm-fee','money-changer','intramuros','haircut'].map(id => { const p = priceOf(id); return [id, p.low, p.high]; })")
    ok(pr == [['tisyu', 12.92, 20], ['sunscreen', 239, 678], ['repellent', 146, 219.25], ['diaper', 8.58, 15], ['shampoo', 8.75, 10.17],
              ['atm-fee', 250, 250], ['money-changer', 200, 200], ['intramuros', 75, 75], ['haircut', 500, 500]],
       f'their prices, as on the source pages ({pr})')
    atm = pg.evaluate("typicalFor('atm-fee').map(r => [r.source, r.low, r.url.split('/')[2], r.date])")
    ok(atm == [['BDO', 250, 'www.bdo.com.ph', '2026-11-11'], ['Landbank', 250, 'www.landbank.com', '2025-05-13']],
       f'the ATM fee for a card from abroad is from BDO’s and Landbank’s own fee pages ({atm})')
    mc = pg.evaluate("(r => [r.source, r.unit, r.url.split('/')[2], /82\\.46/.test(r.note) && /86\\.46/.test(r.note) && /Convert/.test(r.note)])(typicalFor('money-changer')[0])")
    ok(mc == ['BPI', 'per £100 changed', 'www.bpi.com.ph', True], f'the money changer’s margin is worked out from BPI’s own buy and sell rates, and says how ({mc})')
    ia = pg.evaluate("typicalFor('intramuros').map(r => [r.label, r.low, r.url.split('/')[2]])")
    ok(ia == [['Fort Santiago', 75, 'intramuros.gov.ph'], ['Casa Manila or Baluarte de San Diego', 75, 'intramuros.gov.ph']],
       f'Fort Santiago and the Intramuros sites from the Intramuros Administration’s own site ({ia})')
    hc = pg.evaluate("typicalFor('haircut').map(r => [r.low, r.url.split('/')[2]])")
    ok(hc == [[500, 'theelephantsnookbarbershoportigas.setmore.com']], f'the haircut is a barbershop’s own price, not the AI app’s blog ({hc})')
    ok(pg.evaluate("['tisyu','sunscreen','repellent','diaper','atm-fee','money-changer','intramuros'].every(id => glyphFor[id])"), 'the new items have pictures')
    ok(pg.evaluate("['tisyu','sunscreen','repellent','diaper'].every(id => browseOf(itemById(id)) === 'essentials') && ['atm-fee','money-changer','intramuros'].every(id => browseOf(itemById(id)) === 'services')"),
       'toiletries sit under Essentials; the ATM fee, the money changer and Intramuros under Services (no new chip)')
    # the carinderia plate: one row, and the 13 dishes point to it
    pl = pg.evaluate("""(ids) => ({own: ids.filter(id => window.sukiTypical.items[id]), same: ids.every(id => typicalFor(id) === typicalFor('carinderia')
      && JSON.stringify(priceOf(id)) === JSON.stringify(priceOf('carinderia'))), label: typicalFor('carinderia')[0].label, eng: itemById('carinderia').english})""", PLATE)
    ok(pl['own'] == [] and pl['same'], f'the 13 dishes have no rows of their own and show the carinderia plate’s price ({pl["own"]})')
    ok(pl['label'] == 'A carinderia plate: one ulam with rice' and pl['eng'] == 'Carinderia plate', f'one Carinderia plate item ({pl["label"]}, {pl["eng"]})')
    ok(pg.evaluate("typicalFor('sisig').length === 0 && typicalFor('liempo').length === 0"), 'dishes not on the list (sisig, liempo) aren’t given the plate’s price')

    # ── Medicines ────────────────────────────────────────────────
    med = pg.evaluate("""() => ['paracetamol', 'ors', 'cetirizine'].map(id => { const r = typicalFor(id)[0]; return [id, r.low, r.unit, r.kind, r.source, r.url.startsWith('https://www.philhealth.gov.ph/'), r.date]; })""")
    ok(med == [['paracetamol', 2.25, 'per tablet', 'listed', 'PhilHealth Circular 2026-0018', True, '2026-10'],
               ['ors', 12, 'per sachet', 'listed', 'PhilHealth Circular 2026-0018', True, '2026-10'],
               ['cetirizine', 11.25, 'per tablet', 'listed', 'PhilHealth Circular 2026-0018', True, '2026-10']],
       f'paracetamol ₱2.25, ORS ₱12 and cetirizine ₱11.25 from PhilHealth’s GAMOT list ({med})')
    ok(pg.evaluate("typicalFor('loperamide').length === 0 && !!itemById('loperamide')"), 'loperamide is listed with no price yet (PhilHealth’s list has none)')
    ok(pg.evaluate("['medicine', 'pharmacy', 'gamot', 'botika'].every(q => searchItems(q)[0].id === 'paracetamol' && searchItems(q).length === 4)"),
       'medicine, pharmacy, gamot and botika show the four medicines, paracetamol first')
    ok(pg.evaluate("searchItems('diarrhea')[0].id === 'loperamide' && searchItems('allergy')[0].id === 'cetirizine' && searchItems('ors')[0].id === 'ors'"),
       'diarrhea, allergy and ORS find their medicine')

    # ── What Suki doesn't keep ───────────────────────────────────
    ok(pg.evaluate("['hotel', 'cheap hotel near airport', 'rooms', 'flight to cebu', 'plane ticket', 'ferry to bohol', 'bangka', 'ro-ro', 'boat ride'].every(notKept)"),
       'hotels, rooms, flights, ferries and boats count, as whole words or phrases')
    ok(pg.evaluate("!['jeepney', 'coconut', 'shipping', 'inner', 'boathouse'].some(notKept)"), 'other words, and a word only inside another (shipping, inner), don’t')
    tab(pg, 'search')
    for sc in ('light', 'dark'):
        pg.emulate_media(color_scheme=sc)
        search(pg, 'hotel')
        box = pg.locator('#results #notKept')
        ok(box.count() == 1 and 'Suki doesn’t keep this' in box.inner_text() and 'change daily' in box.inner_text(), f'“hotel” says Suki doesn’t keep it, and why ({sc})')
        ok(pg.locator('#results [data-a=newPurchase][data-item="hotel"]').count() == 1, f'and still offers Log “hotel” as a purchase ({sc})')
        ok('No clear match' not in pg.inner_text('#results'), f'instead of No clear match ({sc})')
        t.shot(pg, f'hotel-{sc}')
    search(pg, 'island hopping')
    ok(pg.locator('#results #notKept').count() == 0, 'a search Suki could price later (island hopping) doesn’t get the line')
    search(pg, 'zzzz')
    ok('No clear match' in pg.inner_text('#results') and pg.locator('#notKept').count() == 0, 'a search for nothing still says No clear match')
    pg.click('#results [data-a=newPurchase][data-item="zzzz"]')
    pg.wait_for_function("U.sheet")
    pg.keyboard.press('Escape')
    pg.wait_for_function("U.sheet===null")
    pg.emulate_media(color_scheme='light')
    tab(pg, 'search')
    search(pg, 'ferry')
    pg.click('#results [data-a=newPurchase][data-item="ferry"]')
    pg.wait_for_function("U.sheet")
    ok('ferry' in (pg.evaluate("(document.querySelector('#layer .sheet input[name=item], #layer .sheet #f-item, #layer .sheet input') || {}).value") or '').lower(),
       'Log “ferry” opens the Log sheet with ferry filled in')
    pg.keyboard.press('Escape')
    pg.wait_for_function("U.sheet===null")

    # ── On screen ────────────────────────────────────────────────
    for q, sc in (('bangus', 'light'), ('mango', 'dark'), ('paracetamol', 'light'), ('prutas', 'dark')):
        pg.emulate_media(color_scheme=sc)
        search(pg, q)
        first = pg.locator('#results .row').first.inner_text()
        ok('₱' in first, f'“{q}” shows a price on screen ({first!r})')
        t.shot(pg, f'{q}-{sc}')
    pg.emulate_media(color_scheme='light')
    pg.evaluate("openSheet('item', {id: 'paracetamol'})")
    pg.wait_for_function("U.sheet==='item'")
    body = pg.inner_text('#layer .sheet')
    ok('PhilHealth' in body and 'shelf price may be higher' in body, 'the paracetamol sheet names PhilHealth and says a pharmacy may charge more')
    t.shot(pg, 'paracetamol-sheet')
    pg.keyboard.press('Escape')
    pg.wait_for_function("U.sheet===null")
    for q, sc in (('sunscreen', 'light'), ('ATM', 'dark'), ('adobo', 'light'), ('money changer', 'dark')):
        pg.emulate_media(color_scheme=sc)
        search(pg, q)
        first = pg.locator('#results .row').first.inner_text()
        ok('₱' in first, f'Q38: “{q}” shows a price on screen ({first!r})')
        t.shot(pg, f'q38-{q.replace(" ", "-").lower()}-{sc}')
    pg.emulate_media(color_scheme='light')
    pg.evaluate("openSheet('item', {id: 'adobo-p'})")
    pg.wait_for_function("U.sheet==='item'")
    body = pg.inner_text('#layer .sheet')
    ok('A carinderia plate: one ulam with rice' in body and '₱50–90' in body, 'the pork adobo sheet shows the carinderia plate’s price')
    t.shot(pg, 'adobo-sheet')
    pg.keyboard.press('Escape')
    pg.wait_for_function("U.sheet===null")
    pg.evaluate("openSheet('item', {id: 'atm-fee'})")
    pg.wait_for_function("U.sheet==='item'")
    body = pg.inner_text('#layer .sheet')
    ok('BDO' in body and 'Landbank' in body and '₱250' in body, 'the ATM fee sheet shows BDO’s and Landbank’s fee')
    t.shot(pg, 'atm-sheet')
    pg.keyboard.press('Escape')
    pg.wait_for_function("U.sheet===null")
    pg.evaluate("openSheet('item', {id: 'bangus'})")
    pg.wait_for_function("U.sheet==='item'")
    body = pg.inner_text('#layer .sheet')
    ok('26 October – 1 November 2026' in body and '36 markets' in body and '₱272.70' in body and '₱245.60' in body, 'the bangus sheet shows the DA card for that week')
    t.shot(pg, 'bangus-sheet')
