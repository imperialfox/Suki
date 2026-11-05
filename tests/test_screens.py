"""2.29 Screen IDs (Q25): the register (js/register.js) against the code, every screen's and sheet's ID on the page,
part names (every visible control named, by Vocal Sessions' naming rules), the flows walked by their part names, docs
links, the Show screen IDs switch and label, the changelog's Screens line, and the saved-data list
(MAINTAINING › Where data lives) against every storage key in the code."""
import os, re
import harness


def until(pg, js, timeout=5000):
    """Wait for a condition; True if it came true."""
    try:
        pg.wait_for_function(js, timeout=timeout)
        return True
    except Exception:
        return False

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PART_RE = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
KINDS = {'Tab', 'Screen', 'Sheet', 'Alert', 'Overlay'}
# rule 2: every name ends in a kind word. Vocal Sessions' list, plus Suki's own: banner (Home's notices), chart,
# drawer (the till drawer), layer (a sheet's dim)
KIND_WORDS = ('button', 'row', 'switch', 'picker', 'field', 'slider', 'stepper', 'tile', 'card', 'tab', 'pill', 'chip', 'menu',
              'line', 'bar', 'link', 'option', 'item', 'word', 'dot', 'grabber', 'banner', 'chart', 'drawer', 'layer')
# actions in ACT that no button carries, each with why
NOT_BUTTONS = {}
REG = "JSON.parse(JSON.stringify(REGISTER))"
HERE = "()=>[document.getElementById('app').dataset.screen,SCR.viewKey()]"
SHEET = "()=>{const s=SCR.top();return s?[s.dataset.screen||'',(document.getElementById('scrid')||{}).textContent||'']:null}"
INTERACTIVE = "button,[data-a],input,select,textarea,a[href],[role=switch]"
UNNAMED_JS = """o=>{const out=[],dup={};const re=/^[a-z0-9]+(-[a-z0-9]+)*$/;
 for(const r of o.roots.map(x=>document.querySelector(x)).filter(Boolean))for(const e of r.querySelectorAll(o.sel)){
  const b=e.getBoundingClientRect();if(!b.width||!b.height||e.disabled||e.closest('[aria-hidden=true]')||e.closest('.scrim')&&r.id==='app')continue;
  if(e.type==='hidden'||e.type==='file')continue;
  const n=e.dataset.name||'';
  if(!re.test(n)){out.push((e.dataset.a||e.id||e.className||e.tagName.toLowerCase())+(e.dataset.v?'='+e.dataset.v:'')+' “'+(e.getAttribute('aria-label')||e.innerText||'').trim().slice(0,24)+'”');continue}
  (dup[n]=dup[n]||new Set()).add(e.dataset.a||e.id||e.className)}
 return {unnamed:out,dup:Object.entries(dup).filter(([n,s])=>s.size>1&&!o.roles.includes(n)).map(([n,s])=>n+' ('+[...s].join(', ')+')')}}"""
# standard roles (rule 6) may be different actions on one screen
ROLES = ['back-button', 'close-button', 'cancel-button', 'confirm-button', 'done-button', 'save-button', 'clear-button', 'show-all-button']


def src_all():
    out = ''
    for f in sorted(os.listdir(os.path.join(ROOT, 'js'))):
        # the parts kit and its settings are the kit's own (its parts carry the kit's plain names until Suki's)
        if f.endswith('.js') and f not in ('register.js', 'parts-kit.js', 'parts.settings.js'): out += open(os.path.join(ROOT, 'js', f), encoding='utf-8').read() + '\n'
    return out


def slug(h):
    """A heading's anchor as GitHub writes it."""
    return re.sub(r'[^\w\- ]', '', h.strip().lower()).replace(' ', '-')


def headings():
    out = set()
    for f in ('README.md', 'MAINTAINING.md'):
        for l in open(os.path.join(ROOT, f), encoding='utf-8'):
            m = re.match(r'^#{1,6} (.+)$', l)
            if m: out.add(f + '#' + slug(m.group(1)))
    return out


