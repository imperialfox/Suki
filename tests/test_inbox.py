"""The Siri inbox (Q15): the reader keeping the Shortcut's stamp as saidAt; a stamped inbox saving once; pasting it
again marking every line "Already saved" (greyed, left out of Save, with Clear the box); a mix saving only the new
lines, with the "N new · M already saved" header and Undo for just those; lines without a stamp never skipped; the
same words with another stamp counting as new; saidAt kept through Edit, the check sheet and Edit in the form;
saidAt through a backup round trip, junk stamps dropped and older data left as it was; Help › Log by voice with Siri
listing the six Shortcut steps, how to run it, that clearing the note is optional, and its door to Smart add;
screenshots at 375 px, light and dark. Every line here is made up."""
import os, json, tempfile, datetime as dt
from harness import sample, READ, BAD_TEXT

today = dt.date.today()
iso = lambda n=0: (today - dt.timedelta(days=n)).isoformat()
y = iso(1)
INBOX = f"[{y} 08:10] jeepney 14\n[{y} 12:30] halo-halo 120 at Chowking\n[{y} 18:45] tricycle 50 pesos from Bulakan to Barrio"
MORE = f"\n[{iso(0)} 07:55] taho 25\n[{iso(0)} 09:02] water 25 and banana cue 20"


def typed(pg, text):
    pg.fill('#smartText', text)
    pg.wait_for_timeout(40)


def mine(pg):
    return pg.evaluate("D.purchases.filter(p=>p.saidAt).map(p=>[p.item,p.price,p.saidAt,p.said])")


