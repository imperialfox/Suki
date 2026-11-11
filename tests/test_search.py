"""Search finds his own records (Q09): prices, then In your purchases (three rows and "Show all N in Spending"), then
In your price notes; the no-match message only when nothing at all matches; the price notes door on All; the
placeholder; and Spending's filter matching the same words, so both doors agree. Light and dark screenshots at 375 px."""
from harness import sample, day


def data():
    d = sample()
    # five more jeepney rides, one of them in Cubao with a note, so "jeepney" has more than three
    for i, (n, place, note) in enumerate([(2, 'Quiapo', ''), (3, 'Cubao', 'Back from the mall'), (4, 'Cubao', ''), (5, 'Makati', ''), (6, 'Pasay', '')]):
        d['purchases'].append({'id': f'j{i}', 'item': 'Jeepney', 'price': 14, 'date': day(n), 'category': 'Transport', 'location': place,
                               'venue': '', 'payment': 'Cash', 'notes': note, 'gbpAtPurchase': None, 'rateAtPurchase': None})
    return d


def tab(pg, name):
    pg.evaluate("window.scrollTo(0,0)")
    pg.click(f'#dock [data-v={name}]')
    pg.wait_for_function(f"U.tab==='{name}'")


def search(pg, q):
    pg.fill('#q', q)
    pg.wait_for_function("q=>U.q===q", arg=q)


def heads(pg):
    return [h.upper() for h in pg.locator('#results .hdr h2').all_inner_texts()]


