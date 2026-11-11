"""The price data (Q35): every typical price in js/typical.js and every official record in js/prices.js has a real date
(not in the future), a secure link, a source and a known catalogue id; one item's prices share one unit; no row is copied
across more than 2 items (the carinderia row is on KNOWN_COPIES until Q38 replaces it; the list can only shrink).
The check is proven on broken copies. On screen: pandesal, the SIM card and the tourist SIM show one unit; MRT-3 and
LRT-2 show the half fare; a typical price over 90 days old shows its month and a newer one doesn't; the sources line
gives the real range of dates; the DA card notes its age only once its week is over 30 days old. Screenshots at 375 px,
light and dark."""
import json
from harness import day

# copies of one row across more than 2 items, allowed for now: (label, why). Remove a line when its copies go.
KNOWN_COPIES = [
    ('At a carinderia, with rice', 'Q38 replaces the 13 dish rows with one Carinderia plate item'),
]

# the check, in the page: returns a list of problems in plain words
LINT = r"""([typ, refs, ids, today, known]) => {
  const out = [], ID = new Set(ids), KINDS = ['fare', 'srp', 'shop', 'menu', 'listed', 'guide'];
  const real = (d) => { const m = /^(\d{4})-(\d{2})(?:-(\d{2}))?$/.exec(d || ''); if (!m) return false;
    const x = new Date(Date.UTC(+m[1], +m[2] - 1, +(m[3] || 1))); return x.getUTCMonth() === +m[2] - 1 && x.getUTCDate() === +(m[3] || 1); };
  const start = (d) => (d.length === 7 ? d + '-01' : d);
  const okDate = (d) => real(d) && start(d) <= today;
  if (!okDate(typ.checked)) out.push('typical.js: checked date ' + JSON.stringify(typ.checked));
  const copies = {};
  Object.entries(typ.items || {}).forEach(([id, rows]) => {
    if (!ID.has(id)) out.push(id + ': not a catalogue id');
    if (!Array.isArray(rows) || !rows.length) return out.push(id + ': no prices');
    const units = [...new Set(rows.map((r) => (r.unit || '').trim()))];
    if (units.length > 1) out.push(id + ': more than one unit (' + units.join(' / ') + ')');
    rows.forEach((r) => {
      const at = id + ' · ' + r.label;
      if (!okDate(r.date)) out.push(at + ': date ' + JSON.stringify(r.date || ''));
      if (!/^https:\/\/[^\s/]+\.[^\s]+$/.test(r.url || '')) out.push(at + ': link isn’t https ' + JSON.stringify(r.url || ''));
      if (!(r.source || '').trim()) out.push(at + ': no source');
      if (!(r.label || '').trim() || !(r.unit || '').trim()) out.push(at + ': no label or unit');
      if (!(typeof r.low === 'number' && typeof r.high === 'number' && r.low > 0 && r.low <= r.high)) out.push(at + ': price ' + r.low + '–' + r.high);
      if (!KINDS.includes(r.kind)) out.push(at + ': kind ' + JSON.stringify(r.kind));
      const k = JSON.stringify([r.label, r.low, r.high, r.unit, r.url]);
      (copies[k] = copies[k] || new Set()).add(id);
    });
  });
  const seen = new Set();
  Object.entries(copies).forEach(([k, s]) => {
    if (s.size <= 2) return;
    const label = JSON.parse(k)[0];
    if (known.includes(label)) return seen.add(label);
    out.push('"' + label + '" is copied across ' + s.size + ' items (' + [...s].join(', ') + ')');
  });
  known.forEach((l) => !seen.has(l) && out.push('KNOWN_COPIES lists "' + l + '", which is no longer copied: take it off the list'));
  if (!okDate(refs.periodEnd)) out.push('prices.js: periodEnd ' + JSON.stringify(refs.periodEnd || ''));
  if (!/^https:\/\//.test(refs.sourceUrl || '')) out.push('prices.js: link isn’t https');
  const ru = {};
  (refs.records || []).forEach((r) => {
    if (!ID.has(r.itemId)) out.push('prices.js · ' + r.item + ': unknown item id ' + JSON.stringify(r.itemId));
    if (!(typeof r.price === 'number' && r.price > 0)) out.push('prices.js · ' + r.item + ': price ' + r.price);
    (ru[r.itemId] = ru[r.itemId] || new Set()).add(r.unit);
  });
  Object.entries(ru).forEach(([id, s]) => s.size > 1 && out.push('prices.js · ' + id + ': more than one unit (' + [...s].join(' / ') + ')'));
  return out;
}"""