def code_keys(src):
    """Every screen the code can show, as a code key."""
    keys = set()
    m = re.search(r'const SCREENS = \{([^}]*)\}', src)
    keys |= {'tab:' + k for k in re.findall(r'(\w+):', m.group(1))}
    keys |= {'tab:' + k for k in re.findall(r'^SCREENS\.(\w+) = ', src, re.M)}
    body = src[src.index('function sheetHTML()'):src.index('function renderSheet()')]
    keys |= {'sheet:' + k for k in re.findall(r"case '(\w+)':", body) if k != 'confirm'}
    keys |= {'sheet:confirm/' + a for a in re.findall(r"openSheet\(\s*'confirm',\s*\{[^}]*?action: '(\w+)'", src)}
    keys |= set(re.findall(r"'(overlay:\w+)'", src))
    return keys


# the U values (and the call) that show a sheet from the sample data
SHEETS = {
    'sheet:purchase': "openSheet('purchase',{id:'a1'})",
    'sheet:edit': "openSheet('edit',{})",
    'sheet:item': "openSheet('item',{id:'bigas'})",
    'sheet:notes': "openSheet('notes')",
    'sheet:confirm/delPurchaseYes': "ACT.delPurchase({dataset:{k:'a1'}})",
    'sheet:confirm/delObsYes': "ACT.delObs({dataset:{k:'o1'}})",
    'sheet:erase': "openSheet('erase')",
    'sheet:backup': "openSheet('backup',{})",
    'sheet:restore': "openSheet('restore',{data:{purchases:[],observations:[],rate:null,learned:[]},when:'today'})",
    'sheet:calendar': "(U.calD=localISO(),openSheet('calendar'))",
    'sheet:access': "openSheet('access')",
    'sheet:rescue': "openSheet('rescue')",
    'sheet:putback': "(SAFETY={data:{purchases:[],observations:[]},at:Date.now(),why:'erase'},openSheet('putback'))",
    'sheet:confirm/clearRescueYes': "ACT.clearRescue()",
    'sheet:ahs': "openSheet('ahs',{})",
    'sheet:welcome': "openSheet('welcome')",
    'sheet:learned': "openSheet('learned',{})",
    'sheet:siri': "openSheet('siri',{})",
    'sheet:news': "(go('history'),openSheet('news',{id:newsKey(hNotes()[hNotes().length-1])}))",
    'sheet:cbrate': "openSheet('cbrate',{})",
}
CLEAR = "(()=>{U.stack=[];U.sheet=null;U.sd={};U.calD=null;render()})()"


