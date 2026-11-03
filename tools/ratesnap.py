"""Make js/ratesnap.js: the rate history Suki ships with (Q23), so Rate history works even if Frankfurter stops.

ECB reference rates, as pesos and US dollars per pound, every weekday from 2016 to the newest day. Refresh it with
any normal build (Ivan, 2 Nov 2026):

    python tools/ratesnap.py                  ask Frankfurter (ECB) for 2016 to today
    python tools/ratesnap.py --json rates.json   use a saved list instead: [{"d": "2026-10-30", "php": 85.32, "usd": 1.3399}, ...]
    python tools/ratesnap.py --check          say what the shipped snapshot holds, change nothing

Every day is checked the same way the app checks a reply (dates in order, pesos inside 30-120, no day jumping more
than 10% from the one before), so a bad download never ships. Only the currencies are asked for; nothing else is sent.
"""
import sys, os, json, datetime as dt, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'js', 'ratesnap.js')
START = '2016-01-01'
URL = 'https://api.frankfurter.dev/v1/{a}..{b}?base=GBP&symbols=PHP,USD'


def fetch(a, b):
    with urllib.request.urlopen(URL.format(a=a, b=b), timeout=60) as r:
        j = json.load(r)
    return [{'d': d, 'php': v['PHP'], 'usd': v.get('USD')} for d, v in sorted(j['rates'].items())]


def check(days):
    prev = None
    for x in days:
        dt.date.fromisoformat(x['d'])
        if not 30 <= x['php'] <= 120: raise SystemExit(f"{x['d']}: ₱{x['php']} is outside 30-120")
        if not (x.get('usd') and 0.8 <= x['usd'] <= 3): raise SystemExit(f"{x['d']}: ${x.get('usd')} isn't a sensible dollar rate")
        if prev:
            if x['d'] <= prev['d']: raise SystemExit(f"{x['d']} comes after {prev['d']}: dates out of order")
            if abs(x['php'] / prev['php'] - 1) > 0.10: raise SystemExit(f"{x['d']}: jumps more than 10% from {prev['d']}")
        prev = x


def write(days):
    days = [x for x in days if x['d'] >= START]
    check(days)
    first = dt.date.fromisoformat(days[0]['d'])
    rows, last = [], first
    for x in days:
        d = dt.date.fromisoformat(x['d'])
        rows.append([(d - last).days, round(x['php'] * 100), round(x['usd'] * 1e4)])
        last = d
    js = ('/* Suki · ratesnap.js (Q23)\n'
          '   The rate history Suki ships with: ECB reference rates, pesos and US dollars per pound, every weekday.\n'
          '   Made by tools/ratesnap.py. Don\'t edit by hand: run it again to refresh.\n'
          '   Plain script (not a module): files share one global scope and load in the order listed in index.html. */\n'
          'window.sukiRateSnap = {\n'
          "  source: 'European Central Bank, through Frankfurter',\n"
          f"  made: '{dt.date.today().isoformat()}',\n"
          f"  from: '{days[0]['d']}',\n"
          f"  to: '{days[-1]['d']}',\n"
          '  // each day: [days since the one before, pesos per £1 × 100, US dollars per £1 × 10,000]\n'
          '  days: ' + json.dumps(rows, separators=(',', ':')) + ',\n'
          '};\n')
    open(OUT, 'w', encoding='utf-8').write(js)
    print(f'{OUT}: {len(rows)} days, {days[0]["d"]} to {days[-1]["d"]}, {len(js) // 1024} KB')


def main():
    a = sys.argv[1:]
    if '--check' in a:
        src = open(OUT, encoding='utf-8').read()
        frm = src.split("from: '")[1][:10]; to = src.split("to: '")[1][:10]
        n = src.split('days: ')[1].count('],[') + 1
        return print(f'Shipped snapshot: {n} days, {frm} to {to}')
    if '--json' in a:
        days = json.load(open(a[a.index('--json') + 1], encoding='utf-8'))
    else:
        days = fetch(START, dt.date.today().isoformat())
    write(sorted(days, key=lambda x: x['d']))


if __name__ == '__main__':
    main()
