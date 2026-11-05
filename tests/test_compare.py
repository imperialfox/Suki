"""A number next to something to compare it with (Q12): the calendar's three spending tints (by thirds of the
month's spending days, the middle step for fewer than three days, equal days together), the key, the picked day in
solid ink, and the price range strip on an item (a band per typical price, a dot for each time paid, a ring for each
price note, stacking, the axis and key, the dot–row link both ways, the label kept inside at both ends, nothing
animating). Screenshots at 375 and 402 px, light and dark."""
import datetime as dt
from harness import sample, day, today, RATE


def month_back(n):
    """The first of the month n months before this one."""
    y, m = today.year, today.month - n
    while m < 1:
        y, m = y - 1, m + 12
    return dt.date(y, m, 1)


A = month_back(2)  # six days with different amounts
B = month_back(3)  # two days
C = month_back(4)  # four days, all the same amount


def p(i, item, price, date, loc='', cat='Food & drink'):
    return {'id': i, 'item': item, 'price': price, 'date': date, 'category': cat, 'location': loc, 'venue': '',
            'payment': 'Cash', 'notes': '', 'gbpAtPurchase': None, 'rateAtPurchase': None}


def data():
    d = sample()
    iso = lambda m, n: m.replace(day=n).isoformat()
    d['purchases'] += [p('m%d' % n, 'Lunch', v, iso(A, n)) for n, v in [(3, 50), (5, 120), (8, 300), (11, 640), (14, 1200), (20, 4800)]]
    d['purchases'] += [p('b1', 'Lunch', 90, iso(B, 4)), p('b2', 'Lunch', 2500, iso(B, 9))]
    d['purchases'] += [p('c%d' % n, 'Lunch', 200, iso(C, n)) for n in (2, 6, 10, 15)]
    # jeepney: two set fares (₱14 and ₱17); paid ₱14 twice (they stack), ₱17 once, and a ₱20 price note
    # (the sample also has a ₱13 jeepney, so that's four times paid)
    d['purchases'] += [p('j1', 'Jeepney', 14, day(0), 'Cubao', 'Transport'), p('j2', 'Jeepney', 14, day(2), 'Quiapo', 'Transport'),
                       p('j3', 'Modern jeepney', 17, day(3), 'Bulakan to Barrio', 'Transport')]
    d['observations'] += [{'id': 'oj', 'itemId': 'jeepney', 'itemName': 'Dyip', 'price': 20, 'date': day(4), 'location': 'San Jose City', 'venue': '', 'note': 'Fare sign'}]
    return d


def cal(pg, m, picked=None):
    pg.evaluate(f"U.calM='{m.isoformat()}';U.calD={repr(picked) if picked else 'null'};openSheet('calendar')")
    pg.wait_for_function(f"U.sheet==='calendar'&&U.calM==='{m.isoformat()}'")
    return pg.locator('.sheet .cday').evaluate_all(
        "els=>Object.fromEntries(els.map(e=>[e.dataset.v,(e.className.match(/\\bt([123])\\b/)||[])[1]||'']))")


def close(pg):
    pg.evaluate("U.stack=[];U.sheet=null;U.sd={};rerender()")
    pg.wait_for_function("U.sheet===null")


def item(pg, id):
    pg.evaluate(f"U.dot=null;openSheet('item',{{id:'{id}'}})")
    pg.wait_for_function(f"U.sheet==='item'&&!!document.querySelector('#layer .sheet .dhead')")


def lit(pg):
    return pg.evaluate("""(()=>{const s=document.querySelector('#layer .sheet');
      return {u:U.dot,dots:[...s.querySelectorAll('.sdot.on')].map(e=>e.dataset.dot),
              rows:[...s.querySelectorAll('.row.lit')].map(e=>e.dataset.dot),
              label:s.querySelector('.slabel.on')?s.querySelector('.slabel').textContent:''}})()""")


def inside(pg):
    """Whether the lit label sits inside the strip's track."""
    return pg.evaluate("""(()=>{const s=document.querySelector('#layer .sheet'),l=s.querySelector('.slabel').getBoundingClientRect(),
      t=s.querySelector('.strip').getBoundingClientRect();return l.width>0&&l.left>=t.left-0.5&&l.right<=t.right+0.5})()""")