def run(b, t):
    ok = t.ok

    # ── the reader keeps the stamp ───────────────────────────────
    pg = t.page(b, w=375)
    pg.evaluate("switchSide('smart')"); pg.wait_for_timeout(40)
    r = pg.evaluate("READER.read('[2026-11-21 13:05] tricycle 50 pesos',new Date(2026,10,22,9,0),{},0)")
    ok(len(r) == 1 and r[0].get('saidAt') == '2026-11-21 13:05' and r[0]['said'] == 'tricycle 50 pesos', 'a stamped line keeps its stamp as saidAt, and his words without it')
    ok(r[0]['date'] == '2026-11-21', 'and still counts the day from the stamp')
    r = pg.evaluate("READER.read('tricycle 50 pesos',new Date(2026,10,22,9,0),{},0)")
    ok('saidAt' not in r[0], 'a line without a stamp has no saidAt')
    r = pg.evaluate("READER.read('[2026-02-30 13:05] jeep 14\\n[2026-11-21 25:61] jeep 14',new Date(2026,10,22,9,0),{},0)")
    ok(all('saidAt' not in p for p in r), 'an impossible stamp (30 Feb, 25:61) isn’t kept')
    r = pg.evaluate("READER.read('[2026-11-21 13:05] water 25 and banana cue 20',new Date(2026,10,22,9,0),{},0)")
    ok(len(r) == 2 and all(p.get('saidAt') == '2026-11-21 13:05' for p in r) and [p['said'] for p in r] == ['water 25', 'banana cue 20'], 'each purchase of a stamped line gets the stamp and its own words')
    ok(pg.evaluate("READER.sameKey({said:'Jeepney  14',saidAt:'2026-11-21 13:05'})===READER.sameKey({said:'jeepney 14',saidAt:'2026-11-21 13:05'})"), 'matching ignores case and spacing')
    ok(pg.evaluate("READER.sameKey({said:'jeepney 14'})") == '', 'a purchase with no stamp never matches')

    # ── a stamped inbox saves once ───────────────────────────────
    n0 = pg.evaluate("D.purchases.length")
    typed(pg, INBOX)
    out = pg.inner_text('#smartOut')
    ok('3 purchases found' in out.lower() and 'Save 3 purchases' in out and 'already' not in out.lower(), 'a fresh inbox shows three purchases, nothing already saved')
    pg.click('#smartSave'); pg.wait_for_timeout(150)
    saved = mine(pg)
    ok(pg.evaluate("D.purchases.length") == n0 + 3 and len(saved) == 3, 'saving adds the three')
    ok(sorted(s[2] for s in saved) == [f'{y} 08:10', f'{y} 12:30', f'{y} 18:45'], 'each keeps its stamp')
    pg.wait_for_timeout(100)
    ok(sum(1 for p in pg.evaluate(READ, 'purchases') if p.get('saidAt')) == 3, 'and that’s saved on the phone')

    # ── pasting it again: every line already saved ───────────────
    typed(pg, INBOX)
    out = pg.inner_text('#smartOut')
    ok('all 3 already saved' in out.lower(), 'pasting it again says all three are already saved')
    ok(pg.locator('#smartOut .row.done').count() == 3 and pg.locator('#smartOut [data-a=smartCheck]').count() == 0, 'each line is greyed and isn’t a button')
    ok(out.count('Already saved') >= 3 and pg.locator('#smartSave').count() == 0, 'each says Already saved, and there’s no Save button')
    ok('nothing new to save' in out and pg.locator('#smartOut [data-a=smartClear]').count() == 1, 'it says there’s nothing new, with Clear the box')
    lbl = pg.get_attribute('#smartOut .row.done >> nth=0', 'aria-label')
    ok(lbl and 'already saved' in lbl, f'VoiceOver hears that it’s already saved ({lbl})')
    ok(pg.evaluate("D.purchases.length") == n0 + 3, 'nothing was added')
    t.shot(pg, 'all-saved-375-light')
    pg.click('#smartOut [data-a=smartClear]'); pg.wait_for_timeout(60)
    ok(pg.input_value('#smartText') == '' and pg.evaluate("localStorage.getItem('suki:smart')") is None and 'already' not in pg.inner_text('#smartOut').lower(), 'Clear the box empties it')

    # ── a mix: only the new lines save ───────────────────────────
    typed(pg, INBOX + MORE)
    out = pg.inner_text('#smartOut')
    head = pg.inner_text('#smartHead')
    ok(head.replace('\n', ' ').lower() == '3 new · 3 already saved', f'the header reads “3 new · 3 already saved” ({head!r})')
    ok('Save 3 purchases' in out and pg.locator('#smartOut [data-a=smartCheck]').count() == 3 and pg.locator('#smartOut .row.done').count() == 3, 'Save counts only the new ones, which stay tappable')
    ok('Edit in the form' not in out, 'no Edit in the form for a list')
    t.shot(pg, 'mix-375-light')
    # check one of the new ones in the Log sheet: its stamp stays with it
    pg.click('#smartOut [data-a=smartCheck] >> nth=0'); pg.wait_for_timeout(80)
    ok(pg.evaluate("U.sheet") == 'edit' and pg.evaluate("F.edit.saidAt") == f'{iso(0)} 07:55', 'checking a new one keeps its stamp')
    pg.fill('#edit-price', '30'); pg.click('.sheet .cta'); pg.wait_for_timeout(100)
    pg.click('#smartSave'); pg.wait_for_timeout(150)
    ok(pg.evaluate("D.purchases.length") == n0 + 6, 'saving adds only the three new ones')
    taho = pg.evaluate("D.purchases.find(p=>p.said==='taho 25')")
    ok(taho and taho['price'] == 30 and taho.get('saidAt') == f'{iso(0)} 07:55', 'the checked one saved with its change and its stamp')
    ok(pg.evaluate("D.purchases.filter(p=>p.said==='jeepney 14').length") == 1, 'the old lines weren’t saved again')
    # Undo takes away only the new three
    pg.click('.toast:not(.sticky) button'); pg.wait_for_timeout(150)
    ok(pg.evaluate("D.purchases.length") == n0 + 3 and pg.evaluate("D.purchases.filter(p=>p.saidAt).length") == 3, 'Undo removes just the three new ones')
    typed(pg, INBOX + MORE)
    ok(pg.inner_text('#smartHead').lower() == '3 new · 3 already saved', 'and after Undo they count as new again')
    pg.click('#smartSave'); pg.wait_for_timeout(150)
    typed(pg, INBOX + MORE)
    ok('all 6 already saved' in pg.inner_text('#smartOut').lower(), 'the whole inbox pasted again: all six already saved')

    # ── the same words with another stamp are new; lines without a stamp are never skipped ──
    typed(pg, f'[{iso(0)} 10:40] jeepney 14')
    ok(pg.inner_text('#smartHead').lower() == 'suki read' and pg.locator('#smartSave').count() == 1 and 'Edit in the form' in pg.inner_text('#smartOut'), 'the same words said at another time are a new purchase')
    n1 = pg.evaluate("D.purchases.length")
    typed(pg, 'jeep 14'); pg.click('#smartSave'); pg.wait_for_timeout(150)
    typed(pg, 'jeep 14')
    ok(pg.inner_text('#smartHead').lower() == 'suki read' and 'already' not in pg.inner_text('#smartOut').lower(), 'typing “jeep 14” again isn’t marked already saved')
    pg.click('#smartSave'); pg.wait_for_timeout(150)
    ok(pg.evaluate("D.purchases.length") == n1 + 2, 'so it saves twice')

    # ── one stamped line already saved ───────────────────────────
    typed(pg, f'[{y} 08:10] jeepney 14')
    out = pg.inner_text('#smartOut')
    ok(pg.inner_text('#smartHead').lower() == 'already saved' and pg.locator('#smartSave').count() == 0 and 'Edit in the form' not in out and 'This is already in your purchases' in out, 'one line already saved says so, with nothing to save')
    ok(pg.evaluate(BAD_TEXT) == '', 'no undefined, NaN or null on screen')
    pg.click('#smartOut [data-a=smartClear]'); pg.wait_for_timeout(60)

    # ── Edit in the form, and editing a saved purchase, keep the stamp ──
    typed(pg, f'[{iso(0)} 11:11] buko juice 40')
    pg.click('#smartOut [data-a=smartToForm]'); pg.wait_for_timeout(120)
    ok(pg.evaluate("F.home.saidAt") == f'{iso(0)} 11:11', 'Edit in the form carries the stamp to the form')
    pg.reload(); pg.wait_for_function("!document.getElementById('splash')&&typeof U!=='undefined'"); pg.wait_for_timeout(100)
    ok(pg.evaluate("F.home.saidAt") == f'{iso(0)} 11:11', 'and the draft keeps it after reopening')
    pg.click('#homeSave'); pg.wait_for_timeout(150)
    buko = pg.evaluate("D.purchases.find(p=>p.said==='buko juice 40')")
    ok(buko and buko.get('saidAt') == f'{iso(0)} 11:11', 'saved from the form, it keeps the stamp')
    pg.evaluate("p=>{U.sel=p;openSheet('purchase',{id:p})}", buko['id']); pg.wait_for_timeout(80)
    pg.evaluate("p=>ACT.editPurchase({dataset:{k:p}})", buko['id']); pg.wait_for_timeout(80)
    pg.fill('#edit-price', '45'); pg.click('.sheet .cta'); pg.wait_for_timeout(150)
    buko = pg.evaluate("D.purchases.find(p=>p.said==='buko juice 40')")
    ok(buko['price'] == 45 and buko.get('saidAt') == f'{iso(0)} 11:11', 'editing it keeps the stamp')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(80)
    pg.evaluate("switchSide('smart')"); pg.wait_for_timeout(60)
    typed(pg, f'[{iso(0)} 11:11] buko juice 40')
    ok(pg.inner_text('#smartHead').lower() == 'already saved', 'so its line still counts as saved')
    pg.click('#smartOut [data-a=smartClear]'); pg.wait_for_timeout(60)

    # ── backups ──────────────────────────────────────────────────
    pg.click('#barR [data-v=settings]'); pg.wait_for_timeout(60)
    pg.click('[data-a=exportBackup]'); pg.wait_for_timeout(450)
    with pg.expect_download() as dl:
        pg.click('.sheet .cta')
    data = json.load(open(dl.value.path(), encoding='utf-8'))
    stamped = [p for p in data['purchases'] if p.get('saidAt')]
    ok(len(stamped) == 7, f'a backup holds every stamp ({len(stamped)})')
    pg.click('[data-a=erase]'); pg.wait_for_timeout(80)
    pg.click('.sheet [data-a=eraseYes]'); pg.wait_for_timeout(150)
    tmp = tempfile.mkdtemp(); f = os.path.join(tmp, 'b.json'); json.dump(data, open(f, 'w'))
    pg.set_input_files('#importIn', f); pg.wait_for_timeout(300)
    pg.click('.sheet [data-a=restoreYes]'); pg.wait_for_timeout(200)
    ok(pg.evaluate("D.purchases.filter(p=>p.saidAt).length") == 7, 'restoring brings the stamps back')
    pg.click('#barL [data-v=home], .tabbar [data-v=home] >> nth=0'); pg.wait_for_timeout(80)
    pg.evaluate("switchSide('smart')"); pg.wait_for_timeout(60)
    typed(pg, INBOX + MORE)
    ok('all 6 already saved' in pg.inner_text('#smartOut').lower(), 'and after restoring, the inbox still counts as saved')
    pg.click('#smartOut [data-a=smartClear]'); pg.wait_for_timeout(60)
    # junk stamps are dropped, other fields kept; older purchases without one stay as they were
    junk = sample()
    junk['purchases'][0]['saidAt'] = 'yesterday'
    junk['purchases'][1]['saidAt'] = '2026-11-21 13:05'
    junk['purchases'][1]['said'] = 'jeepney 13'
    f2 = os.path.join(tmp, 'junk.json'); json.dump(dict(junk, app='Suki'), open(f2, 'w'))
    pg.click('#barR [data-v=settings]'); pg.wait_for_timeout(60)
    pg.set_input_files('#importIn', f2); pg.wait_for_timeout(300)
    pg.click('.sheet [data-a=restoreYes]'); pg.wait_for_timeout(200)
    got = pg.evaluate("D.purchases.map(p=>[p.id,'saidAt' in p?p.saidAt:'-'])")
    ok(dict(got) == {'a1': '-', 'a2': '2026-11-21 13:05', 'a3': '-', 'a4': '-'}, f'a junk stamp is dropped, a good one kept, older purchases unchanged ({got})')
    ok(pg.evaluate("D.purchases.length") == 4, 'and no purchase is lost over it')

    # ── Help › Log by voice with Siri ────────────────────────────
    pg.evaluate("go('settings')"); pg.wait_for_timeout(40)
    pg.evaluate("go('help')"); pg.wait_for_timeout(80)
    row = pg.locator('#app [data-a=openSiri]')
    ok(row.count() == 1 and 'Log by voice with Siri' in row.inner_text(), 'Help has Log by voice with Siri')
    row.click(); pg.wait_for_timeout(100)
    txt = pg.inner_text('.sheet')
    ok(pg.evaluate("U.sheet") == 'siri' and 'Log by voice with Siri' in pg.inner_text('.sheet h2'), 'it opens its own sheet')
    steps = pg.locator('#siriSteps .row').all_inner_texts()
    names = ['Dictate Text', 'Format Date', 'Text', 'Append to Note', 'Copy to Clipboard', 'Show Notification']
    ok(len(steps) == 6 and all(s.startswith(f'{i + 1}. {n}') for i, (s, n) in enumerate(zip(steps, names))), f'the six Shortcut steps, in order ({[s.split(chr(10))[0] for s in steps]})')
    ok('yyyy-MM-dd HH:mm' in txt and 'Suki inbox' in txt and 'English (UK)' in txt, 'with the date format, the note’s name and the language')
    ok('Hey Siri, Log to Suki' in txt and 'Action Button' in txt and 'Lock Screen' in txt, 'how to run it: Siri, the Action Button and the Lock Screen')
    ok('Clearing the note is optional' in txt and 'Already saved' in txt, 'that clearing the note is optional, and lines already saved aren’t saved again')
    ok(pg.evaluate("document.querySelector('.sheet').scrollWidth<=document.querySelector('.sheet').clientWidth+1") and pg.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'nothing runs off the side at 375 px')
    ok(pg.evaluate(BAD_TEXT) == '', 'no undefined, NaN or null on screen')
    t.shot(pg, 'help-siri-375-light', full_page=False)
    pg.click('.sheet [data-a=goSmart]'); pg.wait_for_timeout(120)
    ok(pg.evaluate("U.sheet") is None and pg.evaluate("U.tab") == 'home' and pg.locator('#smartText').count() == 1, '“Smart add” in the steps opens Home on Smart add')
    ok(pg.evaluate("document.activeElement.id") == 'smartText', 'with the box ready to paste into')
    pg.evaluate("switchSide('form')"); pg.wait_for_timeout(40)
    pg.evaluate("go('help')"); pg.wait_for_timeout(40)
    pg.click('#app [data-a=openSiri]'); pg.wait_for_timeout(80)
    pg.click('.sheet [data-a=goSmart]'); pg.wait_for_timeout(120)
    ok(pg.locator('#smartText').count() == 1 and pg.evaluate("localStorage.getItem('suki:logSide')") == 'smart', 'and switches Home to Smart add when it was on the form')
    pg.context.close()

    # ── dark mode at 375 px ──────────────────────────────────────
    pg = t.page(b, w=375, sc='dark')
    pg.evaluate("switchSide('smart')"); pg.wait_for_timeout(40)
    typed(pg, INBOX); pg.click('#smartSave'); pg.wait_for_timeout(150)
    typed(pg, INBOX + MORE)
    ok(pg.inner_text('#smartHead').lower() == '3 new · 3 already saved', 'dark mode: the same header')
    t.shot(pg, 'mix-375-dark')
    pg.evaluate("go('help')"); pg.wait_for_timeout(40)
    pg.click('#app [data-a=openSiri]'); pg.wait_for_timeout(100)
    t.shot(pg, 'help-siri-375-dark')
    ok(pg.evaluate(BAD_TEXT) == '', 'dark mode: no undefined, NaN or null on screen')
    pg.context.close()
