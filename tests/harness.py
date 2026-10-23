"""Shared set-up for the Suki tests (adapted from Vocal Sessions).

Every test file has a run(browser, t) function. `t` collects results:
    t.ok(condition, 'what should be true')
Run everything with:  python tests/run.py
"""
import os, json, threading, functools, datetime as dt
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_PATH = os.path.abspath(os.environ.get('SUKI_APP', os.path.join(ROOT, 'index.html')))

# The app is served over http://localhost, like GitHub Pages serves it. One small server per folder.
class _Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store'); super().end_headers()
_servers = {}
def url(path=APP_PATH):
    path = os.path.abspath(path); folder = os.path.dirname(path)
    if folder not in _servers:
        srv = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(_Quiet, directory=folder))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        _servers[folder] = srv
    return f'http://localhost:{_servers[folder].server_address[1]}/'

def offline(path=APP_PATH):
    """Switch the server off: a real "no connection" for the page and its offline helper."""
    folder = os.path.dirname(os.path.abspath(path)); srv = _servers[folder]
    srv.shutdown(); srv.server_close()

def online(path=APP_PATH):
    """Switch it back on, on the same port, so the address (and the saved offline copy) stays the same."""
    folder = os.path.dirname(os.path.abspath(path)); port = _servers[folder].server_address[1]
    srv = ThreadingHTTPServer(('127.0.0.1', port), functools.partial(_Quiet, directory=folder))
    threading.Thread(target=srv.serve_forever, daemon=True).start(); _servers[folder] = srv

OUT = os.path.join(ROOT, 'tests', 'output')
os.makedirs(OUT, exist_ok=True)

UA_IPHONE = ('Mozilla/5.0 (iPhone; CPU iPhone OS 26_0 like Mac OS X) AppleWebKit/605.1.15 '
             '(KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1')

today = dt.date.today()
def day(n): return (today - dt.timedelta(days=n)).isoformat()
RATE = 74.12

def sample():
    """Data shaped like Suki 2.0 saved it: purchases, price notes and a rate."""
    return {
        'purchases': [
            {'id': 'a1', 'item': 'Chickenjoy bucket', 'price': 459, 'date': day(0), 'category': 'Food & drink', 'location': 'SM Megamall',
             'venue': 'Restaurant', 'payment': 'Revolut', 'notes': 'Shared with family', 'gbpAtPurchase': 6.19, 'rateAtPurchase': RATE},
            {'id': 'a2', 'item': 'Jeepney', 'price': 13, 'date': day(1), 'category': 'Transport', 'location': 'Cubao', 'venue': 'Transport',
             'payment': 'Cash', 'notes': '', 'gbpAtPurchase': None, 'rateAtPurchase': None},
            {'id': 'a3', 'item': 'Groceries', 'price': 1234.5, 'date': day(1), 'category': 'Groceries', 'location': '', 'venue': 'Supermarket',
             'payment': 'Cash', 'notes': '', 'gbpAtPurchase': None, 'rateAtPurchase': None},
            {'id': 'a4', 'item': 'Island hopping tour', 'price': 1500, 'date': day(9), 'category': 'Activities', 'location': 'El Nido',
             'venue': '', 'payment': 'Cash', 'notes': '', 'gbpAtPurchase': 20.24, 'rateAtPurchase': RATE},
        ],
        'observations': [
            {'id': 'o1', 'itemId': 'bigas', 'itemName': 'Bigas', 'price': 52, 'date': day(2), 'location': 'Quiapo', 'venue': 'Palengke', 'note': '1 kg'},
            {'id': 'o2', 'itemId': 'tubig', 'itemName': 'Tubig na bottled', 'price': 25, 'date': day(3), 'location': '', 'venue': 'Convenience store', 'note': '500 ml'},
        ],
        'rate': {'value': RATE, 'date': day(0), 'cachedAt': dt.datetime.now(dt.timezone.utc).isoformat(), 'source': 'Frankfurter reference rate'},
    }

# Put data straight into Suki's own storage (IndexedDB 'suki-db', store 'kv'), as an older version would have left it.
# o is {key: value}; keys missing from o are removed. localStorage is cleared apart from the motion setting.
SEED = """async o=>{const m=localStorage.getItem('suki:motion');localStorage.clear();if(m!==null)localStorage.setItem('suki:motion',m);
 if(o&&o.__ls){for(const k in o.__ls)localStorage.setItem(k,o.__ls[k]);delete o.__ls}
 const db=await new Promise((res,rej)=>{const r=indexedDB.open('suki-db',1);r.onupgradeneeded=()=>{if(!r.result.objectStoreNames.contains('kv'))r.result.createObjectStore('kv')};r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error)});
 await new Promise(res=>{const t=db.transaction('kv','readwrite'),s=t.objectStore('kv');s.clear();if(o)for(const k in o)s.put(o[k],k);t.oncomplete=res;t.onerror=res});db.close();}"""