def register(b, t):
    ok = t.ok
    pg = t.page(b)
    R = pg.evaluate(REG)
    S = R['screens']
    ids = [s['id'] for s in S]
    ok(ids == ['SK-%03d' % (i + 1) for i in range(len(S))], f'{len(S)} screens numbered SK-001 to SK-{len(S):03d} in order, none skipped or used twice')
    ok(len({s['key'] for s in S}) == len(S), 'every code key is in the register once')
    ok(all(s['kind'] in KINDS and s['name'] and s['area'] and isinstance(s['aliases'], list) and (s['status'] == 'Live' or re.fullmatch(r'Retired in \d+\.\d+(\.\d+)?', s['status'])) for s in S),
       'each has a name, an area, a kind, aliases and a status (Live, or Retired in a version)')
    allp = [('shared', p) for p in R['shared']] + [('actions', p) for p in R['actions']] + [(s['id'], p) for s in S for p in s['parts']]
    bad = [w + ' › ' + p['name'] for w, p in allp if not (PART_RE.match(p['name']) and p.get('sel') and any(p['name'] == k or p['name'].endswith('-' + k) for k in KIND_WORDS))]
    ok(not bad, f'every part name is lower case with hyphens, ends in a kind word and says where it is ({bad})')
    dup = [s['id'] for s in S if len({p['name'] for p in s['parts']}) != len(s['parts'])]
    ok(not dup, f'no screen names two of its own parts the same ({dup})')
    pos = [w + ' › ' + p['name'] for w, p in allp if re.search(r':nth-|:first-child|:last-child|:first-of-type|:last-of-type', p['sel'])]
    ok(not pos, f'no part is found by its position ({pos})')
    acts = [re.match(r'^\[data-a="([^"]+)"\](?:\[data-v="([^"]+)"\])?$', p['sel']) for p in R['actions']]
    ok(all(acts) and len({m.group(0) for m in acts}) == len(acts), 'every action line is one data-a (and data-v), each once')

    # against the code
    src = src_all()
    have = code_keys(src)
    keys = {s['key'] for s in S}
    missing = sorted(have - keys)
    ok(not missing and len(have) >= 30, f'every screen, sheet and overlay the code can show ({len(have)} found) has a register entry ({missing})')
    gone = sorted(s['id'] + ' ' + s['key'] for s in S if s['status'] == 'Live' and s['key'] not in have)
    ok(not gone, f'every Live entry’s code key is still in the code ({gone})')
    nodoc = [s['id'] + ' ' + s['docs'] for s in S if s['docs'] not in headings()]
    ok(not nodoc, f'every docs link points at a real heading in README.md or MAINTAINING.md ({nodoc})')
    # every part's action or id is still in the code
    html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    kit = open(os.path.join(ROOT, 'js', 'parts-kit.js'), encoding='utf-8').read()  # the kit's alert buttons (yes, no)
    nopart = []
    for w, p in allp:
        for a in re.findall(r'data-a="([A-Za-z]+)"', p['sel']):
            if not re.search(r'data-a=\\?"' + a + r'\\?"|\'' + a + r"'|\b" + a + r':', src + kit): nopart.append(w + ' › ' + p['name'])
        for i in re.findall(r'#([A-Za-z][\w-]*)', p['sel']):
            if i not in ('dock', 'barL', 'barR', 'barT', 'side', 'app') and not re.search(r'id=\\?"' + i + r'|\.id = \'' + i + "'|id=\"' \+ \w+ \+ '-|'" + i + "'", src + html):
                if not (i.startswith('conv-') and "'conv-' + c" in src) and not (i.startswith('till-') and "data-till" in src): nopart.append(w + ' › ' + p['name'] + ' #' + i)
    ok(not nopart, f'every named part’s action or id is still in the code ({nopart})')
    # every button in the code has a name
    used = set(re.findall(r'data-a=\\?"([A-Za-z]\w*)\\?"', src + html))
    used |= set(pg.evaluate("Object.keys(ACT)"))
    named = set(re.findall(r'data-a="([^"]+)"', ' '.join(p['sel'] for _, p in allp)))
    miss = sorted(a for a in used if a not in named and a not in NOT_BUTTONS and a not in ('tab',))
    ok(not miss, f'every action in the code has a name ({len(used)} actions; missing: {miss})')
    tabs = {v for v in re.findall(r'data-v="(\w+)"', ' '.join(p['sel'] for p in R['shared'] if 'data-a="tab"' in p['sel']))}
    ok(tabs >= {'home', 'till', 'search', 'spending', 'convert', 'settings'}, f'every tab button is named, by the tab it opens ({sorted(tabs)})')

    # flows
    F = R['flows']
    ok([f['id'] for f in F] == ['F-%02d' % (i + 1) for i in range(len(F))] and len(F) >= 4, 'flows numbered F-01 onwards')
    ok([f['name'] for f in F[:4]] == ['Log a purchase on Home', 'Pay at the Till and log the bill', 'Look up a price and add a note', 'Check Spending for a day'],
       'the four flows: Log a purchase on Home, Pay at the Till and log the bill, Look up a price and add a note, Check Spending for a day')
    by = {s['id']: s for s in S}
    badst = [f['id'] + ': ' + st['screen'] for f in F for st in f['steps'] if st['screen'] not in by or by[st['screen']]['status'] != 'Live']
    ok(not badst and all(len(f['steps']) >= 3 for f in F), f'every flow step is a Live screen, at least three steps each ({badst})')
    pg.context.close()


