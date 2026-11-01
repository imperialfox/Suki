"""Time doors on Spending (Q10): the period label opens the calendar on that period's month (with the day picked for
D or a picked day bar), a picked bar narrows the list under a "Showing … only" line with the way back, tapping a
purchase in that list keeps the pick, and Help lists Home's title. Light and dark screenshots at 375 px."""
import datetime as dt
from harness import sample, day, today


def tab(pg, name):
    pg.evaluate("window.scrollTo(0,0)")
    pg.click(f'#dock [data-v={name}]')
    pg.wait_for_function(f"U.tab==='{name}'")


def set_range(pg, rng, off=0):
    pg.evaluate(f"U.range='{rng}';U.roff={off};U.bar=null;U.cat='all';U.filter='';rerender()")
    pg.wait_for_function(f"U.range==='{rng}'&&!!document.getElementById('spendSum')")


def tap_bar(pg, i):
    pg.locator('#chart').scroll_into_view_if_needed()
    box = pg.locator('#chart .col').nth(i).bounding_box()
    pg.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] - 4)
    pg.wait_for_function(f"U.bar==={i}")


def open_cal(pg):
    pg.click('#spendSum .plabel.cal')
    pg.wait_for_function("U.sheet==='calendar'")
    return pg.evaluate("[U.calM, U.calD]")


def close_sheet(pg):
    pg.click('.sheet [data-a=close]')
    pg.wait_for_function("U.sheet===null")


def rows(pg):
    return pg.locator('#spendList [data-a=openPurchase]').evaluate_all("els=>els.map(e=>e.dataset.k)")


def first(d):
    return d.replace(day=1).isoformat()


