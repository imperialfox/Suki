"""Offline: after one visit online, Suki opens and works with no connection, and an update arrives with
pull to refresh (then works offline too). Runs on a copy of the app, so it can pretend to publish a new version."""
import os, re, shutil, tempfile
from harness import ROOT, SEED, sample, ready, url, offline, online, rate_route

COPY = ['index.html', 'sw.js', 'manifest.json', 'icon.svg', 'icon-512.png', 'apple-touch-icon.png', 'js', 'css']


def run(b, t):
    ok = t.ok
    tmp = tempfile.mkdtemp()
    for f in COPY:
        src = os.path.join(ROOT, f)
        (shutil.copytree if os.path.isdir(src) else shutil.copy)(src, os.path.join(tmp, f))
    app = os.path.join(tmp, 'index.html')
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, timezone_id='Europe/London', locale='en-GB', service_workers='allow')
    rate_route(ctx)
    ctx.add_init_script("try{localStorage.setItem('suki:motion','0')}catch(e){}")
    pg = ctx.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(url(app)); ready(pg)
    pg.evaluate(SEED, sample()); pg.reload(); ready(pg)
    # the helper takes control once it's ready; on a busy machine (two processors here, WebKit on GitHub) that can be
    # after the page's last load, so the page loads once more, as a phone would next time (Q32, Known test issues)
    try: pg.wait_for_function("navigator.serviceWorker.controller!==null", timeout=15000)
    except Exception:
        pg.evaluate("navigator.serviceWorker.ready.then(()=>1)"); pg.reload(); ready(pg)
        pg.wait_for_function("navigator.serviceWorker.controller!==null", timeout=15000)
    pg.wait_for_timeout(800)  # let the offline copy finish saving
    ok('Ready' in pg.evaluate("SW_STATE"), 'Settings says it works offline')

    offline(app)
    pg.reload(); ready(pg)
    ok('₱3,206.50' in pg.inner_text('#app'), 'with no connection, Suki still opens with your data')
    pg.fill('#home-item', 'Buko juice'); pg.fill('#home-price', '40'); pg.click('form[data-form=home] .cta'); pg.wait_for_timeout(200)
    ok(pg.evaluate("D.purchases[0].item") == 'Buko juice', 'and you can log a purchase offline')
    pg.evaluate("go('search')"); pg.fill('#q', 'bigas'); pg.wait_for_timeout(100)
    ok('₱49.08' in pg.inner_text('#results'), 'official prices work offline')
    # Rate history's snapshot comes from the service worker's saved copy, like every other file (Q23)
    pg.evaluate("go('convert')"); pg.click('[data-a=openHistory]'); pg.wait_for_function("U.tab==='history'&&!!document.querySelector('#hsvg .hline')")
    ok(pg.locator('#hsvg .hline').count() == 1 and pg.evaluate("histSeries()[0].d") == '2016-01-04' and pg.locator('#hNews .evrow').count() >= 1,
       'Rate history works with no connection, from the snapshot and news notes the service worker saved')
    pg.evaluate("go('home')")

    # publish "a new version" and pull to refresh
    online(app)
    html = open(app, encoding='utf-8').read()
    html = re.sub(r"APP_VERSION='[\d.]+'", "APP_VERSION='99.0.0'", html).replace('?v=', '?v=99-')
    open(app, 'w', encoding='utf-8').write(html)
    pg.evaluate("go('home')")
    r = pg.evaluate("refreshApp()")
    ok(r == 'reload', 'pull to refresh finds the new version')
    pg.wait_for_timeout(1500); ready(pg)
    ok(pg.evaluate("APP_VERSION") == '99.0.0', 'and loads it')
    pg.wait_for_timeout(1000)
    offline(app)
    pg.reload(); ready(pg)
    ok(pg.evaluate("APP_VERSION") == '99.0.0' and 'Buko juice' in pg.inner_text('#app'), 'the new version works offline too, with your data')
    ok(not errs, 'no errors' + (': ' + '; '.join(errs[:3]) if errs else ''))
    online(app)
    ctx.close()
    shutil.rmtree(tmp, ignore_errors=True)
