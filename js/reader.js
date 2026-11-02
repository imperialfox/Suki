/* Suki · reader.js
   Smart add's sentence reader (Q14): word rules only, offline, the same answer every time. No AI reads anything.
   READER.read(text, now, learned, rate) turns one line, or several, into purchases for the preview:
     {said, saidAt?, item, price, category, catFrom, date, future, location, venue, payment, notes, flags, match, learnKey, tie?}
   - catFrom: 'learned' (a word Suki learned), 'list' (the price list), 'words' (clue words), 'shop', 'tie' (two fit:
     the preview asks which), 'guess' (no clue at all: the preview tints it)
   - flags: 'amount' (no amount), 'item' (no name), 'future', 'pounds' (changed at the saved rate), 'numbers' (more
     than one number, so the last sure one was taken)
   - saidAt (Q15): the Siri Shortcut's stamp at the start of the line ("2026-11-21 13:05"), only when it had one
   Needs catalog.js (wordMatch, catOf, priceOf) loaded first. Plain script, not a module. */
const READER = (() => {
  const low = (s) => String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  const toks = (s) => low(s).replace(/[^a-z0-9\s]/g, ' ').split(/\s+/).filter(Boolean);

  /* ---------- number words, English and Tagalog ---------- */
  const UNITS = { one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9, isa: 1, isang: 1, dalawa: 2, dalawang: 2, tatlo: 3, tatlong: 3, apat: 4, lima: 5, limang: 5, anim: 6, pito: 7, pitong: 7, walo: 8, walong: 8, siyam: 9, singko: 5, uno: 1, dos: 2, tres: 3, kwatro: 4, sais: 6, siyete: 7, otso: 8, nuwebe: 9 };
  const TEENS = { ten: 10, eleven: 11, twelve: 12, thirteen: 13, fourteen: 14, fifteen: 15, sixteen: 16, seventeen: 17, eighteen: 18, nineteen: 19, sampu: 10, sampung: 10, diyes: 10 };
  const TENS = { twenty: 20, thirty: 30, forty: 40, fifty: 50, sixty: 60, seventy: 70, eighty: 80, ninety: 90, bente: 20, beinte: 20, trenta: 30, treinta: 30, kwarenta: 40, kuwarenta: 40, singkwenta: 50, sinkwenta: 50, sisenta: 60, setenta: 70, otsenta: 80, nobenta: 90 };
  const HUND = { hundred: 1, daan: 1, raan: 1, gatos: 1 };
  const THOU = { thousand: 1, libo: 1 };
  const isNumWord = (w) => w in UNITS || w in TEENS || w in TENS || w in HUND || w in THOU;
  const bare = (p) => (p || '').toLowerCase().replace(/[^a-z]/g, '');
  // "a hundred and twenty" → 120, "one twenty" → 120, "bente" → 20, "isang daan" → 100. "fifty 50 pesos" counts once
  function wordsToDigits(s) {
    const parts = s.split(/(\s+)/),
      out = [];
    for (let i = 0; i < parts.length; i++) {
      const w = bare(parts[i]);
      const startOk = w in UNITS || w in TEENS || w in TENS || ((w === 'a' || w === 'isang') && /^(hundred|thousand|daan|libo)/.test((parts[i + 2] || '').toLowerCase()));
      if (!startOk || /^\W*$/.test(parts[i])) {
        out.push(parts[i]);
        continue;
      }
      let j = i,
        last = i; // the last number word read, so the space after it is kept
      const run = [];
      while (j < parts.length) {
        const x = bare(parts[j]);
        if (/^\s+$/.test(parts[j])) {
          j++;
          continue;
        }
        if (isNumWord(x) || ((x === 'a' || x === 'isang') && !run.length)) {
          run.push(x);
          last = j;
          j++;
          continue;
        }
        if ((x === 'and' || x === 'na' || x === 'ng' || x === 't') && run.length && isNumWord(bare(parts[j + 2]))) {
          j++;
          continue;
        }
        break;
      }
      // a lone "five" or "one" in a name ("five guys", "one way") stays a word unless pesos follow
      const rest = parts.slice(j).join('').toLowerCase();
      if (run.length === 1 && w in UNITS && !/^\s*(pesos?|php|piso)\b/.test(rest)) {
        out.push(parts[i]);
        continue;
      }
      let total = 0,
        cur = 0;
      for (let k = 0; k < run.length; k++) {
        const x = run[k],
          nx = run[k + 1];
        if (x === 'a' || (x === 'isang' && nx && (nx in HUND || nx in THOU))) cur = 1;
        else if (x in UNITS && nx && (nx in TENS || nx in TEENS) && !cur && !total) cur = UNITS[x] * 100;
        else if (x in UNITS) cur += UNITS[x];
        else if (x in TEENS) cur += TEENS[x];
        else if (x in TENS) cur += TENS[x];
        else if (x in HUND) cur = (cur || 1) * 100;
        else if (x in THOU) {
          total += (cur || 1) * 1000;
          cur = 0;
        }
      }
      out.push(String(total + cur));
      const m = parts.slice(j).join('').match(/^\s*(\d+)/);
      if (m && +m[1] === total + cur) {
        i = j;
        while (i < parts.length && !/\d/.test(parts[i])) i++;
        continue;
      }
      i = last;
    }
    return out.join('');
  }

  /* ---------- days ---------- */
  const DAYS = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
  const MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'];
  const iso = (d) => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  const addDays = (d, n) => new Date(d.getFullYear(), d.getMonth(), d.getDate() + n);
  // a date said without a year: the nearest one, so "21 November" said on 1 Nov is this year's (and in the future)
  function nearest(base, m, day) {
    let best = null;
    [base.getFullYear() - 1, base.getFullYear(), base.getFullYear() + 1].forEach((y) => {
      const d = new Date(y, m, day);
      if (d.getMonth() === m && (!best || Math.abs(d - base) < Math.abs(best - base))) best = d;
    });
    return best;
  }
  const MON = '(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*';
  const DATE_RULES = [
    [/\b(today|ngayon|kanina|this (?:morning|afternoon|evening)|tonight|earlier)\b/, (m, b) => b],
    [/\b(yesterday|kahapon|last night)\b/, (m, b) => addDays(b, -1)],
    [/\b(\d+) days? ago\b/, (m, b) => addDays(b, -+m[1])],
    [/\b(?:on )?(last )?(sunday|monday|tuesday|wednesday|thursday|friday|saturday|sun|mon|tues?|wed|thu(?:rs?)?|fri|sat)\b/, (m, b) => {
      const want = DAYS.findIndex((d) => d.startsWith(m[2].slice(0, 3)));
      let back = (b.getDay() - want + 7) % 7;
      if (m[1] && back === 0) back = 7;
      return addDays(b, -back);
    }],
    // a day with st/nd/rd/th is surely a date, so it's looked for first: "jeep 14 november 21st" is the 21st
    [new RegExp('\\b(?:on )?(?:the )?(\\d{1,2})(?:st|nd|rd|th)(?: of)? ' + MON + '\\b'), (m, b) => nearest(b, MONTHS.indexOf(m[2].slice(0, 3)), +m[1])],
    [new RegExp('\\b(?:on )?' + MON + ' (?:the )?(\\d{1,2})(?:st|nd|rd|th)\\b'), (m, b) => nearest(b, MONTHS.indexOf(m[1].slice(0, 3)), +m[2])],
    [new RegExp('\\b(?:on )?(?:the )?(\\d{1,2})(?: of)? ' + MON + '\\b'), (m, b) => nearest(b, MONTHS.indexOf(m[2].slice(0, 3)), +m[1])],
    [new RegExp('\\b(?:on )?' + MON + ' (\\d{1,2})\\b'), (m, b) => nearest(b, MONTHS.indexOf(m[1].slice(0, 3)), +m[2])],
    [/\b(?:on )?(\d{1,2})\/(\d{1,2})\b/, (m, b) => nearest(b, +m[2] - 1, +m[1])],
    [/\b(?:on )?the (\d{1,2})(?:st|nd|rd|th)\b/, (m, b) => nearest(b, b.getMonth(), +m[1])],
  ];
  function takeDate(s, base) {
    for (const [re, fn] of DATE_RULES) {
      const m = s.match(re);
      if (!m) continue;
      const d = fn(m, base);
      if (d && !isNaN(d)) return { date: iso(d), future: iso(d) > iso(base), rest: s.replace(m[0], ' ') };
    }
    return null;
  }

  /* ---------- how he paid ---------- */
  const PAY_RULES = [
    [/\b(?:(?:paid )?(?:via|with|by|using|on|thru|through) )?(g ?cash|maya|paymaya)\b/, 'Other', (m) => (/maya/.test(m[1]) ? 'Maya' : 'GCash')],
    [/\b(?:(?:paid )?(?:via|with|by|using|on) )?(revolut|revolute|revoult|revolt)\b/, 'Revolut'],
    [/\b(?:(?:paid )?(?:via|with|by|using|on) )?(?:my |the )?(credit card|debit card|(?<!sim )card|visa|mastercard|monzo|contactless|apple pay)\b/, 'Other card'],
    [/\b(?:(?:paid )?(?:in|with|by) )?cash\b/, 'Cash'],
  ];
  function takePay(s) {
    for (const [re, pay, note] of PAY_RULES) {
      const m = s.match(re);
      if (m) return { payment: pay, payNote: note ? note(m) : '', rest: s.replace(m[0], ' ').replace(/\bboth\b/, ' ') };
    }
    return null;
  }

  /* ---------- shops: where bought, and a category hint ---------- */
  const SHOPS = [
    [/\b(palengke|wet market|public market|market)\b/, 'Palengke', 'Groceries'],
    [/\b(carinderia|karinderya|carenderia|turo turo|eatery)\b/, 'Carinderia', 'Food & drink'],
    [/\b(jollibee|mcdo|mcdonalds|mcdonald s|chowking|greenwich|kfc|max s|shakey s|starbucks|restaurant|resto|cafe)\b/, 'Restaurant', 'Food & drink'],
    [/\b(seveneleven|ministop|alfamart|family ?mart|lawson|uncle john s|sari sari(?: store)?)\b/, 'Convenience store', 'tie'],
    [/\b(puregold|savemore|sm supermarket|robinsons supermarket|waltermart|landmark|supermarket|grocery store)\b/, 'Supermarket', 'Groceries'],
    [/\b(street vendor|vendor|ambulant)\b/, 'Street vendor', ''],
  ];
  const GENERIC_SHOP = /^(restaurant|resto|cafe|market|supermarket|vendor|street vendor|eatery|grocery store)$/;
  // names as people write them: "san jose city" → "San Jose City", "sm" → "SM", "naia" → "NAIA"
  const nice = (s) =>
    s.trim().split(/\s+/)
      .map((w) => (/^[bcdfghjklmnpqrstvwxz]{2,3}$/.test(w) || /^(naia|lrt|mrt|bgc|sim|atm)$/.test(w) ? w.toUpperCase() : w.charAt(0).toUpperCase() + w.slice(1)))
      .join(' ')
      .replace(/\bSeveneleven\b/g, '7-Eleven');

  /* ---------- category clue words ---------- */
  const CLUES = {
    Transport: 'grab taxi cab bus jeep jeepney trike tricycle angkas joyride ferry boat bangka fare pamasahe lrt mrt train flight plane airfare toll parking gas petrol diesel van habal uv',
    Accommodation: 'hotel hostel airbnb resort inn lodge guesthouse pension homestay nights night',
    Activities: 'tour hopping snorkel snorkelling snorkeling diving dive surf lesson entrance entry ticket tickets museum zipline kayak cinema movie karaoke spa',
    Groceries: 'groceries grocery vegetables veg fruit fruits meat fish eggs mango mangoes banana bananas pineapple calamansi',
    Shopping: 'souvenir souvenirs pasalubong shirt tshirt clothes shoes flip flops tsinelas sunscreen powerbank power bank charger cable toiletries shampoo soap medicine pharmacy watsons mercury gift sunglasses hat',
    'Food & drink': 'tubig buko chips lunch dinner breakfast brunch merienda meryenda snack snacks coffee beer beers drink drinks meal food ulam kain icecream cream water softdrinks coke juice milktea tea cake bread pizza burger fries spaghetti pasta noodles chicken pork bbq barbecue siomai siopao gin rum vodka wine tanduay',
    Other: 'tip tips laundry haircut sim load atm fee donation',
  };
  const CLUE = {};
  Object.keys(CLUES).forEach((c) => CLUES[c].split(' ').forEach((w) => (CLUE[w] = c)));

  /* ---------- amounts ---------- */
  const NUM = '(\\d{1,3}(?:,\\d{3})+|\\d+)(?:\\.(\\d+))?';
  // a number followed by one of these is a quantity, not a price: "2 kilos", "for 2 nights", "x2"
  const QTY = /^\s*(kilos?|kg|g|grams?|ml|l|litres?|liters?|cans?|bottles?|pcs|pieces?|packs?|sachets?|nights?|days?|hours?|hrs?|mins?|minutes?|pax|people|persons?|km|st|nd|rd|th|x|in 1|am|pm)\b/;
  // ... and one after these is part of a name: "NAIA Terminal 3", "LRT 1", "Gate 5"
  const BEFORE_NAME = /(?:\bx|terminal|lrt|mrt|line|no|number|#|gate|room|route|platform|pier)\s*$/;
  function amounts(s) {
    const found = [],
      num = (a, b) => parseFloat(a.replace(/,/g, '') + (b ? '.' + b : '')),
      inside = (i) => found.some((f) => i >= f.i && i < f.i + f.len);
    let m;
    const reP = new RegExp('(?:₱|\\bphp\\s?|\\bp\\s?)' + NUM + '(k)?\\b', 'gi');
    while ((m = reP.exec(s))) found.push({ v: num(m[1], m[2]) * (m[3] ? 1000 : 1), i: m.index, len: m[0].length, sure: true });
    const reG = new RegExp('£\\s?' + NUM + '|' + NUM + '\\s*(?:pounds?|quid|gbp)\\b', 'gi');
    while ((m = reG.exec(s))) if (!inside(m.index)) found.push({ v: num(m[1] || m[3], m[2] || m[4]), i: m.index, len: m[0].length, sure: true, gbp: true });
    const reS = new RegExp(NUM + '(k)?\\s*(?:pesos?|php|piso)\\b', 'gi');
    while ((m = reS.exec(s))) if (!inside(m.index)) found.push({ v: num(m[1], m[2]) * (m[3] ? 1000 : 1), i: m.index, len: m[0].length, sure: true });
    const reB = new RegExp('\\b' + NUM + '(k)?\\b', 'gi');
    while ((m = reB.exec(s))) {
      if (inside(m.index)) continue;
      if (QTY.test(s.slice(m.index + m[0].length)) || BEFORE_NAME.test(s.slice(0, m.index))) continue;
      found.push({ v: num(m[1], m[2]) * (m[3] ? 1000 : 1), i: m.index, len: m[0].length, sure: false });
    }
    return found.sort((a, b) => a.i - b.i);
  }

  /* ---------- one purchase ---------- */
  const PLACE = "[a-z][a-z .'-]*?(?:(?:terminal|line|gate|pier|platform) \\d+)?";
  const STOP = '(?=\\s*$|[,.]| on | at | for | with | by | via | using | paid | and |\\s*(?<!(?:terminal|line|gate|pier|platform) )\\d|\\s*₱)';
  function readOne(seg, shared, base, learned, rate) {
    let s = ' ' + seg + ' ';
    const p = { said: '', flags: [], notes: [] };
    const d = takeDate(s, base);
    if (d) (s = d.rest), (p.date = d.date), (p.future = d.future);
    else if (shared.date) (p.date = shared.date), (p.future = shared.future);
    else p.date = iso(base);
    const pay = takePay(s);
    if (pay) {
      s = pay.rest;
      p.payment = pay.payment;
      if (pay.payNote) p.notes.push('Paid with ' + pay.payNote);
    } else if (shared.payment) {
      p.payment = shared.payment;
      if (shared.payNote) p.notes.push('Paid with ' + shared.payNote);
    }
    // the amount: the last sure one (₱, P, PHP, pesos, £), else the last plain number
    const am = amounts(s),
      sure = am.filter((a) => a.sure),
      pool = sure.length ? sure : am,
      pick = pool[pool.length - 1];
    if (pick) {
      if (pick.gbp) {
        p.flags.push('pounds');
        if (rate > 0) {
          p.price = Math.round(pick.v * rate * 100) / 100;
          p.notes.push('£' + pick.v + ' at £1 = ₱' + rate.toFixed(2));
        } else p.notes.push('£' + pick.v + ': no saved rate yet, so add the pesos');
      } else p.price = pick.v;
      if (pool.length > 1) p.flags.push('numbers');
      s = s.slice(0, pick.i) + ' ' + s.slice(pick.i + pick.len);
    }
    // places: "from X to Y", "at SHOP in TOWN", "in TOWN", "at PLACE", "to PLACE"
    let m = s.match(new RegExp('\\bfrom (' + PLACE + ') to (' + PLACE + ')' + STOP));
    if (m) (p.location = nice(m[1]) + ' to ' + nice(m[2])), (s = s.replace(m[0], ' '));
    let shopName = '';
    for (const [re, venue, hint] of SHOPS) {
      const sm = s.match(re);
      if (!sm) continue;
      p.venue = venue;
      p.shopHint = hint;
      shopName = GENERIC_SHOP.test(sm[1]) ? '' : nice(sm[1]);
      s = s.replace(new RegExp('\\b(?:(?:at|from|in) (?:the )?)?' + sm[1].replace(/ /g, '\\s') + '\\b'), ' ');
      break;
    }
    m = s.match(new RegExp('\\b(?:in|sa) (?:the )?(' + PLACE + ')' + STOP));
    if (m && !p.location) (p.location = (shopName ? shopName + ', ' : '') + nice(m[1])), (s = s.replace(m[0], ' '));
    if (!p.location && shared.location) p.location = shared.location;
    if (!p.venue && shared.location)
      for (const [re, venue, hint] of SHOPS)
        if (re.test(low(shared.location).replace(/\b7[\s-]?eleven\b/, 'seveneleven'))) {
          p.venue = venue;
          p.shopHint = hint;
          break;
        }
    m = s.match(new RegExp('\\bat (?:the )?(' + PLACE + ')' + STOP));
    if (m && !p.location) (p.location = nice(m[1])), (s = s.replace(m[0], ' '));
    m = s.match(new RegExp('\\bto (?:the )?(' + PLACE + ')' + STOP));
    if (m && !p.location) (p.location = nice(m[1])), (s = s.replace(m[0], ' '));
    // the item: whatever is left
    let item = s
      .replace(/\b(i paid|i bought|i got|i had|bought|got|had|paid for|paid|spent|for|worth|pesos?|php|piso|some|my|a|an|the|both|each|around|about|plus)\b/g, ' ')
      .replace(/[^a-z0-9\s'&-]/gi, ' ')
      .replace(/\s+/g, ' ')
      .trim()
      .replace(/^((and|of|on|with|at|to|in)\s+)+|(\s+(and|of|on|with|at|to|in))+$/g, '')
      .trim();
    const hit = item ? wordMatch(item) : null,
      it = hit && itemById(hit.id),
      key0 = toks(item).join(' ');
    // a short word that starts a catalogue name becomes that name: "jeep" → "Jeepney", "trike"… stays as said
    const full = hit && hit.whole && it && [it.english, it.name].find((n) => toks(n).join(' ').startsWith(key0) && toks(n).join(' ') !== key0 && n.split(' ').length <= 2);
    if (full) item = full;
    else if (item) item = item.charAt(0).toUpperCase() + item.slice(1);
    if (!item && shopName) item = shopName;
    p.item = item.slice(0, 200);
    if (it) p.match = matchInfo(p.item);
    // category: a learned word, the price list, clue words, the shop, then a guess
    const key = toks(p.item).join(' '),
      words = toks(p.item + ' ' + (p.venue === 'Palengke' ? 'palengke' : '')),
      lw = learned[key] || words.map((w) => learned[w]).find(Boolean),
      clueCats = [...new Set(toks(seg).map((w) => CLUE[w]).filter(Boolean))];
    if (lw) (p.category = lw), (p.catFrom = 'learned');
    else if (it) (p.category = catOf(it)), (p.catFrom = 'list');
    else if (clueCats.length === 1) (p.category = clueCats[0]), (p.catFrom = 'words');
    else if (clueCats.length > 1) (p.category = clueCats[0]), (p.catFrom = 'tie'), (p.tie = clueCats.slice(0, 2));
    else if (p.shopHint === 'tie') (p.category = 'Food & drink'), (p.catFrom = 'tie'), (p.tie = ['Food & drink', 'Groceries']);
    else if (p.shopHint) (p.category = p.shopHint), (p.catFrom = 'shop');
    else (p.category = 'Food & drink'), (p.catFrom = 'guess');
    delete p.shopHint;
    // the word a category change teaches: the whole name up to two words, else its first word
    const kt = toks(p.item);
    p.learnKey = kt.length ? (kt.length <= 2 ? key : kt[0]) : '';
    if (p.price == null) p.flags.push('amount');
    if (!p.item) p.flags.push('item');
    if (p.future) p.flags.push('future');
    p.notes = p.notes.join(' · ');
    return p;
  }

  // the price-list item a purchase's name matches (whole words), with its typical range, for the preview
  function matchInfo(name) {
    const hit = name ? wordMatch(name) : null,
      it = hit && itemById(hit.id);
    if (!it) return null;
    const r = priceOf(it.id);
    return { id: it.id, name: it.english.split(' ').length <= 2 ? it.english : it.name, low: r ? r.low : null, high: r ? r.high : null, whole: !!hit.whole };
  }

  /* ---------- a whole paste: lines, then purchases within a line ---------- */
  // learned: {word: category}. rate: pesos per pound (for "45 pounds"), or 0
  function read(text, now, learned, rate) {
    learned = learned || {};
    const out = [];
    String(text || '')
      .slice(0, 20000)
      .split(/\r?\n/)
      .forEach((raw) => {
        let line = raw.trim();
        if (!line) return;
        let base = now ? new Date(now) : new Date();
        // a line from the Siri Shortcut starts with when it was said: "yesterday" means the day before that
        const st = line.match(/^\[(\d{4})-(\d\d)-(\d\d)(?:[ T](\d\d):(\d\d))?\]\s*/);
        let saidAt = '';
        if (st) {
          const b = new Date(+st[1], +st[2] - 1, +st[3]);
          if (!isNaN(b) && b.getMonth() === +st[2] - 1) {
            base = b;
            // Q15: the stamp is kept with each purchase (saidAt), so pasting the inbox again saves nothing twice
            saidAt = stampOf(st[1] + '-' + st[2] + '-' + st[3] + (st[4] ? ' ' + st[4] + ':' + st[5] : ''));
          }
          line = line.slice(st[0].length);
        }
        const said = line.slice(0, 500);
        let s =
          ' ' +
          wordsToDigits(low(line).replace(/\b7[\s-]?(eleven|11)\b|\bseven[\s-]eleven\b/g, 'seveneleven'))
            .replace(/(\d{1,2}):(\d{2})(?=\s*(?:pesos?|php))/g, '$1$2') // "1:20 pesos": Siri writing a price as a time
            .replace(/\bg[\s-]cash\b/g, 'gcash')
            .replace(/[–—]/g, ' ') +
          ' ';
        // things said once for the whole line: a day, "both by card", an opening "At Puregold in San Jose,"
        const shared = {},
          d = takeDate(s, base);
        // the line's day applies to each purchase in it, unless a purchase names its own
        if (d) (shared.date = d.date), (shared.future = d.future), (s = d.rest);
        const both = s.match(/\b(both|all|each) (?:by|with|on|via|in) (\w+(?: \w+)?)/);
        if (both) {
          const pay = takePay(' with ' + both[2] + ' ');
          if (pay) (shared.payment = pay.payment), (shared.payNote = pay.payNote), (s = s.replace(both[0], ' '));
        }
        const lead = s.match(/^[\s,]*at ([a-z][a-z .'-]*?)(?: in ([a-z][a-z .'-]*?))?\s*,/);
        if (lead) {
          shared.location = nice(lead[1]) + (lead[2] ? ', ' + nice(lead[2]) : '');
          s = ' ' + s.slice(lead[0].length);
        }
        const first = out.length;
        // sure splits: "also" and semicolons. Soft ones (commas, "and", "then", "plus") only between two amounts
        s.split(/\balso\b|;/).forEach((chunk) => {
          const pieces = chunk.split(/(,(?!\d{3}(?!\d))|\band\b|\bthen\b|\bplus\b)/), // not the comma in 1,250
            segs = [];
          let cur = '';
          for (let i = 0; i < pieces.length; i += 2) {
            const piece = pieces[i] || '',
              joiner = pieces[i - 1] || '';
            if (cur && amounts(cur).length && amounts(piece).length) {
              segs.push(cur);
              cur = piece;
            } else cur += (cur ? joiner : '') + piece;
          }
          if (cur.trim()) segs.push(cur);
          segs.forEach((seg) => seg.replace(/[^a-z0-9]/gi, '') && out.push(readOne(seg, shared, base, learned, rate)));
        });
        // every purchase keeps the words he said for it: the whole line when it's the only one, else its own part
        const mine = out.slice(first);
        mine.forEach((p, i) => {
          p.said = mine.length === 1 ? said : segSaid(line, mine.length, i);
          if (saidAt) p.saidAt = saidAt;
        });
      });
    return out;
  }
  // a Shortcut stamp as kept with a purchase: "2026-11-21 13:05" (or just the day), else ''
  function stampOf(x) {
    const m = String(x == null ? '' : x).trim().match(/^(\d{4})-(\d\d)-(\d\d)(?: (\d\d):(\d\d))?$/);
    if (!m) return '';
    const d = new Date(+m[1], +m[2] - 1, +m[3]);
    if (isNaN(d) || d.getMonth() !== +m[2] - 1 || (m[4] && (+m[4] > 23 || +m[5] > 59))) return '';
    return m[0];
  }
  // what makes a Shortcut line the same as a saved purchase: its stamp and its words (case and spacing aside)
  const sameKey = (p) => (p && p.saidAt && p.said ? p.saidAt + '|' + low(p.said).replace(/\s+/g, ' ').trim() : '');
  // his own words for each purchase of a line that held several: split where the reader split, in his spelling
  function segSaid(line, n, i) {
    const parts = line.split(/\s*(?:\balso\b|;)\s*/i).flatMap((c) => c.split(/\s*,(?!\d{3}(?!\d))\s*|\s+(?:and|then|plus)\s+(?=\S*\d|.*\d)/i));
    return (parts.length === n ? parts[i] : line).trim().slice(0, 500);
  }
  return { read, matchInfo, toks, low, stampOf, sameKey };
})();