def run(b, t):
    ok = t.ok
    pg = t.page(b, w=375, h=812, data=sample())
    tab(pg, 'spending')
    this_month = first(today)

    # ── 1 · The period label is a door to the calendar ───────────
    lab = pg.locator('#spendSum .plabel.cal')
    ok(lab.count() == 1 and lab.evaluate("e=>e.tagName") == 'BUTTON' and lab.locator('svg').count() == 1,
       'Spending’s period label is a button with a small calendar glyph')
    ok(lab.get_attribute('aria-label').endswith('. Open the calendar') and lab.get_attribute('aria-label').startswith('Since'),
       'VoiceOver reads the period, then “Open the calendar”')
    accent = pg.evaluate("(()=>{const e=document.createElement('i');e.style.color='var(--accent)';document.body.appendChild(e);const c=getComputedStyle(e).color;e.remove();return c})()")
    ok(pg.evaluate("getComputedStyle(document.querySelector('#spendSum .plabel.cal')).color") == accent, 'the label is in the accent colour, not grey')
    ok(open_cal(pg) == [this_month, None], 'All opens the calendar on this month, with no day picked')
    close_sheet(pg)

    set_range(pg, 'week')
    sun = today + dt.timedelta(days=6 - today.weekday())
    ok(open_cal(pg) == [first(min(sun, today)), None], 'W (this week) opens on this week’s month')
    close_sheet(pg)
    set_range(pg, 'week', 2)
    sun2 = today + dt.timedelta(days=6 - today.weekday() - 14)
    ok(open_cal(pg) == [first(sun2), None], 'an earlier week opens on that week’s month')
    close_sheet(pg)

    set_range(pg, 'month', 1)
    last = (today.replace(day=1) - dt.timedelta(days=1)).replace(day=1)
    ok(open_cal(pg) == [last.isoformat(), None], 'M (last month) opens on last month')
    close_sheet(pg)

    set_range(pg, 'day')
    ok(open_cal(pg) == [this_month, today.isoformat()], 'D opens with today picked')
    close_sheet(pg)
    set_range(pg, 'day', 1)
    y = today - dt.timedelta(days=1)
    ok(open_cal(pg) == [first(y), y.isoformat()] and 'Groceries' in pg.inner_text('.sheet'),
       'D on yesterday opens with yesterday picked, listing that day')
    close_sheet(pg)

    # ── 2 · A picked bar narrows the list ────────────────────────
    set_range(pg, 'all')
    n = pg.locator('#chart .col').count()
    ok(n == 10 and len(rows(pg)) == 4 and pg.locator('#pickLine').count() == 0, 'All shows ten bars and every purchase, with no “Showing” line')
    tap_bar(pg, n - 2)
    ok(sorted(rows(pg)) == ['a2', 'a3'] and pg.inner_text('#spendSum .plabel') == 'Yesterday', 'tapping yesterday’s bar narrows the list to yesterday')
    ok(pg.inner_text('#pickLine span') == 'Showing Yesterday only', 'a line says “Showing Yesterday only”')
    back = pg.evaluate("'Show '+period().label.replace(/^Since/,'all since')")
    ok(pg.inner_text('#pickLine .tbtn') == back and back.startswith('Show all since '), f'its button goes back to the whole period (“{back}”)')

    # the label door follows the picked day
    ok(open_cal(pg) == [first(y), y.isoformat()], 'with a day picked, the label opens the calendar on that day')
    close_sheet(pg)
    ok(pg.evaluate("U.bar") == n - 2 and pg.locator('#pickLine').count() == 1, 'closing the calendar comes back to the same picked day')

    # ── 3 · Tapping a purchase keeps the pick ────────────────────
    pg.click('#spendList [data-a=openPurchase][data-k=a2]')
    pg.wait_for_function("U.sheet==='purchase'")
    ok(pg.evaluate("U.bar") == n - 2, 'tapping a purchase in the narrowed list keeps the pick')
    close_sheet(pg)
    ok(pg.evaluate("U.bar") == n - 2 and sorted(rows(pg)) == ['a2', 'a3'], 'closing its details with ✕ keeps the pick and the narrowed list')
    pg.click('#spendList [data-a=openPurchase][data-k=a3]')
    pg.wait_for_function("U.sheet==='purchase'")
    pg.mouse.click(20, 40)
    pg.wait_for_function("U.sheet===null")
    ok(pg.evaluate("U.bar") == n - 2 and pg.locator('#pickLine').count() == 1, 'so does tapping outside the sheet to close it')

    # typing in the filter narrows within the picked day
    pg.fill('#filter', 'jeep')
    pg.wait_for_function("U.filter==='jeep'")
    ok(rows(pg) == ['a2'] and pg.evaluate("U.bar") == n - 2, 'the filter narrows within the picked day')
    pg.click('#app .searchbox .clr')
    pg.wait_for_function("U.filter===''")
    ok(pg.evaluate("U.bar") is None and len(rows(pg)) == 4, 'the filter’s ✕ works first time with a day picked (the list widens after the tap)')

    # buttons under the narrowed list don't jump away from the tap: Export as CSV still exports
    tap_bar(pg, n - 2)
    pg.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
    with pg.expect_download() as dl:
        pg.click('[data-a=csv]')
    csv = open(dl.value.path(), encoding='utf-8-sig').read()
    ok(len(csv.strip().splitlines()) == 5, 'Export as CSV, tapped with a day picked, exports the whole period it then shows')
    pg.wait_for_function("!document.getElementById('pickLine')")
    tap_bar(pg, n - 2)

    # tapping anywhere else clears it, as before
    pg.click('#app h1')
    pg.wait_for_function("U.bar===null&&!document.getElementById('pickLine')")
    ok(len(rows(pg)) == 4 and pg.locator('#pickLine').count() == 0 and pg.inner_text('#spendSum .plabel').startswith('Since'),
       'tapping elsewhere clears the pick: the whole list and period are back')

    # the line's own button
    tap_bar(pg, n - 1)
    ok(rows(pg) == ['a1'] and pg.inner_text('#pickLine span') == 'Showing Today only', 'today’s bar shows only today')
    pg.click('#pickLine .tbtn')
    pg.wait_for_function("U.bar===null")
    ok(len(rows(pg)) == 4 and pg.locator('#pickLine').count() == 0, '“Show all since …” brings the whole list back')

    # a day with nothing on it
    tap_bar(pg, 1)
    ok('Nothing spent on this day.' in pg.inner_text('#spendList') and pg.locator('#pickLine').count() == 1, 'an empty day says “Nothing spent on this day.” under the line')
    pg.click('#app h1')
    pg.wait_for_function("U.bar===null")

    # the way back names the period
    set_range(pg, 'week')
    ti = pg.evaluate("buckets(spendingList(),period()).findIndex(b=>b.from===localISO())")
    tap_bar(pg, ti)
    ok(pg.inner_text('#pickLine .tbtn') == 'Show this week', 'on W the way back reads “Show this week”')
    set_range(pg, 'week', 1)
    tap_bar(pg, 0)
    ok(pg.inner_text('#pickLine .tbtn') == 'Show last week', 'and “Show last week” a week back')
    set_range(pg, 'month')
    tap_bar(pg, today.day - 1)
    mon = pg.evaluate("monthName(period().from)")
    ok(pg.inner_text('#pickLine .tbtn') == 'Show all of ' + mon and mon[0].isupper(), f'on M it reads “Show all of {mon}”, with the month’s capital kept')
    t.shot(pg, 'picked-light')
    pg.evaluate("document.getElementById('pickLine').scrollIntoView({block:'center'})")
    t.shot(pg, 'picked-list-light')
    ok(pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'no sideways scroll at 375 px with a bar picked')

    # weekly bars (All over more than two months): the line and the door speak in weeks
    pg.evaluate(f"D.purchases.push({{id:'old',item:'Hostel',price:800,date:'{(today - dt.timedelta(days=100)).isoformat()}',category:'Accommodation',location:'',venue:'',payment:'Cash',notes:''}})")
    set_range(pg, 'all')
    ok(pg.evaluate("buckets(spendingList(),period()).weekly") is True, 'All over 100 days shows a bar a week')
    tap_bar(pg, 0)
    wk = pg.evaluate("buckets(spendingList(),period())[0].from")
    ok(pg.inner_text('#pickLine span') == 'Showing the week of ' + pg.evaluate(f"shortDate('{wk}')") + ' only' and rows(pg) == ['old'],
       'a picked week reads “Showing the week of … only” and lists that week')
    ok(open_cal(pg) == [wk[:8] + '01', None], 'the label opens on that week’s month, with no day picked')
    close_sheet(pg)
    pg.evaluate("D.purchases=D.purchases.filter(p=>p.id!=='old');U.bar=null;rerender()")

    # ── 4 · Help lists the calendar's doors ──────────────────────
    pg.evaluate("go('settings')")
    pg.wait_for_function("U.tab==='settings'")
    pg.click('[data-a=openHelp]')
    pg.wait_for_function("U.tab==='help'")
    txt = pg.inner_text('#app')
    ok('Tap Home’s title' in txt and 'To open the calendar (Spending’s date does too)' in txt, 'Help › Hidden gestures lists “Tap Home’s title”')
    pg.context.close()

    # ── iPad: the details pane beside the list keeps the pick ────
    pi = t.page(b, w=1180, h=820, ua=None, data=sample())
    pi.evaluate("go('spending')")
    pi.wait_for_function("U.tab==='spending'&&!!document.getElementById('chart')")
    m = pi.locator('#chart .col').count()
    tap_bar(pi, m - 2)
    pi.click('#app .sl [data-a=openPurchase][data-k=a2]')
    pi.wait_for_function("U.sel==='a2'")
    ok(pi.evaluate("U.bar") == m - 2 and pi.locator('#pickLine').count() == 1, 'on iPad, picking a purchase in the narrowed list keeps the pick')
    pi.click('#app .pane .dprice')
    ok(pi.evaluate("U.bar") == m - 2, 'and tapping in its details beside the list keeps it too')
    pi.click('#spendBrk .hdr h2')
    pi.wait_for_function("U.bar===null&&!document.getElementById('pickLine')")
    ok(pi.locator('#pickLine').count() == 0, 'tapping elsewhere in the list’s column clears it')
    pi.context.close()

    # ── Dark ─────────────────────────────────────────────────────
    pd = t.page(b, w=375, h=812, sc='dark', data=sample())
    tab(pd, 'spending')
    tap_bar(pd, pd.locator('#chart .col').count() - 2)
    t.shot(pd, 'picked-dark')
    pd.evaluate("document.getElementById('pickLine').scrollIntoView({block:'center'})")
    t.shot(pd, 'picked-list-dark')
    ok(pd.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'no sideways scroll at 375 px in dark')
    pd.context.close()