READ = """async k=>{const db=await new Promise(res=>{const r=indexedDB.open('suki-db',1);r.onsuccess=()=>res(r.result)});
 return await new Promise(res=>{const r=db.transaction('kv','readonly').objectStore('kv').get(k);r.onsuccess=()=>{res(r.result);db.close()}})}"""

# every address the app asks for the rate, in the order it tries them
RATE_HOSTS = ['api.frankfurter.dev', 'api.frankfurter.app', 'cdn.jsdelivr.net', 'currency-api.pages.dev']

def rate_route(ctx, value=RATE, fail=False, down=(), values=None):
    """Answer the exchange-rate requests ourselves, so tests never need the internet.
    fail: every source is down. down: hosts that answer 503. values: {host: rate} to answer a host with another rate."""
    def handle(route):
        host = route.request.url.split('/')[2]
        if fail or any(host.endswith(h) for h in down): return route.fulfill(status=503, body='down', headers={'Access-Control-Allow-Origin': '*'})
        v = next((x for h, x in (values or {}).items() if host.endswith(h)), value)
        d = today.isoformat()
        if host == 'api.frankfurter.dev': body = {'date': d, 'base': 'GBP', 'quote': 'PHP', 'rate': v}
        elif host == 'api.frankfurter.app': body = {'amount': 1.0, 'base': 'GBP', 'date': d, 'rates': {'PHP': v}}
        else: body = {'date': d, 'gbp': {'php': v, 'eur': 1.15}}
        route.fulfill(status=200, content_type='application/json', headers={'Access-Control-Allow-Origin': '*'}, body=json.dumps(body))
    for h in RATE_HOSTS: ctx.route(f'**/*{h}/**', handle)

def rate_noise(m):
    """A rate source that's down on purpose logs a failed load; that isn't a fault in the app."""
    return 'Failed to load resource' in m.text and any(h in (m.location or {}).get('url', '') for h in RATE_HOSTS)


class T:
    """Collects results for one test file."""
    def __init__(self, name):
        self.name, self.passed, self.fails, self.errors = name, 0, [], []

    def ok(self, cond, msg):
        if cond: self.passed += 1
        else: self.fails.append(msg)
        print(('  pass  ' if cond else '  FAIL  ') + msg, flush=True)

    def page(self, b, w=390, h=844, sc='light', touch=False, ua=UA_IPHONE, data='sample', init=None, rate_fail=False, ctx_args=None, rate_opts=None):
        """A fresh app page. data='sample' seeds sample(); None leaves the app empty; a dict seeds that dict."""
        args = dict(viewport={'width': w, 'height': h}, device_scale_factor=2 if w < 500 else 1, color_scheme=sc,
                    has_touch=touch, accept_downloads=True, timezone_id='Europe/London', locale='en-GB',
                    permissions=['clipboard-read', 'clipboard-write'])
        if ua: args['user_agent'] = ua
        args.update(ctx_args or {})
        ctx = b.new_context(**args)
        rate_route(ctx, fail=rate_fail, **(rate_opts or {}))
        # motion off by default, so nothing waits on springs; a test can turn it back on with its own init
        ctx.add_init_script("try{if(localStorage.getItem('suki:motion')===null)localStorage.setItem('suki:motion','0')}catch(e){}")
        if init: ctx.add_init_script(init)
        pg = ctx.new_page()
        tag = f'{self.name} {w}x{h}'
        pg.on('pageerror', lambda e: self.errors.append(f'{tag}: {str(e).splitlines()[0]}'))
        # a rate source switched off on purpose logs a failed request, which isn't a fault
        quiet = rate_noise
        pg.on('console', lambda m: self.errors.append(f'{tag} console: {m.text}') if m.type == 'error' and not quiet(m) else None)
        pg.goto(url())
        ready(pg)
        pg.evaluate(SEED, sample() if data == 'sample' else data)
        pg.reload()
        ready(pg)
        return pg

    def shot(self, pg, name, **kw):
        pg.screenshot(path=os.path.join(OUT, f'{self.name}-{name}.png'), **kw)


def ready(pg):
    """Wait for the launch screen to go."""
    pg.wait_for_function("!document.getElementById('splash')&&typeof U!=='undefined'&&!!document.querySelector('#app h1')", timeout=15000)
    pg.wait_for_timeout(100)

BAD_TEXT = r"""(()=>{const t=document.body.innerText;const m=t.match(/.{0,30}(\bundefined\b|\bNaN\b|\[object Object\]|\bnull\b).{0,30}/);return m?m[0]:''})()"""
