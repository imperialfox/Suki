"""Random-tap tester (from Vocal Sessions): taps, types, scrolls, resizes and reloads at random, checking after every
step that nothing is broken. Each seed is a repeatable run. More steps:  SUKI_FUZZ_STEPS=2000 python tests/run.py fuzz"""
import os, random, collections
from harness import sample, OUT, ready, url, SEED, rate_route, day

STEPS = int(os.environ.get('SUKI_FUZZ_STEPS', '250'))
SEEDS = [int(s) for s in os.environ.get('SUKI_FUZZ_SEEDS', '11,12,13,14').split(',')]
SIZES = [(390, 844, True), (375, 667, True), (852, 393, True), (820, 1180, True), (1180, 820, True), (1440, 900, False), (320, 568, True)]
TEXTS = ['', 'x', '  ', '<b>bold</b> & "quotes" \'single\'', '😀 emoji', 'A' * 300, '-5', '0', '999999', '12.7', '1,000', 'abc', 'Line\nbreak']
INV = r"""(()=>{const p=[];const L=document.getElementById('layer');
 if(document.documentElement.scrollWidth>innerWidth+1)p.push('sideways scroll '+document.documentElement.scrollWidth+'>'+innerWidth);
 if(U.sheet&&!L.querySelector('.sheet'))p.push('sheet state "'+U.sheet+'" but nothing shown');
 if(!U.sheet&&L.querySelector('.sheet'))p.push('sheet shown without state');
 if(!!U.sheet!==document.body.classList.contains('sheet-open'))p.push('page behind a sheet left scaled, or not scaled');
 if(!U.sheet&&![...document.querySelectorAll('[data-a=tab]')].some(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.bottom>0&&r.top<innerHeight}))p.push('no way to switch tabs');
 const ids=new Set();D.purchases.forEach(x=>{if(!(x.price>0)||!isFinite(x.price))p.push('bad price '+x.id+'='+x.price);
   if(!/^\d{4}-\d{2}-\d{2}$/.test(x.date))p.push('bad date '+x.id+'='+x.date);if(!CATS.includes(x.category))p.push('bad category '+x.category);
   if(!x.item||!String(x.item).trim())p.push('purchase without a name');if(ids.has(x.id))p.push('repeated id '+x.id);ids.add(x.id)});
 D.observations.forEach(o=>{if(!(o.price>0))p.push('bad note price '+o.id);if(!itemById(o.itemId))p.push('note for a missing item '+o.itemId)});
 const txt=document.getElementById('app').innerText+' '+L.innerText+' '+document.getElementById('bar').innerText;
 const m=txt.match(/.{0,40}(\bundefined\b|\bNaN\b|\[object Object\]|\bnull\b|Infinity).{0,30}/);if(m)p.push('bad text: '+m[0]);
 if(document.querySelectorAll('.toast').length>1)p.push('two toasts at once');
 if(U.tab==='spending'&&U.sel&&split()&&!D.purchases.some(x=>x.id===U.sel)&&document.querySelector('.pane .dhead'))p.push('pane shows a deleted purchase');
 return p;})()"""
VIS = r"""(()=>{const L=document.getElementById('layer');const root=L.querySelector('.scrim')?L:document;
 const els=[...root.querySelectorAll('[data-a],input:not([type=file]),textarea,select')].filter(e=>{const r=e.getBoundingClientRect();if(r.width<2||r.height<2)return false;if(r.bottom<0||r.top>innerHeight||r.right<0||r.left>innerWidth)return false;
   const cx=Math.min(innerWidth-1,Math.max(0,r.left+r.width/2)),cy=Math.min(innerHeight-1,Math.max(0,r.top+r.height/2));const t=document.elementFromPoint(cx,cy);return t&&(t===e||e.contains(t)||t.closest('[data-a]')===e);});
 return els.map((e,i)=>{e.setAttribute('data-fz',i);return {i,a:e.dataset.a||e.tagName.toLowerCase(),v:e.dataset.v||'',k:e.dataset.k||'',id:e.id||'',type:e.type||'',opts:e.tagName==='SELECT'?[...e.options].map(o=>o.value):[]};});})()"""
SKIP = {'importPick'}
HEAVY = ('openPurchase', 'editPurchase', 'delPurchase', 'delPurchaseYes', 'openItem', 'obsForm', 'delObs', 'delObsYes', 'cat', 'more', 'tillLog',
         'cashAdd', 'cashExact', 'quickGbp', 'example', 'input', 'textarea', 'select', 'erase', 'openNotes', 'exportBackup', 'saveBackup')