def screens_on_page(b, t):
    ok = t.ok
    for sc in ('light', 'dark'):
        pg = t.page(b, sc=sc)
        S = pg.evaluate(REG)['screens']
        pg.evaluate("localStorage.setItem('suki:screenIds','on')")
        pg.reload(); harness.ready(pg)
        wrong, labels, unnamed, dups, parts = [], [], [], [], []
        for s in S:
            if s['kind'] not in ('Tab', 'Screen'): continue
            pg.evaluate(f"go('{s['key'][4:]}')"); pg.wait_for_timeout(60)
            got = pg.evaluate(HERE)
            if got != [s['id'], s['key']]: wrong.append(f"{s['id']} {s['key']} → {got}")
            lab = pg.evaluate("(document.getElementById('scrid')||{}).textContent")
            if lab != s['id']: labels.append(f"{s['id']}: {lab}")
            r = pg.evaluate(UNNAMED_JS, {'sel': INTERACTIVE, 'roles': ROLES, 'roots': ['#app', '#bar', '#dock', '#side']})
            unnamed += [s['id'] + ' ' + x for x in r['unnamed']]; dups += [s['id'] + ' ' + x for x in r['dup']]
            res = pg.evaluate("""s=>s.parts.map(p=>{const els=[...document.querySelectorAll('#app '+p.sel.split(',').join(',#app ')+',#bar '+p.sel.split(',').join(',#bar '))];
              return [p.name,els.length,els.every(e=>e.dataset.name===p.name)]})""", s)
            parts += [s['id'] + ' › ' + n for n, c, good in res if c and not good]
        ok(not wrong, f'{sc}: every tab and screen carries its ID as data-screen ({wrong})')
        ok(not labels, f'{sc}: with Show screen IDs on, the label shows the right ID on each ({labels})')
        ok(not unnamed, f'{sc}: every visible control on every tab and screen carries a name ({unnamed})')
        ok(not dups, f'{sc}: one name is one action on a screen, standard roles aside ({dups})')
        ok(not parts, f'{sc}: each screen’s own parts carry their own names ({parts})')
        if sc == 'light':
            pg.evaluate("go('home')"); pg.wait_for_timeout(60)
            want = ['total-card', 'today-card', 'rate-card', 'item-field', 'amount-field', 'save-button', 'purchase-row', 'show-all-button', 'calendar-button', 'settings-button', 'home-tab', 'till-tab']
            have = set(pg.evaluate("[...document.querySelectorAll('[data-name]')].map(e=>e.dataset.name)"))
            ok(all(w in have for w in want), f'Home’s main parts are named ({[w for w in want if w not in have]})')
        # sheets: each opens from the sample data and carries its own ID; the label shows the screen's then the sheet's
        bad, opened = [], 0
        for s in S:
            if s['kind'] not in ('Sheet', 'Alert'): continue
            pg.evaluate("go('home')")
            pg.evaluate(SHEETS[s['key']]); pg.wait_for_timeout(60)
            got = pg.evaluate(SHEET)
            base = pg.evaluate("document.getElementById('app').dataset.screen")
            if not got or got[0] != s['id'] or got[1] != base + ' · ' + s['id']: bad.append(f"{s['id']} {s['key']}: {got}")
            else:
                opened += 1
                r = pg.evaluate(UNNAMED_JS, {'sel': INTERACTIVE, 'roles': ROLES, 'roots': ['#layer']})
                unnamed_s = [s['id'] + ' ' + x for x in r['unnamed']]
                if unnamed_s: bad += unnamed_s
                if r['dup']: bad += [s['id'] + ' ' + x for x in r['dup']]
            pg.evaluate(CLEAR); pg.wait_for_timeout(30)
        nsheets = sum(1 for s in S if s['kind'] in ('Sheet', 'Alert'))
        ok(not bad and opened == nsheets, f'{sc}: all {opened} of {nsheets} sheets carry their own ID, the label shows both, and every control in them is named ({bad})')
        pg.evaluate("go('home')"); pg.evaluate("openSheet('purchase',{id:'a1'})"); pg.wait_for_timeout(80)
        t.shot(pg, 'label-' + sc)
        pg.context.close()