def run(b, t):
    ok = t.ok
    pg = t.page(b, w=375, h=812, data=data())
    tab(pg, 'search')

    # ── The box says what it searches ────────────────────────────
    ok(pg.get_attribute('#q', 'placeholder') == 'Prices, your purchases, your notes', 'the placeholder reads “Prices, your purchases, your notes”')

    # ── All view: the price notes door comes first ───────────────
    door = pg.locator('#results #notesDoor [data-a=openNotes]')
    ok(door.count() == 1 and pg.locator('#results > *').first.get_attribute('id') == 'notesDoor', 'Search’s All view starts with a Your price notes row')
    ok('Your price notes' in door.inner_text() and '2 notes from the trip' in door.inner_text(), f'it counts the notes ({door.inner_text()!r})')
    t.shot(pg, 'all-light')
    door.click()
    pg.wait_for_function("U.sheet==='notes'")
    ok(pg.inner_text('.sheet h2') == 'Price notes', 'it opens the same Price notes sheet as Settings')
    pg.click('.sheet [data-a=close]')
    pg.wait_for_function("U.sheet===null")
    pg.click('#browse [data-v=transport]')
    pg.wait_for_function("U.scat==='transport'")
    ok(pg.locator('#notesDoor').count() == 0, 'a single category doesn’t repeat the notes row')
    pg.click('#browse [data-v=all]')
    pg.wait_for_function("U.scat==='all'")
    pg.evaluate("go('settings')")
    ok(pg.locator('#app [data-a=openNotes]').count() == 1, 'the Settings row stays as a second door')
    tab(pg, 'search')

    # ── Prices, then In your purchases ───────────────────────────
    search(pg, 'jeepney')
    ok(heads(pg)[:2] == ['PRICES', 'IN YOUR PURCHASES'], f'“jeepney” shows Prices, then In your purchases ({heads(pg)})')
    rows = pg.locator('#mine [data-a=openPurchase]')
    ok(rows.count() == 3, f'three of his purchases are shown (got {rows.count()})')
    ok(rows.first.get_attribute('data-k') == 'a2', 'newest first: yesterday’s ride leads')
    ok('6 purchases' in pg.inner_text('#results .hdr:has(h2:text("In your purchases")) .hint'), 'the header counts all six')
    more = pg.locator('#mine [data-a=searchToSpend]')
    ok(more.count() == 1 and more.locator('.lbl').inner_text() == 'Show all 6 in Spending', 'then “Show all 6 in Spending”')
    t.shot(pg, 'jeepney-light')
    rows.first.click()
    pg.wait_for_function("U.sheet==='purchase'")
    ok(pg.evaluate("U.sd.id") == 'a2' and 'Cubao' in pg.inner_text('.sheet'), 'a purchase row opens the same purchase sheet')
    pg.click('.sheet [data-a=close]')
    pg.wait_for_function("U.sheet===null")

    # ── Show all opens Spending with the same N ──────────────────
    pg.evaluate("U.range='week';U.roff=1;U.cat='Groceries'")
    more.click()
    pg.wait_for_function("U.tab==='spending'")
    ok(pg.evaluate("U.range==='all'&&U.roff===0&&U.cat==='all'") and pg.input_value('#filter') == 'jeepney', 'Show all opens Spending on All, filtered by the same words')
    ok(pg.locator('#spendList [data-a=openPurchase]').count() == 6, 'and Spending shows the same six')
    tab(pg, 'search')

    # ── Every word counts, in any order ──────────────────────────
    search(pg, 'cubao jeepney')
    ok(pg.locator('#mine [data-a=openPurchase]').count() == 3 and pg.locator('#mine [data-a=searchToSpend]').count() == 0,
       '“cubao jeepney” finds the three Cubao rides, words in any order, with no Show all for three')
    search(pg, 'back from')
    ok(pg.locator('#mine [data-a=openPurchase]').count() == 1 and pg.locator('#mine [data-k=j1]').count() == 1, 'notes are searched too (“back from”)')
    search(pg, 'megamall')
    ok(pg.locator('#mine [data-k=a1]').count() == 1, 'and places (“megamall”)')
    search(pg, 'jeepney quiapo makati')
    ok(pg.locator('#mine').count() == 0, 'a word that appears in no purchase rules it out')
    # Spending's filter now matches the same way (Ivan, 1 Nov 2026), so both doors agree
    tab(pg, 'spending')
    pg.fill('#filter', 'cubao jeepney')
    pg.wait_for_function("U.filter==='cubao jeepney'")
    ok(pg.locator('#spendList [data-a=openPurchase]').count() == 3, 'Spending’s filter finds every word in any order too')
    pg.fill('#filter', 'cubao')
    pg.wait_for_function("U.filter==='cubao'")
    ok(pg.locator('#spendList [data-a=openPurchase]').count() == 3, 'one word filters as before')
    pg.click('[data-a=clearFilter]')
    tab(pg, 'search')

    # ── Only his records match: no “No clear match”, but the Log row stays ─
    search(pg, 'island hopping tour')
    txt = pg.inner_text('#results')
    ok('IN YOUR PURCHASES' in heads(pg) and pg.locator('#mine [data-k=a4]').count() == 1, '“island hopping tour” finds his purchase')
    ok('No clear match' not in txt, 'with his own records matching, there’s no “No clear match”')
    ok(pg.locator('#results [data-a=newPurchase]').count() == 1, 'the Log row still shows')
    t.shot(pg, 'island-light')

    # ── In your price notes ──────────────────────────────────────
    search(pg, 'quiapo')
    ok(heads(pg)[-1:] == ['IN YOUR PRICE NOTES'] and pg.locator('#mynotes [data-a=openItem]').count() == 1, f'“quiapo” finds his rice note ({heads(pg)})')
    ok('Bigas · ₱52.00' in pg.inner_text('#mynotes'), 'the note row shows the item and what he saw')
    ok(pg.locator('#mine [data-k=j0]').count() == 1, 'and his Quiapo jeepney ride above it')
    pg.click('#mynotes [data-a=openItem]')
    pg.wait_for_function("U.sheet==='item'")
    ok(pg.evaluate("U.sd.id") == 'bigas', 'a note row opens its item')
    pg.click('.sheet [data-a=close]')
    pg.wait_for_function("U.sheet===null")
    search(pg, 'bigas')
    ok(heads(pg) == ['PRICES', 'IN YOUR PRICE NOTES'], f'“bigas” shows its prices, then the note ({heads(pg)})')

    # ── Nothing at all ───────────────────────────────────────────
    search(pg, 'xqzv')
    ok('No clear match' in pg.inner_text('#results') and pg.locator('#results [data-a=newPurchase]').count() == 1, 'nothing matching says “No clear match”, with the Log row')
    ok(pg.locator('#mine, #mynotes').count() == 0, 'and no empty groups')

    # ── Hostile text stays text ──────────────────────────────────
    pg.evaluate("""D.purchases.push({id:'h1',item:'<img src=x onerror="window.__x=1">tour',price:5,date:localISO(),category:'Other',location:'',venue:'',payment:'Cash',notes:''})""")
    search(pg, 'tour')
    ok(pg.evaluate("!window.__x") and '<img' in pg.inner_text('#mine'), 'a purchase name with markup shows as plain text')
    pg.evaluate("D.purchases=D.purchases.filter(p=>p.id!=='h1')")

    # ── Empty app: the notes row still has somewhere to go ───────
    pg2 = t.page(b, w=375, h=812, data=None)
    tab(pg2, 'search')
    ok('Prices you’ve seen, saved from any item' in pg2.inner_text('#notesDoor'), 'with no notes, the row says what notes are')
    pg2.fill('#q', 'jeepney')
    pg2.wait_for_function("U.q==='jeepney'")
    ok(pg2.locator('#mine, #mynotes').count() == 0 and heads(pg2) == ['PRICES'], 'with nothing logged, Search shows prices only')
    pg2.close()

    # ── Dark ─────────────────────────────────────────────────────
    pd = t.page(b, w=375, h=812, sc='dark', data=data())
    tab(pd, 'search')
    t.shot(pd, 'all-dark')
    pd.fill('#q', 'jeepney')
    pd.wait_for_function("U.q==='jeepney'")
    t.shot(pd, 'jeepney-dark')
    ok(pd.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'no sideways scroll at 375 px in dark')
    pd.close()
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'no sideways scroll at 375 px in light')

    # ── Q36: stricter matching (the cross-audit's search cases, M05 / F3) ─
    pq = t.page(b, w=375, h=812, data=None)
    tab(pq, 'search')

    def prices(q):
        """The item ids in Search's Prices group for q, as he sees them."""
        search(pq, q)
        return pq.evaluate("[...document.querySelectorAll('#results .grp:not(#mine):not(#mynotes):not(#notesDoor) [data-a=openItem]')].map(e=>e.dataset.k)")

    # the six from the audit: nothing, or the right item (Q37 added mango and medicines, so those two find their own)
    for q, want in [('mango', ['mangga']), ('medicine', ['paracetamol', 'ors', 'cetirizine', 'loperamide'])]:
        got = prices(q)
        ok(got == want and 'No clear match' not in pq.inner_text('#results'), f'“{q}” shows only the right item since Q37 (got {got})')
    for q in ['toll', 'coconut', 'kanin']:
        got = prices(q)
        ok(got == [] and 'No clear match' in pq.inner_text('#results') and pq.locator('#results [data-a=newPurchase]').count() == 1,
           f'“{q}” shows no unrelated price, says “No clear match” and offers to log it (got {got})')
    got = prices('load')
    ok(got == ['sim', 'data'], f'“load” shows the SIM card and data promos only (got {got})')
    t.shot(pq, 'q36-load-light')
    prices('mango')
    t.shot(pq, 'q36-mango-light')

    # other loose matches the audits found (Q14's Recon, the cross-audit), checked through the same search. Since Q38
    # "atm" finds its own item, the ATM fee (Q36 allowed nothing, or the right item)
    find = lambda q: pq.evaluate("q=>searchItems(q).map(i=>i.id)", q)
    for q, want in [('mangoes', ['mangga']), ('spaghetti', []), ('gin', []), ('tollgate', []), ('megamall', []), ('atm', ['atm-fee']), ('kanin na hilaw', []), ('coconut milk', []), ('coconut oil', []),
                    ('loaf', ['tasty']), ('ube', ['bus-naia']), ('egg', ['itlog']), ('milk', ['gatas']), ('vinegar', ['suka']), ('ice', ['halo']),
                    ('uber', ['grab']), ('cab', ['taxi'])]:
        got = find(q)
        ok(got == want, f'“{q}” finds {want or "nothing"} (got {got})')
    for q, never in [('rice', 'halo'), ('chickenjoy', 'manok'), ('fishball', 'isda'), ('turon', 'carinderia')]:
        ok(never not in find(q), f'“{q}” doesn’t show {never}')

    # still matching: whole words, plurals, close misspellings, Tagalog and English, words still being typed, phrases
    for q, want in [('jeepney', 'jeepney'), ('jeepneys', 'jeepney'), ('eggs', 'itlog'), ('fish balls', 'fishball'), ('chiken adobo', 'adobo-c'),
                    ('sinigan baboy', 'sinigang-p'), ('tricyle', 'tricycle'), ('trycicle', 'tricycle'), ('coffe', 'kape'), ('manok', 'manok'),
                    ('chicken', 'manok'), ('bigas', 'bigas'), ('rice', 'bigas'), ('uncooked rice', 'bigas'), ('1 kilo bigas', 'bigas'), ('isang kilong bigas', 'bigas'),
                    ('adob', 'adobo-p'), ('sinig', 'sinigang-p'), ('tric', 'tricycle'), ('halo halo', 'halo'), ('bus to san jose', 'bus-sanjose'),
                    ('taro', 'laing'), ('banana', 'turon'), ('sim', 'sim'), ('pork stew', 'menudo'),
                    ('taro leaves in coconut milk', 'laing')]:
        got = find(q)
        ok(want in got, f'“{q}” still finds {want} (got {got})')
    missing = pq.evaluate("CATALOG.flatMap(it=>[it.name,it.english,...it.aliases].filter(n=>!searchItems(n).some(x=>x.id===it.id)).map(n=>it.id+': '+n))")
    ok(missing == [], f'every name, English name and other spelling in the catalogue finds its own item ({missing[:5]})')
    pq.close()

    pd = t.page(b, w=375, h=812, sc='dark', data=None)
    tab(pd, 'search')
    search(pd, 'kanin')
    t.shot(pd, 'q36-kanin-dark')
    pd.close()