def run(b, t):
    ok = t.ok
    pg = t.page(b, w=402, h=874, data=data())

    # ── 1 · Calendar tints ───────────────────────────────────────
    a = cal(pg, A)
    got = [a[A.replace(day=n).isoformat()] for n in (3, 5, 8, 11, 14, 20)]
    ok(got == ['1', '1', '2', '2', '3', '3'], f'six spending days are tinted in thirds, lightest to strongest ({got})')
    ok(all(v == '' for k, v in a.items() if int(k[-2:]) not in (3, 5, 8, 11, 14, 20)), 'days with no spending stay plain')
    bg = pg.evaluate("[1,2,3].map(n=>getComputedStyle(document.querySelector('.sheet .cday.t'+n)).backgroundColor)")
    ok(len(set(bg)) == 3 and 'rgba(0, 0, 0, 0)' not in bg, f'the three steps are three different tints ({bg})')
    lab = pg.get_attribute(f'.sheet .cday[data-v="{A.replace(day=20).isoformat()}"]', 'aria-label')
    ok(lab.endswith('₱4,800.00'), f'VoiceOver still reads the day’s amount ({lab})')
    ok(pg.locator('.sheet .tkey').count() == 1 and pg.inner_text('.sheet .tkey').replace('\n', ' ').split() == ['Less', 'More']
       and pg.locator('.sheet .tkey i').count() == 3, 'a “Less ● ● ● More” key sits under the grid')
    ok(pg.get_attribute('.sheet .tkey', 'aria-hidden') == 'true', 'the key is hidden from VoiceOver (the days read their amounts)')
    ok('Stronger days are the ones you spent more on' in pg.inner_text('.sheet .foot'), 'the footnote says what the tints mean')

    # a picked day is solid ink, never a tint
    big = A.replace(day=20).isoformat()
    pg.click(f'.sheet .cday[data-v="{big}"]')
    pg.wait_for_function(f"U.calD==='{big}'")
    st = pg.evaluate(f"""(()=>{{const e=document.querySelector('.sheet .cday[data-v="{big}"]'),c=getComputedStyle(e),r=getComputedStyle(document.documentElement);
      return [c.backgroundColor,c.color,e.classList.contains('on')]}})()""")
    ok(st[0] == 'rgb(0, 0, 0)' and st[1] == 'rgb(242, 242, 247)' and st[2], f'a picked day is solid black with light text ({st[:2]})')
    tapped_big = pg.evaluate("U.calD")
    ok(tapped_big == big and 'Lunch' in pg.inner_text('.sheet'), 'tapping a day still shows what you bought')
    close(pg)

    b_ = cal(pg, B)
    ok([v for v in b_.values() if v] == ['2', '2'], 'fewer than three spending days all get the middle step')
    close(pg)
    c_ = cal(pg, C)
    ok([v for v in c_.values() if v] == ['2'] * 4, 'days with the same amount share a step (four equal days: the middle)')
    close(pg)
    empty = month_back(6)
    cal(pg, empty)
    ok(pg.locator('.sheet .tkey').count() == 0 and 'Stronger days' not in pg.inner_text('.sheet'), 'a month with nothing logged has no key')
    close(pg)
    # today keeps its outline
    cal(pg, today.replace(day=1))
    ok(pg.locator('.sheet .cday.today').count() == 1 and 'inset' in pg.evaluate("getComputedStyle(document.querySelector('.sheet .cday.today')).boxShadow"),
       'today keeps its outline')
    ok(pg.evaluate("document.querySelector('.sheet .cday.today').getAnimations().length===0"), 'the tints don’t animate')
    close(pg)

    # ── 2 · The price range strip ─────────────────────────────────
    item(pg, 'jeepney')
    s = '#layer .sheet '
    ok(pg.locator(s + '.typical .strip').count() == 1, 'the jeepney sheet has a price range strip in its typical-prices card')
    ok(pg.evaluate("(()=>{const c=document.querySelector('#layer .sheet .typical');const r=c.querySelectorAll('.ofrow');return !!(c.querySelector('.strip').compareDocumentPosition(r[r.length-1])&2)&&!!c.querySelector('.strip ~ .small')})()"),
       'it sits under the price rows, before the sources')
    bands = pg.locator(s + '.strip .band').evaluate_all("els=>els.map(e=>{const r=e.getBoundingClientRect();return [r.left,r.right]})")
    ok(len(bands) == 2 and bands[0][1] <= bands[1][0], f'one band per typical price, and the two never merge ({bands})')
    ok(pg.locator(s + '.sdot.s-paid').count() == 4 and pg.locator(s + '.sdot.s-note').count() == 1, 'a dot for each time paid and a ring for the price note')
    st = pg.evaluate("""[...document.querySelectorAll('#layer .sheet .sdot')].map(e=>{const r=e.querySelector('i').getBoundingClientRect();return [e.dataset.dot,Math.round(r.left+r.width/2),Math.round(r.top+r.height/2)]})""")
    j1 = next(x for x in st if x[0] == 'paid:j1'); j2 = next(x for x in st if x[0] == 'paid:j2')
    ok(abs(j1[1] - j2[1]) <= 1 and abs(j1[2] - j2[2]) >= 11, f'two ₱14 dots stack upwards ({j1}, {j2})')
    ax = pg.inner_text(s + '.strip .axis').split()
    ok(ax == ['₱10', '₱25'], f'the axis shows a rounded low and high ({ax})')
    ok(pg.inner_text(s + '.skey').split() == ['Typical', 'You', 'paid', 'Price', 'notes'], 'the key says Typical · You paid · Price notes')
    txt = pg.inner_text(s + '.strip').lower()
    ok(not any(w in txt for w in ('good', 'bad', 'overcharged', 'cheap', 'expensive', 'fair')), 'no good or bad words')
    al = pg.get_attribute(s + '.sdot[data-dot="paid:j1"]', 'aria-label')
    ok(al == 'You paid ₱14, Today, Cubao', f'each dot reads what it is to VoiceOver ({al})')

    # dot → row
    pg.click(s + '.sdot[data-dot="paid:j3"]')
    L = lit(pg)
    ok(L['u'] == 'paid:j3' and L['dots'] == ['paid:j3'] and L['rows'] == ['paid:j3'], f'tapping a dot lights it and its row in You paid ({L})')
    ok(L['label'] == '₱17 · 3 days ago · Bulakan to Barrio', f'and shows its label ({L["label"]})')
    ok(inside(pg), 'the label stays inside the strip')
    ok(pg.evaluate("document.querySelectorAll('#layer .sheet .strip *').length>0&&[...document.querySelectorAll('#layer .sheet .strip *')].every(e=>e.getAnimations().length===0)")
       and pg.evaluate("getComputedStyle(document.querySelector('#layer .sheet .sdot.on i')).transitionDuration") == '0s', 'nothing on the strip animates')
    pg.click(s + '.sdot[data-dot="paid:j3"]')
    ok(lit(pg)['u'] is None and not lit(pg)['rows'] and lit(pg)['label'] == '', 'tapping the lit dot again clears it')
    # row → dot (a price note row)
    pg.click(s + '.row[data-dot="note:oj"] .lbl')
    L = lit(pg)
    ok(L['dots'] == ['note:oj'] and L['rows'] == ['note:oj'] and L['label'] == '₱20 · 4 days ago · San Jose City', f'tapping a price note row lights its ring ({L})')
    # tapping elsewhere clears it
    pg.click(s + '.dhead h3')
    ok(lit(pg) == {'u': None, 'dots': [], 'rows': [], 'label': ''}, 'tapping elsewhere clears it')
    # the bin on a note row doesn't light it
    pg.click(s + '.row[data-dot="note:oj"] [data-a=delObs]')
    pg.wait_for_function("U.sheet!=='item'")
    ok(pg.evaluate("U.dot") is None, 'the bin on a price note row opens the delete alert without lighting the ring')
    pg.click('#layer .pk-alert [data-a=no]')
    pg.wait_for_function("U.sheet==='item'")
    # a You paid row still opens the purchase, and its dot is lit when you come back
    pg.click(s + '.row[data-dot="paid:j2"]')
    pg.wait_for_function("U.sheet==='purchase'")
    ok(pg.evaluate("U.dot") == 'paid:j2', 'a You paid row still opens the purchase')
    pg.click('#layer .sheet [data-a=close]')
    pg.wait_for_function("U.sheet==='item'&&!!document.querySelector('#layer .sheet .strip')")
    L = lit(pg)
    ok(L['dots'] == ['paid:j2'] and L['rows'] == ['paid:j2'] and L['label'].startswith('₱14 · 2 days ago'), f'coming back, its dot and row are lit ({L})')
    close(pg)

    # the label stays inside at both ends
    ends = data()
    ends['purchases'] += [p('t1', 'Tricycle', 16, day(1), 'Somewhere with a long place name, Nueva Ecija', 'Transport'),
                          p('t2', 'Tricycle', 95, day(2), 'Another long place name to push the label wide', 'Transport')]
    pg2 = t.page(b, w=375, h=812, data=ends)
    item(pg2, 'tricycle')
    for k in ('paid:t1', 'paid:t2'):
        pg2.click(f'#layer .sheet .sdot[data-dot="{k}"]')
        ok(pg2.evaluate("U.dot") == k and inside(pg2), f'at 375 px the label stays inside the strip at the {"low" if k.endswith("1") else "high"} end')
    t.shot(pg2, 'strip-ends-375')
    close(pg2)
    # no strip without anything to compare
    item(pg2, 'halo')
    ok(pg2.locator('#layer .sheet .typical').count() == 1 and pg2.locator('#layer .sheet .strip').count() == 0,
       'an item with typical prices but nothing paid and no notes has no strip')
    close(pg2)
    pg2.context.close()

    # ── 3 · Screenshots, light and dark ───────────────────────────
    for w, h in ((375, 812), (402, 874)):
        for sc in ('light', 'dark'):
            q = t.page(b, w=w, h=h, sc=sc, data=data())
            cal(q, A, A.replace(day=14).isoformat())
            ok(q.evaluate("document.documentElement.scrollWidth<=innerWidth"), f'{w} px {sc}: the calendar has no sideways scroll')
            t.shot(q, f'calendar-{w}-{sc}')
            close(q)
            item(q, 'jeepney')
            q.click('#layer .sheet .sdot[data-dot="paid:j1"]')
            q.locator('#layer .sheet .strip').scroll_into_view_if_needed()
            ok(q.evaluate("document.documentElement.scrollWidth<=innerWidth") and inside(q), f'{w} px {sc}: the strip fits, label inside')
            t.shot(q, f'strip-{w}-{sc}')
            q.context.close()
    pg.context.close()