def ipad_and_mac(b, t):
    ok = t.ok
    for w, h, name in ((820, 1180, 'iPad'), (1440, 900, 'Mac')):
        pg = t.page(b, w=w, h=h)
        unnamed, wrong = [], []
        for tab in ('home', 'till', 'search', 'spending', 'convert', 'settings', 'help', 'history'):
            pg.evaluate(f"go('{tab}')"); pg.wait_for_timeout(60)
            if tab == 'spending': pg.evaluate("ACT.openPurchase({dataset:{k:'a1'}})"); pg.wait_for_timeout(60)
            if tab == 'search': pg.evaluate("(U.item='bigas',render())"); pg.wait_for_timeout(60)
            got = pg.evaluate(HERE)
            if got[1] != 'tab:' + tab or not re.fullmatch(r'SK-\d{3}', got[0]): wrong.append(f'{tab}: {got}')
            r = pg.evaluate(UNNAMED_JS, {'sel': INTERACTIVE, 'roles': ROLES, 'roots': ['#app', '#bar', '#dock', '#side']})
            unnamed += [tab + ' ' + x for x in r['unnamed']]
        ok(not wrong and not unnamed, f'{name}: every page carries its ID, and every control (the sidebar, top tabs and the details pane too) is named ({wrong} {unnamed})')
        pg.context.close()


def overlays(b, t):
    ok = t.ok
    pg = t.page(b)
    pg.evaluate("toast('Purchase deleted',()=>{})")
    ok(pg.evaluate("(()=>{const e=document.querySelector('.toast:not(.sticky)');return e&&e.dataset.screen==='SK-016'&&e.querySelector('[data-name=undo-button]')?1:0})()") == 1,
       'a toast is SK-016 · Toast, its Undo named undo-button')
    pg.evaluate("toast('Couldn’t save',null,true)")
    ok(pg.evaluate("(()=>{const e=document.querySelector('.toast.sticky');return e&&e.dataset.screen==='SK-016'&&e.querySelector('[data-name=ok-button]')?1:0})()") == 1,
       'the sticky warning is SK-016 too, its OK named ok-button')
    pg.evaluate("(()=>{document.querySelectorAll('.toast').forEach(e=>e.remove());go('till');OB.tips=true;showTip('till')})()"); pg.wait_for_timeout(60)
    ok(pg.evaluate("(()=>{const e=document.getElementById('tip');return e?[e.dataset.screen,(e.querySelector('[data-name=close-button]')||{}).dataset]:null})()") == ['SK-026', {'a': 'tipX', 'name': 'close-button'}],
       'a tip is SK-026 · Tip, its ✕ named close-button')
    pg.context.close()
    # the launch screen, read while it's still up (motion on, so it stays about half a second)
    ctx = b.new_context(viewport={'width': 390, 'height': 844})
    p2 = ctx.new_page()
    p2.goto(harness.url(), wait_until='domcontentloaded')
    v = p2.evaluate("(()=>{const s=document.getElementById('splash');return s?s.dataset.screen||'':'gone'})()")
    ok(v in ('SK-017', 'gone'), f'the launch screen is SK-017 · Launch screen ({v})')
    if v == 'gone': print('  note: the launch screen had already gone; checked only that nothing went wrong')
    ctx.close()