def run(b, t):
    found = collections.OrderedDict()
    def note(key, trace):
        if key not in found: found[key] = list(trace)[-14:]
    for seed in SEEDS:
        R = random.Random(seed); w, h, touch = R.choice(SIZES)
        ctx = b.new_context(viewport={'width': w, 'height': h}, has_touch=touch, color_scheme=R.choice(['light', 'dark']), accept_downloads=True,
                            timezone_id='Europe/London', locale='en-GB', permissions=['clipboard-read', 'clipboard-write'])
        rate_route(ctx)
        ctx.add_init_script("try{localStorage.setItem('suki:motion','0')}catch(e){}")
        pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('JavaScript error: ' + str(e).split('\n')[0]))
        pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
        pg.on('dialog', lambda d: d.dismiss())
        pg.goto(url()); ready(pg)
        data = sample()
        data['purchases'] += [{'id': f'f{i}', 'item': f'Item {i}', 'price': 10 + i, 'date': day(i % 12), 'category': ['Other', 'Shopping', 'Transport'][i % 3]} for i in range(14)]
        pg.evaluate(SEED, data); pg.reload(); ready(pg)
        trace = collections.deque(maxlen=24); trace.append(f'seed {seed}, {w}x{h}')
        for step in range(STEPS):
            r = R.random()
            try:
                if r < 0.03:
                    w, h, _ = R.choice(SIZES); pg.set_viewport_size({'width': w, 'height': h}); trace.append(f'resize {w}x{h}'); pg.wait_for_timeout(120)
                elif r < 0.05:
                    pg.reload(); trace.append('reload'); ready(pg)
                elif r < 0.07:
                    pg.keyboard.press('Escape'); trace.append('escape')
                elif r < 0.10:
                    pg.mouse.wheel(0, R.choice([-800, 400, 1500])); trace.append('scroll'); pg.wait_for_timeout(120)
                elif r < 0.11:
                    pg.keyboard.press(f'Control+{R.randint(1, 5)}'); trace.append('shortcut')
                else:
                    els = [e for e in pg.evaluate(VIS) if e['a'] not in SKIP]
                    if not els:
                        note('nothing tappable on screen', trace); trace.append('nothing tappable'); pg.keyboard.press('Escape'); continue
                    wts = [0.3 if x['a'] == 'tab' else (3 if x['a'] in HEAVY else 1) for x in els]
                    e = R.choices(els, weights=wts)[0]; sel = f'[data-fz="{e["i"]}"]'
                    if e['a'] == 'select':
                        v = R.choice(e['opts'] or [''])
                        try: pg.select_option(sel, v, timeout=1500)
                        except Exception: pass
                        trace.append(f'choose {e["id"]} = {v!r}')
                    elif e['a'] in ('input', 'textarea'):
                        val = R.choice(TEXTS)
                        if e['type'] == 'date': val = R.choice(['2026-01-01', '2025-12-31', '2030-05-05', day(0)])
                        try: pg.fill(sel, val, timeout=1500)
                        except Exception: pass
                        trace.append(f'type {e["id"] or e["a"]} = {val[:20]!r}')
                        if R.random() < 0.3: pg.keyboard.press('Enter'); trace.append('enter')
                    else:
                        trace.append(f'tap {e["a"]} v={e["v"][:20]} k={e["k"][:14]}')
                        pg.click(sel, timeout=1500, no_wait_after=True)
                    pg.wait_for_timeout(R.choice([30, 80, 250]))
                for x in errs:
                    if 'Failed to load resource' not in x: note(x, trace)
                errs.clear()
                for prob in pg.evaluate(INV):
                    if prob not in found: pg.screenshot(path=os.path.join(OUT, f'fuzz-{len(found)}.png'))
                    note(prob, trace)
            except Exception as ex:
                msg = str(ex).split('\n')[0][:120]
                if 'Timeout' in msg: trace.append('tap timed out'); continue
                note('test driver: ' + msg, trace)
        ctx.close()
    if not found:
        t.ok(True, f'{len(SEEDS) * STEPS} random steps over {len(SEEDS)} runs found no problems')
    for k, tr in found.items():
        t.ok(False, 'random taps found: ' + k)
        for x in tr: print('        ' + x)