def lint(pg, change=None):
    """The problems in the app's data, or in a copy of it with `change` (JS run on t and r) made first."""
    return pg.evaluate("""([lint, change]) => {
      const t = JSON.parse(JSON.stringify(window.sukiTypical)), r = JSON.parse(JSON.stringify(window.sukiPriceReferences));
      if (change) new Function('t', 'r', change)(t, r);
      return eval(lint)([t, r, CATALOG.map((i) => i.id), localISO(), %s]);
    }""" % json.dumps([k for k, _ in KNOWN_COPIES]), [LINT, change])


def row(pg, q, id):
    pg.fill('#q', q)
    pg.wait_for_function("q=>U.q===q", arg=q)
    r = pg.locator(f'#results [data-a=openItem][data-k="{id}"]')
    return r.inner_text().replace('\n', ' ') if r.count() else ''


def item(pg, id):
    pg.evaluate("id=>openSheet('item',{id})", id)
    pg.wait_for_function("id=>U.sheet==='item'&&!!document.querySelector('#layer .sheet .dhead')", arg=id)
    return pg.locator('#layer .sheet').last


def close(pg):
    pg.keyboard.press('Escape')
    pg.wait_for_function("U.sheet===null")


def run(b, t):
    ok = t.ok
    pg = t.page(b, w=375, h=812)

    # ── The data ────────────────────────────────────────────────
    probs = lint(pg)
    ok(not probs, 'every price has a real date, an https link, a source, a known id and one unit per item, and no new copied row' + (': ' + '; '.join(probs[:8]) if probs else ''))
    n = pg.evaluate("Object.values(window.sukiTypical.items).reduce((a,r)=>a+r.length,0)")
    ok(n >= 90, f'the check read every typical price ({n})')

    # ── The check catches each kind of fault (on copies) ────────
    for change, want, what in [
        ("t.items.jeepney[0].date=''", 'jeepney · Traditional jeepney: date ""', 'a missing date'),
        ("t.items.lrt2[0].date='2023-08 (fare matrix)'", 'date "2023-08 (fare matrix)"', 'a broken date'),
        ("t.items.lrt2[0].date='2026-02-30'", 'date "2026-02-30"', 'a date that doesn’t exist'),
        ("t.items.taxi[0].date='2999-01-01'", 'date "2999-01-01"', 'a date in the future'),
        ("t.items.taxi[0].url='http://www.philstar.com/'", 'link isn’t https', 'a non-https link'),
        ("t.items.pandesal[1].unit='per pack'", 'pandesal: more than one unit', 'two units in one item'),
        ("['taho','turon','kikiam'].forEach(k=>t.items[k]=[Object.assign({},t.items.isaw[0])])", 'copied across', 'a row copied across more than 2 items'),
        ("t.items['not-an-item']=[Object.assign({},t.items.taxi[0])]", 'not-an-item: not a catalogue id', 'an unknown item id'),
        ("r.records[0].itemId='rice-x'", 'unknown item id "rice-x"', 'an unknown id in the DA snapshot'),
        ("r.records.push(Object.assign({},r.records[0],{unit:'per sack'}))", 'prices.js · bigas: more than one unit', 'two units in the DA snapshot'),
        ("t.items.taxi[0].source=''", 'no source', 'a missing source'),
        ("t.items.taxi[0].low=99", 'price 99–65', 'a low above the high'),
    ]:
        got = lint(pg, change)
        ok(any(want in p for p in got), f'the check catches {what} ({got[:1]})')
    got = pg.evaluate("([lint])=>eval(lint)([window.sukiTypical, window.sukiPriceReferences, CATALOG.map((i) => i.id), localISO(), ['At a carinderia, with rice','Not copied anywhere']])", [LINT])
    ok(any('no longer copied' in p for p in got), 'a KNOWN_COPIES line that’s no longer copied fails, so the list can only shrink')
    got = pg.evaluate("([lint])=>eval(lint)([window.sukiTypical, window.sukiPriceReferences, CATALOG.map((i) => i.id), localISO(), []])", [LINT])
    ok(any('At a carinderia, with rice' in p and 'copied across' in p for p in got), f'without its KNOWN_COPIES line the carinderia row fails ({len(got)} problem)')

    # ── One unit in each Search row ─────────────────────────────
    pg.click('#dock [data-v=search]')
    pg.wait_for_function("U.tab==='search'")
    r = row(pg, 'pandesal', 'pandesal')
    ok('₱2–2.73' in r and 'per piece' in r, f'pandesal shows one unit, per piece ({r!r})')
    r = row(pg, 'sim card', 'sim')
    ok('₱59–99' in r and 'Prepaid SIM' in r, f'the SIM card is ₱59–99, without the airport package ({r!r})')
    r = row(pg, 'tourist sim', 'sim-tourist')
    ok('₱500–1,000' in r, f'the tourist SIM package is its own item ({r!r})')
    ok(pg.evaluate("itemById('sim-tourist').unit") == 'per package' and pg.evaluate("wordItemFor('Tourist SIM at the airport')") == 'sim-tourist', 'it’s per package, and a logged “Tourist SIM” matches it')

    # ── The rail half fare is the headline ──────────────────────
    r = row(pg, 'mrt', 'mrt3')
    ok('₱6–14' in r, f'MRT-3 shows the half fare, ₱6–14 ({r!r})')
    r = row(pg, 'lrt2', 'lrt2')
    ok('₱8–18' in r, f'LRT-2 shows the half fare, ₱8–18 ({r!r})')
    s = item(pg, 'mrt3').inner_text()
    ok('Full fare ₱13–28' in s and '23 Mar 2026' in s, 'MRT-3’s note keeps the full fare and the day the discount began')
    close(pg)
    s = item(pg, 'lrt2').inner_text()
    ok('Full fare ₱15–35' in s and '23 Mar 2026' in s, 'LRT-2’s note keeps the full fare and the day the discount began')
    close(pg)

    # ── A price's age ──────────────────────────────────────────
    import datetime as dt
    month = lambda iso: dt.date.fromisoformat(iso).strftime('%B %Y')
    old, new = day(120), day(10)
    pg.evaluate("([a,b])=>{const r=window.sukiTypical.items.tricycle;r[0].date=b;r[1].date=a}", [old, new])
    s = item(pg, 'tricycle')
    kinds = s.locator('.ofrow small.kind').all_inner_texts()
    ages = [s.locator('.ofrow').nth(i).locator('.age').count() for i in range(2)]
    ok(month(old) in kinds[1] and ages == [0, 1], f'a price over 90 days old shows its month, a newer one doesn’t ({kinds[1]!r}, {ages})')
    head = s.locator('.typical > p.small').last.inner_text()
    ok(head == f'Sources dated {month(old)} to {month(new)}:', f'the sources line gives the real range ({head!r})')
    t.shot(pg, 'tricycle-light')
    close(pg)
    pg.evaluate("([a])=>{const r=window.sukiTypical.items.tricycle;r[0].date=a;r[1].date=a}", [day(91)])
    s = item(pg, 'tricycle')
    ok(all(month(day(91)) in k for k in s.locator('.ofrow small.kind').all_inner_texts()), 'the month shows from 91 days')
    close(pg)
    pg.evaluate("([a])=>{const r=window.sukiTypical.items.tricycle;r[0].date=a;r[1].date=a}", [day(90)])
    s = item(pg, 'tricycle')
    ok(s.locator('.ofrow .age').count() == 0, 'and not at 90 days')
    close(pg)
    pg.evaluate("([a])=>{window.sukiTypical.items.kikiam[0].date=a}", [day(120)[:7]])
    s = item(pg, 'kikiam')
    ok(month(day(120)[:7] + '-01') in s.inner_text(), 'a month-only date over 90 days old shows its month too')
    ok(s.locator('.typical > p.small').last.inner_text().startswith('Source dated '), 'one source says “Source dated …”')
    close(pg)

    # ── The DA card's age ──────────────────────────────────────
    for n, want in [(10, None), (30, None), (31, '4 weeks'), (40, '5 weeks'), (100, '3 months')]:
        pg.evaluate("d=>window.sukiPriceReferences.periodEnd=d", day(n))
        s = item(pg, 'bigas')
        a = s.locator('#daAge')
        if want:
            ok(a.count() == 1 and a.inner_text() == f'This week is {want} old. Prices may have moved since.', f'a week {n} days old: “{a.inner_text() if a.count() else ""}”')
        else:
            ok(a.count() == 0, f'a week {n} days old has no age note')
        if n == 40: t.shot(pg, 'bigas-light')
        close(pg)

    # dark mode
    dk = t.page(b, w=375, h=812, sc='dark')
    dk.evaluate("([a,b])=>{const r=window.sukiTypical.items.tricycle;r[0].date=b;r[1].date=a;window.sukiPriceReferences.periodEnd=a}", [day(120), day(10)])
    item(dk, 'tricycle'); t.shot(dk, 'tricycle-dark'); close(dk)
    item(dk, 'bigas'); t.shot(dk, 'bigas-dark'); close(dk)