def flows(b, t):
    """Each flow walked by its part names, checking each step's screen ID (F-01 to F-04)."""
    ok = t.ok
    pg = t.page(b)
    n = lambda: pg.evaluate("D.purchases.length")
    at = lambda: pg.evaluate("[document.getElementById('app').dataset.screen,(SCR.top()||{dataset:{}}).dataset.screen||null]")
    # F-01 Log a purchase on Home
    before = n()
    ok(at() == ['SK-001', None], 'F-01: starts on SK-001 · Home')
    pg.fill('#app [data-name=item-field]', 'Halo-halo')
    pg.fill('#app [data-name=amount-field]', '120')
    pg.click('#app [data-name=save-button]')
    ok(until(pg, f"D.purchases.length==={before + 1}") and at() == ['SK-001', None], 'F-01: item-field, amount-field, save-button: saved, still on SK-001')
    # F-02 Pay at the Till and log the bill
    pg.click('#dock [data-name=till-tab]')
    ok(at() == ['SK-002', None], 'F-02: till-tab opens SK-002 · Quick Till')
    pg.fill('#app [data-name=bill-field]', '230')
    pg.click('#app [data-name=note-button][data-v="500"]')
    pg.click('#app [data-name=log-bill-button]')
    ok(until(pg, "!!document.querySelector('#layer .sheet[data-screen=\"SK-008\"]')"), 'F-02: bill-field, note-button, log-bill-button: SK-008 · Log or edit a purchase opens')
    before = n()
    pg.fill('#layer [data-name=item-field]', 'Sari-sari')
    pg.click('#layer [data-name=save-button]')
    ok(until(pg, f"D.purchases.length==={before + 1}&&!U.sheet") and at() == ['SK-002', None], 'F-02: save-button saves the bill, back on SK-002')
    # F-03 Look up a price and add a note
    pg.click('#dock [data-name=search-tab]')
    pg.fill('#app [data-name=search-field]', 'bigas')
    ok(until(pg, "!!document.querySelector('#app [data-name=item-row]')"), 'F-03: search-field on SK-003 · Search finds item rows')
    pg.click('#app [data-name=item-row] >> nth=0')
    ok(until(pg, "!!document.querySelector('#layer .sheet[data-screen=\"SK-009\"]')"), 'F-03: item-row opens SK-009 · Item')
    obs = pg.evaluate("D.observations.length")
    pg.click('#layer [data-name=add-note-button]')
    pg.fill('#layer [data-name=amount-field]', '55')
    pg.click('#layer [data-name=save-button]')
    ok(until(pg, f"D.observations.length==={obs + 1}") and at()[1] == 'SK-009', 'F-03: add-note-button, amount-field, save-button: the note is added, SK-009 still open')
    pg.evaluate(CLEAR)
    # F-04 Check Spending for a day
    pg.click('#dock [data-name=spending-tab]')
    pg.click('#app [data-name=period-button]')
    ok(until(pg, "!!document.querySelector('#layer .sheet[data-screen=\"SK-018\"]')"), 'F-04: period-button on SK-004 · Spending opens SK-018 · Calendar')
    pg.click(f"#layer [data-name=day-button][data-v=\"{harness.day(0)}\"]")
    ok(until(pg, "!!document.querySelector('#layer [data-name=purchase-row]')"), 'F-04: day-button picks the day, listing its purchase rows')
    pg.click('#layer [data-name=purchase-row] >> nth=0')
    ok(until(pg, "!!document.querySelector('#layer .sheet[data-screen=\"SK-007\"]')"), 'F-04: purchase-row opens SK-007 · Purchase')
    pg.context.close()


def missing_entry(b, t):
    ok = t.ok
    pg = t.page(b)
    warns = []
    pg.on('console', lambda m: warns.append(m.text) if m.type == 'warning' else None)
    pg.evaluate("(()=>{window.__keep=SCR.BY['tab:till'];delete SCR.BY['tab:till'];go('till')})()"); pg.wait_for_timeout(100)
    ok(pg.evaluate(HERE)[0] == 'SK-???', 'a screen missing from the register shows SK-???')
    ok(any('No screen ID' in w and 'tab:till' in w for w in warns), 'and warns in the console, naming its code key')
    pg.evaluate("(()=>{SCR.BY['tab:till']=window.__keep;go('home')})()")
    pg.context.close()


def switch(b, t):
    ok = t.ok
    for sc in ('light', 'dark'):
        pg = t.page(b, sc=sc)
        ok(pg.locator('#scrid').count() == 0 and pg.evaluate("localStorage.getItem('suki:screenIds')") is None, f'{sc}: no label until Show screen IDs is switched on')
        pg.evaluate("go('settings')"); pg.click('#app [data-name=accessibility-row]')
        sw = pg.locator('#layer [data-name=screen-ids-switch]')
        ok(sw.count() == 1 and not sw.is_checked() and sw.get_attribute('role') == 'switch' and 'Show screen IDs' in pg.inner_text('#layer'),
           f'{sc}: Settings › Accessibility has a Show screen IDs switch, off')
        pg.click('#layer label:has([data-name=screen-ids-switch])')
        ok(until(pg, "!!document.getElementById('scrid')") and pg.inner_text('#scrid') == 'SK-006 · SK-019',
           f'{sc}: switched on, the label shows Settings then the sheet, SK-006 · SK-019')
        ok(pg.evaluate("localStorage.getItem('suki:screenIds')") == 'on' and 'screenIds' not in pg.evaluate("backupJSON(new Date())"),
           f'{sc}: saved on this device only (suki:screenIds), not in a backup')
        st = pg.evaluate("""(()=>{const l=document.getElementById('scrid'),c=getComputedStyle(l),r=l.getBoundingClientRect();
          return {fs:parseFloat(c.fontSize),pe:c.pointerEvents,hidden:l.getAttribute('aria-hidden'),right:innerWidth-r.right,top:r.top}})()""")
        ok(st['fs'] <= 12 and st['pe'] == 'none' and st['hidden'] == 'true' and st['right'] < 20 and st['top'] < 120,
           f'{sc}: a small label in the top corner that taps go through, hidden from VoiceOver ({st})')
        pg.evaluate(CLEAR)
        for tab in ('home', 'till', 'search', 'spending', 'convert', 'settings', 'help', 'history'):
            pg.evaluate(f"go('{tab}')"); pg.wait_for_timeout(60)
            hit = pg.evaluate("""(()=>{const r=document.getElementById('scrid').getBoundingClientRect();
              return [...document.querySelectorAll('#bar button,#dock button')].filter(b=>{const q=b.getBoundingClientRect();
              return q.width&&r.left<q.right&&r.right>q.left&&r.top<q.bottom&&r.bottom>q.top}).map(b=>b.dataset.name)})()""")
            if hit: ok(False, f'{sc}: on {tab} the label covers {hit}')
        pg.evaluate("go('home')")
        if sc == 'light': t.shot(pg, 'home-ids')
        pg.reload(); harness.ready(pg)
        ok(pg.inner_text('#scrid') == 'SK-001', f'{sc}: still on after a reload, on SK-001 · Home')
        pg.evaluate("openSheet('access')"); pg.wait_for_timeout(60)
        pg.click('#layer label:has([data-name=screen-ids-switch])')
        ok(until(pg, "!document.getElementById('scrid')") and pg.evaluate("localStorage.getItem('suki:screenIds')") is None, f'{sc}: switched off, the label goes and the key is removed')
        pg.context.close()


def changelog(b, t):
    ok = t.ok
    top = open(os.path.join(ROOT, 'CHANGELOG.md'), encoding='utf-8').read().split('\n## ')[1]
    ok(re.search(r'^Screens: (none|SK-\d{3}(, SK-\d{3})*)$', top, re.M), 'the newest version has a Screens line')


def saved_data(b, t):
    ok = t.ok
    m = open(os.path.join(ROOT, 'MAINTAINING.md'), encoding='utf-8').read()
    sec = m[m.index('\n## Where data lives'):m.index('\n## Keeping data safe')]
    src = src_all()
    keys = sorted(set(re.findall(r"'(suki:[a-zA-Z]+)'", src)))
    miss = [k for k in keys if '`' + k + '`' not in sec]
    ok(len(keys) >= 9 and not miss, f'every suki: storage key in the code ({len(keys)}) is in MAINTAINING › Where data lives ({miss})')
    row = next((l for l in sec.splitlines() if '`suki:screenIds`' in l), '')
    ok('Q25' in row and 'not backed up' in row.lower(), 'suki:screenIds has its row: Q25, not backed up')


def run(b, t):
    register(b, t)
    screens_on_page(b, t)
    ipad_and_mac(b, t)
    overlays(b, t)
    flows(b, t)
    missing_entry(b, t)
    switch(b, t)
    changelog(b, t)
    saved_data(b, t)
